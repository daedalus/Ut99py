"""Port of Engine/Inc/UnObj.h (36 declared symbols).

Defines FBspNode, FPointRegion, FLeaf, FBspSurf, FZoneProperties,
FShadowMask, FLightMapIndex, FPoly, UPolys, FVert, FDecal, and
related BSP/enums. C++ serializer operators (FArchive& <<)
are documented but not fully implemented; bodies in prebuilt
Engine.lib handle persistence.
"""
from typing import Optional, List, ClassVar
from enum import IntEnum
from ..core import UObject, FArchive, FName, FVector, FPlane

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


# ------------------------------------------------------------------
# Point region (FPointRegion)
# ------------------------------------------------------------------
class FPointRegion:
    def __init__(
        self,
        zone: Optional["AZoneInfo"] = None,
        i_leaf: int = -1,
        zone_number: int = 0,
    ):
        self.zone = zone
        self.i_leaf = i_leaf
        self.zone_number = zone_number


# ------------------------------------------------------------------
# BSP node (FBspNode)
# ------------------------------------------------------------------
class FBspNode:
    MAX_NODE_VERTICES = 16
    MAX_FINAL_VERTICES = 24
    MAX_ZONES = 64

    def __init__(self):
        self.plane: FPlane = FPlane()
        self.zone_mask: int = 0
        self.i_vert_pool: int = 0
        self.i_surf: int = 0
        # Union iBack / iChild[1]
        self.i_back: int = 0
        self.i_front: int = 0
        self.i_plane: int = -1  # INDEX_NONE equivalent
        self.i_collision_bound: int = 0
        self.i_render_bound: int = 0
        self.i_zone: List[int] = [0, 0]
        self.num_vertices: int = 0
        self.node_flags: int = 0
        self.i_leaf: List[int] = [-1, -1]  # INDEX_NONE = -1

    def is_csg(self, extra_flags: int = 0) -> bool:
        return (
            self.num_vertices > 0
            and not (self.node_flags & (EBspNodeFlags.NF_IsNew | EBspNodeFlags.NF_NotCsg | extra_flags))
        )

    def child_outside(self, i_child: int, outside: bool, extra_flags: int = 0) -> bool:
        if i_child:
            return outside or self.is_csg(extra_flags)
        return outside and not self.is_csg(extra_flags)


# ------------------------------------------------------------------
# Zone properties (FZoneProperties)
# ------------------------------------------------------------------
class FZoneProperties:
    def __init__(self):
        self.zone_actor: Optional["AZoneInfo"] = None
        self.last_render_time: float = 0.0
        self.connectivity: int = 0
        self.visibility: int = 0


# ------------------------------------------------------------------
# BSP leaf (FLeaf)
# ------------------------------------------------------------------
class FLeaf:
    def __init__(
        self,
        i_zone: int = 0,
        i_permeating: int = 0,
        i_volumetric: int = 0,
        visible_zones: int = 0,
    ):
        self.i_zone = i_zone
        self.i_permeating = i_permeating
        self.i_volumetric = i_volumetric
        self.visible_zones = visible_zones


# ------------------------------------------------------------------
# BSP surface (FBspSurf)
# ------------------------------------------------------------------
class FBspSurf:
    def __init__(self):
        self.texture: Optional["UTexture"] = None
        self.poly_flags: int = 0
        self.p_base: int = 0
        self.v_normal: int = 0
        self.v_texture_u: int = 0
        self.v_texture_v: int = 0
        self.i_light_map: int = 0
        self.i_brush_poly: int = 0
        self.pan_u: int = 0
        self.pan_v: int = 0
        self.actor: Optional["ABrush"] = None
        self.decals: List["FDecal"] = []
        self.nodes: List[int] = []


# ------------------------------------------------------------------
# Polygon flags (EPolyFlags)
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# Shadow mask (FShadowMask)
# ------------------------------------------------------------------
class FShadowMask:
    def __init__(self):
        self.owner: Optional["AActor"] = None
        self.shadow_data: List[int] = []


# ------------------------------------------------------------------
# Light map index (FLightMapIndex)
# ------------------------------------------------------------------
class FLightMapIndex:
    def __init__(self):
        self.data_offset: int = 0
        self.i_light_actors: int = 0
        self.pan: FVector = FVector()
        self.u_scale: float = 1.0
        self.v_scale: float = 1.0
        self.u_clamp: int = 0
        self.v_clamp: int = 0
        self.u_bits: int = 0
        self.v_bits: int = 0


# ------------------------------------------------------------------
# Split type (ESplitType)
# ------------------------------------------------------------------
class ESplitType:
    SP_Coplanar = 0
    SP_Front = 1
    SP_Back = 2
    SP_Split = 3


# ------------------------------------------------------------------
# General-purpose polygon (FPoly)
# ------------------------------------------------------------------
class FPoly:
    MAX_VERTICES = 16
    VERTEX_THRESHOLD = MAX_VERTICES - 2  # 14

    def __init__(self):
        self.base: FVector = FVector()
        self.normal: FVector = FVector()
        self.texture_u: FVector = FVector()
        self.texture_v: FVector = FVector()
        self.vertex: List[FVector] = [FVector() for _ in range(self.MAX_VERTICES)]
        self.poly_flags: int = 0
        self.actor: Optional["ABrush"] = None
        self.texture: Optional["UTexture"] = None
        self.item_name: FName = FName()
        self.num_vertices: int = 0
        self.i_link: int = 0
        self.i_brush_poly: int = 0
        self.pan_u: int = 0
        self.pan_v: int = 0
        self.save_poly_index: int = 0
        self.b_face_drag_sel: bool = False

    def init(self) -> None:
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

    def reverse(self) -> None:
        for i in range(self.num_vertices // 2):
            j = self.num_vertices - i - 1
            self.vertex[i], self.vertex[j] = self.vertex[j], self.vertex[i]
        self.normal = -self.normal

    def is_backfaced(self, point: FVector) -> bool:
        return (point - self.base) | self.normal < 0.0

    def is_coplanar(self, test: "FPoly") -> bool:
        return (
            abs((self.base - test.base) | self.normal) < 0.01
            and abs(self.normal | test.normal) > 0.9999
        )


# ------------------------------------------------------------------
# List of FPolys (UPolys) — UObject subclass
# ------------------------------------------------------------------
class UPolys(UObject):
    def __init__(self):
        super().__init__()
        self.element: List[FPoly] = []

    def serialize(self, ar: FArchive) -> "UPolys":
        super().serialize(ar)
        ar << self.element
        return self


# ------------------------------------------------------------------
# BSP vertex (FVert)
# ------------------------------------------------------------------
class FVert:
    def __init__(self, p_vertex: int = 0, i_side: int = -1):
        self.p_vertex = p_vertex
        self.i_side = i_side


# ------------------------------------------------------------------
# Decal (FDecal)
# ------------------------------------------------------------------
class FDecal:
    def __init__(self):
        self.vertices: List[FVector] = [FVector() for _ in range(4)]
        self.actor: Optional["ADecal"] = None
        self.nodes: List[int] = []


__all__ = [
    "EBspNodeFlags", "FPointRegion", "FBspNode",
    "FZoneProperties", "FLeaf", "FBspSurf", "EPolyFlags",
    "FShadowMask", "FLightMapIndex", "ESplitType", "FPoly",
    "UPolys", "FVert", "FDecal",
]
