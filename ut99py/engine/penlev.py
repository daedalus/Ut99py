"""Port of Engine/Inc/UnPenLev.h (2 declared symbols).

UPendingLevel (abstract) + UNetPendingLevel.
All bodies raise NotImplementedError("Engine.lib").
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import UObject
from ..engine import UEngine, UNetDriver


class UPendingLevel(UObject):
    """UPendingLevel (UnPenLev.h:15-55)"""
    def __init__(self) -> None:
        # NO_DEFAULT_CONSTRUCTOR: body in Engine.lib -> raise.
        raise NotImplementedError("C++ UPendingLevel constructor: Engine.lib")

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UPendingLevel::StaticConstructor: Engine.lib")

    def Tick(self, delta_time: float) -> None:
        raise NotImplementedError("C++ UPendingLevel::Tick: Engine.lib")

    def GetDriver(self) -> Any:
        raise NotImplementedError("C++ UPendingLevel::GetDriver: Engine.lib")

    def SendJoin(self) -> None:
        raise NotImplementedError("C++ UPendingLevel::SendJoin: Engine.lib")

    def TrySkipFile(self) -> bool:
        raise NotImplementedError("C++ UPendingLevel::TrySkipFile: Engine.lib")

    def __init__(self, engine: Any = None, url: Any = None) -> None:
        raise NotImplementedError("C++ UPendingLevel(engine,url): Engine.lib")


class UNetPendingLevel(UPendingLevel):
    """UNetPendingLevel (UnPenLev.h:57-87)"""

    def __init__(self, engine: Any = None, url: Any = None) -> None:
        super().__init__()
        self.Success: bool = False
        self.SentJoin: bool = False
        self.LonePlayer: bool = False
        self.FilesNeeded: int = 0
        self.Error: str = ""
        self.FailCode: str = ""
        self.FailURL: str = ""

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UNetPendingLevel::StaticConstructor: Engine.lib")

    def Tick(self, delta_time: float) -> None:
        raise NotImplementedError("C++ UNetPendingLevel::Tick: Engine.lib")

    def GetDriver(self) -> Any:
        return self.NetDriver

    def SendJoin(self) -> None:
        raise NotImplementedError("C++ UNetPendingLevel::SendJoin: Engine.lib")

    def TrySkipFile(self) -> bool:
        raise NotImplementedError("C++ UNetPendingLevel::TrySkipFile: Engine.lib")

    def NotifyAcceptingConnection(self) -> int:
        raise NotImplementedError("C++ UNetPendingLevel::NotifyAcceptingConnection: Engine.lib")

    def NotifyAcceptedConnection(self, connection: Any) -> None:
        raise NotImplementedError("C++ UNetPendingLevel::NotifyAcceptedConnection: Engine.lib")

    def NotifyAcceptingChannel(self, channel: Any) -> bool:
        raise NotImplementedError("C++ UNetPendingLevel::NotifyAcceptingChannel: Engine.lib")

    def NotifyGetLevel(self) -> Any:
        raise NotImplementedError("C++ UNetPendingLevel::NotifyGetLevel: Engine.lib")

    def NotifyReceivedText(self, connection: Any, text: str) -> None:
        raise NotImplementedError("C++ UNetPendingLevel::NotifyReceivedText: Engine.lib")

    def NotifyReceivedFile(self, connection: Any, package_index: int, error: str, skipped: bool) -> None:
        raise NotImplementedError("C++ UNetPendingLevel::NotifyReceivedFile: Engine.lib")

    def NotifySendingFile(self, connection: Any, guid: Any) -> bool:
        raise NotImplementedError("C++ UNetPendingLevel::NotifySendingFile: Engine.lib")

    def ReceiveNextFile(self, connection: Any) -> None:
        raise NotImplementedError("C++ UNetPendingLevel::ReceiveNextFile: Engine.lib")