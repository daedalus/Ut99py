"""Tests for Engine/Inc/UnRenderIterator.h port (graphics/unrender_iterator.py)."""

import pytest

from ut99py.graphics.unrender_iterator import URenderIterator
from ut99py.core import UObject


def test_urenderiterator_is_a_uobject():
    assert issubclass(URenderIterator, UObject)


def test_urenderiterator_constructor_is_in_engine_lib():
    with pytest.raises(NotImplementedError):
        URenderIterator()


def test_urenderiterator_lib_bodies_raise():
    iterator = URenderIterator.__new__(URenderIterator)
    with pytest.raises(NotImplementedError):
        iterator.Init(None)
    with pytest.raises(NotImplementedError):
        iterator.UnInit()
    with pytest.raises(NotImplementedError):
        iterator.First()
    with pytest.raises(NotImplementedError):
        iterator.Next()
    with pytest.raises(NotImplementedError):
        iterator.IsDone()
    with pytest.raises(NotImplementedError):
        iterator.CurrentItem()
