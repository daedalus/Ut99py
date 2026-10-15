"""Validate the linker port against real UT99 packages.

The layouts under test come from UnLinker.h, UnArc.h and Help/PACKAGES.md.
engine/ut_reader.py is a second, independently written decoder of the same
format, so it serves as a differential oracle for the tables -- but it shares
the name-table version gate with core/linkers.py, so test_name_table_shapes
reads that layout straight off disk instead.

UT99_GAME_DIR points at another install; the module skips when it is absent.
A stock install covers package versions 61-69, i.e. both sides of
VER_SIZED_NAME_TABLE (64) and VER_GUID_AND_GENERATIONS (68).

engine/ut_reader.py keeps a whole package in memory, so the differential runs
on the three engine packages rather than the whole install.
"""

import os
import struct
from pathlib import Path

import pytest

from ut99py.core import objects
from ut99py.core.linkers import ULinkerLoad
from ut99py.core.objects import (
    PKG_AllowDownload,
    RF_LoadForClient,
    RF_Public,
    RF_Transactional,
)
from ut99py.core.objver import (
    PACKAGE_FILE_TAG,
    VER_GUID_AND_GENERATIONS,
    VER_SIZED_NAME_TABLE,
)
from ut99py.engine.ut_reader import PackageReader

GAME_DIR = Path(
    os.environ.get("UT99_GAME_DIR", "/home/dclavijo/Games/UnrealTournament")
)
SYSTEM_DIR = GAME_DIR / "System"

PACKAGE_SUFFIXES = (".u", ".utx", ".unr", ".umx", ".uax")

# Header is 9 x INT32, then (pre-68) INT32 HeritageCount, INT32 HeritageOffset,
# then one 16-byte GUID, then the name table.
OLDVER_HEADER_SIZE = 36
OLDVER_HERITAGE_GUID_SIZE = 16
OLDVER_NAME_OFFSET = OLDVER_HEADER_SIZE + 8 + OLDVER_HERITAGE_GUID_SIZE

# UT99's root classes; the stock packages that declare them are known.
STOCK_EXPORTS = {
    "Core.u": ("Object", "Class"),
    "Engine.u": ("Actor", "GameInfo", "Level", "Texture", "Palette"),
    "BotPack.u": ("Bot", "DeathMatchPlus", "CTFGame"),
}

pytestmark = pytest.mark.skipif(
    not (SYSTEM_DIR / "Core.u").is_file(),
    reason=f"no UT99 install at {GAME_DIR} (set UT99_GAME_DIR)",
)

PACKAGE_PATHS = sorted(
    p for p in GAME_DIR.glob("*/*") if p.suffix.lower() in PACKAGE_SUFFIXES
)
SYSTEM_PATHS = sorted(SYSTEM_DIR.glob("*.u"))

_LINKERS = {}


def load(path: Path) -> ULinkerLoad:
    linker = _LINKERS.get(path)
    if linker is None:
        linker = ULinkerLoad(None, str(path))
        _LINKERS[path] = linker
    assert linker.success, f"{path} failed to load"
    return linker


def file_version(path: Path) -> int:
    """Low WORD of the header's Version DWORD; the high WORD is the licensee."""
    with open(path, "rb") as fh:
        fh.seek(4)
        return int.from_bytes(fh.read(2), "little")


def oldver_paths() -> list:
    return [p for p in PACKAGE_PATHS if file_version(p) < VER_GUID_AND_GENERATIONS]


def guid_bytes(guid) -> str:
    """FGuid as it sits on disk: four little-endian dwords."""
    return "".join(
        struct.pack("<I", dword & 0xFFFFFFFF).hex()
        for dword in (guid.a, guid.b, guid.c, guid.d)
    ).upper()


def reference(path: Path) -> PackageReader:
    reader = PackageReader(str(path))
    reader.read_package()
    return reader


def import_row(linker: ULinkerLoad, i: int) -> tuple:
    imp = linker.import_map[i]
    return (
        imp.class_package.name,
        imp.class_name.name,
        imp.package_index,
        imp.object_name.name,
    )


def export_row(linker: ULinkerLoad, i: int) -> tuple:
    exp = linker.export_map[i]
    return (
        exp.class_index,
        exp.super_index,
        exp.package_index,
        exp.object_name.name,
        exp.object_flags,
        exp.serial_size,
        exp.serial_offset,
    )


def reference_imports(reader: PackageReader) -> list:
    names = reader.get_name_table()
    return [
        (
            names[i["class_package_index"]]["name"],
            names[i["class_name_index"]]["name"],
            i["package_index"],
            names[i["object_name_index"]]["name"],
        )
        for i in reader.get_import_table()
    ]


def reference_exports(reader: PackageReader) -> list:
    names = reader.get_name_table()
    return [
        (
            e["class_index"],
            e["super_index"],
            e["package_index"],
            names[e["object_name_index"]]["name"],
            e["object_flags"],
            e["serial_size"],
            e["serial_offset"],
        )
        for e in reader.get_export_table()
    ]


def test_core_header_is_a_version_69_package():
    summary = load(SYSTEM_DIR / "Core.u").summary
    assert summary.tag & 0xFFFFFFFF == PACKAGE_FILE_TAG
    assert summary.get_file_version() == 69
    assert summary.name_offset > 0
    assert summary.export_offset > 0
    assert summary.import_offset > 0


def test_table_lengths_match_the_header_counts():
    for package in ("Core.u", "Engine.u", "BotPack.u"):
        linker = load(SYSTEM_DIR / package)
        summary = linker.summary
        assert len(linker.name_map) == summary.name_count
        assert len(linker.import_map) == summary.import_count
        assert len(linker.export_map) == summary.export_count


