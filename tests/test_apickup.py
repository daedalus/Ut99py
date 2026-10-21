"""Tests for Engine/Inc/APickup.h port (engine/apickup.py)."""

import pytest

from ut99py.engine.apickup import APickup
from ut99py.engine.ainventory import AInventory


def test_apickup_base_chain_matches_engine_classes():
    # EngineClasses.h:2051 - class APickup : public AInventory
    assert issubclass(APickup, AInventory)


def test_apickup_constructor_is_inline():
    pickup = APickup()
    assert isinstance(pickup, AInventory)


def test_get_optimized_rep_list_is_in_engine_lib():
    pickup = APickup()
    with pytest.raises(NotImplementedError):
        pickup.GetOptimizedRepList(None, None, None, None, 0)
