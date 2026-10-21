"""Port of Engine/Inc/AGameReplicationInfo.h (0 declared symbols).

AGameReplicationInfo: the class-body fragment included from EngineClasses.h.
The constructor is inline; GetOptimizedRepList() lives in Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .actor import AActor


class AInfo(AActor):
    """AInfo (EngineClasses.h:2239) - minimal local placeholder.

    AInfo is declared in EngineClasses.h and has no header fragment of its
    own, so it is not part of this port. The placeholder only supplies the
    base class of AZoneInfo and AReplicationInfo; the C++ class has no
    default constructor.
    """

    def __init__(self) -> None:
        super().__init__()


class AReplicationInfo(AInfo):
    """AReplicationInfo (EngineClasses.h:2247) - minimal local placeholder.

    Declared in EngineClasses.h without a header fragment of its own, so it
    is not part of this port; it only supplies the base class of the
    replication info actors.
    """

    def __init__(self) -> None:
        super().__init__()


class AGameReplicationInfo(AReplicationInfo):
    """AGameReplicationInfo (AGameReplicationInfo.h + EngineClasses.h:2255)."""

    def __init__(self) -> None:
        super().__init__()

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError(
            "C++ AGameReplicationInfo::GetOptimizedRepList: Engine.lib"
        )


__all__ = ["AInfo", "AReplicationInfo", "AGameReplicationInfo"]
