"""Core types: FName, FString, math, containers.

Ported from Core/Inc/UnMath.h (vectors, rotators, quats, matrices,
coords, geometry free functions, global trig tables) and
Core/Inc/UnArc.h (FGuid, FCompactIndex, TArray/TMap containers; see
core/system.py for the FArchive serializer itself).
"""

import struct
import numpy as np
from typing import TypeVar, Generic, Iterator, Iterable, Optional, Any
from collections.abc import MutableSequence, Sequence
from abc import ABC, abstractmethod

PI = 3.1415926535897932
SMALL_NUMBER = 1e-8
KINDA_SMALL_NUMBER = 1e-4
DELTA = 0.00001
SLERP_DELTA = 0.0001

# Magic numbers for numerical precision.
THRESH_POINT_ON_PLANE = 0.10
THRESH_POINT_ON_SIDE = 0.20
THRESH_POINTS_ARE_SAME = 0.002
THRESH_POINTS_ARE_NEAR = 0.015
THRESH_NORMALS_ARE_SAME = 0.00002
THRESH_VECTORS_ARE_NEAR = 0.0004
THRESH_SPLIT_POLY_WITH_PLANE = 0.25
THRESH_SPLIT_POLY_PRECISELY = 0.01
THRESH_ZERO_NORM_SQUARED = 0.0001
THRESH_VECTORS_ARE_PARALLEL = 0.02

# Global math table constants (FGlobalMath).
ANGLE_SHIFT = 2
ANGLE_BITS = 14
NUM_ANGLES = 16384
NUM_SQRTS = 16384
ANGLE_MASK = ((1 << ANGLE_BITS) - 1) << (16 - ANGLE_BITS)


def FSnap(location: float, grid: float) -> float:
    """Snap a value to the nearest grid multiple."""
    import math

    if grid == 0.0:
        return location
    return math.floor((location + 0.5 * grid) / grid) * grid


def FSheerSnap(sheer: float) -> float:
    """Internal sheer adjusting function so it snaps nicely at 0 and 45 degrees."""
    if sheer < -0.65:
        return sheer + 0.15
    elif sheer > 0.65:
        return sheer - 0.15
    elif sheer < -0.55:
        return -0.50
    elif sheer > 0.55:
        return 0.50
    elif sheer < -0.05:
        return sheer + 0.05
    elif sheer > 0.05:
        return sheer - 0.05
    return 0.0


def FNextPowerOfTwo(n: int) -> int:
    """Find the closest power of 2 that is >= N."""
    if n <= 0:
        return 0
    result = 1
    while result < n and result < 65536:
        result <<= 1
    return result if result <= 65536 else 0


def FAddAngleConfined(angle: int, delta: int, min_thresh: int, max_thresh: int) -> int:
    """Add to a word angle, constraining it within a min/max (not to cross).

    Accounts for the funkyness of word angles.  Assumes that angle is
    initially in the desired range.
    """
    if delta < 0:
        if delta <= -0x10000 or delta <= -((angle - min_thresh) & 0xFFFF):
            return min_thresh & 0xFFFF
    elif delta > 0:
        if delta >= 0x10000 or delta >= ((max_thresh - angle) & 0xFFFF):
            return max_thresh & 0xFFFF
    return (angle + delta) & 0xFFFF


def ReduceAngle(angle: int) -> int:
    """Eliminate all fractional precision from an angle."""
    return angle & ANGLE_MASK


def IsNegativeFloat(f: float) -> bool:
    """Detect the sign bit of a float."""
    return struct.unpack("<I", struct.pack("<f", f))[0] >= 0x80000000


def IsSmallerPositiveFloat(f1: float, f2: float) -> bool:
    return (
        struct.unpack("<I", struct.pack("<f", f1))[0]
        < struct.unpack("<I", struct.pack("<f", f2))[0]
    )


def MinPositiveFloat(f1: float, f2: float) -> float:
    return f1 if IsSmallerPositiveFloat(f1, f2) else f2


def MaxPositiveFloat(f1: float, f2: float) -> float:
    return f2 if IsSmallerPositiveFloat(f1, f2) else f1


def EqualPositiveFloat(f1: float, f2: float) -> bool:
    return (
        struct.unpack("<I", struct.pack("<f", f1))[0]
        == struct.unpack("<I", struct.pack("<f", f2))[0]
    )


def ClampPositiveFloat(f0: float, f1: float, f2: float) -> float:
    if IsSmallerPositiveFloat(f0, f1):
        return f1
    if not IsSmallerPositiveFloat(f0, f2):
        return f2
    return f0


MAXBYTE = 0xFF
MAXWORD = 0xFFFF
MAXDWORD = 0xFFFFFFFF
MAXSBYTE = 0x7F
MAXSWORD = 0x7FFF
MAXINT = 0x7FFFFFFF
INDEX_NONE = -1
UNICODE_BOM = 0xFEFF

T = TypeVar("T")


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
    def from_float(cls, f: float) -> "FTime":
        return cls(int(f * cls.FIXTIME))

    def get_float(self) -> float:
        return self.v / self.FIXTIME

    def __add__(self, other: float) -> "FTime":
        if isinstance(other, FTime):
            return FTime(self.v + other.v)
        return FTime(self.v + int(other * self.FIXTIME))

    def __sub__(self, other: "FTime") -> float:
        return (self.v - other.v) / self.FIXTIME

    def __mul__(self, other: float) -> "FTime":
        return FTime(int(self.v * other))

    def __truediv__(self, other: float) -> "FTime":
        return FTime(int(self.v / other))

    def __iadd__(self, other: float) -> "FTime":
        self.v += int(other * self.FIXTIME)
        return self

    def __imul__(self, other: float) -> "FTime":
        self.v = int(self.v * other)
        return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FTime):
            return self.v == other.v
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __gt__(self, other: "FTime") -> bool:
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

    def get_index(self) -> int:
        """FName::GetIndex (UnName.h:73) - index into the global name table."""
        return FName._name_to_index[self.name]

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
ENAME_Exit = FName("Exit")
ENAME_Title = FName("Title")
ENAME_Heading = FName("Heading")
ENAME_SubHeading = FName("SubHeading")
ENAME_ExecWarning = FName("ExecWarning")
ENAME_ScriptWarning = FName("ScriptWarning")
ENAME_Progress = FName("Progress")


