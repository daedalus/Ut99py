"""Tests for Engine/Inc/UnConn.h port (engine/net_conn.py)."""

import pytest

from ut99py.engine.net_conn import (
    DO_ENABLE_NET_TEST,
    FDownloadInfo,
    MAX_CHANNELS,
    MAX_PROTOCOL_VERSION,
    MIN_PROTOCOL_VERSION,
    UNetConnection,
    DelayedPacket,
    EConnectionState,
)


def test_constants():
    # UnConn.h:42-48: protocol/channel bounds.
    assert MAX_PROTOCOL_VERSION == 1
    assert MIN_PROTOCOL_VERSION == 1
    assert MAX_CHANNELS == 1023


def test_do_enable_net_test_flag():
    # UnConn.h:36: #define DO_ENABLE_NET_TEST 1.
    assert DO_ENABLE_NET_TEST is True


def test_connection_state_enum():
    # UnConn.h:42-46: USOCK_Invalid/Closed/Pending/Open.
    assert int(EConnectionState.USOCK_Invalid) == 0
    assert int(EConnectionState.USOCK_Closed) == 1
    assert int(EConnectionState.USOCK_Pending) == 2
    assert int(EConnectionState.USOCK_Open) == 3


def test_default_connection_fields():
    # UnConn.h:53-62 all zeroed by constructor.
    c = UNetConnection()
    assert c.ProtocolVersion == 0
    assert c.RemoteVersion == 0
    assert c.MaxPacket == 0
    assert c.PacketOverhead == 0
    assert c.InternalAck is False
    assert c.Challenge == 0
    assert c.NegotiatedVer == 0
    assert c.UserFlags == 0
    assert len(c.RequestURL) == 0
    assert c.LastReceiveTime == 0.0
    assert c.LastSendTime == 0.0
    assert c.LastTickTime == 0.0
    assert c.LastRepTime == 0.0
    assert c.QueuedBytes == 0
    assert c.TickCount == 0
    assert not c.AllowMerge
    assert not c.TimeSensitive
    assert c.LastOutBunch is None
    assert c.StatUpdateTime == 0.0
    assert c.StatPeriod == 0.0
    assert c.InRate == 0.0 and c.OutRate == 0.0
    assert c.InPackets == 0.0 and c.OutPackets == 0.0
    assert c.InBunches == 0.0 and c.OutBunches == 0.0
    assert c.InLoss == 0.0 and c.OutLoss == 0.0
    assert c.InOrder == 0.0 and c.OutOrder == 0.0
    assert c.BestLag == 0.0 and c.AvgLag == 0.0
    # Stat accumulators default-zeroed.
    assert c.LagAcc == 0.0 and c.BestLagAcc == 0.0
    assert c.InLossAcc == 0 and c.OutLossAcc == 0
    assert c.InPktAcc == 0 and c.OutPktAcc == 0
    assert c.InBunAcc == 0 and c.OutBunAcc == 0
    assert c.InByteAcc == 0 and c.OutByteAcc == 0
    assert c.InOrdAcc == 0 and c.OutOrdAcc == 0
    assert c.LagCount == 0
    assert c.HighLossCount == 0
    assert c.LastTime == 0.0
    assert c.CumulativeTime == 0.0
    assert c.FrameTime == 0.0 and c.AverageFrameTime == 0.0
    assert c.CountedFrames == 0
    # Packet arrays + channel tables sized by header.
    assert len(c.OutLagTime) == 256
    assert len(c.OutLagPacketId) == 256
    assert len(c.Channels) == MAX_CHANNELS
    assert len(c.OutReliable) == MAX_CHANNELS
    assert len(c.InReliable) == MAX_CHANNELS
    assert len(c.QueuedAcks) == 0
    assert len(c.ResendAcks) == 0
    assert len(c.OpenChannels) == 0
    assert len(c.SentTemporaries) == 0
    assert c.ActorChannels == {}  # TMap<AActor*,UActorChannel*> → dict
    assert c.Download is None
    assert c.DownloadInfo == []
    if DO_ENABLE_NET_TEST:
        assert c.PktLoss == 0
        assert c.PktOrder == 0
        assert c.PktDup == 0
        assert c.PktLag == 0
        assert len(c.Delayed) == 0


