"""Port of Engine/Inc/UnLevel.h (12 declared symbols).

Level management structures: ULevelBase, ULevel (extends ULevelBase),
FNetworkNotify, FCollisionHashBase interfaces, plus EAcceptConnection,
ETraceActorFlags, ELevelTick enums and FStaticBrushIterator.
Serialization implemented from UnLevel.cpp lines 67-100, 233-260.
"""
from typing import Optional, Any, List
from enum import IntFlag, IntEnum

from ..core import UObject, FName, FVector, FRotator, FArchive, FGuid, FString
from ..core.system import AR_INDEX
from .unreach import FReachSpec
from .unurl import FURL


# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------
class EAcceptConnection(IntEnum):
    ACCEPTC_Reject = 0
    ACCEPTC_Accept = 1
    ACCEPTC_Ignore = 2


class ETraceActorFlags(IntFlag):
    TRACE_Pawns = 0x01
    TRACE_Movers = 0x02
    TRACE_Level = 0x04
    TRACE_ZoneChanges = 0x08
    TRACE_Others = 0x10
    TRACE_OnlyProjActor = 0x20

    TRACE_VisBlocking = TRACE_Level | TRACE_Movers
    TRACE_AllColliding = TRACE_Pawns | TRACE_Movers | TRACE_Level | TRACE_Others
    TRACE_AllEverything = TRACE_Pawns | TRACE_Movers | TRACE_Level | TRACE_ZoneChanges | TRACE_Others
    TRACE_ProjTargets = TRACE_OnlyProjActor | TRACE_AllColliding


class ELevelTick(IntEnum):
    LEVELTICK_TimeOnly = 0
    LEVELTICK_ViewportsOnly = 1
    LEVELTICK_All = 2


# ----------------------------------------------------------------------
# FNetworkNotify: network notification sink interface
# ----------------------------------------------------------------------
class FNetworkNotify:
    """Accepting connection responses and network notifications."""

    def notify_accepting_connection(self) -> EAcceptConnection:
        """FNetworkNotify::notify_accepting_connection (UnLevel.h:50) - virtual
        in C++ Engine.lib. The port stubs it as no-op."""
        return EAcceptConnection.ACCEPTC_Ignore

    def notify_accepted_connection(self, Connection: Any) -> None:
        """FNetworkNotify::notify_accepted_connection (UnLevel.h:55) - virtual."""
        pass

    def notify_accepting_channel(self, Channel: Any) -> bool:
        """FNetworkNotify::notify_accepting_channel (UnLevel.h:59) - virtual."""
        return False

    def notify_get_level(self) -> Optional['ULevelBase']:
        """FNetworkNotify::notify_get_level (UnLevel.h:62) - virtual."""
        return None

    def notify_received_text(self, Connection: Any, Text: str) -> None:
        """FNetworkNotify::notify_received_text (UnLevel.h:65) - virtual."""
        pass

    def notify_sending_file(self, Connection: Any, GUID: FGuid) -> bool:
        """FNetworkNotify::notify_sending_file (UnLevel.h:68) - virtual."""
        return False

    def notify_received_file(self, Connection: Any, PackageIndex: int,
                             Error: str, Skipped: bool) -> None:
        """FNetworkNotify::notify_received_file (UnLevel.h:72) - virtual."""
        pass

    def notify_progress(self, Str1: str, Str2: str, Seconds: float) -> None:
        """FNetworkNotify::notify_progress (UnLevel.h:75) - virtual."""
        pass


# ----------------------------------------------------------------------
# FCollisionHashBase: collision hash base class
# ----------------------------------------------------------------------
class FCollisionHashBase:
    def tick(self) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def add_actor(self, Actor: Any) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def remove_actor(self, Actor: Any) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def actor_line_check(self, Mem: Any, End: FVector, Start: FVector,
                         Extent: FVector, ExtraNodeFlags: int) -> Any:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def actor_point_check(self, Mem: Any, Location: FVector, Extent: FVector,
                          ExtraNodeFlags: int) -> Any:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def actor_radius_check(self, Mem: Any, Location: FVector, Radius: float,
                           ExtraNodeFlags: int) -> Any:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def actor_encroachment_check(self, Mem: Any, Actor: Any,
                                  Location: FVector, Rotation: FRotator,
                                  ExtraNodeFlags: int) -> Any:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def check_actor_not_referenced(self, Actor: Any) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")


def g_new_collision_hash() -> FCollisionHashBase:
    """Factory for creating a collision hash instance."""
    raise NotImplementedError("C++ GNewCollisionHash in Engine.lib")


# ----------------------------------------------------------------------
# ULevelBase: base level class with network notify
# ----------------------------------------------------------------------
NUM_LEVEL_TEXT_BLOCKS = 16


class ULevelBase(UObject, FNetworkNotify):
    """A game level base class."""

    def __init__(self) -> None:
        super().__init__()
        self.Actors: List[Any] = []
        self.NetDriver: Optional[Any] = None
        self.Engine: Optional[Any] = None
        self.URL: Optional[Any] = None
        self.DemoRecDriver: Optional[Any] = None

    def serialize(self, ar: Any) -> 'ULevelBase':
        """ULevelBase::Serialize (UnLevel.cpp:67-100).

        Args:
            ar: Archive (ULinkerLoad or FArchiveMemoryReader).
        Returns:
            self for chaining.
        """
        super().serialize(ar)  # UObject::Serialize: the property block.

        # Actors (UnLevel.cpp:77-88): the old file format keeps the count
        # twice, then the actor references.
        if ar.is_trans():
            ar.serialize_tarray(self.Actors)
        else:
            db_num = ar.serialize_int32(len(self.Actors))
            ar.serialize_int32(db_num)  # DbMax
            if ar.is_loading():
                self.Actors = [ar.serialize_object(None) for _ in range(db_num)]

        # URL (UnLevel.cpp:91): an FURL value, not a pointer.
        if self.URL is None:
            self.URL = FURL()
        self.URL.serialize(ar)

        if not ar.is_loading() and not ar.is_saving():
            ar.serialize_object(self.NetDriver)
            ar.serialize_object(self.DemoRecDriver)
        return self


