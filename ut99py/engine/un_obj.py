"""Port of Engine/Inc/UnObj.h (36 declared symbols).

Defines FBspNode, FPointRegion, FLeaf, FBspSurf, FZoneProperties,
FShadowMask, FLightMapIndex, FPoly, UPolys, FVert, FDecal, and
related BSP/enums, with the archive operators (FArchive& <<).

The operators whose body is CORE_API or ENGINE_API live in the prebuilt
Core.lib/Engine.lib; their layout was read off the map files, with the
inline ones (FZoneProperties, FLeaf, FLightMapIndex, FVert, FDecal,
UPolys) taken from the header.
"""
from ..core import UObject, FPlane, FVector, FName
from ..core.system import AR_INDEX

# ------------------------------------------------------------------
# BSP node flags (EBspNodeFlags)
# ------------------------------------------------------------------
class EBspNodeFlags:
    NF_NotCsg = 0x01
    NF_ShootThrough = 0x02
    NF_NotVisBlocking = 0x04
    NF_PolyOccluded = 0x08
    NF_BoxOccluded = 0x10
    NF_BrightCorners = 0x10
    NF_IsNew = 0x20
    NF_IsFront = 0x40
    NF_IsBack = 0x80
    NF_NeverMove = 0


class FPointRegion:
    def __init__(self, zone=None, i_leaf=-1, zone_number=0):
        self.zone = zone
        self.i_leaf = i_leaf
        self.zone_number = zone_number


class FBspNode:
    MAX_NODE_VERTICES = 16
    MAX_FINAL_VERTICES = 24
    MAX_ZONES = 64

    def __init__(self):
        self.plane = FPlane()
        self.zone_mask = 0
        self.i_vert_pool = 0
        self.i_surf = 0
        self.i_back = 0
        self.i_front = 0
        self.i_plane = -1
        self.i_collision_bound = 0
        self.i_render_bound = 0
        self.i_zone = [0, 0]
        self.num_vertices = 0
        self.node_flags = 0
        self.i_leaf = [-1, -1]

    def is_csg(self, extra_flags=0):
        return (self.num_vertices > 0
                and not (self.node_flags & (EBspNodeFlags.NF_IsNew | EBspNodeFlags.NF_NotCsg | extra_flags)))

    def child_outside(self, i_child, outside, extra_flags=0):
        if i_child:
            return outside or self.is_csg(extra_flags)
        return outside and not self.is_csg(extra_flags)

    def serialize(self, ar) -> "FBspNode":
        """operator<<(FArchive&, FBspNode&) (UnObj.h:132).

        The C++ body is ENGINE_API; the layout was read off the map files:
        the plane, the zone mask, the node flags, nine compact indices, the
        vertex count and the two leaf indices. The nine index fields are
        INT in the header but compact indices on disk.
        """
        self.plane.serialize(ar)
        self.zone_mask = ar.serialize_qword(self.zone_mask)
        self.node_flags = ar.serialize_byte(self.node_flags)
        self.i_vert_pool = AR_INDEX(ar, self.i_vert_pool)
        self.i_surf = AR_INDEX(ar, self.i_surf)
        self.i_back = AR_INDEX(ar, self.i_back)
        self.i_front = AR_INDEX(ar, self.i_front)
        self.i_plane = AR_INDEX(ar, self.i_plane)
        self.i_collision_bound = AR_INDEX(ar, self.i_collision_bound)
        self.i_render_bound = AR_INDEX(ar, self.i_render_bound)
        self.i_zone[0] = AR_INDEX(ar, self.i_zone[0])
        self.i_zone[1] = AR_INDEX(ar, self.i_zone[1])
        self.num_vertices = ar.serialize_byte(self.num_vertices)
        self.i_leaf[0] = ar.serialize_int32(self.i_leaf[0])
        self.i_leaf[1] = ar.serialize_int32(self.i_leaf[1])
        return self


class FZoneProperties:
    def __init__(self):
        self.zone_actor = None
        self.last_render_time = 0.0
        self.connectivity = 0
        self.visibility = 0

    def serialize(self, ar) -> "FZoneProperties":
        """operator<<(FArchive&, FZoneProperties&) (UnObj.h:148).

        The C++ returns before writing LastRenderTime, so it is never on disk.
        """
        self.zone_actor = ar.serialize_object(self.zone_actor)
        self.connectivity = ar.serialize_qword(self.connectivity)
        self.visibility = ar.serialize_qword(self.visibility)
        return self


class FLeaf:
    def __init__(self, i_zone=0, i_permeating=0, i_volumetric=0, visible_zones=0):
        self.i_zone = i_zone
        self.i_permeating = i_permeating
        self.i_volumetric = i_volumetric
        self.visible_zones = visible_zones

    def serialize(self, ar) -> "FLeaf":
        """operator<<(FArchive&, FLeaf&) (UnObj.h:179)."""
        self.i_zone = AR_INDEX(ar, self.i_zone)
        self.i_permeating = AR_INDEX(ar, self.i_permeating)
        self.i_volumetric = AR_INDEX(ar, self.i_volumetric)
        self.visible_zones = ar.serialize_qword(self.visible_zones)
        return self


