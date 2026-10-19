"""Port of Engine/Inc/UnConn.h (6 declared symbols).

Network connection class UNetConnection with full C++ member set.
Notes:
- MAX_PROTOCOL_VERSION / MIN_PROTOCOL_VERSION / MAX_CHANNELS constants
  already exist in engine/__init__.py (line constants); re-declared here
  for port fidelity.
- EConnectionState enum, DelayedPacket and FDownloadInfo already exist
  in engine/__init__.py; re-declared here as plain aliases/classes to keep
  the port self-contained.
- UDownload/UActorChannel/UPackageMap/FURL/FBitWriter/FBitWriterMark are
  referenced but not yet ported; typed as Optional[Any] / Any.
- All method bodies raise NotImplementedError("Engine.lib") per port fidelity.
"""

from __future__ import annotations

from typing import Any

from ..engine import UPlayer

# ----------------------------------------------------------------------
# Constants (UnConn.h:42-48)
# ----------------------------------------------------------------------
DO_ENABLE_NET_TEST: bool = True
MAX_PROTOCOL_VERSION: int = 1
MIN_PROTOCOL_VERSION: int = 1
MAX_CHANNELS: int = 1023


# ----------------------------------------------------------------------
# Enums / structs already present in engine/__init__.py; redeclared here
# so this module porting UnConn.h is self-contained.
# ----------------------------------------------------------------------
class EConnectionState:
    """State of a connection (UnConn.h:42-46)."""

    USOCK_Invalid = 0
    USOCK_Closed = 1
    USOCK_Pending = 2
    USOCK_Open = 3


class DelayedPacket:
    """Lagged packet for net testing (UnConn.h:44-50)."""

    def __init__(self) -> None:
        self.Data: list = []
        self.SendTime: float = 0.0


class FDownloadInfo:
    """Info about a file download (UnConn.h:51-57)."""

    def __init__(self) -> None:
        self.Class: Any = None  # UClass*
        self.ClassName: str = ""
        self.Params: str = ""
        self.Compression: bool = False