class FString(str):
    def __new__(cls, s: str = "") -> "FString":
        return super().__new__(cls, s)

    def __repr__(self) -> str:
        return f'FString("{self}")'

    def left(self, count: int) -> "FString":
        return FString(self[:count])

    def right(self, count: int) -> "FString":
        return FString(self[len(self) - count :])

    def mid(self, start: int, count: int = -1) -> "FString":
        if count < 0:
            count = len(self) - start
        return FString(self[start : start + count])


class FVector:
    __slots__ = ("x", "y", "z", "w")

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    # Binary math operators.
    def __add__(self, other: "FVector") -> "FVector":
        return FVector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "FVector") -> "FVector":
        return FVector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other) -> "FVector":
        if isinstance(other, FVector):
            return FVector(self.x * other.x, self.y * other.y, self.z * other.z)
        return FVector(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, scalar: float) -> "FVector":
        return self.__mul__(scalar)

    def __truediv__(self, other) -> "FVector":
        if isinstance(other, FVector):
            return FVector(self.x / other.x, self.y / other.y, self.z / other.z)
        rscale = 1.0 / other
        return FVector(self.x * rscale, self.y * rscale, self.z * rscale)

    def __neg__(self) -> "FVector":
        return FVector(-self.x, -self.y, -self.z)

    def __iadd__(self, other: "FVector") -> "FVector":
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __isub__(self, other: "FVector") -> "FVector":
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __imul__(self, other) -> "FVector":
        if isinstance(other, FVector):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        else:
            self.x *= other
            self.y *= other
            self.z *= other
        return self

    def __itruediv__(self, other) -> "FVector":
        if isinstance(other, FVector):
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
        else:
            rv = 1.0 / other
            self.x *= rv
            self.y *= rv
            self.z *= rv
        return self

    def __xor__(self, other: "FVector") -> "FVector":
        """Cross product, operator^."""
        return self.cross(other)

    def __or__(self, other: "FVector") -> float:
        """Dot product, operator|."""
        return self.dot(other)

    # Binary comparison operators.
    def __eq__(self, other: object) -> bool:
        if isinstance(other, FVector):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, FVector):
            return self.x != other.x or self.y != other.y or self.z != other.z
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))

    def dot(self, other: "FVector") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "FVector") -> "FVector":
        return FVector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def size(self) -> float:
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def size_squared(self) -> float:
        return self.x**2 + self.y**2 + self.z**2

    def size_2d(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def size_squared_2d(self) -> float:
        return self.x**2 + self.y**2

    def is_nearly_zero(self) -> bool:
        return (
            abs(self.x) < KINDA_SMALL_NUMBER
            and abs(self.y) < KINDA_SMALL_NUMBER
            and abs(self.z) < KINDA_SMALL_NUMBER
        )

    def is_near_zero(self, tolerance: float = KINDA_SMALL_NUMBER) -> bool:
        return self.size_squared() < tolerance * tolerance

    def is_zero(self) -> bool:
        return self.x == 0.0 and self.y == 0.0 and self.z == 0.0

    def normalize(self) -> "FVector":
        s = self.size()
        if s > SMALL_NUMBER:
            return self / s
        return FVector()

    def projection(self) -> "FVector":
        rz = 1.0 / self.z
        return FVector(self.x * rz, self.y * rz, 1.0)

    def unsafe_normal(self) -> "FVector":
        scale = 1.0 / ((self.x * self.x + self.y * self.y + self.z * self.z) ** 0.5)
        return FVector(self.x * scale, self.y * scale, self.z * scale)

    def safe_normal(self) -> "FVector":
        square_sum = self.size_squared()
        if square_sum >= SMALL_NUMBER:
            scale = 1.0 / (square_sum**0.5)
            return FVector(self.x * scale, self.y * scale, self.z * scale)
        return FVector()

    def grid_snap(self, grid: "FVector") -> "FVector":
        return FVector(
            FSnap(self.x, grid.x), FSnap(self.y, grid.y), FSnap(self.z, grid.z)
        )

    def bound_to_cube(self, radius: float) -> "FVector":
        return FVector(
            max(-radius, min(radius, self.x)),
            max(-radius, min(radius, self.y)),
            max(-radius, min(radius, self.z)),
        )

    def add_bounded(self, v: "FVector", radius: float = MAXSWORD) -> None:
        result = (self + v).bound_to_cube(radius)
        self.x, self.y, self.z = result.x, result.y, result.z

    def component(self, index: int) -> float:
        return (self.x, self.y, self.z)[index]

    def booleanize(self) -> int:
        """Return a boolean based on the vector's direction."""
        if self.x > 0.0:
            return 1
        if self.x < 0.0:
            return 0
        if self.y > 0.0:
            return 1
        if self.y < 0.0:
            return 0
        return 1 if self.z >= 0.0 else 0

    # Transformation.
    def mirror_by_vector(self, mirror_normal: "FVector") -> "FVector":
        return self - mirror_normal * (2.0 * (self | mirror_normal))

    def mirror_by_plane(self, mirror_plane: "FPlane") -> "FVector":
        return self - mirror_plane * (2.0 * mirror_plane.plane_dot(self))

    def transform_vector_by(self, coords: "FCoords") -> "FVector":
        return FVector(self | coords.x_axis, self | coords.y_axis, self | coords.z_axis)

    def transform_point_by(self, coords: "FCoords") -> "FVector":
        temp = self - coords.origin
        return FVector(temp | coords.x_axis, temp | coords.y_axis, temp | coords.z_axis)

    def pivot_transform(self, coords: "FCoords") -> "FVector":
        return coords.origin + FVector(
            self | coords.x_axis, self | coords.y_axis, self | coords.z_axis
        )

    def rotation(self) -> "FRotator":
        """Convert a vector into a rotation facing in its direction."""
        import math

        r = FRotator()
        r.yaw = int(round(math.atan2(self.y, self.x) * (65536.0 / (2.0 * PI)))) & 0xFFFF
        r.pitch = (
            int(
                round(
                    math.atan2(self.z, (self.x * self.x + self.y * self.y) ** 0.5)
                    * (65536.0 / (2.0 * PI))
                )
            )
            & 0xFFFF
        )
        r.roll = 0
        return r

    def find_best_axis_vectors(self) -> tuple:
        """Find two vectors which are orthogonal to this one and to each other."""
        best = FVector(abs(self.x), abs(self.y), abs(self.z))
        if best.x > best.y and best.x > best.z:
            axis1 = FVector(0.0, 1.0, 0.0)
            axis2 = FVector(0.0, 0.0, 1.0)
        elif best.y > best.z:
            axis1 = FVector(0.0, 0.0, 1.0)
            axis2 = FVector(1.0, 0.0, 0.0)
        else:
            axis1 = FVector(1.0, 0.0, 0.0)
            axis2 = FVector(0.0, 1.0, 0.0)
        return axis1, axis2

    def __repr__(self) -> str:
        return f"FVector({self.x}, {self.y}, {self.z})"


class FPlane(FVector):
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        super().__init__(x, y, z, w)

    @classmethod
    def from_normal_w(cls, normal: FVector, w: float) -> "FPlane":
        return cls(normal.x, normal.y, normal.z, w)

    @classmethod
    def from_base_normal(cls, base: FVector, normal: FVector) -> "FPlane":
        return cls(normal.x, normal.y, normal.z, base | normal)

    @classmethod
    def from_points(cls, a: FVector, b: FVector, c: FVector) -> "FPlane":
        normal = ((b - a) ^ (c - a)).safe_normal()
        return cls(normal.x, normal.y, normal.z, a | normal)

    def plane_dot(self, p: FVector) -> float:
        return self.x * p.x + self.y * p.y + self.z * p.z - self.w

    def flip(self) -> "FPlane":
        return FPlane(-self.x, -self.y, -self.z, -self.w)

    def transform_plane_by_ortho(self, coords: "FCoords") -> "FPlane":
        normal = FVector(
            self | coords.x_axis, self | coords.y_axis, self | coords.z_axis
        )
        return FPlane(
            normal.x,
            normal.y,
            normal.z,
            self.w - (coords.origin.transform_vector_by(coords) | normal),
        )


class FRotator:
    __slots__ = ("pitch", "yaw", "roll")

    def __init__(self, pitch: int = 0, yaw: int = 0, roll: int = 0):
        self.pitch = pitch & 0xFFFF
        self.yaw = yaw & 0xFFFF
        self.roll = roll & 0xFFFF

    def __repr__(self) -> str:
        return f"FRotator(p={self.pitch}, y={self.yaw}, r={self.roll})"

    # Binary arithmetic operators.
    def __add__(self, other: "FRotator") -> "FRotator":
        return FRotator(
            self.pitch + other.pitch, self.yaw + other.yaw, self.roll + other.roll
        )

    def __sub__(self, other: "FRotator") -> "FRotator":
        return FRotator(
            self.pitch - other.pitch, self.yaw - other.yaw, self.roll - other.roll
        )

    def __mul__(self, scale: float) -> "FRotator":
        import math

        return FRotator(
            int(math.floor(self.pitch * scale + 0.5)),
            int(math.floor(self.yaw * scale + 0.5)),
            int(math.floor(self.roll * scale + 0.5)),
        )

    def __rmul__(self, scale: float) -> "FRotator":
        return self.__mul__(scale)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FRotator):
            return (
                self.pitch == other.pitch
                and self.yaw == other.yaw
                and self.roll == other.roll
            )
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, FRotator):
            return (
                self.pitch != other.pitch
                or self.yaw != other.yaw
                or self.roll != other.roll
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.pitch, self.yaw, self.roll))

    # Functions.
    def reduce(self) -> "FRotator":
        return FRotator(
            ReduceAngle(self.pitch), ReduceAngle(self.yaw), ReduceAngle(self.roll)
        )

    def is_zero(self) -> bool:
        return (
            (self.pitch & 0xFFFF) == 0
            and (self.yaw & 0xFFFF) == 0
            and (self.roll & 0xFFFF) == 0
        )

    def add(self, delta_pitch: int, delta_yaw: int, delta_roll: int) -> "FRotator":
        self.yaw = (self.yaw + delta_yaw) & 0xFFFF
        self.pitch = (self.pitch + delta_pitch) & 0xFFFF
        self.roll = (self.roll + delta_roll) & 0xFFFF
        return self

    def add_bounded(
        self, delta_pitch: int, delta_yaw: int, delta_roll: int
    ) -> "FRotator":
        self.yaw = (self.yaw + delta_yaw) & 0xFFFF
        self.pitch = FAddAngleConfined(self.pitch, delta_pitch, 192 * 0x100, 64 * 0x100)
        self.roll = FAddAngleConfined(self.roll, delta_roll, 192 * 0x100, 64 * 0x100)
        return self

    def grid_snap(self, rot_grid: "FRotator") -> "FRotator":
        import math

        return FRotator(
            int(math.floor(FSnap(self.pitch, rot_grid.pitch) + 0.5)),
            int(math.floor(FSnap(self.yaw, rot_grid.yaw) + 0.5)),
            int(math.floor(FSnap(self.roll, rot_grid.roll) + 0.5)),
        )

    def vector(self) -> FVector:
        """Convert a rotation into a vector facing in its direction."""
        return (GMath.unit_coords / self).x_axis

    @classmethod
    def from_vector(cls, v: FVector) -> "FRotator":
        return v.rotation()


