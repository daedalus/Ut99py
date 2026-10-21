"""Port of Engine/Inc/UnReach.h (1 declared symbol).

FReachSpec: AI reach specifications (endpoints, collision size, flags).
supports(), Init() and the archive operator<< have inline bodies; every
other method lives in UnReach.cpp and raises NotImplementedError.
"""

from __future__ import annotations
from typing import Any, Optional


class FReachSpec:
    """FReachSpec (UnReach.h:9-60)"""

    def __init__(self) -> None:
        # Members (UnReach.h:13-19); FReachSpec::Init() zeroes them all.
        self.distance: int = 0
        self.Start: Optional[Any] = None  # AActor*
        self.End: Optional[Any] = None  # AActor* at the path endpoint
        self.CollisionRadius: int = 0
        self.CollisionHeight: int = 0
        self.reachFlags: int = 0  # EReachSpecFlags bits
        self.bPruned: int = 0

    def supports(self, iRadius: int, iHeight: int, moveFlags: int) -> bool:
        """FReachSpec::supports (UnReach.h:25-30) - inline body.

        Distance is not considered.
        """
        return (
            self.CollisionRadius >= iRadius
            and self.CollisionHeight >= iHeight
            and (self.reachFlags & moveFlags) == self.reachFlags
        )

    def Init(self) -> None:
        """FReachSpec::Init (UnReach.h:38-47) - inline body."""
        self.Start = None
        self.End = None
        self.distance = 0
        self.CollisionRadius = 0
        self.CollisionHeight = 0
        self.reachFlags = 0
        self.bPruned = 0

    def serialize(self, Ar: Any) -> Any:
        """C++ friend operator<<(FArchive& Ar, FReachSpec& ReachSpec) (UnReach.h:49-57) - inline body.

        Start and End are actor references, so they travel as compact object
        indices; bPruned is a BYTE, not an INT.
        """
        self.distance = Ar.serialize_int32(self.distance)
        self.Start = Ar.serialize_object(self.Start)
        self.End = Ar.serialize_object(self.End)
        self.CollisionRadius = Ar.serialize_int32(self.CollisionRadius)
        self.CollisionHeight = Ar.serialize_int32(self.CollisionHeight)
        self.reachFlags = Ar.serialize_int32(self.reachFlags)
        self.bPruned = Ar.serialize_byte(self.bPruned)
        return Ar

    def __add__(self, Spec: "FReachSpec") -> "FReachSpec":
        """C++ operator+ (const FReachSpec& Spec) const (UnReach.h:31)."""
        raise NotImplementedError("C++ FReachSpec::operator+: Engine.lib")

    def defineFor(self, begin: Any, dest: Any, Scout: Any) -> int:
        raise NotImplementedError("C++ FReachSpec::defineFor: Engine.lib")

    def __le__(self, Spec: "FReachSpec") -> bool:
        """C++ operator<= (const FReachSpec& Spec) (UnReach.h:33)."""
        raise NotImplementedError("C++ FReachSpec::operator<=: Engine.lib")

    def __eq__(self, Spec: "FReachSpec") -> bool:
        """C++ operator== (const FReachSpec& Spec) (UnReach.h:34)."""
        raise NotImplementedError("C++ FReachSpec::operator==: Engine.lib")

    def MonsterPath(self) -> int:
        raise NotImplementedError("C++ FReachSpec::MonsterPath: Engine.lib")

    def BotOnlyPath(self) -> int:
        raise NotImplementedError("C++ FReachSpec::BotOnlyPath: Engine.lib")

    def findBestReachable(self, Start: Any, Destination: Any, Scout: Any) -> int:
        raise NotImplementedError("C++ FReachSpec::findBestReachable: Engine.lib")


__all__ = ["FReachSpec"]
