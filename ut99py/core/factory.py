"""Port of Core/Inc/UFactory.h (factory class definition).

Classes:
- UFactory : UObject
"""

from __future__ import annotations

from typing import Optional

from .objects import UObject


class UFactory(UObject):
    """Object responsible for creating and importing new objects (UFactory)."""

    def __init__(self) -> None:
        super().__init__()
        self.SupportedClass: Optional[type] = None
        self.ContextClass: Optional[type] = None
        self.Description: str = ""
        self.InContextCommand: str = ""
        self.OutOfContextCommand: str = ""
        self.Formats: list[str] = []
        self.bCreateNew: bool = False
        self.bShowPropertySheet: bool = False
        self.bShowCategories: bool = False
        self.bText: bool = False
        self.bMulti: bool = False
        self.AutoPriority: int = 0

    def Serialize(self, archive) -> None:
        raise NotImplementedError

    def StaticConstructor(self) -> None:
        pass
