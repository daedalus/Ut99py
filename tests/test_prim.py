"""Tests for Engine/Inc/UnPrim.h port (engine/prim.py)."""

import pytest

from ut99py.engine.prim import (
    UPrimitive,
    FCheckResult,
    FIteratorActorList,
)


def test_iterator_actor_list():
    # UnPrim.h:36-45: FIteratorActorList has Actor and GetNext.
    it = FIteratorActorList()
    assert it.Actor is None
    assert it.GetNext() is None

    actor = object()
    it2 = FIteratorActorList(None, actor)
    assert it2.Actor is actor


def test_check_result_defaults():
    # UnPrim.h:47-77: FCheckResult fields.
    res = FCheckResult()
    assert res.Location.x == 0.0
    assert res.Normal.x == 0.0
    assert res.Primitive is None
    assert res.Time == 0.0
    assert res.Item == -1  # INDEX_NONE


def test_check_result_with_time():
    # UnPrim.h:66-74: FCheckResult(InTime, InNext=NULL).
    res = FCheckResult(1.5)
    assert res.Time == 1.5
    assert res.Item == -1
    assert res.Primitive is None


def test_primitive_defaults():
    # UnPrim.h:79-111: UPrimitive has BoundingBox and BoundingSphere.
    prim = UPrimitive()
    assert prim.BoundingBox is not None
    assert prim.BoundingSphere is not None


def test_primitive_lib_bodies_raise():
    prim = UPrimitive()
    with pytest.raises(NotImplementedError):
        prim.Serialize(None)
    with pytest.raises(NotImplementedError):
        prim.PointCheck(None, None, None, None, 0)
    with pytest.raises(NotImplementedError):
        prim.LineCheck(None, None, None, None, None, 0)
    with pytest.raises(NotImplementedError):
        prim.GetRenderBoundingBox(None, True)
    with pytest.raises(NotImplementedError):
        prim.GetRenderBoundingSphere(None, True)
    with pytest.raises(NotImplementedError):
        prim.GetCollisionBoundingBox(None)