def _sincos(angle: float):
    import math

    return math.sin(angle), math.cos(angle)


# Sheer axis along which sheering is performed (ESheerAxis).
SHEER_None = 0
SHEER_XY = 1
SHEER_XZ = 2
SHEER_YX = 3
SHEER_YZ = 4
SHEER_ZX = 5
SHEER_ZY = 6


class FScale:
    """Scaling and sheering info associated with a brush."""

    __slots__ = ("scale", "sheer_rate", "sheer_axis")

    def __init__(
        self,
        scale: Optional[FVector] = None,
        sheer_rate: float = 0.0,
        sheer_axis: int = SHEER_None,
    ):
        self.scale = scale if scale is not None else FVector(1.0, 1.0, 1.0)
        self.sheer_rate = sheer_rate
        self.sheer_axis = sheer_axis

    def orientation(self) -> float:
        v = self.scale.x * self.scale.y * self.scale.z
        return (v > 0.0) - (v < 0.0)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FScale):
            return (
                self.scale == other.scale
                and self.sheer_rate == other.sheer_rate
                and self.sheer_axis == other.sheer_axis
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash(
            (self.scale.x, self.scale.y, self.scale.z, self.sheer_rate, self.sheer_axis)
        )

    def __repr__(self) -> str:
        return f"FScale({self.scale}, rate={self.sheer_rate}, axis={self.sheer_axis})"


class FGlobalMath:
    """Global mathematics info with sine/cosine lookup tables."""

    def __init__(self):
        # Tables built as whole batches with numpy (~3x faster than a per-element
        # loop), then converted to lists: scalar table access is faster on lists.
        angles = np.arange(NUM_ANGLES, dtype=np.float64) * (2.0 * PI / NUM_ANGLES)
        self.trig_float = np.sin(angles).tolist()
        self.sqrt_float = np.sqrt(np.arange(NUM_SQRTS, dtype=np.float64)).tolist()
        self.light_sqrt_float = np.sqrt(np.arange(NUM_SQRTS, dtype=np.float64)).tolist()

        self.world_min = FVector(-32768.0, -32768.0, -32768.0)
        self.world_max = FVector(32767.0, 32767.0, 32767.0)
        self.unit_coords = FCoords(
            FVector(0.0, 0.0, 0.0),
            FVector(1.0, 0.0, 0.0),
            FVector(0.0, 1.0, 0.0),
            FVector(0.0, 0.0, 1.0),
        )
        self.unit_scale = FScale(FVector(1.0, 1.0, 1.0), 0.0, SHEER_None)
        self.view_coords = FCoords(
            FVector(0.0, 0.0, 0.0),
            FVector(1.0, 0.0, 0.0),
            FVector(0.0, 1.0, 0.0),
            FVector(0.0, 0.0, 1.0),
        )

    def sqrt(self, i: int) -> float:
        return self.sqrt_float[i]

    def sin_tab(self, i: int) -> float:
        return self.trig_float[(i >> ANGLE_SHIFT) & (NUM_ANGLES - 1)]

    def cos_tab(self, i: int) -> float:
        return self.trig_float[((i + 16384) >> ANGLE_SHIFT) & (NUM_ANGLES - 1)]

    def sin_float(self, f: float) -> float:
        import math

        return self.sin_tab(int(math.floor((f * 65536.0) / (2.0 * PI) + 0.5)))

    def cos_float(self, f: float) -> float:
        import math

        return self.cos_tab(int(math.floor((f * 65536.0) / (2.0 * PI) + 0.5)))


GMath = None


class FCoords:
    """A coordinate system matrix."""

    __slots__ = ("origin", "x", "y", "z")

    def __init__(
        self,
        origin: Optional[FVector] = None,
        x: Optional[FVector] = None,
        y: Optional[FVector] = None,
        z: Optional[FVector] = None,
    ):
        self.origin = origin if origin is not None else FVector(0.0, 0.0, 0.0)
        self.x = x if x is not None else FVector(1.0, 0.0, 0.0)
        self.y = y if y is not None else FVector(0.0, 1.0, 0.0)
        self.z = z if z is not None else FVector(0.0, 0.0, 1.0)

    @property
    def x_axis(self) -> FVector:
        return self.x

    @x_axis.setter
    def x_axis(self, value: FVector) -> None:
        self.x = value

    @property
    def y_axis(self) -> FVector:
        return self.y

    @y_axis.setter
    def y_axis(self, value: FVector) -> None:
        self.y = value

    @property
    def z_axis(self) -> FVector:
        return self.z

    @z_axis.setter
    def z_axis(self, value: FVector) -> None:
        self.z = value

    def transpose(self) -> "FCoords":
        return FCoords(
            -self.origin.transform_vector_by(self),
            FVector(self.x.x, self.y.x, self.z.x),
            FVector(self.x.y, self.y.y, self.z.y),
            FVector(self.x.z, self.y.z, self.z.z),
        )

    def inverse(self) -> "FCoords":
        return self.transpose()

    def mirror_by_vector(self, mirror_normal: FVector) -> "FCoords":
        return FCoords(
            self.origin.mirror_by_vector(mirror_normal),
            self.x.mirror_by_vector(mirror_normal),
            self.y.mirror_by_vector(mirror_normal),
            self.z.mirror_by_vector(mirror_normal),
        )

    def mirror_by_plane(self, plane: "FPlane") -> "FCoords":
        return FCoords(
            self.origin.mirror_by_plane(plane),
            self.x.mirror_by_vector(plane),
            self.y.mirror_by_vector(plane),
            self.z.mirror_by_vector(plane),
        )

    def ortho_rotation(self) -> "FRotator":
        return self.x.rotation()

    def __imul__(self, other) -> "FCoords":
        if isinstance(other, FCoords):
            self.origin = self.origin.transform_point_by(other)
            self.x = self.x.transform_vector_by(other)
            self.y = self.y.transform_vector_by(other)
            self.z = self.z.transform_vector_by(other)
        elif isinstance(other, FRotator):
            rot = other
            # Apply yaw rotation.
            self *= FCoords(
                FVector(0.0, 0.0, 0.0),
                FVector(+GMath.cos_tab(rot.yaw), +GMath.sin_tab(rot.yaw), 0.0),
                FVector(-GMath.sin_tab(rot.yaw), +GMath.cos_tab(rot.yaw), 0.0),
                FVector(0.0, 0.0, 1.0),
            )
            # Apply pitch rotation.
            self *= FCoords(
                FVector(0.0, 0.0, 0.0),
                FVector(+GMath.cos_tab(rot.pitch), 0.0, +GMath.sin_tab(rot.pitch)),
                FVector(0.0, 1.0, 0.0),
                FVector(-GMath.sin_tab(rot.pitch), 0.0, +GMath.cos_tab(rot.pitch)),
            )
            # Apply roll rotation.
            self *= FCoords(
                FVector(0.0, 0.0, 0.0),
                FVector(1.0, 0.0, 0.0),
                FVector(0.0, +GMath.cos_tab(rot.roll), -GMath.sin_tab(rot.roll)),
                FVector(0.0, +GMath.sin_tab(rot.roll), +GMath.cos_tab(rot.roll)),
            )
        elif isinstance(other, FVector):
            self.origin -= other
        elif isinstance(other, FScale):
            shear = FSheerSnap(other.sheer_rate)
            temp = FCoords()
            axis = other.sheer_axis
            if axis == SHEER_XY:
                temp.x.y = shear
            elif axis == SHEER_XZ:
                temp.x.z = shear
            elif axis == SHEER_YX:
                temp.y.x = shear
            elif axis == SHEER_YZ:
                temp.y.z = shear
            elif axis == SHEER_ZX:
                temp.z.x = shear
            elif axis == SHEER_ZY:
                temp.z.y = shear
            self *= temp
            # Apply scaling.
            self.x *= other.scale
            self.y *= other.scale
            self.z *= other.scale
            self.origin.x /= other.scale.x
            self.origin.y /= other.scale.y
            self.origin.z /= other.scale.z
        return self

    def __mul__(self, other) -> "FCoords":
        import copy

        result = FCoords(
            FVector(self.origin.x, self.origin.y, self.origin.z),
            FVector(self.x.x, self.x.y, self.x.z),
            FVector(self.y.x, self.y.y, self.y.z),
            FVector(self.z.x, self.z.y, self.z.z),
        )
        result *= other
        return result

    def __itruediv__(self, other) -> "FCoords":
        if isinstance(other, FRotator):
            rot = other
            # Apply inverse roll rotation.
            self *= FCoords(
                FVector(0.0, 0.0, 0.0),
                FVector(1.0, 0.0, 0.0),
                FVector(0.0, +GMath.cos_tab(rot.roll), +GMath.sin_tab(rot.roll)),
                FVector(0.0, -GMath.sin_tab(rot.roll), +GMath.cos_tab(rot.roll)),
            )
            # Apply inverse pitch rotation.
            self *= FCoords(
                FVector(0.0, 0.0, 0.0),
                FVector(+GMath.cos_tab(rot.pitch), 0.0, -GMath.sin_tab(rot.pitch)),
                FVector(0.0, 1.0, 0.0),
                FVector(+GMath.sin_tab(rot.pitch), 0.0, +GMath.cos_tab(rot.pitch)),
            )
            # Apply inverse yaw rotation.
            self *= FCoords(
                FVector(0.0, 0.0, 0.0),
                FVector(+GMath.cos_tab(rot.yaw), -GMath.sin_tab(rot.yaw), 0.0),
                FVector(+GMath.sin_tab(rot.yaw), +GMath.cos_tab(rot.yaw), 0.0),
                FVector(0.0, 0.0, 1.0),
            )
        elif isinstance(other, FVector):
            self.origin += other
        elif isinstance(other, FScale):
            # Deapply scaling.
            self.x /= other.scale
            self.y /= other.scale
            self.z /= other.scale
            self.origin.x *= other.scale.x
            self.origin.y *= other.scale.y
            self.origin.z *= other.scale.z
            # Deapply sheering.
            shear = FSheerSnap(other.sheer_rate)
            temp = FCoords()
            axis = other.sheer_axis
            if axis == SHEER_XY:
                temp.x.y = -shear
            elif axis == SHEER_XZ:
                temp.x.z = -shear
            elif axis == SHEER_YX:
                temp.y.x = -shear
            elif axis == SHEER_YZ:
                temp.y.z = -shear
            elif axis == SHEER_ZX:
                temp.z.x = -shear
            elif axis == SHEER_ZY:
                temp.z.y = -shear
            self *= temp
        return self

    def __truediv__(self, other) -> "FCoords":
        result = FCoords(
            FVector(self.origin.x, self.origin.y, self.origin.z),
            FVector(self.x.x, self.x.y, self.x.z),
            FVector(self.y.x, self.y.y, self.y.z),
            FVector(self.z.x, self.z.y, self.z.z),
        )
        result /= other
        return result

    def __repr__(self) -> str:
        return f"FCoords(origin={self.origin}, x={self.x}, y={self.y}, z={self.z})"


class FModelCoords:
    """A model coordinate system: covariant and contravariant transforms."""

    __slots__ = ("point_xform", "vector_xform")

    def __init__(
        self,
        point_xform: Optional[FCoords] = None,
        vector_xform: Optional[FCoords] = None,
    ):
        self.point_xform = point_xform if point_xform is not None else FCoords()
        self.vector_xform = vector_xform if vector_xform is not None else FCoords()

    def inverse(self) -> "FModelCoords":
        return FModelCoords(self.vector_xform.transpose(), self.point_xform.transpose())


GMath = FGlobalMath()


class FQuat:
    """Floating point quaternion (X,Y,Z,W doubles as Axis/Angle format)."""

    __slots__ = ("x", "y", "z", "w")

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __repr__(self) -> str:
        return f"FQuat(x={self.x}, y={self.y}, z={self.z}, w={self.w})"

    # Binary operators.
    def __add__(self, q: "FQuat") -> "FQuat":
        return FQuat(self.x + q.x, self.y + q.y, self.z + q.z, self.w + q.w)

    def __sub__(self, q: "FQuat") -> "FQuat":
        return FQuat(self.x - q.x, self.y - q.y, self.z - q.z, self.w - q.w)

    def __mul__(self, other) -> "FQuat":
        if isinstance(other, FQuat):
            return FQuat(
                self.x * other.x
                - self.y * other.y
                - self.z * other.z
                - self.w * other.w,
                self.x * other.y
                + self.y * other.x
                + self.z * other.w
                - self.w * other.z,
                self.x * other.z
                - self.y * other.w
                + self.z * other.x
                + self.w * other.y,
                self.x * other.w
                + self.y * other.z
                - self.z * other.y
                + self.w * other.x,
            )
        return FQuat(other * self.x, other * self.y, other * self.z, other * self.w)

    def __rmul__(self, scale: float) -> "FQuat":
        return FQuat(scale * self.x, scale * self.y, scale * self.z, scale * self.w)

    # Unary operators.
    def __neg__(self) -> "FQuat":
        return FQuat(self.x, self.y, self.z, -self.w)

    def __ne__(self, other: object) -> bool:
        if isinstance(other, FQuat):
            return (
                self.x != other.x
                or self.y != other.y
                or self.z != other.z
                or self.w != other.w
            )
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FQuat):
            return (
                self.x == other.x
                and self.y == other.y
                and self.z == other.z
                and self.w == other.w
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z, self.w))

    def size_squared(self) -> float:
        return self.x**2 + self.y**2 + self.z**2 + self.w**2

    def sizeSquared(self) -> float:
        return self.size_squared()

    def normalize(self) -> bool:
        """Normalize this quaternion in place.  Returns False (and resets) on failure."""
        square_sum = (
            self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w
        )
        if square_sum >= DELTA:
            scale = 1.0 / (square_sum**0.5)
            self.x *= scale
            self.y *= scale
            self.z *= scale
            self.w *= scale
            return True
        self.x = 0.0
        self.y = 0.0
        self.z = 0.1
        self.w = 0.0
        return False

    def quat_to_ang_axis(self) -> "FQuat":
        """Convert a normalized quaternion to angle-axis format."""
        import math

        scale = math.sin(self.w)
        a = FQuat()
        if scale >= DELTA:
            a.x = self.z / scale
            a.y = self.y / scale
            a.z = self.z / scale
            a.w = 2.0 * math.acos(self.w)
        else:
            a.x = 0.0
            a.y = 0.0
            a.z = 1.0
            a.w = 0.0
        return a

    def ang_axis_to_quat(self) -> "FQuat":
        """Convert angle-axis format to quaternion.  Axis need not be normalized."""
        import math

        scale = self.x * self.x + self.y * self.y + self.z * self.z
        q = FQuat()
        if scale >= DELTA:
            invscale = 1.0 / (scale**0.5)
            q.x = self.x * invscale
            q.y = self.y * invscale
            q.z = self.z * invscale
            q.w = math.cos(self.w * 0.5)
        else:
            q.x = 0.0
            q.y = 0.0
            q.z = 1.0
            q.w = 0.0
        return q


