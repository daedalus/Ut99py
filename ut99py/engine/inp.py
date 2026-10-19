"""Port of Engine/Inc/UnIn.h (2 declared symbols).

UInput (USubsystem) input subsystem + FAlias struct.
All method bodies raise NotImplementedError("Engine.lib") except accessors (inline).
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import USubsystem, FString, FName
from ..core.template import FStringNoInit
from ..core.objects import UEnum
from ..engine import UViewport

ALIAS_MAX: int = 40
IK_MAX: int = 256  # input keys


class FAlias:
    """FAlias (UnIn.h:22-30)"""
    def __init__(self) -> None:
        self.Alias: Any = FName()
        self.Command: Any = FStringNoInit()


class UInput(USubsystem):
    """UInput (UnIn.h:34-90)"""

    def __init__(self) -> None:
        super().__init__()
        self.Aliases = [FAlias() for _ in range(ALIAS_MAX)]
        self.Bindings = ["" for _ in range(IK_MAX)]
        self.Viewport: Optional['UViewport'] = None
        self.InputKeys: Optional[UEnum] = None
        self.Action: Any = None
        self.Delta: float = 0.0
        self.KeyDownTable = [0 for _ in range(IK_MAX)]

    def StaticConfigName(self) -> str:
        return "User"

    def StaticConstructor(self) -> None:
        raise NotImplementedError("C++ UInput::StaticConstructor: Engine.lib")

    def Serialize(self, Ar: Any) -> None:
        raise NotImplementedError("C++ UInput::Serialize: Engine.lib")

    @staticmethod
    def StaticInitInput() -> None:
        raise NotImplementedError("C++ UInput::StaticInitInput: Engine.lib")

    def Init(self, viewport: 'UViewport') -> None:
        raise NotImplementedError("C++ UInput::Init: Engine.lib")

    def Exec(self, cmd: str, ar: Any) -> bool:
        raise NotImplementedError("C++ UInput::Exec: Engine.lib")

    def PreProcess(self, i_key: Any, state: Any, delta: float = 0.0) -> bool:
        raise NotImplementedError("C++ UInput::PreProcess: Engine.lib")

    def Process(self, ar: Any, i_key: Any, state: Any, delta: float = 0.0) -> bool:
        raise NotImplementedError("C++ UInput::Process: Engine.lib")

    def DirectAxis(self, key: Any, length: float, delta: float) -> None:
        raise NotImplementedError("C++ UInput::DirectAxis: Engine.lib")

    def ReadInput(self, delta_seconds: float, ar: Any) -> None:
        raise NotImplementedError("C++ UInput::ReadInput: Engine.lib")

    def ResetInput(self) -> None:
        raise NotImplementedError("C++ UInput::ResetInput: Engine.lib")

    def GetKeyName(self, key: Any) -> str:
        raise NotImplementedError("C++ UInput::GetKeyName: Engine.lib")

    def FindKeyName(self, key_name: str, i_key: Any) -> int:
        raise NotImplementedError("C++ UInput::FindKeyName: Engine.lib")

    # Accessors (inline at UnIn.h:78-84).
    def SetInputAction(self, new_action: Any, new_delta: float = 0.0) -> None:
        self.Action = new_action
        self.Delta = new_delta

    def GetInputAction(self) -> Any:
        return self.Action

    def GetInputDelta(self) -> float:
        return self.Delta

    def KeyDown(self, i: int) -> int:
        return self.KeyDownTable[i] if 0 <= i < IK_MAX else 0

    def FindButtonName(self, actor: Any, button_name: str) -> Optional[Any]:
        raise NotImplementedError("C++ UInput::FindButtonName: Engine.lib")

    def FindAxisName(self, actor: Any, button_name: str) -> Optional[Any]:
        raise NotImplementedError("C++ UInput::FindAxisName: Engine.lib")

    def ExecInputCommands(self, cmd: str, ar: Any) -> None:
        raise NotImplementedError("C++ UInput::ExecInputCommands: Engine.lib")


__all__ = ["UInput", "FAlias", "ALIAS_MAX", "IK_MAX"]
