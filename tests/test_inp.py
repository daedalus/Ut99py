"""Tests for Engine/Inc/UnIn.h port (engine/inp.py)."""
import pytest
from ut99py.engine.inp import UInput, FAlias, ALIAS_MAX, IK_MAX


def test_constants():
    assert ALIAS_MAX == 40
    assert IK_MAX == 256


def test_alias_defaults():
    alias = FAlias()
    assert alias.Alias is not None
    assert alias.Command is not None


def test_input_defaults():
    inp = UInput()
    assert len(inp.Aliases) == ALIAS_MAX
    assert len(inp.Bindings) == IK_MAX
    assert len(inp.KeyDownTable) == IK_MAX
    assert inp.Viewport is None
    assert inp.Delta == 0.0
    assert inp.StaticConfigName() == "User"


def test_input_accessors():
    inp = UInput()
    inp.SetInputAction("IA_Press", 0.5)
    assert inp.GetInputAction() == "IA_Press"
    assert inp.GetInputDelta() == 0.5
    assert inp.KeyDown(0) == 0


def test_input_lib_methods_raise():
    inp = UInput()
    with pytest.raises(NotImplementedError):
        inp.StaticConstructor()
    with pytest.raises(NotImplementedError):
        inp.Serialize(None)
    with pytest.raises(NotImplementedError):
        UInput.StaticInitInput()
    with pytest.raises(NotImplementedError):
        inp.Init(None)
    with pytest.raises(NotImplementedError):
        inp.Exec("cmd", None)
    with pytest.raises(NotImplementedError):
        inp.PreProcess(None, None)
    with pytest.raises(NotImplementedError):
        inp.Process(None, None, None)
    with pytest.raises(NotImplementedError):
        inp.DirectAxis(None, 0.0, 0.0)
    with pytest.raises(NotImplementedError):
        inp.ReadInput(0.0, None)
    with pytest.raises(NotImplementedError):
        inp.ResetInput()
    with pytest.raises(NotImplementedError):
        inp.GetKeyName(None)
    with pytest.raises(NotImplementedError):
        inp.FindKeyName("a", None)
    with pytest.raises(NotImplementedError):
        inp.FindButtonName(None, "a")
    with pytest.raises(NotImplementedError):
        inp.FindAxisName(None, "a")
    with pytest.raises(NotImplementedError):
        inp.ExecInputCommands("a", None)
