"""Tests for Engine/Inc/AGameReplicationInfo.h port (engine/agame_replication_info.py)."""

import pytest

from ut99py.engine.agame_replication_info import (
    AGameReplicationInfo,
    AInfo,
    AReplicationInfo,
)
from ut99py.engine.actor import AActor


def test_agame_replication_info_base_chain_matches_engine_classes():
    # EngineClasses.h:2255 - class AGameReplicationInfo : public AReplicationInfo
    assert issubclass(AGameReplicationInfo, AReplicationInfo)
    assert issubclass(AReplicationInfo, AInfo)
    assert issubclass(AInfo, AActor)


def test_agame_replication_info_constructor_is_inline():
    info = AGameReplicationInfo()
    assert isinstance(info, AReplicationInfo)


def test_get_optimized_rep_list_is_in_engine_lib():
    info = AGameReplicationInfo()
    with pytest.raises(NotImplementedError):
        info.GetOptimizedRepList(None, None, None, None, 0)
