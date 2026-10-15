"""Port of Engine/Inc/UnCamera.h (16 declared symbols).

Viewport, canvas, and camera structures: UCanvas for drawing, UViewport
for rendering windows, UClient for viewport management, and related enums
(ERenderType, EViewportShowFlags, EMouseButtons, etc.). C++ event dispatch
/ ProcessEvent bodies raise NotImplementedError.
"""
from typing import Optional, List, Any
from enum import IntFlag, IntEnum
from ..core import UObject, FName, FVector, FRotator, FPlane, FArchive, FOutputDevice, TArray
from .render_structs import FSceneNode, FSpanBuffer


# ----------------------------------------------------------------------
# Enums for viewport rendering
# ----------------------------------------------------------------------
class ETextOut(IntEnum):
    TEXTOUT_Center = 0x01
    TEXTOUT_CenterVertical = 0x02
    TEXTOUT_Right = 0x04
    TEXTOUT_Bottom = 0x08
    TEXTOUT_Wrap = 0x10


class EViewportBlitFlags(IntFlag):
    BLIT_Fullscreen = 0x0001
    BLIT_Temporary = 0x0002
    BLIT_DibSection = 0x0004
    BLIT_DirectDraw = 0x0008
    BLIT_Direct3D = 0x0010
    BLIT_NoWindowChange = 0x0020
    BLIT_NoWindowFrame = 0x0040
    BLIT_OpenGL = 0x0080
    BLIT_HardwarePaint = 0x0100


class ERenderType(IntEnum):
    REN_None = 0
    REN_Wire = 1
    REN_Zones = 2
    REN_Polys = 3
    REN_PolyCuts = 4
    REN_DynLight = 5
    REN_PlainTex = 6
    REN_OrthXY = 13
    REN_OrthXZ = 14
    REN_OrthYZ = 15
    REN_TexView = 16
    REN_TexBrowser = 17
    REN_MeshView = 18
    REN_MAX = 20


class EViewportCaps(IntFlag):
    CC_RGB565 = 1
    CC_Mask = 0xff


class EViewportShowFlags(IntFlag):
    SHOW_Frame = 0x00000001
    SHOW_ActorRadii = 0x00000002
    SHOW_Backdrop = 0x00000004
    SHOW_Actors = 0x00000008
    SHOW_Coords = 0x00000010
    SHOW_ActorIcons = 0x00000020
    SHOW_Brush = 0x00000040
    SHOW_StandardView = 0x00000080
    SHOW_Menu = 0x00000100
    SHOW_ChildWindow = 0x00000200
    SHOW_MovingBrushes = 0x00000400
    SHOW_PlayerCtrl = 0x00000800
    SHOW_Paths = 0x00001000
    SHOW_NoButtons = 0x00002000
    SHOW_RealTime = 0x00004000


class EMouseButtons(IntEnum):
    MOUSE_Left = 0x0001
    MOUSE_Right = 0x0002
    MOUSE_Middle = 0x0004
    MOUSE_FirstHit = 0x0008
    MOUSE_LastRelease = 0x0010
    MOUSE_SetMode = 0x0020
    MOUSE_ExitMode = 0x0040
    MOUSE_Ctrl = 0x0080
    MOUSE_Shift = 0x0100
    MOUSE_Alt = 0x0200
    MOUSE_LeftDouble = 0x0200


# ----------------------------------------------------------------------
# UCanvas: drawing canvas
# ----------------------------------------------------------------------
class UCanvas(UObject):
    """Canvas for 2D drawing operations."""

    def __init__(self):
        super().__init__()
        self.Font: Optional[Any] = None  # UFont*
        self.SpaceX = 0.0
        self.SpaceY = 0.0
        self.OrgX = 0.0
        self.OrgY = 0.0
        self.ClipX = 0.0
        self.ClipY = 0.0
        self.CurX = 0.0
        self.CurY = 0.0
        self.Z = 0.0
        self.Style = 0
        self.CurYL = 0.0
        self.Color = None  # FColor
        self.bCenter = False
        self.bNoSmooth = False
        self.X = 0
        self.Y = 0
        self.SmallFont: Optional[Any] = None
        self.MedFont: Optional[Any] = None
        self.BigFont: Optional[Any] = None
        self.LargeFont: Optional[Any] = None
        self.Viewport: Optional["UViewport"] = None
        self.Frame: Optional[FSceneNode] = None
        self.Render: Optional["URenderBase"] = None

    def init(self, InViewport: "UViewport") -> None:
        self.Viewport = InViewport

    def update(self, Frame: FSceneNode) -> None:
        self.Frame = Frame

    def draw_tile(self, Texture: Any, X: float, Y: float, XL: float, YL: float,
                  U: float, V: float, UL: float, VL: float,
                  SpanBuffer: Optional[FSpanBuffer], Z: float,
                  Color: FPlane, Fog: FPlane, PolyFlags: int) -> None:
        raise NotImplementedError("C++ DrawTile in Engine.lib")

    def draw_text(self, Font: Any, X: float, Y: float, Text: str,
                  ClipX: float, ClipY: float, Style: int) -> None:
        raise NotImplementedError("C++ DrawText in Engine.lib")


