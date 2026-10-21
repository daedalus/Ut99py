"""Tests for Engine/Inc/AInventory.h port (engine/ainventory.py)."""

import pytest

from ut99py.engine.ainventory import AInventory
from ut99py.engine.actor import AActor


def test_ainventory_base_chain_matches_engine_classes():
    # EngineClasses.h:1980 - class AInventory : public AActor
    assert issubclass(AInventory, AActor)


def test_ainventory_constructor_is_inline():
    inventory = AInventory()
    assert isinstance(inventory, AActor)


def test_check_recent_changes_is_inline_and_returns_true():
    # AInventory.h:16 - virtual UBOOL CheckRecentChanges() {return 1;}
    assert AInventory().CheckRecentChanges() is True


def test_lib_bodies_raise():
    inventory = AInventory()
    with pytest.raises(NotImplementedError):
        inventory.GetOptimizedRepList(None, None, None, None, 0)
    with pytest.raises(NotImplementedError):
        inventory.ShouldDoScriptReplication()
    with pytest.raises(NotImplementedError):
        inventory.NoVariablesToReplicate(None)
    with pytest.raises(NotImplementedError):
        inventory.UpdateFrequency(None, None, None)
