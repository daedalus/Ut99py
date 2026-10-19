"""Tests for Engine/Inc/UnDemoPenLev.h."""
import pytest
from ut99py.engine.demopenlev import UDemoPlayPendingLevel, ACCEPTC_Reject

def test_constructor_raises():
    with pytest.raises(NotImplementedError):
        UDemoPlayPendingLevel()

def test_inline_defaults():
    # Construct via __new__ since __init__ raises.
    p = UDemoPlayPendingLevel.__new__(UDemoPlayPendingLevel)
    assert p.NotifyAcceptingConnection() == ACCEPTC_Reject
    assert p.NotifyAcceptedConnection(None) is None  # inline empty body
    assert p.NotifyAcceptingChannel(None) is True
    assert p.NotifyReceivedFile(None, 0, "a", False) is None  # inline empty body
    assert p.NotifySendingFile(None, None) is False  # inline {return 0;}
    assert p.TrySkipFile() is False  # inline {return 0;}
    p.SendJoin()  # inline {SentJoin = 1;}
    assert p.SentJoin is True

def test_notify_getlevel_raises():
    p = UDemoPlayPendingLevel.__new__(UDemoPlayPendingLevel)
    with pytest.raises(NotImplementedError):
        p.NotifyGetLevel()

def test_tick_ok():
    p = UDemoPlayPendingLevel.__new__(UDemoPlayPendingLevel)
    p.Tick(0.0)  # no raise

def test_tick_float_arg():
    p = UDemoPlayPendingLevel.__new__(UDemoPlayPendingLevel)
    p.Tick(1.5)  # should not raise
