"""Tests for Engine/Inc/AMover.h port (engine/amover.py)."""

import pytest

from ut99py.engine.abrush import ABrush
from ut99py.engine.amover import AMover


def test_amover_base_chain_matches_engine_classes():
    # EngineClasses.h:1910 - class AMover : public ABrush
    assert issubclass(AMover, ABrush)


def test_amover_constructor_is_in_engine_lib():
    with pytest.raises(NotImplementedError):
        AMover()


def test_lib_bodies_raise():
    mover = AMover.__new__(AMover)
    with pytest.raises(NotImplementedError):
        mover.PostLoad()
    with pytest.raises(NotImplementedError):
        mover.PostEditChange()
    with pytest.raises(NotImplementedError):
        mover.Spawned()
    with pytest.raises(NotImplementedError):
        mover.PostEditMove()
    with pytest.raises(NotImplementedError):
        mover.PreRaytrace()
    with pytest.raises(NotImplementedError):
        mover.PostRaytrace()
    with pytest.raises(NotImplementedError):
        mover.GetOptimizedRepList(None, None, None, None, 0)
    with pytest.raises(NotImplementedError):
        mover.SetWorldRaytraceKey()
    with pytest.raises(NotImplementedError):
        mover.SetBrushRaytraceKey()