class FBspSurf:
    def __init__(self):
        self.texture = None
        self.poly_flags = 0
        self.p_base = 0
        self.v_normal = 0
        self.v_texture_u = 0
        self.v_texture_v = 0
        self.i_light_map = 0
        self.i_brush_poly = 0
        self.pan_u = 0
        self.pan_v = 0
        self.actor = None
        self.decals = []
        self.nodes = []

    def serialize(self, ar) -> "FBspSurf":
        """operator<<(FArchive&, FBspSurf&) (UnObj.h:217).

        The C++ body is ENGINE_API; the layout was read off the map files:
        the texture and the brush actor are object references, the rest are
        compact indices, the pan values are 16 bit and the flags a DWORD.
        The Decals and Nodes arrays are not serialized.
        """
        self.texture = ar.serialize_object(self.texture)
        self.poly_flags = ar.serialize_int32(self.poly_flags)
        self.p_base = AR_INDEX(ar, self.p_base)
        self.v_normal = AR_INDEX(ar, self.v_normal)
        self.v_texture_u = AR_INDEX(ar, self.v_texture_u)
        self.v_texture_v = AR_INDEX(ar, self.v_texture_v)
        self.i_light_map = AR_INDEX(ar, self.i_light_map)
        self.i_brush_poly = AR_INDEX(ar, self.i_brush_poly)
        self.pan_u = ar.serialize_word(self.pan_u)
        self.pan_v = ar.serialize_word(self.pan_v)
        self.actor = ar.serialize_object(self.actor)
        return self


class EPolyFlags:
    PF_Invisible = 0x00000001
    PF_Masked = 0x00000002
    PF_Translucent = 0x00000004
    PF_NotSolid = 0x00000008
    PF_Environment = 0x00000010
    PF_ForceViewZone = 0x00000010
    PF_Semisolid = 0x00000020
    PF_Modulated = 0x00000040
    PF_FakeBackdrop = 0x00000080
    PF_TwoSided = 0x00000100
    PF_AutoUPan = 0x00000200
    PF_AutoVPan = 0x00000400
    PF_NoSmooth = 0x00000800
    PF_BigWavy = 0x00001000
    PF_SpecialPoly = 0x00001000
    PF_SmallWavy = 0x00002000
    PF_Flat = 0x00004000
    PF_LowShadowDetail = 0x00008000
    PF_NoMerge = 0x00010000
    PF_CloudWavy = 0x00020000
    PF_DirtyShadows = 0x00040000
    PF_BrightCorners = 0x00080000
    PF_SpecialLit = 0x00100000
    PF_Gouraud = 0x00200000
    PF_NoBoundRejection = 0x00200000
    PF_Unlit = 0x00400000
    PF_HighShadowDetail = 0x00800000
    PF_Portal = 0x04000000
    PF_Mirrored = 0x08000000
    PF_Memorized = 0x01000000
    PF_Selected = 0x02000000
    PF_Highlighted = 0x10000000
    PF_FlatShaded = 0x40000000
    PF_EdProcessed = 0x40000000
    PF_EdCut = 0x80000000
    PF_RenderFog = 0x40000000
    PF_Occlude = 0x80000000
    PF_RenderHint = 0x01000000
    PF_NoOcclude = PF_Masked | PF_Translucent | PF_Invisible | PF_Modulated
    PF_NoEdit = PF_Memorized | PF_Selected | PF_EdProcessed | PF_NoMerge | PF_EdCut
    PF_NoImport = PF_NoEdit | PF_NoMerge | PF_Memorized | PF_Selected | PF_EdProcessed | PF_EdCut
    PF_AddLast = PF_Semisolid | PF_NotSolid
    PF_NoAddToBSP = PF_EdCut | PF_EdProcessed | PF_Selected | PF_Memorized
    PF_NoShadows = PF_Unlit | PF_Invisible | PF_Environment | PF_FakeBackdrop
    PF_Transient = PF_Highlighted


class FShadowMask:
    def __init__(self):
        self.owner = None
        self.shadow_data = []


class FLightMapIndex:
    def __init__(self):
        self.data_offset = 0
        self.i_light_actors = 0
        self.pan = FVector()
        self.u_scale = 1.0
        self.v_scale = 1.0
        self.u_clamp = 0
        self.v_clamp = 0
        self.u_bits = 0
        self.v_bits = 0

    def serialize(self, ar) -> "FLightMapIndex":
        """operator<<(FArchive&, FLightMapIndex&) (UnObj.h:307)."""
        self.data_offset = ar.serialize_int32(self.data_offset)
        self.pan.serialize(ar)
        self.u_clamp = AR_INDEX(ar, self.u_clamp)
        self.v_clamp = AR_INDEX(ar, self.v_clamp)
        self.u_scale = ar.serialize_float(self.u_scale)
        self.v_scale = ar.serialize_float(self.v_scale)
        self.i_light_actors = ar.serialize_int32(self.i_light_actors)
        return self


