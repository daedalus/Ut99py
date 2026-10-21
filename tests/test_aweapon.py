"""Tests for Engine/Inc/AWeapon.h port (engine/aweapon.py)."""

import pytest

from ut99py.engine.aweapon import AWeapon
from ut99py.engine.ainventory import AInventory


def test_aweapon_base_chain_matches_engine_classes():
    # EngineClasses.h:2078 - class AWeapon : public AInventory
    assert issubclass(AWeapon, AInventory)


def test_aweapon_constructor_is_inline():
    weapon = AWeapon()
    assert isinstance(weapon, AInventory)


def test_get_optimized_rep_list_is_in_engine_lib():
    weapon = AWeapon()
    with pytest.raises(NotImplementedError):
        weapon.GetOptimizedRepList(None, None, None, None, 0)
