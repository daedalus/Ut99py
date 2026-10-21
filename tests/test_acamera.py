"""Tests for Engine/Inc/ACamera.h port (engine/acamera.py)."""

from ut99py.engine.acamera import ACamera
from ut99py.engine.aplayer_pawn import APlayerPawn


def test_acamera_base_chain_matches_engine_classes():
    # EngineClasses.h:1847 - class ACamera : public APlayerPawn
    assert issubclass(ACamera, APlayerPawn)


def test_acamera_constructor_is_inline():
    camera = ACamera()
    assert isinstance(camera, APlayerPawn)
