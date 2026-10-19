"""Port of Engine/Inc/UnEngineWin.h (8 declared symbols).

Windows-specific engine startup and UI: the config wizard (WConfigWizard and
its WConfigPage* pages), the console exec hook (FExecHook), and the mplayer
launcher. Bases WWizardDialog/WWizardPage (Window/Inc/Window.h) and window
controls (WLabel, WButton, ...) are not yet ported; Win32-bound bodies
(dialogs, registry, ShellExecute, splash dirs) raise NotImplementedError.
Portable logic (page chaining, button delegates, exec-hook notification) is
ported inline per the header. The static InitEngine/MainLoop startup (Win32
message pump) is not ported; the Linux/X11 loop lives in ut99py/__main__.py
and graphics/window_qt.py.
"""

from __future__ import annotations

from typing import Any, Optional

from ..core.system import FExec
from ..window import FNotifyHook

# UnEngineWin.h:487-488 (#defines used by LaunchMplayer).
MPI_FILE = "mput.mpi"
MPLAYNOW_EXE = "mplaynow.exe"

# UnEngineWin.h:72: filled by InitSysDirs via Win32 GetSystemDirectory etc.
SysDir = ""
WinDir = ""
ThisFile = ""


def init_sys_dirs() -> None:
    # UnEngineWin.h:73-98: Win32 GetSystemDirectory/GetWindowsDirectory/
    # GetModuleFileName.
    raise NotImplementedError("Win32 GetSystemDirectory family")


def get_mplayer_directory() -> str:
    # UnEngineWin.h:489-510: registry lookup under
    # software\mpath\mplayer\main.
    raise NotImplementedError("Win32 registry lookup (RegOpenKeyExX)")


def launch_mplayer() -> None:
    # UnEngineWin.h:512-526: ShellExecuteX of mplaunch.exe/mplaynow.exe.
    raise NotImplementedError("Win32 ShellExecuteX")


class WConfigWizard:
    """Startup config wizard (UnEngineWin.h:101, base WWizardDialog)."""

    def __init__(self) -> None:
        # Controls (WLabel LogoStatic, FWindowsBitmap LogoBitmap) come from
        # Window/Inc/Window.h, not yet ported.
        self.LogoStatic: Optional[Any] = None
        self.LogoBitmap: Optional[Any] = None
        self.Cancel = False
        self.Title = ""
        init_sys_dirs()  # UnEngineWin.h:110-112 ctor.

    def OnInitDialog(self) -> None:
        # UnEngineWin.h:114-124: WM_SETICON/STM_SETIMAGE.
        raise NotImplementedError("Win32 dialog (WM_SETICON/STM_SETIMAGE)")


class WConfigPageFirstTime:
    """Final wizard page (UnEngineWin.h:127, base WWizardPage)."""

    def __init__(self, InOwner: WConfigWizard) -> None:
        self.Owner = InOwner

    def GetNextText(self) -> str:
        # UnEngineWin.h:135-138: LocalizeGeneral("Run", "Startup").
        raise NotImplementedError("Win32 localization (LocalizeGeneral)")

    def GetNext(self) -> Optional[WConfigWizard]:
        # UnEngineWin.h:139-142: Owner->EndDialog(1); return NULL.
        self.Owner.EndDialog(1)
        return None


class WConfigPageSafeOptions:
    """Safe-options page (UnEngineWin.h:146, base WWizardPage)."""

    def __init__(self, InOwner: WConfigWizard) -> None:
        self.Owner = InOwner
        # WButton controls (Window/Inc/Window.h), not yet ported.
        self.NoSoundButton = None
        self.No3DSoundButton = None
        self.No3DVideoButton = None
        self.WindowButton = None
        self.ResButton = None
        self.ResetConfigButton = None
        self.NoProcessorButton = None
        self.NoJoyButton = None

    def OnInitDialog(self) -> None:
        # UnEngineWin.h:163-173: BM_SETCHECK on the checkboxes.
        raise NotImplementedError("Win32 dialog (BM_SETCHECK)")

    def GetNextText(self) -> str:
        # UnEngineWin.h:175-178: LocalizeGeneral("Run", "Startup").
        raise NotImplementedError("Win32 localization (LocalizeGeneral)")

    def GetNext(self) -> Optional[WConfigWizard]:
        # UnEngineWin.h:179-202: builds a command line from checkbox state
        # (BM_GETCHECK) and relaunches ThisFile via ShellExecuteX.
        raise NotImplementedError("Win32 checkbox state + ShellExecuteX")


class WConfigPageDetail:
    """Auto-config detail page (UnEngineWin.h:204, base WWizardPage)."""

    def __init__(self, InOwner: WConfigWizard) -> None:
        self.Owner = InOwner
        self.DetailEdit = None  # WEdit (Window/Inc/Window.h).

    def OnInitDialog(self) -> None:
        # UnEngineWin.h:214-296: hardware probe writing GConfig render,
        # sound, skin, world and resolution settings.
        raise NotImplementedError("hardware auto-config (Win32 dialog)")

    def GetNext(self) -> WConfigPageFirstTime:
        # UnEngineWin.h:300-303.
        return WConfigPageFirstTime(self.Owner)