@pytest.mark.parametrize("package", sorted(STOCK_EXPORTS))
def test_stock_classes_are_exported(package):
    exported = {e.object_name.name for e in load(SYSTEM_DIR / package).export_map}
    assert not [c for c in STOCK_EXPORTS[package] if c not in exported]


@pytest.mark.parametrize("package", ["Core.u", "Engine.u", "BotPack.u"])
def test_tables_match_the_reference_decoder(package):
    linker = load(SYSTEM_DIR / package)
    reader = reference(SYSTEM_DIR / package)

    assert [n.name for n in linker.name_map] == [
        n["name"] for n in reader.get_name_table()
    ]
    assert [
        import_row(linker, i) for i in range(len(linker.import_map))
    ] == reference_imports(reader)
    assert [
        export_row(linker, i) for i in range(len(linker.export_map))
    ] == reference_exports(reader)


def test_name_table_shapes():
    """Read each entry's first bytes to pin the two on-disk shapes.

    Below VER_SIZED_NAME_TABLE the entry is a bare NUL-terminated string; from
    it on, a one-byte length (count including the NUL) precedes the text. Both
    were only covered by synthetic fixtures before.
    """
    seen = set()
    for path in PACKAGE_PATHS:
        linker = load(path)
        version = linker.summary.get_file_version()
        name = linker.name_map[0].name
        seen.add((version >= VER_SIZED_NAME_TABLE, version))

        with open(path, "rb") as fh:
            fh.seek(linker.summary.name_offset)
            head = fh.read(64)

        if version >= VER_SIZED_NAME_TABLE:
            assert head[0] == len(name) + 1
            assert head[1 : 1 + len(name)].decode("latin-1") == name
            assert head[1 + len(name)] == 0
        else:
            assert head.split(b"\x00", 1)[0].decode("latin-1") == name

    assert {sized for sized, _ in seen} == {False, True}


def test_oldver_packages_synthesise_one_generation():
    """Pre-68 files carry a heritage GUID instead of a generation table.

    UnLinker.h:158: the GUID list sits behind HeritageOffset and the linker
    synthesises one generation from the table counts it just read.
    """
    paths = oldver_paths()
    assert paths, "install has no pre-68 packages"
    for path in paths:
        summary = load(path).summary
        assert summary.get_file_version() == file_version(path)
        assert len(summary.generations) == 1
        assert (
            summary.generations[0].export_count,
            summary.generations[0].name_count,
        ) == (summary.export_count, summary.name_count)
        # The heritage GUID is real data, not a zero-filled field.
        assert (summary.guid.a, summary.guid.b, summary.guid.c, summary.guid.d) != (
            0,
            0,
            0,
            0,
        )
        assert summary.name_offset == OLDVER_NAME_OFFSET


def test_versioned_headers_match_the_reference_decoder():
    """The GUID + generation list from version 68 on (UnLinker.h:100).

    engine/ut_reader.py decodes the same bytes; the header is the part of the
    file where it can disagree without the table offsets covering it up.
    """
    paths = [p for p in SYSTEM_PATHS if file_version(p) >= VER_GUID_AND_GENERATIONS]
    assert paths, "install has no versioned System packages"
    for path in paths:
        summary = load(path).summary
        header = PackageReader(str(path)).get_package_header()
        assert guid_bytes(summary.guid) == header["guid"], path
        assert [(g.export_count, g.name_count) for g in summary.generations] == [
            (g["export_count"], g["name_count"]) for g in header["generations"]
        ], path


def test_every_package_loads():
    assert len(PACKAGE_PATHS) >= 100
    for path in PACKAGE_PATHS:
        linker = load(path)
        summary = linker.summary
        assert len(linker.name_map) == summary.name_count, path
        assert len(linker.import_map) == summary.import_count, path
        assert len(linker.export_map) == summary.export_count, path


def _defined_bits(prefix: str) -> int:
    """OR of every named constant with this prefix (UnObjBas.h enums).

    A bit is "defined" iff some EObjectFlags/EPackageFlags member carries it,
    aliases included; combo constants like RF_Load are subsets and harmless.
    """
    total = 0
    for name, value in vars(objects).items():
        if name.startswith(prefix) and isinstance(value, int):
            total |= value
    return total


def test_export_object_flags_use_only_defined_bits():
    """Every FObjectExport.ObjectFlags value is a UT99 EObjectFlags bit.

    The port once carried the UT2003 layout (RF_Public=0x1); real packages use
    0x4, so this catches a regression straight off disk.
    """
    mask = _defined_bits("RF_")
    seen = 0
    for path in PACKAGE_PATHS:
        for export in load(path).export_map:
            undefined = export.object_flags & ~mask
            assert undefined == 0, (path, export.object_name.name, hex(undefined))
            seen |= export.object_flags
    # The install exercises the common load flags, not just one bit.
    assert seen & RF_Public
    assert seen & RF_Transactional
    assert seen & RF_LoadForClient


def test_package_flags_use_only_defined_bits():
    """FPackageFileSummary.PackageFlags holds only UT99 EPackageFlags bits."""
    mask = _defined_bits("PKG_")
    seen = 0
    for path in PACKAGE_PATHS:
        flags = load(path).summary.package_flags
        undefined = flags & ~mask
        assert undefined == 0, (path, hex(undefined))
        seen |= flags
    assert seen & PKG_AllowDownload
