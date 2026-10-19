"""Port of Engine/Inc/AActor.h (2 declared symbols).

AActor base actor class + APlayerPawn reference. Methods raise NotImplementedError("Engine.lib") per port fidelity.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import UObject, UClass
from ..engine import ULevel

class AActor(UObject):
    """AActor (AActor.h)"""
    def __init__(self):
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


__all__ = ["AActor"]
