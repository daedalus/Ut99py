"""Port of Core/Inc/FFileManagerPSX2.h (PSX2-based file manager).

Classes:
- FArchiveFileReader : FArchive
- FArchiveFileWriter : FArchive
- FFileManagerPSX2 : FArchive
"""

from __future__ import annotations

from typing import Optional


class FArchiveFileReader:
    """File reader archive (FArchiveFileReader)."""

    def __init__(
        self,
        file: int,
        error: Optional[object] = None,
        size: int = 0,
    ) -> None:
        self.File = file
        self.Error = error
        self.Size = size
        self.Pos = 0
        self.BufferBase = 0
        self.BufferCount = 0


class FArchiveFileWriter:
    """File writer archive (FArchiveFileWriter)."""

    def __init__(
        self,
        file: int,
        error: Optional[object] = None,
        size: int = 0,
    ) -> None:
        self.File = file
        self.Error = error
        self.Size = size
        self.Pos = 0
        self.BufferBase = 0
        self.BufferCount = 0


class FFileManagerPSX2:
    """PSX2 file manager (FFileManagerPSX2)."""

    def __init__(self) -> None:
        self.Reader: Optional[FArchiveFileReader] = None
        self.Writer: Optional[FArchiveFileWriter] = None
