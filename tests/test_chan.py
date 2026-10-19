"""Tests for Engine/Inc/UnChan.h port (engine/__init__.py)."""

import pytest

from ut99py.engine import (
    UChannel,
    UControlChannel,
    UActorChannel,
    UFileChannel,
    EChannelType,
)


def test_channel_constants():
    # UnChan.h:34-36: ChannelClasses[CHTYPE_MAX].
    assert EChannelType.CHTYPE_None == 0
    assert EChannelType.CHTYPE_Control == 1
    assert EChannelType.CHTYPE_Actor == 2
    assert EChannelType.CHTYPE_File == 3
    assert EChannelType.CHTYPE_MAX == 8


def test_channel_defaults():
    # UnChan.h:16-32: UChannel variables.
    ch = UChannel()
    assert ch.Connection is None
    assert ch.OpenAcked is False
    assert ch.Closing is False
    assert ch.ChIndex == 0
    assert ch.OpenedLocally == 0
    assert ch.OpenPacketId == 0
    assert ch.OpenTemporary is False
    assert ch.ChType == EChannelType.CHTYPE_None
    assert ch.NumInRec == 0
    assert ch.NumOutRec == 0
    assert ch.NegotiatedVer == 0
    assert ch.InRec is None
    assert ch.OutRec is None
    assert ch.Broken is False


def test_channel_lib_bodies_raise():
    ch = UChannel()
    with pytest.raises(NotImplementedError):
        ch.Destroy()
    with pytest.raises(NotImplementedError):
        ch.Init(None, 0, False)
    with pytest.raises(NotImplementedError):
        ch.SetClosingFlag()
    with pytest.raises(NotImplementedError):
        ch.Close()
    with pytest.raises(NotImplementedError):
        ch.Describe()
    with pytest.raises(NotImplementedError):
        ch.ReceivedBunch(None)
    with pytest.raises(NotImplementedError):
        ch.ReceivedNak(0)
    with pytest.raises(NotImplementedError):
        ch.Tick()
    with pytest.raises(NotImplementedError):
        ch.RouteDestroy()
    with pytest.raises(NotImplementedError):
        ch.ReceivedAcks()
    with pytest.raises(NotImplementedError):
        ch.ReceivedSequencedBunch(None)
    with pytest.raises(NotImplementedError):
        ch.ReceivedRawBunch(None)
    with pytest.raises(NotImplementedError):
        ch.SendBunch(None, False)
    with pytest.raises(NotImplementedError):
        ch.IsNetReady(False)
    with pytest.raises(NotImplementedError):
        ch.AssertInSequenced()
    with pytest.raises(NotImplementedError):
        ch.MaxSendBytes()
    with pytest.raises(NotImplementedError):
        UChannel.IsKnownChannelType(0)


def test_control_channel():
    # UnChan.h:74-106: UControlChannel : UChannel, FOutputDevice.
    ch = UControlChannel()
    assert ch.ChType == EChannelType.CHTYPE_Control
    with pytest.raises(NotImplementedError):
        ch.StaticConstructor()
    with pytest.raises(NotImplementedError):
        ch.Init(None, 0, False)
    with pytest.raises(NotImplementedError):
        ch.Destroy()
    with pytest.raises(NotImplementedError):
        ch.ReceivedBunch(None)
    with pytest.raises(NotImplementedError):
        ch.Serialize("data", "Log")
    with pytest.raises(NotImplementedError):
        ch.Describe()


def test_actor_channel():
    # UnChan.h:108-166: UActorChannel variables + GetActor inline.
    ch = UActorChannel()
    assert ch.ChType == EChannelType.CHTYPE_Actor
    assert ch.Level is None
    assert ch.Actor is None
    assert ch.ActorClass is None
    assert ch.SpawnAcked is False
    assert ch.NumReps == 0
    assert ch.Recent == []
    assert ch.RepEval == []
    assert ch.Dirty == []
    assert ch.Retirement == []
    with pytest.raises(NotImplementedError):
        ch.StaticConstructor()
    with pytest.raises(NotImplementedError):
        ch.Init(None, 0, False)
    with pytest.raises(NotImplementedError):
        ch.Destroy()
    with pytest.raises(NotImplementedError):
        ch.SetClosingFlag()
    with pytest.raises(NotImplementedError):
        ch.ReceivedBunch(None)
    with pytest.raises(NotImplementedError):
        ch.ReceivedNak(0)
    with pytest.raises(NotImplementedError):
        ch.Close()
    with pytest.raises(NotImplementedError):
        ch.Tick()
    with pytest.raises(NotImplementedError):
        ch.Describe()
    with pytest.raises(NotImplementedError):
        ch.ReplicateActor()
    with pytest.raises(NotImplementedError):
        ch.SetChannelActor(None)
    # UnChan.h:165 inline: GetActor() returns Actor.
    assert ch.GetActor() is None


def test_file_channel():
    # UnChan.h:168-189: UFileChannel variables.
    ch = UFileChannel()
    assert ch.ChType == EChannelType.CHTYPE_File
    assert ch.Download is None
    assert ch.SendFileAr is None
    assert ch.SrcFilename == ""
    assert ch.PackageIndex == 0
    assert ch.SentData == 0
    with pytest.raises(NotImplementedError):
        ch.StaticConstructor()
    with pytest.raises(NotImplementedError):
        ch.Init(None, 0, False)
    with pytest.raises(NotImplementedError):
        ch.Destroy()
    with pytest.raises(NotImplementedError):
        ch.ReceivedBunch(None)
    with pytest.raises(NotImplementedError):
        ch.Describe()
    with pytest.raises(NotImplementedError):
        ch.Tick()
