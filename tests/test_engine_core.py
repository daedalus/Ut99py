"""Tests for Engine/Inc/UnEngine.h port (engine/engine_core.py)."""

import pytest

from ut99py.engine.engine_core import (
    UEngine,
    UServerCommandlet,
    DO_ENABLE_NET_TEST,
)


def test_engine_constants():
    # UnEngine.h doesn't declare these; from UnConn.h originally.
    assert DO_ENABLE_NET_TEST is True


def test_engine_subsystem_abstract():
    # UEngine inherits USubsystem, declares CLASS_Config|CLASS_Transient.
    eng = UEngine()
    assert hasattr(eng, "StaticConstructor")
    assert hasattr(eng, "Init")
    assert hasattr(eng, "Exit")
    assert hasattr(eng, "Exec")
    assert hasattr(eng, "Flush")
    assert hasattr(eng, "Key")
    assert hasattr(eng, "InputEvent")
    assert hasattr(eng, "Tick")
    assert hasattr(eng, "Draw")
    assert hasattr(eng, "MouseDelta")
    assert hasattr(eng, "MousePosition")
    assert hasattr(eng, "Click")
    assert hasattr(eng, "SetClientTravel")
    assert hasattr(eng, "ChallengeResponse")
    assert hasattr(eng, "GetMaxTickRate")
    assert hasattr(eng, "SetProgress")
    assert hasattr(eng, "InitAudio")
    assert hasattr(eng, "edSetClickLocation")


def test_engine_lib_bodies_raise():
    # UnEngine.h bodies live in prebuilt Engine.lib.
    eng = UEngine()
    with pytest.raises(NotImplementedError):
        eng.Serialize(None)
    with pytest.raises(NotImplementedError):
        eng.Destroy()
    with pytest.raises(NotImplementedError):
        eng.Init()
    with pytest.raises(NotImplementedError):
        eng.Exit()
    with pytest.raises(NotImplementedError):
        eng.Exec("cmd")
    with pytest.raises(NotImplementedError):
        eng.Flush(False)
    with pytest.raises(NotImplementedError):
        eng.Key(None, None)
    with pytest.raises(NotImplementedError):
        eng.InputEvent(None, None, None, None)
    with pytest.raises(NotImplementedError):
        eng.Tick(0.0)
    with pytest.raises(NotImplementedError):
        eng.Draw(None, False)
    with pytest.raises(NotImplementedError):
        eng.MouseDelta(None, 0, 0.0, 0.0)
    with pytest.raises(NotImplementedError):
        eng.MousePosition(None, 0, 0.0, 0.0)
    with pytest.raises(NotImplementedError):
        eng.Click(None, 0, 0.0, 0.0)
    with pytest.raises(NotImplementedError):
        eng.SetClientTravel(None, None, False, None)
    with pytest.raises(NotImplementedError):
        eng.ChallengeResponse(0)
    with pytest.raises(NotImplementedError):
        eng.GetMaxTickRate()
    with pytest.raises(NotImplementedError):
        eng.SetProgress(None, None, 0.0)


def test_server_commandlet():
    # UnEngine.h:91-93: Simple commandlet with StaticConstructor and Main.
    cmd = UServerCommandlet()
    assert cmd._help_text == "server: run as dedicated server"
    assert cmd._usage == "server <map>"
    result = cmd.main("mapname")
    assert result == 0
