"""Port of Core/Inc/UnCorObj.h core object definitions.

Classes:
- UPackage (CORE_API) : UObject
- USubsystem (CORE_API) : UObject, FExec (abstract)
- UCommandlet (CORE_API) : UObject (abstract)
- ULanguage (CORE_API) : UObject (abstract)
- UTextBuffer (CORE_API) : UObject, FOutputDevice
- USystem (CORE_API) : USubsystem

Plus UCommandlet_eventMain_Parms struct.
"""

from __future__ import annotations

from typing import Optional, Any

from .objects import (
    UObject,
    USubsystem,
    FOutputDevice,
)
from .template import FStringNoInit


class UCommandlet_eventMain_Parms:
    """Parameters for UCommandlet::eventMain."""

    def __init__(self) -> None:
        self.InParms: str = ""
        self.ReturnValue: int = 0


class UPackage(UObject):
    """A package."""

    # Variables.
    DllHandle: Optional[Any] = None
    AttemptedBind: bool = False
    PackageFlags: int = 0

    def __init__(self) -> None:
        super().__init__()

    def Destroy(self) -> None:
        pass

    def Serialize(self, Ar) -> None:
        pass

    def GetDllExport(self, ExportName: str, Checked: bool) -> Optional[Any]:
        pass


class UCommandlet(UObject):
    """A command-line applet."""

    HelpCmd: str = ""
    HelpOneLiner: str = ""
    HelpUsage: str = ""
    HelpWebLink: str = ""
    HelpParm: list[str] = []
    HelpDesc: list[str] = []
    LogToStdout: bool = False
    IsServer: bool = False
    IsClient: bool = False
    IsEditor: bool = False
    LazyLoad: bool = False
    ShowErrorCount: bool = False
    ShowBanner: bool = False

    def __init__(self) -> None:
        super().__init__()
        self.HelpParm = [FStringNoInit() for _ in range(16)]
        self.HelpDesc = [FStringNoInit() for _ in range(16)]

    def Main(self, Parms: str) -> int:
        """Main entry point."""
        return 0

    def eventMain(self, InParms: str) -> int:
        """Executes Main with parsed parameters."""
        Parms = UCommandlet_eventMain_Parms()
        Parms.InParms = InParms
        self.ProcessEvent(self.FindFunctionChecked("NAME_Main"), Parms)
        return Parms.ReturnValue

    def execMain(self, Parms: str) -> None:
        """Delegate for execMain."""
        self.eventMain(Parms)


class ULanguage(UObject):
    """A language (special case placeholder class)."""

    SuperLanguage: Optional["ULanguage"] = None

    def __init__(self) -> None:
        super().__init__()


class UTextBuffer(UObject, FOutputDevice):
    """An object that holds text, NULL-terminated."""

    def __init__(self, Str: str = "") -> None:
        super().__init__()
        self.Pos: int = 0
        self.Top: int = 0
        self.Text: str = Str

    def Serialize(self, Ar) -> None:
        pass

    def serialize(self, Data: str, Event) -> None:
        self.Text += Data


class USystem(USubsystem):
    """A system."""

    LicenseeMode: int = 0
    PurgeCacheDays: int = 0
    SavePath: str = ""
    CachePath: str = ""
    CacheExt: str = ""
    Paths: list[str] = []
    Suppress: list[str] = []

    def __init__(self) -> None:
        super().__init__()

    def StaticConstructor(self) -> None:
        pass

    def Exec(self, Cmd: str, Ar: Optional[Any] = None) -> bool:
        pass
