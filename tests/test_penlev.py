"""Tests for Engine/Inc/UnPenLev.h port (engine/penlev.py)."""
import pytest
from ut99py.engine.penlev import UPendingLevel, UNetPendingLevel

def test_unpending_level_noconstruct():
    with pytest.raises(NotImplementedError):
        UPendingLevel()

def test_unpending_level_lib_bodies():
    p = UPendingLevel.__new__(UPendingLevel)
    with pytest.raises(NotImplementedError):
        p.Tick(0.0)
    with pytest.raises(NotImplementedError):
        p.GetDriver()
    with pytest.raises(NotImplementedError):
        p.SendJoin()
    with pytest.raises(NotImplementedError):
        p.TrySkipFile()

def test_unet_pending_level_noconstruct():
    with pytest.raises(NotImplementedError):
        UNetPendingLevel()

def test_unet_pending_level_lib_bodies():
    p = UNetPendingLevel.__new__(UNetPendingLevel)
    with pytest.raises(NotImplementedError):
        p.Tick(0.0)
    with pytest.raises(NotImplementedError):
        p.GetDriver()
    with pytest.raises(NotImplementedError):
        p.SendJoin()
    with pytest.raises(NotImplementedError):
        p.TrySkipFile()
    with pytest.raises(NotImplementedError):
        p.NotifyAcceptingConnection()
    with pytest.raises(NotImplementedError):
        p.NotifyAcceptedConnection(None)
    with pytest.raises(NotImplementedError):
        p.NotifyAcceptingChannel(None)
    with pytest.raises(NotImplementedError):
        p.NotifyGetLevel()
    with pytest.raises(NotImplementedError):
        p.NotifyReceivedText(None, "a")
    with pytest.raises(NotImplementedError):
        p.NotifyReceivedFile(None, 0, "a", False)
    with pytest.raises(NotImplementedError):
        p.NotifySendingFile(None, None)
    with pytest.raises(NotImplementedError):
        p.ReceiveNextFile(None)
