"""Port of Engine/Inc/UnScrTex.h (1 declared symbol).

UScriptedTexture: a UTexture whose contents are drawn from UnrealScript.
PostEditChange() has an inline body (it calls PostLoad); every other body
lives in UnScrTex.cpp and raises NotImplementedError.
"""

from __future__ import annotations
from typing import Any, Optional
from .texture import FTextureInfo, UTexture


class UScriptedTexture(UTexture):
    """UScriptedTexture (UnScrTex.h:13-45)"""

    def __init__(self) -> None:
        super().__init__()
        # Variables (UnScrTex.h:28-29).
        self.NotifyActor: Optional[Any] = None  # AActor*
        self.SourceTexture: Optional[UTexture] = None
        # Private (UnScrTex.h:38-42).
        self.OldSourceTex: Optional[UTexture] = None
        self.LocalSourceBitmap: Optional[bytearray] = None  # BYTE*
        self.PaletteMap: Optional[Any] = None  # TMap<UTexture*, TArray<BYTE>>*
        self.LocalTime: float = 0.0
        # UScriptedTexture() body is in UnScrTex.cpp.
        raise NotImplementedError("C++ UScriptedTexture constructor: Engine.lib")

    def PostLoad(self) -> None:
        raise NotImplementedError("C++ UScriptedTexture::PostLoad: Engine.lib")

    def PostEditChange(self) -> None:
        """UScriptedTexture::PostEditChange (UnScrTex.h:21) - inline body."""
        self.PostLoad()

    def Destroy(self) -> None:
        raise NotImplementedError("C++ UScriptedTexture::Destroy: Engine.lib")

    def Init(self, InUSize: int, InVSize: int) -> None:
        raise NotImplementedError("C++ UScriptedTexture::Init: Engine.lib")

    def Tick(self, DeltaSeconds: float) -> None:
        raise NotImplementedError("C++ UScriptedTexture::Tick: Engine.lib")

    def DrawTile(
        self,
        X: float,
        Y: float,
        XL: float,
        YL: float,
        U: float,
        V: float,
        UL: float,
        VL: float,
        Tex: UTexture,
        Info: FTextureInfo,
        bMasked: bool,
        bUseColor: bool = False,
        ColorIndex: int = 0,
    ) -> None:
        raise NotImplementedError("C++ UScriptedTexture::DrawTile: Engine.lib")

    # Natives (UnScrTex.h:33-37): DECLARE_FUNCTION declares
    # `void name(FFrame& TheStack, RESULT_DECL)` members.
    def execDrawText(self, TheStack: Any, Result: Any = None) -> None:
        raise NotImplementedError("C++ UScriptedTexture::execDrawText: Engine.lib")

    def execDrawTile(self, TheStack: Any, Result: Any = None) -> None:
        raise NotImplementedError("C++ UScriptedTexture::execDrawTile: Engine.lib")

    def execDrawColoredText(self, TheStack: Any, Result: Any = None) -> None:
        raise NotImplementedError(
            "C++ UScriptedTexture::execDrawColoredText: Engine.lib"
        )

    def execReplaceTexture(self, TheStack: Any, Result: Any = None) -> None:
        raise NotImplementedError(
            "C++ UScriptedTexture::execReplaceTexture: Engine.lib"
        )

    def execTextSize(self, TheStack: Any, Result: Any = None) -> None:
        raise NotImplementedError("C++ UScriptedTexture::execTextSize: Engine.lib")


__all__ = ["UScriptedTexture"]
