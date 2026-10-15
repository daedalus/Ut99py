"""Port of Core/Inc/FOutputDeviceFile.h (file output device).

Classes:
- FOutputDeviceFile : FOutputDevice
"""

from __future__ import annotations


class FOutputDeviceFile:
    def __init__(self) -> None:
        pass

    def Serialize(self, msg: str, event: str) -> None:
        pass

    def Flush(self) -> None:
        pass
