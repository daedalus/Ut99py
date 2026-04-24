"""Core types: FName, FString, math, containers"""

import struct
from typing import TypeVar, Generic, Iterator, Iterable, Optional, Any
from collections.abc import MutableSequence, Sequence
from abc import ABC, abstractmethod

PI = 3.1415926535897932
SMALL_NUMBER = 1e-8
KINDA_SMALL_NUMBER = 1e-4
DELTA = 0.00001
SLERP_DELTA = 0.0001

MAXBYTE = 0xff
MAXWORD = 0xffff
MAXDWORD = 0xffffffff
MAXSBYTE = 0x7f
MAXSWORD = 0x7fff
MAXINT = 0x7fffffff
INDEX_NONE = -1
UNICODE_BOM = 0xfeff

T = TypeVar('T')


class FTime:
    FIXTIME = 4294967296.0
    
    def __init__(self, value=0.0):
        if isinstance(value, float):
            self.v = int(value * self.FIXTIME)
        elif isinstance(value, int):
            self.v = value
        else:
            self.v = 0
    
    @classmethod
    def from_float(cls, f: float) -> 'FTime':
        return cls(int(f * cls.FIXTIME))
    
    def get_float(self) -> float:
        return self.v / self.FIXTIME
    
    def __add__(self, other: float) -> 'FTime':
        if isinstance(other, FTime):
            return FTime(self.v + other.v)
        return FTime(self.v + int(other * self.FIXTIME))
    
    def __sub__(self, other: 'FTime') -> float:
        return (self.v - other.v) / self.FIXTIME
    
    def __mul__(self, other: float) -> 'FTime':
        return FTime(int(self.v * other))
    
    def __truediv__(self, other: float) -> 'FTime':
        return FTime(int(self.v / other))
    
    def __iadd__(self, other: float) -> 'FTime':
        self.v += int(other * self.FIXTIME)
        return self
    
    def __imul__(self, other: float) -> 'FTime':
        self.v = int(self.v * other)
        return self
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, FTime):
            return self.v == other.v
        return False
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __gt__(self, other: 'FTime') -> bool:
        return self.v > other.v
    
    def __repr__(self) -> str:
        return f"FTime({self.get_float()})"


class FName:
    _names: dict[int, str] = {}
    _name_to_index: dict[str, int] = {}
    _next_index: int = 1
    
    def __init__(self, name: str = "None", number: int = 0):
        self.name = name
        self.number = number
        if name not in FName._name_to_index:
            FName._name_to_index[name] = FName._next_index
            FName._names[FName._next_index] = name
            FName._next_index += 1
    
    def __str__(self) -> str:
        if self.number:
            return f"{self.name}_{self.number}"
        return self.name
    
    def __repr__(self) -> str:
        return f"FName('{self}')"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, FName):
            return self.name == other.name and self.number == other.number
        return False
    
    def __hash__(self) -> int:
        return hash((self.name, self.number))


NAME_None = FName("None", 0)
NAME_ByteProperty = FName("ByteProperty")
NAME_IntProperty = FName("IntProperty")
NAME_BoolProperty = FName("BoolProperty")
NAME_FloatProperty = FName("FloatProperty")
NAME_ObjectProperty = FName("ObjectProperty")
NAME_NameProperty = FName("NameProperty")
NAME_StringProperty = FName("StringProperty")
NAME_ClassProperty = FName("ClassProperty")
NAME_ArrayProperty = FName("ArrayProperty")
NAME_StructProperty = FName("StructProperty")
NAME_VectorProperty = FName("VectorProperty")
NAME_RotatorProperty = FName("RotatorProperty")

ENAME_Load = FName("Load")
ENAME_Log = FName("Log")
ENAME_Event = FName("Event")
ENAME_Warning = FName("Warning")
ENAME_Error = FName("Error")


