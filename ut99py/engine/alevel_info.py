"""Port of Engine/Inc/ALevelInfo.h (0 declared symbols).

ALevelInfo: the class-body fragment included from EngineClasses.h. The
constructor is inline; GetOptimizedRepList() lives in Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .azone_info import AZoneInfo


class ALevelInfo(AZoneInfo):
    """ALevelInfo (ALevelInfo.h + EngineClasses.h:2572)."""

    def __init__(self) -> None:
        super().__init__()

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError("C++ ALevelInfo::GetOptimizedRepList: Engine.lib")


__all__ = ["ALevelInfo"]
