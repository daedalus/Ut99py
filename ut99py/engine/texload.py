"""Texture and palette deserialization from export serial data.

Decodes the on-disk layout produced by the C++ serializers declared in
Engine/Inc/UnTex.h (UTexture/UBitmap/UPalette/FMipmap/FColor) on top of the
tagged-property block (see engine/properties.py). A texture export is:

    [tagged properties, ended by None]
    [mips: TArray<FMipmap> compact count, then per mip the FMipmap
     operator<< order -- DataArray first, then USize/VSize (INT) and
     UBits/VBits (BYTE), UnTex.h:204]

The mip DataArray is a TLazyArray<BYTE> (Core/Inc/UnTemplate.h:1043): for
v<=61 it stores a compact byte count before the data ("oldver"), for v>=62 an
INT32 absolute end position followed by the array. A palette export is the
tagged block followed by TArray<FColor> (count + R,G,B,A bytes).
"""

from typing import Optional

import numpy as np

from ..core.linkers import FObjectExport, ULinkerLoad
from ..core.system import AR_INDEX
from .properties import read_properties
from .texture import NUM_PAL_COLORS, FColor, FMipmap, UPalette, UTexture

# Object-reference indices (PACKAGES.md:799): 0 = NULL, positive = 1-based
# export index, negative = import (-Index-1).
_NULL_INDEX = 0

# Tagged property names that map 1:1 onto ported UTexture/UBitmap attributes.
_PROP_ATTRS = {
    "Format": "format",
    "UBits": "u_bits",
    "VBits": "v_bits",
    "USize": "u_size",
    "VSize": "v_size",
    "UClamp": "u_clamp",
    "VClamp": "v_clamp",
    "PolyFlags": "poly_flags",
    "Diffuse": "diffuse",
    "Specular": "specular",
    "Alpha": "alpha",
    "Scale": "scale",
    "Friction": "friction",
    "LODSet": "lod_set",
    "PrimeCount": "prime_count",
    "MinFrameRate": "min_frame_rate",
    "MaxFrameRate": "max_frame_rate",
    "bHighColorQuality": "b_high_color_quality",
    "bHighTextureQuality": "b_high_texture_quality",
    "bRealtime": "b_realtime",
    "bParametric": "b_parametric",
    "bRealtimeChanged": "b_realtime_changed",
    "bHasComp": "b_has_comp",
}
# Struct Color payloads (4 bytes R,G,B,A, UnTex.h:42) go to FColor attrs.
_COLOR_PROPS = {
    "MipZero": "mip_zero",
    "MaxColor": "max_color",
}
_PALETTE_PROP = "Palette"
# Class-name suffix of texture exports (Texture, FireTexture, WetTexture);
# the class itself is usually an import from Engine.
_TEXTURE_CLASS_SUFFIX = "Texture"


def is_texture_export(linker: ULinkerLoad, export: FObjectExport) -> bool:
    """True when the export's class is a texture subclass.

    Local (script-defined) classes return False: their native tail layout is
    unknown here.
    """
    if export.class_index >= _NULL_INDEX:
        return False
    cls = linker.import_map[-export.class_index - 1].object_name.name
    return cls.endswith(_TEXTURE_CLASS_SUFFIX)


def resolve_export(linker: ULinkerLoad, index: int) -> Optional[FObjectExport]:
    """Resolve an object-reference index to a local export.

    Imports need a cross-package load and return None here.
    """
    if index > _NULL_INDEX:
        return linker.export_map[index - 1]
    return None


def _read_lazy_byte_array(ar, ver: int) -> bytearray:
    """TLazyArray<BYTE> load path (Core/Inc/UnTemplate.h:1057)."""
    if ver <= 61:
        # oldver: compact byte count, then the raw bytes.
        count = AR_INDEX(ar, 0)
        return bytearray(ar.read(count))
    # v>=62: INT32 absolute end position, then the TArray (compact count +
    # bytes); the count/data span must land exactly on it.
    end_pos = int.from_bytes(ar.read(4), "little", signed=True)
    count = AR_INDEX(ar, 0)
    data = bytearray(ar.read(count))
    if ar.tell() != end_pos:
        raise ValueError(f"Lazy array ended at {ar.tell()}, tag said {end_pos}")
    return data


