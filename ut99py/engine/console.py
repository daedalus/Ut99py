"""Port of Engine/Inc/UnCon.h (8 declared symbols).

Viewport console: UConsole (UObject, FOutputDevice, DECLARE_CLASS
CLASS_Transient, Engine) plus its script-event parameter structs. Referenced
types live elsewhere: UViewport/UCanvas (engine/camera.py), UTexture/UFont
(engine/texture.py), AZoneInfo (engine/classes.py); APlayerReplicationInfo is
not yet ported. C++ method bodies raise NotImplementedError; inline bodies
(event wrappers, IsTimeDemo) are ported per the header. Event dispatch calls
ProcessEvent/FindFunctionChecked following the core/corobj.py pattern.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ..core import UObject, FOutputDevice, FName
from ..core.types import ENAME_Log
from ..core.template import FStringNoInit

if TYPE_CHECKING:
    from .camera import UViewport, UCanvas
    from .texture import UTexture, UFont
    from .classes import AZoneInfo

_ENGINE_LIB = "Engine.lib (Engine/Src absent from the source drop)"


class UConsole_eventMessage_Parms:
    """Parameters for UConsole::eventMessage (UnCon.h:15-21)."""

    def __init__(self) -> None:
        self.PRI: Optional[Any] = None  # APlayerReplicationInfo (not ported)
        self.S: str = ""
        self.PZone: Optional["AZoneInfo"] = None
        self.N: FName = FName()


class UConsole_eventConnectFailure_Parms:
    """Parameters for UConsole::eventConnectFailure (UnCon.h:22-26)."""

    def __init__(self) -> None:
        self.FailCode: str = ""
        self.URL: str = ""


# Anonymous inline structs lifted from the event bodies (UnCon.h:56, 72, 76,
# 94, 98).
class UConsole_eventTick_Parms:
    def __init__(self) -> None:
        self.DeltaTime: float = 0.0


class UConsole_eventPostRender_Parms:
    def __init__(self) -> None:
        self.C: Optional[UCanvas] = None


class UConsole_eventPreRender_Parms:
    def __init__(self) -> None:
        self.C: Optional[UCanvas] = None


class UConsole_eventKeyType_Parms:
    def __init__(self) -> None:
        self.Key: int = 0
        self.ReturnValue: int = 0


class UConsole_eventKeyEvent_Parms:
    def __init__(self) -> None:
        self.Key: int = 0
        self.Action: int = 0
        self.Delta: float = 0.0
        self.ReturnValue: int = 0


class UConsole(UObject, FOutputDevice):
    """Viewport console (UnCon.h:27). Transient (CLASS_Transient)."""

    # Constants (UnCon.h:112-114).
    MAX_BORDER: int = 6
    MAX_LINES: int = 64
    MAX_HISTORY: int = 16

    def __init__(self) -> None:
        super().__init__()
        # Variables (UnCon.h:117-172). The C++ constructor is in Engine.lib;
        # fields are zero/empty-initialized as in UE1 object allocation.
        self.Viewport: Optional[UViewport] = None
        self.HistoryTop: int = 0
        self.HistoryBot: int = 0
        self.HistoryCur: int = 0
        self.TypedStr: FStringNoInit = FStringNoInit()
        self.History: list[str] = [FStringNoInit() for _ in range(self.MAX_HISTORY)]
        self.Scrollback: int = 0
        self.numLines: int = 0
        self.TopLine: int = 0
        self.TextLines: int = 0
        self.MsgTime: float = 0.0
        self.MsgTickTime: float = 0.0
        self.MsgText: list[str] = [FStringNoInit() for _ in range(self.MAX_LINES)]
        self.MsgType: list[FName] = [FName() for _ in range(self.MAX_LINES)]
        self.MsgPlayer: list[Optional[Any]] = [None] * self.MAX_LINES
        self.MsgTick: list[float] = [0.0] * self.MAX_LINES
        self.BorderSize: int = 0
        self.ConsoleLines: int = 0
        self.BorderLines: int = 0
        self.BorderPixels: int = 0
        self.ConsolePos: float = 0.0
        self.ConsoleDest: float = 0.0
        self.FrameX: float = 0.0
        self.FrameY: float = 0.0
        self.ConBackground: Optional[UTexture] = None
        self.Border: Optional[UTexture] = None
        # BITFIELD members (UnCon.h:146-152, GCC_PACK(4) has no Python
        # equivalent).
        self.bNoStuff: bool = False
        self.bTyping: bool = False
        self.bNoDrawWorld: bool = False
        self.bTimeDemo: bool = False
        self.bStartTimeDemo: bool = False
        self.bRestartTimeDemo: bool = False
        self.bSaveTimeDemoToFile: bool = False
        self.StartTime: float = 0.0
        self.ExtraTime: float = 0.0
        self.LastFrameTime: float = 0.0
        self.LastSecondStartTime: float = 0.0
        self.FrameCount: int = 0
        self.LastSecondFrameCount: int = 0
        self.MinFPS: float = 0.0
        self.MaxFPS: float = 0.0
        self.LastSecFPS: float = 0.0
        self.Font: Optional[UFont] = None
        self.LoadingMessage: FStringNoInit = FStringNoInit()
        self.SavingMessage: FStringNoInit = FStringNoInit()
        self.ConnectingMessage: FStringNoInit = FStringNoInit()
        self.PausedMessage: FStringNoInit = FStringNoInit()
        self.PrecachingMessage: FStringNoInit = FStringNoInit()
        self.FrameRateText: FStringNoInit = FStringNoInit()
        self.AvgText: FStringNoInit = FStringNoInit()
        self.LastSecText: FStringNoInit = FStringNoInit()
        self.MinText: FStringNoInit = FStringNoInit()
        self.MaxText: FStringNoInit = FStringNoInit()
        self.fpsText: FStringNoInit = FStringNoInit()
        self.SecondsText: FStringNoInit = FStringNoInit()
        self.FramesText: FStringNoInit = FStringNoInit()

    # UConsole interface (UnCon.h:32-38; bodies in Engine.lib).
    def _Init(self, Viewport: UViewport) -> None:
        raise NotImplementedError(f"C++ UConsole::_Init: {_ENGINE_LIB}")

    def PreRender(self, Frame: Any) -> None:
        raise NotImplementedError(f"C++ UConsole::PreRender: {_ENGINE_LIB}")

    def PostRender(self, Frame: Any) -> None:
        raise NotImplementedError(f"C++ UConsole::PostRender: {_ENGINE_LIB}")

    def serialize(self, Data: str, MsgType: FName = ENAME_Log) -> None:
        raise NotImplementedError(f"C++ UConsole::Serialize: {_ENGINE_LIB}")

    def GetDrawWorld(self) -> bool:
        raise NotImplementedError(f"C++ UConsole::GetDrawWorld: {_ENGINE_LIB}")

    # Natives (UnCon.h:41-42; thunks in Engine.lib).
    def execConsoleCommand(self, Parms: Any) -> None:
        raise NotImplementedError(f"C++ native execConsoleCommand: {_ENGINE_LIB}")

    def execSaveTimeDemo(self, Parms: Any) -> None:
        raise NotImplementedError(f"C++ native execSaveTimeDemo: {_ENGINE_LIB}")

    # Script events (UnCon.h:45-103; dispatch via ProcessEvent like
    # core/corobj.py eventMain).
    def eventMessage(self, PRI: Any, S: str, PZone: "AZoneInfo", Name: FName) -> None:
        Parms = UConsole_eventMessage_Parms()
        Parms.PRI = PRI
        Parms.S = S
        Parms.PZone = PZone
        Parms.N = Name
        self.ProcessEvent(self.FindFunctionChecked("NAME_Message"), Parms)

    def eventTick(self, DeltaTime: float) -> None:
        Parms = UConsole_eventTick_Parms()
        Parms.DeltaTime = DeltaTime
        self.ProcessEvent(self.FindFunctionChecked("ENGINE_Tick"), Parms)

    def eventVideoChange(self) -> None:
        self.ProcessEvent(self.FindFunctionChecked("NAME_VideoChange"), None)

    def eventPostRender(self, C: UCanvas) -> None:
        Parms = UConsole_eventPostRender_Parms()
        Parms.C = C
        self.ProcessEvent(self.FindFunctionChecked("ENGINE_PostRender"), Parms)

    def eventPreRender(self, C: UCanvas) -> None:
        Parms = UConsole_eventPreRender_Parms()
        Parms.C = C
        self.ProcessEvent(self.FindFunctionChecked("ENGINE_PreRender"), Parms)

    def eventKeyType(self, Key: int) -> int:
        Parms = UConsole_eventKeyType_Parms()
        Parms.Key = Key
        self.ProcessEvent(self.FindFunctionChecked("NAME_KeyType"), Parms)
        return Parms.ReturnValue

    def eventKeyEvent(self, Key: int, Action: int, Delta: float) -> int:
        Parms = UConsole_eventKeyEvent_Parms()
        Parms.Key = Key
        Parms.Action = Action
        Parms.Delta = Delta
        self.ProcessEvent(self.FindFunctionChecked("NAME_KeyEvent"), Parms)
        return Parms.ReturnValue

    def eventNotifyLevelChange(self) -> None:
        self.ProcessEvent(self.FindFunctionChecked("NAME_NotifyLevelChange"), None)

    def eventConnectFailure(self, FailCode: str, URL: str) -> None:
        Parms = UConsole_eventConnectFailure_Parms()
        Parms.FailCode = FailCode
        Parms.URL = URL
        self.ProcessEvent(self.FindFunctionChecked("NAME_ConnectFailure"), Parms)

    def IsTimeDemo(self) -> bool:
        # UnCon.h:104-107 inline: return bTimeDemo.
        return self.bTimeDemo


__all__ = [
    "UConsole",
    "UConsole_eventMessage_Parms",
    "UConsole_eventConnectFailure_Parms",
    "UConsole_eventTick_Parms",
    "UConsole_eventPostRender_Parms",
    "UConsole_eventPreRender_Parms",
    "UConsole_eventKeyType_Parms",
    "UConsole_eventKeyEvent_Parms",
]
