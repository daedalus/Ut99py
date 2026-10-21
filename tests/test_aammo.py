"""Tests for Engine/Inc/AAmmo.h port (engine/aammo.py)."""

import pytest

from ut99py.engine.aammo import AAmmo
from ut99py.engine.apickup import APickup
from ut99py.engine.ainventory import AInventory
from ut99py.engine.actor import AActor


def test_aammo_base_chain_matches_engine_classes():
    # EngineClasses.h:2065 - class AAmmo : public APickup
    assert issubclass(AAmmo, APickup)
    assert issubclass(APickup, AInventory)
    assert issubclass(AInventory, AActor)


def test_aammo_constructor_is_inline():
    ammo = AAmmo()
    assert isinstance(ammo, APickup)


def test_get_optimized_rep_list_is_in_engine_lib():
    ammo = AAmmo()
    with pytest.raises(NotImplementedError):
        ammo.GetOptimizedRepList(None, None, None, None, 0)
