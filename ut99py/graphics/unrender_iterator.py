"""Port of Engine/Inc/UnRenderIterator.h (1 declared symbol).

URenderIterator: walks the actors visible from a camera frame. Every method
body lives in UnRenderIterator.cpp, so all of them raise NotImplementedError.
"""

from __future__ import annotations
from typing import Any, Optional
from ..core import UObject
from ..engine.render_structs import FSceneNode


class URenderIterator(UObject):
    """URenderIterator (UnRenderIterator.h:3-21)"""

    def __init__(self) -> None:
        super().__init__()
        # Members (UnRenderIterator.h:7-10).
        self.MaxItems: int = 0
        self.Index: int = 0
        self.Observer: Optional[Any] = None  # APlayerPawn*
        self.Frame: Optional[FSceneNode] = None
        # URenderIterator() body is in UnRenderIterator.cpp.
        raise NotImplementedError("C++ URenderIterator constructor: Engine.lib")

    def Init(self, Camera: FSceneNode) -> None:
        raise NotImplementedError("C++ URenderIterator::Init: Engine.lib")

    def UnInit(self) -> None:
        raise NotImplementedError("C++ URenderIterator::UnInit: Engine.lib")

    def First(self) -> None:
        raise NotImplementedError("C++ URenderIterator::First: Engine.lib")

    def Next(self) -> None:
        raise NotImplementedError("C++ URenderIterator::Next: Engine.lib")

    def IsDone(self) -> bool:
        raise NotImplementedError("C++ URenderIterator::IsDone: Engine.lib")

    def CurrentItem(self) -> Optional[Any]:
        raise NotImplementedError("C++ URenderIterator::CurrentItem: Engine.lib")


__all__ = ["URenderIterator"]
