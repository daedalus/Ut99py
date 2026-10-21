"""Tests for Engine/Inc/ABrush.h port (engine/abrush.py)."""

import pytest

from ut99py.core import FModelCoords, FScale, FVector, FRotator, GMath
from ut99py.engine.abrush import ABrush
from ut99py.engine.actor import AActor


class StubModel:
    """Stand-in for the UModel the brush points at."""

    def __init__(self):
        self.bounds_built = 0

    def BuildBound(self):
        self.bounds_built += 1


def test_abrush_base_chain_matches_engine_classes():
    # EngineClasses.h:1872 - class ABrush : public AActor
    assert issubclass(ABrush, AActor)


def test_abrush_defaults():
    brush = ABrush()
    assert brush.Location == FVector(0.0, 0.0, 0.0)
    assert brush.Rotation == FRotator()
    assert brush.PrePivot == FVector(0.0, 0.0, 0.0)
    assert brush.MainScale == FScale()
    assert brush.PostScale == FScale()
    assert brush.Brush is None


def test_to_local_and_to_world_of_an_identity_brush():
    brush = ABrush()
    local = brush.ToLocal()
    world = brush.ToWorld()
    for coords in (local, world):
        assert coords.origin == FVector(0.0, 0.0, 0.0)
        assert coords.x == FVector(1.0, 0.0, 0.0)
        assert coords.y == FVector(0.0, 1.0, 0.0)
        assert coords.z == FVector(0.0, 0.0, 1.0)


def test_to_local_and_to_world_move_by_the_location():
    brush = ABrush()
    brush.Location = FVector(10.0, 20.0, 30.0)
    # FCoords / FVector adds the point to the origin, FCoords * FVector
    # subtracts it (UnMath.h).
    assert brush.ToLocal().origin == FVector(10.0, 20.0, 30.0)
    assert brush.ToWorld().origin == FVector(-10.0, -20.0, -30.0)


def test_build_coords_fills_both_transforms():
    brush = ABrush()
    brush.PostScale = FScale(FVector(2.0, 2.0, 2.0))
    brush.MainScale = FScale(FVector(4.0, 4.0, 4.0))
    coords = FModelCoords()
    uncoords = FModelCoords()

    orientation = brush.BuildCoords(coords, uncoords)

    # MainScale.Orientation() * PostScale.Orientation()
    assert orientation == 1.0

    expected_point = (
        GMath.unit_coords * brush.PostScale * brush.Rotation * brush.MainScale
    )
    assert coords.point_xform.origin == expected_point.origin
    assert coords.point_xform.x == expected_point.x

    expected_unpoint = (
        GMath.unit_coords / brush.MainScale / brush.Rotation / brush.PostScale
    )
    assert uncoords.point_xform.origin == expected_unpoint.origin
    assert coords.vector_xform.origin == expected_unpoint.transpose().origin
    assert uncoords.vector_xform.origin == expected_point.transpose().origin


def test_build_coords_accepts_null_transforms():
    brush = ABrush()
    assert brush.BuildCoords(None, None) == 1.0


def test_copy_pos_rot_scale_from_copies_the_transform():
    source = ABrush()
    source.Location = FVector(1.0, 2.0, 3.0)
    source.PrePivot = FVector(4.0, 5.0, 6.0)
    source.MainScale = FScale(FVector(2.0, 2.0, 2.0))
    source.PostScale = FScale(FVector(3.0, 3.0, 3.0))
    source.Brush = StubModel()

    target = ABrush()
    target.Brush = StubModel()
    target.CopyPosRotScaleFrom(source)

    assert target.Location == source.Location
    assert target.Rotation == source.Rotation
    assert target.PrePivot == source.PrePivot
    assert target.MainScale == source.MainScale
    assert target.PostScale == source.PostScale
    assert target.Brush.bounds_built == 1


def test_copy_pos_rot_scale_from_rejects_a_null_brush():
    source = ABrush()
    source.Brush = StubModel()
    with pytest.raises(ValueError):
        ABrush().CopyPosRotScaleFrom(source)


def test_lib_bodies_raise():
    brush = ABrush()
    with pytest.raises(NotImplementedError):
        brush.PostLoad()
    with pytest.raises(NotImplementedError):
        brush.InitPosRotScale()
