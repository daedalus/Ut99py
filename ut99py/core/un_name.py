"""Port of Core/Inc/UnName.h (FName and FNameEntry structures)."""

from __future__ import annotations

class FName:
    """Simple name structure (FName)."""

    def __init__(self, name: str) -> None:
        self.Name = name


class FNameEntry:
    """Name entry structure (FNameEntry)."""

    def __init__(self, name: str, offset: int, length: int) -> None:
        self.Name = name
        self.Offset = offset
        self.Length = length
