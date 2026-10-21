"""Maps UnrealScript class names to the Python classes that model them.

A map file imports its classes from Engine.u, so an export only stores a
class index (UnLinker.h:39 FObjectExport::ClassIndex). The loader resolves
that index to a name through the import table and looks the name up here.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.objects import FName, UObject

_TABLE: Optional[Dict[str, type]] = None


class UImportedObject(UObject):
    """Stand-in for an object imported from another package.

    The C++ resolves an import through its source linker (UnLinker.h:867).
    The port has no parent package loaded, so the name and class from the
    import table stand in for it.
    """

    def __init__(self, name: FName, class_name: str) -> None:
        super().__init__()
        self.name = name
        self.class_name = class_name


def _table() -> Dict[str, type]:
    """The classes whose native data differs from the plain UObject layout.

    Everything else is an actor: AActor::Serialize only calls the UObject
    one (UnActor.cpp:971), so the actor stand-in reads the same bytes.
    """
    global _TABLE
    if _TABLE is None:
        from . import AActor, ABrush
        from .level import ULevel
        from .texture import UTexture
        from .un_obj import UPolys
        from ..graphics.model import UModel

        _TABLE = {
            "Level": ULevel,
            "Model": UModel,
            "Polys": UPolys,
            "Texture": UTexture,
            "Brush": ABrush,
        }
    return _TABLE


def class_for_name(name: str) -> type:
    """The Python class that models an UnrealScript class name."""
    from . import AActor

    return _table().get(name, AActor)


def import_placeholder(imp: Any) -> UImportedObject:
    """The stand-in for an import table entry (UnLinker.h:40 FObjectImport)."""
    return UImportedObject(imp.object_name, imp.class_name.name)


__all__ = ["UImportedObject", "class_for_name", "import_placeholder"]
