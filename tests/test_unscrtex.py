"""Tests for Engine/Inc/UnScrTex.h port (engine/unscrtex.py)."""

import pytest

from ut99py.engine.unscrtex import UScriptedTexture
from ut99py.engine.texture import UTexture


def test_uscriptedtexture_is_a_utexture():
    assert issubclass(UScriptedTexture, UTexture)


def test_uscriptedtexture_constructor_is_in_engine_lib():
    with pytest.raises(NotImplementedError):
        UScriptedTexture()


def test_post_edit_change_calls_post_load():
    texture = UScriptedTexture.__new__(UScriptedTexture)
    with pytest.raises(NotImplementedError, match="UScriptedTexture::PostLoad"):
        texture.PostEditChange()


def test_lib_bodies_raise():
    texture = UScriptedTexture.__new__(UScriptedTexture)
    with pytest.raises(NotImplementedError):
        texture.PostLoad()
    with pytest.raises(NotImplementedError):
        texture.Destroy()
    with pytest.raises(NotImplementedError):
        texture.Init(64, 64)
    with pytest.raises(NotImplementedError):
        texture.Tick(0.016)
    with pytest.raises(NotImplementedError):
        texture.DrawTile(0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, None, None, False)
    with pytest.raises(NotImplementedError):
        texture.execDrawText(None)
    with pytest.raises(NotImplementedError):
        texture.execDrawTile(None)
    with pytest.raises(NotImplementedError):
        texture.execDrawColoredText(None)
    with pytest.raises(NotImplementedError):
        texture.execReplaceTexture(None)
    with pytest.raises(NotImplementedError):
        texture.execTextSize(None)
