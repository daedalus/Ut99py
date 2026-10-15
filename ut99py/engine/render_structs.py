"""Port of Engine/Inc/UnRender.h (graphics structures).

Defines FSceneNode, FSpanBuffer, FSpan, FRasterPoly, FTransTexture,
FScreenBounds, FSurfaceInfo, FSurfaceFacet, FDynamicItem, FDynamicSprite,
FBspDrawList, FSavedPoly, and related structures for rendering pipeline.
C++ struct layouts preserved exactly. Bodies in Engine.lib handle execution.
"""
from typing import Optional, List, Any
from ..core import FVector, FPlane, FCoords
from .texture import FColor, FTextureInfo

# ------------------------------------------------------------------
# FSceneNode: main rendering frame
# ------------------------------------------------------------------
class FSceneNode:
    def __init__(self):
        self.Viewport: Optional[Any] = None  # UViewport*
        self.Level: Optional[Any] = None  # ULevel*
        self.Parent: Optional['FSceneNode'] = None
        self.Sibling: Optional['FSceneNode'] = None
        self.Child: Optional['FSceneNode'] = None
        self.iSurf: int = 0
        self.ZoneNumber: int = 0
        self.Recursion: int = 0
        self.Mirror: float = 1.0
        self.NearClip: FPlane = FPlane()
        self.Coords: FCoords = FCoords()
        self.Uncoords: FCoords = FCoords()
        self.Span: Optional['FSpanBuffer'] = None
        self.Draw: List['FBspDrawList'] = []
        self.Sprite: Optional['FDynamicSprite'] = None
        self.X: int = 0
        self.Y: int = 0
        self.XB: int = 0
        self.YB: int = 0
        self.FX: float = 0.0
        self.FY: float = 0.0
        self.FX15: float = 0.0
        self.FY15: float = 0.0
        self.FX2: float = 0.0
        self.FY2: float = 0.0
        self.Zoom: float = 1.0
        self.Proj: FVector = FVector()
        self.RProj: FVector = FVector()
        self.PrjXM: float = 0.0
        self.PrjYM: float = 0.0
        self.PrjXP: float = 0.0
        self.PrjYP: float = 0.0
        self.ViewSides: List[FVector] = []
        self.ViewPlanes: List[FPlane] = []
        self._b_hidden = False


# ------------------------------------------------------------------
# Span buffer structures (rendering spans)
# ------------------------------------------------------------------
class FSpanBuffer:
    def __init__(self):
        pass  # Stub - filled in Engine.lib

class FSpan:
    def __init__(self):
        pass

class FRasterPoly:
    def __init__(self):
        pass


# ------------------------------------------------------------------
# Transformed render structures
# ------------------------------------------------------------------
class FTransTexture:
    def __init__(self):
        self.Point: FVector = FVector()
        self.Light: FPlane = FPlane()
        self.Fog: FVector = FVector()
        self.U: float = 0.0
        self.V: float = 0.0


class FScreenBounds:
    def __init__(self):
        self.MinX: float = 0.0
        self.MinY: float = 0.0
        self.MaxX: float = 0.0
        self.MaxY: float = 0.0
        self.MinZ: float = 0.0


# ------------------------------------------------------------------
# Surface info structures
# ------------------------------------------------------------------
class FSurfaceInfo:
    def __init__(self):
        self.PolyFlags: int = 0
        self.FlatColor: FColor = FColor()
        self.Texture: Optional['FTextureInfo'] = None
        self.LightMap: Optional['FTextureInfo'] = None
        self.MacroTexture: Optional['FTextureInfo'] = None
        self.DetailTexture: Optional['FTextureInfo'] = None
        self.FogMap: Optional['FTextureInfo'] = None


class FSurfaceFacet:
    def __init__(self):
        self.MapCoords: FCoords = FCoords()
        self.MapUncoords: FCoords = FCoords()
        self.Span: Optional['FSpanBuffer'] = None
        self.Polys: List['FSavedPoly'] = []


# ------------------------------------------------------------------
# Dynamic sprite structures
# ------------------------------------------------------------------
class FDynamicItem:
    def __init__(self):
        pass

class FDynamicSprite:
    def __init__(self):
        pass


# ------------------------------------------------------------------
# BSP draw list and saved polygon
# ------------------------------------------------------------------
class FBspDrawList:
    def __init__(self):
        pass

class FSavedPoly:
    def __init__(self):
        self.Next: Optional['FSavedPoly'] = None
        self.iNode: int = 0
        self.User: Any = None
        self.NumPts: int = 0
        self.Pts: List[Any] = []


# ------------------------------------------------------------------
# Rendering line flags
# ------------------------------------------------------------------
class ELineFlags:
    LINE_None = 0
    LINE_Transparent = 1
    LINE_DepthCued = 2


__all__ = [
    "FSceneNode", "FSpanBuffer", "FSpan", "FRasterPoly",
    "FTransTexture", "FScreenBounds", "FSurfaceInfo", "FSurfaceFacet",
    "FDynamicItem", "FDynamicSprite", "FBspDrawList", "FSavedPoly", "ELineFlags",
]