# ----------------------------------------------------------------------
# ULevel: level object (extends ULevelBase)
# ----------------------------------------------------------------------
class ULevel(ULevelBase):
    """The level object. Contains the level's actor list, Bsp info, brush list."""

    def __init__(self) -> None:
        super().__init__()
        self.ReachSpecs: List[FReachSpec] = []
        self.Model: Optional[Any] = None
        self.TextBlocks: List[Optional[Any]] = [None] * NUM_LEVEL_TEXT_BLOCKS
        self.TimeSeconds: float = 0.0
        self.TravelInfo: dict = {}

        self.Hash: Optional['FCollisionHashBase'] = None
        self.BrushTracker: Optional[Any] = None
        self.FirstDeleted: Optional[Any] = None
        self.NewlySpawned: Optional[Any] = None
        self.InTick = False
        self.Ticked = False
        self.iFirstDynamicActor = 0
        self.iFirstNetRelevantActor = 0
        self.NetTag = 0
        self.ZoneDist = [[0] * 64 for _ in range(64)]

        self.NetTickCycles = 0
        self.NetDiffCycles = 0
        self.ActorTickCycles = 0
        self.AudioTickCycles = 0
        self.FindPathCycles = 0
        self.MoveCycles = 0
        self.NumMoves = 0
        self.NumReps = 0
        self.NumPV = 0
        self.GetRelevantCycles = 0
        self.NumRPC = 0
        self.SeePlayer = 0
        self.Spawning = 0
        self.Unused = 0

    def serialize_level(self, ar: Any) -> 'ULevel':
        """ULevel::Serialize (UnLevel.cpp:233-263).

        Args:
            ar: Archive (ULinkerLoad or FArchiveMemoryReader).

        Returns:
            self for chaining.
        """
        super().serialize(ar)  # ULevelBase::Serialize

        # Model (UModel reference).
        self.Model = ar.serialize_object(self.Model)
        # ReachSpecs (TArray<FReachSpec>).
        self.ReachSpecs = ar.serialize_tarray(self.ReachSpecs, element=FReachSpec)
        # ApproxTime: the C++ writes TimeSeconds as a FLOAT.
        self.TimeSeconds = ar.serialize_float(float(self.TimeSeconds))
        # FirstDeleted (AActor reference).
        self.FirstDeleted = ar.serialize_object(self.FirstDeleted)
        # TextBlocks[NUM_LEVEL_TEXT_BLOCKS] (UTextBuffer references).
        for i in range(NUM_LEVEL_TEXT_BLOCKS):
            self.TextBlocks[i] = ar.serialize_object(self.TextBlocks[i])
        # TravelInfo (TMap<FString,FString>), which the C++ stores as the
        # map's pair array (UnTemplate.h:1745).
        if ar.ver() > 62:
            count = AR_INDEX(ar, len(self.TravelInfo))
            if ar.is_loading():
                self.TravelInfo = {}
                for _ in range(count):
                    key = ar.serialize_str(FString())
                    value = ar.serialize_str(FString())
                    self.TravelInfo[str(key)] = str(value)
            else:
                for key, value in self.TravelInfo.items():
                    ar.serialize_str(FString(key))
                    ar.serialize_str(FString(value))
        elif ar.ver() >= 61:
            # oldver (UnLevel.cpp:249-255): the map as two string arrays.
            names = ar.serialize_tarray([], element=FString)
            items = ar.serialize_tarray([], element=FString)
            if ar.is_loading():
                self.TravelInfo = dict(zip(names, items))

        # Preload Model if present and not trans
        if self.Model is not None and not ar.is_trans():
            pass  # Ar.Preload(Model) would happen here

        if self.BrushTracker:
            ar.count_bytes(0, 0)  # BrushTracker->CountBytes(Ar)

        return self

    def serialize(self, ar: Any) -> 'ULevel':
        """ULevel::Serialize (UnLevel.cpp:233-263) - the linker entry point."""
        return self.serialize_level(ar)

    def destroy(self) -> None:
        raise NotImplementedError("C++ Destroy in Engine.lib")


# ----------------------------------------------------------------------
# FStaticBrushIterator: iterate static brushes in a level
# ----------------------------------------------------------------------
class FStaticBrushIterator:
    def __init__(self, Level: ULevel) -> None:
        self.Level = Level
        self.Index = -1
        self._increment()

    def _increment(self) -> None:
        while True:
            self.Index += 1
            if self.Index >= len(self.Level.Actors):
                self.Level = None
                break
            actor = self.Level.Actors[self.Index]
            if actor and actor.is_static_brush():
                break

    def __next__(self) -> Any:
        if self.Level is None:
            raise StopIteration
        result = self.Level.Actors[self.Index]
        self._increment()
        return result

    def __iter__(self):
        return self


__all__ = [
    "EAcceptConnection", "ETraceActorFlags", "ELevelTick",
    "FNetworkNotify", "FCollisionHashBase", "g_new_collision_hash",
    "NUM_LEVEL_TEXT_BLOCKS", "ULevelBase", "ULevel", "FStaticBrushIterator",
]