"""Tests for Engine/Inc/UnCon.h port (engine/console.py)."""

import pytest

from ut99py.engine.camera import UCanvas
from ut99py.engine.console import (
    UConsole,
    UConsole_eventConnectFailure_Parms,
    UConsole_eventKeyEvent_Parms,
    UConsole_eventKeyType_Parms,
    UConsole_eventMessage_Parms,
    UConsole_eventPostRender_Parms,
    UConsole_eventTick_Parms,
)
from ut99py.core.types import FName


def test_console_constants():
    # UnCon.h:112-114 private enums.
    assert UConsole.MAX_BORDER == 6
    assert UConsole.MAX_LINES == 64
    assert UConsole.MAX_HISTORY == 16


def test_console_fixed_arrays_match_header_sizes():
    # UnCon.h:124-134 History[16], MsgText/MsgType/MsgPlayer/MsgTick[64].
    con = UConsole()
    assert len(con.History) == UConsole.MAX_HISTORY
    assert len(con.MsgText) == UConsole.MAX_LINES
    assert len(con.MsgType) == UConsole.MAX_LINES
    assert len(con.MsgPlayer) == UConsole.MAX_LINES
    assert len(con.MsgTick) == UConsole.MAX_LINES


def test_console_is_time_demo_reads_the_bitfield():
    # UnCon.h:132 inline: return bTimeDemo.
    con = UConsole()
    assert con.IsTimeDemo() is False
    con.bTimeDemo = True
    assert con.IsTimeDemo() is True


def test_console_lib_bodies_raise():
    # UnCon.h:32-38 bodies live in prebuilt Engine.lib.
    con = UConsole()
    with pytest.raises(NotImplementedError):
        con._Init(None)
    with pytest.raises(NotImplementedError):
        con.PreRender(None)
    with pytest.raises(NotImplementedError):
        con.PostRender(None)
    with pytest.raises(NotImplementedError):
        con.serialize("data")
    with pytest.raises(NotImplementedError):
        con.GetDrawWorld()
    with pytest.raises(NotImplementedError):
        con.execConsoleCommand(None)
    with pytest.raises(NotImplementedError):
        con.execSaveTimeDemo(None)


def test_event_message_parms_struct():
    # UnCon.h:15-21.
    parms = UConsole_eventMessage_Parms()
    assert parms.PRI is None
    assert parms.S == ""
    assert parms.PZone is None
    assert isinstance(parms.N, FName)


def test_event_connect_failure_parms_struct():
    # UnCon.h:22-26.
    parms = UConsole_eventConnectFailure_Parms()
    assert parms.FailCode == ""
    assert parms.URL == ""


def test_anonymous_event_parms_structs():
    # UnCon.h:56/72/76/94/98 inline anonymous structs lifted to module scope.
    tick = UConsole_eventTick_Parms()
    assert tick.DeltaTime == 0.0
    post = UConsole_eventPostRender_Parms()
    assert post.C is None
    key_type = UConsole_eventKeyType_Parms()
    assert key_type.Key == 0
    assert key_type.ReturnValue == 0
    key_event = UConsole_eventKeyEvent_Parms()
    assert key_event.Delta == 0.0
    assert key_event.ReturnValue == 0


def test_event_post_render_dispatches_through_process_event(monkeypatch):
    # UnCon.h:72-77 inline body: Parms, ProcessEvent(FindFunctionChecked(x)).
    con = UConsole()
    calls = []
    monkeypatch.setattr(
        con,
        "FindFunctionChecked",
        lambda name: calls.append(name) or name,
        raising=False,
    )
    monkeypatch.setattr(
        con, "ProcessEvent", lambda fn, parms: calls.append(parms), raising=False
    )
    canvas = UCanvas()
    con.eventPostRender(canvas)
    assert calls[0] == "ENGINE_PostRender"
    assert calls[1].C is canvas


def test_event_video_change_dispatches_with_null_parms(monkeypatch):
    # UnCon.h:62-65: ProcessEvent(..., NULL).
    con = UConsole()
    calls = []
    monkeypatch.setattr(
        con,
        "FindFunctionChecked",
        lambda name: calls.append(name) or name,
        raising=False,
    )
    monkeypatch.setattr(
        con, "ProcessEvent", lambda fn, parms: calls.append(parms), raising=False
    )
    con.eventVideoChange()
    assert calls[0] == "NAME_VideoChange"
    assert calls[1] is None
