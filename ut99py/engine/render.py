"""Port of Engine/Inc/UnRender.h (21 declared symbols).

Rendering structures and base classes: FSceneNode (view frustum + precomputed transforms),
FOutVector/FTransform/FTransSample/FTransTexture (vertex transformation pipeline),
FSurfaceInfo/FSavedPoly/FSurfaceFacet (surface description), FScreenBounds (bbox culling),
ELineFlags, URenderBase (abstract rendering device), plus hit proxies (HBspSurf, HActor, HCoords).
C++ method bodies raise NotImplementedError; persistence handled by prebuilt Engine.lib.
"""
from typing import Optional, List, Any
from enum import IntFlag, IntEnum
from ..core import UObject, FVector, FPlane, FCoords
from .texture import FColor, FTextureInfo


# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
ORTHO_LOW_DETAIL = 40000.0

# ----------------------------------------------------------------------
# Hit flag constants (from FTransform::ComputeOutcode)
# ----------------------------------------------------------------------
FVF_OutXMin = 0x01
FVF_OutXMax = 0x02
FVF_OutYMin = 0x04
FVF_OutYMax = 0x08
FVF_OutZMin = 0x10
FVF_OutZMax = 0x20


# ----------------------------------------------------------------------
# FOutVector: transformed vector with outcode info
# ----------------------------------------------------------------------
class FOutVector:
    def __init__(self):
        self.Point: FVector = FVector()
        self.Flags: int = 0


# ----------------------------------------------------------------------
# FTransform: transformed and projected vector
# ----------------------------------------------------------------------
class FTransform(FOutVector):
    def __init__(self):
        super().__init__()
        self.ScreenX: float = 0.0
        self.ScreenY: float = 0.0
        self.IntY: int = 0
        self.RZ: float = 0.0

    def project(self, Frame: 'FSceneNode') -> None:
        self.RZ = Frame.Proj.Z / self.Point.Z if self.Point.Z != 0 else 0.0
        self.ScreenX = self.Point.X * self.RZ + Frame.FX15
        self.ScreenY = self.Point.Y * self.RZ + Frame.FY15
        self.IntY = int(self.ScreenY)

    def compute_outcode(self, Frame: 'FSceneNode') -> None:
        # Simplified version - asm implementations omitted for clarity
        ClipXM = Frame.PrjXM * self.Point.Z + self.Point.X
        ClipXP = Frame.PrjXP * self.Point.Z - self.Point.X
        ClipYM = Frame.PrjYM * self.Point.Z + self.Point.Y
        ClipYP = Frame.PrjYP * self.Point.Z - self.Point.Y
        
        self.Flags = 0
        if ClipXM < 0: self.Flags |= FVF_OutXMin
        if ClipXP < 0: self.Flags |= FVF_OutXMax
        if ClipYM < 0: self.Flags |= FVF_OutYMin
        if ClipYP < 0: self.Flags |= FVF_OutYMax

    def __add__(self, V: 'FTransform') -> 'FTransform':
        Temp = FTransform()
        Temp.Point = self.Point + V.Point
        return Temp

    def __sub__(self, V: 'FTransform') -> 'FTransform':
        Temp = FTransform()
        Temp.Point = self.Point - V.Point
        return Temp

    def __mul__(self, Scale: float) -> 'FTransform':
        Temp = FTransform()
        Temp.Point = self.Point * Scale
        return Temp


# ----------------------------------------------------------------------
# FTransSample: transformed sample point (with normal, light, fog)
# ----------------------------------------------------------------------
class FTransSample(FTransform):
    def __init__(self):
        super().__init__()
        self.Normal: FPlane = FPlane()
        self.Light: FPlane = FPlane()
        self.Fog: FVector = FVector()

    def __add__(self, T: 'FTransSample') -> 'FTransSample':
        Temp = FTransSample()
        Temp.Point = self.Point + T.Point
        Temp.Light = self.Light + T.Light
        Temp.Fog = self.Fog + T.Fog
        return Temp

    def __sub__(self, T: 'FTransSample') -> 'FTransSample':
        Temp = FTransSample()
        Temp.Point = self.Point - T.Point
        Temp.Light = self.Light - T.Light
        Temp.Fog = self.Fog - T.Fog
        return Temp

    def __mul__(self, Scale: float) -> 'FTransSample':
        Temp = FTransSample()
        Temp.Point = self.Point * Scale
        Temp.Light = self.Light * Scale
        Temp.Fog = self.Fog * Scale
        return Temp


