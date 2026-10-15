"""Cache item and memory cache (UnCache.h).

Ported from Core/Inc/UnCache.h.
"""

from __future__ import annotations
from typing import Optional

from .types import QWORD, BYTE, INT, WORD, DWORD, UBOOL


class FCacheItem:
    """Cache item (32 bytes) inside FMemCache (UnCache.h:21-76)."""

    COST_INFINITE = 0x1000000
    TCacheTime = WORD

    def __init__(self) -> None:
        self.Id: QWORD = 0
        self.Data: Optional[bytes] = None
        self.Time: self.TCacheTime = 0
        self.Segment: BYTE = 0
        self.Extra: BYTE = 0
        self.Cost: INT = 0
        self.LinearNext: Optional[FCacheItem] = None
        self.LinearPrev: Optional[FCacheItem] = None
        self.HashNext: Optional[FCacheItem] = None

    def Unlock(self) -> None:
        self.Cost -= self.COST_INFINITE

    def GetId(self) -> QWORD:
        return self.Id

    def GetData(self) -> Optional[bytes]:
        return self.Data

    def GetSize(self) -> INT:
        if self.Data is None or self.LinearNext is None or self.LinearNext.Data is None:
            return 0
        return len(self.LinearNext.Data) - len(self.Data)

    def GetExtra(self) -> BYTE:
        return self.Extra

    def SetExtra(self, b: BYTE) -> None:
        self.Extra = b

    def GetCost(self) -> INT:
        return self.Cost

    def GetTime(self) -> int:
        return self.Time


class FMemCache:
    """Memory cache (UnCache.h:16-187)."""

    HASH_COUNT = 16384
    IGNORE_SIZE = 256
    COST_INFINITE = 0x1000000

    def __init__(self) -> None:
        self.Initialized: UBOOL = False
        self.Time: INT = 0
        self.MruId: QWORD = 0
        self.MruItem: Optional[FCacheItem] = None
        self.ItemMemory: Optional[FCacheItem] = None
        self.CacheItems: Optional[FCacheItem] = None
        self.LastItem: Optional[FCacheItem] = None
        self.UnusedItems: Optional[FCacheItem] = None
        self.HashItems: list = [None] * self.HASH_COUNT
        self.CacheMemory: Optional[bytes] = None
        # Stats.
        self.NumGets: INT = 0
        self.NumCreates: INT = 0
        self.CreateCycles: INT = 0
        self.GetCycles: INT = 0
        self.TickCycles: INT = 0
        self.ItemsFresh: INT = 0
        self.ItemsStale: INT = 0
        self.ItemsTotal: INT = 0
        self.ItemGaps: INT = 0
        self.MemFresh: INT = 0
        self.MemStale: INT = 0
        self.MemTotal: INT = 0

    def Init(self, BytesToAllocate: INT, MaxItems: INT, Start: Optional[bytes] = None, SegSize: int = 0) -> None:
        self.Initialized = True
        self.Time = 0

    def Exit(self, FreeMemory: int) -> None:
        self.Initialized = False

    def Flush(self, Id: QWORD = 0, Mask: DWORD = ~0, IgnoreLocked: UBOOL = False) -> None:
        pass

    def Create(self, Id: QWORD, Item: list, CreateSize: INT, Alignment: int = 4, SafetyPad: int = 0) -> Optional[bytes]:
        return None

    def Tick(self) -> None:
        self.Time += 1

    def CheckState(self) -> None:
        pass

    def Exec(self, Cmd: str, Ar=None) -> bool:
        return False

    def Status(self, Msg: str) -> None:
        pass

    def GetTime(self) -> int:
        return self.Time

    def First(self) -> Optional[FCacheItem]:
        return self.CacheItems

    def Last(self) -> Optional[FCacheItem]:
        return self.LastItem

    def Next(self, Item: FCacheItem) -> Optional[FCacheItem]:
        return Item.LinearNext

    def GHash(self, Val: QWORD) -> int:
        D = int(Val) & 0xFFFFFFFF
        return (D ^ (D >> 12) ^ (D >> 24)) & (self.HASH_COUNT - 1)

    def Get(self, Id: QWORD, Item: list, Alignment: int = 4) -> Optional[bytes]:
        if Id == self.MruId:
            if self.MruItem is not None:
                Item[0] = self.MruItem
                self.MruItem.Cost += self.COST_INFINITE
                return self.MruItem.Data
        hash_idx = self.GHash(Id)
        hash_item = self.HashItems[hash_idx]
        while hash_item is not None:
            if hash_item.Id == Id:
                self.MruId = Id
                self.MruItem = hash_item
                Item[0] = hash_item
                hash_item.Time = self.Time
                hash_item.Cost += self.COST_INFINITE
                return hash_item.Data
            hash_item = hash_item.HashNext
        return None