def FQuatDot(q1: FQuat, q2: FQuat) -> float:
    """Dot product of axes to get cos of angle."""
    return q1.x * q2.x + q1.y * q2.y + q1.z * q2.z


def FQuatError(q1: FQuat, q2: FQuat) -> float:
    """Error measure (angle) between two quaternions, ranged [0..1]."""
    import math

    cosom = q1.x * q2.x + q1.y * q2.y + q1.z * q2.z + q1.w * q2.w
    return math.acos(cosom) * (1.0 / PI) if abs(cosom) < 0.9999999 else 0.0


def AlignFQuatWith(quat1: FQuat, quat2: FQuat) -> None:
    """Ensure quat1 points to the same side of the hypersphere as quat2."""
    minus = (
        (quat1.x - quat2.x) ** 2
        + (quat1.y - quat2.y) ** 2
        + (quat1.z - quat2.z) ** 2
        + (quat1.w - quat2.w) ** 2
    )
    plus = (
        (quat1.x + quat2.x) ** 2
        + (quat1.y + quat2.y) ** 2
        + (quat1.z + quat2.z) ** 2
        + (quat1.w + quat2.w) ** 2
    )
    if minus > plus:
        quat1.x = -quat1.x
        quat1.y = -quat1.y
        quat1.z = -quat1.z
        quat1.w = -quat1.w