# ----------------------------------------------------------------------
# FTransTexture: transformed texture mapped point
# ----------------------------------------------------------------------
class FTransTexture(FTransSample):
    def __init__(self):
        super().__init__()
        self.U: float = 0.0
        self.V: float = 0.0

    def __add__(self, T: 'FTransTexture') -> 'FTransTexture':
        Temp = FTransTexture()
        Temp.Point = self.Point + T.Point
        Temp.Light = self.Light + T.Light
        Temp.Fog = self.Fog + T.Fog
        Temp.U = self.U + T.U
        Temp.V = self.V + T.V
        return Temp

    def __sub__(self, T: 'FTransTexture') -> 'FTransTexture':
        Temp = FTransTexture()
        Temp.Point = self.Point - T.Point
        Temp.Light = self.Light - T.Light
        Temp.Fog = self.Fog - T.Fog
        Temp.U = self.U - T.U
        Temp.V = self.V - T.V
        return Temp

    def __mul__(self, Scale: float) -> 'FTransTexture':
        Temp = FTransTexture()
        Temp.Point = self.Point * Scale
        Temp.Light = self.Light * Scale
        Temp.Fog = self.Fog * Scale
        Temp.U = self.U * Scale
        Temp.V = self.V * Scale
        return Temp


# ----------------------------------------------------------------------
# FSurfaceInfo: description of a renderable surface
# ----------------------------------------------------------------------
class FSurfaceInfo:
    def __init__(self):
        self.PolyFlags: int = 0
        self.FlatColor: FColor = FColor()
        self.Level: Optional['ULevel'] = None
        self.Texture: Optional[FTextureInfo] = None
        self.LightMap: Optional[FTextureInfo] = None
        self.MacroTexture: Optional[FTextureInfo] = None
        self.DetailTexture: Optional[FTextureInfo] = None
        self.FogMap: Optional[FTextureInfo] = None


# ----------------------------------------------------------------------
# FSavedPoly: a saved polygon
# ----------------------------------------------------------------------
class FSavedPoly:
    def __init__(self):
        self.Next: Optional['FSavedPoly'] = None
        self.iNode: int = 0
        self.User: Any = None
        self.NumPts: int = 0
        self.Pts: List[Any] = []  # FTransform*


# ----------------------------------------------------------------------
# FSurfaceFacet: description of a surface facet
# ----------------------------------------------------------------------
class FSurfaceFacet:
    def __init__(self):
        self.MapCoords: FCoords = FCoords()
        self.MapUncoords: FCoords = FCoords()
        self.Span: Optional[Any] = None  # FSpanBuffer*
        self.Polys: Optional[FSavedPoly] = None


# ----------------------------------------------------------------------
# FScreenBounds: screen extents of an axis-aligned bounding box
# ----------------------------------------------------------------------
class FScreenBounds:
    def __init__(self):
        self.MinX: float = 0.0
        self.MinY: float = 0.0
        self.MaxX: float = 0.0
        self.MaxY: float = 0.0
        self.MinZ: float = 0.0


# ----------------------------------------------------------------------
# ELineFlags: line drawing flags
# ----------------------------------------------------------------------
class ELineFlags(IntFlag):
    LINE_None = 0
    LINE_Transparent = 1
    LINE_DepthCued = 2


