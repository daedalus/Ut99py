"""Port of Setup/Inc/USetupDefinitionWindows.h (Windows-specific setup).

Classes:
- USetupShortcut : USetupObject
- USetupGroupWindows : USetupGroup
- USetupDefinitionWindows : USetupDefinition
"""

from __future__ import annotations
from typing import Optional


class USetupObject:
    pass


class USetupGroup:
    pass


class USetupDefinition:
    pass


class USetupShortcut(USetupObject):
    def __init__(self) -> None:
        self.Template: str = ""
        self.WorkingDirectory: str = ""
        self.Command: str = ""
        self.Parameters: str = ""
        self.Icon: str = ""
        self.Caption: str = ""


class USetupGroupWindows(USetupGroup):
    def __init__(self) -> None:
        self.DirectXHook: str = ""
        self.WinRegistry: list[str] = []
        self.Shortcut: list[str] = []


class USetupDefinitionWindows(USetupDefinition):
    def __init__(self) -> None:
        self.WinPath: str = ""
        self.WinSysPath: str = ""
        self.DesktopPath: str = ""
        self.ProgramsPath: str = ""
        self.FavoritesPath: str = ""
        self.StartupPath: str = ""
        self.CommonProgramsPath: str = ""
        self.CommonFavoritesPath: str = ""
        self.CommonStartupPath: str = ""
        self.hWndManager: Optional[object] = None
