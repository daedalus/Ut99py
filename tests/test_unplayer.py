"""Tests for Engine/Inc/UnPlayer.h port (engine/unplayer.py)."""

import pytest

from ut99py.engine.unplayer import UPlayer


def test_uplayer_constructor_is_in_engine_lib():
    with pytest.raises(NotImplementedError):
        UPlayer()


def test_uplayer_methods_are_in_engine_lib():
    player = UPlayer.__new__(UPlayer)
    with pytest.raises(NotImplementedError):
        player.Serialize(None)
    with pytest.raises(NotImplementedError):
        player.Destroy()
    with pytest.raises(NotImplementedError):
        player.Exec("stat fps")
    with pytest.raises(NotImplementedError):
        player.ReadInput(0.016)
