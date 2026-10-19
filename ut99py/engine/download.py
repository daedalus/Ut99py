"""Port of Engine/Inc/UnDownload.h (2 declared symbols).

UDownload (UObject abstract) + UChannelDownload subclass.
Members per header; all method bodies raise NotImplementedError("Engine.lib").
NO_DEFAULT_CONSTRUCTOR markers raise on constructors.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import UObject, FArchive
from ..engine import UNetConnection


class UDownload(UObject):
    """UDownload (UnDownload.h:15-49)"""
    def __init__(self) -> None:
        # NO_DEFAULT_CONSTRUCTOR: body in Engine.lib -> raise.
        raise NotImplementedError("C++ UDownload constructor: Engine.lib")

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UDownload::StaticConstructor: Engine.lib")

    def Destroy(self) -> None:
        raise NotImplementedError("C++ UDownload::Destroy: Engine.lib")

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UDownload::Serialize: Engine.lib")

    def TrySkipFile(self) -> bool:
        raise NotImplementedError("C++ UDownload::TrySkipFile: Engine.lib")

    def ReceiveFile(self, connection: UNetConnection, package_index: int, params: str = "", compression: bool = False) -> None:
        raise NotImplementedError("C++ UDownload::ReceiveFile: Engine.lib")

    def ReceiveData(self, data: Any, count: int) -> None:
        raise NotImplementedError("C++ UDownload::ReceiveData: Engine.lib")

    def Tick(self) -> None:
        pass  # virtual void Tick() {}

    def DownloadError(self, error: str) -> None:
        raise NotImplementedError("C++ UDownload::DownloadError: Engine.lib")

    def DownloadDone(self) -> None:
        raise NotImplementedError("C++ UDownload::DownloadDone: Engine.lib")

    # Member defaults (for subclass use when constructed via lib path).
    Connection: Optional[UNetConnection] = None
    PackageIndex: int = 0
    Info: Any = None  # FPackageInfo*
    DownloadParams: str = ""
    UseCompression: bool = False
    RecvFileAr: Optional[FArchive] = None
    TempFilename: str = ""
    Error: str = ""
    Transfered: int = 0
    SkippedFile: bool = False
    IsCompressed: bool = False


class UChannelDownload(UDownload):
    """UChannelDownload (UnDownload.h:52-70)"""
    def __init__(self) -> None:
        # NO_DEFAULT_CONSTRUCTOR: body in Engine.lib -> raise.
        raise NotImplementedError("C++ UChannelDownload constructor: Engine.lib")

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UChannelDownload::StaticConstructor: Engine.lib")

    def Destroy(self) -> None:
        raise NotImplementedError("C++ UChannelDownload::Destroy: Engine.lib")

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UChannelDownload::Serialize: Engine.lib")

    def ReceiveFile(self, connection: UNetConnection, package_index: int, params: str = "", compression: bool = False) -> None:
        raise NotImplementedError("C++ UChannelDownload::ReceiveFile: Engine.lib")

    def TrySkipFile(self) -> bool:
        raise NotImplementedError("C++ UChannelDownload::TrySkipFile: Engine.lib")

    Ch: Any = None  # UFileChannel*


__all__ = ["UDownload", "UChannelDownload"]
