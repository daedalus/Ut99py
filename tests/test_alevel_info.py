"""Tests for Engine/Inc/ALevelInfo.h port (engine/alevel_info.py)."""

import pytest

from ut99py.engine.alevel_info import ALevelInfo
from ut99py.engine.azone_info import AZoneInfo


def test_alevel_info_base_chain_matches_engine_classes():
    # EngineClasses.h:2572 - class ALevelInfo : public AZoneInfo
    assert issubclass(ALevelInfo, AZoneInfo)


def test_alevel_info_constructor_is_inline():
    level = ALevelInfo()
    assert isinstance(level, AZoneInfo)


def test_get_optimized_rep_list_is_in_engine_lib():
    level = ALevelInfo()
    with pytest.raises(NotImplementedError):
        level.GetOptimizedRepList(None, None, None, None, 0)
