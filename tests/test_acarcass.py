"""Tests for Engine/Inc/ACarcass.h port (engine/acarcass.py)."""

import pytest

from ut99py.engine.acarcass import ACarcass, ADecoration
from ut99py.engine.actor import AActor


def test_acarcass_base_chain_matches_engine_classes():
    # EngineClasses.h:3047 - class ACarcass : public ADecoration
    assert issubclass(ACarcass, ADecoration)
    assert issubclass(ADecoration, AActor)


def test_acarcass_constructor_is_inline():
    carcass = ACarcass()
    assert isinstance(carcass, ADecoration)


def test_update_frequency_is_in_engine_lib():
    carcass = ACarcass()
    with pytest.raises(NotImplementedError):
        carcass.UpdateFrequency(None, None, None)
