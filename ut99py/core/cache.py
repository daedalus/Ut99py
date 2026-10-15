"""Port of Core/Inc/UnCache.h (Unreal fast memory cache support).

Classes:
- FCacheItem : cache item (32 bytes)
- FMemCache : memory cache
"""

from __future__ import annotations

from typing import Optional


class FCacheItem:
    """Information about a cache item (32 bytes)."""

    COST_INFINITE = 0x1000000

    def __init__(self) -> None:
        self.Id: int = 0
        self.Data: Optional[bytes] = None
        self.Time: int = 0
        self.Segment: int = 0
        self.Extra: int = 0
        self.Cost: int = 0
        self.LinearNext: Optional["FCacheItem"] = None
        self.LinearPrev: Optional["FCacheItem"] = None
        self.HashNext: Optional["FCacheItem"] = None

    def Unlock(self) -> None:
        self.Cost -= self.COST_INFINITE

    def GetId(self) -> int:
        return self.Id

    def GetData(self) -> Optional[bytes]:
        return self.Data

    def GetSize(self) -> int:
        if self.LinearNext is not None and self.Data is not None:
            return len(self.LinearNext.Data or b"") - len(self.Data)
        return 0

    def GetExtra(self) -> int:
        return self.Extra

    def SetExtra(self, b: int) -> None:
        self.Extra = b

    def GetCost(self) -> int:
        return self.Cost

    def GetTime(self) -> int:
        return self.Time


class FMemCache:
    """Memory cache (FMemCache)."""

    HASH_COUNT = 16384
    IGNORE_SIZE = 256

    def __init__(self) -> None:
        self.Initialized: bool = False
        self.Time: int = 0
        self.MruId: int = 0
        self.MruItem: Optional[FCacheItem] = None
        self.ItemMemory: Optional[FCacheItem] = None
        self.CacheItems: list[FCacheItem] = []
        self.LastItem: Optional[FCacheItem] = None
        self.UnusedItems: Optional[FCacheItem] = None
        self.HashItems: list[Optional[FCacheItem]] = [None] * self.HASH_COUNT
        self.CacheMemory: Optional[bytes] = None
        self.NumGets: int = 0
        self.NumCreates: int = 0
        self.ItemsFresh: int = 0
        self.ItemsStale: int = 0
        self.ItemsTotal: int = 0
        self.MemFresh: int = 0
        self.MemStale: int = 0
        self.MemTotal: int = 0

    def Init(
        self,
        bytes_to_allocate: int,
        max_items: int,
        start: Optional[bytes] = None,
        seg_size: int = 0,
    ) -> None:
        raise NotImplementedError

    def Exit(self, free_memory: int) -> None:
        pass

    def Flush(self, id: int = 0, mask: int = ~0, ignore_locked: bool = False) -> None:
        pass

    def Create(
        self,
        id: int,
        item: FCacheItem,
        create_size: int,
        alignment: int = 0,
        safety_pad: int = 0,
    ) -> Optional[bytes]:
        raise NotImplementedError

    def Tick(self) -> None:
        pass

    def CheckState(self) -> None:
        pass

    def Status(self, msg: str) -> None:
        pass

    def GetTime(self) -> int:
        return self.Time

    def First(self) -> Optional[FCacheItem]:
        return self.CacheItems[0] if self.CacheItems else None

    def Last(self) -> Optional[FCacheItem]:
        return self.LastItem

    def Next(self, item: FCacheItem) -> Optional[FCacheItem]:
        return item.LinearNext

    def GHash(self, val: int) -> int:
        d = val & 0xFFFFFFFF
        return (d ^ (d >> 12) ^ (d >> 24)) & (self.HASH_COUNT - 1)

    def Get(self, id: int, alignment: int = 0) -> Optional[FCacheItem]:
        """Look up a cache item by id. Returns the FCacheItem or None.

        C++ signature is BYTE* Get( QWORD Id, FCacheItem*& Item, INT Alignment )
        where Item is an output parameter; in Python we return the item.
        """
        if id == self.MruId and self.MruItem is not None:
            self.MruItem.Cost += FCacheItem.COST_INFINITE
            return self.MruItem
        hash_item = self.HashItems[self.GHash(id)]
        while hash_item is not None:
            if hash_item.Id == id:
                self.MruId = id
                self.MruItem = hash_item
                hash_item.Time = self.Time
                hash_item.Cost += FCacheItem.COST_INFINITE
                return hash_item
            hash_item = hash_item.HashNext
        return None
