from pathlib import Path

import numpy as np
import OpenImageIO as oiio

from metal2f0.processing.processor import (
    load_image,
    save_image,
)


def test_load_rgb_png(tmp_path: Path):
    path = tmp_path / "test.png"

    pixels = np.array(
        [
            [
                [255, 0, 0],
                [0, 255, 0],
            ],
        ],
        dtype=np.uint8,
    )

    spec = oiio.ImageSpec(
        2,
        1,
        3,
        oiio.UINT8,
    )

    output = oiio.ImageOutput.create(str(path))

    assert output is not None

    assert output.open(
        str(path),
        spec,
    )

    output.write_image(
        pixels,
    )

    output.close()

    result, result_spec = load_image(path)

    assert result.dtype == np.float32
    assert result.shape == (1, 2, 3)
    assert result_spec.nchannels == 3

    np.testing.assert_allclose(
        result,
        pixels / 255.0,
        atol=1e-6,
    )


def test_save_and_load_rgb_png(tmp_path: Path):
    pixels = np.array(
        [
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            [
                [0.0, 0.0, 1.0],
                [0.5, 0.25, 0.75],
            ],
        ],
        dtype=np.float32,
    )

    path = tmp_path / "test.png"

    save_image(
        path,
        pixels,
    )

    result, spec = load_image(path)

    assert result.shape == (2, 2, 3)
    assert result.dtype == np.float32

    np.testing.assert_allclose(
        result,
        pixels,
        atol=1 / 255,
    )

    assert spec.width == 2
    assert spec.height == 2
    assert spec.nchannels == 3


def test_save_and_load_rgba_png(tmp_path: Path):
    pixels = np.array(
        [
            [
                [1.0, 0.0, 0.0, 1.0],
                [0.0, 1.0, 0.0, 0.5],
            ],
            [
                [0.0, 0.0, 1.0, 0.25],
                [0.5, 0.25, 0.75, 0.0],
            ],
        ],
        dtype=np.float32,
    )

    path = tmp_path / "test.png"

    save_image(
        path,
        pixels,
    )

    result, spec = load_image(path)

    assert result.shape == (2, 2, 4)
    assert result.dtype == np.float32

    np.testing.assert_allclose(
        result,
        pixels,
        atol=1 / 255,
    )

    assert spec.width == 2
    assert spec.height == 2
    assert spec.nchannels == 4


def test_save_and_load_rgb_tga(tmp_path: Path):
    pixels = np.array(
        [
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            [
                [0.0, 0.0, 1.0],
                [0.5, 0.25, 0.75],
            ],
        ],
        dtype=np.float32,
    )

    path = tmp_path / "test.tga"

    save_image(
        path,
        pixels,
    )

    result, spec = load_image(path)

    assert result.shape == (2, 2, 3)
    assert result.dtype == np.float32
    assert spec.nchannels == 3

    np.testing.assert_allclose(
        result,
        pixels,
        atol=1 / 255,
    )


def test_save_and_load_rgba_tga(tmp_path: Path):
    pixels = np.array(
        [
            [
                [1.0, 0.0, 0.0, 1.0],
                [0.0, 1.0, 0.0, 0.5],
            ],
            [
                [0.0, 0.0, 1.0, 0.25],
                [0.5, 0.25, 0.75, 0.0],
            ],
        ],
        dtype=np.float32,
    )

    path = tmp_path / "test.tga"

    save_image(
        path,
        pixels,
    )

    result, spec = load_image(path)

    assert result.shape == (2, 2, 4)
    assert result.dtype == np.float32
    assert spec.nchannels == 4

    np.testing.assert_allclose(
        result,
        pixels,
        atol=1 / 255,
    )


def test_save_and_load_rgb_exr(tmp_path: Path):
    pixels = np.array(
        [
            [
                [0.123456, 0.5, 1.25],
                [2.0, 0.25, 0.75],
            ],
        ],
        dtype=np.float32,
    )

    path = tmp_path / "test.exr"

    save_image(
        path,
        pixels,
    )

    result, spec = load_image(path)

    assert result.shape == (1, 2, 3)
    assert result.dtype == np.float32
    assert spec.nchannels == 3

    np.testing.assert_allclose(
        result,
        pixels,
        rtol=1e-6,
        atol=1e-6,
    )


def test_save_and_load_rgba_exr(tmp_path: Path):
    pixels = np.array(
        [
            [
                [0.123456, 0.5, 1.25, 1.0],
                [2.0, 0.25, 0.75, 0.25],
            ],
        ],
        dtype=np.float32,
    )

    path = tmp_path / "test.exr"

    save_image(
        path,
        pixels,
    )

    result, spec = load_image(path)

    assert result.shape == (1, 2, 4)
    assert result.dtype == np.float32
    assert spec.nchannels == 4

    np.testing.assert_allclose(
        result,
        pixels,
        rtol=1e-6,
        atol=1e-6,
    )


def test_rgb_image_does_not_gain_alpha(tmp_path: Path):
    pixels = np.array(
        [[[0.2, 0.4, 0.6]]],
        dtype=np.float32,
    )

    path = tmp_path / "rgb.png"

    save_image(
        path,
        pixels,
    )

    result, spec = load_image(path)

    assert result.shape == (1, 1, 3)
    assert spec.nchannels == 3


def test_rgba_alpha_is_not_premultiplied(tmp_path: Path):
    pixels = np.array(
        [
            [
                [0.0, 1.0, 0.0, 0.5],
            ],
        ],
        dtype=np.float32,
    )

    path = tmp_path / "rgba.png"

    save_image(
        path,
        pixels,
    )

    result, spec = load_image(path)

    assert spec.nchannels == 4

    np.testing.assert_allclose(
        result[0, 0],
        pixels[0, 0],
        atol=1 / 255,
    )
