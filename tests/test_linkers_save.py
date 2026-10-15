"""ULinkerSave must map names/objects through NameIndices/ObjectIndices.

UnLinker.h:317 operator<<(FName&) and UnLinker.h:324 operator<<(UObject*&)
write the operand's index in the save file's tables, not its global index.
The C++ bodies are inline; the Saver plumbing (UnLinker.h:333 Serialize) lives
in Core.lib but forwards to a plain FArchive.
"""

import pytest

from ut99py.core.linkers import ULinkerSave
from ut99py.core.objects import UStruct
from ut99py.core.system import FArchiveFileWriter
from ut99py.core.types import FCompactIndex, FName


def _make_save(tmp_path):
    save = ULinkerSave(None, "test")
    out = tmp_path / "pkg.bin"
    save.saver = FArchiveFileWriter(str(out))
    return save, out


def test_name_operator_writes_the_name_indices_entry(tmp_path):
    # UnLinker.h:317: Save = NameIndices(Name.GetIndex()), written as AR_INDEX.
    save, out = _make_save(tmp_path)
    name = FName("Actor")
    index = name.get_index()
    save.name_indices = [0] * (index + 1)
    save.name_indices[index] = 7

    result = save << name

    assert result is name
    save.saver.close()
    assert out.read_bytes() == FCompactIndex(7).encode()


def test_object_operator_writes_the_object_indices_entry(tmp_path):
    # UnLinker.h:324: Save = ObjectIndices(Obj->GetIndex()).
    save, out = _make_save(tmp_path)
    obj = UStruct()
    index = obj.get_index()
    save.object_indices = [0] * (index + 1)
    save.object_indices[index] = 5

    result = save << obj

    assert result is obj
    save.saver.close()
    assert out.read_bytes() == FCompactIndex(5).encode()


def test_null_object_maps_to_index_zero(tmp_path):
    # UnLinker.h:324: Save = Obj ? ObjectIndices(...) : 0.
    save, out = _make_save(tmp_path)

    assert save.serialize_object(None) is None

    save.saver.close()
    assert out.read_bytes() == FCompactIndex(0).encode()


def test_write_without_a_saver_is_reported():
    # UnLinker.h:306: the C++ dereferences Saver unconditionally.
    save = ULinkerSave(None, "test")
    name = FName("Core")
    save.name_indices = [0] * (name.get_index() + 1)
    with pytest.raises(NotImplementedError):
        save << name
