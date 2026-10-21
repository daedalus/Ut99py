"""Tests for Engine/Inc/UnGame.h port (engine/ungame.py)."""

import pytest

from ut99py.engine.ungame import UGameEngine
from ut99py.engine.engine_core import UEngine


def test_ugameengine_is_a_uengine():
    assert issubclass(UGameEngine, UEngine)


def test_ugameengine_constructor_is_in_engine_lib():
    with pytest.raises(NotImplementedError):
        UGameEngine()


def test_ugameengine_lib_bodies_raise():
    engine = UGameEngine.__new__(UGameEngine)
    with pytest.raises(NotImplementedError):
        engine.StaticConstructor()
    with pytest.raises(NotImplementedError):
        engine.Serialize(None)
    with pytest.raises(NotImplementedError):
        engine.Destroy()
    with pytest.raises(NotImplementedError):
        engine.Init()
    with pytest.raises(NotImplementedError):
        engine.Exit()
    with pytest.raises(NotImplementedError):
        engine.Tick(0.016)
    with pytest.raises(NotImplementedError):
        engine.Draw(None)
    with pytest.raises(NotImplementedError):
        engine.Exec("get url")
    with pytest.raises(NotImplementedError):
        engine.MouseDelta(None, 0, 0.0, 0.0)
    with pytest.raises(NotImplementedError):
        engine.MousePosition(None, 0, 0.0, 0.0)
    with pytest.raises(NotImplementedError):
        engine.Click(None, 0, 0.0, 0.0)
    with pytest.raises(NotImplementedError):
        engine.SetClientTravel(None, "?game=ut99", True, None)
    with pytest.raises(NotImplementedError):
        engine.GetMaxTickRate()
    with pytest.raises(NotImplementedError):
        engine.ChallengeResponse(1)
    with pytest.raises(NotImplementedError):
        engine.SetProgress("Loading", "Map", 1.0)
    with pytest.raises(NotImplementedError):
        engine.Browse(None)
    with pytest.raises(NotImplementedError):
        engine.LoadMap(None)
    with pytest.raises(NotImplementedError):
        engine.SaveGame(0)
    with pytest.raises(NotImplementedError):
        engine.CancelPending()
    with pytest.raises(NotImplementedError):
        engine.PaintProgress()
    with pytest.raises(NotImplementedError):
        engine.UpdateConnectingMessage()
    with pytest.raises(NotImplementedError):
        engine.BuildServerMasterMap(None, None)
    with pytest.raises(NotImplementedError):
        engine.NotifyLevelChange()
    with pytest.raises(NotImplementedError):
        engine.FixUpLevel()
