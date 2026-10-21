"""Tests for Engine/Inc/UnEngineNative.h port (engine/unengine_native.py)."""

from ut99py.core.native import _native_type_infos
from ut99py.engine.unengine_native import (
    AUTO_INITIALIZE_REGISTRANTS_ENGINE,
    ENGINE_NATIVE_TYPES,
)


def test_engine_native_types_are_declared():
    assert len(ENGINE_NATIVE_TYPES) >= 14
    for name in ("AActor", "APawn", "APlayerPawn", "UScriptedTexture"):
        assert name in ENGINE_NATIVE_TYPES


def test_engine_native_types_are_registered():
    registered = {(info.Pkg, info.TypeName) for info in _native_type_infos}
    for name in ENGINE_NATIVE_TYPES:
        assert ("Engine", name) in registered


def test_auto_initialize_registrants_engine():
    assert len(AUTO_INITIALIZE_REGISTRANTS_ENGINE) >= 93
    for name in ("UGameEngine", "ULevelSummary", "AMover", "UScriptedTexture"):
        assert name in AUTO_INITIALIZE_REGISTRANTS_ENGINE
