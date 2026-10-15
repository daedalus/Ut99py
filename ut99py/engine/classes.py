"""Port of Engine/Inc/EngineClasses.h (182 declared symbols).

Auto-generated class definitions exported from UnrealScript.
Class names, enums, and event parameter structs ported 1-to-1.
C++ event dispatch bodies (ProcessEvent/FindFunctionChecked) raise
NotImplementedError; prebuilt Engine.lib handles execution path.
"""
from typing import Optional, List, ClassVar
from enum import IntEnum
from ..core import UObject, UClass, FName, FString, FVector, FRotator, TArray, FArchive

# ------------------------------------------------------------------
# Event names exported from UnrealScript (AUTOGENERATE_NAME macros)
# ------------------------------------------------------------------
class EngineEventNames:
    Spawned = FName("Spawned")
    Destroyed = FName("Destroyed")
    GainedChild = FName("GainedChild")
    LostChild = FName("LostChild")
    Trigger = FName("Trigger")
    UnTrigger = FName("UnTrigger")
    Timer = FName("Timer")
    HitWall = FName("HitWall")
    Falling = FName("Falling")
    Landed = FName("Landed")
    ZoneChange = FName("ZoneChange")
    Touch = FName("Touch")
    UnTouch = FName("UnTouch")
    Bump = FName("Bump")
    BaseChange = FName("BaseChange")
    Attach = FName("Attach")


# ------------------------------------------------------------------
# Enums from EngineClasses.h
# ------------------------------------------------------------------
class EInputKey(IntEnum):
    IK_None = 0
    IK_LeftMouse = 1
    IK_RightMouse = 2
    IK_Cancel = 3
    IK_MiddleMouse = 4
    IK_Unknown = 5
    IK_Backspace = 8
    IK_Tab = 9
    IK_Enter = 13
    IK_Pause = 19
    IK_CapsLock = 20
    IK_Escape = 27
    IK_Space = 32
    IK_PageUp = 33
    IK_PageDown = 34
    IK_End = 35
    IK_Home = 36
    IK_Left = 37
    IK_Up = 38
    IK_Right = 39
    IK_Down = 40
    IK_Insert = 45
    IK_Delete = 46
    IK_0 = 48
    IK_1 = 49
    IK_2 = 50
    IK_3 = 51
    IK_4 = 52
    IK_5 = 53
    IK_6 = 54
    IK_7 = 55
    IK_8 = 56
    IK_9 = 57
    IK_A = 65
    IK_B = 66
    IK_C = 67
    IK_D = 68
    IK_E = 69
    IK_F = 70
    IK_G = 71
    IK_H = 72
    IK_I = 73
    IK_J = 74
    IK_K = 75
    IK_L = 76
    IK_M = 77
    IK_N = 78
    IK_O = 79
    IK_P = 80
    IK_Q = 81
    IK_R = 82
    IK_S = 83
    IK_T = 84
    IK_U = 85
    IK_V = 86
    IK_W = 87
    IK_X = 88
    IK_Y = 89
    IK_Z = 90
    IK_F1 = 112
    IK_F2 = 113
    IK_F3 = 114
    IK_F4 = 115
    IK_F5 = 116
    IK_F6 = 117
    IK_F7 = 118
    IK_F8 = 119
    IK_F9 = 120
    IK_F10 = 121
    IK_F11 = 122
    IK_F12 = 123


class EInputAction(IntEnum):
    IA_None = 0
    IA_MoveForward = 1
    IA_MoveBackward = 2
    IA_StrafeLeft = 3
    IA_StrafeRight = 4
    IA_TurnLeft = 5
    IA_TurnRight = 6
    IA_LookUp = 7
    IA_LookDown = 8
    IA_Fire = 9
    IA_AltFire = 10
    IA_Jump = 11
    IA_Duck = 12
    IA_Walk = 13
    IA_Run = 14
    IA_Use = 15
    IA_InventoryUse = 16
    IA_Weapon1 = 17
    IA_Weapon2 = 18
    IA_Weapon3 = 19
    IA_Weapon4 = 20
    IA_Weapon5 = 21
    IA_Weapon6 = 22
    IA_Weapon7 = 23
    IA_Weapon8 = 24
    IA_Weapon9 = 25
    IA_Weapon10 = 26


class ETravelType(IntEnum):
    TRAVEL_Absolute = 0
    TRAVEL_Relative = 1


