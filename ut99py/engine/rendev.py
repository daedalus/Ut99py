"""Port of Engine/Inc/UnRenDev.h (3 declared symbols).

URenderDevice (USubsystem, CLASS_Config, Engine) with ELockRenderFlags and
EDescriptionFlags enums. All method bodies raise NotImplementedError("Engine.lib")
except Placeholder() which is inline virtual with empty body.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import USubsystem, UObject, FOutputDevice, FPlane
from ..core.types import FVector
from ..engine.texture import FTextureInfo, FColor
from ..engine.render_structs import (
    FSceneNode,
    FSurfaceInfo,
    FSurfaceFacet,
    FSpanBuffer,
    FTransTexture,
)
from ..engine.camera import UViewport


# ----------------------------------------------------------------------
# Enums (UnRenDev.h:16-32)
# ----------------------------------------------------------------------
class ELockRenderFlags(int):
    """LockRenderFlags bit flags (UnRenDev.h)."""
    LOCKR_ClearScreen = 1
    LOCKR_LightDiminish = 2


class EDescriptionFlags(int):
    """DescriptionFlags bit flags (UnRenDev.h)."""
    RDDESCF_Certified = 1
    RDDESCF_Incompatible = 2
    RDDESCF_LowDetailWorld = 4
    RDDESCF_LowDetailSkins = 8
    RDDESCF_LowDetailActors = 16


# ----------------------------------------------------------------------
# URenderDevice
# ----------------------------------------------------------------------
class URenderDevice(USubsystem):
    """URenderDevice (UnRenDev.h:34-105). Abstract rendering device interface."""

    # Variables (UnRenDev.h:37-56).
    DecompFormat: int = 0  # BYTE
    RecommendedLOD: int = 0  # INT
    Viewport: Optional['UViewport'] = None  # UViewport*
    Description: str = ""  # FString
    DescFlags: int = 0  # DWORD
    SpanBased: bool = False  # BITFIELD
    FullscreenOnly: bool = False  # BITFIELD
    SupportsFogMaps: bool = False  # BITFIELD
    SupportsDistanceFog: bool = False  # BITFIELD
    VolumetricLighting: bool = False  # BITFIELD
    ShinySurfaces: bool = False  # BITFIELD
    Coronas: bool = False  # BITFIELD
    HighDetailActors: bool = False  # BITFIELD
    SupportsTC: bool = False  # BITFIELD
    PrecacheOnFlip: bool = False  # BITFIELD
    SupportsLazyTextures: bool = False  # BITFIELD
    PrefersDeferredLoad: bool = False  # BITFIELD
    DetailTextures: bool = False  # BITFIELD
    Pad1: list = [0] * 8  # BITFIELD[8] as ints
    Pad0: list = [0] * 8  # DWORD[8]

    # Constructors (UnRenDev.h:58-60).
    def __init__(self) -> None:
        super().__init__()

    # UObject interface (UnRenDev.h:62).
    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ URenderDevice::Serialize: Engine.lib")

    # URenderDevice low-level functions (UnRenDev.h:64-102).
    def StaticConstructor(self) -> None:
        # UnRenDev.h:63: body in Engine.lib -> raise.
        raise NotImplementedError("C++ URenderDevice::StaticConstructor: Engine.lib")

    def Init(self, InViewport: 'UViewport', NewX: int, NewY: int, NewColorBytes: int, Fullscreen: bool) -> bool:
        raise NotImplementedError("C++ URenderDevice::Init: Engine.lib")

    def SetRes(self, NewX: int, NewY: int, NewColorBytes: int, Fullscreen: bool) -> bool:
        raise NotImplementedError("C++ URenderDevice::SetRes: Engine.lib")

    def Exit(self) -> None:
        raise NotImplementedError("C++ URenderDevice::Exit: Engine.lib")

    def Flush(self, AllowPrecache: bool) -> None:
        raise NotImplementedError("C++ URenderDevice::Flush: Engine.lib")

    def Exec(self, Cmd: str, Ar: 'FOutputDevice') -> bool:
        # UnRenDev.h:78: virtual UBOOL Exec( const TCHAR* Cmd, FOutputDevice& Ar );
        # Note: has default implementation {} in header? Actually it's virtual with body?
        # In header: virtual UBOOL Exec( const TCHAR* Cmd, FOutputDevice& Ar ); -> no body shown -> raise.
        raise NotImplementedError("C++ URenderDevice::Exec: Engine.lib")

    def Lock(self, FlashScale: 'FPlane', FlashFog: 'FPlane', ScreenClear: 'FPlane', RenderLockFlags: int, HitData: Any, HitSize: Any) -> None:
        raise NotImplementedError("C++ URenderDevice::Lock: Engine.lib")

    def Unlock(self, Blit: bool) -> None:
        raise NotImplementedError("C++ URenderDevice::Unlock: Engine.lib")

    def DrawComplexSurface(self, Frame: 'FSceneNode', Surface: 'FSurfaceInfo', Facet: 'FSurfaceFacet') -> None:
        raise NotImplementedError("C++ URenderDevice::DrawComplexSurface: Engine.lib")

    def DrawGouraudPolygon(self, Frame: 'FSceneNode', Info: 'FTextureInfo', Pts: Any, NumPts: int, PolyFlags: int, Span: 'FSpanBuffer') -> None:
        raise NotImplementedError("C++ URenderDevice::DrawGouraudPolygon: Engine.lib")

    def DrawTile(self, Frame: 'FSceneNode', Info: 'FTextureInfo', X: float, Y: float, XL: float, YL: float, U: float, V: float, UL: float, VL: float, Span: 'FSpanBuffer', Z: float, Color: 'FPlane', Fog: 'FPlane', PolyFlags: int) -> None:
        raise NotImplementedError("C++ URenderDevice::DrawTile: Engine.lib")

    def Draw3DLine(self, Frame: 'FSceneNode', Color: 'FPlane', LineFlags: int, OrigP: 'FVector', OrigQ: 'FVector') -> None:
        raise NotImplementedError("C++ URenderDevice::Draw3DLine: Engine.lib")

    def Draw2DClippedLine(self, Frame: 'FSceneNode', Color: 'FPlane', LineFlags: int, P1: 'FVector', P2: 'FVector') -> None:
        raise NotImplementedError("C++ URenderDevice::Draw2DClippedLine: Engine.lib")

    def Draw2DLine(self, Frame: 'FSceneNode', Color: 'FPlane', LineFlags: int, P1: 'FVector', P2: 'FVector') -> None:
        raise NotImplementedError("C++ URenderDevice::Draw2DLine: Engine.lib")

    def Draw2DPoint(self, Frame: 'FSceneNode', Color: 'FPlane', LineFlags: int, X1: float, Y1: float, X2: float, Y2: float, Z: float) -> None:
        raise NotImplementedError("C++ URenderDevice::Draw2DPoint: Engine.lib")

    def ClearZ(self, Frame: 'FSceneNode') -> None:
        raise NotImplementedError("C++ URenderDevice::ClearZ: Engine.lib")

    def PushHit(self, Data: Any, Count: int) -> None:
        raise NotImplementedError("C++ URenderDevice::PushHit: Engine.lib")

    def PopHit(self, Count: int, bForce: bool) -> None:
        raise NotImplementedError("C++ URenderDevice::PopHit: Engine.lib")

    def GetStats(self, Result: str) -> None:
        raise NotImplementedError("C++ URenderDevice::GetStats: Engine.lib")

    def ReadPixels(self, Pixels: 'FColor') -> None:
        raise NotImplementedError("C++ URenderDevice::ReadPixels: Engine.lib")

    def EndFlash(self) -> None:
        # UnRenDev.h:91: virtual void EndFlash() {} -> inline empty body.
        return None

    def DrawStats(self, Frame: 'FSceneNode') -> None:
        # UnRenDev.h:92: virtual void DrawStats( FSceneNode* Frame ) {} -> inline empty body.
        return None

    def SetSceneNode(self, Frame: 'FSceneNode') -> None:
        # UnRenDev.h:93: virtual void SetSceneNode( FSceneNode* Frame ) {} -> inline empty body.
        return None

    def PrecacheTexture(self, Info: 'FTextureInfo', PolyFlags: int) -> None:
        # UnRenDev.h:94: virtual void PrecacheTexture( FTextureInfo& Info, DWORD PolyFlags ) {} -> inline empty body.
        return None

    # Padding virtuals (UnRenDev.h:96-103).
    def vtblPad0(self) -> None:
        raise NotImplementedError("C++ URenderDevice::vtblPad0: Engine.lib")

    def vtblPad1(self) -> None:
        raise NotImplementedError("C++ URenderDevice::vtblPad1: Engine.lib")

    def vtblPad2(self) -> None:
        raise NotImplementedError("C++ URenderDevice::vtblPad2: Engine.lib")

    def vtblPad3(self) -> None:
        raise NotImplementedError("C++ URenderDevice::vtblPad3: Engine.lib")

    def vtblPad4(self) -> None:
        raise NotImplementedError("C++ URenderDevice::vtblPad4: Engine.lib")

    def vtblPad5(self) -> None:
        raise NotImplementedError("C++ URenderDevice::vtblPad5: Engine.lib")

    def vtblPad6(self) -> None:
        raise NotImplementedError("C++ URenderDevice::vtblPad6: Engine.lib")

    def vtblPad7(self) -> None:
        raise NotImplementedError("C++ URenderDevice::vtblPad7: Engine.lib")