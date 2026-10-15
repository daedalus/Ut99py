"""Port of Core/Inc/FOutputDeviceNull.h (null output device).

Classes:
- FOutputDeviceNull : FOutputDevice
"""

from __future__ import annotations


class FOutputDeviceNull:
    def __init__(self) -> None:
        pass

    def Serialize(self, msg: str, event: str) -> None:
        pass

    def Flush(self) -> None:
        pass
