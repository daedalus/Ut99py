"""UnTemplate.h serializers: TArray and FString.

TArray's operators are inline in the header (UnTemplate.h:435, plus the
TArray<BYTE> specialization at :686). FString's is CORE_API (UnTemplate.h:1403,
body in the prebuilt Core.lib), so its on-disk layout is taken from
Help/PACKAGES.md:656 -- "a bunch of characters (one nonzero byte each)
terminated by a zero byte" -- which is also what engine/ut_reader.py's
_read_string decodes.
"""

import struct

import pytest

from ut99py.core.linkers import FGenerationInfo
from ut99py.core.system import FArchiveFileWriter, FArchiveMemoryReader
from ut99py.core.types import FCompactIndex, FString


def _write(tmp_path, fn) -> bytes:
    path = tmp_path / "out.bin"
    ar = FArchiveFileWriter(str(path))
    fn(ar)
    ar.close()
    return path.read_bytes()


def test_fstring_is_nul_terminated_ansi(tmp_path):
    data = _write(tmp_path, lambda ar: ar.serialize_str(FString("System\\Setup.dll")))
    assert data == b"System\\Setup.dll\x00"


def test_fstring_round_trips(tmp_path):
    for text in ("", "A", "Skins\\CommandoSkins.utx"):
        data = _write(tmp_path, lambda ar, t=text: ar.serialize_str(FString(t)))
        assert FArchiveMemoryReader(data).serialize_str(FString()) == text


def test_tarray_of_int32_is_element_wise(tmp_path):
    data = _write(tmp_path, lambda ar: ar.serialize_tarray([10, 20, 30], element=int))
    assert data == b"\x03" + struct.pack("<iii", 10, 20, 30)

    loaded = []
    FArchiveMemoryReader(data).serialize_tarray(loaded, element=int)
    assert loaded == [10, 20, 30]


def test_tarray_byte_specialization_writes_a_raw_buffer(tmp_path):
    # UnTemplate.h:686: sizeof(T)==1 skips construction and serialises the buffer.
    data = _write(tmp_path, lambda ar: ar.serialize_tarray([1, 2, 255], element_size=1))
    assert data == b"\x03\x01\x02\xff"

    loaded = []
    FArchiveMemoryReader(data).serialize_tarray(loaded, element_size=1)
    assert loaded == [1, 2, 255]


def test_tarray_count_is_a_compact_index(tmp_path):
    values = list(range(64))
    data = _write(tmp_path, lambda ar: ar.serialize_tarray(values, element_size=1))

    count = FCompactIndex(len(values)).encode()
    assert len(count) > 1  # 64 needs more than the low six bits
    assert data == count + bytes(values)


def test_tarray_of_structs_uses_each_elements_operator(tmp_path):
    # FGenerationInfo's operator<< is UnLinker.h:102: two INTs per element.
    items = [FGenerationInfo(1, 2), FGenerationInfo(3, 4)]
    data = _write(
        tmp_path, lambda ar: ar.serialize_tarray(items, element=FGenerationInfo)
    )
    assert data == b"\x02" + struct.pack("<iiii", 1, 2, 3, 4)

    loaded = []
    FArchiveMemoryReader(data).serialize_tarray(loaded, element=FGenerationInfo)
    assert [(g.export_count, g.name_count) for g in loaded] == [(1, 2), (3, 4)]


def test_tarray_load_without_an_element_factory_fails_loudly():
    # The stream carries no element type, so loading must not guess one.
    data = b"\x01" + struct.pack("<i", 5)
    with pytest.raises(NotImplementedError):
        FArchiveMemoryReader(data).serialize_tarray([])
