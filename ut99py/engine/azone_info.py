"""Port of Engine/Inc/AZoneInfo.h (0 declared symbols).

AZoneInfo: the class-body fragment included from EngineClasses.h. The
constructor is inline; PostEditChange() and GetOptimizedRepList() live in
Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .agame_replication_info import AInfo


class AZoneInfo(AInfo):
    """AZoneInfo (AZoneInfo.h + EngineClasses.h:2434)."""

    def __init__(self) -> None:
        super().__init__()

    def PostEditChange(self) -> None:
        raise NotImplementedError("C++ AZoneInfo::PostEditChange: Engine.lib")

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError("C++ AZoneInfo::GetOptimizedRepList: Engine.lib")


__all__ = ["AZoneInfo"]
