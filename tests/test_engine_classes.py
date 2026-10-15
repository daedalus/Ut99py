"""Regression tests for Engine/Inc/UnSkeletalMesh.h port."""
import sys
sys.path.insert(0, "/home/dclavijo/my_code/Ut99py")
from ut99py.engine import (
    VJointPos, FMeshBone, FNamedBone, FNamedBoneBinary,
    AnimInfoBinary, VChunkHeader, VMaterial, VBone,
    VBoneInfIndex, VBoneInfluence, VRawBoneInfluence,
    VQuatAnimKey, AnalogTrack, MotionChunkDigestInfo,
    MotionChunk, TrackDiffs, VVertex, VPoint, VTriangle,
    USkelImport, USkeletalMesh, UAnimation,
)
from ut99py.core import FName, FVector


def test_vjoint_pos():
    vp = VJointPos()
    assert hasattr(vp, "orientation")
    assert hasattr(vp, "position")
    assert hasattr(vp, "length")
    assert hasattr(vp, "x_size")
    assert hasattr(vp, "y_size")
    assert hasattr(vp, "z_size")
    assert vp.length == 0.0


def test_bone_structs():
    mb = FMeshBone(name=FName("test_bone"))
    assert mb.name == FName("test_bone")
    assert mb.parent_index == -1

    nb = FNamedBone(name=FName("named_bone"))
    assert nb.name == FName("named_bone")


def test_vchunk_header():
    vch = VChunkHeader(chunk_id=b"TEST", type_flag=1, data_size=200, data_count=5)
    assert vch.chunk_id == b"TEST"
    assert vch.type_flag == 1
    assert vch.data_size == 200
    assert vch.data_count == 5


def test_vmaterial():
    vm = VMaterial(material_name=b"mat", texture_index=5, poly_flags=0x100,
                   aux_material=2, aux_flags=0x200, lod_bias=10, lod_style=5)
    assert vm.material_name == b"mat"
    assert vm.texture_index == 5
    assert vm.poly_flags == 0x100
    assert vm.aux_material == 2
    assert vm.aux_flags == 0x200
    assert vm.lod_bias == 10
    assert vm.lod_style == 5


if __name__ == "__main__":
    test_vjoint_pos()
    test_bone_structs()
    test_vchunk_header()
    test_vmaterial()
    print("UnSkeletalMesh tests passed.")
