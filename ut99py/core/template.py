"""Port of Core/Inc/UnTemplate.h template utilities.

Provides buffer serialization (FBufferReader, FBufferWriter, FBufferArchive),
lazy loading (FLazyLoader, TLazyArray), string output device, and FStringNoInit.
"""

from __future__ import annotations

from typing import Optional, TypeVar, Generic

from .types import FString
from .system import FArchive, ENAME_Log
from .objects import FOutputDevice, FName


T = TypeVar("T")


class FBufferWriter(FArchive):
    """Buffer writer that appends to a bytearray (UnTemplate.h:1484-1518).

    C++ wraps a TArray<BYTE>&; Python extends the bytearray to the write
    end, same net effect. The C++ body is inline in the header.
    """

    def __init__(self, bytes_array: bytearray) -> None:
        super().__init__()
        self._saving = True
        self._bytes = bytes_array
        self._pos = 0

    def write(self, data: bytes) -> int:
        end = self._pos + len(data)
        if end > len(self._bytes):
            self._bytes.extend(b"\x00" * (end - len(self._bytes)))
        self._bytes[self._pos : end] = data
        self._pos = end
        return len(data)

    def tell(self) -> int:
        return self._pos

    def seek(self, pos: int) -> None:
        self._pos = pos


class FBufferReader(FArchive):
    """Buffer reader that reads from bytes/bytearray (UnTemplate.h)."""

    def __init__(self, data: bytes | bytearray) -> None:
        super().__init__()
        self._loading = True
        self._bytes = bytes(data)
        self._size = len(self._bytes)
        self._pos = 0
        self._archive_size = self._size

    def read(self, length: int) -> bytes:
        if self._pos + length > self._size:
            self._pos = self._size
            return b""
        data = self._bytes[self._pos : self._pos + length]
        self._pos += length
        return data

    def seek(self, pos: int) -> None:
        if pos < 0 or pos > self._size:
            raise ValueError("FBufferReader: seek out of bounds")
        self._pos = pos

    def tell(self) -> int:
        return self._pos

    def at_end(self) -> bool:
        return self._pos >= self._size

    def total_size(self) -> int:
        return self._size

    def count_bytes(self, used: int, allocated: int) -> None:
        """Base no-op; FBufferReader does not track allocated capacity."""
        return


class FBufferArchive(FBufferWriter):
    """Buffer archive that owns its byte buffer (UnTemplate.h:1523-1529)."""

    def __init__(self) -> None:
        super().__init__(bytearray())


class FLazyLoader:
    """Base class for lazy-loaded objects (UnTemplate.h:1025-1038)."""

    def __init__(self) -> None:
        self._saved_ar: Optional[FArchive] = None
        self._saved_pos: int = 0

    def load(self) -> None:
        raise NotImplementedError("FLazyLoader.load: override in subclass")

    def unload(self) -> None:
        raise NotImplementedError("FLazyLoader.unload: override in subclass")


class TLazyArray(list, FLazyLoader, Generic[T]):
    """Lazy-loadable dynamic array (UnTemplate.h:1043-1150).

    Inherits from list for simplicity; FLazyLoader mixin provides load/unload.
    """

    def __init__(self, in_num: int = 0) -> None:
        list.__init__(self)
        self._saved_ar: Optional[FArchive] = None
        self._saved_pos: int = 0

    def load(self) -> None:
        if self._saved_ar is not None and self._saved_pos > 0:
            pushed_pos = self._saved_ar.tell()
            self._saved_ar.seek(self._saved_pos)
            self._saved_ar.seek(pushed_pos)

    def unload(self) -> None:
        if self._saved_pos < 0:
            self.clear()
            self._saved_pos *= -1


class FStringOutputDevice(FOutputDevice):
    """String output device (UnTemplate.h:1469-1479).

    Accumulates output into an FString.
    """

    def __init__(self, in_str: str = "") -> None:
        super().__init__()
        self._string = FString(in_str)

    def serialize(self, v: str, event: FName = ENAME_Log) -> None:
        self._string += v

    def __str__(self) -> str:
        return str(self._string)


class FStringNoInit(FString):
    """FString variant that skips zero initialization (UnTemplate.h:1413-1440)."""

    pass
