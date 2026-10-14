"""Core system: FArchive, serialization, config"""

from typing import TYPE_CHECKING, Optional, Any
import io
import struct

from .types import FName, FString, TArray, FGuid, FCompactIndex, INDEX_NONE, ENAME_Log
from .objver import (
    ENGINE_NEGOTIATION_VERSION,
    PACKAGE_FILE_VERSION,
    PACKAGE_FILE_VERSION_LICENSEE,
)
from .objects import UObject, UClass, UPackage, ULinkerLoad, FOutputDevice

if TYPE_CHECKING:
    from .types import FVector, FRotator


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

    def serialize_double(self, value: float) -> float:
        """QWORD / SQWORD (UnArc.h:182-191): eight bytes."""
        if self._loading:
            return self._read_double()
        self.write(struct.pack('<d', value))
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

    def serialize_str(self, s: FString) -> 'FArchive':
        return self

    def serialize_int(self, value: int, max_bits: int = 0) -> int:
        """C++ SerializeInt(Value, Max). The base FArchive writes a full DWORD
        whatever Max says (UnArc.h:31); FBitWriter overrides this in UnBits.h."""
        return self.serialize_dword(value)

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
    
    def _read_double(self) -> float:
        data = self.read(8)
        return struct.unpack('<d', data)[0] if len(data) == 8 else 0.0
    
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


class FMalloc:
    def malloc(self, size: int) -> int:
        raise NotImplementedError
    
    def free(self, ptr: int) -> None:
        raise NotImplementedError
    
    def realloc(self, ptr: int, size: int) -> int:
        raise NotImplementedError
    
    def get_size(self, ptr: int) -> int:
        return 0
    
    def get_physical_size(self, ptr: int) -> int:
        return 0


class FMallocAnsi(FMalloc):
    def __init__(self):
        pass
    
    def malloc(self, size: int) -> int:
        import ctypes
        return ctypes.windll.kernel32.LocalAlloc(0, size) if hasattr(ctypes, 'windll') else 0
    
    def free(self, ptr: int) -> None:
        import ctypes
        if ptr and hasattr(ctypes, 'windll'):
            ctypes.windll.kernel32.LocalFree(ptr)


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


class FConfigCacheIni:
    def __init__(self):
        self._sections: dict[str, dict[str, str]] = {}
    
    def get_string(self, group: str, key: str) -> str:
        if group in self._sections and key in self._sections[group]:
            return self._sections[group][key]
        return ""
    
    def get_int(self, group: str, key: str, default: int = 0) -> int:
        val = self.get_string(group, key)
        if val:
            try:
                return int(val)
            except ValueError:
                pass
        return default
    
    def get_float(self, group: str, key: str, default: float = 0.0) -> float:
        val = self.get_string(group, key)
        if val:
            try:
                return float(val)
            except ValueError:
                pass
        return default
    
    def get_bool(self, group: str, key: str, default: bool = False) -> bool:
        val = self.get_string(group, key)
        if val:
            return val.lower() in ('true', '1', 'yes', 'on')
        return default
    
    def set_string(self, group: str, key: str, value: str) -> None:
        if group not in self._sections:
            self._sections[group] = {}
        self._sections[group][key] = value
    
    def set_int(self, group: str, key: str, value: int) -> None:
        self.set_string(group, key, str(value))
    
    def set_float(self, group: str, key: str, value: float) -> None:
        self.set_string(group, key, str(value))
    
    def set_bool(self, group: str, key: str, value: bool) -> None:
        self.set_string(group, key, "True" if value else "False")
    
    def flush(self) -> None:
        pass
    
    def close(self) -> None:
        pass


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