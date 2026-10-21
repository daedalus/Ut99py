"""Port of Engine/Inc/ULevelSummary.h (0 declared symbols).

ULevelSummary: the class-body fragment included from EngineClasses.h; it
holds the level title and the ideal player count. PostLoad() has an inline
body that calls UObject::PostLoad (Core.lib) and Localize (Core.lib).
"""

from __future__ import annotations
from ..core import FString, UObject


class ULevelSummary(UObject):
    """ULevelSummary (ULevelSummary.h + EngineClasses.h:3186)."""

    def __init__(self) -> None:
        super().__init__()
        # Members (EngineClasses.h ULevelSummary).
        self.Title: FString = FString()
        self.Author: FString = FString()
        self.IdealPlayerCount: FString = FString()
        self.RecommendedEnemies: int = 0
        self.RecommendedTeammates: int = 0
        self.LevelEnterText: FString = FString()

    def PostLoad(self) -> None:
        """ULevelSummary::PostLoad (ULevelSummary.h:11-25) - inline body.

        The C++ calls Super::PostLoad() (UObject::PostLoad, UnObjBas.h:534)
        first and then two Localize() lookups (Core/Inc/UnFile.h) that fill
        Title and IdealPlayerCount. Both helpers live in Core.lib.
        """
        raise NotImplementedError("C++ UObject::PostLoad: Core.lib")


__all__ = ["ULevelSummary"]
