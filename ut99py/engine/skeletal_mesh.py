"""Port of Engine/Inc/UnSkeletalMesh.h (22 declared symbols).

Skeletal mesh data structures: bone hierarchies, animation tracks,
vertex formats, and the USkeletalMesh/UAnimation classes. C++ event
dispatch / ProcessEvent bodies raise NotImplementedError; persistence
is handled by the prebuilt Engine.lib serializer path.
"""
from typing import List, Optional
from ..core import UObject, UClass, FName, FArchive, FVector, FQuat
from ..engine.mesh import ULodMesh

# ------------------------------------------------------------------
# VJointPos: a bone's orientation + position relative to its parent
# ------------------------------------------------------------------
class VJointPos:
    def __init__(self, orientation=None, position=None, length=0.0,
                 x_size=0.0, y_size=0.0, z_size=0.0):
        self.orientation = orientation or FQuat()
        self.position = position or FVector()
        self.length = length
        self.x_size = x_size
        self.y_size = y_size
        self.z_size = z_size


# ------------------------------------------------------------------
# FMeshBone: reference-skeleton bone (package-serializable)
# ------------------------------------------------------------------
class FMeshBone:
    def __init__(self, name: FName = FName(), flags: int = 0,
                 bone_pos: Optional['VJointPos'] = None,
                 parent_index: int = -1, num_children: int = 0,
                 depth: int = 0):
        self.name = name
        self.flags = flags
        self.bone_pos = bone_pos or VJointPos()
        self.parent_index = parent_index
        self.num_children = num_children
        self.depth = depth


# ------------------------------------------------------------------
# FNamedBone: named bone for animating skeleton
# ------------------------------------------------------------------
class FNamedBone:
    def __init__(self, name: FName = FName(), flags: int = 0,
                 parent_index: int = -1):
        self.name = name
        self.flags = flags
        self.parent_index = parent_index


# ------------------------------------------------------------------
# FNamedBoneBinary: binary bone format
# ------------------------------------------------------------------
class FNamedBoneBinary:
    def __init__(self, name: bytes = b'', flags: int = 0,
                 num_children: int = 0, parent_index: int = -1):
        self.name = name
        self.flags = flags
        self.num_children = num_children
        self.parent_index = parent_index


# ------------------------------------------------------------------
# AnimInfoBinary: binary animation info format
# ------------------------------------------------------------------
class AnimInfoBinary:
    def __init__(self, name: bytes = b'', group: bytes = b'',
                 total_bones: int = 0, root_include: int = 0,
                 key_compression_style: int = 0, key_quotum: int = 0,
                 key_reduction: float = 0.0, track_time: float = 0.0,
                 anim_rate: float = 0.0, start_bone: int = -1,
                 first_raw_frame: int = 0, num_raw_frames: int = 0):
        self.name = name
        self.group = group
        self.total_bones = total_bones
        self.root_include = root_include
        self.key_compression_style = key_compression_style
        self.key_quotum = key_quotum
        self.key_reduction = key_reduction
        self.track_time = track_time
        self.anim_rate = anim_rate
        self.start_bone = start_bone
        self.first_raw_frame = first_raw_frame
        self.num_raw_frames = num_raw_frames


# ------------------------------------------------------------------
# VChunkHeader: file chunk header (serialization)
# ------------------------------------------------------------------
class VChunkHeader:
    def __init__(self, chunk_id: bytes = b'', type_flag: int = 0,
                 data_size: int = 0, data_count: int = 0):
        self.chunk_id = chunk_id
        self.type_flag = type_flag
        self.data_size = data_size
        self.data_count = data_count


# ------------------------------------------------------------------
# VMaterial: raw data material
# ------------------------------------------------------------------
class VMaterial:
    def __init__(self, material_name: bytes = b'', texture_index: int = 0,
                 poly_flags: int = 0, aux_material: int = 0,
                 aux_flags: int = 0, lod_bias: int = 0,
                 lod_style: int = 0):
        self.material_name = material_name
        self.texture_index = texture_index
        self.poly_flags = poly_flags
        self.aux_material = aux_material
        self.aux_flags = aux_flags
        self.lod_bias = lod_bias
        self.lod_style = lod_style


# ------------------------------------------------------------------
# VBone: raw data bone
# ------------------------------------------------------------------
class VBone:
    def __init__(self, name: bytes = b'', flags: int = 0,
                 num_children: int = -1, parent_index: int = -1,
                 bone_pos: Optional['VJointPos'] = None):
        self.name = name
        self.flags = flags
        self.num_children = num_children
        self.parent_index = parent_index
        self.bone_pos = bone_pos or VJointPos()


