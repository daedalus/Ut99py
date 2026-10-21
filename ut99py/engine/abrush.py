"""Port of Engine/Inc/ABrush.h (0 declared symbols).

ABrush: the class-body fragment included from EngineClasses.h. ToLocal(),
ToWorld(), BuildCoords() and CopyPosRotScaleFrom() have inline bodies;
PostLoad() and InitPosRotScale() live in Engine.lib.
"""

from __future__ import annotations
from typing import Any, Optional
from ..core import FCoords, FModelCoords, FScale, FVector, FRotator, GMath
from .actor import AActor


class ABrush(AActor):
    """ABrush (ABrush.h + EngineClasses.h:1872)."""

    def __init__(self) -> None:
        super().__init__()
        # Transform attributes of the brush (EngineClasses.h ABrush).
        self.Location: FVector = FVector()
        self.Rotation: FRotator = FRotator()
        self.PrePivot: FVector = FVector()
        self.MainScale: FScale = FScale()
        self.PostScale: FScale = FScale()
        self.Brush: Optional[Any] = None  # UModel*

    def PostLoad(self) -> None:
        raise NotImplementedError("C++ ABrush::PostLoad: Engine.lib")

    def ToLocal(self) -> FCoords:
        """ABrush::ToLocal (ABrush.h:19-23) - inline body."""
        return (
            GMath.unit_coords
            / -self.PrePivot
            / self.MainScale
            / self.Rotation
            / self.PostScale
            / self.Location
        )

    def ToWorld(self) -> FCoords:
        """ABrush::ToWorld (ABrush.h:24-28) - inline body."""
        return (
            GMath.unit_coords
            * self.Location
            * self.PostScale
            * self.Rotation
            * self.MainScale
            * -self.PrePivot
        )

    def BuildCoords(
        self, Coords: Optional[FModelCoords], Uncoords: Optional[FModelCoords]
    ) -> float:
        """ABrush::BuildCoords (ABrush.h:29-45) - inline body."""
        if Coords is not None:
            Coords.point_xform = (
                GMath.unit_coords * self.PostScale * self.Rotation * self.MainScale
            )
            Coords.vector_xform = (
                GMath.unit_coords / self.MainScale / self.Rotation / self.PostScale
            ).transpose()
        if Uncoords is not None:
            Uncoords.point_xform = (
                GMath.unit_coords / self.MainScale / self.Rotation / self.PostScale
            )
            Uncoords.vector_xform = (
                GMath.unit_coords * self.PostScale * self.Rotation * self.MainScale
            ).transpose()
        return self.MainScale.orientation() * self.PostScale.orientation()

    def CopyPosRotScaleFrom(self, Other: "ABrush") -> None:
        """ABrush::CopyPosRotScaleFrom (ABrush.h:46-62) - inline body."""
        # The C++ uses check() here, which aborts on a null brush.
        if self.Brush is None:
            raise ValueError("ABrush::CopyPosRotScaleFrom: Brush is null")
        if Other is None or Other.Brush is None:
            raise ValueError(
                "ABrush::CopyPosRotScaleFrom: Other or Other->Brush is null"
            )
        self.Location = Other.Location
        self.Rotation = Other.Rotation
        self.PrePivot = Other.PrePivot
        self.MainScale = Other.MainScale
        self.PostScale = Other.PostScale
        self.Brush.BuildBound()

    def InitPosRotScale(self) -> None:
        raise NotImplementedError("C++ ABrush::InitPosRotScale: Engine.lib")


__all__ = ["ABrush"]