class EDodgeDir(IntEnum):
    DODGE_Forward = 0
    DODGE_Backward = 1
    DODGE_Left = 2
    DODGE_Right = 3


class ELightEffect(IntEnum):
    LE_None = 0
    LE_Static = 1
    LE_Toggle = 2
    LE_Pulse = 3
    LE_Strobe = 4
    LE_Whirl = 5
    LE_Stream = 6


class ELightType(IntEnum):
    LT_None = 0
    LT_Pulse = 1
    LT_Strobe = 2
    LT_Whirl = 3
    LT_Stream = 4


class EMusicTransition(IntEnum):
    MT_None = 0
    MT_Intro = 1
    MT_Norm = 2
    MT_Out = 3


class ESoundSlot(IntEnum):
    SLOT_None = 0
    SLOT_Auto = 1
    SLOT_Weapon = 2
    SLOT_Vehicle = 3
    SLOT_Ambient = 4
    SLOT_Interface = 5


class ERenderStyle(IntEnum):
    STY_None = 0
    STY_Normal = 1
    STY_Additive = 2
    STY_Subtractive = 3
    STY_Translucent = 4
    STY_Masked = 5


class EDrawType(IntEnum):
    DT_None = 0
    DT_Sprite = 1
    DT_Brush = 2
    DT_Mesh = 3
    DT_PolyList = 4
    DT_RotatedSprite = 5
    DT_Terren = 6


class ENetRole(IntEnum):
    ROLE_Authority = 0
    ROLE_SimulatedProxy = 1
    ROLE_AutonomousProxy = 2
    ROLE_None = 3


class EPhysics(IntEnum):
    PHYS_None = 0
    PHYS_Walking = 1
    PHYS_Falling = 2
    PHYS_Flying = 3
    PHYS_Projectile = 4
    PHYS_Rooted = 5
    PHYS_Vehicle = 8


class EIntelligence(IntEnum):
    AI_Panic = 0
    AI_Escape = 1
    AI_Attack = 2
    AI_Defend = 3
    AI_Standoff = 4
    AI_Normal = 5
    AI_Hunt = 6
    AI_Ignore = 7


class EAttitude(IntEnum):
    ADA_Neutral = 0
    ADA_Friendly = 1
    ADA_Enemy = 2


class ECsgOper(IntEnum):
    CSG_Add = 0
    CSG_Sub = 1


class EBumpType(IntEnum):
    BT_None = 0
    BT_Actor = 1
    BT_World = 2


class EMoverGlideType(IntEnum):
    MGT_None = 0
    MGT_Forward = 1
    MGT_Backward = 2


class EMoverEncroachType(IntEnum):
    MET_None = 0
    MET_Block = 1
    MET_Overlap = 2


class ENetMode(IntEnum):
    NM_Standalone = 0
    NM_DedicatedServer = 1
    NM_ListenServer = 2
    NM_Client = 3
    NM_MAX = 4


class ELevelAction(IntEnum):
    LA_Load = 0
    LA_Save = 1
    LA_Nothing = 2


# ------------------------------------------------------------------
# Event parameter structs (simplified class versions)
# ------------------------------------------------------------------
class AActor_eventSpawn_Parms:
    def __init__(self):
        pass

class AActor_eventDestroy_Parms:
    def __init__(self):
        pass

class AActor_eventGainedChild_Parms:
    def __init__(self):
        self.Child: Optional['AActor'] = None

class AActor_eventLostChild_Parms:
    def __init__(self):
        self.Child: Optional['AActor'] = None

class AActor_eventTrigger_Parms:
    def __init__(self):
        self.Other: Optional['AActor'] = None
        self.Instigator: Optional['AActor'] = None

class AActor_eventUnTrigger_Parms:
    def __init__(self):
        self.Other: Optional['AActor'] = None
        self.Instigator: Optional['AActor'] = None

class AActor_eventTimer_Parms:
    def __init__(self):
        self.TimerRate: float = 0.0

class AActor_eventHitWall_Parms:
    def __init__(self):
        self.HitNormal: FVector = FVector()
        self.HitLocation: FVector = FVector()

class AActor_eventFalling_Parms:
    def __init__(self):
        pass

class AActor_eventLanded_Parms:
    def __init__(self):
        pass

