"""Port of Core/Inc/FOutputDeviceWindowsError.h (Windows error output device).

Classes:
- FOutputDeviceWindowsError : FOutputDeviceError
"""

from __future__ import annotations


class FOutputDeviceWindowsError:
    def __init__(self) -> None:
        pass

    def Serialize(self, msg: str, event: str) -> None:
        pass

    def Flush(self) -> None:
        pass
