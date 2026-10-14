"""Pin object/pakage version constants to Core/Inc/UnObjVer.h."""

import struct

from ut99py.core.objver import (
    ENGINE_MIN_NET_VERSION,
    ENGINE_NEGOTIATION_VERSION,
    ENGINE_VERSION,
    PACKAGE_FILE_TAG,
    PACKAGE_FILE_VERSION,
    PACKAGE_FILE_VERSION_LICENSEE,
    PACKAGE_MIN_VERSION,
    VERSION_ENGINE_ONLY,
)


def test_engine_versions_match_header():
    assert ENGINE_MIN_NET_VERSION == 400
    assert ENGINE_VERSION == 430
    assert ENGINE_NEGOTIATION_VERSION == 400


def test_package_versions_match_header():
    assert PACKAGE_FILE_VERSION == 69
    assert PACKAGE_MIN_VERSION == 60
    assert PACKAGE_FILE_VERSION_LICENSEE == 0x00
    assert VERSION_ENGINE_ONLY == 0x00


def test_package_tag_bytes_are_the_ut_signature():
    # Unreal packages start with 0x9E2A83C1 little-endian: C1 83 2A 9E.
    assert struct.pack("<I", PACKAGE_FILE_TAG) == b"\xc1\x83\x2a\x9e"
