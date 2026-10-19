"""Port of Engine/Inc/UnDemoPenLev.h (1 declared symbol).

UDemoPlayPendingLevel (extends UPendingLevel) - all method bodies raised NotImplementedError("Engine.lib");
trivial inline bodies from UnDemoPenLev.h (NotifyAcceptingConnection etc.) are preserved where declared.
NO_DEFAULT_CONSTRUCTOR raises on constructors.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import UObject
from ..engine import UPendingLevel, UNetDriver

ACCEPTC_Reject = 0


class UDemoPlayPendingLevel(UPendingLevel):
    """UDemoPlayPendingLevel (UnDemoPenLev.h:22-62)."""
    def __init__(self, engine: Any = None, url: Any = None) -> None:
        # NO_DEFAULT_CONSTRUCTOR: body in Engine.lib -> raise.
        raise NotImplementedError("C++ UDemoPlayPendingLevel constructor: Engine.lib")

    def NotifyAcceptingConnection(self) -> int:
        """inline: {return ACCEPTC_Reject;}."""
        return ACCEPTC_Reject

    def NotifyAcceptedConnection(self, Connection: Any) -> None:
        """inline: {} -> nothing."""
        pass

    def NotifyAcceptingChannel(self, Channel: Any) -> bool:
        """inline: {return 1;}"""
        return True

    def NotifyGetLevel(self) -> Any:
        """inline: NOT IMPLEMENTED IN THIS HEADER (body in Engine.lib)."""
        raise NotImplementedError("C++ UDemoPlayPendingLevel::NotifyGetLevel: Engine.lib")

    def NotifyReceivedText(self, Connection: Any, Text: str) -> None:
        """NOT IMPLEMENTED IN THIS HEADER (body in Engine.lib)."""
        raise NotImplementedError("C++ UDemoPlayPendingLevel::NotifyReceivedText: Engine.lib")

    def NotifyReceivedFile(self, Connection: Any, PackageIndex: int, Error: str, Skipped: bool) -> None:
        """inline: {} -> nothing."""
        pass

    def NotifySendingFile(self, Connection: Any, GUID: Any) -> bool:
        """inline: {return 0;}"""
        return False

    def Tick(self, DeltaTime: float) -> None:
        """inline: empty body."""
        pass

    def GetDriver(self) -> Optional[UNetDriver]:
        """inline: {return DemoRecDriver;}"""
        return getattr(self, 'DemoRecDriver', None)

    def SendJoin(self) -> None:
        """inline: {SentJoin = 1;}"""
        self.SentJoin = True

    def TrySkipFile(self) -> bool:
        """inline: {return 0;}"""
        return False

    __all__ = ["UDemoPlayPendingLevel", "ACCEPTC_Reject"]