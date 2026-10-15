"""Port of Core/Inc/FFileManagerAnsi.h (ANSI-based file manager).

Classes:
- FArchiveFileReader : FArchive
- FArchiveFileWriter : FArchive
- FFileManagerAnsi : FArchive
"""

from __future__ import annotations

from typing import Optional


class FArchiveFileReader:
    def __init__(
        self,
        file: object,
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
    def __init__(
        self,
        file: object,
        error: Optional[object] = None,
        size: int = 0,
    ) -> None:
        self.File = file
        self.Error = error
        self.Size = size
        self.Pos = 0
        self.BufferBase = 0
        self.BufferCount = 0


class FFileManagerAnsi:
    def __init__(self) -> None:
        self.Reader: Optional[FArchiveFileReader] = None
        self.Writer: Optional[FArchiveFileWriter] = None