# ----------------------------------------------------------------------
# FHitCause: hit-test cause info
# ----------------------------------------------------------------------
class FHitCause:
    """Information about a hit-test cause."""

    def __init__(self, Observer: Any, Viewport: "UViewport",
                 Buttons: int, MouseX: float, MouseY: float):
        self.Observer = Observer
        self.Viewport = Viewport
        self.Buttons = Buttons
        self.MouseX = MouseX
        self.MouseY = MouseY


# ----------------------------------------------------------------------
# FHitObserver: hit observer interface
# ----------------------------------------------------------------------
class FHitObserver:
    """Hit observer class for receiving hit-test notification."""

    def click(self, Cause: FHitCause, Hit: "HHitProxy") -> None:
        pass


# ----------------------------------------------------------------------
# HHitProxy: base hit proxy
# ----------------------------------------------------------------------
class HHitProxy:
    """Base class for detecting user-interface hits."""

    def __init__(self):
        self.Size: int = 0
        self.Parent: Optional["HHitProxy"] = None

    def get_name(self) -> str:
        return "HHitProxy"

    def isa(self, Str: str) -> bool:
        return Str == "HHitProxy" or (self.Parent and self.Parent.isa(Str))

    def click(self, Cause: FHitCause) -> None:
        if self.Observer:
            self.Observer.click(Cause, self)


# ----------------------------------------------------------------------
# UViewport: viewport object for rendering windows
# ----------------------------------------------------------------------
MAX_COLOR_BYTES = 9


class UViewport(UObject):
    """Viewport object, associates an actor with a window."""

    def __init__(self):
        super().__init__()
        self.Canvas: Optional[UCanvas] = None
        self.Input: Optional[Any] = None  # UInput*
        self.RenDev: Optional[Any] = None  # URenderDevice*

        self.MiscRes: Optional[UObject] = None
        self.Group = FName("None")
        self.LastUpdateTime = 0.0
        self.SizeX = 0
        self.SizeY = 0
        self.ColorBytes = 0
        self.FrameCount = 0
        self.Caps = 0
        self.Current = False
        self.Dragging = False
        self.RenderFlags = 0
        self.ExtraPolyFlags = 0

        self.TravelType = 0  # ETravelType
        self.TravelURL = ""
        self.bTravelItems = False

        self.CurrentTime = 0.0
        self.ScreenPointer: bytes = b""
        self.Stride = 0

        self.HitTesting = False
        self.HitX = 0
        self.HitY = 0
        self.HitXL = 0
        self.HitYL = 0
        self.HitSizes: List[int] = []

        self.SavedOrthoZoom = 0.0
        self.SavedFovAngle = 0.0
        self.SavedShowFlags = 0
        self.SavedRendMap = 0
        self.SavedMisc1 = 0
        self.SavedMisc2 = 0

    def _Screen(self, X: int, Y: int) -> int:
        return self.ScreenPointer + (X + Y * self.Stride) * self.ColorBytes

    def is_ortho(self, RendMap: int) -> bool:
        return RendMap in (REN_OrthXY, REN_OrthXZ, REN_OrthYZ)

    def byte_id(self) -> int:
        ColorBytesID = [0, 0, 1, 2, 3]
        return ColorBytesID[self.ColorBytes] | (self.Caps & 7) * 4


# ----------------------------------------------------------------------
# UClient: client for tracking viewports
# ----------------------------------------------------------------------
LODSET_MAX = 3


class UClient(UObject):
    """Client, responsible for tracking viewports."""

    def __init__(self):
        super().__init__()
        self.Engine: Optional[Any] = None  # UEngine*
        self.Viewports: List[UViewport] = []
        self.DrawCycles = 0

        self.CaptureMouse = False
        self.CurvedSurfaces = False
        self.ScreenFlashes = False
        self.NoLighting = False
        self.Decals = True
        self.NoDynamicLights = False
        self.NoFractalAnim = False
        self.WindowedViewportX = 640
        self.WindowedViewportY = 480
        self.WindowedColorBits = 32
        self.FullscreenViewportX = 1024
        self.FullscreenViewportY = 768
        self.FullscreenColorBits = 32
        self.Brightness = 1.0
        self.MipFactor = 1.0
        self.TextureLODSet = [0] * LODSET_MAX
        self.MinDesiredFrameRate = 30.0
        self.ParticleDensity = 0.0

    def new_viewport(self, Name: FName) -> UViewport:
        vp = UViewport()
        vp.Group = Name
        self.Viewports.append(vp)
        return vp


# ----------------------------------------------------------------------
# URenderBase: base rendering class (placeholder for Engine.lib)
# ----------------------------------------------------------------------
class URenderBase(UObject):
    """Base rendering class."""

    def __init__(self):
        super().__init__()


__all__ = [
    "ETextOut", "EViewportBlitFlags", "ERenderType", "EViewportCaps",
    "EViewportShowFlags", "EMouseButtons",
    "UCanvas", "FHitCause", "FHitObserver", "HHitProxy",
    "UViewport", "UClient", "URenderBase",
    "MAX_COLOR_BYTES", "LODSET_MAX",
]