def SlerpQuat(quat1: FQuat, quat2: FQuat, slerp: float) -> FQuat:
    """No-frills spherical interpolation.  Assumes aligned quaternions."""
    import math

    cosom = (
        quat1.x * quat2.x + quat1.y * quat2.y + quat1.z * quat2.z + quat1.w * quat2.w
    )
    if cosom < 0.99999999:
        omega = math.acos(cosom)
        sininv = 1.0 / math.sin(omega)
        scale0 = math.sin((1.0 - slerp) * omega) * sininv
        scale1 = math.sin(slerp * omega) * sininv
        return FQuat(
            scale0 * quat1.x + scale1 * quat2.x,
            scale0 * quat1.y + scale1 * quat2.y,
            scale0 * quat1.z + scale1 * quat2.z,
            scale0 * quat1.w + scale1 * quat2.w,
        )
    return FQuat(quat1.x, quat1.y, quat1.z, quat1.w)


class FMatrix:
    """Floating point 4x4 (4x3) matrix.  Each plane is a *column* of the matrix."""

    __slots__ = ("m",)

    def __init__(
        self,
        x_plane: Optional[FPlane] = None,
        y_plane: Optional[FPlane] = None,
        z_plane: Optional[FPlane] = None,
        w_plane: Optional[FPlane] = None,
    ):
        self.m = [[0.0] * 4 for _ in range(4)]
        if x_plane is None and y_plane is None and z_plane is None and w_plane is None:
            for i in range(4):
                self.m[i][i] = 1.0
            return
        xp = x_plane if x_plane is not None else FPlane(0, 0, 0, 0)
        yp = y_plane if y_plane is not None else FPlane(0, 0, 0, 0)
        zp = z_plane if z_plane is not None else FPlane(0, 0, 0, 0)
        wp = w_plane if w_plane is not None else FPlane(0, 0, 0, 0)
        self.m[0] = [xp.x, xp.y, xp.z, xp.w]
        self.m[1] = [yp.x, yp.y, yp.z, yp.w]
        self.m[2] = [zp.x, zp.y, zp.z, zp.w]
        self.m[3] = [wp.x, wp.y, wp.z, wp.w]

    def M(self, i: int, j: int) -> float:
        return self.m[i][j]

    def transform_fvector(self, v: FVector) -> FVector:
        m = self.m
        return FVector(
            v.x * m[0][0] + v.y * m[0][1] + v.z * m[0][2] + m[0][3],
            v.x * m[1][0] + v.y * m[1][1] + v.z * m[1][2] + m[1][3],
            v.x * m[2][0] + v.y * m[2][1] + v.z * m[2][2] + m[2][3],
        )

    def transform_fplane(self, p: FPlane) -> FPlane:
        m = self.m
        return FPlane(
            p.x * m[0][0] + p.y * m[0][1] + p.z * m[0][2] + m[0][3],
            p.x * m[1][0] + p.y * m[1][1] + p.z * m[1][2] + m[1][3],
            p.x * m[2][0] + p.y * m[2][1] + p.z * m[2][2] + m[2][3],
            p.x * m[3][0] + p.y * m[3][1] + p.z * m[3][2] + m[3][3],
        )

    @classmethod
    def from_fcoords(cls, fc: FCoords) -> "FMatrix":
        return cls(
            FPlane(fc.x.x, fc.x.y, fc.x.z, fc.origin.x),
            FPlane(fc.y.x, fc.y.y, fc.y.z, fc.origin.y),
            FPlane(fc.z.x, fc.z.y, fc.z.z, fc.origin.z),
            FPlane(0.0, 0.0, 0.0, 1.0),
        )

    def to_fcoords(self) -> FCoords:
        return FCoords(
            FVector(self.m[0][3], self.m[1][3], self.m[2][3]),
            FVector(self.m[0][0], self.m[0][1], self.m[0][2]),
            FVector(self.m[1][0], self.m[1][1], self.m[1][2]),
            FVector(self.m[2][0], self.m[2][1], self.m[2][2]),
        )

    def __repr__(self) -> str:
        lines = []
        for row in self.m:
            lines.append(f"  [{row[0]:8.4f} {row[1]:8.4f} {row[2]:8.4f} {row[3]:8.4f}]")
        return "FMatrix(\n" + "\n".join(lines) + "\n)"