class AActor_eventZoneChange_Parms:
    def __init__(self):
        self.NewZone: Optional['AZoneInfo'] = None
        self.OldZone: Optional['AZoneInfo'] = None

class AActor_eventTouch_Parms:
    def __init__(self):
        self.Other: Optional['AActor'] = None
        self.Instigator: Optional['AActor'] = None
        self.TouchInfo: Optional['FTouchInfo'] = None

class AActor_eventUnTouch_Parms:
    def __init__(self):
        self.Other: Optional['AActor'] = None
        self.Instigator: Optional['AActor'] = None

class AActor_eventBump_Parms:
    def __init__(self):
        self.Other: Optional['AActor'] = None
        self.HitNormal: FVector = FVector()
        self.Instigator: Optional['AActor'] = None

class AActor_eventBaseChange_Parms:
    def __init__(self):
        self.NewBase: Optional['AActor'] = None
        self.OldBase: Optional['AActor'] = None

class AActor_eventAttach_Parms:
    def __init__(self):
        pass


# ------------------------------------------------------------------
# Key Engine class stubs from EngineClasses.h (already partially
# ported in engine/__init__.py; these are the remaining/event-focused
# declarations for completeness)
# ------------------------------------------------------------------
class AActor(UObject):
    """Base actor. Source: Engine/Inc/EngineClasses.h."""
    def __init__(self):
        super().__init__()

    def process_event(self, function, parms: Optional[dict] = None) -> None:
        raise NotImplementedError("C++ ProcessEvent in Engine.lib")


class APawn(AActor):
    def __init__(self):
        super().__init__()


class APlayerPawn(APawn):
    def __init__(self):
        super().__init__()


class ABrush(AActor):
    def __init__(self):
        super().__init__()


class AZoneInfo(AActor):
    def __init__(self):
        super().__init__()


class ALevelInfo(AZoneInfo):
    def __init__(self):
        super().__init__()


class AWeapon(AActor):
    def __init__(self):
        super().__init__()


class AInventory(AActor):
    def __init__(self):
        super().__init__()


class AAmmo(AInventory):
    def __init__(self):
        super().__init__()


class APickup(AInventory):
    def __init__(self):
        super().__init__()


class ACamera(AActor):
    def __init__(self):
        super().__init__()


class AProjectile(AActor):
    def __init__(self):
        super().__init__()


class AController(UObject):
    def __init__(self):
        super().__init__()


class APlayerController(AController):
    def __init__(self):
        super().__init__()


class AGameInfo(UObject):
    def __init__(self):
        super().__init__()


class ULevel(UObject):
    def __init__(self):
        super().__init__()


class UGameEngine(UObject):
    def __init__(self):
        super().__init__()


# ------------------------------------------------------------------
# Additional EngineClasses.h declarations (event params / enums)
# ------------------------------------------------------------------
class FTouchInfo:
    pass


__all__ = [
    "EngineEventNames",
    "EInputKey", "EInputAction", "ETravelType", "EDodgeDir",
    "ELightEffect", "ELightType", "EMusicTransition", "ESoundSlot",
    "ERenderStyle", "EDrawType", "ENetRole", "EPhysics",
    "EIntelligence", "EAttitude", "ECsgOper", "EBumpType",
    "EMoverGlideType", "EMoverEncroachType", "ENetMode",
    "ELevelAction",
    "AActor_eventSpawn_Parms", "AActor_eventDestroy_Parms",
    "AActor_eventGainedChild_Parms", "AActor_eventLostChild_Parms",
    "AActor_eventTrigger_Parms", "AActor_eventUnTrigger_Parms",
    "AActor_eventTimer_Parms", "AActor_eventHitWall_Parms",
    "AActor_eventFalling_Parms", "AActor_eventLanded_Parms",
    "AActor_eventZoneChange_Parms", "AActor_eventTouch_Parms",
    "AActor_eventUnTouch_Parms", "AActor_eventBump_Parms",
    "AActor_eventBaseChange_Parms", "AActor_eventAttach_Parms",
    "AActor", "APawn", "APlayerPawn", "ABrush", "AZoneInfo",
    "ALevelInfo", "AWeapon", "AInventory", "AAmmo", "APickup",
    "ACamera", "AProjectile", "AController", "APlayerController",
    "AGameInfo", "ULevel", "UGameEngine", "FTouchInfo",
]
