"""Port of Engine/Inc/APlayerReplicationInfo.h (0 declared symbols).

APlayerReplicationInfo: the class-body fragment included from
EngineClasses.h. The constructor is inline; GetOptimizedRepList() lives in
Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .agame_replication_info import AReplicationInfo


class APlayerReplicationInfo(AReplicationInfo):
    """APlayerReplicationInfo (APlayerReplicationInfo.h + EngineClasses.h:2286)."""

    def __init__(self) -> None:
        super().__init__()

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError(
            "C++ APlayerReplicationInfo::GetOptimizedRepList: Engine.lib"
        )


__all__ = ["APlayerReplicationInfo"]