def CombineTransforms(m: FMatrix, n: FMatrix) -> FMatrix:
    """Combine two 4x4 transforms (M x N)."""
    result = FMatrix()
    for i in range(4):
        for j in range(4):
            result.m[i][j] = (
                m.m[i][0] * n.m[0][j]
                + m.m[i][1] * n.m[1][j]
                + m.m[i][2] * n.m[2][j]
                + m.m[i][3] * n.m[3][j]
            )
    return result


class TArray(MutableSequence[T]):
    __slots__ = ("_data",)

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


KT = TypeVar("KT")
VT = TypeVar("VT")


class TMap(Generic[KT, VT]):
    __slots__ = ("_data",)

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
            return (
                self.a == other.a
                and self.b == other.b
                and self.c == other.c
                and self.d == other.d
            )
        return False

    def __hash__(self) -> int:
        return hash((self.a, self.b, self.c, self.d))


class FCompactIndex:
    """Compactly encoded 32-bit signed index.

    Declared in Core/Inc/UnArc.h:216; the implementation lives in the prebuilt
    Core.lib. Ported from the disassembled serializer in Help/PACKAGES.md
    ("Compact Indices"): B0 holds the sign in 0x80 and a "more bytes follow"
    marker in 0x40 plus the low 6 bits, followed by up to four 7-bit bytes.
    """

    def __init__(self, value: int = 0):
        self.value = value

    def encode(self) -> bytes:
        """Write path of operator<<(FArchive&, FCompactIndex&)."""
        original = self.value
        v = abs(self.value)
        b0 = (0 if self.value >= 0 else 0x80) + (v if v < 0x40 else (v & 0x3F) + 0x40)
        out = bytearray([b0 & 0xFF])
        if b0 & 0x40:
            v >>= 6
            b1 = v if v < 0x80 else (v & 0x7F) + 0x80
            out.append(b1 & 0xFF)
            if b1 & 0x80:
                v >>= 7
                b2 = v if v < 0x80 else (v & 0x7F) + 0x80
                out.append(b2 & 0xFF)
                if b2 & 0x80:
                    v >>= 7
                    b3 = v if v < 0x80 else (v & 0x7F) + 0x80
                    out.append(b3 & 0xFF)
                    if b3 & 0x80:
                        v >>= 7
                        out.append(v & 0xFF)
        # The C++ serializer appErrorf()s when saving changes the value; do the
        # same so an unrepresentable index can't be written out silently.
        if FCompactIndex.decode(bytes(out))[0].value != original:
            raise ValueError(f"FCompactIndex: {original} does not survive encoding")
        return bytes(out)

    @staticmethod
    def decode(data: bytes, offset: int = 0) -> tuple["FCompactIndex", int]:
        """Read path of operator<<(FArchive&, FCompactIndex&).

        Returns the index and the offset just past it. The reconstructed value
        wraps to a signed 32-bit int, as the C++ INT does.
        """
        pos = offset
        b0 = data[pos]
        pos += 1
        value = 0
        if b0 & 0x40:
            b1 = data[pos]
            pos += 1
            if b1 & 0x80:
                b2 = data[pos]
                pos += 1
                if b2 & 0x80:
                    b3 = data[pos]
                    pos += 1
                    if b3 & 0x80:
                        value = data[pos]
                        pos += 1
                    value = (value << 7) + (b3 & 0x7F)
                value = (value << 7) + (b2 & 0x7F)
            value = (value << 7) + (b1 & 0x7F)
        value = (value << 6) + (b0 & 0x3F)
        if b0 & 0x80:
            value = -value
        value &= 0xFFFFFFFF
        if value >= 0x80000000:
            value -= 0x100000000
        return FCompactIndex(value), pos

    def __repr__(self) -> str:
        return f"FCompactIndex({self.value})"


