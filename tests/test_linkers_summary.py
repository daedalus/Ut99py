"""Regression: ULinkerLoad must accept a valid UT package tag.

The tag was compared as raw bytes against the literal `0x9E2A83C` — one hex
digit short of `PACKAGE_FILE_TAG` and the wrong type — so every real package
failed to load. Header layout per UnLinker.h:138 (FPackageFileSummary).
"""

import struct

from ut99py.core.linkers import ULinkerLoad
from ut99py.core.objver import PACKAGE_FILE_TAG, VER_GUID_AND_GENERATIONS


def _header(
    version=VER_GUID_AND_GENERATIONS,
    guid=(1, 2, 3, 4),
    generations=((11, 12), (13, 14)),
    heritage=(0, 0),
):
    data = struct.pack("<I", PACKAGE_FILE_TAG)  # Tag
    data += struct.pack("<i", version)  # FileVersion
    data += struct.pack("<i", 0)  # PackageFlags
    data += struct.pack("<ii", 6, 0)  # NameCount, NameOffset
    data += struct.pack("<ii", 2, 0)  # ExportCount, ExportOffset
    data += struct.pack("<ii", 0, 0)  # ImportCount, ImportOffset
    if version >= VER_GUID_AND_GENERATIONS:
        for word in guid:
            data += struct.pack("<I", word)
        data += struct.pack("<i", len(generations))
        for export_count, name_count in generations:
            data += struct.pack("<ii", export_count, name_count)
    else:
        data += struct.pack("<ii", *heritage)  # HeritageCount, HeritageOffset
    return data


def _guid(*words):
    return b"".join(struct.pack("<I", word) for word in words)


def test_valid_header_is_loaded(tmp_path):
    path = tmp_path / "ok.u"
    path.write_bytes(_header())

    linker = ULinkerLoad(None, str(path))

    assert linker.success
    # Tag is an INT on disk (UnLinker.h:113), so it reads back negative.
    assert linker.summary.tag & 0xFFFFFFFF == PACKAGE_FILE_TAG
    assert linker.summary.get_file_version() == VER_GUID_AND_GENERATIONS
    assert linker.summary.get_file_version_licensee() == 0
    assert (
        linker.summary.guid.a,
        linker.summary.guid.b,
        linker.summary.guid.c,
        linker.summary.guid.d,
    ) == (1, 2, 3, 4)
    assert [(g.export_count, g.name_count) for g in linker.summary.generations] == [
        (11, 12),
        (13, 14),
    ]


def test_wrong_tag_is_rejected(tmp_path):
    data = bytearray(_header())
    data[0] ^= 0xFF
    path = tmp_path / "bad.u"
    path.write_bytes(bytes(data))

    assert not ULinkerLoad(None, str(path)).success


def test_pre_68_header_synthesizes_one_generation(tmp_path):
    # oldver branch (UnLinker.h:158): no Guid/Generations on disk; one
    # generation is built from the header's own ExportCount/NameCount.
    path = tmp_path / "old.u"
    path.write_bytes(_header(version=VER_GUID_AND_GENERATIONS - 1))

    linker = ULinkerLoad(None, str(path))

    assert linker.success
    assert [(g.export_count, g.name_count) for g in linker.summary.generations] == [
        (2, 6)
    ]


def test_pre_68_heritage_guids_come_from_their_offset(tmp_path):
    """The heritage list lives at HeritageOffset, not right after the fields.

    UnLinker.h:158 seeks there and reads HeritageCount GUIDs into Sum.Guid, so
    the last one in the list is what remains.
    """
    filler = _guid(0x0EAD0001, 0x0EAD0002, 0x0EAD0003, 0x0EAD0004)
    first = (0xA1, 0xA2, 0xA3, 0xA4)
    last = (0xB1, 0xB2, 0xB3, 0xB4)

    header = _header(
        version=VER_GUID_AND_GENERATIONS - 1, heritage=(2, 44 + len(filler))
    )
    assert len(header) == 44
    path = tmp_path / "heritage.u"
    path.write_bytes(header + filler + _guid(*first) + _guid(*last))

    linker = ULinkerLoad(None, str(path))

    assert linker.success
    # Dropping the seek would start at 44 and yield `first` instead.
    assert (
        linker.summary.guid.a,
        linker.summary.guid.b,
        linker.summary.guid.c,
        linker.summary.guid.d,
    ) == last


def test_pre_68_unbacked_heritage_count_is_not_followed(tmp_path):
    """A count the file cannot back must not spin the loader.

    Deviation from UnLinker.h:158, which runs the loop for whatever
    HeritageCount says; the Guid simply stays empty here.
    """
    path = tmp_path / "bogus.u"
    path.write_bytes(
        _header(version=VER_GUID_AND_GENERATIONS - 1, heritage=(2**30, 44))
    )

    linker = ULinkerLoad(None, str(path))

    assert linker.success
    assert (
        linker.summary.guid.a,
        linker.summary.guid.b,
        linker.summary.guid.c,
        linker.summary.guid.d,
    ) == (0, 0, 0, 0)