def _apply_props(tex: UTexture, props: dict) -> None:
    for name, attr in _PROP_ATTRS.items():
        if name in props:
            setattr(tex, attr, props[name])
    for name, attr in _COLOR_PROPS.items():
        raw = props.get(name)
        if isinstance(raw, (bytes, bytearray)) and len(raw) == 4:
            setattr(tex, attr, FColor(raw[0], raw[1], raw[2], raw[3]))
    # Remaining script vars (bMasked, Detail, AnimNext, ...) stay in props.
    tex.props = props


def load_palette(linker: ULinkerLoad, export: FObjectExport) -> UPalette:
    """Deserialize a Palette export (native tail = TArray<FColor>)."""
    ar = linker.loader
    ar.seek(export.serial_offset)
    read_properties(linker)  # palettes carry no script properties
    palette = UPalette()
    palette._name = export.object_name
    count = AR_INDEX(ar, 0)
    raw = ar.read(count * 4)
    if len(raw) != count * 4:
        raise ValueError(f"Truncated palette {export.object_name.name}")
    palette.colors = [
        FColor(raw[i], raw[i + 1], raw[i + 2], raw[i + 3])
        for i in range(0, len(raw), 4)
    ]
    return palette


def load_texture(linker: ULinkerLoad, export: FObjectExport) -> UTexture:
    """Deserialize one texture-class export (properties + native mips).

    Fire/Wet textures share this layout; their script-side fields stay in
    `tex.props`.
    """
    ar = linker.loader
    ar.seek(export.serial_offset)
    tex = UTexture()
    tex._name = export.object_name
    _apply_props(tex, read_properties(linker))
    if tex.b_has_comp:
        # CompMips/CompFormat after the mip chain is unverified; stock UT99
        # textures never set bHasComp (empirically the stream ends with mips).
        raise NotImplementedError(f"{export.object_name.name}: bHasComp")
    ver = linker.summary.get_file_version()
    mip_count = AR_INDEX(ar, 0)
    for _ in range(mip_count):
        data = _read_lazy_byte_array(ar, ver)
        mip = _read_mip(ar, data)
        tex.mips.append(mip)
    palette_export = resolve_export(linker, tex.props.get(_PALETTE_PROP, 0))
    if palette_export is not None:
        tex.palette = load_palette(linker, palette_export)
    return tex


def _read_mip(ar, data: bytearray) -> FMipmap:
    """Tail of the FMipmap operator<< after DataArray (UnTex.h:204)."""
    u_size = int.from_bytes(ar.read(4), "little", signed=True)
    v_size = int.from_bytes(ar.read(4), "little", signed=True)
    u_bits = ar.read(1)[0]
    v_bits = ar.read(1)[0]
    mip = FMipmap(u_bits, v_bits)
    mip.u_size = u_size
    mip.v_size = v_size
    mip.data_array = data
    return mip


def texture_to_rgba(tex: UTexture) -> Optional[np.ndarray]:
    """Decode mip 0 through the palette into an (V, U, 4) uint8 array.

    Returns None for parametric/fire textures (no stored pixels) or when the
    palette lives in another package.
    """
    if not tex.mips or not tex.mips[0].data_array:
        return None
    palette = tex.palette
    if palette is None or len(palette.colors) != NUM_PAL_COLORS:
        return None
    mip = tex.mips[0]
    expected = mip.u_size * mip.v_size
    if len(mip.data_array) != expected:
        raise ValueError(
            f"{tex._name.name}: mip0 {len(mip.data_array)} bytes, expected {expected}"
        )
    lut = np.array([[c.r, c.g, c.b, c.a] for c in palette.colors], dtype=np.uint8)
    indices = np.frombuffer(bytes(mip.data_array), dtype=np.uint8)
    return lut[indices].reshape((mip.v_size, mip.u_size, 4))
