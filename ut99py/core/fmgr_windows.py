"""Port of Core/Inc/FFileManagerWindows.h (Windows-based file manager).

Classes:
- FArchiveFileReader : FArchive
- FArchiveFileWriter : FArchive
- FFileManagerWindows : FArchive
"""

from __future__ import annotations

from typing import Optional


class FArchiveFileReader:
    """Windows file reader archive (FArchiveFileReader)."""

    def __init__(
        self,
        handle: object,
        error: Optional[object] = None,
        size: int = 0,
    ) -> None:
        self.Handle = handle
        self.Error = error
        self.Size = size
        self.Pos = 0
        self.BufferBase = 0
        self.BufferCount = 0

    def Precache(self, hint_count: int) -> None:
        pass

    def Seek(self, in_pos: int) -> None:
        self.Pos = in_pos

    def Serialize(self, data: Optional[bytes] = None) -> bytes:
        return b""


class FArchiveFileWriter:
    """Windows file writer archive (FArchiveFileWriter)."""

    def __init__(
        self,
        handle: object,
        error: Optional[object] = None,
    ) -> None:
        self.Handle = handle
        self.Error = error
        self.Size = 0
        self.Pos = 0
        self.BufferBase = 0
        self.BufferCount = 0

    def Precache(self, hint_count: int) -> None:
        pass

    def Seek(self, in_pos: int) -> None:
        self.Pos = in_pos

    def Serialize(self, data: Optional[bytes] = None) -> bytes:
        return b""


class FFileManagerWindows:
    """Windows file manager (FFileManagerWindows)."""

    def __init__(self) -> None:
        self.Reader: Optional[FArchiveFileReader] = None
        self.Writer: Optional[FArchiveFileWriter] = None
