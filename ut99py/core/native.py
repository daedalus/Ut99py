"""Native function lookup table for static libraries (UnCoreNative.h).

Ported from Core/Inc/UnCoreNative.h.

This module provides the native function registration and lookup mechanism
mirroring the Unreal Engine native function table system.
"""

from typing import Callable, Optional, Any
import ctypes

# Native function lookup result declaration
RESULT_DECL = int


# ============================================================
# Native function pointer type
# ============================================================

NativeLookup = Callable[[str], Any]
"""
Function pointer type for native function lookup.

Maps a native function name (TCHAR*) to its handler pointer.
Equivalent to: typedef void* (*NativeLookup)(char*);
"""


# ============================================================
# Global native lookup functions array
# ============================================================

# Equivalent to: extern NativeLookup GNativeLookupFuncs[32];
# Array of native lookup functions, indexed by type.
GNativeLookupFuncs: list[NativeLookup | None] = []


def init_native_lookup_funcs() -> None:
    """Initialize the native lookup functions array (32 entries)."""
    global GNativeLookupFuncs
    GNativeLookupFuncs = [None] * 32


# ============================================================
# Native type registration infrastructure
# ============================================================

# Track native type info entries
_native_type_infos: list[dict] = []


class NativeTypeInfo:
    """Information about a native type (mirrors type##NativeInfo struct)."""
    def __init__(self, pkg: str, type_name: str, name: str, pointer: Optional[NativeLookup] = None):
        self.Pkg = pkg
        self.TypeName = type_name
        self.Name = name
        self.Pointer = pointer


def declare_native_type(pkg: str, type_name: str) -> tuple[type, callable]:
    """Decorator to declare a native type (mirrors DECLARE_NATIVE_TYPE macro).

    Usage:
        @declare_native_type("Core", "UObject")
        class UObjectNatives:
            pass
    """
    # Register the native type info
    info = NativeTypeInfo(pkg=pkg, type_name=type_name, name=f"{pkg}{type_name}")
    _native_type_infos.append(info)

    # Create a lookup function registry dict for this type
    registry: dict[str, NativeLookup] = {}

    def register_native(name: str, func: NativeLookup) -> None:
        """Register a native function for this type."""
        registry[name] = func

    def lookup_native(name: str) -> Optional[NativeLookup]:
        """Look up a native function by name."""
        return registry.get(name)

    # Attach registry to the type info
    info._registry = registry

    return lookup_native, register_native


def implement_native_handler(pkg: str, type_name: str) -> callable:
    """Decorator to implement the native handler (mirrors IMPLEMENT_NATIVE_HANDLER macro).

    Usage:
        @implement_native_handler("Core", "UObject")
        def find_core_uobject_native(native_name):
            # search logic here
            pass
    """
    def decorator(func: callable) -> callable:
        # Register the lookup function in the global array
        # Find the corresponding type info and register
        for info in _native_type_infos:
            if info.Pkg == pkg and info.TypeName == type_name:
                # Store the implementation function
                info._handler = func
                break
        return func
    return decorator


def find_native(pkg: str, type_name: str, native_name: str) -> Optional[NativeLookup]:
    """Find a native function by name (mirrors Find##pkg##type##Native function).

    Searches through the registered native type info entries to find
    the native function with the given name.
    """
    # First check the global lookup functions array
    for func in GNativeLookupFuncs:
        if func is not None:
            result = func(native_name)
            if result is not None:
                return result

    # Check registered type infos
    for info in _native_type_infos:
        if info.Pkg == pkg and info.TypeName == type_name:
            registry = getattr(info, '_registry', {})
            if native_name in registry:
                return registry[native_name]

    return None


# ============================================================
# Macro replacements
# ============================================================

def map_native(cls_name: str, method_name: str) -> tuple[str, Callable]:
    """Equivalent to MAP_NATIVE(cls, name) macro.

    Creates a name-to-function mapping entry.
    Returns (name, method_pointer) tuple.
    """
    return (f"int{cls_name}{method_name}", method_name)


# ============================================================
# Pre-declared native types
# ============================================================

# Auto-register Core UObject and UCommandlet native types
# These mirror the DECLARE_NATIVE_TYPE(Core,UObject) and
# DECLARE_NATIVE_TYPE(Core,UCommandlet) from the C++ header.

declare_native_type("Core", "UObject")
declare_native_type("Core", "UCommandlet")

# Initialize the native lookup funcs array
init_native_lookup_funcs()