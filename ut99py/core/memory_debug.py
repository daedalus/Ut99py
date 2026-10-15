"""Port of Core/Inc/FMallocDebug.h (debug memory allocator).

Classes:
- FMallocDebug : FMalloc
- FMemDebugBase (struct) : debug memory entry

Enums:
- Memory tag constants: MEM_PreTag, MEM_PostTag, MEM_Tag, MEM_WipeTag
"""

from __future__ import annotations


class FMemDebugBase:
    """Debug memory entry (FMemDebugBase struct)."""

    def __init__(self) -> None:
        self.Tag: str = ""
        self.Size: int = 0
        self.RefCount: int = 0
        self.PreTag: int = 0


class FMallocDebug:
    """Debug memory allocator (FMallocDebug)."""

    MEM_PRE_TAG = 0xF0ED1CEE
    MEM_POST_TAG = 0xDEADF00F
    MEM_TAG = 0xFE
    MEM_WIPE_TAG = 0xCD

    def __init__(self) -> None:
        self.GFirstDebug: FMemDebugBase | None = None
        self.MemInited: bool = False

    def Malloc(self, size: int, tag: str) -> int:
        raise NotImplementedError

    def Free(self, ptr: int) -> None:
        raise NotImplementedError

    def Realloc(self, ptr: int, size: int, tag: str) -> int:
        raise NotImplementedError

    def GetPageSize(self) -> int:
        return 0

    def Init(self) -> None:
        pass

    def Exit(self) -> None:
        pass

    def OnOutOfMemory(self) -> None:
        raise MemoryError("OOM")