class WConfigPageDriver:
    """D3D driver info page (UnEngineWin.h:306, base WWizardPage)."""

    def __init__(self, InOwner: WConfigWizard) -> None:
        self.Owner = InOwner
        # WUrlButton/WLabel (Window/Inc/Window.h).
        self.WebButton = None
        self.Card = None

    def OnInitDialog(self) -> None:
        # UnEngineWin.h:318-323: GConfig driver Description + SetText.
        raise NotImplementedError("Win32 dialog (SetText)")

    def GetNext(self) -> WConfigPageDetail:
        # UnEngineWin.h:325-328.
        return WConfigPageDetail(self.Owner)


class WConfigPageRenderer:
    """Render-device selection page (UnEngineWin.h:331, base WWizardPage)."""

    def __init__(self, InOwner: WConfigWizard) -> None:
        self.Owner = InOwner
        # Window controls (Window/Inc/Window.h).
        self.RenderList = None
        self.ShowCompatible = None
        self.ShowAll = None
        self.RenderNote = None
        self.First = 0  # UnEngineWin.h:345.
        self.Classes: list = []  # TArray<FRegistryObjectInfo> (UnEngineWin.h:346).

    def RefreshList(self) -> None:
        # UnEngineWin.h:349-396: registry scan of URenderDevice classes.
        raise NotImplementedError("registry scan (UObject::GetRegistryObjects)")

    def CurrentChange(self) -> None:
        # UnEngineWin.h:397-400: localized driver description.
        raise NotImplementedError("Win32 localization (Localize)")

    def OnPaint(self) -> None:
        # UnEngineWin.h:401-417: spawns ThisFile with testrendev= and waits
        # for Detected.ini.
        raise NotImplementedError("Win32 paint + ShellExecuteX detect")

    def OnCurrent(self) -> None:
        pass  # UnEngineWin.h:418-421: empty guard body.

    def OnInitDialog(self) -> None:
        # UnEngineWin.h:410-417: BM_SETCHECK + delegate wiring.
        raise NotImplementedError("Win32 dialog (BM_SETCHECK)")

    def CurrentDriver(self) -> str:
        # UnEngineWin.h:418-431: maps list selection back to a class path.
        raise NotImplementedError("registry-backed driver lookup")

    def GetNext(self) -> Any:
        # UnEngineWin.h:433-442: saves GameRenderDevice, then branches to
        # WConfigPageDriver (D3D) or WConfigPageDetail.
        raise NotImplementedError("GConfig write + page branch")


class WConfigPageSafeMode:
    """Safe-mode menu page (UnEngineWin.h:444, base WWizardPage)."""

    def __init__(self, InOwner: WConfigWizard) -> None:
        self.Owner = InOwner
        # WCoolButton controls (Window/Inc/Window.h).
        self.RunButton = None
        self.VideoButton = None
        self.SafeModeButton = None
        self.WebButton = None

    def OnRun(self) -> None:
        # UnEngineWin.h:457-459.
        self.Owner.EndDialog(1)

    def OnVideo(self) -> None:
        # UnEngineWin.h:461-463.
        self.Owner.Advance(WConfigPageRenderer(self.Owner))

    def OnSafeMode(self) -> None:
        # UnEngineWin.h:465-467.
        self.Owner.Advance(WConfigPageSafeOptions(self.Owner))

    def OnWeb(self) -> None:
        # UnEngineWin.h:469-472: ShellExecuteX of the localized web page.
        raise NotImplementedError("Win32 ShellExecuteX")

    def GetNextText(self) -> Optional[str]:
        # UnEngineWin.h:474-477: return NULL.
        return None


class FExecHook(FExec, FNotifyHook):
    """Console exec hook (UnEngineWin.h:537, FExec + FNotifyHook)."""

    def __init__(self) -> None:
        super().__init__()
        self.Preferences: Optional[Any] = None  # WConfigProperties.

    def notify_destroy(self, src: Any) -> None:
        # UnEngineWin.h:541-545 inline: if Src==Preferences, Preferences=NULL.
        if src is self.Preferences:
            self.Preferences = None

    def exec_commands(self, cmd: str, ar: Optional[Any] = None) -> bool:
        # UnEngineWin.h:546-681: ShowLog/TakeFocus/EditActor/HideLog/
        # Preferences/MPLAYER/HEAT; all paths touch Win32 windows.
        raise NotImplementedError("Win32 exec hook (ShowLog/EditActor/...)")


__all__ = [
    "MPI_FILE",
    "MPLAYNOW_EXE",
    "SysDir",
    "WinDir",
    "ThisFile",
    "init_sys_dirs",
    "get_mplayer_directory",
    "launch_mplayer",
    "WConfigWizard",
    "WConfigPageFirstTime",
    "WConfigPageSafeOptions",
    "WConfigPageDetail",
    "WConfigPageDriver",
    "WConfigPageRenderer",
    "WConfigPageSafeMode",
    "FExecHook",
]
