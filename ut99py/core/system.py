"""Core system: FArchive, serialization, config"""

from typing import TYPE_CHECKING, Iterator, Optional, Any
import io
import re
import struct
import sys

from .types import (
    FName,
    FString,
    TArray,
    FGuid,
    FCompactIndex,
    INDEX_NONE,
    ENAME_Log,
    ENAME_Exit,
    ENAME_Warning,
    ENAME_Error,
    ENAME_Title,
    ENAME_Heading,
    ENAME_SubHeading,
    ENAME_ExecWarning,
    ENAME_ScriptWarning,
    ENAME_Progress,
)
from .file_utils import appToUpper
from .objver import (
    ENGINE_NEGOTIATION_VERSION,
    PACKAGE_FILE_VERSION,
    PACKAGE_FILE_VERSION_LICENSEE,
)
from .objects import (
    UObject,
    UClass,
    UPackage,
    ULinkerLoad,
    FOutputDevice,
    FContextSupplier,
    FFeedbackContext,
)

if TYPE_CHECKING:
    from .types import FVector, FRotator


def AR_INDEX(ar: 'FArchive', value: int) -> int:
    """C++ AR_INDEX(x) (UnArc.h:234): serialize x as an FCompactIndex."""
    return ar.serialize_compact_index(FCompactIndex(value)).value


