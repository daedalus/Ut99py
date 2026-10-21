"""Tests for Engine/Inc/Palette.h port (graphics/palette.py)."""

import pytest

from ut99py.graphics.palette import (
    ARGB_1555,
    ARGB_4444,
    ARGB_8888,
    RGB_565,
    RGB_888,
    XRGB_8888,
    HeckbertQuantize,
)


def test_source_data_formats():
    assert ARGB_8888 == 0
    assert XRGB_8888 == 1
    assert RGB_888 == 2
    assert RGB_565 == 3
    assert ARGB_1555 == 4
    assert ARGB_4444 == 5


def test_heckbert_quantize_is_in_engine_lib():
    with pytest.raises(NotImplementedError):
        HeckbertQuantize(
            None,  # srcdata
            None,  # dstdata
            None,  # paldata
            ARGB_8888,
            256,
            4,
            4,
            0,
            0,
            0,
        )
