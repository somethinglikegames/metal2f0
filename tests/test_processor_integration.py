from pathlib import Path

import numpy as np
import OpenImageIO as oiio

from metal2f0.processing.processor import (
    process,
)


def _write_test_image(
    path: Path,
    pixels: np.ndarray,
) -> None:
    height, width, channels = pixels.shape

    spec = oiio.ImageSpec(
        width,
        height,
        channels,
        oiio.FLOAT,
    )

    if channels == 4:
        spec.alpha_channel = 3
        spec.attribute(
            "oiio:UnassociatedAlpha",
            1,
        )

    output = oiio.ImageOutput.create(
        str(path),
    )

    assert output is not None

    try:
        assert output.open(
            str(path),
            spec,
        )

        assert output.write_image(
            pixels,
        )
    finally:
        output.close()


def _read_test_image(
    path: Path,
) -> np.ndarray:
    input = oiio.ImageInput.open(
        str(path),
    )

    assert input is not None

    try:
        pixels = input.read_image(
            oiio.FLOAT,
        )

        assert pixels is not None

        return np.asarray(
            pixels,
            dtype=np.float32,
        )
    finally:
        input.close()


def test_process_rgb_base_color_with_red_metal_channel(
    tmp_path: Path,
):
    base_color_path = tmp_path / "base_color.png"
    metal_path = tmp_path / "metal.png"
    diffuse_path = tmp_path / "diffuse.png"
    f0_path = tmp_path / "f0.png"

    base_color = np.array(
        [
            [
                [0.8, 0.4, 0.2],
                [0.2, 0.4, 0.8],
            ],
        ],
        dtype=np.float32,
    )

    metal = np.array(
        [
            [
                [0.0],
                [1.0],
            ],
        ],
        dtype=np.float32,
    )

    _write_test_image(
        base_color_path,
        base_color,
    )

    _write_test_image(
        metal_path,
        metal,
    )

    process(
        base_color_path=base_color_path,
        metal_path=metal_path,
        metal_channel=0,
        specularity=0.04,
        diffuse_path=diffuse_path,
        f0_path=f0_path,
    )

    diffuse = _read_test_image(
        diffuse_path,
    )

    f0 = _read_test_image(
        f0_path,
    )

    expected_diffuse = np.array(
        [
            [
                [0.8, 0.4, 0.2],
                [0.0, 0.0, 0.0],
            ],
        ],
        dtype=np.float32,
    )

    expected_f0 = np.array(
        [
            [
                [0.04, 0.04, 0.04],
                [0.2, 0.4, 0.8],
            ],
        ],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        diffuse,
        expected_diffuse,
        atol=1 / 255,
    )

    np.testing.assert_allclose(
        f0,
        expected_f0,
        atol=1 / 255,
    )


def test_process_preserves_base_color_alpha(
    tmp_path: Path,
):
    base_color_path = tmp_path / "base_color.png"
    metal_path = tmp_path / "metal.png"
    diffuse_path = tmp_path / "diffuse.png"
    f0_path = tmp_path / "f0.png"

    base_color = np.array(
        [
            [
                [0.8, 0.4, 0.2, 0.25],
                [0.2, 0.4, 0.8, 0.75],
            ],
        ],
        dtype=np.float32,
    )

    metal = np.array(
        [
            [
                [0.0],
                [1.0],
            ],
        ],
        dtype=np.float32,
    )

    _write_test_image(
        base_color_path,
        base_color,
    )

    _write_test_image(
        metal_path,
        metal,
    )

    process(
        base_color_path=base_color_path,
        metal_path=metal_path,
        metal_channel=0,
        specularity=0.04,
        diffuse_path=diffuse_path,
        f0_path=f0_path,
    )

    diffuse = _read_test_image(
        diffuse_path,
    )

    f0 = _read_test_image(
        f0_path,
    )

    assert diffuse.shape == (1, 2, 4)
    assert f0.shape == (1, 2, 4)

    np.testing.assert_allclose(
        diffuse[..., 3],
        base_color[..., 3],
        atol=1 / 255,
    )

    np.testing.assert_allclose(
        f0[..., 3],
        base_color[..., 3],
        atol=1 / 255,
    )
