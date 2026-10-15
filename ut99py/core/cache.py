"""Cache ID enumeration and MakeCacheID functions for Unreal Tournament 99.

Mirrors Core/Inc/UnCId.h from Unreal Tournament 99 source.
"""

from enum import IntEnum


class ECacheIDBase(IntEnum):
    """Cache ID's for all global Unreal objects."""

    ShadowMap = 0x15
    IlluminationMap = 0x16
    LightPalette = 0x17
    StaticMap = 0x18
    DepthLineTable = 0x1C
    TweenAnim = 0x1D
    TriPalette = 0x1E
    InputMap = 0x1F
    VolumetricScaler = 0x20
    RenderPalette = 0x25
    RenderFogMap = 0x26
    CoronaCache = 0x27
    PolyPalette = 0x28
    PolyMMXPalette = 0x29
    SurfPalette = 0x2A
    SurfMMXPalette = 0x2B
    LitTilePal = 0x2C
    LitTileTrans = 0x2D
    LitTileMMX = 0x2E
    LitTileMod = 0x2F
    ActorLightCache = 0x30
    DynamicMap = 0x31
    GlidePal = 0x32
    BumpNormals = 0x33
    SkeletalData = 0x34
    RenderTexture = 0xE0
    Max = 0xFF


def make_cache_id(base: ECacheIDBase, frame_index: int = 0) -> int:
    """Create a cache ID from base ID and optional frame index.
    
    Mirrors: inline QWORD MakeCacheID( ECacheIDBase Base, UObject* Frame )
    
    Args:
        base: Base cache ID (from ECacheIDBase enum).
        frame_index: Frame index (0 if no frame).
        
    Returns:
        Cache ID as integer: base + (frame_index << 8)
    """
    return int(base) + (frame_index << 8)


def make_cache_id_with_objects(base: ECacheIDBase, obj_index: int, frame_index: int = 0) -> int:
    """Create a cache ID from base ID, object index, and frame index.
    
    Mirrors: inline QWORD MakeCacheID( ECacheIDBase Base, UObject* Obj, UObject* Frame )
    
    Args:
        base: Base cache ID (from ECacheIDBase enum).
        obj_index: Object index (0 if no object).
        frame_index: Frame index (0 if no frame).
        
    Returns:
        Cache ID as integer: base + (obj_index << 8) + (frame_index << 32)
    """
    return int(base) + (obj_index << 8) + (frame_index << 32)


def make_cache_id_with_bytes(base: ECacheIDBase, byte: int, word: int, frame_index: int = 0) -> int:
    """Create a cache ID from base ID, byte, word, and frame index.
    
    Mirrors: inline QWORD MakeCacheID( ECacheIDBase Base, DWORD Word, DWORD Byte, UObject* Frame )
    
    Args:
        base: Base cache ID (from ECacheIDBase enum).
        byte: Byte value (0-255).
        word: Word value (0-65535).
        frame_index: Frame index (0 if no frame).
        
    Returns:
        Cache ID as integer: base + (byte << 8) + (word << 16) + (frame_index << 32)
    """
    return int(base) + (byte << 8) + (word << 16) + (frame_index << 32)


def make_cache_id_with_three_bytes(base: ECacheIDBase, byte_a: int, byte_b: int, byte_c: int, frame_index: int = 0) -> int:
    """Create a cache ID from base ID, three bytes, and frame index.
    
    Mirrors: inline QWORD MakeCacheID( ECacheIDBase Base, DWORD ByteA, DWORD ByteB, DWORD ByteC, UObject* Frame )
    
    Args:
        base: Base cache ID (from ECacheIDBase enum).
        byte_a: First byte value (0-255).
        byte_b: Second byte value (0-255).
        byte_c: Third byte value (0-255).
        frame_index: Frame index (0 if no frame).
        
    Returns:
        Cache ID as integer: base + (byte_a << 8) + (byte_b << 16) + (byte_c << 24) + (frame_index << 32)
    """
    return int(base) + (byte_a << 8) + (byte_b << 16) + (byte_c << 24) + (frame_index << 32)


def make_cache_id_from_qword(base: ECacheIDBase, qword: int) -> int:
    """Create a cache ID from base ID and QWORD value.
    
    Mirrors: inline QWORD MakeCacheID( ECacheIDBase Base, QWORD Q )
    
    Args:
        base: Base cache ID (from ECacheIDBase enum).
        qword: QWORD value.
        
    Returns:
        Cache ID as integer: base + (qword & ~CID_MAX)
    """
    return int(base) + (qword & ~int(ECacheIDBase.Max))
