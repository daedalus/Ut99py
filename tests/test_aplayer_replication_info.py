"""Tests for Engine/Inc/APlayerReplicationInfo.h port (engine/aplayer_replication_info.py)."""

import pytest

from ut99py.engine.agame_replication_info import AReplicationInfo
from ut99py.engine.aplayer_replication_info import APlayerReplicationInfo


def test_aplayer_replication_info_base_chain_matches_engine_classes():
    # EngineClasses.h:2286 - class APlayerReplicationInfo : public AReplicationInfo
    assert issubclass(APlayerReplicationInfo, AReplicationInfo)


def test_aplayer_replication_info_constructor_is_inline():
    info = APlayerReplicationInfo()
    assert isinstance(info, AReplicationInfo)


def test_get_optimized_rep_list_is_in_engine_lib():
    info = APlayerReplicationInfo()
    with pytest.raises(NotImplementedError):
        info.GetOptimizedRepList(None, None, None, None, 0)
