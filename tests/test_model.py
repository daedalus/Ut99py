"""Tests for Engine/Inc/UnModel.h port (graphics/model.py)."""

import pytest

from ut99py.graphics.model import (
    UModel, UBspNodes, UBspSurfs, UVectors, UVerts,
    MAX_NODES, MAX_POINTS,
)


def test_constants():
    assert MAX_NODES == 65536
    assert MAX_POINTS == 128000


def test_model_default():
    model = UModel()
    assert model.RootOutside is True
    assert model.Linked is False
    assert model.MoverLink == 0
    assert model.NumSharedSides == 0
    assert model.NumZones == 0
    # UnModel.h:53: FZoneProperties Zones[FBspNode::MAX_ZONES].
    assert len(model.Zones) == 64
    assert model.Polys is None
    assert model.Nodes == []
    assert model.Verts == []
    assert model.Vectors == []
    assert model.Points == []
    assert model.Surfs == []
    assert model.LightMap == []
    assert model.LightBits == []
    assert model.Bounds == []
    assert model.LeafHulls == []
    assert model.Leaves == []
    assert model.Lights == []


def test_model_lib_bodies_raise():
    model = UModel()
    with pytest.raises(NotImplementedError):
        model.Serialize(None)
    with pytest.raises(NotImplementedError):
        model.PostLoad()
    with pytest.raises(NotImplementedError):
        model.Modify()
    with pytest.raises(NotImplementedError):
        model.BuildBound()
    with pytest.raises(NotImplementedError):
        model.Transform(None)
    with pytest.raises(NotImplementedError):
        model.EmptyModel(1, 0)
    with pytest.raises(NotImplementedError):
        model.ShrinkModel()
    with pytest.raises(NotImplementedError):
        model.PotentiallyVisible(1, 2)
    with pytest.raises(NotImplementedError):
        model.FastLineCheck(None, None)
    with pytest.raises(NotImplementedError):
        model.PointCheck(None, None, None, None, 0)
    with pytest.raises(NotImplementedError):
        model.LineCheck(None, None, None, None, None, 0)
    with pytest.raises(NotImplementedError):
        model.GetCollisionBoundingBox(None)
    with pytest.raises(NotImplementedError):
        model.GetRenderBoundingBox(None, True)
    with pytest.raises(NotImplementedError):
        model.ModifySelectedSurfs(True)
    with pytest.raises(NotImplementedError):
        model.ModifyAllSurfs(True)
    with pytest.raises(NotImplementedError):
        model.ModifySurf(1, True)
    # Inline GetLightMapIndex: body in Engine.lib.
    with pytest.raises(NotImplementedError):
        model.GetLightMapIndex(1)


def test_sub_objects():
    nodes = UBspNodes()
    assert len(nodes.Element) == 0
    surfs = UBspSurfs()
    assert len(surfs.Element) == 0
    vecs = UVectors()
    assert len(vecs.Element) == 0
    verts = UVerts()
    assert len(verts.Element) == 0
    assert verts.NumSharedSides == 0
