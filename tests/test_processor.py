import numpy as np
import pytest

from metal2f0.processing.processor import (
    calculate_diffuse,
    calculate_f0,
    extract_metal_channel,
)


# ============================================================================
# Diffuse Albedo
# ============================================================================


def test_diffuse_is_base_color_for_zero_metal():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[0.0]],
        dtype=np.float32,
    )

    result = calculate_diffuse(
        base_color,
        metal,
    )

    np.testing.assert_allclose(
        result,
        base_color,
    )


def test_diffuse_is_black_for_full_metal():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[1.0]],
        dtype=np.float32,
    )

    expected = np.zeros_like(base_color)

    result = calculate_diffuse(
        base_color,
        metal,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_diffuse_interpolates_at_half_metal():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[0.5]],
        dtype=np.float32,
    )

    expected = np.array(
        [[[0.4, 0.2, 0.1]]],
        dtype=np.float32,
    )

    result = calculate_diffuse(
        base_color,
        metal,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_diffuse_preserves_alpha():
    base_color = np.array(
        [[[0.8, 0.4, 0.2, 0.35]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[0.5]],
        dtype=np.float32,
    )

    result = calculate_diffuse(
        base_color,
        metal,
    )

    expected = np.array(
        [[[0.4, 0.2, 0.1, 0.35]]],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_diffuse_clamps_metal_below_zero():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[-1.0]],
        dtype=np.float32,
    )

    result = calculate_diffuse(
        base_color,
        metal,
    )

    np.testing.assert_allclose(
        result,
        base_color,
    )


def test_diffuse_clamps_metal_above_one():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[2.0]],
        dtype=np.float32,
    )

    expected = np.zeros_like(base_color)

    result = calculate_diffuse(
        base_color,
        metal,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


# ============================================================================
# F0 / Specular
# ============================================================================


def test_f0_is_specularity_for_zero_metal():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[0.0]],
        dtype=np.float32,
    )

    specularity = 0.04

    expected = np.array(
        [[[0.04, 0.04, 0.04]]],
        dtype=np.float32,
    )

    result = calculate_f0(
        base_color,
        metal,
        specularity,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_f0_is_base_color_for_full_metal():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[1.0]],
        dtype=np.float32,
    )

    specularity = 0.04

    result = calculate_f0(
        base_color,
        metal,
        specularity,
    )

    np.testing.assert_allclose(
        result,
        base_color,
    )


def test_f0_interpolates_at_half_metal():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[0.5]],
        dtype=np.float32,
    )

    specularity = 0.04

    expected = np.array(
        [[[0.42, 0.22, 0.12]]],
        dtype=np.float32,
    )

    result = calculate_f0(
        base_color,
        metal,
        specularity,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_f0_preserves_alpha():
    base_color = np.array(
        [[[0.8, 0.4, 0.2, 0.35]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[0.5]],
        dtype=np.float32,
    )

    specularity = 0.04

    expected = np.array(
        [[[0.42, 0.22, 0.12, 0.35]]],
        dtype=np.float32,
    )

    result = calculate_f0(
        base_color,
        metal,
        specularity,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_f0_clamps_metal_below_zero():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[-1.0]],
        dtype=np.float32,
    )

    specularity = 0.04

    expected = np.array(
        [[[0.04, 0.04, 0.04]]],
        dtype=np.float32,
    )

    result = calculate_f0(
        base_color,
        metal,
        specularity,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_f0_clamps_metal_above_one():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[2.0]],
        dtype=np.float32,
    )

    specularity = 0.04

    result = calculate_f0(
        base_color,
        metal,
        specularity,
    )

    np.testing.assert_allclose(
        result,
        base_color,
    )


def test_f0_clamps_specularity_below_zero():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[0.0]],
        dtype=np.float32,
    )

    result = calculate_f0(
        base_color,
        metal,
        -1.0,
    )

    expected = np.zeros_like(base_color)

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_f0_clamps_specularity_above_one():
    base_color = np.array(
        [[[0.8, 0.4, 0.2]]],
        dtype=np.float32,
    )

    metal = np.array(
        [[0.0]],
        dtype=np.float32,
    )

    result = calculate_f0(
        base_color,
        metal,
        2.0,
    )

    expected = np.ones_like(base_color)

    np.testing.assert_allclose(
        result,
        expected,
    )


# ============================================================================
# Metal channel extraction
# ============================================================================


def test_extract_red_metal_channel():
    metal = np.array(
        [
            [[0.1, 0.2, 0.3, 0.4]],
        ],
        dtype=np.float32,
    )

    result = extract_metal_channel(metal, 0)

    expected = np.array(
        [[0.1]],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_extract_green_metal_channel():
    metal = np.array(
        [
            [[0.1, 0.2, 0.3, 0.4]],
        ],
        dtype=np.float32,
    )

    result = extract_metal_channel(metal, 1)

    expected = np.array(
        [[0.2]],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_extract_blue_metal_channel():
    metal = np.array(
        [
            [[0.1, 0.2, 0.3, 0.4]],
        ],
        dtype=np.float32,
    )

    result = extract_metal_channel(metal, 2)

    expected = np.array(
        [[0.3]],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_extract_alpha_metal_channel():
    metal = np.array(
        [
            [[0.1, 0.2, 0.3, 0.4]],
        ],
        dtype=np.float32,
    )

    result = extract_metal_channel(metal, 3)

    expected = np.array(
        [[0.4]],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        result,
        expected,
    )


def test_extract_metal_channel_rejects_invalid_channel():
    metal = np.array(
        [
            [[0.1, 0.2, 0.3, 0.4]],
        ],
        dtype=np.float32,
    )

    with pytest.raises(ValueError):
        extract_metal_channel(metal, 4)


# ============================================================================
# Image dimensions
# ============================================================================


def test_diffuse_rejects_mismatched_dimensions():
    base_color = np.zeros(
        (2, 2, 3),
        dtype=np.float32,
    )

    metal = np.zeros(
        (3, 2),
        dtype=np.float32,
    )

    with pytest.raises(ValueError):
        calculate_diffuse(
            base_color,
            metal,
        )


def test_f0_rejects_mismatched_dimensions():
    base_color = np.zeros(
        (2, 2, 3),
        dtype=np.float32,
    )

    metal = np.zeros(
        (3, 2),
        dtype=np.float32,
    )

    with pytest.raises(ValueError):
        calculate_f0(
            base_color,
            metal,
            0.04,
        )