class FString(str):
    def __new__(cls, s: str = "") -> 'FString':
        return super().__new__(cls, s)
    
    def __repr__(self) -> str:
        return f'FString("{self}")'
    
    def left(self, count: int) -> 'FString':
        return FString(self[:count])
    
    def right(self, count: int) -> 'FString':
        return FString(self[len(self)-count:])
    
    def mid(self, start: int, count: int = -1) -> 'FString':
        if count < 0:
            count = len(self) - start
        return FString(self[start:start+count])


class FVector:
    __slots__ = ('x', 'y', 'z', 'w')
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
    
    def __add__(self, other: 'FVector') -> 'FVector':
        return FVector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'FVector') -> 'FVector':
        return FVector(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'FVector':
        return FVector(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar: float) -> 'FVector':
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'FVector':
        return FVector(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __neg__(self) -> 'FVector':
        return FVector(-self.x, -self.y, -self.z)
    
    def dot(self, other: 'FVector') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'FVector') -> 'FVector':
        return FVector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def size(self) -> float:
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5
    
    def size_squared(self) -> float:
        return self.x**2 + self.y**2 + self.z**2
    
    def normalize(self) -> 'FVector':
        s = self.size()
        if s > SMALL_NUMBER:
            return self / s
        return FVector()
    
    def is_near_zero(self, tolerance: float = KINDA_SMALL_NUMBER) -> bool:
        return self.size_squared() < tolerance * tolerance
    
    def __repr__(self) -> str:
        return f"FVector({self.x}, {self.y}, {self.z})"


class FPlane(FVector):
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        super().__init__(x, y, z, w)
    
    def plane_dot(self, p: FVector) -> float:
        return self.x * p.x + self.y * p.y + self.z * p.z + self.w


class FRotator:
    __slots__ = ('pitch', 'yaw', 'roll')
    
    def __init__(self, pitch: int = 0, yaw: int = 0, roll: int = 0):
        self.pitch = pitch & 0xFFFF
        self.yaw = yaw & 0xFFFF
        self.roll = roll & 0xFFFF
    
    def __repr__(self) -> str:
        return f"FRotator(p={self.pitch}, y={self.yaw}, r={self.roll})"
    
    def vector(self) -> FVector:
        cp = self.pitch / 182.0
        cy = self.yaw / 182.0
        sr, cr = _sincos(self.roll / 182.0)
        sp, cp = _sincos(cp)
        sy, cy = _sincos(cy)
        
        return FVector(
            cp * cy,
            cp * sy,
            sp
        )
    
    @classmethod
    def from_vector(cls, v: FVector) -> 'FRotator':
        cls
        raise NotImplementedError


def _sincos(angle: float):
    import math
    return math.sin(angle), math.cos(angle)


class FQuat:
    __slots__ = ('x', 'y', 'z', 'w')
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
    
    def __repr__(self) -> str:
        return f"FQuat(x={self.x}, y={self.y}, z={self.z}, w={self.w})"
    
    def sizeSquared(self) -> float:
        return self.x**2 + self.y**2 + self.z**2 + self.w**2
    
    def normalize(self) -> 'FQuat':
        size = self.sizeSquared() ** 0.5
        if size > SMALL_NUMBER:
            return FQuat(self.x/size, self.y/size, self.z/size, self.w/size)
        return FQuat()


class FMatrix:
    __slots__ = ('m',)
    
    def __init__(self):
        self.m = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            self.m[i][i] = 1.0
    
    def __repr__(self) -> str:
        lines = []
        for row in self.m:
            lines.append(f"  [{row[0]:8.4f} {row[1]:8.4f} {row[2]:8.4f} {row[3]:8.4f}]")
        return "FMatrix(\n" + "\n".join(lines) + "\n)"


class TArray(MutableSequence[T]):
    __slots__ = ('_data',)
    
    def __init__(self, initial: Iterable[T] = None):
        self._data: list[T] = []
        if initial:
            self._data = list(initial)
    
    def __getitem__(self, index: int) -> T:
        return self._data[index]
    
    def __setitem__(self, index: int, value: T) -> None:
        self._data[index] = value
    
    def __delitem__(self, index: int) -> None:
        del self._data[index]
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __iter__(self) -> Iterator[T]:
        return iter(self._data)
    
    def __repr__(self) -> str:
        return f"TArray({self._data})"
    
    def insert(self, index: int, value: T) -> None:
        self._data.insert(index, value)
    
    def append(self, value: T) -> None:
        self._data.append(value)
    
    def add(self, value: T) -> int:
        self._data.append(value)
        return len(self._data) - 1
    
    def remove(self, value: T) -> None:
        self._data.remove(value)
    
    def pop(self, index: int = -1) -> T:
        return self._data.pop(index)
    
    def empty(self) -> None:
        self._data.clear()
    
    def num(self) -> int:
        return len(self._data)
    
    def get_data(self) -> list[T]:
        return self._data


KT = TypeVar('KT')
VT = TypeVar('VT')

class TMap(Generic[KT, VT]):
    __slots__ = ('_data',)
    
    def __init__(self, initial: dict[KT, VT] = None):
        self._data: dict[KT, VT] = {}
        if initial:
            self._data = dict(initial)
    
    def __getitem__(self, key: KT) -> VT:
        return self._data[key]
    
    def __setitem__(self, key: KT, value: VT) -> None:
        self._data[key] = value
    
    def __delitem__(self, key: KT) -> None:
        del self._data[key]
    
    def __iter__(self):
        return iter(self._data)
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __contains__(self, key: KT) -> bool:
        return key in self._data
    
    def get(self, key: KT, default: VT = None) -> VT:
        return self._data.get(key, default)
    
    def keys(self):
        return self._data.keys()
    
    def values(self):
        return self._data.values()
    
    def items(self):
        return self._data.items()
    
    def __repr__(self) -> str:
        return f"TMap({self._data})"


class FGuid:
    def __init__(self, a: int = 0, b: int = 0, c: int = 0, d: int = 0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
    
    def __repr__(self) -> str:
        return f"FGuid({self.a:08x}, {self.b:08x}, {self.c:08x}, {self.d:08x})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, FGuid):
            return self.a == other.a and self.b == other.b and self.c == other.c and self.d == other.d
        return False
    
    def __hash__(self) -> int:
        return hash((self.a, self.b, self.c, self.d))


class FCompactIndex:
    def __init__(self, value: int = 0):
        self.value = value
    
    def encode(self) -> bytes:
        if self.value == 0:
            return bytes([0])
        result = []
        val = self.value
        if val < 0:
            val = -val | (1 << 31)
        while val >= 0x80:
            result.append((val & 0x7F) | 0x80)
            val >>= 7
        result.append(val & 0x7F)
        return bytes(result)
    
    def __repr__(self) -> str:
        return f"FCompactIndex({self.value})"


class FBox:
    def __init__(self, min: Optional[FVector] = None, max: Optional[FVector] = None, is_valid: int = 0):
        self.min = min if min else FVector(0, 0, 0)
        self.max = max if max else FVector(0, 0, 0)
        self.is_valid = is_valid
    
    def init(self) -> None:
        self.is_valid = 0
    
    def get_center(self) -> FVector:
        return (self.min + self.max) * 0.5
    
    def get_extent(self) -> FVector:
        return self.max - self.min
    
    def is_valid_box(self) -> bool:
        return self.is_valid != 0
    
    def is_inside(self, point: FVector) -> bool:
        if not self.is_valid_box():
            return False
        return (point.x >= self.min.x and point.x <= self.max.x and
                point.y >= self.min.y and point.y <= self.max.y and
                point.z >= self.min.z and point.z <= self.max.z)
    
    def __repr__(self) -> str:
        return f"FBox({self.min}, {self.max}, valid={self.is_valid})"


class FSphere:
    def __init__(self, center: Optional[FVector] = None, w: float = 0.0):
        self.center = center if center else FVector(0, 0, 0)
        self.w = w
    
    def get_center(self) -> FVector:
        return self.center
    
    def get_radius(self) -> float:
        return self.w
    
    def is_valid_sphere(self) -> bool:
        return self.w > 0.0
    
    def __repr__(self) -> str:
        return f"FSphere({self.center}, {self.w})"