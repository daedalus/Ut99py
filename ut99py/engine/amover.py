"""Port of Engine/Inc/AMover.h (0 declared symbols).

AMover: the class-body fragment included from EngineClasses.h. The
constructor body lives in UnMover.cpp; every other body lives in
Engine.lib as well.
"""

from __future__ import annotations
from typing import Any
from .abrush import ABrush


class AMover(ABrush):
    """AMover (AMover.h + EngineClasses.h:1910)."""

    def __init__(self) -> None:
        super().__init__()
        # AMover() body is in UnMover.cpp.
        raise NotImplementedError("C++ AMover constructor: Engine.lib")

    def PostLoad(self) -> None:
        raise NotImplementedError("C++ AMover::PostLoad: Engine.lib")

    def PostEditChange(self) -> None:
        raise NotImplementedError("C++ AMover::PostEditChange: Engine.lib")

    def Spawned(self) -> None:
        raise NotImplementedError("C++ AMover::Spawned: Engine.lib")

    def PostEditMove(self) -> None:
        raise NotImplementedError("C++ AMover::PostEditMove: Engine.lib")

    def PreRaytrace(self) -> None:
        raise NotImplementedError("C++ AMover::PreRaytrace: Engine.lib")

    def PostRaytrace(self) -> None:
        raise NotImplementedError("C++ AMover::PostRaytrace: Engine.lib")

    def GetOptimizedRepList(
        self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int
    ) -> Any:
        raise NotImplementedError("C++ AMover::GetOptimizedRepList: Engine.lib")

    def SetWorldRaytraceKey(self) -> None:
        raise NotImplementedError("C++ AMover::SetWorldRaytraceKey: Engine.lib")

    def SetBrushRaytraceKey(self) -> None:
        raise NotImplementedError("C++ AMover::SetBrushRaytraceKey: Engine.lib")


__all__ = ["AMover"]
