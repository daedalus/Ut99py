"""Port of Engine/Inc/UnDynBsp.h (1 declared symbol).

FMovingBrushTrackerBase virtual base class + global GNewBrushTracker factory.
All pure virtual bodies raise NotImplementedError("Engine.lib").
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import FArchive


class FMovingBrushTrackerBase:
    """FMovingBrushTrackerBase (UnDynBsp.h:12-23) - moving brush tracker base.

    This object keeps the list of all dynamic brushes that are currently
    affecting the Bsp.
    """

    def __init__(self) -> None:
        pass  # virtual base destructor in C++ is empty {}

    def __del__(self) -> None:
        pass  # virtual destructor handled by Python GC

    def Update(self, Actor: Any) -> None:
        raise NotImplementedError("C++ FMovingBrushTrackerBase::Update: Engine.lib")

    def Flush(self, Actor: Any) -> None:
        raise NotImplementedError("C++ FMovingBrushTrackerBase::Flush: Engine.lib")

    def SurfIsDynamic(self, iSurf: int) -> bool:
        raise NotImplementedError("C++ FMovingBrushTrackerBase::SurfIsDynamic: Engine.lib")

    def CountBytes(self, Ar: Any) -> None:
        raise NotImplementedError("C++ FMovingBrushTrackerBase::CountBytes: Engine.lib")


def GNewBrushTracker(Level: Any) -> Optional[FMovingBrushTrackerBase]:
    """GNewBrushTracker (UnDynBsp.h:25) - factory for brush tracker instance.

    Returns a brush tracker object for the specified level.
    """
    raise NotImplementedError("C++ GNewBrushTracker: Engine.lib")


__all__ = ["FMovingBrushTrackerBase", "GNewBrushTracker"]
