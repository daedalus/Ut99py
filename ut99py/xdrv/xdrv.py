"""Port of XDrv/Inc/XDrv.h (X viewport and platform driver).

Classes: UXClient, UXViewport.
Enums: EXViewportStatus
"""

from __future__ import annotations


class EXViewportStatus:
    X_ViewportOpening = 0
    X_ViewportNormal = 1
    X_ViewportClosing = 2


class UXClient:
    def __init__(self) -> None:
        self.StartupFullscreen: bool = False
        self.SlowVideoBuffering: bool = False
        self.DGAMouseEnabled: bool = False
        self.XDisplay: object | None = None
        self.InMenuLoop: bool = False
        self.ConfigReturnFullscreen: bool = False
        self.NormalMouseInfo: list[int] = []
        self.CaptureMouseInfo: list[int] = []

    def Init(self, engine) -> None:
        pass

    def ShowViewportWindows(self, show_flags: int, do_show: int) -> None:
        pass

    def EnableViewportWindows(self, show_flags: int, do_enable: int) -> None:
        pass

    def Exec(self, cmd: str, error: object = None) -> bool:
        return False

    def Tick(self) -> None:
        pass

    def MakeCurrent(self, viewport) -> None:
        pass

    def NewViewport(self, name: str):
        return None

    def Destroy(self) -> None:
        pass

    def NotifyDestroy(self, src: object) -> None:
        pass

    def StaticConstructor(self) -> None:
        pass
