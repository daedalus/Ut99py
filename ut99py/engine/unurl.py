"""Port of Engine/Inc/UnURL.h (1 declared symbol).

FURL: a uniform resource locator (protocol, host, port, map, options).
Every method body lives in UnURL.cpp, so all of them raise NotImplementedError.
"""

from __future__ import annotations
from typing import Any, Optional
from ..core import FString, TArray


class FURL:
    """FURL (UnURL.h:16-61)"""

    # Statics (UnURL.h:31-40). FURL::StaticInit fills them from the URL
    # config section; they stay empty until that runs.
    DefaultProtocol: FString = FString()
    DefaultProtocolDescription: FString = FString()
    DefaultName: FString = FString()
    DefaultMap: FString = FString()
    DefaultLocalMap: FString = FString()
    DefaultHost: FString = FString()
    DefaultPortal: FString = FString()
    DefaultMapExt: FString = FString()
    DefaultSaveExt: FString = FString()
    DefaultPort: int = 0

    def __init__(self, filename: Optional[str] = None) -> None:
        # URL components (UnURL.h:19-25).
        self.Protocol: FString = FString(FURL.DefaultProtocol)
        self.Host: FString = FString(FURL.DefaultHost)
        self.Port: int = FURL.DefaultPort
        self.Map: FString = FString(filename if filename else FURL.DefaultMap)
        self.Op: TArray = TArray()
        self.Portal: FString = FString(FURL.DefaultPortal)
        # Status (UnURL.h:28).
        self.Valid: bool = True

    @staticmethod
    def StaticInit() -> None:
        raise NotImplementedError("C++ FURL::StaticInit: Engine.lib")

    @staticmethod
    def StaticExit() -> None:
        raise NotImplementedError("C++ FURL::StaticExit: Engine.lib")

    def IsInternal(self) -> bool:
        raise NotImplementedError("C++ FURL::IsInternal: Engine.lib")

    def IsLocalInternal(self) -> bool:
        raise NotImplementedError("C++ FURL::IsLocalInternal: Engine.lib")

    def HasOption(self, Test: str) -> bool:
        raise NotImplementedError("C++ FURL::HasOption: Engine.lib")

    def GetOption(self, Match: str, Default: Optional[str] = None) -> Optional[str]:
        raise NotImplementedError("C++ FURL::GetOption: Engine.lib")

    def LoadURLConfig(self, Section: str, Filename: Optional[str] = None) -> None:
        raise NotImplementedError("C++ FURL::LoadURLConfig: Engine.lib")

    def SaveURLConfig(
        self, Section: str, Item: str, Filename: Optional[str] = None
    ) -> None:
        raise NotImplementedError("C++ FURL::SaveURLConfig: Engine.lib")

    def AddOption(self, Str: str) -> None:
        raise NotImplementedError("C++ FURL::AddOption: Engine.lib")

    def String(self, FullyQualified: bool = False) -> FString:
        raise NotImplementedError("C++ FURL::String: Engine.lib")

    def serialize(self, Ar: Any) -> Any:
        """C++ friend operator<<(FArchive& Ar, FURL& U) (UnURL.cpp:62-68).

        The C++ writes Protocol, Host, Map, Portal, Op, Port and Valid in that
        order; Valid is a UBOOL, which is an INT in UE1.
        """
        self.Protocol = Ar.serialize_str(self.Protocol)
        self.Host = Ar.serialize_str(self.Host)
        self.Map = Ar.serialize_str(self.Map)
        self.Portal = Ar.serialize_str(self.Portal)
        self.Op = Ar.serialize_tarray(self.Op, element=FString)
        self.Port = Ar.serialize_int32(self.Port)
        self.Valid = Ar.serialize_int32(1 if self.Valid else 0) != 0
        return Ar

    def __eq__(self, Other: "FURL") -> bool:
        """C++ operator==(const FURL& Other) const (UnURL.h:60)."""
        raise NotImplementedError("C++ FURL::operator==: Engine.lib")


__all__ = ["FURL"]
