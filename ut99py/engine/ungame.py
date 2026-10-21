"""Port of Engine/Inc/UnGame.h (1 declared symbol).

UGameEngine: the Unreal game engine object - level load and travel, server
play and frame drawing. Every method body lives in UnGame.cpp, so all of
them raise NotImplementedError.
"""

from __future__ import annotations
from typing import Any, Optional
from ..core import TArray
from .engine_core import UEngine
from .unurl import FURL


class UGameEngine(UEngine):
    """UGameEngine (UnGame.h:18-58)"""

    def __init__(self) -> None:
        super().__init__()
        # Variables (UnGame.h:22-27).
        self.GLevel: Optional[Any] = None  # ULevel*
        self.GEntry: Optional[Any] = None  # ULevel*
        self.GPendingLevel: Optional[Any] = None  # UPendingLevel*
        # FURL's constructor lives in Engine.lib, so the last URL stays
        # empty until the engine fills it in.
        self.LastURL: Optional[FURL] = None
        self.ServerActors: TArray = TArray()
        self.ServerPackages: TArray = TArray()
        # UGameEngine() body is in UnGame.cpp.
        raise NotImplementedError("C++ UGameEngine constructor: Engine.lib")

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UGameEngine::StaticConstructor: Engine.lib")

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UGameEngine::Serialize: Engine.lib")

    def Destroy(self) -> None:
        raise NotImplementedError("C++ UGameEngine::Destroy: Engine.lib")

    def Init(self) -> None:
        raise NotImplementedError("C++ UGameEngine::Init: Engine.lib")

    def Exit(self) -> None:
        raise NotImplementedError("C++ UGameEngine::Exit: Engine.lib")

    def Tick(self, DeltaSeconds: float) -> None:
        raise NotImplementedError("C++ UGameEngine::Tick: Engine.lib")

    def Draw(
        self,
        Viewport: Any,
        Blit: bool = True,
        HitData: Any = None,
        HitSize: Any = None,
    ) -> None:
        raise NotImplementedError("C++ UGameEngine::Draw: Engine.lib")

    def Exec(self, Cmd: str, Ar: Any = None) -> bool:
        raise NotImplementedError("C++ UGameEngine::Exec: Engine.lib")

    def MouseDelta(self, Viewport: Any, Buttons: int, DX: float, DY: float) -> None:
        raise NotImplementedError("C++ UGameEngine::MouseDelta: Engine.lib")

    def MousePosition(self, Viewport: Any, Buttons: int, X: float, Y: float) -> None:
        raise NotImplementedError("C++ UGameEngine::MousePosition: Engine.lib")

    def Click(self, Viewport: Any, Buttons: int, X: float, Y: float) -> None:
        raise NotImplementedError("C++ UGameEngine::Click: Engine.lib")

    def SetClientTravel(
        self, Viewport: Any, NextURL: str, bItems: bool, TravelType: Any
    ) -> None:
        raise NotImplementedError("C++ UGameEngine::SetClientTravel: Engine.lib")

    def GetMaxTickRate(self) -> float:
        raise NotImplementedError("C++ UGameEngine::GetMaxTickRate: Engine.lib")

    def ChallengeResponse(self, Challenge: int) -> int:
        raise NotImplementedError("C++ UGameEngine::ChallengeResponse: Engine.lib")

    def SetProgress(self, Str1: str, Str2: str, Seconds: float) -> None:
        raise NotImplementedError("C++ UGameEngine::SetProgress: Engine.lib")

    def Browse(self, URL: FURL, TravelInfo: Any = None, Error: Any = None) -> bool:
        raise NotImplementedError("C++ UGameEngine::Browse: Engine.lib")

    def LoadMap(
        self,
        URL: FURL,
        Pending: Any = None,
        TravelInfo: Any = None,
        Error: Any = None,
    ) -> Optional[Any]:
        raise NotImplementedError("C++ UGameEngine::LoadMap: Engine.lib")

    def SaveGame(self, Position: int) -> None:
        raise NotImplementedError("C++ UGameEngine::SaveGame: Engine.lib")

    def CancelPending(self) -> None:
        raise NotImplementedError("C++ UGameEngine::CancelPending: Engine.lib")

    def PaintProgress(self) -> None:
        raise NotImplementedError("C++ UGameEngine::PaintProgress: Engine.lib")

    def UpdateConnectingMessage(self) -> None:
        raise NotImplementedError(
            "C++ UGameEngine::UpdateConnectingMessage: Engine.lib"
        )

    def BuildServerMasterMap(self, NetDriver: Any, InLevel: Any) -> None:
        raise NotImplementedError("C++ UGameEngine::BuildServerMasterMap: Engine.lib")

    def NotifyLevelChange(self) -> None:
        raise NotImplementedError("C++ UGameEngine::NotifyLevelChange: Engine.lib")

    def FixUpLevel(self) -> None:
        raise NotImplementedError("C++ UGameEngine::FixUpLevel: Engine.lib")


__all__ = ["UGameEngine"]
