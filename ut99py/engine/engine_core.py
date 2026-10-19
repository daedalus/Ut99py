"""Port of Engine/Inc/UnEngine.h (6 declared symbols).

UEngine (USubsystem, CLASS_Config|CLASS_Transient) + UServerCommandlet.
Reference C++ classes: UAudioSubsystem, UClient, UPrimitive, URenderBase.
All method bodies raise NotImplementedError("Engine.lib").
"""

from __future__ import annotations
from typing import Any

from ..core import USubsystem
from ..ucc import UServerCommandlet

DO_ENABLE_NET_TEST: bool = True
MAX_PROTOCOL_VERSION: int = 1
MIN_PROTOCOL_VERSION: int = 1
MAX_CHANNELS: int = 1023


class UEngine(USubsystem):
    """UnEngine.h:11-93"""

    GameRenderDeviceClass: Any = None
    AudioDeviceClass: Any = None
    ConsoleClass: Any = None
    NetworkDriverClass: Any = None
    LanguageClass: Any = None
    Cylinder: Any = None
    Client: Any = None
    Render: Any = None
    Audio: Any = None
    TickCycles: int = 0
    GameCycles: int = 0
    ClientCycles: int = 0
    CacheSizeMegs: int = 0
    UseSound: bool = False
    CurrentTickRate: float = 0.0

    def __init__(self) -> None:
        super().__init__()

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UEngine::Serialize: Engine.lib")

    def Destroy(self) -> None:
        raise NotImplementedError("C++ UEngine::Destroy: Engine.lib")

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UEngine::StaticConstructor: Engine.lib")

    def Init(self) -> None:
        raise NotImplementedError("C++ UEngine::Init: Engine.lib")

    def Exit(self) -> None:
        raise NotImplementedError("C++ UEngine::Exit: Engine.lib")

    def Exec(self, Cmd: Any, Out: Any = None) -> bool:
        raise NotImplementedError("C++ UEngine::Exec: Engine.lib")

    def Flush(self, AllowPrecache: bool) -> None:
        raise NotImplementedError("C++ UEngine::Flush: Engine.lib")

    def Key(self, Viewport: Any, Key: Any) -> bool:
        raise NotImplementedError("C++ UEngine::Key: Engine.lib")

    def InputEvent(
        self, Viewport: Any, iKey: Any, State: Any, Delta: float = 0.0
    ) -> bool:
        raise NotImplementedError("C++ UEngine::InputEvent: Engine.lib")

    def Tick(self, DeltaSeconds: float) -> None:
        raise NotImplementedError("C++ UEngine::Tick: Engine.lib")

    def Draw(
        self, Viewport: Any, Blit: bool = True, HitData: Any = None, HitSize: Any = None
    ) -> None:
        raise NotImplementedError("C++ UEngine::Draw: Engine.lib")

    def MouseDelta(self, Viewport: Any, Buttons: int, DX: float, DY: float) -> None:
        raise NotImplementedError("C++ UEngine::MouseDelta: Engine.lib")

    def MousePosition(self, Viewport: Any, Buttons: int, X: float, Y: float) -> None:
        raise NotImplementedError("C++ UEngine::MousePosition: Engine.lib")

    def Click(self, Viewport: Any, Buttons: int, X: float, Y: float) -> None:
        raise NotImplementedError("C++ UEngine::Click: Engine.lib")

    def SetClientTravel(
        self, Viewport: Any, NextURL: Any, bItems: bool, TravelType: Any
    ) -> None:
        raise NotImplementedError("C++ UEngine::SetClientTravel: Engine.lib")

    def ChallengeResponse(self, Challenge: int) -> int:
        raise NotImplementedError("C++ UEngine::ChallengeResponse: Engine.lib")

    def GetMaxTickRate(self) -> float:
        raise NotImplementedError("C++ UEngine::GetMaxTickRate: Engine.lib")

    def SetProgress(self, Str1: Any, Str2: Any, Seconds: float) -> None:
        raise NotImplementedError("C++ UEngine::SetProgress: Engine.lib")

    def InitAudio(self) -> None:
        raise NotImplementedError("C++ UEngine::InitAudio: Engine.lib")

    def edSetClickLocation(self, InLocation: Any) -> None:
        pass  # UnEngine.h:93 inline return 0

    def edcamMode(self, Viewport: Any) -> int:
        return 0  # UnEngine.h:88 inline


__all__ = [
    "UEngine",
    "UServerCommandlet",
    "DO_ENABLE_NET_TEST",
    "MAX_PROTOCOL_VERSION",
    "MIN_PROTOCOL_VERSION",
    "MAX_CHANNELS",
]
