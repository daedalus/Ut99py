"""Port of Engine/Inc/UnPrim.h (3 declared symbols).

UPrimitive (UObject) + FCheckResult + FIteratorActorList.
Provides bounding box/sphere and collision results.
All UPrimitive virtuals raise NotImplementedError("Engine.lib"); other
struct constructors inline.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core.types import FBox, FVector, FSphere
from ..core.template import FIteratorList
from ..core import UObject


class FIteratorActorList(FIteratorList):
    """FIteratorActorList (UnPrim.h:36-45)"""

    def __init__(self) -> None:
        # C++ FIteratorActorList() {}
        super().__init__()
        self.Actor: Optional["AActor"] = None

    def __init__(self, next_node: Any, actor: "AActor") -> None:
        # C++ FIteratorActorList( FIteratorActorList* InNext, AActor* InActor )
        # Not trivial to reimplement with FIteratorList; omitted.
        super().__init__(next_node)
        self.Actor = actor

    def GetNext(self) -> Optional["FIteratorActorList"]:
        return super().GetNext()  # returns Any


class FCheckResult(FIteratorActorList):
    """FCheckResult (UnPrim.h:47-77)"""

    def __init__(self) -> None:
        # C++ FCheckResult() {}
        super().__init__()
        self.Location: FVector = FVector()
        self.Normal: FVector = FVector()
        self.Primitive: Optional["UPrimitive"] = None
        self.Time: float = 0.0
        self.Item: int = -1

    def __init__(self, time: float, next_node: Any = None) -> None:
        # C++ FCheckResult( FLOAT InTime, FCheckResult* InNext=NULL )
        super().__init__(next_node, None)
        self.Time = time
        self.Location = FVector()
        self.Normal = FVector()
        self.Primitive = None
        self.Item = -1

    def GetNext(self) -> Optional["FCheckResult"]:
        return super().GetNext()

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