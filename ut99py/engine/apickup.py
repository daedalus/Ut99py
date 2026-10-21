"""Port of Engine/Inc/APickup.h (0 declared symbols).

APickup: the class-body fragment included from EngineClasses.h. The
constructor is inline; GetOptimizedRepList() lives in Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .ainventory import AInventory


class APickup(AInventory):
    """APickup (APickup.h + EngineClasses.h:2051)."""

    def __init__(self) -> None:
        super().__init__()

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError("C++ APickup::GetOptimizedRepList: Engine.lib")


__all__ = ["APickup"]
