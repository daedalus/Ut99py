"""Tests for Engine/Inc/APlayerPawn.h port (engine/aplayer_pawn.py)."""

import pytest

from ut99py.engine.aplayer_pawn import APlayerPawn
from ut99py.engine.pawn import APawn


def test_aplayer_pawn_base_chain_matches_engine_classes():
    # EngineClasses.h:1631 - class APlayerPawn : public APawn
    assert issubclass(APlayerPawn, APawn)


def test_aplayer_pawn_constructor_is_inline():
    pawn = APlayerPawn()
    assert isinstance(pawn, APawn)


def test_lib_bodies_raise():
    pawn = APlayerPawn()
    with pytest.raises(NotImplementedError):
        pawn.GetOptimizedRepList(None, None, None, None, 0)
    with pytest.raises(NotImplementedError):
        pawn.SetPlayer(None)
    with pytest.raises(NotImplementedError):
        pawn.ClearScreen()
    with pytest.raises(NotImplementedError):
        pawn.RecomputeLighting()
    with pytest.raises(NotImplementedError):
        pawn.CanSee(None)
    with pytest.raises(NotImplementedError):
        pawn.GetViewZone(0, None)
    with pytest.raises(NotImplementedError):
        pawn.IsZoneVisible(0)
    with pytest.raises(NotImplementedError):
        pawn.IsSurfVisible(None, 0, None)
    with pytest.raises(NotImplementedError):
        pawn.IsActorVisible(None)
