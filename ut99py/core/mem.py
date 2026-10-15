"""Port of Core/Inc/UnMem.h (memory management).

Classes:
- FMemMark : memory marking context
- FMemStack : linear memory stack

Enums:
- EMemOned : oned memory allocation type
- EMemZeroed : zeroed memory allocation type
"""

from __future__ import annotations

from typing import Optional


class FMemMark:
    """Memory marking context for tracking allocations (UnMem.h:68)."""

    def __init__(self) -> None:
        self._old_mark: Optional[int] = None

    def Pop(self) -> None:
        """Pop the current mark context."""
        raise NotImplementedError


class FMemStack:
    """Simple linear-allocation memory stack.

    Items are allocated via PushBytes() and freed en masse by FMemMark::Pop().
    Ported from Core/Inc/UnMem.h:26.
    """

    def __init__(self) -> None:
        self.Top: int = 0
        self.End: int = 0
        self.BucketSize: int = 0
        self.Head: Optional[int] = None

    def PushBytes(self, size: int, align: int = 4) -> int:
        """Push bytes to the stack and return the pointer.

        Align must be a power of 2.
        """
        # Debug checks.
        assert size >= 0, "AllocSize must be non-negative"
        assert align > 0, "Align must be positive"
        assert (align & (align - 1)) == 0, "Align must be power of 2"

        # Align the pointer.
        Result = (self.Top + align - 1) & ~(align - 1)
        self.Top = Result + size

        # Check overflow — caller must grow the chunk if Top > End.
        if self.Top > self.End:
            raise NotImplementedError("GROW: chunk exhausted")

        return Result

    def PushStruct(self, size: int, align: int = 4) -> int:
        """Push a struct to the stack and return the pointer."""
        return self.PushBytes(size, align)

    def __repr__(self) -> str:
        return f"<FMemStack Top={self.Top}, End={self.End}, BucketSize={self.BucketSize}>"