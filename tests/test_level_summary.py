"""Tests for Engine/Inc/ULevelSummary.h port (engine/level_summary.py)."""

import pytest

from ut99py.engine.level_summary import ULevelSummary
from ut99py.core import UObject


def test_ulevelsummary_is_a_uobject():
    assert issubclass(ULevelSummary, UObject)


def test_ulevelsummary_members():
    summary = ULevelSummary()
    assert summary.Title == ""
    assert summary.Author == ""
    assert summary.IdealPlayerCount == ""
    assert summary.RecommendedEnemies == 0
    assert summary.RecommendedTeammates == 0
    assert summary.LevelEnterText == ""


def test_post_load_stops_at_the_core_lib_super_call():
    summary = ULevelSummary()
    with pytest.raises(NotImplementedError, match="UObject::PostLoad"):
        summary.PostLoad()
