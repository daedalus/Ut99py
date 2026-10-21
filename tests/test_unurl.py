"""Tests for Engine/Inc/UnURL.h port (engine/unurl.py)."""

import pytest

from ut99py.engine.unurl import FURL


def test_furl_constructor_is_in_engine_lib():
    with pytest.raises(NotImplementedError):
        FURL()


def test_furl_static_methods_are_in_engine_lib():
    with pytest.raises(NotImplementedError):
        FURL.StaticInit()
    with pytest.raises(NotImplementedError):
        FURL.StaticExit()


def test_furl_methods_are_in_engine_lib():
    url = FURL.__new__(FURL)
    with pytest.raises(NotImplementedError):
        url.IsInternal()
    with pytest.raises(NotImplementedError):
        url.IsLocalInternal()
    with pytest.raises(NotImplementedError):
        url.HasOption("game")
    with pytest.raises(NotImplementedError):
        url.GetOption("game")
    with pytest.raises(NotImplementedError):
        url.LoadURLConfig("Engine")
    with pytest.raises(NotImplementedError):
        url.SaveURLConfig("Engine", "URL")
    with pytest.raises(NotImplementedError):
        url.AddOption("?game=ut99")
    with pytest.raises(NotImplementedError):
        url.String()
    with pytest.raises(NotImplementedError):
        url.serialize(None)
    with pytest.raises(NotImplementedError):
        url == FURL.__new__(FURL)


def test_furl_static_defaults_are_empty():
    # FURL::StaticInit fills these from the URL config section; until it
    # runs they keep their zero value.
    assert FURL.DefaultProtocol == ""
    assert FURL.DefaultName == ""
    assert FURL.DefaultMap == ""
    assert FURL.DefaultHost == ""
    assert FURL.DefaultPort == 0