class FBox:
    def __init__(
        self,
        min: Optional[FVector] = None,
        max: Optional[FVector] = None,
        is_valid: int = 0,
    ):
        self.min = min if min else FVector(0, 0, 0)
        self.max = max if max else FVector(0, 0, 0)
        self.is_valid = 1 if (min is not None and max is not None) else is_valid

    def init(self) -> None:
        self.is_valid = 0

    def get_center(self) -> FVector:
        return (self.min + self.max) * 0.5

    def get_extent(self) -> FVector:
        return self.max - self.min

    def get_extrema(self, i: int) -> FVector:
        return self.min if i == 0 else self.max

    def is_valid_box(self) -> bool:
        return self.is_valid != 0

    def is_inside(self, point: FVector) -> bool:
        if not self.is_valid_box():
            return False
        return (
            point.x >= self.min.x
            and point.x <= self.max.x
            and point.y >= self.min.y
            and point.y <= self.max.y
            and point.z >= self.min.z
            and point.z <= self.max.z
        )

    def __iadd__(self, other) -> "FBox":
        if isinstance(other, FVector):
            if self.is_valid:
                self.min = FVector(
                    min(self.min.x, other.x),
                    min(self.min.y, other.y),
                    min(self.min.z, other.z),
                )
                self.max = FVector(
                    max(self.max.x, other.x),
                    max(self.max.y, other.y),
                    max(self.max.z, other.z),
                )
            else:
                self.min = FVector(other.x, other.y, other.z)
                self.max = FVector(other.x, other.y, other.z)
                self.is_valid = 1
        elif isinstance(other, FBox):
            if self.is_valid and other.is_valid:
                self.min = FVector(
                    min(self.min.x, other.min.x),
                    min(self.min.y, other.min.y),
                    min(self.min.z, other.min.z),
                )
                self.max = FVector(
                    max(self.max.x, other.max.x),
                    max(self.max.y, other.max.y),
                    max(self.max.z, other.max.z),
                )
            else:
                self.min = FVector(other.min.x, other.min.y, other.min.z)
                self.max = FVector(other.max.x, other.max.y, other.max.z)
                self.is_valid = other.is_valid
        return self

    def __add__(self, other) -> "FBox":
        result = FBox(
            FVector(self.min.x, self.min.y, self.min.z),
            FVector(self.max.x, self.max.y, self.max.z),
            self.is_valid,
        )
        result += other
        return result

    def transform_by(self, coords: FCoords) -> "FBox":
        new_box = FBox(None, None, 0)
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    new_box += FVector(
                        self.get_extrema(i).x,
                        self.get_extrema(j).y,
                        self.get_extrema(k).z,
                    ).transform_point_by(coords)
        return new_box

    def expand_by(self, w: float) -> "FBox":
        return FBox(self.min - FVector(w, w, w), self.max + FVector(w, w, w))

    def __repr__(self) -> str:
        return f"FBox({self.min}, {self.max}, valid={self.is_valid})"


