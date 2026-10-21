"""Port of Engine/Inc/UnModel.h (5 declared symbols).

UModel (UPrimitive) + UBspNodes, UBspSurfs, UVectors, UVerts.
Uses FBspNode/FBspSurf/FLeaf/FBox/FZoneProperties/UPolys/FVert from
engine/un_obj.py (UnObj.h). Inline serializers match UnObj.h patterns.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core.types import FBox, FVector
from ..engine.un_obj import (
    FBspNode, FBspSurf, FLeaf, FVert, FZoneProperties,
    UPolys, FLightMapIndex, EBspNodeFlags,
)
from ..engine.prim import UPrimitive
from ..core import UObject

MAX_NODES: int = 65536
MAX_POINTS: int = 128000


class UModel(UPrimitive):
    """UModel (UnModel.h)."""

    def __init__(self) -> None:
        super().__init__()
        self.Polys: Optional[Any] = None  # UPolys*
        self.Nodes: list = []  # TTransArray<FBspNode>
        self.Verts: list = []  # TTransArray<FVert>
        self.Vectors: list = []  # TArray<FVector>
        self.Points: list = []  # TArray<FVector>
        self.Surfs: list = []  # TTransArray<FBspSurf>
        self.LightMap: list = []  # TArray<FLightMapIndex>
        self.LightBits: list = []  # TArray<BYTE>
        self.Bounds: list = []  # TArray<FBox>
        self.LeafHulls: list = []  # TArray<INT>
        self.Leaves: list = []  # TArray<FLeaf>
        self.Lights: list = []  # TArray<AActor*>
        self.RootOutside: bool = True
        self.Linked: bool = False
        self.MoverLink: int = 0
        self.NumSharedSides: int = 0
        self.NumZones: int = 0
        self.Zones = [FZoneProperties() for _ in range(FBspNode.MAX_ZONES)]

    def serialize(self, ar: Any) -> "UModel":
        """UModel::Serialize (UnModel.cpp:253).

        The arrays come first, then the shared side and zone counts, the
        zones, the brush polys, the lighting data and the two flags. The
        pre-62 layout kept the arrays in separate objects; the port reads
        the version 62+ layout only.
        """
        super().serialize(ar)
        if ar.ver() <= 61:
            raise NotImplementedError(
                "UModel::Serialize: the pre-62 layout stores the arrays in "
                "separate UBspSurfs/UVectors/UVerts objects"
            )
        self.Vectors = self._read_array(ar, FVector)
        self.Points = self._read_array(ar, FVector)
        self.Nodes = self._read_array(ar, FBspNode)
        self.Surfs = self._read_array(ar, FBspSurf)
        self.Verts = self._read_array(ar, FVert)
        self.NumSharedSides = ar.serialize_int32(self.NumSharedSides)
        self.NumZones = ar.serialize_int32(self.NumZones)
        for i in range(self.NumZones):
            self.Zones[i].serialize(ar)
        self.Polys = ar.serialize_object(self.Polys)
        # The C++ calls Ar.Preload(Polys) after the reference so the brush
        # list's data is loaded, not just the index (UnModel.cpp:304-307).
        if self.Polys is not None and not ar.is_trans():
            if hasattr(ar, "preload"):
                ar.preload(self.Polys)
        self.LightMap = self._read_array(ar, FLightMapIndex)
        self.LightBits = self._read_array(ar, int, element_size=1)
        self.Bounds = self._read_array(ar, FBox)
        self.LeafHulls = self._read_array(ar, int)
        self.Leaves = self._read_array(ar, FLeaf)
        self.Lights = self._read_array(ar, UObject)
        self.RootOutside = ar.serialize_int32(self.RootOutside)
        self.Linked = ar.serialize_int32(self.Linked)
        return self

    @staticmethod
    def _read_array(ar: Any, element: type, element_size: Optional[int] = None) -> list:
        """A TArray read with the count as a compact index (UnTemplate.h:435)."""
        from ..core.types import TArray

        array = TArray()
        ar.serialize_tarray(array, element=element, element_size=element_size)
        return list(array)

    def PostLoad(self) -> None:
        raise NotImplementedError("C++ UModel::PostLoad: Engine.lib")

    def Modify(self, DoTransArrays: bool = False) -> None:
        raise NotImplementedError("C++ UModel::Modify: Engine.lib")

    def BuildBound(self) -> None:
        raise NotImplementedError("C++ UModel::BuildBound: Engine.lib")

    def Transform(self, Owner: Any) -> None:
        raise NotImplementedError("C++ UModel::Transform: Engine.lib")

    def EmptyModel(self, EmptySurfInfo: int, EmptyPolys: int) -> None:
        raise NotImplementedError("C++ UModel::EmptyModel: Engine.lib")

    def ShrinkModel(self) -> None:
        raise NotImplementedError("C++ UModel::ShrinkModel: Engine.lib")

    def PotentiallyVisible(self, iLeaf1: int, iLeaf2: int) -> bool:
        raise NotImplementedError("C++ UModel::PotentiallyVisible: Engine.lib")

    def FastLineCheck(self, End: Any, Start: Any) -> int:
        raise NotImplementedError("C++ UModel::FastLineCheck: Engine.lib")

    def PointCheck(self, Result: Any, Owner: Any, Location: Any, Extent: Any, ExtraNodeFlags: int) -> bool:
        raise NotImplementedError("C++ UModel::PointCheck: Engine.lib")

    def LineCheck(self, Result: Any, Owner: Any, End: Any, Start: Any, Extent: Any, ExtraNodeFlags: int) -> bool:
        raise NotImplementedError("C++ UModel::LineCheck: Engine.lib")

    def GetCollisionBoundingBox(self, Owner: Any) -> Any:
        raise NotImplementedError("C++ UModel::GetCollisionBoundingBox: Engine.lib")

    def GetRenderBoundingBox(self, Owner: Any, Exact: bool) -> Any:
        raise NotImplementedError("C++ UModel::GetRenderBoundingBox: Engine.lib")

    def ModifySelectedSurfs(self, UpdateMaster: bool) -> None:
        raise NotImplementedError("C++ UModel::ModifySelectedSurfs: Engine.lib")

    def ModifyAllSurfs(self, UpdateMaster: bool) -> None:
        raise NotImplementedError("C++ UModel::ModifyAllSurfs: Engine.lib")

    def ModifySurf(self, Index: int, UpdateMaster: bool) -> None:
        raise NotImplementedError("C++ UModel::ModifySurf: Engine.lib")

    def GetLightMapIndex(self, iSurf: int) -> Optional[Any]:
        # UnModel.h inline (line 119): guard + return pointer or NULL.
        if iSurf < 0:
            return None
        # Simplified: body in Engine.lib; port returns stub.
        raise NotImplementedError("C++ UModel::GetLightMapIndex inline: Engine.lib")


class UBspSurfs(UObject):
    """UnModel.h:157-180"""

    def __init__(self) -> None:
        super().__init__()
        self.Element: list = []  # TArray<FBspSurf>

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UBspSurfs::Serialize: Engine.lib")


class UBspNodes(UObject):
    """UnModel.h:74-103"""

    def __init__(self) -> None:
        super().__init__()
        self.Element: list = []  # TTransArray<FBspNode>
        self._NumZones: int = 0
        self._Zones = [FZoneProperties() for _ in range(FBspNode.MAX_ZONES)]

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UBspNodes::Serialize: Engine.lib")


class UVectors(UObject):
    """UnModel.h:182-200"""

    def __init__(self) -> None:
        super().__init__()
        self.Element: list = []  # TArray<FVector>

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UVectors::Serialize: Engine.lib")


class UVerts(UObject):
    """UnModel.h:202-234"""

    def __init__(self) -> None:
        super().__init__()
        self.Element: list = []  # TArray<FVert>
        self.NumSharedSides: int = 0

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UVerts::Serialize: Engine.lib")


__all__ = ["UModel", "UBspNodes", "UBspSurfs", "UVectors", "UVerts",
           "MAX_NODES", "MAX_POINTS"]