class ESplitType:
    SP_Coplanar = 0
    SP_Front = 1
    SP_Back = 2
    SP_Split = 3


class FPoly:
    MAX_VERTICES = 16
    VERTEX_THRESHOLD = 14

    def __init__(self):
        self.base = FVector()
        self.normal = FVector()
        self.texture_u = FVector()
        self.texture_v = FVector()
        self.vertex = [FVector() for _ in range(self.MAX_VERTICES)]
        self.poly_flags = 0
        self.actor = None
        self.texture = None
        self.item_name = FName()
        self.num_vertices = 0
        self.i_link = 0
        self.i_brush_poly = 0
        self.pan_u = 0
        self.pan_v = 0
        self.save_poly_index = 0
        self.b_face_drag_sel = False

    def init(self):
        self.base = FVector()
        self.normal = FVector()
        self.texture_u = FVector()
        self.texture_v = FVector()
        self.poly_flags = 0
        self.num_vertices = 0
        self.actor = None
        self.texture = None
        self.item_name = FName()
        self.i_link = 0
        self.i_brush_poly = 0
        self.pan_u = 0
        self.pan_v = 0
        self.save_poly_index = 0
        self.b_face_drag_sel = False

    def reverse(self):
        for i in range(self.num_vertices // 2):
            j = self.num_vertices - i - 1
            self.vertex[i], self.vertex[j] = self.vertex[j], self.vertex[i]
        self.normal = -self.normal

    def is_backfaced(self, point):
        return (point - self.base) | self.normal < 0.0

    def is_coplanar(self, test):
        return (abs((self.base - test.base) | self.normal) < 0.01
                and abs(self.normal | test.normal) > 0.9999)

    def serialize(self, ar) -> "FPoly":
        """operator<<(FArchive&, FPoly&) (UnModel.cpp:60-74)."""
        from ..core.system import AR_INDEX
        self.num_vertices = AR_INDEX(ar, self.num_vertices)
        self.base.serialize(ar)
        self.normal.serialize(ar)
        self.texture_u.serialize(ar)
        self.texture_v.serialize(ar)
        # Only serialize the used vertices; NumVertices controls the loop.
        for i in range(self.num_vertices):
            if i < len(self.vertex):
                self.vertex[i].serialize(ar)
        self.poly_flags = ar.serialize_int32(self.poly_flags)
        self.actor = ar.serialize_object(self.actor)
        self.texture = ar.serialize_object(self.texture)
        self.item_name = ar.serialize_name(self.item_name)
        self.i_link = AR_INDEX(ar, self.i_link)
        self.i_brush_poly = AR_INDEX(ar, self.i_brush_poly)
        self.pan_u = ar.serialize_word(self.pan_u)
        self.pan_v = ar.serialize_word(self.pan_v)
        return self


class UPolys(UObject):
    def __init__(self):
        super().__init__()
        self.element = []

    def serialize(self, ar):
        """UPolys::Serialize (UnObj.h:412).

        The element count and capacity come first, then the polygons.
        """
        super().serialize(ar)
        db_num = ar.serialize_int32(len(self.element))
        ar.serialize_int32(db_num)  # DbMax
        if ar.is_loading():
            self.element = []
        for _ in range(db_num):
            self.element.append(FPoly().serialize(ar))
        return self


class FVert:
    def __init__(self, p_vertex=0, i_side=-1):
        self.p_vertex = p_vertex
        self.i_side = i_side

    def serialize(self, ar) -> "FVert":
        """operator<<(FArchive&, FVert&) (UnObj.h:454)."""
        self.p_vertex = AR_INDEX(ar, self.p_vertex)
        self.i_side = AR_INDEX(ar, self.i_side)
        return self


class FDecal:
    def __init__(self):
        self.vertices = [FVector() for _ in range(4)]
        self.actor = None
        self.nodes = []

    def serialize(self, ar) -> "FDecal":
        """operator<<(FArchive&, FDecal&) (UnObj.h:478).

        The inline C++ only writes the actor for a trans archive, so a decal
        takes no space in a map file.
        """
        if not ar.is_loading() and not ar.is_saving():
            self.actor = ar.serialize_object(self.actor)
        return self


__all__ = [
    "EBspNodeFlags", "FPointRegion", "FBspNode",
    "FZoneProperties", "FLeaf", "FBspSurf", "EPolyFlags",
    "FShadowMask", "FLightMapIndex", "ESplitType", "FPoly",
    "UPolys", "FVert", "FDecal",
]
