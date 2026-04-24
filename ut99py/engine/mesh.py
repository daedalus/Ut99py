from typing import List, Optional
from ut99py.core import FName, UObject, FArchive, UStruct, UProperty, FVector, FRotator
from ut99py.core.types import FBox, FSphere


class UTexture:
    pass


class FMeshVert:
    def __init__(self, x: int = 0, y: int = 0, z: int = 0):
        self.x = x
        self.y = y
        self.z = z

    def vector(self) -> FVector:
        return FVector(self.x, self.y, self.z)

    @staticmethod
    def from_vector(v: FVector) -> 'FMeshVert':
        return FMeshVert(int(v.x), int(v.y), int(v.z))


class FMeshUV:
    def __init__(self, u: int = 0, v: int = 0):
        self.u = u
        self.v = v


class FMeshFloatUV:
    def __init__(self, u: float = 0.0, v: float = 0.0):
        self.u = u
        self.v = v


class FMeshTri:
    def __init__(self):
        self.i_vertex: List[int] = [0, 0, 0]
        self.tex: List[FMeshUV] = [FMeshUV(), FMeshUV(), FMeshUV()]
        self.poly_flags: int = 0
        self.texture_index: int = 0


class FMeshWedge:
    def __init__(self, vertex: int = 0, u: int = 0, v: int = 0):
        self.i_vertex = vertex
        self.tex_uv = FMeshUV(u, v)


class FMeshExtWedge:
    def __init__(self, vertex: int = 0, flags: int = 0, u: float = 0.0, v: float = 0.0):
        self.i_vertex = vertex
        self.flags = flags
        self.tex_uv = FMeshFloatUV(u, v)


class FMeshFace:
    def __init__(self):
        self.i_wedge: List[int] = [0, 0, 0]
        self.material_index: int = 0


class FMeshMaterial:
    def __init__(self):
        self.poly_flags: int = 0
        self.texture_index: int = 0


class FMeshVertConnect:
    def __init__(self):
        self.num_vert_triangles: int = 0
        self.triangle_list_offset: int = 0


class FMeshAnimSeq:
    def __init__(self):
        self.name: FName = FName()
        self.start_key: int = 0
        self.group: FName = FName()
        self.flags: int = 0
        self.num_keys: int = 0


class UMesh(UObject):
    def __init__(self):
        super().__init__()
        self.verts: List[FMeshVert] = []
        self.tris: List[FMeshTri] = []
        self.anim_seqs: List[FMeshAnimSeq] = []
        self.connects: List[FMeshVertConnect] = []
        self.bounding_boxes: List[FBox] = []
        self.bounding_spheres: List[FSphere] = []
        self.vert_links: List[int] = []
        self.textures: List[Optional['UTexture']] = []
        self.texture_lod: List[float] = []
        self.frame_verts: int = 0
        self.anim_frames: int = 0
        self.and_flags: int = 0
        self.or_flags: int = 0
        self.scale: FVector = FVector(1, 1, 1)
        self.origin: FVector = FVector(0, 0, 0)
        self.rot_origin: FRotator = FRotator()
        self.cur_poly: int = -1
        self.cur_vertex: int = -1

    def serialize(self, ar: FArchive) -> 'UMesh':
        super().serialize(ar)
        ar << self.verts
        ar << self.tris
        ar << self.anim_seqs
        ar << self.connects
        ar << self.bounding_boxes
        ar << self.bounding_spheres
        ar << self.vert_links
        ar << self.textures
        ar << self.texture_lod
        ar << self.frame_verts
        ar << self.anim_frames
        ar << self.and_flags
        ar << self.or_flags
        ar << self.scale
        ar << self.origin
        ar << self.rot_origin
        ar << self.cur_poly
        ar << self.cur_vertex
        return self

    def get_anim_seq(self, seq_name: FName) -> Optional[FMeshAnimSeq]:
        for seq in self.anim_seqs:
            if seq.name == seq_name:
                return seq
        return None

    def set_scale(self, new_scale: FVector) -> None:
        self.scale = new_scale


class ULodMesh(UMesh):
    def __init__(self):
        super().__init__()
        self.collapse_point_thus: List[int] = []
        self.face_level: List[int] = []
        self.faces: List[FMeshFace] = []
        self.collapse_wedge_thus: List[int] = []
        self.wedges: List[FMeshWedge] = []
        self.materials: List[FMeshMaterial] = []
        self.special_faces: List[FMeshFace] = []
        self.model_verts: int = 0
        self.special_verts: int = 0
        self.mesh_scale_max: float = 1.0
        self.lod_strength: float = 1.0
        self.lod_min_verts: int = 10
        self.lod_morph: float = 0.0
        self.lod_z_displace: float = 0.0
        self.lod_hysteresis: float = 0.0
        self.remap_animation_verts: List[int] = []
        self.old_frame_verts: int = 0

    def serialize(self, ar: FArchive) -> 'ULodMesh':
        super().serialize(ar)
        ar << self.collapse_point_thus
        ar << self.face_level
        ar << self.faces
        ar << self.collapse_wedge_thus
        ar << self.wedges
        ar << self.materials
        ar << self.special_faces
        ar << self.model_verts
        ar << self.special_verts
        ar << self.mesh_scale_max
        ar << self.lod_strength
        ar << self.lod_min_verts
        ar << self.lod_morph
        ar << self.lod_z_displace
        ar << self.lod_hysteresis
        ar << self.remap_animation_verts
        ar << self.old_frame_verts
        return self


__all__ = [
    'FMeshVert',
    'FMeshUV',
    'FMeshFloatUV',
    'FMeshTri',
    'FMeshWedge',
    'FMeshExtWedge',
    'FMeshFace',
    'FMeshMaterial',
    'FMeshVertConnect',
    'FMeshAnimSeq',
    'UMesh',
    'ULodMesh',
]