class FArchive:
    """Byte-order-neutral serializer. Ported from Core/Inc/UnArc.h.

    C++ has a single `operator<<` whose direction comes from the concrete
    archive (ArIsLoading / ArIsSaving). Python has no reference arguments, so
    `Ar << X` and `Ar >> X` both call `_serialize`: the operand's runtime type
    selects the serializer, which returns the loaded value and writes into
    mutable operands in place. Load paths use `>>`, save paths `<<`.
    """

    def __init__(self):
        self._pos: int = 0
        self._size: int = 0
        self._error: bool = False
        self._archive_size: int = 0
        self._linker: Optional[ULinkerLoad] = None
        # Status variables (UnArc.h:194-205), defaults from its constructor.
        self._ver: int = PACKAGE_FILE_VERSION
        self._net_ver: int = ENGINE_NEGOTIATION_VERSION
        self._licensee_ver: int = PACKAGE_FILE_VERSION_LICENSEE
        self._loading: bool = False
        self._saving: bool = False
        self._trans: bool = False
        self._persistent: bool = False
        self._for_edit: bool = True
        self._for_client: bool = True
        self._for_server: bool = True

    # Status accessors (UnArc.h:126-139).

    def ver(self) -> int:
        return self._ver

    def net_ver(self) -> int:
        return self._net_ver & 0x7fffffff

    def licensee_ver(self) -> int:
        return self._licensee_ver

    def is_loading(self) -> bool:
        return self._loading

    def is_saving(self) -> bool:
        return self._saving

    def is_trans(self) -> bool:
        return self._trans

    def is_net(self) -> bool:
        return (self._net_ver & 0x80000000) != 0

    def is_persistent(self) -> bool:
        return self._persistent

    def is_error(self) -> bool:
        return self._error

    def for_edit(self) -> bool:
        return self._for_edit

    def for_client(self) -> bool:
        return self._for_client

    def for_server(self) -> bool:
        return self._for_server

    def pos(self) -> int:
        return self._pos

    def total_size(self) -> int:
        return self._archive_size

    def size(self) -> int:
        return self._size

    def tell(self) -> int:
        return self._pos

    def seek(self, pos: int) -> None:
        self._pos = pos

    def at_end(self) -> bool:
        return self._pos >= self._size

    def read(self, length: int) -> bytes:
        return b''

    def write(self, data: bytes) -> int:
        return 0

    def close(self) -> None:
        pass

    # Serialize operators (UnArc.h:39-192).

    def __lshift__(self, value: Any) -> Any:
        """C++ `Ar << X`."""
        return self._serialize(value)

    def __rshift__(self, value: Any) -> Any:
        """Read form of `Ar << X`; see the class docstring."""
        return self._serialize(value)

    def _check_direction(self) -> None:
        if not (self._loading or self._saving):
            raise NotImplementedError(
                f"{type(self).__name__} has no direction; set _loading or _saving "
                "as FArchiveFileReader/FArchiveFileWriter do (UnArc.h:115-116)")

    def _serialize(self, value: Any) -> Any:
        """Dispatch `Ar << X` on the operand type."""
        self._check_direction()
        if isinstance(value, bool):
            return self.serialize_byte(1 if value else 0) != 0
        if isinstance(value, int):
            return self.serialize_int32(value)
        if isinstance(value, float):
            return self.serialize_float(value)
        if isinstance(value, str):
            return self.serialize_str(value)
        if isinstance(value, FName):
            return self.serialize_name(value)
        if isinstance(value, FGuid):
            return self.serialize_guid(value)
        if isinstance(value, FCompactIndex):
            return self.serialize_compact_index(value)
        if hasattr(value, 'serialize'):
            value.serialize(self)
            return value
        raise NotImplementedError(
            f"FArchive has no serializer for {type(value).__name__}; add the "
            "operator<< from whichever C++ header declares it")

    def serialize_byte(self, value: int) -> int:
        """ANSICHAR / BYTE / SBYTE (UnArc.h:142-156): one byte."""
        if self._loading:
            return self._read_byte()
        self.write(struct.pack('<B', value & 0xFF))
        return value

    def serialize_word(self, value: int) -> int:
        """_WORD / SWORD (UnArc.h:157-166): two bytes."""
        if self._loading:
            return self._read_uint16()
        self.write(struct.pack('<H', value & 0xFFFF))
        return value

    def serialize_dword(self, value: int) -> int:
        """DWORD (UnArc.h:167-171): four bytes."""
        if self._loading:
            return self._read_uint32()
        self.write(struct.pack('<I', value & 0xFFFFFFFF))
        return value

    def serialize_int32(self, value: int) -> int:
        """INT (UnArc.h:172-176): signed four bytes."""
        if self._loading:
            return self._read_int32()
        self.write(struct.pack('<i', value))
        return value

    def serialize_float(self, value: float) -> float:
        """FLOAT (UnArc.h:177-181): four bytes."""
        if self._loading:
            return self._read_float()
        self.write(struct.pack('<f', value))
        return value

    def serialize_qword(self, value: int) -> int:
        """QWORD (UnArc.h:182-186): eight bytes, unsigned."""
        if self._loading:
            return self._read_uint64()
        self.write(struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))
        return value

    def serialize_sqword(self, value: int) -> int:
        """SQWORD (UnArc.h:187-191): eight bytes, signed."""
        if self._loading:
            return self._read_int64()
        self.write(struct.pack('<q', value))
        return value

    def serialize_guid(self, guid: FGuid) -> FGuid:
        """FGuid (UnObjBas.h:190): four consecutive ints."""
        guid.a = self.serialize_dword(guid.a)
        guid.b = self.serialize_dword(guid.b)
        guid.c = self.serialize_dword(guid.c)
        guid.d = self.serialize_dword(guid.d)
        return guid

    def serialize_compact_index(self, value: FCompactIndex) -> FCompactIndex:
        """FCompactIndex (UnArc.h:216-221)."""
        if self._loading:
            raw = bytearray([self._read_byte()])
            if raw[0] & 0x40:
                byte = self._read_byte()
                raw.append(byte)
                if byte & 0x80:
                    byte = self._read_byte()
                    raw.append(byte)
                    if byte & 0x80:
                        byte = self._read_byte()
                        raw.append(byte)
                        if byte & 0x80:
                            raw.append(self._read_byte())
            value.value = FCompactIndex.decode(bytes(raw))[0].value
            return value
        self.write(value.encode())
        return value

    def serialize_name(self, name: FName) -> FName:
        """Virtual `operator<<(FName&)` (UnArc.h:39). The C++ base is a no-op
        and ULinkerLoad/ULinkerSave override it; Python raises instead so a
        missing override can't silently desynchronise the stream."""
        raise NotImplementedError("override serialize_name for this archive")

    def serialize_object(self, obj: Any) -> Any:
        """Virtual `operator<<(UObject*&)` (UnArc.h:43). See serialize_name."""
        raise NotImplementedError("override serialize_object for this archive")

    def serialize_str(self, s: FString) -> FString:
        """operator<<(FArchive&, FString&) (UnTemplate.h:1403).

        The C++ body is CORE_API (in the prebuilt Core.lib); the on-disk layout
        follows Help/PACKAGES.md:656 -- characters, one byte each, terminated by
        a zero byte -- which is also what engine/ut_reader.py's _read_string
        decodes. C++ returns the FArchive, but Python strings are immutable, so
        the loaded value is returned the way the other primitives are.
        """
        if self._loading:
            return FString(self._read_null_terminated_string())
        self.write(s.encode('latin-1', errors='replace') + b'\x00')
        return s

    def serialize_int(self, value: int, max_bits: int = 0) -> int:
        """C++ SerializeInt(Value, Max). The base FArchive writes a full DWORD
        whatever Max says (UnArc.h:31); FBitWriter overrides this in UnBits.h."""
        return self.serialize_dword(value)

    def count_bytes(self, used: int, allocated: int) -> None:
        """C++ `virtual CountBytes( SIZE_T InNum, SIZE_T InMax )` (UnArc.h:37).
        Only the memory archive overrides it; file archives ignore it."""
        return

    def serialize_tarray(self, array: TArray, element: Optional[type] = None,
                         element_size: Optional[int] = None) -> TArray:
        """operator<<(FArchive&, TArray&) (UnTemplate.h:435), plus the
        TArray<BYTE> specialization (UnTemplate.h:686).

        Python has no `sizeof(T)`, so `element_size` stands in for it: 1 selects
        the byte specialization that skips construction and moves the buffer
        raw. `element` is the C++ `new(A) T` factory; loading a non-empty array
        needs it because the stream stores only the count.
        """
        count = AR_INDEX(self, len(array))
        size = element_size or 0
        self.count_bytes(count * size, len(array) * size)

        if element_size == 1:
            if self._loading:
                array[:] = self.read(count)
            else:
                self.write(bytes(array))
            return array

        if self._loading:
            del array[:]
            if element is None:
                raise NotImplementedError(
                    "serialize_tarray needs `element` to load elements: the "
                    "stream stores the count only (UnTemplate.h:455)")
            append = array.append
            for _ in range(count):
                append(self._serialize(element()))
        else:
            for item in array:
                self._serialize(item)
        return array

    def serialize_bytes(self, data: bytes) -> bytes:
        """C++ Serialize(V, Length) for a raw buffer. When loading, `data`
        carries the length and the loaded bytes are returned."""
        if self._loading:
            return self.read(len(data))
        self.write(data)
        return b''

    def serialize_bits(self, value: bytes, length_bits: int) -> bytes:
        """C++ SerializeBits(V, LengthBits) (UnArc.h:25-30)."""
        if length_bits <= 0:
            return b''
        count = (length_bits + 7) // 8
        if self._loading:
            data = bytearray(self.read(count))
            remainder = length_bits & 7
            if remainder and len(data) > length_bits // 8:
                data[length_bits // 8] &= (1 << remainder) - 1
            return bytes(data)
        self.write(bytes(value[:count]))
        return bytes(value[:count])
    
    def _read_byte(self) -> int:
        data = self.read(1)
        return struct.unpack('<B', data)[0] if len(data) == 1 else 0
    
    def _read_int32(self) -> int:
        data = self.read(4)
        return struct.unpack('<i', data)[0] if len(data) == 4 else 0
    
    def _read_uint32(self) -> int:
        data = self.read(4)
        return struct.unpack('<I', data)[0] if len(data) == 4 else 0
    
    def _read_int16(self) -> int:
        data = self.read(2)
        return struct.unpack('<h', data)[0] if len(data) == 2 else 0
    
    def _read_uint16(self) -> int:
        data = self.read(2)
        return struct.unpack('<H', data)[0] if len(data) == 2 else 0
    
    def _read_float(self) -> float:
        data = self.read(4)
        return struct.unpack('<f', data)[0] if len(data) == 4 else 0.0
    
    def _read_int64(self) -> int:
        data = self.read(8)
        return struct.unpack('<q', data)[0] if len(data) == 8 else 0
    
    def _read_uint64(self) -> int:
        data = self.read(8)
        return struct.unpack('<Q', data)[0] if len(data) == 8 else 0
    
    def _read_string(self) -> str:
        length = self._read_int32()
        if length < 0:
            length = -length
        if length == 0:
            return ""
        data = self.read(length * 2)
        return data.decode('utf-16-le').rstrip('\x00')
    
    def _read_ansi_string(self) -> str:
        """Size-prefixed ANSI string: BYTE size, then `size` bytes whose last
        is the terminator (Help/PACKAGES.md "Data types stored in package
        files")."""
        length = self._read_byte()
        if length == 0:
            return ""
        data = self.read(length)
        return data.decode('ascii', errors='replace').rstrip('\x00')

    def _read_null_terminated_string(self) -> str:
        """NUL-terminated ANSI string, the pre-64 name-table layout."""
        chars = []
        while True:
            byte = self._read_byte()
            if byte == 0:
                break
            chars.append(byte)
        return bytes(chars).decode('latin-1', errors='replace')

    def _read_bool(self) -> bool:
        return self._read_byte() != 0


class FArchiveFileReader(FArchive):
    def __init__(self, filename: str):
        super().__init__()
        self._loading = True
        self._persistent = True
        self._file = open(filename, 'rb')
        self._file.seek(0, 2)
        self._size = self._file.tell()
        self._file.seek(0)
        self._archive_size = self._size
    
    def read(self, length: int) -> bytes:
        if self._pos + length > self._size:
            self._error = True
            return b''
        data = self._file.read(length)
        self._pos += length
        return data
    
    def seek(self, pos: int) -> None:
        self._file.seek(pos)
        self._pos = pos
    
    def close(self) -> None:
        self._file.close()
        super().close()


class FArchiveMemoryReader(FArchive):
    def __init__(self, data: bytes):
        super().__init__()
        self._loading = True
        self._persistent = True
        self._data = data
        self._size = len(data)
        self._archive_size = self._size
    
    def read(self, length: int) -> bytes:
        if self._pos + length > self._size:
            self._error = True
            remaining = self._size - self._pos
            if remaining <= 0:
                return b''
            data = self._data[self._pos:self._pos + remaining]
            self._pos = self._size
            return data
        data = self._data[self._pos:self._pos + length]
        self._pos += length
        return data
    
    def seek(self, pos: int) -> None:
        self._pos = pos
    
    def at_end(self) -> bool:
        return self._pos >= self._size


class FBufferWriter(FArchive):
    """Buffer writer (UnTemplate.h:1484-1518); the C++ body is inline in the
    header. Wraps a caller-owned bytearray like the C++ wraps a TArray<BYTE>&,
    growing it and writing at Pos. Deviation: C++ resizes via TArray::Add;
    Python extends the bytearray to the write end, same net effect."""
    def __init__(self, data: bytearray):
        super().__init__()
        self._saving = True
        self._bytes = data
        self._pos = 0
    
    def write(self, data: bytes) -> int:
        end = self._pos + len(data)
        if end > len(self._bytes):
            self._bytes.extend(b'\x00' * (end - len(self._bytes)))
        self._bytes[self._pos:end] = data
        self._pos = end
        return len(data)
    
    def tell(self) -> int:
        return self._pos
    
    def seek(self, pos: int) -> None:
        self._pos = pos
    
    def total_size(self) -> int:
        return len(self._bytes)


class FArchiveFileWriter(FArchive):
    def __init__(self, filename: str):
        super().__init__()
        self._saving = True
        self._persistent = True
        self._file = open(filename, 'wb')
    
    def write(self, data: bytes) -> int:
        self._file.write(data)
        self._pos += len(data)
        self._size = max(self._size, self._pos)
        return len(data)
    
    def seek(self, pos: int) -> None:
        # The C++ file writer is seekable; FRiffChunk::Save (FRiffChunk.h:94)
        # relies on this to patch a chunk-size field after the body is written.
        self._file.seek(pos)
        self._pos = pos
    
    def close(self) -> None:
        self._file.close()
        super().close()


class FArray(FArchive):
    def __init__(self, type_size: int = 1):
        super().__init__()
        self._data = bytearray()
        self._type_size = type_size
    
    def read(self, length: int) -> bytes:
        if self._pos + length > len(self._data):
            self._error = True
            return b''
        data = bytes(self._data[self._pos:self._pos + length])
        self._pos += length
        return data
    
    def write(self, data: bytes) -> int:
        self._data.extend(data)
        self._pos += len(data)
        self._size = len(self._data)
        return len(data)
    
    def get_data(self) -> bytes:
        return bytes(self._data)
    
    def size(self) -> int:
        return len(self._data)


class FOutputDeviceNull(FOutputDevice):
    def serialize(self, v: str, event: FName = ENAME_Log) -> None:
        pass


class FOutputDeviceStdout(FOutputDevice):
    def serialize(self, v: str, event: FName = ENAME_Log) -> None:
        print(v)
    
    def log(self, v: str) -> None:
        print(v)


class FOutputDeviceFile(FOutputDevice):
    def __init__(self, filename: str, append: bool = False):
        mode = 'a' if append else 'w'
        self._file = open(filename, mode)
    
    def serialize(self, v: str, event: FName = ENAME_Log) -> None:
        self._file.write(v + '\n')
        self._file.flush()
    
    def flush(self) -> None:
        self._file.flush()
    
    def shutdown(self) -> None:
        self._file.close()


_WARNING_EVENTS = frozenset(
    (ENAME_Warning, ENAME_Error, ENAME_ExecWarning, ENAME_ScriptWarning)
)


class FFeedbackContextAnsi(FFeedbackContext):
    """Unreal Ansi user interface interaction (Core/Inc/FFeedbackContextAnsi.h).
    
    Deviations: appSprintf/GET_VARARGS become Python % formatting and *args;
    LocalPrint writes to stdout and C++'s fflush(stdout) becomes flush=True.
    YesNof reads the appCmdLine "Silent" switch (unported) from the `silent`
    ctor flag instead.
    """
    
    def __init__(self, silent: bool = False):
        self.slow_task_count = 0
        self.warning_count = 0
        self.context: Optional[FContextSupplier] = None
        self.aux_out: Optional[FOutputDevice] = None
        self.silent = silent
    
    def local_print(self, s: str) -> None:
        # FFeedbackContextAnsi.h:26-33 LocalPrint.
        print(s, end='', flush=True)
    
    def serialize(self, v: str, event: FName = ENAME_Log) -> None:
        # FFeedbackContextAnsi.h:42-86. The guard/unguard scaffolding is
        # dropped; the Event chain and re-Serialize formats are verbatim.
        if event == ENAME_Title:
            return
        if event == ENAME_Heading:
            v = f'--------------------{v}--------------------'
        elif event == ENAME_SubHeading:
            v = f'{v}...'
        elif event in _WARNING_EVENTS:
            # Context is prefixed only when a supplier is installed.
            if self.context:
                v = f'{self.context.get_context()} : {event}, {v}'
            self.warning_count += 1
        elif event == ENAME_Progress:
            self.local_print(v)
            self.local_print('\r')
            return
        self.local_print(v)
        self.local_print('\n')
        if GLog is not self:
            GLog.serialize(v, event)
        if self.aux_out:
            self.aux_out.serialize(v, event)
    
    def yes_nof(self, fmt: str, *args) -> bool:
        # FFeedbackContextAnsi.h:87-101.
        temp_str = fmt % args
        if (GIsClient or GIsEditor) and not self.silent:
            self.local_print(temp_str)
            self.local_print(' (Y/N): ')
            ch = sys.stdin.read(1)
            return ch in ('Y', 'y')
        return True
    
    def begin_slow_task(self, task: str, status_window: bool, cancelable: bool) -> None:
        # FFeedbackContextAnsi.h:102-107; only the count matters.
        global GIsSlowTask
        self.slow_task_count += 1
        GIsSlowTask = self.slow_task_count > 0
    
    def end_slow_task(self) -> None:
        # FFeedbackContextAnsi.h:108-114: check(SlowTaskCount>0).
        global GIsSlowTask
        if self.slow_task_count <= 0:
            raise ValueError('FFeedbackContextAnsi: EndSlowTask without BeginSlowTask')
        self.slow_task_count -= 1
        GIsSlowTask = self.slow_task_count > 0
    
    def status_updatef(self, numerator: int, denominator: int, fmt: str, *args) -> bool:
        # FFeedbackContextAnsi.h:115-126. GET_VARARGS builds TempStr, but the
        # only consumer is the stripped //!! body, so it is not formatted.
        return True
    
    def set_context(self, supplier: Optional[FContextSupplier]) -> None:
        # FFeedbackContextAnsi.h:127-132.
        self.context = supplier


class FMalloc:
    """Allocator interface (Core.h:210-219); all methods pure virtual."""
    def malloc(self, size: int, tag: str = '') -> int:
        raise NotImplementedError
    
    def realloc(self, ptr: int, new_size: int, tag: str = '') -> int:
        raise NotImplementedError
    
    def free(self, ptr: int) -> None:
        raise NotImplementedError
    
    def dump_allocs(self) -> None:
        raise NotImplementedError
    
    def heap_check(self) -> None:
        raise NotImplementedError
    
    def init(self) -> None:
        raise NotImplementedError
    
    def exit(self) -> None:
        raise NotImplementedError


_LIBC = None


def _get_libc():
    """Process-local C library; set 64-bit-safe pointer signatures."""
    global _LIBC
    if _LIBC is None:
        import ctypes
        libc = ctypes.CDLL(None)
        libc.malloc.restype = ctypes.c_void_p
        libc.malloc.argtypes = [ctypes.c_size_t]
        libc.realloc.restype = ctypes.c_void_p
        libc.realloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        libc.free.argtypes = [ctypes.c_void_p]
        _LIBC = libc
    return _LIBC


class FMallocAnsi(FMalloc):
    """ANSI C allocator (Core/Inc/FMallocAnsi.h).

    C++ hands out raw malloc pointers; Python represents them as int
    addresses via ctypes (retypes are set to pointer width, else the
    address truncates to 32 bits). Tag feeds C++ unguardf diagnostics
    only; unused here.
    """
    def malloc(self, size: int, tag: str = '') -> int:
        # FMallocAnsi.h:16-24: check(Size>0); malloc; check(Ptr).
        if size <= 0:
            raise ValueError(f'FMallocAnsi: size must be >0, got {size}')
        ptr = _get_libc().malloc(size)
        if not ptr:
            raise MemoryError(f'FMallocAnsi: malloc({size}) failed')
        return ptr
    
    def realloc(self, ptr: int, new_size: int, tag: str = '') -> int:
        # FMallocAnsi.h:25-46: NULL/zero-size branches; C++ checks
        # NewSize>=0 but never the result, so NULL propagates as 0.
        if new_size < 0:
            raise ValueError(f'FMallocAnsi: new_size must be >=0, got {new_size}')
        libc = _get_libc()
        if ptr and new_size:
            return libc.realloc(ptr, new_size) or 0
        if new_size:
            return libc.malloc(new_size) or 0
        if ptr:
            libc.free(ptr)
        return 0
    
    def free(self, ptr: int) -> None:
        # FMallocAnsi.h:47-52; free(NULL) is a C no-op.
        if ptr:
            _get_libc().free(ptr)
    
    def dump_allocs(self) -> None:
        # debugf(NAME_Exit, "Allocation checking disabled")
        # (FMallocAnsi.h:53-58); debugf is unported, so GLog carries it.
        GLog.serialize('Allocation checking disabled', ENAME_Exit)
    
    def heap_check(self) -> None:
        # FMallocAnsi.h:59-71: the body is #if _MSC_VER only; a no-op on
        # the Unix toolchain this port targets.
        pass
    
    def init(self) -> None:
        # FMallocAnsi.h:72-76: no-op in the C++ too.
        pass
    
    def exit(self) -> None:
        # FMallocAnsi.h:77-81: no-op in the C++ too.
        pass


class FFileManager:
    def __init__(self):
        pass
    
    def file_exists(self, filename: str) -> bool:
        import os
        return os.path.exists(filename)
    
    def directory_exists(self, dirname: str) -> bool:
        import os
        return os.path.isdir(dirname)
    
    def create_directory(self, dirname: str) -> bool:
        import os
        try:
            os.makedirs(dirname, exist_ok=True)
            return True
        except OSError:
            return False
    
    def delete_file(self, filename: str) -> bool:
        import os
        try:
            os.remove(filename)
            return True
        except OSError:
            return False
    
    def copy_file(self, dest: str, src: str, replace: bool = False) -> bool:
        import shutil
        try:
            if replace or not os.path.exists(dest):
                shutil.copy2(src, dest)
                return True
            return False
        except IOError:
            return False
    
    def move_file(self, dest: str, src: str) -> bool:
        import shutil
        try:
            shutil.move(src, dest)
            return True
        except IOError:
            return False
    
    def rename_file(self, oldname: str, newname: str) -> bool:
        import os
        try:
            os.rename(oldname, newname)
            return True
        except OSError:
            return False
    
    def file_size(self, filename: str) -> int:
        import os
        try:
            return os.path.getsize(filename)
        except OSError:
            return -1
    
    def get_time_stamp(self, filename: str) -> float:
        import os
        try:
            return os.path.getmtime(filename)
        except OSError:
            return 0.0
    
    def set_time_stamp(self, filename: str, timestamp: float) -> None:
        import os
        try:
            import time
            os.utime(filename, time.localtime(timestamp))
        except OSError:
            pass
    
    def create_file_reader(self, filename: str) -> Optional[FArchive]:
        if self.file_exists(filename):
            return FArchiveFileReader(filename)
        return None
    
    def create_file_writer(self, filename: str, append: bool = False) -> Optional[FArchive]:
        return FArchiveFileWriter(filename)
    
    def find_files(self, directory: str, pattern: str = "*", recursive: bool = False) -> list:
        import glob as g
        import os
        if recursive:
            return [os.path.join(dp, f) for dp, dn, fn in os.walk(directory) for f in fn]
        search_path = os.path.join(directory, pattern)
        return g.glob(search_path)
    
    def find_directories(self, directory: str) -> list:
        import os
        return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]