# ------------------------------------------------------------------
# VBoneInfIndex: bone influence blending
# ------------------------------------------------------------------
class VBoneInfIndex:
    def __init__(self, weight_index: int = 0, number: int = 0,
                 detail_a: int = 0, detail_b: int = 0):
        self.weight_index = weight_index
        self.number = number
        self.detail_a = detail_a
        self.detail_b = detail_b


# ------------------------------------------------------------------
# VBoneInfluence: weight and vertex number
# ------------------------------------------------------------------
class VBoneInfluence:
    def __init__(self, point_index: int = 0, bone_weight: int = 0):
        self.point_index = point_index
        self.bone_weight = bone_weight


# ------------------------------------------------------------------
# VRawBoneInfluence: raw bone influence (sorted later)
# ------------------------------------------------------------------
class VRawBoneInfluence:
    def __init__(self, weight: float = 0.0, point_index: int = 0,
                 bone_index: int = -1):
        self.weight = weight
        self.point_index = point_index
        self.bone_index = bone_index


# ------------------------------------------------------------------
# VQuatAnimKey: an animation key (position + quat + time)
# ------------------------------------------------------------------
class VQuatAnimKey:
    def __init__(self, position: Optional['FVector'] = None,
                 orientation: Optional['FQuat'] = None, time: float = 0.0):
        self.position = position or FVector()
        self.orientation = orientation or FQuat()
        self.time = time


# ------------------------------------------------------------------
# AnalogTrack: single bone/element animation track
# ------------------------------------------------------------------
class AnalogTrack:
    def __init__(self, flags: int = 0):
        self.flags = flags
        self.key_quat: List['FQuat'] = []
        self.key_pos: List['FVector'] = []
        self.key_time: List[float] = []


# ------------------------------------------------------------------
# MotionChunkDigestInfo: animation chunk digest info
# ------------------------------------------------------------------
class MotionChunkDigestInfo:
    def __init__(self, name: FName = FName(), group: FName = FName(),
                 root_include: int = 0, key_compression_style: int = 0,
                 key_quotum: int = 0, key_reduction: float = 0.0,
                 track_time: float = 0.0, anim_rate: float = 0.0,
                 start_bone: int = -1, first_raw_frame: int = 0,
                 num_raw_frames: int = 0):
        self.name = name
        self.group = group
        self.root_include = root_include
        self.key_compression_style = key_compression_style
        self.key_quotum = key_quotum
        self.key_reduction = key_reduction
        self.track_time = track_time
        self.anim_rate = anim_rate
        self.start_bone = start_bone
        self.first_raw_frame = first_raw_frame
        self.num_raw_frames = num_raw_frames


# ------------------------------------------------------------------
# MotionChunk: compressed animation data
# ------------------------------------------------------------------
class MotionChunk:
    def __init__(self, root_speed_3d: Optional['FVector'] = None,
                 track_time: float = 0.0, start_bone: int = -1,
                 flags: int = 0):
        self.root_speed_3d = root_speed_3d or FVector()
        self.track_time = track_time
        self.start_bone = start_bone
        self.flags = flags
        self.bone_indices: List[int] = []
        self.anim_tracks: List['AnalogTrack'] = []
        self.root_track: Optional['AnalogTrack'] = None


# ------------------------------------------------------------------
# TrackDiffs: error tolerance for animation key tracks
# ------------------------------------------------------------------
class TrackDiffs:
    def __init__(self, bone_bias: float = 0.0, quat_err: Optional[List[float]] = None,
                 pos_err: Optional[List[float]] = None):
        self.bone_bias = bone_bias
        self.quat_err = quat_err or []
        self.pos_err = pos_err or []


# ------------------------------------------------------------------
# VVertex: textured vertex (import only)
# ------------------------------------------------------------------
class VVertex:
    def __init__(self, point_index: int = -1, u: float = 0.0, v: float = 0.0,
                 mat_index: int = 0, reserved: int = 0):
        self.point_index = point_index
        self.u = u
        self.v = v
        self.mat_index = mat_index
        self.reserved = reserved


# ------------------------------------------------------------------
# VPoint: regular FVector point
# ------------------------------------------------------------------
class VPoint:
    def __init__(self, point: Optional['FVector'] = None):
        self.point = point or FVector()


