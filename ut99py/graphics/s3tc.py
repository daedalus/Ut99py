"""Port of Engine/Inc/S3tc.h (1 declared symbol).

PALETTEENTRY plus the S3TC encoding constants and the compression entry
points used by the DirectDraw surface code. The compression routines have no
body in the source tree, so they raise NotImplementedError.
"""

from __future__ import annotations
import ctypes
from typing import Any, Optional
from .unddraw import DDSURFACEDESC

BYTE = ctypes.c_uint8


class PALETTEENTRY(ctypes.Structure):
    """PALETTEENTRY (S3tc.h:21-26): one palette entry."""

    _fields_ = [
        ("peRed", BYTE),
        ("peGreen", BYTE),
        ("peBlue", BYTE),
        ("peFlags", BYTE),
    ]


# RGB encoding types (S3tc.h:28-31).
S3TC_ENCODE_RGB_FULL = 0x0
S3TC_ENCODE_RGB_COLOR_KEY = 0x1
S3TC_ENCODE_RGB_ALPHA_COMPARE = 0x2
_S3TC_ENCODE_RGB_MASK = 0xFF

# Alpha encoding types (S3tc.h:33-37).
S3TC_ENCODE_ALPHA_NONE = 0x000
S3TC_ENCODE_ALPHA_EXPLICIT = 0x100
S3TC_ENCODE_ALPHA_INTERPOLATED = 0x200
_S3TC_ENCODE_ALPHA_MASK = 0xFF00

# Additional alpha encoding flags (S3tc.h:39-41).
S3TC_ENCODE_ALPHA_NEED0 = 0x10000
S3TC_ENCODE_ALPHA_NEED1 = 0x20000


def S3TCsetAlphaReference(nRef: int) -> None:
    """S3TCsetAlphaReference (S3tc.h:46)."""
    raise NotImplementedError("C++ S3TCsetAlphaReference: Engine.lib")


def S3TCgetEncodeSize(lpDesc: DDSURFACEDESC, dwEncodeType: int) -> int:
    """S3TCgetEncodeSize (S3tc.h:49-51)."""
    raise NotImplementedError("C++ S3TCgetEncodeSize: Engine.lib")


def S3TCencode(
    lpSrc: DDSURFACEDESC,
    lpPal: Optional[PALETTEENTRY],
    lpDest: DDSURFACEDESC,
    lpDestBuf: Any,
    dwEncodeType: int,
    weight: Any,
) -> None:
    """S3TCencode (S3tc.h:54-60)."""
    raise NotImplementedError("C++ S3TCencode: Engine.lib")


def S3TCgetDecodeSize(lpDesc: DDSURFACEDESC) -> int:
    """S3TCgetDecodeSize (S3tc.h:63)."""
    raise NotImplementedError("C++ S3TCgetDecodeSize: Engine.lib")


def S3TCdecode(lpSrc: DDSURFACEDESC, lpDest: DDSURFACEDESC, lpDestBuf: Any) -> None:
    """S3TCdecode (S3tc.h:66-69)."""
    raise NotImplementedError("C++ S3TCdecode: Engine.lib")


__all__ = [
    "PALETTEENTRY",
    "BYTE",
    "S3TC_ENCODE_RGB_FULL",
    "S3TC_ENCODE_RGB_COLOR_KEY",
    "S3TC_ENCODE_RGB_ALPHA_COMPARE",
    "_S3TC_ENCODE_RGB_MASK",
    "S3TC_ENCODE_ALPHA_NONE",
    "S3TC_ENCODE_ALPHA_EXPLICIT",
    "S3TC_ENCODE_ALPHA_INTERPOLATED",
    "_S3TC_ENCODE_ALPHA_MASK",
    "S3TC_ENCODE_ALPHA_NEED0",
    "S3TC_ENCODE_ALPHA_NEED1",
    "S3TCsetAlphaReference",
    "S3TCgetEncodeSize",
    "S3TCencode",
    "S3TCgetDecodeSize",
    "S3TCdecode",
]