def _app_stricmp(str1: str, str2: str) -> int:
    """appStricmp (UnFile.h:298): ASCII case-insensitive compare."""
    for c1, c2 in zip(str1, str2):
        u1, u2 = appToUpper(c1), appToUpper(c2)
        if u1 != u2:
            return ord(u1) - ord(u2)
    return len(str1) - len(str2)


def _app_strcmp(str1: str, str2: str) -> int:
    """appStrcmp (UnFile.h:297): exact compare (sign only matters)."""
    if str1 == str2:
        return 0
    return -1 if str1 < str2 else 1


# appAtoi/appAtof (UnFile.h:310, bodies in Core.lib) follow C atoi/atof: parse a
# leading number, stop at the first invalid character, yield 0 when there is
# none.
_ATOI_RE = re.compile(r"[ \t\r\n\f\v]*[+-]?\d+")
_ATOF_RE = re.compile(r"[ \t\r\n\f\v]*[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")


def _app_atoi(text: str) -> int:
    match = _ATOI_RE.match(text)
    return int(match.group()) if match else 0


def _app_atof(text: str) -> float:
    match = _ATOF_RE.match(text)
    return float(match.group()) if match else 0.0


def _file_size(filename: str) -> int:
    """FFileManager::FileSize (Core.h:318) as used by Find: -1 when missing."""
    import os
    try:
        return os.path.getsize(filename)
    except OSError:
        return -1


