"""Port of Core/Inc/FOutputDeviceAnsiError.h (ANSI stdout error output device).

Classes:
- FOutputDeviceAnsiError : FOutputDeviceError
"""

from __future__ import annotations


class FOutputDeviceAnsiError:
    def __init__(self) -> None:
        self.ErrorPos: int = 0
        self.ErrorType: str = "None"

    def LocalPrint(self, message: str) -> None:
        print(message)

    def Serialize(self, msg: str, event: str) -> None:
        pass
