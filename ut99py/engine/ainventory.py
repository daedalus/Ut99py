"""Port of Engine/Inc/AInventory.h (0 declared symbols).

AInventory: the class-body fragment included from EngineClasses.h.
CheckRecentChanges() has an inline body (it returns 1); every other body
lives in Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .actor import AActor


class AInventory(AActor):
    """AInventory (AInventory.h + EngineClasses.h:1980)."""

    def __init__(self) -> None:
        super().__init__()

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError("C++ AInventory::GetOptimizedRepList: Engine.lib")

    def ShouldDoScriptReplication(self) -> bool:
        raise NotImplementedError(
            "C++ AInventory::ShouldDoScriptReplication: Engine.lib"
        )

    def NoVariablesToReplicate(self, OldVer: Any) -> bool:
        raise NotImplementedError("C++ AInventory::NoVariablesToReplicate: Engine.lib")

    def CheckRecentChanges(self) -> bool:
        """AInventory::CheckRecentChanges (AInventory.h:16) - inline body."""
        return True

    def UpdateFrequency(self, Viewer: Any, ViewDir: Any, ViewPos: Any) -> float:
        raise NotImplementedError("C++ AInventory::UpdateFrequency: Engine.lib")


__all__ = ["AInventory"]
