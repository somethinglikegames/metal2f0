"""Converts BaseColor + Metalness textures to Diffuse / Albedo + F0 / Specular textures."""
import numpy as np


def extract_metal_channel(
    metal: np.ndarray,
    channel: int,
) -> np.ndarray:
    """Extract and clamp one channel from a Metal texture."""

    if metal.ndim != 3:
        raise ValueError(
            "Metal texture must have shape (height, width, channels)"
        )

    if channel < 0 or channel >= metal.shape[2]:
        raise ValueError(
            f"Invalid metal channel: {channel}"
        )

    return np.clip(
        metal[..., channel],
        0.0,
        1.0,
    )


def calculate_diffuse(
    base_color: np.ndarray,
    metal: np.ndarray,
) -> np.ndarray:
    """Calculate Diffuse Albedo from BaseColor and Metal mask."""

    _validate_dimensions(
        base_color,
        metal,
    )

    metal = np.clip(
        metal,
        0.0,
        1.0,
    )

    result = (
        base_color
        * (1.0 - metal[..., None])
    )

    # BaseColor alpha is preserved unchanged.
    if base_color.shape[2] == 4:
        result[..., 3] = base_color[..., 3]

    return result


def calculate_f0(
    base_color: np.ndarray,
    metal: np.ndarray,
    specularity: float,
) -> np.ndarray:
    """Calculate F0 / Specular from BaseColor and Metal mask."""

    _validate_dimensions(
        base_color,
        metal,
    )

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

    result = (
        specularity * (1.0 - metal[..., None])
        + base_color * metal[..., None]
    )

    # BaseColor alpha is preserved unchanged.
    if base_color.shape[2] == 4:
        result[..., 3] = base_color[..., 3]

    return result


def _validate_dimensions(
    base_color: np.ndarray,
    metal: np.ndarray,
) -> None:
    """Ensure BaseColor and Metal have identical image dimensions."""

    if base_color.ndim != 3:
        raise ValueError(
            "BaseColor texture must have shape "
            "(height, width, channels)"
        )

    if metal.ndim != 2:
        raise ValueError(
            "Metal mask must have shape (height, width)"
        )

    if base_color.shape[:2] != metal.shape[:2]:
        raise ValueError(
            "BaseColor and Metal must have identical dimensions: "
            f"BaseColor={base_color.shape[:2]}, "
            f"Metal={metal.shape[:2]}"
        )

    if base_color.shape[2] not in (3, 4):
        raise ValueError(
            "BaseColor must have 3 or 4 channels"
        )