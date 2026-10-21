"""Port of Engine/Inc/UnEngineNative.h (0 declared symbols).

Native type registration table of the Engine package plus the list of
classes the static-library registrant initialises. Importing the module
registers every DECLARE_NATIVE_TYPE(Engine, X) entry.
"""

from __future__ import annotations
from ..core import declare_native_type

# DECLARE_NATIVE_TYPE(Engine, X) (UnEngineNative.h:18-31).
ENGINE_NATIVE_TYPES: tuple[str, ...] = (
    "AActor",
    "APawn",
    "APlayerPawn",
    "ADecal",
    "AStatLog",
    "AStatLogFile",
    "AZoneInfo",
    "AWarpZoneInfo",
    "ALevelInfo",
    "AGameInfo",
    "ANavigationPoint",
    "UCanvas",
    "UConsole",
    "UScriptedTexture",
)

# AUTO_INITIALIZE_REGISTRANTS_ENGINE (UnEngineNative.h:33-131): the classes
# whose StaticClass() the Engine registrant calls at start-up.
AUTO_INITIALIZE_REGISTRANTS_ENGINE: tuple[str, ...] = (
    "AMutator",
    "ULodMesh",
    "AActor",
    "ALight",
    "AWeapon",
    "ALevelInfo",
    "AGameInfo",
    "ACamera",
    "AZoneInfo",
    "ASkyZoneInfo",
    "APathNode",
    "ANavigationPoint",
    "AScout",
    "AInterpolationPoint",
    "ADecoration",
    "AProjectile",
    "AWarpZoneInfo",
    "ATeleporter",
    "APlayerStart",
    "AKeypoint",
    "AInventory",
    "AInventorySpot",
    "ATriggers",
    "ATrigger",
    "ATriggerMarker",
    "AButtonMarker",
    "AWarpZoneMarker",
    "AHUD",
    "AMenu",
    "ASavedMove",
    "ACarcass",
    "ALiftCenter",
    "ALiftExit",
    "AInfo",
    "AReplicationInfo",
    "APlayerReplicationInfo",
    "AInternetInfo",
    "AStatLog",
    "AStatLogFile",
    "AGameReplicationInfo",
    "ULevelSummary",
    "Alocationid",
    "ADecal",
    "ASpawnNotify",
    "AAmmo",
    "APickup",
    "USound",
    "UMusic",
    "UAudioSubsystem",
    "UClient",
    "UViewport",
    "UCanvas",
    "UChannel",
    "UControlChannel",
    "UActorChannel",
    "UFileChannel",
    "UConsole",
    "UNetConnection",
    "UDemoPlayPendingLevel",
    "UDemoRecConnection",
    "UDemoRecDriver",
    "ABrush",
    "UEngine",
    "URenderBase",
    "URenderDevice",
    "URenderIterator",
    "UServerCommandlet",
    "UPolys",
    "UFont",
    "UGameEngine",
    "UInput",
    "ULevelBase",
    "ULevel",
    "UMesh",
    "UBspNodes",
    "UBspSurfs",
    "UVectors",
    "UVerts",
    "UModel",
    "AMover",
    "UPackageMapLevel",
    "UNetDriver",
    "APawn",
    "APlayerPawn",
    "UPendingLevel",
    "UNetPendingLevel",
    "UPlayer",
    "UPrimitive",
    "UScriptedTexture",
    "UBitmap",
    "UTexture",
    "UPalette",
    "UAnimation",
)


def _declare_engine_natives() -> None:
    """Register the Engine native types (UnEngineNative.h:18-31)."""
    for type_name in ENGINE_NATIVE_TYPES:
        declare_native_type("Engine", type_name)


_declare_engine_natives()


__all__ = [
    "ENGINE_NATIVE_TYPES",
    "AUTO_INITIALIZE_REGISTRANTS_ENGINE",
]
