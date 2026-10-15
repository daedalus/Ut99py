"""FArchive serialization operators, ported from Core/Inc/UnArc.h.

C++ `Ar << X` serializes X in whichever direction the concrete archive was
opened for. Python has no reference arguments, so the operand's runtime type
selects the serializer and the loaded value is returned (callers pass a
placeholder of the intended type as the read target).
"""

import pytest

from ut99py.core.objver import PACKAGE_FILE_VERSION
from ut99py.core.system import (
    FArchive,
    FArchiveFileReader,
    FArchiveFileWriter,
)
from ut99py.core.types import FCompactIndex, FGuid


def test_direction_defaults_match_the_cpp_constructor():
    ar = FArchive()
    assert ar.ver() == PACKAGE_FILE_VERSION
    assert not ar.is_loading()
    assert not ar.is_saving()
    assert ar.is_error() is False
    assert ar.for_edit() and ar.for_client() and ar.for_server()


def test_file_reader_and_writer_set_their_direction(tmp_path):
    # FFileManagerLinux.h: reader sets ArIsLoading=ArIsPersistent=1,
    # writer sets ArIsSaving=ArIsPersistent=1.
    path = str(tmp_path / "dir.bin")
    w = FArchiveFileWriter(path)
    assert w.is_saving() and not w.is_loading() and w.is_persistent()
    w << 0
    w.close()

    r = FArchiveFileReader(path)
    assert r.is_loading() and not r.is_saving() and r.is_persistent()
    r.close()


def test_operator_needs_a_direction():
    with pytest.raises(NotImplementedError):
        FArchive() << 1


def test_primitive_roundtrip(tmp_path):
    path = str(tmp_path / "prims.bin")
    w = FArchiveFileWriter(path)
    w << 0x01020304
    w << 1.5
    w << True
    w.close()

    r = FArchiveFileReader(path)
    assert (r >> 0) == 0x01020304
    assert abs((r >> 0.0) - 1.5) < 1e-6
    assert (r >> False) is True
    r.close()


def test_guid_roundtrip(tmp_path):
    # FGuid serializes as four consecutive ints (UnObjBas.h:190).
    path = str(tmp_path / "guid.bin")
    w = FArchiveFileWriter(path)
    w << FGuid(0x11, 0x22, 0x33, 0x44)
    w.close()

    r = FArchiveFileReader(path)
    out = r >> FGuid()
    assert (out.a, out.b, out.c, out.d) == (0x11, 0x22, 0x33, 0x44)
    r.close()


def test_compact_index_roundtrip_through_archive(tmp_path):
    values = [0, 1, 63, 64, 1000, 16384, 2**31 - 1, -1, -65, -128, -2**31]
    path = str(tmp_path / "ci.bin")
    w = FArchiveFileWriter(path)
    for value in values:
        w << FCompactIndex(value)
    w.close()

    r = FArchiveFileReader(path)
    assert [(r >> FCompactIndex()).value for _ in values] == values
    r.close()


def test_qword_and_sqword_roundtrip(tmp_path):
    # QWORD/SQWORD are 8-byte ints (UnArc.h:182-191, UnGnuG.h:127,136), not
    # doubles: SQWORD must survive a negative value, which a <d packer cannot.
    path = str(tmp_path / "qwords.bin")
    values = [0, 1, 0x0102030405060708, 0xFFFFFFFFFFFFFFFF]
    signed = [0, -1, -0x0102030405060708, 0x7FFFFFFFFFFFFFFF]
    w = FArchiveFileWriter(path)
    for value in values:
        w.serialize_qword(value)
    for value in signed:
        w.serialize_sqword(value)
    w.close()

    with open(path, "rb") as f:
        raw = f.read()
    # values are 0, 1, 0x0102030405060708, 0xffffffffffffffff.
    assert raw[16:24] == bytes([0x08, 0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01])

    r = FArchiveFileReader(path)
    assert [r.serialize_qword(0) for _ in values] == values
    assert [r.serialize_sqword(0) for _ in signed] == signed
    r.close()


def test_unsupported_operand_raises():
    ar = FArchive()
    ar._loading = True
    with pytest.raises(NotImplementedError):
        ar << object()
