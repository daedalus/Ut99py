"""Port of Engine/Inc/Palette.h (0 declared symbols).

Heckbert quantiser used to build paletted textures out of high/true colour
sources. The C++ body is not part of the source tree (the header only
declares the exported entry point), so HeckbertQuantize raises
NotImplementedError.
"""

from __future__ import annotations
from typing import Any

# Source data formats (Palette.h:38-43).
ARGB_8888 = 0
XRGB_8888 = 1
RGB_888 = 2
RGB_565 = 3
ARGB_1555 = 4
ARGB_4444 = 5


def HeckbertQuantize(
    srcdata: Any,
    dstdata: Any,
    paldata: Any,
    srcformat: int,
    nentries: int,
    width: int,
    height: int,
    has_colourkey: int,
    keyval: int,
    generate_mipmaps: int,
) -> int:
    """HeckbertQuantize (Palette.h:18-30)."""
    raise NotImplementedError("C++ HeckbertQuantize: Engine.lib")


__all__ = [
    "ARGB_8888",
    "XRGB_8888",
    "RGB_888",
    "RGB_565",
    "ARGB_1555",
    "ARGB_4444",
    "HeckbertQuantize",
]
