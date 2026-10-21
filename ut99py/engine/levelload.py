"""Generic ULevel loader from a .unr package (UnLevel.cpp:65-263).

The level export's serialised data is the ULevelBase::Serialize /
ULevel::Serialize byte stream; the linker's preload() walks it through
UObject::Serialize (which reads the tagged property block and, for
RF_HasStack exports, the execution stack) and the level's own tail. This
module is a thin wrapper that resolves the level export and asserts the
stream was consumed exactly, so any layout drift fails loudly instead of
returning a half-parsed level.
"""
from __future__ import annotations

from typing import Any, Optional

from ..engine.level import ULevel, ULevelBase


def load_level(linker: Any, export: Any) -> ULevel:
    """Parse the level export and return a populated ULevel.

    Args:
        linker: the ULinkerLoad that owns the export.
        export: the FObjectExport describing the level (0-based index
            into the linker's export_map, or the export object itself).

    Returns:
        A ULevel whose Actors, URL, Model, ReachSpecs, TimeSeconds,
        TextBlocks and TravelInfo are populated.

    Raises:
        ValueError if the serialised data is not consumed exactly.
    """
    # Accept either the export index or the FObjectExport instance.
    if isinstance(export, int):
        index = export
        exp = linker.export_map[index]
    else:
        exp = export
        index = linker.export_map.index(exp)
    level = linker.create_export(index)
    if not isinstance(level, ULevelBase):
        raise ValueError(
            "level export resolved to "
            f"{type(level).__name__}, not a ULevelBase"
        )
    linker.preload(level)
    # ULevel::Serialize calls Ar.Preload(Model) after writing it
    # (UnLevel.cpp:257-258); the reference alone leaves the model empty.
    if level.Model is not None:
        linker.preload(level.Model)
    return level


__all__ = ["load_level"]