class FSphere(FPlane):
    """A sphere, stored as a plane whose (X,Y,Z) is the center and W is the radius."""

    def __init__(self, center: Optional[FVector] = None, w: float = 0.0):
        c = center if center is not None else FVector(0.0, 0.0, 0.0)
        super().__init__(c.x, c.y, c.z, w)

    @property
    def center(self) -> FVector:
        return FVector(self.x, self.y, self.z)

    @property
    def radius(self) -> float:
        return self.w

    def get_center(self) -> FVector:
        return FVector(self.x, self.y, self.z)

    def get_radius(self) -> float:
        return self.w

    def is_valid_sphere(self) -> bool:
        return self.w > 0.0

    @classmethod
    def from_vectors(cls, points: Iterable[FVector]) -> "FSphere":
        """Compute a bounding sphere for a set of points.

        Note: the C++ FSphere(Pts,Count) body ships only in Core.lib, so this
        uses centroid + max distance (whole-batch numpy) rather than the exact
        engine algorithm.
        """
        arr = np.array([[p.x, p.y, p.z] for p in points], dtype=np.float64)
        if arr.size == 0:
            return cls(FVector(0.0, 0.0, 0.0), 0.0)
        center = arr.mean(axis=0)
        radius = float(np.sqrt(((arr - center) ** 2).sum(axis=1).max()))
        return cls(FVector(center[0], center[1], center[2]), radius)

    def __repr__(self) -> str:
        return f"FSphere({self.center}, {self.w})"


def FDist(v1: FVector, v2: FVector) -> float:
    """Euclidean distance between two points."""
    return ((v2.x - v1.x) ** 2 + (v2.y - v1.y) ** 2 + (v2.z - v1.z) ** 2) ** 0.5


def FDistSquared(v1: FVector, v2: FVector) -> float:
    """Squared distance between two points."""
    return (v2.x - v1.x) ** 2 + (v2.y - v1.y) ** 2 + (v2.z - v1.z) ** 2


def FPointsAreSame(p: FVector, q: FVector) -> int:
    """Compare two points using a threshold.  Uses a fast distance approximation."""
    temp = p.x - q.x
    if (-THRESH_POINTS_ARE_SAME) < temp < THRESH_POINTS_ARE_SAME:
        temp = p.y - q.y
        if (-THRESH_POINTS_ARE_SAME) < temp < THRESH_POINTS_ARE_SAME:
            temp = p.z - q.z
            if (-THRESH_POINTS_ARE_SAME) < temp < THRESH_POINTS_ARE_SAME:
                return 1
    return 0


def FPointsAreNear(point1: FVector, point2: FVector, dist: float) -> int:
    if abs(point1.x - point2.x) >= dist:
        return 0
    if abs(point1.y - point2.y) >= dist:
        return 0
    if abs(point1.z - point2.z) >= dist:
        return 0
    return 1


def FPointPlaneDist(
    point: FVector, plane_base: FVector, plane_normal: FVector
) -> float:
    """Signed distance (in the direction of the normal) between a point and a plane."""
    return (point - plane_base) | plane_normal


def FParallel(normal1: FVector, normal2: FVector) -> int:
    """See if two normal vectors (or plane normals) are nearly parallel."""
    normal_dot = normal1 | normal2
    return 1 if abs(normal_dot - 1.0) <= THRESH_VECTORS_ARE_PARALLEL else 0


def FCoplanar(
    base1: FVector, normal1: FVector, base2: FVector, normal2: FVector
) -> int:
    """See if two planes are coplanar."""
    if not FParallel(normal1, normal2):
        return 0
    if FPointPlaneDist(base2, base1, normal1) > THRESH_POINT_ON_PLANE:
        return 0
    return 1


def FTriple(x: FVector, y: FVector, z: FVector) -> float:
    """Triple product of three vectors."""
    return (
        x.x * (y.y * z.z - y.z * z.y)
        + x.y * (y.z * z.x - y.x * z.z)
        + x.z * (y.x * z.y - y.y * z.x)
    )


def FLinePlaneIntersection(
    point1: FVector, point2: FVector, plane_origin: FVector, plane_normal: FVector
) -> FVector:
    """Intersection of an infinite line (two points) and a plane (origin+normal)."""
    return point1 + (point2 - point1) * (
        ((plane_origin - point1) | plane_normal) / ((point2 - point1) | plane_normal)
    )


def FLinePlaneIntersectionPlane(
    point1: FVector, point2: FVector, plane: FPlane
) -> FVector:
    """Intersection of an infinite line (two points) and an FPlane."""
    return point1 + (point2 - point1) * (
        (plane.w - (point1 | plane)) / ((point2 - point1) | plane)
    )


def FIntersectPlanes3(p1: FPlane, p2: FPlane, p3: FPlane) -> tuple:
    """Compute intersection point of three planes.  Returns (valid, point)."""
    det = (p1 ^ p2) | p3
    if det * det < 0.001 * 0.001:
        return False, FVector(0.0, 0.0, 0.0)
    return True, (p1.w * (p2 ^ p3) + p2.w * (p3 ^ p1) + p3.w * (p1 ^ p2)) / det


def FIntersectPlanes2(p1: FPlane, p2: FPlane) -> tuple:
    """Compute intersection point and direction of the line joining two planes.

    Returns (valid, point, direction).
    """
    direction = p1 ^ p2
    dd = direction.size_squared()
    if dd < 0.001 * 0.001:
        return False, FVector(0.0, 0.0, 0.0), FVector(0.0, 0.0, 0.0)
    point = (p1.w * (p2 ^ direction) + p2.w * (direction ^ p1)) / dd
    direction = direction.normalize()
    return True, point, direction


def FBoxPushOut(normal: FVector, size: FVector) -> float:
    """Compute the pushout of a box from a plane."""
    return abs(normal.x * size.x) + abs(normal.y * size.y) + abs(normal.z * size.z)


def VRand() -> FVector:
    """Return a uniformly distributed random unit vector."""
    import random

    while True:
        result = FVector(
            random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1
        )
        if result.size_squared() <= 1.0:
            return result.unsafe_normal()


def RandomSpreadVector(spread_degrees: float) -> FVector:
    """Return a random unit vector within a cone of spread_degrees (no bunching near axis)."""
    import math
    import random

    max_pitch = max(0.0, min(spread_degrees * (PI / 180.0 / 2.0), 180.0))
    k = 1.0 - math.cos(max_pitch)
    pitch = math.acos(max(0.0, min(1.0, 1.0 - random.random() * k)))
    rand_roll = random.random() * (2.0 * PI)
    radius = math.sin(pitch)
    return FVector(
        math.cos(pitch), radius * math.sin(rand_roll), radius * math.cos(rand_roll)
    )
