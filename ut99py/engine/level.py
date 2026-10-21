"""Port of Engine/Inc/UnLevel.h (12 declared symbols).

Level management structures: ULevelBase, ULevel (extends ULevelBase),
FNetworkNotify, FCollisionHashBase interfaces, plus EAcceptConnection,
ETraceActorFlags, ELevelTick enums and FStaticBrushIterator.
Serialization implemented from UnLevel.cpp lines 67-100, 233-260.
"""
from typing import Optional, Any, List
from enum import IntFlag, IntEnum

from ..core import UObject, FName, FVector, FRotator, FArchive, FGuid


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
        raise NotImplementedError("C++ virtual in Engine.lib")

    def notify_accepted_connection(self, Connection: Any) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def notify_accepting_channel(self, Channel: Any) -> bool:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def notify_get_level(self) -> Optional['ULevelBase']:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def notify_received_text(self, Connection: Any, Text: str) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def notify_sending_file(self, Connection: Any, GUID: FGuid) -> bool:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def notify_received_file(self, Connection: Any, PackageIndex: int,
                             Error: str, Skipped: bool) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")

    def notify_progress(self, Str1: str, Str2: str, Seconds: float) -> None:
        raise NotImplementedError("C++ virtual in Engine.lib")


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
        """ULevelBase::Serialize (UnLevel.cpp:72-100).

        Args:
            ar: Archive (ULinkerLoad or FArchiveMemoryReader).
        Returns:
            self for chaining.
        """
        # Super::Serialize(Ar) — UObject base handled by archive itself.

        # Actors TArray<AActor*>
        if ar.is_trans():
            # IsTrans path: simple tarray serialize
            ar.serialize_tarray(self.Actors)
        else:
            # oldver path
            db_num = len(self.Actors)
            db_max = db_num
            ar.count_bytes(db_num * 4, db_num * 4)
            ar.serialize_int32(db_num)
            ar.serialize_int32(db_max)
            if ar.is_loading():
                self.Actors = []
            for _ in range(db_num):
                ar.serialize_object(None)  # UObject* ref via AR_INDEX -> linker

        # URL (FString/FURL)
        ar.serialize_object(self.URL)

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
        self.ReachSpecs: List[int] = []
        self.Model: Optional[Any] = None
        self.TextBlocks: List[int] = [0] * NUM_LEVEL_TEXT_BLOCKS
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
        """ULevel::Serialize (UnLevel.cpp:233-260).

        Args:
            ar: Archive (ULinkerLoad or FArchiveMemoryReader).

        Returns:
            self for chaining.
        """
        # Super::Serialize(Ar) — ULevelBase
        super().serialize(ar)

        # ApproxTime (TimeSeconds stored as FLOAT)
        approx_time = float(self.TimeSeconds)
        ar.serialize_float(approx_time)

        # Model (UModel*) — compact object index
        ar.serialize_object(self.Model)

        # ReachSpecs - TArray<INT>
        ar.serialize_tarray(self.ReachSpecs, element=int)

        # FirstDeleted (INT)
        ar.serialize_int32(0)

        # TextBlocks[NUM_LEVEL_TEXT_BLOCKS] (16 INT32s)
        for i in range(NUM_LEVEL_TEXT_BLOCKS):
            ar.serialize_int32(self.TextBlocks[i])

        # TravelInfo (version-dependent)
        if ar.licensee_ver() > 62:
            # TMap<FString,FString> — placeholder (not fully decoded yet)
            ar.serialize_tarray([])
        elif ar.licensee_ver() >= 61:
            # Old format: Names array + Items array
            ar.serialize_tarray([])
            ar.serialize_tarray([])

        # Preload Model if present and not trans
        if self.Model is not None and not ar.is_trans():
            pass  # Ar.Preload(Model) would happen here

        if self.BrushTracker:
            ar.count_bytes(0, 0)  # BrushTracker->CountBytes(Ar)

        return self

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