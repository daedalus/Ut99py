"""Port of Core/Inc/FOutputDeviceStdout.h (stdout output device).

Classes:
- FOutputDeviceStdout : FOutputDevice
"""

from __future__ import annotations


class FOutputDeviceStdout:
    def __init__(self) -> None:
        pass

    def Serialize(self, msg: str, event: str) -> None:
        print(msg)

    def Flush(self) -> None:
        pass
