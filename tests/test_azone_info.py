"""Tests for Engine/Inc/AZoneInfo.h port (engine/azone_info.py)."""

import pytest

from ut99py.engine.agame_replication_info import AInfo
from ut99py.engine.azone_info import AZoneInfo


def test_azone_info_base_chain_matches_engine_classes():
    # EngineClasses.h:2434 - class AZoneInfo : public AInfo
    assert issubclass(AZoneInfo, AInfo)


def test_azone_info_constructor_is_inline():
    zone = AZoneInfo()
    assert isinstance(zone, AInfo)


def test_lib_bodies_raise():
    zone = AZoneInfo()
    with pytest.raises(NotImplementedError):
        zone.PostEditChange()
    with pytest.raises(NotImplementedError):
        zone.GetOptimizedRepList(None, None, None, None, 0)
