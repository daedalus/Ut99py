"""Port of Core/Inc/UExporter.h (exporter class).

Classes:
- UExporter : UObject
"""

from __future__ import annotations

from typing import Optional

from .objects import UObject


class UExporter(UObject):
    """Object responsible for exporting other objects to files (UExporter)."""

    def __init__(self) -> None:
        super().__init__()
        self.SupportedClass: Optional[type] = None
        self.Formats: list[str] = []
        self.TextIndent: int = 0
        self.bText: bool = False
        self.bMulti: bool = False

    def Serialize(self, archive) -> None:
        raise NotImplementedError

    def StaticConstructor(self) -> None:
        pass

    def ExportText(
        self,
        obj: Optional[UObject],
        typ: str,
        ar,
        warn,
    ) -> bool:
        return False

    def ExportBinary(
        self,
        obj: Optional[UObject],
        typ: str,
        ar,
        warn,
    ) -> bool:
        return False

    @staticmethod
    def FindExporter(obj: Optional[UObject], filetype: str) -> Optional["UExporter"]:
        return None

    @staticmethod
    def ExportToFile(
        obj: Optional[UObject],
        exporter: Optional["UExporter"],
        filename: str,
        no_replace_identical: bool = False,
        prompt: bool = False,
    ) -> int:
        return 0

    @staticmethod
    def ExportToArchive(
        obj: Optional[UObject],
        exporter: Optional["UExporter"],
        ar,
        filetype: str,
    ) -> None:
        pass

    @staticmethod
    def ExportToOutputDevice(
        obj: Optional[UObject],
        exporter: Optional["UExporter"],
        out,
        filetype: str,
        indent: int,
    ) -> None:
        pass
