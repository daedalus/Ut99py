"""Port of Core/Inc/FFileManagerPSX2CD.h (PSX2 CD-based file manager).

Classes:
- FArchiveFileReader : FArchive (CD reader with sector caching)
- FArchiveFileWriter : FArchive
- FFileManagerPSX2CD : FFileManagerGeneric
"""

from __future__ import annotations

from typing import Optional


class FArchiveFileReader:
    """CD file reader with sector caching (FArchiveFileReader)."""

    SECTOR_SIZE = 2048
    DEFAULT_CACHE_SIZE = 32768 * 8
    DEFAULT_MAX_CACHE_ENTRIES = 24

    def __init__(
        self,
        filename: str,
        file: object,
        error: Optional[object] = None,
    ) -> None:
        self.File = file
        self.Filename = filename
        self.Error = error
        self.Pos = 0
        self.Offset = 0
        self.Sector = 0
        self.BufferBase = 0
        self.BufferCount = 0
        self.BufferOffset = 0
        self.Buffer = bytearray(67584)
        self.ReadCache: dict[int, bytearray] = {}
        self.CacheTimestamp: dict[int, float] = {}
        self.MaxCacheEntries = self.DEFAULT_MAX_CACHE_ENTRIES
        self.CacheSize = self.DEFAULT_CACHE_SIZE
        self.CacheKey = 0
        self.ReadBytes = 0

    def Precache(self, hint_count: int) -> None:
        pass

    def Seek(self, in_pos: int) -> None:
        self.Pos = in_pos
        self.Sector = in_pos // self.SECTOR_SIZE
        self.Offset = in_pos - (self.Sector * self.SECTOR_SIZE)

    def Tell(self) -> int:
        return self.Pos

    def TotalSize(self) -> int:
        return getattr(self.File, "size", 0)

    def Close(self) -> bool:
        for mem in self.ReadCache.values():
            pass
        self.ReadCache.clear()
        self.CacheTimestamp.clear()
        self.File = None
        return True

    def Serialize(self, data: bytes, length: int) -> None:
        pass


class FArchiveFileWriter:
    """File writer archive (FArchiveFileWriter)."""

    def __init__(
        self,
        file: int,
        error: Optional[object] = None,
    ) -> None:
        self.File = file
        self.Error = error
        self.Pos = 0
        self.BufferCount = 0
        self.Buffer = bytearray(4096)

    def Seek(self, in_pos: int) -> None:
        self.Pos = in_pos

    def Tell(self) -> int:
        return self.Pos

    def Close(self) -> bool:
        return True

    def Serialize(self, data: bytes, length: int) -> None:
        self.Pos += length

    def Flush(self) -> None:
        pass


class FFileManagerPSX2CD:
    """PSX2 CD file manager (FFileManagerPSX2CD)."""

    def __init__(self) -> None:
        pass

    def CreateFileReader(
        self, filename: str, flags: int, error: Optional[object] = None
    ) -> Optional[FArchiveFileReader]:
        return None

    def CreateFileWriter(
        self, filename: str, flags: int, error: Optional[object] = None
    ) -> Optional[FArchiveFileWriter]:
        return None