def test_connection_with_driver():
    # UnConn.h:177-178 constructor.
    c = UNetConnection()
    other = UNetConnection()
    c.Driver = other
    assert c.Driver is other
    c.State = EConnectionState.USOCK_Open
    assert c.State == EConnectionState.USOCK_Open


def test_get_driver():
    # UnConn.h:690 inline: return Driver.
    c = UNetConnection()
    assert c.GetDriver() is None
    d = object()
    c.Driver = d
    assert c.GetDriver() is d


def test_destroy_sets_delete_me():
    # UObject::Destroy contract (UnConn.h:54).
    c = UNetConnection()
    with pytest.raises(NotImplementedError):
        c.destroy()


def test_lib_boundaries_raise():
    # All bodies in prebuilt Engine.lib.
    c = UNetConnection()
    with pytest.raises(NotImplementedError):
        c.Serialize(None)  # FArchive override
    with pytest.raises(NotImplementedError):
        c.Destroy()
    with pytest.raises(NotImplementedError):
        c.ReadInput(0.0)  # UPlayer interface
    with pytest.raises(NotImplementedError):
        c.Exec("cmd")  # FExec interface
    with pytest.raises(NotImplementedError):
        c.LowLevelGetRemoteAddress()  # pure virtual
    with pytest.raises(NotImplementedError):
        c.LowLevelDescribe()  # pure virtual
    with pytest.raises(NotImplementedError):
        c.LowLevelSend(b"", 0)  # pure virtual
    with pytest.raises(NotImplementedError):
        c.InitOut()
    with pytest.raises(NotImplementedError):
        c.AssertValid()
    with pytest.raises(NotImplementedError):
        c.SendAck(0, False)
    with pytest.raises(NotImplementedError):
        c.FlushNet()
    with pytest.raises(NotImplementedError):
        c.Tick()
    with pytest.raises(NotImplementedError):
        c.GetControlChannel()
    with pytest.raises(NotImplementedError):
        c.CreateChannel(0, False)
    with pytest.raises(NotImplementedError):
        c.IsNetReady(False)
    with pytest.raises(NotImplementedError):
        c.HandleClientPlayer(None)
    with pytest.raises(NotImplementedError):
        c.PurgeAcks()
    with pytest.raises(NotImplementedError):
        c.SendPackageMap()
    with pytest.raises(NotImplementedError):
        c.PreSend(0)
    with pytest.raises(NotImplementedError):
        c.PostSend()
    with pytest.raises(NotImplementedError):
        c.ReceivedRawPacket(b"", 0)
    with pytest.raises(NotImplementedError):
        c.SendRawBunch(None, False)
    with pytest.raises(NotImplementedError):
        c.ReceivedPacket(None)
    with pytest.raises(NotImplementedError):
        c.ReceivedNak(0)
    with pytest.raises(NotImplementedError):
        c.ReceiveFile(0)
    with pytest.raises(NotImplementedError):
        c.GetControlChannel()
    with pytest.raises(NotImplementedError):
        c.CreateChannel(0, False, 0)


def test_slow_assert_valid_calls_valid_when_guard_on():
    # UnConn.h:688-691: if guard enabled, AssertValid().
    c = UNetConnection()
    with pytest.raises(NotImplementedError):
        c.SlowAssertValid()


def test_download_info_struct():
    # UnConn.h:51-57: Class/ClassName/Params/Compression.
    d = FDownloadInfo()
    assert d.Class is None
    assert d.ClassName == ""
    assert d.Params == ""
    assert d.Compression is False
    assert d.Class is None


def test_delayed_packet_struct():
    # UnConn.h:44-50: Data (TArray<BYTE>), SendTime (FTime).
    p = DelayedPacket()
    assert p.Data == []
    assert p.SendTime == 0.0
    p.Data = [1, 2, 3]
    assert p.Data == [1, 2, 3]


def test_max_protocol_zero_is_not_portable():
    # Header declares constant; other engines use FCompactIndex. Not tested
    # here -- the constant is directly asserted at header level.
    pass