# ----------------------------------------------------------------------
# URenderBase: pure virtual base class of the rendering subsystem
# ----------------------------------------------------------------------
class URenderBase(UObject):
    def __init__(self):
        super().__init__()
        self.Engine: Optional[Any] = None  # UEngine*

    def init(self, InEngine: Any) -> None:
        self.Engine = InEngine

    def exec(self, cmd: str, out: Any) -> bool:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def pre_render(self, Frame: 'FSceneNode') -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def post_render(self, Frame: 'FSceneNode') -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def create_master_frame(self, Viewport: Any, Location: FVector, Rotation: Any,
                           Bounds: Optional[FScreenBounds]) -> 'FSceneNode':
        raise NotImplementedError("C++ virtual in Engine.lib")

    def create_child_frame(self, Parent: 'FSceneNode', Span: Any, Level: Any,
                          iSurf: int, iZone: int, Mirror: float, NearClip: FPlane,
                          Coords: FCoords, Bounds: Optional[FScreenBounds]) -> 'FSceneNode':
        raise NotImplementedError("C++ virtual in Engine.lib")

    def finish_master_frame(self) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def draw_world(self, Frame: 'FSceneNode') -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def draw_actor(self, Frame: 'FSceneNode', Actor: Any) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def project(self, Frame: 'FSceneNode', V: FVector) -> tuple[float, float, float]:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def deproject(self, Frame: 'FSceneNode', ScreenX: int, ScreenY: int) -> FVector:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def bound_visible(self, Frame: 'FSceneNode', Bound: Any, SpanBuffer: Any) -> FScreenBounds:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def get_visible_surfs(self, Viewport: Any) -> list[int]:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def global_lighting(self, Realtime: bool, Owner: Any) -> tuple[float, FPlane]:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def precache(self, Viewport: Any) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def draw_circle(self, Frame: 'FSceneNode', Color: FPlane, LineFlags: int,
                   Location: FVector, Radius: float, bScaleRadiusByZoom: bool = False) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def draw_box(self, Frame: 'FSceneNode', Color: FPlane, LineFlags: int,
                Min: FVector, Max: FVector) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def draw_cylinder(self, Frame: 'FSceneNode', Color: FPlane, LineFlags: int,
                     Location: FVector, Radius: float, Height: float) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")


# ----------------------------------------------------------------------
# HBspSurf: hit a Bsp surface
# ----------------------------------------------------------------------
class HBspSurf:
    def __init__(self, iInSurf: int = 0):
        self.iSurf: int = iInSurf
        self.Name: str = "HBspSurf"

    def get_name(self) -> str:
        return self.Name

    def isa(self, Str: str) -> bool:
        return Str == "HBspSurf"


# ----------------------------------------------------------------------
# HActor: hit an actor
# ----------------------------------------------------------------------
class HActor:
    def __init__(self, InActor: Any = None):
        self.Actor: Any = InActor
        self.Name: str = "HActor"

    def get_name(self) -> str:
        return self.Name

    def isa(self, Str: str) -> bool:
        return Str == "HActor"


# ----------------------------------------------------------------------
# HCoords: hit ray descriptor
# ----------------------------------------------------------------------
class HCoords:
    def __init__(self, InFrame: 'FSceneNode'):
        self.Coords: FCoords = InFrame.Coords
        self.Uncoords: FCoords = InFrame.Uncoords
        self.Direction: FVector = FVector()
        # Simplified - full computation omitted
        self.Name: str = "HCoords"

    def get_name(self) -> str:
        return self.Name

    def isa(self, Str: str) -> bool:
        return Str == "HCoords"


__all__ = [
    "ORTHO_LOW_DETAIL",
    "FVF_OutXMin", "FVF_OutXMax", "FVF_OutYMin", "FVF_OutYMax", "FVF_OutZMin", "FVF_OutZMax",
    "FOutVector", "FTransform", "FTransSample", "FTransTexture",
    "FSurfaceInfo", "FSavedPoly", "FSurfaceFacet", "FScreenBounds", "ELineFlags",
    "URenderBase", "HBspSurf", "HActor", "HCoords",
]