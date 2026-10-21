"""Tests for Engine/Inc/UnDDraw.h port (graphics/unddraw.py)."""

from ut99py.graphics.unddraw import (
    DDPIXELFORMAT,
    DDSCAPS,
    DDSURFACEDESC,
    DDCOLORKEY,
    DDPF_FOURCC,
    DDPF_RGB,
    DDSD_CAPS,
    DDSD_HEIGHT,
    DDSD_LPSURFACE,
    DDSD_PIXELFORMAT,
    DDSD_PITCH,
    DDSD_WIDTH,
)


def test_ddcolorkey_fields():
    key = DDCOLORKEY()
    key.dwColorSpaceLowValue = 0x1234
    key.dwColorSpaceHighValue = 0x5678
    assert key.dwColorSpaceLowValue == 0x1234
    assert key.dwColorSpaceHighValue == 0x5678


def test_ddscaps_fields():
    caps = DDSCAPS()
    caps.dwCaps = 0x400
    assert caps.dwCaps == 0x400


def test_ddpixelformat_fields():
    fmt = DDPIXELFORMAT()
    fmt.dwSize = 32
    fmt.dwFlags = DDPF_RGB
    fmt.dwFourCC = DDPF_FOURCC
    fmt.bit_count.dwRGBBitCount = 32
    fmt.red.dwRBitMask = 0x00FF0000
    fmt.green.dwGBitMask = 0x0000FF00
    fmt.blue.dwBBitMask = 0x000000FF
    fmt.alpha.dwRGBAlphaBitMask = 0xFF000000

    assert fmt.dwSize == 32
    assert fmt.dwFlags == DDPF_RGB
    assert fmt.dwFourCC == DDPF_FOURCC
    assert fmt.bit_count.dwRGBBitCount == 32
    assert fmt.red.dwRBitMask == 0x00FF0000
    assert fmt.green.dwGBitMask == 0x0000FF00
    assert fmt.blue.dwBBitMask == 0x000000FF
    assert fmt.alpha.dwRGBAlphaBitMask == 0xFF000000


def test_ddpixelformat_unions_alias_the_same_storage():
    fmt = DDPIXELFORMAT()
    fmt.bit_count.dwRGBBitCount = 16
    # The C++ union makes the bit-count members share one DWORD.
    assert fmt.bit_count.dwYUVBitCount == 16
    fmt.red.dwRBitMask = 0xF800
    assert fmt.red.dwYBitMask == 0xF800


def test_ddsurfacedesc_fields():
    desc = DDSURFACEDESC()
    desc.dwSize = 120
    desc.dwFlags = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH
    desc.dwHeight = 32
    desc.dwWidth = 64
    desc.pitch.lPitch = 256
    desc.dwBackBufferCount = 1
    desc.mip_count.dwMipMapCount = 4
    desc.dwAlphaBitDepth = 8
    desc.ddpfPixelFormat.bit_count.dwRGBBitCount = 32
    desc.ddsCaps.dwCaps = 0x400

    assert desc.dwSize == 120
    assert desc.dwHeight == 32
    assert desc.dwWidth == 64
    assert desc.pitch.lPitch == 256
    assert desc.dwBackBufferCount == 1
    assert desc.mip_count.dwMipMapCount == 4
    assert desc.dwAlphaBitDepth == 8
    assert desc.ddpfPixelFormat.bit_count.dwRGBBitCount == 32
    assert desc.ddsCaps.dwCaps == 0x400


def test_surface_flags():
    assert DDSD_CAPS == 0x00000001
    assert DDSD_HEIGHT == 0x00000002
    assert DDSD_WIDTH == 0x00000004
    assert DDSD_PITCH == 0x00000008
    assert DDSD_LPSURFACE == 0x00000800
    assert DDSD_PIXELFORMAT == 0x00001000
    assert DDPF_FOURCC == 0x00000004
    assert DDPF_RGB == 0x00000040
