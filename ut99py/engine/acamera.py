"""Port of Engine/Inc/ACamera.h (0 declared symbols).

ACamera: the class-body fragment included from EngineClasses.h. The
constructor is inline and the class adds no methods of its own.
"""

from __future__ import annotations
from .aplayer_pawn import APlayerPawn


class ACamera(APlayerPawn):
    """ACamera (ACamera.h + EngineClasses.h:1847)."""

    def __init__(self) -> None:
        super().__init__()


__all__ = ["ACamera"]
