"""Regression: ULinkerLoad must accept a valid UT package tag.

The tag was compared as raw bytes against the literal `0x9E2A83C` — one hex
digit short of `PACKAGE_FILE_TAG` and the wrong type — so every real package
failed to load. Header layout per UnLinker.h:138 (FPackageFileSummary).
"""

import struct

from ut99py.core.linkers import ULinkerLoad
from ut99py.core.objver import PACKAGE_FILE_TAG, VER_GUID_AND_GENERATIONS


def _header(version=VER_GUID_AND_GENERATIONS, guid=(1, 2, 3, 4), generations=((11, 12), (13, 14))):
    data = struct.pack("<I", PACKAGE_FILE_TAG)   # Tag
    data += struct.pack("<i", version)           # FileVersion
    data += struct.pack("<i", 0)                 # PackageFlags
    for _ in range(6):                            # Name/Export/Import count+offset
        data += struct.pack("<i", 0)
    if version >= VER_GUID_AND_GENERATIONS:
        for word in guid:
            data += struct.pack("<I", word)
        data += struct.pack("<i", len(generations))
        for export_count, name_count in generations:
            data += struct.pack("<i", export_count)
            data += struct.pack("<i", name_count)
    return data


def test_valid_header_is_loaded(tmp_path):
    path = tmp_path / "ok.u"
    path.write_bytes(_header())

    linker = ULinkerLoad(None, str(path))

    assert linker.success
    assert linker.summary.tag == PACKAGE_FILE_TAG
    assert linker.summary.get_file_version() == VER_GUID_AND_GENERATIONS
    assert linker.summary.get_file_version_licensee() == 0
    assert (linker.summary.guid.a, linker.summary.guid.b,
            linker.summary.guid.c, linker.summary.guid.d) == (1, 2, 3, 4)
    assert [(g.export_count, g.name_count) for g in linker.summary.generations] == [(11, 12), (13, 14)]


def test_wrong_tag_is_rejected(tmp_path):
    data = bytearray(_header())
    data[0] ^= 0xFF
    path = tmp_path / "bad.u"
    path.write_bytes(bytes(data))

    assert not ULinkerLoad(None, str(path)).success


def test_pre_68_header_has_no_guid_or_generations(tmp_path):
    path = tmp_path / "old.u"
    path.write_bytes(_header(version=VER_GUID_AND_GENERATIONS - 1))

    linker = ULinkerLoad(None, str(path))

    assert linker.success
    assert linker.summary.generations == []
