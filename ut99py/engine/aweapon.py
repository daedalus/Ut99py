"""Port of Engine/Inc/AWeapon.h (0 declared symbols).

AWeapon: the class-body fragment included from EngineClasses.h. The
constructor is inline; GetOptimizedRepList() lives in Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .ainventory import AInventory


class AWeapon(AInventory):
    """AWeapon (AWeapon.h + EngineClasses.h:2078)."""

    def __init__(self) -> None:
        super().__init__()

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError("C++ AWeapon::GetOptimizedRepList: Engine.lib")


__all__ = ["AWeapon"]
