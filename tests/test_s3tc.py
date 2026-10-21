"""Tests for Engine/Inc/S3tc.h port (graphics/s3tc.py)."""

import pytest

from ut99py.graphics.s3tc import (
    S3TC_ENCODE_ALPHA_EXPLICIT,
    S3TC_ENCODE_ALPHA_INTERPOLATED,
    S3TC_ENCODE_ALPHA_NEED0,
    S3TC_ENCODE_ALPHA_NEED1,
    S3TC_ENCODE_ALPHA_NONE,
    S3TC_ENCODE_RGB_ALPHA_COMPARE,
    S3TC_ENCODE_RGB_COLOR_KEY,
    S3TC_ENCODE_RGB_FULL,
    PALETTEENTRY,
    S3TCdecode,
    S3TCencode,
    S3TCgetDecodeSize,
    S3TCgetEncodeSize,
    S3TCsetAlphaReference,
)
from ut99py.graphics.unddraw import DDSURFACEDESC


def test_paletteentry_fields():
    entry = PALETTEENTRY()
    entry.peRed = 1
    entry.peGreen = 2
    entry.peBlue = 3
    entry.peFlags = 4
    assert entry.peRed == 1
    assert entry.peGreen == 2
    assert entry.peBlue == 3
    assert entry.peFlags == 4


def test_encoding_constants():
    assert S3TC_ENCODE_RGB_FULL == 0x0
    assert S3TC_ENCODE_RGB_COLOR_KEY == 0x1
    assert S3TC_ENCODE_RGB_ALPHA_COMPARE == 0x2
    assert S3TC_ENCODE_ALPHA_NONE == 0x000
    assert S3TC_ENCODE_ALPHA_EXPLICIT == 0x100
    assert S3TC_ENCODE_ALPHA_INTERPOLATED == 0x200
    assert S3TC_ENCODE_ALPHA_NEED0 == 0x10000
    assert S3TC_ENCODE_ALPHA_NEED1 == 0x20000


def test_s3tc_entry_points_are_in_engine_lib():
    desc = DDSURFACEDESC()
    with pytest.raises(NotImplementedError):
        S3TCsetAlphaReference(128)
    with pytest.raises(NotImplementedError):
        S3TCgetEncodeSize(desc, S3TC_ENCODE_RGB_FULL)
    with pytest.raises(NotImplementedError):
        S3TCencode(desc, None, desc, None, S3TC_ENCODE_RGB_FULL, None)
    with pytest.raises(NotImplementedError):
        S3TCgetDecodeSize(desc)
    with pytest.raises(NotImplementedError):
        S3TCdecode(desc, desc, None)
