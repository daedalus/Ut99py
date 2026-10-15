"""Regression tests for Engine/Inc/EngineClasses.h port.

Expected values derived from C++ semantics in EngineClasses.h, not
echoing the Python implementation back.
"""
import sys
sys.path.insert(0, "/home/dclavijo/my_code/Ut99py")

from ut99py.engine import (
    EInputKey, EInputAction, ETravelType, EDodgeDir,
    ELightEffect, ELightType, EMusicTransition, ESoundSlot,
    ERenderStyle, EDrawType, ENetRole, EPhysics,
    EIntelligence, EAttitude, ECsgOper, EBumpType,
    EMoverGlideType, EMoverEncroachType, ENetMode,
    ELevelAction,
)


def test_enum_int_values():
    """C++ enums assign sequential integer values."""
    assert EInputKey.IK_None == 0
    assert EInputKey.IK_Enter == 13
    assert EInputKey.IK_Space == 32
    assert EInputKey.IK_F1 == 112

    assert EPhysics.PHYS_None == 0
    assert EPhysics.PHYS_Walking == 1
    assert EPhysics.PHYS_Falling == 2
    assert EPhysics.PHYS_Vehicle == 8

    assert ENetRole.ROLE_Authority == 0
    assert ENetRole.ROLE_SimulatedProxy == 1
    assert ENetRole.ROLE_AutonomousProxy == 2
    assert ENetRole.ROLE_None == 3

    assert EDodgeDir.DODGE_Forward == 0
    assert EDodgeDir.DODGE_Backward == 1
    assert EDodgeDir.DODGE_Left == 2
    assert EDodgeDir.DODGE_Right == 3

    assert ETravelType.TRAVEL_Absolute == 0
    assert ETravelType.TRAVEL_Relative == 1

    assert EIntelligence.AI_Panic == 0
    assert EIntelligence.AI_Ignore == 7

    assert EAttitude.ADA_Neutral == 0
    assert EAttitude.ADA_Enemy == 2

    assert ECsgOper.CSG_Add == 0
    assert ECsgOper.CSG_Sub == 1

    assert ENetMode.NM_Standalone == 0
    assert ENetMode.NM_Client == 3


def test_int_enum_behavior():
    """IntEnum members are ints; comparisons and hashing work."""
    assert int(EInputKey.IK_Enter) == 13
    assert EInputKey.IK_Enter == 13
    assert hash(EInputKey.IK_Enter) == hash(13)


def test_enum_name_matching():
    """Member names mirror C++ macros."""
    assert EInputKey.__members__["IK_LeftMouse"].value == 1
    assert ESoundSlot.SLOT_Weapon == 2
    assert EMusicTransition.MT_Norm == 2


if __name__ == "__main__":
    test_enum_int_values()
    test_int_enum_behavior()
    test_enum_name_matching()
    print("All EngineClasses tests passed.")
