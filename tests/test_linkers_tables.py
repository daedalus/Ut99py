"""ULinkerLoad must read the name, import and export tables.

Table layouts come from UnLinker.h (FObjectExport/FObjectImport/
FPackageFileSummary operators) and Help/PACKAGES.md; the name-table entry
layout follows engine/ut_reader.py, since the C++ body (FNameEntry::operator<<,
UnName.h:45) lives in the prebuilt Core.lib.
"""

import struct

import pytest

from ut99py.core.linkers import ULinkerLoad
from ut99py.core.objver import (
    PACKAGE_FILE_TAG,
    VER_GUID_AND_GENERATIONS,
    VER_SIZED_NAME_TABLE,
)
from ut99py.core.types import FCompactIndex

NAMES = ["None", "Core", "Object", "Class", "MyPackage", "MyClass"]

# Reference values the fixture encodes; see _build_package for where each lands.
IMPORT_CLASS_PACKAGE = 1  # "Core"
IMPORT_CLASS_NAME = 2  # "Object"
IMPORT_OBJECT_NAME = 4  # "MyPackage"
EXPORT_SERIAL_SIZE = 12
EXPORT_SERIAL_OFFSET = 4096
EXPORT_OBJECT_FLAGS = 0x00000004


def _compact(value: int) -> bytes:
    return FCompactIndex(value).encode()


def _name_entry(name: str, sized: bool) -> bytes:
    if sized:
        text = struct.pack("<B", len(name) + 1) + name.encode("latin-1") + b"\x00"
    else:
        text = name.encode("latin-1") + b"\x00"
    return text + struct.pack("<i", 0)  # + NameFlags


def _build_package(version=VER_GUID_AND_GENERATIONS, object_name_index=5):
    sized = version >= VER_SIZED_NAME_TABLE
    name_table = b"".join(_name_entry(n, sized) for n in NAMES)

    imports = (
        _compact(IMPORT_CLASS_PACKAGE)
        + _compact(IMPORT_CLASS_NAME)
        + struct.pack("<i", 0)  # PackageIndex
        + _compact(IMPORT_OBJECT_NAME)
    )
    exports = (
        _compact(-1)
        + _compact(0)
        + struct.pack("<i", 1)
        + _compact(object_name_index)
        + struct.pack("<I", EXPORT_OBJECT_FLAGS)
        + _compact(EXPORT_SERIAL_SIZE)
        + _compact(EXPORT_SERIAL_OFFSET)
        # Second export: SerialSize 0, so no SerialOffset is written.
        + _compact(-1)
        + _compact(0)
        + struct.pack("<i", 1)
        + _compact(3)
        + struct.pack("<I", 0)
        + _compact(0)
    )

    if version >= VER_GUID_AND_GENERATIONS:
        trailer = (
            struct.pack("<IIII", 1, 2, 3, 4)
            + struct.pack("<i", 1)
            + struct.pack("<ii", 2, 6)
        )
    else:
        trailer = struct.pack("<ii", 0, 0)  # HeritageCount, HeritageOffset

    header_size = 36 + len(trailer)
    name_offset = header_size
    import_offset = name_offset + len(name_table)
    export_offset = import_offset + len(imports)

    header = (
        struct.pack("<I", PACKAGE_FILE_TAG)
        + struct.pack("<i", version)
        + struct.pack("<i", 0)  # PackageFlags
        + struct.pack("<ii", len(NAMES), name_offset)
        + struct.pack("<ii", 2, export_offset)
        + struct.pack("<ii", 1, import_offset)
        + trailer
    )
    return header + name_table + imports + exports


def _write(tmp_path, name, data):
    path = tmp_path / name
    path.write_bytes(data)
    return str(path)


def test_full_package_decodes(tmp_path):
    linker = ULinkerLoad(None, _write(tmp_path, "full.u", _build_package()))

    assert linker.success
    assert [str(n) for n in linker.name_map] == NAMES

    assert len(linker.import_map) == 1
    imp = linker.import_map[0]
    assert (imp.class_package.name, imp.class_name.name, imp.object_name.name) == (
        "Core",
        "Object",
        "MyPackage",
    )
    assert imp.package_index == 0

    assert len(linker.export_map) == 2
    first, second = linker.export_map
    assert (first.class_index, first.super_index, first.package_index) == (-1, 0, 1)
    assert first.object_name.name == "MyClass"
    assert first.object_flags == EXPORT_OBJECT_FLAGS
    assert (first.serial_size, first.serial_offset) == (
        EXPORT_SERIAL_SIZE,
        EXPORT_SERIAL_OFFSET,
    )
    # SuperIndex/PackageIndex prove the mixture of compact and plain ints.
    assert (second.class_index, second.super_index, second.package_index) == (-1, 0, 1)
    assert second.object_name.name == "Class"
    assert (second.serial_size, second.serial_offset) == (0, 0)


def test_export_object_name_resolves_through_the_name_table(tmp_path):
    data = _build_package(object_name_index=1)  # "Core" instead of "MyClass"
    linker = ULinkerLoad(None, _write(tmp_path, "ref.u", data))

    assert linker.success
    assert linker.export_map[0].object_name.name == "Core"


def test_out_of_range_name_index_is_rejected(tmp_path):
    # UnLinker.h:283 appErrorf()s on a bad name index; the port must not
    # silently hand back a wrong or aliased FName.
    linker = ULinkerLoad(
        None, _write(tmp_path, "bad.u", _build_package(object_name_index=99))
    )
    assert not linker.success


@pytest.mark.parametrize("version", [68, 69])
def test_guid_and_generations_decode(tmp_path, version):
    linker = ULinkerLoad(
        None, _write(tmp_path, f"v{version}.u", _build_package(version=version))
    )

    assert linker.success
    assert linker.summary.get_file_version() == version
    assert (
        linker.summary.guid.a,
        linker.summary.guid.b,
        linker.summary.guid.c,
        linker.summary.guid.d,
    ) == (1, 2, 3, 4)
    assert [(g.export_count, g.name_count) for g in linker.summary.generations] == [
        (2, 6)
    ]


def test_sized_name_table_is_gated_on_version(tmp_path):
    # Below VER_SIZED_NAME_TABLE the names are NUL-terminated instead of
    # size-prefixed, so a wrong gate shifts every following table.
    assert VER_SIZED_NAME_TABLE <= VER_GUID_AND_GENERATIONS
    linker = ULinkerLoad(None, _write(tmp_path, "v63.u", _build_package(version=63)))

    assert linker.success
    assert [str(n) for n in linker.name_map] == NAMES
    # oldver synthesizes one generation from the header counts.
    assert [(g.export_count, g.name_count) for g in linker.summary.generations] == [
        (2, 6)
    ]
