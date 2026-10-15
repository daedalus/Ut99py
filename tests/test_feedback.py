"""Tests for FFeedbackContextAnsi (Core/Inc/FFeedbackContextAnsi.h).

Expected strings follow the C++ appSprintf formats verbatim; GLog is
swapped for a recorder so forwarding is observable and stdout holds only
the LocalPrint output.
"""

import io
import sys

import pytest

from ut99py.core import system
from ut99py.core.objects import FContextSupplier, FFeedbackContext
from ut99py.core.system import FFeedbackContextAnsi
from ut99py.core.types import (
    ENAME_Error,
    ENAME_ExecWarning,
    ENAME_Heading,
    ENAME_Log,
    ENAME_Progress,
    ENAME_ScriptWarning,
    ENAME_SubHeading,
    ENAME_Title,
    ENAME_Warning,
)


class Recorder:
    """FOutputDevice-shaped sink; records (value, event) pairs."""

    def __init__(self):
        self.calls = []

    def serialize(self, v, event=ENAME_Log):
        self.calls.append((v, event))


class Supplier(FContextSupplier):
    def get_context(self):
        return "UT-Logo-Map.LevelInfo0"


@pytest.fixture
def glog(monkeypatch):
    rec = Recorder()
    monkeypatch.setattr(system, "GLog", rec)
    return rec


@pytest.fixture
def fb(glog):
    return FFeedbackContextAnsi()


def test_base_interface_is_abstract():
    # Core.h:275-279: all five methods are pure virtual.
    base = FFeedbackContext()
    calls = (
        lambda: base.yes_nof("x"),
        lambda: base.begin_slow_task("x", False, False),
        base.end_slow_task,
        lambda: base.status_updatef(0, 1, "x"),
        lambda: base.set_context(None),
    )
    for call in calls:
        with pytest.raises(NotImplementedError):
            call()


def test_context_supplier_is_abstract():
    # Core.h:268.
    with pytest.raises(NotImplementedError):
        FContextSupplier().get_context()


def test_title_is_suppressed(fb, glog, capsys):
    fb.serialize("Window Title", ENAME_Title)
    assert capsys.readouterr().out == ""
    assert glog.calls == []


def test_heading_format(fb, glog, capsys):
    fb.serialize("Setup", ENAME_Heading)
    assert capsys.readouterr().out == "--------------------Setup--------------------\n"
    assert glog.calls == [
        ("--------------------Setup--------------------", ENAME_Heading)
    ]


def test_subheading_format(fb, glog, capsys):
    fb.serialize("Loading", ENAME_SubHeading)
    assert capsys.readouterr().out == "Loading...\n"
    assert glog.calls == [("Loading...", ENAME_SubHeading)]


def test_warning_without_context_keeps_text(fb, glog, capsys):
    # No Context -> V is untouched, only WarningCount moves.
    fb.serialize("Kicked off", ENAME_Warning)
    assert capsys.readouterr().out == "Kicked off\n"
    assert fb.warning_count == 1


def test_error_with_context_prefixes_supplier(fb, glog, capsys):
    fb.set_context(Supplier())
    assert fb.context is not None
    fb.serialize("Missing package", ENAME_Error)
    assert (
        capsys.readouterr().out == "UT-Logo-Map.LevelInfo0 : Error, Missing package\n"
    )
    assert fb.warning_count == 1


@pytest.mark.parametrize(
    "event", [ENAME_Warning, ENAME_Error, ENAME_ExecWarning, ENAME_ScriptWarning]
)
def test_every_warning_event_counts(fb, glog, event):
    fb.serialize("w", event)
    assert fb.warning_count == 1
    assert glog.calls == [("w", event)]


def test_progress_uses_carriage_return_and_no_forward(fb, glog, capsys):
    fb.serialize("50%", ENAME_Progress)
    assert capsys.readouterr().out == "50%\r"
    assert glog.calls == []


def test_plain_line_is_printed_and_forwarded(fb, glog, capsys):
    fb.serialize("hello", ENAME_Log)
    assert capsys.readouterr().out == "hello\n"
    assert glog.calls == [("hello", ENAME_Log)]


def test_aux_out_gets_a_copy(fb, glog, capsys):
    aux = Recorder()
    fb.aux_out = aux
    fb.serialize("both", ENAME_Log)
    assert capsys.readouterr().out == "both\n"
    assert glog.calls == [("both", ENAME_Log)]
    assert aux.calls == [("both", ENAME_Log)]


def test_serialize_to_itself_does_not_forward(monkeypatch):
    # `if( GLog != this )` (FFeedbackContextAnsi.h:80).
    fb = FFeedbackContextAnsi()
    monkeypatch.setattr(system, "GLog", fb)
    fb.serialize("self", ENAME_Log)
    assert fb.warning_count == 0


def test_slow_task_toggles_global(fb, monkeypatch):
    monkeypatch.setattr(system, "GIsSlowTask", False)
    fb.begin_slow_task("Compiling", False, False)
    assert fb.slow_task_count == 1
    assert system.GIsSlowTask is True
    fb.end_slow_task()
    assert fb.slow_task_count == 0
    assert system.GIsSlowTask is False


def test_end_slow_task_underflow_checks(fb):
    # check(SlowTaskCount>0) (FFeedbackContextAnsi.h:111).
    with pytest.raises(ValueError):
        fb.end_slow_task()


def test_status_updatef_returns_true_and_prints_nothing(fb, glog, capsys):
    # The GET_VARARGS result is unused (the //!! body is stripped in C++).
    assert fb.status_updatef(1, 4, "stage %i of %i", 1, 4) is True
    assert capsys.readouterr().out == ""
    assert glog.calls == []


def test_yes_nof_silent_returns_true(fb, capsys):
    fb = FFeedbackContextAnsi(silent=True)
    assert fb.yes_nof("Overwrite %s?", "Foo") is True
    assert capsys.readouterr().out == ""


def test_yes_nof_headless_returns_true(fb, monkeypatch, capsys):
    # GIsClient and GIsEditor are both false in this port -> no prompt.
    monkeypatch.setattr(system, "GIsClient", False)
    monkeypatch.setattr(system, "GIsEditor", False)
    assert fb.yes_nof("Continue?") is True
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "answer,expected", [("y", True), ("Y", True), ("n", False), ("\n", False)]
)
def test_yes_nof_prompts_when_client(fb, monkeypatch, capsys, answer, expected):
    monkeypatch.setattr(system, "GIsClient", True)
    monkeypatch.setattr(sys, "stdin", io.StringIO(answer))
    assert fb.yes_nof("Continue?") is expected
    assert capsys.readouterr().out == "Continue? (Y/N): "