def _load_file_to_string(filename: str) -> Optional[str]:
    """appLoadFileToString (UnFile.h:416): whole file as ANSI (latin-1).

    The C++ routes through GFileManager (body in Core.lib); the port reads the
    file directly, as core/riff.py does. Returns None when it cannot open.
    """
    try:
        with open(filename, "rb") as handle:
            return handle.read().decode("latin-1")
    except OSError:
        return None


def _save_string_to_file(text: str, filename: str) -> bool:
    """appSaveStringToFile (UnFile.h:418). Returns True on success."""
    try:
        with open(filename, "wb") as handle:
            handle.write(text.encode("latin-1"))
        return True
    except OSError:
        return False


def _split_lines(text: str) -> Iterator[str]:
    """Split on \\r/\\n runs, as FConfigFile::Read walks its buffer (FConfigCacheIni.h:36-45)."""
    length = len(text)
    ptr = 0
    while ptr < length:
        while ptr < length and text[ptr] in "\r\n":
            ptr += 1
        start = ptr
        while ptr < length and text[ptr] not in "\r\n":
            ptr += 1
        yield text[start:ptr]


def _split_pair(line: str) -> Optional[tuple[str, str]]:
    """Key/Value of one line: split at the first '=', strip one quote pair
    (FConfigCacheIni.h:56-65). None when the line has no '='."""
    eq = line.find("=")
    if eq < 0:
        return None
    value = line[eq + 1:]
    # The C++ misses the degenerate single-quote case; the len check avoids it.
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return line[:eq], value


