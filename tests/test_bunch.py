"""Tests for Engine/Inc/UnBunch.h port (engine/bunch.py)."""

import pytest

from ut99py.engine.bunch import FOutBunch, FInBunch
from ut99py.engine import UNetConnection, UChannel, FTime


def test_foutbunch_defaults():
    bunch = FOutBunch()
    assert bunch.Next is None
    assert bunch.Channel is None
    assert isinstance(bunch.Time, FTime)
    assert bunch.ReceivedAck is False
    assert bunch.ChIndex == 0
    assert bunch.ChType == 0
    assert bunch.ChSequence == 0
    assert bunch.PacketId == 0
    assert bunch.bOpen == 0
    assert bunch.bClose == 0
    assert bunch.bReliable == 0


def test_foutbunch_with_params():
    chan = UChannel()
    bunch = FOutBunch(in_channel=chan, b_close=True)
    assert bunch.Channel is chan
    assert bunch.bClose == 1
    assert bunch.bOpen == 0


def test_finbunch_defaults():
    conn = UNetConnection()
    bunch = FInBunch(conn)
    assert bunch.Connection is conn
    assert bunch.Next is None
    assert bunch.PacketId == 0
    assert bunch.ChIndex == 0
    assert bunch.ChType == 0
    assert bunch.ChSequence == 0
    assert bunch.bOpen == 0
    assert bunch.bClose == 0
    assert bunch.bReliable == 0


def test_foutbunch_lshift_raises():
    bunch = FOutBunch()
    with pytest.raises(NotImplementedError):
        bunch.__lshift__(None)
    with pytest.raises(NotImplementedError):
        bunch.__lshift_obj__(None)


def test_finbunch_lshift_raises():
    conn = UNetConnection()
    bunch = FInBunch(conn)
    with pytest.raises(NotImplementedError):
        bunch.__lshift__(None)
    with pytest.raises(NotImplementedError):
        bunch.__lshift_obj__(None)
