"""Port of Engine/Inc/UnDemoRec.h (2 declared symbols).

UDemoRecConnection (UNetConnection subclass) + UDemoRecDriver (UNetDriver subclass).
All method bodies raise NotImplementedError("Engine.lib"); inline getters preserved where declared.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import UObject, FArchive, FOutputDevice, FString
from ..engine import (
    UNetConnection, UNetDriver, ULevel, UURL,
)


class UDemoRecConnection(UNetConnection):
    """UDemoRecConnection (UnDemoRec.h:29-49)"""
    def __init__(self, driver: Any = None, url: Any = None) -> None:
        # NO_DEFAULT_CONSTRUCTOR: body in Engine.lib -> raise.
        raise NotImplementedError("C++ UDemoRecConnection constructor: Engine.lib")

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UDemoRecConnection::StaticConstructor: Engine.lib")

    def LowLevelGetRemoteAddress(self) -> str:
        raise NotImplementedError("C++ UDemoRecConnection::LowLevelGetRemoteAddress: Engine.lib")

    def LowLevelDescribe(self) -> str:
        raise NotImplementedError("C++ UDemoRecConnection::LowLevelDescribe: Engine.lib")

    def LowLevelSend(self, data: Any, count: int) -> None:
        raise NotImplementedError("C++ UDemoRecConnection::LowLevelSend: Engine.lib")

    def IsNetReady(self, saturate: bool) -> bool:
        raise NotImplementedError("C++ UDemoRecConnection::IsNetReady: Engine.lib")

    def FlushNet(self) -> None:
        raise NotImplementedError("C++ UDemoRecConnection::FlushNet: Engine.lib")

    def HandleClientPlayer(self, pawn: Any) -> None:
        raise NotImplementedError("C++ UDemoRecConnection::HandleClientPlayer: Engine.lib")

    def GetDriver(self) -> Optional["UDemoRecDriver"]:
        raise NotImplementedError("C++ UDemoRecConnection::GetDriver: Engine.lib")


class UDemoRecDriver(UNetDriver):
    """UDemoRecDriver (UnDemoRec.h:52-90)"""

    def __init__(self) -> None:
        super().__init__()
        self.DemoFilename: str = ""
        self.DemoSpectatorClass: str = ""
        self.FileAr: Optional[Any] = None  # FArchive*
        self.ClientThirdPerson: bool = False
        self.TimeBased: bool = False
        self.NoFrameCap: bool = False
        self.DemoEnded: bool = False
        self.Loop: bool = False
        self.FrameNum: int = 0
        self.LoopURL: Any = None  # UURL

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UDemoRecDriver::StaticConstructor: Engine.lib")

    def LowLevelDestroy(self) -> None:
        raise NotImplementedError("C++ UDemoRecDriver::LowLevelDestroy: Engine.lib")

    def LowLevelGetNetworkNumber(self) -> str:
        raise NotImplementedError("C++ UDemoRecDriver::LowLevelGetNetworkNumber: Engine.lib")

    def InitConnect(self, notify: Any, connect_url: Any, error: Any) -> bool:
        raise NotImplementedError("C++ UDemoRecDriver::InitConnect: Engine.lib")

    def InitListen(self, notify: Any, connect_url: Any, error: Any) -> bool:
        raise NotImplementedError("C++ UDemoRecDriver::InitListen: Engine.lib")

    def TickDispatch(self, delta_time: float) -> None:
        raise NotImplementedError("C++ UDemoRecDriver::TickDispatch: Engine.lib")

    def Exec(self, cmd: str, ar: Any = None) -> int:
        raise NotImplementedError("C++ UDemoRecDriver::Exec: Engine.lib")

    def InitBase(self, connect: bool, notify: Any, connect_url: Any, error: Any) -> bool:
        raise NotImplementedError("C++ UDemoRecDriver::InitBase: Engine.lib")

    def GetLevel(self) -> Optional[Any]:
        raise NotImplementedError("C++ UDemoRecDriver::GetLevel: Engine.lib")

    def SpawnDemoRecSpectator(self, connection: Any) -> None:
        raise NotImplementedError("C++ UDemoRecDriver::SpawnDemoRecSpectator: Engine.lib")


__all__ = ["UDemoRecConnection", "UDemoRecDriver"]