class FConfigSection:
    """FConfigSection (FConfigCacheIni.h:14): TMultiMap<FString,FString>.

    Kept as an insertion-ordered list of (Key,Value) pairs. TMapBase::Add
    appends (UnTemplate.h:1634) and each hash bucket is LIFO, so Find returns
    the most recently added duplicate (UnTemplate.h:1718).
    """

    def __init__(self) -> None:
        self._pairs: list[tuple[str, str]] = []

    def add(self, key: str, value: str) -> str:
        """TMultiMap::Add (UnTemplate.h:1814): append a pair."""
        self._pairs.append((key, value))
        return value

    def find(self, key: str) -> Optional[str]:
        """TMapBase::Find (UnTemplate.h:1718): newest value for Key, else None."""
        index = self._find_index(key)
        return None if index < 0 else self._pairs[index][1]

    def set(self, key: str, value: str) -> None:
        """SetString's `*Str = Value` (FConfigCacheIni.h:222): update in place."""
        index = self._find_index(key)
        if index >= 0:
            self._pairs[index] = (key, value)

    def empty(self) -> None:
        """TMapBase::Empty (UnTemplate.h:1688)."""
        self._pairs.clear()

    def _find_index(self, key: str) -> int:
        for index in range(len(self._pairs) - 1, -1, -1):
            if self._pairs[index][0] == key:
                return index
        return -1

    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self._pairs)

    def __len__(self) -> int:
        return len(self._pairs)


