"""Port of Engine/Inc/UnBunch.h (2 declared symbols).

FOutBunch (FBitWriter) and FInBunch (FBitReader) with full member sets.
All method bodies raise NotImplementedError("Engine.lib").
"""
from __future__ import annotations
from typing import Any, Optional
from ..core.bits import FBitWriter, FBitReader
from ..core import FName, UObject, FArchive, FTime
from ..engine import UChannel, UNetConnection


class FOutBunch(FBitWriter):
    """FOutBunch (UnBunch.h:15-30)"""
    def __init__(self, in_channel: Optional["UChannel"] = None, b_close: bool = False, max_bits: int = 1024):
        super().__init__(max_bits)
        self.Next: Optional["FOutBunch"] = None
        self.Channel: Optional["UChannel"] = in_channel
        self.Time: FTime = FTime()
        self.ReceivedAck: bool = False
        self.ChIndex: int = 0
        self.ChType: int = 0
        self.ChSequence: int = 0
        self.PacketId: int = 0
        self.bOpen: int = 0
        self.bClose: int = 1 if b_close else 0
        self.bReliable: int = 0

    def __lshift__(self, name):
        raise NotImplementedError("C++ FOutBunch::operator<< FName: Engine.lib")

    def __lshift_obj__(self, obj):
        raise NotImplementedError("C++ FOutBunch::operator<< UObject: Engine.lib")


class FInBunch(FBitReader):
    """FInBunch (UnBunch.h:33-48)"""
    def __init__(self, connection: "UNetConnection", src: Optional[bytes] = None, count_bits: int = 0) -> None:
        super().__init__(src, count_bits)
        self.PacketId: int = 0
        self.Next: Optional["FInBunch"] = None
        self.Connection: Optional["UNetConnection"] = connection
        self.ChIndex: int = 0
        self.ChType: int = 0
        self.ChSequence: int = 0
        self.bOpen: int = 0
        self.bClose: int = 0
        self.bReliable: int = 0

    def __lshift__(self, name):
        raise NotImplementedError("C++ FInBunch::operator<< FName: Engine.lib")

    def __lshift_obj__(self, obj):
        raise NotImplementedError("C++ FInBunch::operator<< UObject: Engine.lib")


__all__ = ["FOutBunch", "FInBunch"]