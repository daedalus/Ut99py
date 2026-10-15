"""Port of Core/Inc/FFileManagerArc.h (archive-based file manager).

Classes:
- FFileManagerArc : FArchive
- FFileReaderArc : FArchive
- FArchiveHeader : archive header structure
- FArchiveItem : individual file entry in archive

Enums:
- EArchiveFlags : archive operation flags (bootstrap, compressed, etc.)
"""

from __future__ import annotations

from typing import Optional




class FArchiveItem:
    """A single file entry within an archive."""

    def __init__(
        self, filename: str = "", offset: int = 0, size: int = 0, flags: int = 0
    ) -> None:
        self._Filename_ = filename
        self.Offset = offset
        self.Size = size
        self.Flags = flags

    def __str__(self) -> str:
        return f"{self._Filename_}:{self.Offset}-{self.Size}"


class FArchiveHeader:
    """Archive header containing metadata for the archive."""

    def __init__(
        self,
        magic: int = 0x9FE3C5A3,
        table_offset: int = -1,
        file_size: int = 0,
        ver: int = 1,
        crc: int = 0,
    ) -> None:
        self.Magic = magic
        self.TableOffset = table_offset
        self.FileSize = file_size
        self.Ver = ver
        self.CRC = crc

    def __str__(self) -> str:
        return f"FArchiveHeader(magic={self.Magic:#x}, table_offset={self.TableOffset}, file_size={self.FileSize}, ver={self.Ver}, crc={self.CRC})"


class FFileManagerArc:
    """Archive-based file manager (FFileManagerArc)."""

    def __init__(self) -> None:
        self._header: Optional[FArchiveHeader] = None
        self._items: list[FArchiveItem] = []

    def Load(self, path: str) -> FArchiveItem:
        """Load an item from the archive at the given path."""
        raise NotImplementedError

    def Save(self, path: str, item: FArchiveItem) -> None:
        """Save an item to the archive at the given path."""
        raise NotImplementedError

    def ReadItem(self, path: str) -> FArchiveItem:
        """Read an item from the archive at the given path."""
        raise NotImplementedError

    def WriteItem(self, path: str, item: FArchiveItem) -> None:
        """Write an item to the archive at the given path."""
        raise NotImplementedError