# ----------------------------------------------------------------------
# UNetConnection
# ----------------------------------------------------------------------
class UNetConnection(UPlayer):
    """Network connection (UnConn.h:51-188)."""

    # Constants (UnConn.h:42-48).
    MAX_PROTOCOL_VERSION: int = 1
    MIN_PROTOCOL_VERSION: int = 1
    MAX_CHANNELS: int = 1023

    def __init__(self, Driver: Any = None, InURL: Any = None) -> None:
        super().__init__()
        # Connection information (UnConn.h:63-66).
        self.Driver: Any = Driver
        self.State: EConnectionState = EConnectionState.USOCK_Invalid
        self.URL: Any = InURL
        self.PackageMap: Any = None

        # Negotiated parameters (UnConn.h:69-70).
        self.ProtocolVersion: int = 0
        self.RemoteVersion: int = 0
        self.MaxPacket: int = 0
        self.PacketOverhead: int = 0
        self.InternalAck: bool = False
        self.Challenge: int = 0
        self.NegotiatedVer: int = 0
        self.UserFlags: int = 0
        self.RequestURL: str = ""

        # Internal (UnConn.h:71-83).
        self.LastReceiveTime: float = 0.0
        self.LastSendTime: float = 0.0
        self.LastTickTime: float = 0.0
        self.LastRepTime: float = 0.0
        self.QueuedBytes: int = 0
        self.TickCount: int = 0

        # Merge info (UnConn.h:86-87).
        self.LastStart: Any = None  # FBitWriterMark
        self.LastEnd: Any = None  # FBitWriterMark
        self.AllowMerge: bool = False
        self.TimeSensitive: bool = False
        self.LastOutBunch: Any = None  # FOutBunch*
        self.LastOut: Any = None  # FOutBunch

        # Stat display (UnConn.h:91-96).
        self.StatUpdateTime: float = 0.0
        self.StatPeriod: float = 0.0
        self.InRate: float = 0.0
        self.OutRate: float = 0.0
        self.InPackets: float = 0.0
        self.OutPackets: float = 0.0
        self.InBunches: float = 0.0
        self.OutBunches: float = 0.0
        self.InLoss: float = 0.0
        self.OutLoss: float = 0.0
        self.InOrder: float = 0.0
        self.OutOrder: float = 0.0
        self.BestLag: float = 0.0
        self.AvgLag: float = 0.0

        # Stat accumulators (UnConn.h:97-102).
        self.LagAcc: float = 0.0
        self.BestLagAcc: float = 0.0
        self.InLossAcc: int = 0
        self.OutLossAcc: int = 0
        self.InPktAcc: int = 0
        self.OutPktAcc: int = 0
        self.InBunAcc: int = 0
        self.OutBunAcc: int = 0
        self.InByteAcc: int = 0
        self.OutByteAcc: int = 0
        self.InOrdAcc: int = 0
        self.OutOrdAcc: int = 0
        self.LagCount: int = 0
        self.HighLossCount: int = 0
        self.LastTime: float = 0.0
        self.CumulativeTime: float = 0.0
        self.FrameTime: float = 0.0
        self.AverageFrameTime: float = 0.0
        self.CountedFrames: int = 0

        # Packet (UnConn.h:111-122).
        self.Out: Any = None  # FBitWriter
        self.OutLagTime: list = [0.0] * 256
        self.OutLagPacketId: list = [0] * 256
        self.InPacketId: int = 0
        self.OutPacketId: int = 0
        self.OutAckPacketId: int = 0

        # Channel table (UnConn.h:124-126).
        self.Channels: list = [None] * MAX_CHANNELS  # UChannel*
        self.OutReliable: list = [0] * MAX_CHANNELS
        self.InReliable: list = [0] * MAX_CHANNELS
        self.QueuedAcks: list = []
        self.ResendAcks: list = []
        self.OpenChannels: list = []  # TArray<UChannel*>
        self.SentTemporaries: list = []  # TArray<AActor*>
        self.ActorChannels: dict = {}  # TMap<AActor*,UActorChannel*>

        # File Download (UnConn.h:130-131).
        self.Download: Any = None  # UDownload*
        self.DownloadInfo: list = []  # TArray<FDownloadInfo>

        # Development stats (UnConn.h:132-134).
        self.PktLoss: int = 0
        self.PktOrder: int = 0
        self.PktDup: int = 0
        self.PktLag: int = 0
        self.Delayed: list = []  # TArray<DelayedPacket>

    # UObject interface (UnConn.h:52-53).
    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UNetConnection::Serialize: Engine.lib")

    def Destroy(self) -> None:
        raise NotImplementedError("C++ UNetConnection::Destroy: Engine.lib")

    # UPlayer interface (UnConn.h:53).
    def ReadInput(self, DeltaSeconds: float) -> None:
        raise NotImplementedError("C++ UNetConnection::ReadInput: Engine.lib")

    # FArchive interface (UnConn.h:54).
    def serialize(self, Data: Any, MsgType: Any = None) -> None:
        raise NotImplementedError("C++ UNetConnection::Serialize: Engine.lib")

    # FExec interface (UnConn.h:54-64).
    def exec_commands(self, cmd: str, ar: Any = None) -> bool:
        raise NotImplementedError("C++ UNetConnection::Exec: Engine.lib")

    # Alias for header fidelity (C++ calls it Exec, FExec uses exec_commands).
    def Exec(self, Cmd: Any, Ar: Any = None) -> bool:
        return self.exec_commands(Cmd, Ar)

    # UNetConnection interface (UnConn.h:134-140).
    def LowLevelGetRemoteAddress(self) -> Any:
        raise NotImplementedError(
            "C++ UNetConnection::LowLevelGetRemoteAddress: Engine.lib"
        )

    def LowLevelDescribe(self) -> Any:
        raise NotImplementedError("C++ UNetConnection::LowLevelDescribe: Engine.lib")

    def LowLevelSend(self, Data: Any, Count: int) -> None:
        raise NotImplementedError("C++ UNetConnection::LowLevelSend: Engine.lib")

    def InitOut(self) -> None:
        raise NotImplementedError("C++ UNetConnection::InitOut: Engine.lib")

    def AssertValid(self) -> None:
        raise NotImplementedError("C++ UNetConnection::AssertValid: Engine.lib")

    def SendAck(self, PacketId: int, FirstTime: bool = True) -> None:
        raise NotImplementedError("C++ UNetConnection::SendAck: Engine.lib")

    def FlushNet(self) -> None:
        raise NotImplementedError("C++ UNetConnection::FlushNet: Engine.lib")

    def Tick(self) -> None:
        raise NotImplementedError("C++ UNetConnection::Tick: Engine.lib")

    def IsNetReady(self, Saturate: bool) -> bool:
        raise NotImplementedError("C++ UNetConnection::IsNetReady: Engine.lib")

    def HandleClientPlayer(self, Pawn: Any) -> None:
        raise NotImplementedError("C++ UNetConnection::HandleClientPlayer: Engine.lib")

    # UNetConnection functions (UnConn.h:141-143).
    def PurgeAcks(self) -> None:
        raise NotImplementedError("C++ UNetConnection::PurgeAcks: Engine.lib")

    def SendPackageMap(self) -> None:
        raise NotImplementedError("C++ UNetConnection::SendPackageMap: Engine.lib")

    def PreSend(self, SizeBits: int) -> None:
        raise NotImplementedError("C++ UNetConnection::PreSend: Engine.lib")

    def PostSend(self) -> None:
        raise NotImplementedError("C++ UNetConnection::PostSend: Engine.lib")

    def ReceivedRawPacket(self, Data: Any, Count: int) -> None:
        raise NotImplementedError("C++ UNetConnection::ReceivedRawPacket: Engine.lib")

    def SendRawBunch(self, Bunch: Any, InAllowMerge: bool) -> int:
        raise NotImplementedError("C++ UNetConnection::SendRawBunch: Engine.lib")

    def ReceivedPacket(self, Reader: Any) -> None:
        raise NotImplementedError("C++ UNetConnection::ReceivedPacket: Engine.lib")

    def ReceivedNak(self, NakPacketId: int) -> None:
        raise NotImplementedError("C++ UNetConnection::ReceivedNak: Engine.lib")

    def ReceiveFile(self, PackageIndex: int) -> None:
        raise NotImplementedError("C++ UNetConnection::ReceiveFile: Engine.lib")

    def SlowAssertValid(self) -> None:
        raise NotImplementedError("C++ UNetConnection::SlowAssertValid: Engine.lib")

    def GetDriver(self) -> Any:
        return self.Driver

    def GetControlChannel(self) -> Any:
        raise NotImplementedError("C++ UNetConnection::GetControlChannel: Engine.lib")

    def CreateChannel(
        self, Type: Any, OpenedLocally: bool, ChannelIndex: int = -1
    ) -> Any:
        raise NotImplementedError("C++ UNetConnection::CreateChannel: Engine.lib")


__all__ = [
    "DO_ENABLE_NET_TEST",
    "FDownloadInfo",
    "MAX_CHANNELS",
    "MAX_PROTOCOL_VERSION",
    "MIN_PROTOCOL_VERSION",
    "UNetConnection",
    "DelayedPacket",
    "EConnectionState",
]
