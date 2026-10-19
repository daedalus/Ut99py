"""Port of Engine/Inc/AActor.h and Engine/Inc/UnActor.h (3 declared symbols).

AActor base actor class + APlayerPawn reference. Methods raise NotImplementedError("Engine.lib") per port fidelity.
Inline bodies from UnActor.h are ported faithfully.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import UObject
from ..engine import ULevel, ABrush, AProjectile, APawn, APlayerPawn


class AActor(UObject):
    """AActor (AActor.h / UnActor.h)"""
    def __init__(self) -> None:
        super().__init__()

    def Destroy(self) -> None:
        raise NotImplementedError("C++ AActor::Destroy: Engine.lib")

    def GetOptimizedRepList(self, InDefault: Any, Retire: Any, Ptr: Any, Map: Any, NumReps: int) -> Any:
        raise NotImplementedError("C++ AActor::GetOptimizedRepList: Engine.lib")

    def ShouldDoScriptReplication(self) -> bool:
        return True  # inline: return 1; -> True.

    def NoVariablesToReplicate(self, OldVer: "AActor") -> bool:
        return False  # inline: return 0; -> False.

    def CheckRecentChanges(self) -> bool:
        return False  # inline: return 0; -> False.

    def UpdateFrequency(self, Viewer: "AActor", ViewDir: Any, ViewPos: Any) -> float:
        raise NotImplementedError("C++ AActor::UpdateFrequency: Engine.lib")

    def ProcessEvent(self, Function: Any, Parms: Any, Result: Any = None) -> None:
        raise NotImplementedError("C++ AActor::ProcessEvent: Engine.lib")

    def ProcessState(self, DeltaSeconds: float) -> None:
        raise NotImplementedError("C++ AActor::ProcessState: Engine.lib")

    def ProcessRemoteFunction(self, Function: Any, Parms: Any, Stack: Any) -> bool:
        raise NotImplementedError("C++ AActor::ProcessRemoteFunction: Engine.lib")

    def ProcessDemoRecFunction(self, Function: Any, Parms: Any, Stack: Any) -> None:
        raise NotImplementedError("C++ AActor::ProcessDemoRecFunction: Engine.lib")

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ AActor::Serialize: Engine.lib")

    def InitExecution(self) -> None:
        raise NotImplementedError("C++ AActor::InitExecution: Engine.lib")

    def PostEditChange(self) -> None:
        raise NotImplementedError("C++ AActor::PostEditChange: Engine.lib")

    def PostLoad(self) -> None:
        raise NotImplementedError("C++ AActor::PostLoad: Engine.lib")

    def GetLevel(self) -> Optional[ULevel]:
        raise NotImplementedError("C++ AActor::GetLevel: Engine.lib")

    def GetPlayerPawn(self) -> Optional[Any]:
        raise NotImplementedError("C++ AActor::GetPlayerPawn: Engine.lib")

    def IsPlayer(self) -> bool:
        return False  # inline: return False by default unless overridden.

    def IsOwnedBy(self, TestOwner: "AActor") -> bool:
        raise NotImplementedError("C++ AActor::IsOwnedBy: Engine.lib")

    def WorldSoundRadius(self) -> float:
        return 25.0  # inline: {return 25.f * ((INT)SoundRadius+1);}

    # --- UnActor.h inline methods ---

    def IsBrush(self) -> bool:
        """AActor::IsBrush() - inline from UnActor.h."""
        return self.Brush is not None and self.IsA(ABrush.StaticClass())

    def IsStaticBrush(self) -> bool:
        """AActor::IsStaticBrush() - inline from UnActor.h."""
        return (self.Brush is not None and
                self.IsA(ABrush.StaticClass()) and
                getattr(self, 'bStatic', False))

    def IsMovingBrush(self) -> bool:
        """AActor::IsMovingBrush() - inline from UnActor.h."""
        return (self.Brush is not None and
                self.IsA(ABrush.StaticClass()) and
                not getattr(self, 'bStatic', True))

    def IsOwnedBy(self, TestOwner: Any) -> bool:
        """AActor::IsOwnedBy() - inline from UnActor.h (iterates Owner chain)."""
        for Arg in [self, *(getattr(self, 'Owner', []))]:
            if Arg == TestOwner:
                return True
        return False

    def GetTopOwner(self) -> Any:
        """AActor::GetTopOwner() - inline from UnActor.h."""
        Top = self
        while getattr(Top, 'Owner', None) is not None:
            Top = getattr(Top, 'Owner', None)
        return Top

    def IsInZone(self, TestZone: Any) -> bool:
        """AActor::IsInZone() - inline from UnActor.h."""
        return (getattr(self, 'Region', type('obj', (), {'Zone': None}))().Zone !=
                getattr(self, 'Level', None)) and \
               (getattr(self, 'Region', type('obj', (), {'Zone': None}))().Zone ==
                TestZone or 1)

    def GetPlayerPawn(self) -> Any:
        """AActor::GetPlayerPawn() - inline from UnActor.h."""
        if not self.IsA(APawn.StaticClass()):
            return None
        player = getattr(self, 'Player', None)
        if player is None:
            return None
        return self

    def IsPlayer(self) -> bool:
        """AActor::IsPlayer() - inline from UnActor.h."""
        if not self.IsA(APawn.StaticClass()):
            return False
        return getattr(self, 'bIsPlayer', False)

    def IsBlockedBy(self, Other: Any) -> bool:
        """AActor::IsBlockedBy() - inline from UnActor.h."""
        if Other == self.Level:
            return getattr(self, 'bCollideWorld', False)
        if Other.IsBrush():
            ob = getattr(Other, 'bCollideWorld', False)
            return (ob and
                    (Other.GetPlayerPawn() and self.bBlockPlayers or
                     Other.bBlockActors))
        if self.IsBrush():
            ob = getattr(Other, 'bCollideWorld', False)
            return (ob and
                    (Other.GetPlayerPawn() and Other.bBlockPlayers or
                     Other.bBlockActors))
        return ((self.GetPlayerPawn() or self.IsA(AProjectile.StaticClass())) and
                Other.bBlockPlayers and
                (Other.GetPlayerPawn() or Other.IsA(AProjectile.StaticClass()))) and \
               (Other.GetPlayerPawn() or Other.IsA(AProjectile.StaticClass())) and \
               (Other.bBlockPlayers or Other.bBlockActors)

    def IsBasedOn(self, Other: Any) -> bool:
        """AActor::IsBasedOn() - inline from UnActor.h."""
        for Test in [self, *(getattr(self, 'Base', []))]:
            if Test == Other:
                return True
        return False

    def GetLevel(self) -> ULevel:
        """AActor::GetLevel() - inline from UnActor.h."""
        return self.XLevel

    def GetViewRotation(self) -> Any:
        """AActor::GetViewRotation() - inline from UnActor.h."""
        if self.IsA(APawn.StaticClass()):
            return getattr(self, 'ViewRotation', None)
        return self.Rotation

    def GetPrimitive(self) -> Any:
        """AActor::GetPrimitive() - inline from UnActor.h."""
        if self.Brush:
            return self.Brush
        elif self.Mesh:
            return self.Mesh
        else:
            return self.Level.Engine.Cylinder

    __all__ = ["AActor"]