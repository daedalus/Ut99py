"""Port of Core/Inc/UnCoreNet.h (Core networking support).

Fully-inline members are ported 1-to-1.  The CORE_API constructors and
serializers (`FFieldNetCache::operator<<`, `FClassNetCache::FClassNetCache`,
`FClassNetCache::operator<<`, `FPackageInfo::FPackageInfo`,
`FPackageInfo::operator<<`, `UPackageMap::*`) live in the prebuilt Core.lib and
are marked as such rather than guessed.  `UPackageMap` itself is the stub that
already lives in `core/objects.py` (its UnCoreNet.h home), so it is not
duplicated here.

Source line numbers refer to Core/Inc/UnCoreNet.h.
"""

from typing import Any, Optional

from .types import FString, FGuid, TArray, TMap, INDEX_NONE

__all__ = [
    "FFieldNetCache",
    "FClassNetCache",
    "FPackageInfo",
    "FPropertyRetirement",
    "serialize_class_net_cache_ptr",
]


class FFieldNetCache:
    """FFieldNetCache (UnCoreNet.h:12): info about one networked field."""

    def __init__(
        self, field: Any = None, field_net_index: int = 0, condition_index: int = 0
    ):
        # The C++ default ctor (UnCoreNet.h:18) leaves the members
        # uninitialised; the arg ctor (UnCoreNet.h:20-22) assigns them.
        self.field = field
        self.field_net_index = field_net_index
        self.condition_index = condition_index

    def __repr__(self) -> str:
        return (
            f"FFieldNetCache(field={self.field!r}, "
            f"field_net_index={self.field_net_index}, "
            f"condition_index={self.condition_index})"
        )


class FClassNetCache:
    """FClassNetCache (UnCoreNet.h:29): per-class field cache for replication.

    The constructors and `operator<<` are in Core.lib; only the inline
    accessors are ported.  Private C++ members keep a leading underscore here,
    matching the rest of the port.
    """

    def __init__(self, cls: Any = None):
        # `FClassNetCache();` / `FClassNetCache( UClass* Class );` bodies are
        # in Core.lib.  Zero-init the fields so the inline accessors are safe.
        self._fields_base: int = 0
        self._super: Optional["FClassNetCache"] = None
        self._rep_condition_count: int = 0
        self._class: Any = cls
        self._fields: TArray = TArray()
        self._field_map: TMap = TMap()
        # Public in C++ (UnCoreNet.h:53).
        self.rep_properties: TArray = TArray()

    def get_max_index(self) -> int:
        """GetMaxIndex() (UnCoreNet.h:35-38)."""
        return self._fields_base + len(self._fields)

    def get_rep_condition_count(self) -> int:
        """GetRepConditionCount() (UnCoreNet.h:39-42)."""
        return self._rep_condition_count

    def get_from_field(self, field: Any) -> Optional[FFieldNetCache]:
        """GetFromField( UObject* Field ) (UnCoreNet.h:43-51)."""
        # Walk the Super chain until a cache maps the field.
        cache: Optional[FClassNetCache] = self
        while cache is not None:
            result = cache._field_map.get(field)
            if result is not None:
                return result
            cache = cache._super
        return None

    def get_from_index(self, index: int) -> Optional[FFieldNetCache]:
        """GetFromIndex( INT Index ) (UnCoreNet.h:53-61)."""
        # Index ranges are contiguous across the Super chain.
        cache: Optional[FClassNetCache] = self
        while cache is not None:
            if cache._fields_base <= index < cache._fields_base + len(cache._fields):
                return cache._fields[index - cache._fields_base]
            cache = cache._super
        return None

    def __repr__(self) -> str:
        return (
            f"FClassNetCache(class={self._class!r}, "
            f"fields_base={self._fields_base}, fields={len(self._fields)})"
        )


class FPackageInfo:
    """FPackageInfo (UnCoreNet.h:76): ordered linker-file requirement."""

    def __init__(self, linker: Any = None):
        # FPackageInfo( ULinkerLoad* InLinker=NULL ) body is in Core.lib; the
        # members are zero-initialised here so an unloaded record is inert.
        self.url: FString = FString("")
        self.linker: Any = linker
        self.parent: Any = None
        self.guid: FGuid = FGuid()
        self.file_size: int = 0
        self.object_base: int = 0
        self.object_count: int = 0
        self.name_base: int = 0
        self.name_count: int = 0
        self.local_generation: int = 0
        self.remote_generation: int = 0
        self.package_flags: int = 0

    def __repr__(self) -> str:
        return f"FPackageInfo(url={self.url!r}, file_size={self.file_size})"


class FPropertyRetirement:
    """FPropertyRetirement (UnCoreNet.h:140): property retirement tracking.

    The C++ ctor (UnCoreNet.h:145-148) initialises both packet ids to
    INDEX_NONE; `Reliable` is left uninitialised, zeroed here.
    """

    def __init__(self):
        self.in_packet_id: int = INDEX_NONE
        self.out_packet_id: int = INDEX_NONE
        self.reliable: int = 0


def serialize_class_net_cache_ptr(ar: Any, cache: Any) -> Any:
    """inline operator<<( FArchive& Ar, FClassNetCache* ) (UnCoreNet.h:132).

    A pointer to a FClassNetCache serialises as nothing; the operator just
    returns the archive.
    """
    return ar
