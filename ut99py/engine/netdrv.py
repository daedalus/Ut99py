"""Port of Engine/Inc/UnNetDrv.h (2 declared symbols).

UNetDriver (USubsystem) + UPackageMapLevel (UPackageMap subclass).
All bodies raise NotImplementedError("Engine.lib") except constructors/initializers.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import UObject, USubsystem, UPackageMap
from ..core.types import FTime
from ..engine import UNetConnection, AActor


class UPackageMapLevel(UPackageMap):
    """UPackageMapLevel (UnNetDrv.h:14-25)"""

    def __init__(self, connection: Optional[UNetConnection] = None) -> None:
        super().__init__()
        self.Connection: Optional[UNetConnection] = connection

    def CanSerializeObject(self, obj: UObject) -> bool:
        raise NotImplementedError("C++ UPackageMapLevel::CanSerializeObject: Engine.lib")

    def SerializeObject(self, ar: Any, cls: Any, obj: Any) -> bool:
        raise NotImplementedError("C++ UPackageMapLevel::SerializeObject: Engine.lib")


class UNetDriver(USubsystem):
    """UNetDriver (UnNetDrv.h:28-85)"""

    def __init__(self) -> None:
        super().__init__()
        self.ClientConnections: list = []  # TArray<UNetConnection*>
        self.ServerConnection: Optional[UNetConnection] = None
        self.Notify: Optional[Any] = None  # FNetworkNotify*
        self.MasterMap: Optional[Any] = None  # UPackageMap*
        self.Time: FTime = FTime()
        self.ConnectionTimeout: float = 0.0
        self.InitialConnectTimeout: float = 0.0
        self.KeepAliveTime: float = 0.0
        self.RelevantTimeout: float = 0.0
        self.SpawnPrioritySeconds: float = 0.0
        self.ServerTravelPause: float = 0.0
        self.MaxClientRate: int = 0
        self.NetServerMaxTickRate: int = 0
        self.LanServerMaxTickRate: int = 0
        self.AllowDownloads: bool = False
        self.ProfileStats: bool = False
        self.RoleProperty: Any = None  # UProperty*
        self.RemoteRoleProperty: Any = None  # UProperty*
        self.SendCycles: int = 0
        self.RecvCycles: int = 0
        self.MaxDownloadSize: int = 0
        self.DownloadManagers: list = []  # TArray<FString>

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UNetDriver::StaticConstructor: Engine.lib")

    def Destroy(self) -> None:
        raise NotImplementedError("C++ UNetDriver::Destroy: Engine.lib")

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UNetDriver::Serialize: Engine.lib")

    def LowLevelDestroy(self) -> None:
        raise NotImplementedError("C++ UNetDriver::LowLevelDestroy: Engine.lib")

    def LowLevelGetNetworkNumber(self) -> str:
        raise NotImplementedError("C++ UNetDriver::LowLevelGetNetworkNumber: Engine.lib")

    def AssertValid(self) -> None:
        raise NotImplementedError("C++ UNetDriver::AssertValid: Engine.lib")

    def InitConnect(self, notify: Any, connect_url: Any, error: Any) -> bool:
        raise NotImplementedError("C++ UNetDriver::InitConnect: Engine.lib")

    def InitListen(self, notify: Any, listen_url: Any, error: Any) -> bool:
        raise NotImplementedError("C++ UNetDriver::InitListen: Engine.lib")

    def TickFlush(self) -> None:
        raise NotImplementedError("C++ UNetDriver::TickFlush: Engine.lib")

    def TickDispatch(self, delta_time: float) -> None:
        raise NotImplementedError("C++ UNetDriver::TickDispatch: Engine.lib")

    def Exec(self, cmd: str, ar: Any = None) -> bool:
        raise NotImplementedError("C++ UNetDriver::Exec: Engine.lib")

    def NotifyActorDestroyed(self, actor: AActor) -> None:
        raise NotImplementedError("C++ UNetDriver::NotifyActorDestroyed: Engine.lib")


__all__ = ["UNetDriver", "UPackageMapLevel"]
