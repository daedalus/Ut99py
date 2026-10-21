"""Port of Engine/Inc/AAmmo.h (0 declared symbols).

AAmmo: the class-body fragment included from EngineClasses.h. The constructor
is inline; GetOptimizedRepList() lives in Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .apickup import APickup


class AAmmo(APickup):
    """AAmmo (AAmmo.h + EngineClasses.h:2065)."""

    def __init__(self) -> None:
        super().__init__()

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError("C++ AAmmo::GetOptimizedRepList: Engine.lib")


__all__ = ["AAmmo"]
