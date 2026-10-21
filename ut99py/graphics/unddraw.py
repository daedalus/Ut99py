"""Port of Engine/Inc/UnDDraw.h (4 declared symbols).

DirectDraw surface definitions needed by the S3TC compression code. The C
unions are modelled with ctypes unions so the overlapping members keep the
C++ aliasing behaviour.
"""

from __future__ import annotations
import ctypes

# Windows scalar types (UnDDraw.h:34-35).
DWORD = ctypes.c_uint32
LONG = ctypes.c_int32
LPVOID = ctypes.c_void_p


class DDCOLORKEY(ctypes.Structure):
    """DDCOLORKEY (UnDDraw.h:38-44): colour key range of a surface."""

    _fields_ = [
        ("dwColorSpaceLowValue", DWORD),
        ("dwColorSpaceHighValue", DWORD),
    ]


class DDSCAPS(ctypes.Structure):
    """DDSCAPS (UnDDraw.h:47-51): capabilities of the wanted surface."""

    _fields_ = [("dwCaps", DWORD)]


class _DDPIXELFORMAT_COUNT(ctypes.Union):
    """First union of DDPIXELFORMAT (UnDDraw.h:60-67): bits per pixel."""

    _fields_ = [
        ("dwRGBBitCount", DWORD),
        ("dwYUVBitCount", DWORD),
        ("dwZBufferBitDepth", DWORD),
        ("dwAlphaBitDepth", DWORD),
        ("dwLuminanceBitCount", DWORD),
        ("dwBumpBitCount", DWORD),
    ]


class _DDPIXELFORMAT_RED(ctypes.Union):
    """Second union of DDPIXELFORMAT (UnDDraw.h:68-74): red bit mask."""

    _fields_ = [
        ("dwRBitMask", DWORD),
        ("dwYBitMask", DWORD),
        ("dwStencilBitDepth", DWORD),
        ("dwLuminanceBitMask", DWORD),
        ("dwBumpDuBitMask", DWORD),
    ]


class _DDPIXELFORMAT_GREEN(ctypes.Union):
    """Third union of DDPIXELFORMAT (UnDDraw.h:75-81): green bit mask."""

    _fields_ = [
        ("dwGBitMask", DWORD),
        ("dwUBitMask", DWORD),
        ("dwZBitMask", DWORD),
        ("dwBumpDvBitMask", DWORD),
    ]


class _DDPIXELFORMAT_BLUE(ctypes.Union):
    """Fourth union of DDPIXELFORMAT (UnDDraw.h:82-88): blue bit mask."""

    _fields_ = [
        ("dwBBitMask", DWORD),
        ("dwVBitMask", DWORD),
        ("dwStencilBitMask", DWORD),
        ("dwBumpLuminanceBitMask", DWORD),
    ]


class _DDPIXELFORMAT_ALPHA(ctypes.Union):
    """Fifth union of DDPIXELFORMAT (UnDDraw.h:89-95): alpha bit mask."""

    _fields_ = [
        ("dwRGBAlphaBitMask", DWORD),
        ("dwYUVAlphaBitMask", DWORD),
        ("dwLuminanceAlphaBitMask", DWORD),
        ("dwRGBZBitMask", DWORD),
        ("dwYUVZBitMask", DWORD),
    ]


class DDPIXELFORMAT(ctypes.Structure):
    """DDPIXELFORMAT (UnDDraw.h:56-96): pixel format of a surface."""

    _fields_ = [
        ("dwSize", DWORD),
        ("dwFlags", DWORD),
        ("dwFourCC", DWORD),
        ("bit_count", _DDPIXELFORMAT_COUNT),
        ("red", _DDPIXELFORMAT_RED),
        ("green", _DDPIXELFORMAT_GREEN),
        ("blue", _DDPIXELFORMAT_BLUE),
        ("alpha", _DDPIXELFORMAT_ALPHA),
    ]


class _DDSURFACEDESC_PITCH(ctypes.Union):
    """First union of DDSURFACEDESC (UnDDraw.h:104-107): surface pitch."""

    _fields_ = [
        ("lPitch", LONG),
        ("dwLinearSize", DWORD),
    ]


class _DDSURFACEDESC_MIPS(ctypes.Union):
    """Second union of DDSURFACEDESC (UnDDraw.h:112-116): mip/z/refresh."""

    _fields_ = [
        ("dwMipMapCount", DWORD),
        ("dwZBufferBitDepth", DWORD),
        ("dwRefreshRate", DWORD),
    ]


class DDSURFACEDESC(ctypes.Structure):
    """DDSURFACEDESC (UnDDraw.h:99-125): DirectDraw surface description."""

    _fields_ = [
        ("dwSize", DWORD),
        ("dwFlags", DWORD),
        ("dwHeight", DWORD),
        ("dwWidth", DWORD),
        ("pitch", _DDSURFACEDESC_PITCH),
        ("dwBackBufferCount", DWORD),
        ("mip_count", _DDSURFACEDESC_MIPS),
        ("dwAlphaBitDepth", DWORD),
        ("dwReserved", DWORD),
        ("lpSurface", LPVOID),
        ("ddckCKDestOverlay", DDCOLORKEY),
        ("ddckCKDestBlt", DDCOLORKEY),
        ("ddckCKSrcOverlay", DDCOLORKEY),
        ("ddckCKSrcBlt", DDCOLORKEY),
        ("ddpfPixelFormat", DDPIXELFORMAT),
        ("ddsCaps", DDSCAPS),
    ]


# ddsCaps field is valid (UnDDraw.h:132).
DDSD_CAPS = 0x00000001
# dwHeight field is valid (UnDDraw.h:137).
DDSD_HEIGHT = 0x00000002
# dwWidth field is valid (UnDDraw.h:142).
DDSD_WIDTH = 0x00000004
# lPitch is valid (UnDDraw.h:147).
DDSD_PITCH = 0x00000008
# lpSurface is valid (UnDDraw.h:152).
DDSD_LPSURFACE = 0x00000800
# ddpfPixelFormat is valid (UnDDraw.h:157).
DDSD_PIXELFORMAT = 0x00001000
# The FourCC code is valid (UnDDraw.h:163).
DDPF_FOURCC = 0x00000004
# The RGB data in the pixel format structure is valid (UnDDraw.h:169).
DDPF_RGB = 0x00000040


__all__ = [
    "DDCOLORKEY",
    "DDSCAPS",
    "DDPIXELFORMAT",
    "DDSURFACEDESC",
    "DWORD",
    "LONG",
    "LPVOID",
    "DDSD_CAPS",
    "DDSD_HEIGHT",
    "DDSD_WIDTH",
    "DDSD_PITCH",
    "DDSD_LPSURFACE",
    "DDSD_PIXELFORMAT",
    "DDPF_FOURCC",
    "DDPF_RGB",
]
