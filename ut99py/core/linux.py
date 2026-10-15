"""Port of Core/Inc/FFileManagerLinux.h (Linux-based file manager).

Classes:
- FArchiveFileReader : FArchive
- FArchiveFileWriter : FArchive
- FFileManagerLinux : FArchive

Structs:
- dirent : directory entry struct
"""

from __future__ import annotations

from typing import Optional

from .system import FArchive, FOutputDeviceNull


class dirent:
    """Directory entry (struct dirent from <dirent.h>)."""

    def __init__(self) -> None:
        self.d_name: str = ""
        self.d_ino: int = 0
        self.d_reclen: int = 0
        self.d_type: int = 0


class FArchiveFileReader(FArchive):
    """File reader archive (FArchiveFileReader)."""

    def __init__(
        self, size: int = 0, error: Optional[FOutputDeviceNull] = None
    ) -> None:
        super().__init__()
        self._file: Optional[object] = None
        self._error: Optional[FOutputDeviceNull] = error
        self.Size: int = size
        self.Pos: int = 0
        self.BufferBase: int = 0
        self.BufferCount: int = 0
        self.Buffer: bytearray = bytearray(1024)

    def Precache(self, hint_count: int) -> None:
        """Precache data from the file."""
        raise NotImplementedError

    def Seek(self, in_pos: int) -> None:
        """Seek to a position in the file."""
        raise NotImplementedError

    def Serialize(self, data: Optional[bytes] = None) -> bytes:
        """Serialize data from the file."""
        raise NotImplementedError


class FArchiveFileWriter(FArchive):
    """File writer archive (FArchiveFileWriter)."""

    def __init__(self) -> None:
        super().__init__()
        self._file: Optional[object] = None
        self._error: Optional[FOutputDeviceNull] = None
        self.Size: int = 0
        self.Pos: int = 0
        self.BufferBase: int = 0
        self.BufferCount: int = 0
        self.Buffer: bytearray = bytearray(1024)

    def Precache(self, hint_count: int) -> None:
        """Precache data from the file."""
        raise NotImplementedError

    def Seek(self, in_pos: int) -> None:
        """Seek to a position in the file."""
        raise NotImplementedError

    def Serialize(self, data: Optional[bytes] = None) -> bytes:
        """Serialize data to the file."""
        raise NotImplementedError


class FFileManagerLinux:
    """Linux file manager (FFileManagerLinux)."""

    def __init__(self) -> None:
        self._reader: Optional[FArchiveFileReader] = None
        self._writer: Optional[FArchiveFileWriter] = None

    def Load(self, path: str) -> FArchiveFileReader:
        """Load a file from the filesystem."""
        raise NotImplementedError

    def Save(self, path: str) -> FArchiveFileWriter:
        """Save a file to the filesystem."""
        raise NotImplementedError

    def Find(self, path: str) -> list[dirent]:
        """Find files in a directory."""
        raise NotImplementedError