class FConfigFile:
    """FConfigFile (FConfigCacheIni.h:18): TMap<FString,FConfigSection> + flags."""

    def __init__(self) -> None:
        self.dirty: bool = False
        self.no_save: bool = False
        self._sections: dict[str, FConfigSection] = {}

    def find(self, section: str) -> Optional[FConfigSection]:
        """TMapBase::Find (UnTemplate.h:1718)."""
        return self._sections.get(section)

    def set(self, section: str, value: FConfigSection) -> FConfigSection:
        """TMapBase::Set (UnTemplate.h:1697): update in place or append."""
        self._sections[section] = value
        return value

    def empty(self) -> None:
        """TMapBase::Empty (UnTemplate.h:1688)."""
        self._sections.clear()

    def read(self, filename: str) -> None:
        """FConfigFile::Read (FConfigCacheIni.h:26)."""
        self.empty()
        text = _load_file_to_string(filename)
        if text is None:
            return
        current: Optional[FConfigSection] = None
        for line in _split_lines(text):
            if line.startswith("[") and line.endswith("]"):
                name = line[1:-1]
                section = self.find(name)
                if section is None:
                    section = self.set(name, FConfigSection())
                current = section
            elif current is not None and line:
                pair = _split_pair(line)
                if pair is not None:
                    current.add(*pair)

    def write(self, filename: str) -> bool:
        """FConfigFile::Write (FConfigCacheIni.h:72)."""
        if not self.dirty or self.no_save:
            return True
        self.dirty = False
        parts: list[str] = []
        for name, section in self._sections.items():
            parts.append(f"[{name}]\r\n")
            for key, value in section:
                parts.append(f"{key}={value}\r\n")
            parts.append("\r\n")
        return _save_string_to_file("".join(parts), filename)

    def __len__(self) -> int:
        return len(self._sections)


