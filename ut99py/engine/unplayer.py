"""Port of Engine/Inc/UnPlayer.h (1 declared symbol).

UPlayer: base class of UViewport (local players) and UNetConnection.
Every method body lives in UnPlayer.cpp, so all of them raise.
"""

from __future__ import annotations
from typing import Any, Optional
from ..core import FOutputDevice, UObject
from ..core.system import FExec


class UPlayer(UObject, FOutputDevice, FExec):
    """UPlayer (UnPlayer.h:16-44)"""

    def __init__(self) -> None:
        super().__init__()
        # Objects (UnPlayer.h:21-22).
        self.Actor: Optional[Any] = None  # APlayerPawn*
        self.Console: Optional[Any] = None  # UConsole*
        # Bitfields (UnPlayer.h:24-26).
        self.bWindowsMouseAvailable: bool = False
        self.bShowWindowsMouse: bool = False
        self.bSuspendPrecaching: bool = False
        self.WindowsMouseX: float = 0.0
        self.WindowsMouseY: float = 0.0
        self.CurrentNetSpeed: int = 0
        self.ConfiguredInternetSpeed: int = 0
        self.ConfiguredLanSpeed: int = 0
        self.SelectedCursor: int = 0  # BYTE
        # UPlayer() body is in UnPlayer.cpp.
        raise NotImplementedError("C++ UPlayer constructor: Engine.lib")

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UPlayer::Serialize: Engine.lib")

    def Destroy(self) -> None:
        raise NotImplementedError("C++ UPlayer::Destroy: Engine.lib")

    def Exec(self, Cmd: str, Ar: Optional[Any] = None) -> bool:
        raise NotImplementedError("C++ UPlayer::Exec: Engine.lib")

    def ReadInput(self, DeltaSeconds: float) -> None:
        """UPlayer::ReadInput (UnPlayer.h:43) - pure virtual."""
        raise NotImplementedError("C++ UPlayer::ReadInput: Engine.lib")


__all__ = ["UPlayer"]
