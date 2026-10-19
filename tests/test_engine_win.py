"""Tests for Engine/Inc/UnEngineWin.h port (engine/engine_win.py)."""

import pytest

from ut99py.engine.engine_win import (
    FExecHook,
    WConfigPageDetail,
    WConfigPageDriver,
    WConfigPageFirstTime,
    WConfigPageRenderer,
    WConfigPageSafeMode,
    WConfigPageSafeOptions,
    WConfigWizard,
    init_sys_dirs,
    launch_mplayer,
)


class _FakeOwner:
    """Stand-in for WConfigWizard (base WWizardDialog not yet ported)."""

    def __init__(self) -> None:
        self.end_dialog_calls = []
        self.advance_calls = []

    def EndDialog(self, result: int) -> None:
        self.end_dialog_calls.append(result)

    def Advance(self, page) -> None:
        self.advance_calls.append(page)


def test_exec_hook_notify_destroy_clears_preferences():
    # UnEngineWin.h:541-545 inline: if Src==Preferences, Preferences=NULL.
    hook = FExecHook()
    assert hook.Preferences is None
    prefs = object()
    hook.Preferences = prefs
    hook.notify_destroy(object())
    assert hook.Preferences is prefs
    hook.notify_destroy(prefs)
    assert hook.Preferences is None


def test_exec_hook_exec_is_win32_bound():
    # UnEngineWin.h:546-681: ShowLog/EditActor/Preferences via Win32 windows.
    hook = FExecHook()
    with pytest.raises(NotImplementedError):
        hook.exec_commands("ShowLog")


def test_first_time_page_get_next_ends_dialog():
    # UnEngineWin.h:139-142: Owner->EndDialog(1); return NULL.
    owner = _FakeOwner()
    page = WConfigPageFirstTime(owner)
    assert page.GetNext() is None
    assert owner.end_dialog_calls == [1]


def test_detail_page_get_next_returns_first_time():
    # UnEngineWin.h:300-303: return new WConfigPageFirstTime(Owner).
    owner = _FakeOwner()
    page = WConfigPageDetail(owner)
    nxt = page.GetNext()
    assert isinstance(nxt, WConfigPageFirstTime)
    assert nxt.Owner is owner


def test_driver_page_get_next_returns_detail():
    # UnEngineWin.h:325-328.
    owner = _FakeOwner()
    page = WConfigPageDriver(owner)
    nxt = page.GetNext()
    assert isinstance(nxt, WConfigPageDetail)
    assert nxt.Owner is owner


def test_safe_mode_page_button_delegates():
    # UnEngineWin.h:457-467: OnRun ends, OnVideo/OnSafeMode advance.
    owner = _FakeOwner()
    page = WConfigPageSafeMode(owner)
    page.OnRun()
    assert owner.end_dialog_calls == [1]
    page.OnVideo()
    assert isinstance(owner.advance_calls[0], WConfigPageRenderer)
    page.OnSafeMode()
    assert isinstance(owner.advance_calls[1], WConfigPageSafeOptions)
    assert page.GetNextText() is None  # UnEngineWin.h:474-477 return NULL.


def test_renderer_page_initial_state():
    # UnEngineWin.h:331-347 ctor: First(0), empty Classes array.
    page = WConfigPageRenderer(_FakeOwner())
    assert page.First == 0
    assert page.Classes == []


def test_win32_bound_bodies_raise():
    # Splash dirs (InitSysDirs) and mplayer launch are pure Win32.
    with pytest.raises(NotImplementedError):
        init_sys_dirs()
    with pytest.raises(NotImplementedError):
        launch_mplayer()
    with pytest.raises(NotImplementedError):
        WConfigWizard()