class FConfigCacheIni:
    """FConfigCacheIni (FConfigCacheIni.h:92): the INI config database.

    Implements the FConfigCache interface (Core.h:223) and the
    TMap<FString,FConfigFile> of cached files. `filename` selects the file
    (None uses SystemIni, as the C++ NULL does); a None return mirrors the C++
    0/NULL failure result instead of fabricating an empty value.
    """

    def __init__(self) -> None:
        self.system_ini: str = ""
        self.user_ini: str = ""
        self._files: dict[str, FConfigFile] = {}

    def find(self, filename: Optional[str], create_if_not_found: bool) -> Optional[FConfigFile]:
        """FConfigCacheIni::Find (FConfigCacheIni.h:105)."""
        name = filename if filename else self.system_ini
        length = len(name)
        # Add ".ini" unless a dot sits at either extension position (:114).
        if length < 5 or (name[length - 4] != "." and name[length - 5] != "."):
            name += ".ini"
        if _app_stricmp(name, "User.ini") == 0:
            name = self.user_ini
        elif _app_stricmp(name, "System.ini") == 0:
            name = self.system_ini
        result = self._files.get(name)
        if result is None and (create_if_not_found or _file_size(name) >= 0):
            result = self._files.setdefault(name, FConfigFile())
            result.read(name)
        return result

    def flush(self, read: bool, filename: Optional[str] = None) -> None:
        """FConfigCacheIni::Flush (FConfigCacheIni.h:135)."""
        for name, config in self._files.items():
            if filename is None or name == filename:
                config.write(name)
        if not read:
            return
        if filename is not None:
            self._files.pop(filename, None)
        else:
            self._files.clear()

    def detach(self, filename: str) -> None:
        """FConfigCacheIni::Detach (FConfigCacheIni.h:150)."""
        config = self.find(filename, True)
        if config is not None:
            config.no_save = True

    def get_string(self, section: str, key: str, filename: Optional[str] = None) -> Optional[str]:
        """FConfigCacheIni::GetString (FConfigCacheIni.h:158,263): the value, or
        None where the C++ returns 0 (missing file, section or key)."""
        config = self.find(filename, False)
        if config is None:
            return None
        sec = config.find(section)
        if sec is None:
            return None
        return sec.find(key)

    def get_str(self, section: str, key: str, filename: Optional[str] = None) -> str:
        """FConfigCacheIni::GetStr (FConfigCacheIni.h:278): "" when missing."""
        value = self.get_string(section, key, filename)
        return value if value is not None else ""

    def get_section(self, section: str, filename: Optional[str] = None, size: int = 1024) -> Optional[str]:
        """FConfigCacheIni::GetSection (FConfigCacheIni.h:175): the section as
        the C++ NUL-separated buffer ``key=value\\0...\\0``; None when missing."""
        config = self.find(filename, False)
        if config is None:
            return None
        sec = config.find(section)
        if sec is None:
            return None
        out = ""
        for key, value in sec:
            if len(out) + len(key) + 1 < size:
                out += f"{key}={value}\0"
        return out + "\0"

    def get_section_private(self, section: str, force: bool, const: bool,
                            filename: Optional[str] = None) -> Optional[FConfigSection]:
        """FConfigCacheIni::GetSectionPrivate (FConfigCacheIni.h:192)."""
        config = self.find(filename, force)
        if config is None:
            return None
        sec = config.find(section)
        if sec is None and force:
            sec = config.set(section, FConfigSection())
        if sec is not None and (force or not const):
            config.dirty = True
        return sec

    def set_string(self, section: str, key: str, value: str, filename: Optional[str] = None) -> None:
        """FConfigCacheIni::SetString (FConfigCacheIni.h:206)."""
        config = self.find(filename, True)
        sec = config.find(section)
        if sec is None:
            sec = config.set(section, FConfigSection())
        current = sec.find(key)
        if current is None:
            sec.add(key, value)
            config.dirty = True
        elif _app_stricmp(current, value) != 0:
            config.dirty = _app_strcmp(current, value) != 0
            sec.set(key, value)

    def empty_section(self, section: str, filename: Optional[str] = None) -> None:
        """FConfigCacheIni::EmptySection (FConfigCacheIni.h:226)."""
        config = self.find(filename, False)
        if config is None:
            return
        sec = config.find(section)
        if sec is not None and len(sec) > 0:
            sec.empty()
            config.dirty = True

    def init(self, system_ini: str, user_ini: str, require_config: bool = False) -> None:
        """FConfigCacheIni::Init (FConfigCacheIni.h:241). RequireConfig is unused
        in the C++ body too."""
        self.system_ini = system_ini
        self.user_ini = user_ini

    def exit(self) -> None:
        """FConfigCacheIni::Exit (FConfigCacheIni.h:248)."""
        self.flush(True)

    def dump(self, out: FOutputDevice) -> None:
        """FConfigCacheIni::Dump (FConfigCacheIni.h:254). The C++ then dumps the
        TMap; the port logs the file/section counts."""
        out.serialize("Files map:")
        for name, config in self._files.items():
            out.serialize(f"   {name}: {len(config)} sections")

    def get_int(self, section: str, key: str, filename: Optional[str] = None) -> Optional[int]:
        """FConfigCacheIni::GetInt (FConfigCacheIni.h:286)."""
        text = self.get_string(section, key, filename)
        return None if text is None else _app_atoi(text)

    def get_float(self, section: str, key: str, filename: Optional[str] = None) -> Optional[float]:
        """FConfigCacheIni::GetFloat (FConfigCacheIni.h:304)."""
        text = self.get_string(section, key, filename)
        return None if text is None else _app_atof(text)

    def get_bool(self, section: str, key: str, filename: Optional[str] = None) -> Optional[bool]:
        """FConfigCacheIni::GetBool (FConfigCacheIni.h:322)."""
        text = self.get_string(section, key, filename)
        if text is None:
            return None
        if _app_stricmp(text, "True") == 0:
            return True
        return _app_atoi(text) == 1

    def set_int(self, section: str, key: str, value: int, filename: Optional[str] = None) -> None:
        """FConfigCacheIni::SetInt (FConfigCacheIni.h:347): "%i"."""
        self.set_string(section, key, f"{value}", filename)

    def set_float(self, section: str, key: str, value: float, filename: Optional[str] = None) -> None:
        """FConfigCacheIni::SetFloat (FConfigCacheIni.h:361): "%f" (6 decimals)."""
        self.set_string(section, key, f"{value:.6f}", filename)

    def set_bool(self, section: str, key: str, value: bool, filename: Optional[str] = None) -> None:
        """FConfigCacheIni::SetBool (FConfigCacheIni.h:375): "True"/"False"."""
        self.set_string(section, key, "True" if value else "False", filename)

    @staticmethod
    def factory() -> "FConfigCacheIni":
        """FConfigCacheIni::Factory (FConfigCacheIni.h:389)."""
        return FConfigCacheIni()


