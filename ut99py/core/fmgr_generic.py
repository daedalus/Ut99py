"""Port of Core/Inc/FFileManagerGeneric.h (generic file manager support).

Classes:
- FFileManagerGeneric : FFileManager
"""

from __future__ import annotations

from typing import Callable, Optional


class FFileManagerGeneric:
    """Generic file manager support (FFileManagerGeneric).

    Provides simple, unoptimized implementations of functions whose
    implementations can be derived from other functions.
    """

    def __init__(self) -> None:
        pass

    def FileSize(self, filename: str) -> int:
        """Get file size via CreateFileReader. Returns -1 on failure."""
        raise NotImplementedError

    def Copy(
        self,
        dest_file: str,
        src_file: str,
        replace_existing: bool = False,
        even_if_read_only: bool = False,
        attributes: bool = False,
        progress: Optional[Callable[[float], None]] = None,
    ) -> bool:
        raise NotImplementedError

    def Delete(
        self, filename: str, require_exists: bool = False, even_read_only: bool = False
    ) -> bool:
        raise NotImplementedError

    def Move(self, dest: str, src: str, replace_existing: bool = False) -> bool:
        raise NotImplementedError

    def MakeDirectory(self, path: str, tree: bool = False) -> bool:
        raise NotImplementedError

    def DeleteDirectory(
        self, path: str, require_exists: bool = False, tree: bool = False
    ) -> bool:
        raise NotImplementedError

    def FindFiles(
        self, filename: str, files: bool = True, directories: bool = False
    ) -> list[str]:
        raise NotImplementedError

    def SetDefaultDirectory(self, filename: str) -> bool:
        raise NotImplementedError

    def GetDefaultDirectory(self) -> str:
        raise NotImplementedError

    def GetGlobalTime(self, filename: str) -> int:
        raise NotImplementedError

    def SetGlobalTime(self, filename: str) -> bool:
        raise NotImplementedError
