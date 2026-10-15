"""Port of Core/Inc/FFeedbackContextWindows.h (Windows feedback context).

Classes:
- FFeedbackContextWindows : FFeedbackContext
"""

from __future__ import annotations


class FFeedbackContextWindows:
    """Windows user interface interaction (FFeedbackContextWindows)."""

    def __init__(self) -> None:
        self.SlowTaskCount: int = 0
        self.hWndProgressBar: int = 0
        self.hWndProgressText: int = 0
        self.hWndProgressDlg: int = 0

    def Serialize(self, message: str, event: str) -> None:
        pass

    def YesNof(self, fmt: str, *args) -> bool:
        return False

    def BeginSlowTask(self, task: str, status_window: bool, cancelable: bool) -> None:
        pass