class UFactory:
    pass


class FTransactionBase:
    def __init__(self):
        self._data = None
    
    def transact(self, object: UObject) -> None:
        pass
    
    def commit(self) -> None:
        pass
    
    def abort(self) -> None:
        pass
    
    def reset(self) -> None:
        pass


class FCacheableData:
    def __init__(self):
        self._size = 0
    
    def get_min_size(self) -> int:
        return self._size
    
    def get_max_size(self) -> int:
        return self._size
    
    def get_cur_size(self) -> int:
        return self._size


class FCachedTextures(FCacheableData):
    def __init__(self):
        super().__init__()


class FMemStack:
    def __init__(self):
        self._top = 0
        self._mark = 0
    
    def unmark(self) -> None:
        pass
    
    def mark(self) -> None:
        self._mark = self._top
    
    def get_top(self) -> int:
        return self._top
    
    def flash(self) -> None:
        pass


class FMemCache:
    def __init__(self):
        self._hit = 0
        self._miss = 0
    
    def get_hit_count(self) -> int:
        return self._hit
    
    def get_miss_count(self) -> int:
        return self._miss


class FExec:
    def exec_commands(self, cmd: str) -> bool:
        return False


class FCallbackParams:
    def __init__(self):
        self._depth = 0


from .objects import FOutputDevice


class FCacheIndex:
    def __init__(self):
        self._buckets = {}
    
    def init(self) -> None:
        pass
    
    def exit(self) -> None:
        pass
    
    def flush(self, evict_classes: bool = True) -> None:
        pass
    
    def get_data(self) -> bytes:
        return b''


class FObj:
    _max_objects = 20000
    _hash_mod = 8
    _hash_bucket = None
    
    def __init__(self):
        self._next = None
    
    @classmethod
    def get_hash_bucket(cls, name: FName) -> 'FObj':
        if cls._hash_bucket is None:
            cls._hash_bucket = [None] * cls._hash_mod
        idx = hash(name) % cls._hash_mod
        return cls._hash_bucket[idx]


GNull = FOutputDeviceNull()
GLog = FOutputDeviceStdout()
GError = FOutputDevice()
# Core globals (Core.h:366-372); set by engine startup, which is unported, so
# the false defaults keep this build headless.
GIsEditor = False
GIsClient = False
GIsSlowTask = False