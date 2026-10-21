"""Port of Engine/Inc/ACarcass.h (0 declared symbols).

ACarcass: the class-body fragment included from EngineClasses.h. The
constructor is inline; UpdateFrequency() lives in Engine.lib.
"""

from __future__ import annotations
from typing import Any
from .actor import AActor


class ADecoration(AActor):
    """ADecoration (EngineClasses.h:3026) - minimal local placeholder.

    ADecoration is declared in EngineClasses.h and has no header fragment
    of its own, so it is not part of this port; it only supplies the base
    class of ACarcass.
    """

    def __init__(self) -> None:
        super().__init__()


class ACarcass(ADecoration):
    """ACarcass (ACarcass.h + EngineClasses.h:3047)."""

    def __init__(self) -> None:
        super().__init__()

    def UpdateFrequency(self, Viewer: Any, ViewDir: Any, ViewPos: Any) -> float:
        raise NotImplementedError("C++ ACarcass::UpdateFrequency: Engine.lib")


__all__ = ["ADecoration", "ACarcass"]
