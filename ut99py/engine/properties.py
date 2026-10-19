"""UE1/UE2 tagged-property block (the property list preceding each export's
native tail).

The tag struct lives in the prebuilt Core.lib; only the entry point is
published (Core/Inc/UnClass.h:237, UStruct::SerializeTaggedProperties). The
byte layout below was derived from the prebuilt serializer, the same way
FCompactIndex was (see core/types.py):

    Name        FName (linker name-table compact index)
    if Name == None: end of the block
    Info        BYTE: bit7 = is-array, bits4-6 = data-size code,
                bits0-3 = EPropType
    StrucName   FName, StructProperty only (read right after Info)
    Size        from the size code: 0..4 -> 1/2/4/12/16 bytes,
                5 -> u8, 6 -> u16, 7 -> i32
    ArrayIndex  if type != Bool and is-array, byte-encoded
    Data        Size bytes (Bool carries its value in the array flag instead)
"""

import struct
from enum import IntEnum
from typing import Any, Dict, Optional

from ..core.linkers import ULinkerLoad
from ..core.objects import FName
from ..core.system import AR_INDEX, FArchiveMemoryReader


class EPropType(IntEnum):
    """Property type ids hardcoded in the prebuilt Core.lib serializer."""

    BYTE = 1
    INT = 2
    BOOL = 3
    FLOAT = 4
    OBJECT = 5
    NAME = 6
    STRING = 7
    CLASS = 8
    ARRAY = 9
    STRUCT = 10
    VECTOR = 11
    ROTATOR = 12
    STR = 13
    MAP = 14
    FIXED_ARRAY = 15


PROP_ARRAY_FLAG = 0x80  # info bit7: IsArray (Bool value when type == BOOL)
PROP_TYPE_MASK = 0x0F
PROP_SIZE_SHIFT = 4
PROP_SIZE_MASK = 0x07
_NONE_NAME = "None"
# Info size codes 0..4 select a fixed payload width; 5..7 read it inline.
_FIXED_SIZES = (1, 2, 4, 12, 16)
_SIZE_CODE_U8 = 5
_SIZE_CODE_U16 = 6
_SIZE_CODE_I32 = 7


class FPropertyTag:
    """One property tag; fields mirror the C++ FPropertyTag."""

    def __init__(self):
        self.name: str = ""
        self.type: EPropType = EPropType.BYTE
        self.size: int = 0
        self.array_index: int = 0
        self.bool_value: bool = False
        self.struc_name: Optional[str] = None


def _read_name(linker: ULinkerLoad) -> str:
    name = FName()
    linker.serialize_name(name)
    return name.name


def _read_array_index(ar) -> int:
    """Byte-encoded ArrayIndex from the prebuilt tag serializer."""
    b = ar.read(1)[0]
    if b < 128:
        return b
    b2 = ar.read(1)[0]
    if b & 0x40:
        b3, b4 = ar.read(1)[0], ar.read(1)[0]
        return ((b << 24) | (b2 << 16) | (b3 << 8) | b4) & 0x3FFFFF
    return ((b << 8) | b2) & 0x3FFF


def read_property_tag(linker: ULinkerLoad) -> Optional[FPropertyTag]:
    """Read one tag at the linker's file cursor; None at block end."""
    ar = linker.loader
    name = _read_name(linker)
    if name == _NONE_NAME:
        return None
    info = ar.read(1)[0]
    tag = FPropertyTag()
    tag.name = name
    tag.type = EPropType(info & PROP_TYPE_MASK)
    if tag.type == EPropType.STRUCT:
        tag.struc_name = _read_name(linker)
    code = (info >> PROP_SIZE_SHIFT) & PROP_SIZE_MASK
    if code < len(_FIXED_SIZES):
        tag.size = _FIXED_SIZES[code]
    elif code == _SIZE_CODE_U8:
        tag.size = ar.read(1)[0]
    elif code == _SIZE_CODE_U16:
        tag.size = int.from_bytes(ar.read(2), "little")
    else:
        tag.size = int.from_bytes(ar.read(4), "little", signed=True)
    tag.bool_value = bool(info & PROP_ARRAY_FLAG)
    if tag.type != EPropType.BOOL and info & PROP_ARRAY_FLAG:
        tag.array_index = _read_array_index(ar)
    return tag


def _decode_value(linker: ULinkerLoad, tag: FPropertyTag, raw: bytes) -> Any:
    """Decode a fixed payload per tag type; unknown shapes stay raw bytes."""
    t = tag.type
    if t == EPropType.BYTE:
        return raw[0]
    if t == EPropType.INT:
        return int.from_bytes(raw, "little", signed=True)
    if t == EPropType.FLOAT:
        return struct.unpack("<f", raw)[0]
    if t in (EPropType.OBJECT, EPropType.CLASS):
        # Object refs are AR_INDEX compact indices (UnLinker.h:266).
        return AR_INDEX(FArchiveMemoryReader(raw), 0)
    if t == EPropType.NAME:
        index = AR_INDEX(FArchiveMemoryReader(raw), 0)
        return linker.name_map[index].name
    if t == EPropType.VECTOR and len(raw) == 12:
        return struct.unpack("<3f", raw)
    if t == EPropType.ROTATOR and len(raw) == 12:
        return struct.unpack("<3i", raw)
    if t in (EPropType.STR, EPropType.STRING):
        # v<64 strings are null-terminated; v>=64 carry a u8 length
        # (see core/linkers.py _load_name_table for the same gate).
        if linker.summary.get_file_version() >= 64 and raw:
            return raw[1 : 1 + raw[0]].decode("latin-1")
        return raw.split(b"\0", 1)[0].decode("latin-1")
    return bytes(raw)


def read_properties(linker: ULinkerLoad) -> Dict[str, Any]:
    """Decode the export's property block into a name -> value dict.

    Array members land under "name[i]" keys; Struct payloads stay raw bytes
    (e.g. Color = 4 bytes R,G,B,A per UnTex.h:42).
    """
    ar = linker.loader
    props: Dict[str, Any] = {}
    while True:
        tag = read_property_tag(linker)
        if tag is None:
            return props
        raw = ar.read(tag.size)
        if len(raw) != tag.size:
            raise ValueError(f"Truncated property {tag.name}")
        key = tag.name
        if tag.array_index != 0:
            key = f"{tag.name}[{tag.array_index}]"
        if tag.type == EPropType.BOOL:
            props[key] = tag.bool_value
        else:
            props[key] = _decode_value(linker, tag, raw)