# ------------------------------------------------------------------
# VTriangle: textured triangle
# ------------------------------------------------------------------
class VTriangle:
    def __init__(self, wedge_index: List[int] = [-1, -1, -1],
                 mat_index: int = 0, aux_mat_index: int = 0,
                 smoothing_groups: int = 0):
        self.wedge_index = wedge_index
        self.mat_index = mat_index
        self.aux_mat_index = aux_mat_index
        self.smoothing_groups = smoothing_groups


# ------------------------------------------------------------------
# USkelImport: raw data bundle from 3DSMax plugin
# ------------------------------------------------------------------
class USkelImport:
    def __init__(self):
        self.materials: List['VMaterial'] = []
        self.points: List['FVector'] = []
        self.wedges: List['VVertex'] = []
        self.faces: List['VTriangle'] = []
        self.ref_bones_binary: List['VBone'] = []
        self.influences: List['VRawBoneInfluence'] = []


# ------------------------------------------------------------------
# USkeletalMesh: skeletal mesh class
# ------------------------------------------------------------------
class USkeletalMesh(ULodMesh):
    def __init__(self):
        super().__init__()
        self.ext_wedges: List = []
        self.points: List['FVector'] = []
        self.ref_skeleton: List['FMeshBone'] = []
        self.bone_weight_idx: List = []
        self.bone_weights: List['VBoneInfluence'] = []
        self.local_points: List['FVector'] = []
        self.weapon_bone_index: int = -1
        self.weapon_adjust = FVector(1, 1, 1)  # FCoords simplified
        self.skeletal_depth: int = 0
        self.default_animation = None  # UAnimation*
        self.debug_pivots: List['FVector'] = []
        self.debug_parents: List[int] = []
        self.debug_verts: List[int] = []
        self.display_bones: bool = False
        self.display_influences: bool = False
        self.classic_weapon_coords = FVector(1, 1, 1)  # FCoords

    def serialize(self, ar: 'FArchive') -> 'USkeletalMesh':
        super().serialize(ar)
        ar << self.ext_wedges
        ar << self.points
        ar << self.ref_skeleton
        ar << self.bone_weight_idx
        ar << self.bone_weights
        ar << self.local_points
        ar << self.weapon_bone_index
        ar << self.weapon_adjust
        ar << self.skeletal_depth
        ar << self.default_animation
        ar << self.debug_pivots
        ar << self.debug_parents
        ar << self.debug_verts
        ar << self.display_bones
        ar << self.display_influences
        ar << self.classic_weapon_coords
        return self

    def set_scale(self, new_scale: 'FVector') -> None:
        pass

    def flip_faces(self) -> None:
        pass

    def get_frame(self, verts, size, coords, owner, lod_request):
        raise NotImplementedError("C++ GetFrame in Engine.lib")

    def get_render_bounding_box(self, owner, exact):
        raise NotImplementedError("C++ GetRenderBoundingBox in Engine.lib")


# ------------------------------------------------------------------
# UAnimation: base class for animating skeletal bones
# ------------------------------------------------------------------
class UAnimation(UObject):
    def __init__(self):
        super().__init__()
        self.ref_bones: List['FNamedBone'] = []
        self.moves: List['MotionChunk'] = []
        self.anim_seqs: List = []
        self.moves_info: List = []
        self.raw_num_frames: int = 0
        self.raw_anim_keys: List = []
        self.raw_anim_seq_info: List = []
        self.comp_factor: float = 1.0

    def serialize(self, ar: 'FArchive') -> 'UAnimation':
        super().serialize(ar)
        ar << self.ref_bones
        ar << self.moves
        ar << self.anim_seqs
        ar << self.moves_info
        ar << self.raw_num_frames
        ar << self.raw_anim_keys
        ar << self.raw_anim_seq_info
        ar << self.comp_factor
        return self

    def get_anim_seq(self, seq_name: FName):
        for seq in self.anim_seqs:
            if seq_name == seq.name:
                return seq
        return None

    def get_movement(self, seq_name: FName):
        for move in self.moves:
            if seq_name == move.name:
                return move
        return None


__all__ = [
    "VJointPos", "FMeshBone", "FNamedBone", "FNamedBoneBinary",
    "AnimInfoBinary", "VChunkHeader", "VMaterial", "VBone",
    "VBoneInfIndex", "VBoneInfluence", "VRawBoneInfluence",
    "VQuatAnimKey", "AnalogTrack", "MotionChunkDigestInfo",
    "MotionChunk", "TrackDiffs", "VVertex", "VPoint", "VTriangle",
    "USkelImport", "USkeletalMesh", "UAnimation",
]