"""Port of Engine/Inc/APlayerPawn.h (0 declared symbols).

APlayerPawn: the class-body fragment included from EngineClasses.h. It
adds the player link and the PlayerPawn Render Control Interface; every
body lives in Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .pawn import APawn
from .unplayer import UPlayer


class APlayerPawn(APawn):
    """APlayerPawn (APlayerPawn.h + EngineClasses.h:1631)."""

    def __init__(self) -> None:
        super().__init__()

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError("C++ APlayerPawn::GetOptimizedRepList: Engine.lib")

    def SetPlayer(self, Player: UPlayer) -> None:
        raise NotImplementedError("C++ APlayerPawn::SetPlayer: Engine.lib")

    # PlayerPawn Render Control Interface (APlayerPawn.h:16-23).
    def ClearScreen(self) -> bool:
        raise NotImplementedError("C++ APlayerPawn::ClearScreen: Engine.lib")

    def RecomputeLighting(self) -> bool:
        raise NotImplementedError("C++ APlayerPawn::RecomputeLighting: Engine.lib")

    def CanSee(self, Actor: Any) -> bool:
        raise NotImplementedError("C++ APlayerPawn::CanSee: Engine.lib")

    def GetViewZone(self, iViewZone: int, Model: Any) -> int:
        raise NotImplementedError("C++ APlayerPawn::GetViewZone: Engine.lib")

    def IsZoneVisible(self, iZone: int) -> bool:
        raise NotImplementedError("C++ APlayerPawn::IsZoneVisible: Engine.lib")

    def IsSurfVisible(self, Node: Any, iZone: int, Poly: Any) -> bool:
        raise NotImplementedError("C++ APlayerPawn::IsSurfVisible: Engine.lib")

    def IsActorVisible(self, Actor: Any) -> bool:
        raise NotImplementedError("C++ APlayerPawn::IsActorVisible: Engine.lib")


__all__ = ["APlayerPawn"]
