"""Port of Engine/Inc/UnPrim.h (3 declared symbols).

UPrimitive (UObject) + FCheckResult + FIteratorActorList.
Provides bounding box/sphere and collision results.
All UPrimitive virtuals raise NotImplementedError("Engine.lib"); other
struct constructors inline.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core.types import FBox, FVector, FSphere
from ..core import UObject


class FIteratorList:
    """Minimal FIteratorList stand-in (UnPrim.h base)."""
    def __init__(self, next_node=None):
        self.Next = next_node

    def GetNext(self):
        return self.Next


class FIteratorActorList(FIteratorList):
    """FIteratorActorList (UnPrim.h:36-45)"""

    def __init__(self, next_node=None, actor=None):
        # C++ FIteratorActorList() {}
        # C++ FIteratorActorList( FIteratorActorList* InNext, AActor* InActor )
        super().__init__(next_node)
        self.Actor = actor  # None if first ctor


class FCheckResult(FIteratorActorList):
    """FCheckResult (UnPrim.h:47-77)"""

    def __init__(self, time: float = 0.0, next_node=None):
        # C++ FCheckResult() {}
        # C++ FCheckResult( FLOAT InTime, FCheckResult* InNext=NULL )
        super().__init__(next_node)
        self.Time = time
        self.Location: FVector = FVector()
        self.Normal: FVector = FVector()
        self.Primitive: Optional["UPrimitive"] = None
        self.Item: int = -1

    @staticmethod
    def compare_hits(a: "FCheckResult", b: "FCheckResult") -> int:
        # C++ CompareHits, used for sorting; stub for now.
        return 0


class UPrimitive(UObject):
    """UPrimitive (UnPrim.h:79-111)"""

    def __init__(self) -> None:
        super().__init__()
        self.BoundingBox: FBox = FBox()
        self.BoundingSphere: FSphere = FSphere()

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UPrimitive::Serialize: Engine.lib")

    def PointCheck(
        self, result: "FCheckResult", owner: Optional["AActor"], location: FVector, extent: FVector, extra_node_flags: int
    ) -> bool:
        raise NotImplementedError("C++ UPrimitive::PointCheck: Engine.lib")

    def LineCheck(
        self, result: "FCheckResult", owner: Optional["AActor"], end: FVector, start: FVector, extent: FVector, extra_node_flags: int
    ) -> bool:
        raise NotImplementedError("C++ UPrimitive::LineCheck: Engine.lib")

    def GetRenderBoundingBox(self, owner: Optional["AActor"], exact: bool) -> FBox:
        raise NotImplementedError("C++ UPrimitive::GetRenderBoundingBox: Engine.lib")

    def GetRenderBoundingSphere(self, owner: Optional["AActor"], exact: bool) -> FSphere:
        raise NotImplementedError("C++ UPrimitive::GetRenderBoundingSphere: Engine.lib")

    def GetCollisionBoundingBox(self, owner: Optional["AActor"]) -> FBox:
        raise NotImplementedError("C++ UPrimitive::GetCollisionBoundingBox: Engine.lib")