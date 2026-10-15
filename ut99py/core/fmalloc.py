"""Port of Core/Inc/FMallocWindows.h (Windows optimized memory allocator).

Classes:
- FMallocWindows : FMalloc
- FFreeMem : free memory block
- FPoolInfoBase : memory pool info
- FPoolTable : pool table
"""

from __future__ import annotations

from typing import Optional


class FFreeMem:
    """Information about a piece of free memory (FMallocWindows.h:38)."""

    def __init__(self) -> None:
        self.Next: Optional["FFreeMem"] = None
        self.Blocks: int = 0

    def GetPool(self) -> Optional["FPoolInfoBase"]:
        """Get the pool this free memory belongs to."""
        return None


class FPoolInfoBase:
    """Memory pool info, 32 bytes (FMallocWindows.h:26)."""

    def __init__(self) -> None:
        self.Bytes: int = 0
        self.OsBytes: int = 0
        self.Taken: int = 0
        self.Mem: Optional[bytes] = None
        self.Table: Optional["FPoolTable"] = None
        self.FirstMem: Optional[FFreeMem] = None
        self.PrevLink: Optional[list] = None


class FPoolTable:
    """Pool table (FMallocWindows.h:49)."""

    def __init__(self) -> None:
        self.FirstPool: Optional[FPoolInfoBase] = None
        self.ExaustedPool: Optional[FPoolInfoBase] = None
        self.BlockSize: int = 0


class FMallocWindows:
    """Optimized Windows virtual memory allocator (FMallocWindows.h:14)."""

    POOL_COUNT: int = 49
    POOL_MAX: int = 32768 + 1

    def __init__(self) -> None:
        self.PoolTable: list[FPoolTable] = [
            FPoolTable() for _ in range(self.POOL_COUNT)
        ]
        self.OsTable: FPoolTable = FPoolTable()
        self.PoolIndirect: list[Optional[FPoolInfoBase]] = [None] * 256
        self.MemSizeToPoolTable: list[Optional[FPoolTable]] = [None] * self.POOL_MAX
        self.MemInit: int = 0
        self.OsCurrent: int = 0
        self.OsPeak: int = 0
        self.UsedCurrent: int = 0
        self.UsedPeak: int = 0
        self.CurrentAllocs: int = 0
        self.TotalAllocs: int = 0
        self.MemTime: float = 0.0

    def OutOfMemory(self) -> None:
        """Handle out of memory condition."""
        raise RuntimeError("OutOfMemory")

    def CreateIndirect(self) -> FPoolInfoBase:
        """Create an indirect pool info entry."""
        raise NotImplementedError

    def Malloc(self, size: int, tag: str) -> bytes:
        """Allocate memory."""
        raise NotImplementedError

    def Realloc(self, ptr: bytes, new_size: int, tag: str) -> bytes:
        """Reallocate memory."""
        raise NotImplementedError

    def Free(self, ptr: bytes) -> None:
        """Free memory."""
        raise NotImplementedError

    def DumpAllocs(self) -> None:
        """Dump memory allocation statistics."""
        raise NotImplementedError

    def HeapCheck(self) -> None:
        """Check heap integrity."""
        raise NotImplementedError

    def Init(self) -> None:
        """Initialize the allocator."""
        raise NotImplementedError

    def Exit(self) -> None:
        """Exit the allocator."""
        pass
