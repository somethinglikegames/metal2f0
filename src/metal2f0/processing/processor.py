"""Converts BaseColor + Metalness textures to Diffuse / Albedo + F0 / Specular textures."""
from pathlib import Path

import numpy as np
import OpenImageIO as oiio


def process(base_color_path: Path,
            metal_path: Path,
            metal_channel: int,
            specularity: float,
            diffuse_path: Path,
            f0_path: Path,
            ) -> None:
    base_color, base_color_spec = load_image(base_color_path, )
    if base_color_spec.nchannels not in (3, 4):
        raise ValueError("BaseColor must have 3 or 4 channels")

    metal, metal_spec = load_image(metal_path, )
    if metal_spec.nchannels not in (1, 2, 3, 4):
        raise ValueError("Metal texture must have between 1 and 4 channels")
    metal_channel = extract_metal_channel(metal, metal_channel)

    diffuse = calculate_diffuse(base_color, metal_channel)
    f0 = calculate_f0(base_color, metal_channel, specularity)

    save_image(diffuse_path, diffuse)
    save_image(f0_path, f0)


def load_image(path: Path) -> tuple[np.ndarray, oiio.ImageSpec]:
    # Determine channel count to enforce non-premultiplied alpha
    native_input = oiio.ImageInput.open(str(path))

    if native_input is None:
        raise RuntimeError(
            f"Could not open image '{path}': "
            f"{oiio.geterror()}"
        )

    try:
        source_spec = native_input.spec()

        channels = source_spec.nchannels

        if channels not in (1, 2, 3, 4):
            raise ValueError(
                f"Unsupported channel count: {channels}"
            )

        output_spec = oiio.ImageSpec(
            source_spec.width,
            source_spec.height,
            channels,
            oiio.FLOAT,
        )

        output_spec.channelnames = source_spec.channelnames

        if channels == 4:
            output_spec.alpha_channel = 3
            output_spec.attribute(
                "oiio:UnassociatedAlpha",
                1,
            )

    finally:
        native_input.close()

    # Reread image with correct spec
    input = oiio.ImageInput.open(
        str(path),
        output_spec,
    )

    if input is None:
        raise RuntimeError(
            f"Could not open image '{path}' "
            f"with requested spec: "
            f"{oiio.geterror()}"
        )

    try:
        pixels = input.read_image(
            oiio.FLOAT,
        )

        if pixels is None:
            raise RuntimeError(
                f"Could not read image '{path}': "
                f"{input.geterror()}"
            )

        return (
            np.asarray(
                pixels,
                dtype=np.float32,
            ),
            input.spec(),
        )

    finally:
        input.close()


def save_image(path: Path, pixels: np.ndarray) -> None:
    """Save an RGB or RGBA float32 image using OpenImageIO."""

    if pixels.dtype != np.float32:
        raise ValueError("Image data must use float32")

    if pixels.ndim != 3:
        raise ValueError(
            "Image data must have shape (height, width, channels)")

    height, width, channels = pixels.shape

    if channels not in (3, 4):
        raise ValueError("Image must have 3 or 4 channels")

    if not np.isfinite(pixels).all():
        raise ValueError("Image contains non-finite values")

    spec = oiio.ImageSpec(
        width,
        height,
        channels,
        oiio.FLOAT,
    )
    if channels == 4:
        spec.alpha_channel = 3
        spec.attribute("oiio:UnassociatedAlpha", 1)

    output = oiio.ImageOutput.create(str(path))

    if output is None:
        raise RuntimeError(
            f"Could not create image output '{path}': {oiio.geterror()}")

    try:
        if not output.open(str(path), spec):
            raise RuntimeError(
                f"Could not open image output '{path}': {output.geterror()}")

        if not output.write_image(pixels):
            raise RuntimeError(
                f"Could not write image '{path}': {output.geterror()}")

    finally:
        output.close()


def extract_metal_channel(metal: np.ndarray, channel: int) -> np.ndarray:
    """Extract and clamp one channel from a Metal texture."""

    if metal.ndim != 3:
        raise ValueError(
            "Metal texture must have shape (height, width, channels)")

    if channel < 0 or channel >= metal.shape[2]:
        raise ValueError(f"Invalid metal channel: {channel}")

    return np.clip(
        metal[..., channel],
        0.0,
        1.0,
    )


def calculate_diffuse(base_color: np.ndarray, metal: np.ndarray) -> np.ndarray:
    """Calculate Diffuse Albedo from BaseColor and Metal mask."""

    _validate_dimensions(base_color, metal)

    metal = np.clip(
        metal,
        0.0,
        1.0,
    )

    result = (base_color * (1.0 - metal[..., None]))

    # BaseColor alpha is preserved unchanged.
    if base_color.shape[2] == 4:
        result[..., 3] = base_color[..., 3]

    return result


def calculate_f0(base_color: np.ndarray, metal: np.ndarray, specularity: float,) -> np.ndarray:
    """Calculate F0 / Specular from BaseColor and Metal mask."""

    _validate_dimensions(base_color, metal)

    metal = np.clip(
        metal,
        0.0,
        1.0,
    )

    specularity = float(
        np.clip(
            specularity,
            0.0,
            1.0,
        )
    )

    result = specularity * \
        (1.0 - metal[..., None]) + base_color * metal[..., None]

    # BaseColor alpha is preserved unchanged.
    if base_color.shape[2] == 4:
        result[..., 3] = base_color[..., 3]

    return result


def _validate_dimensions(base_color: np.ndarray, metal: np.ndarray) -> None:
    """Ensure BaseColor and Metal have identical image dimensions."""

    if base_color.ndim != 3:
        raise ValueError(
            "BaseColor texture must have shape (height, width, channels)")

    if metal.ndim != 2:
        raise ValueError("Metal mask must have shape (height, width)")

    if base_color.shape[:2] != metal.shape[:2]:
        raise ValueError(
            "BaseColor and Metal must have identical dimensions: "
            f"BaseColor={base_color.shape[:2]}, Metal={metal.shape[:2]}"
        )

    if base_color.shape[2] not in (3, 4):
        raise ValueError("BaseColor must have 3 or 4 channels")
