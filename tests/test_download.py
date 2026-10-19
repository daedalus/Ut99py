"""Tests for Engine/Inc/UnDownload.h."""
import pytest
from ut99py.engine.download import UDownload, UChannelDownload

def test_udownload_noconstruct():
    with pytest.raises(NotImplementedError):
        UDownload()

def test_uchannel_download_noconstruct():
    with pytest.raises(NotImplementedError):
        UChannelDownload()

def test_udownload_fields():
    dl = UDownload.__new__(UDownload)
    assert dl.Connection is None
    assert dl.PackageIndex == 0
    assert dl.UseCompression is False
    assert dl.Transfered == 0
    assert dl.SkippedFile is False
    assert dl.IsCompressed is False

def test_udownload_tick():
    dl = UDownload.__new__(UDownload)
    # virtual void Tick() {} -> no raise
    dl.Tick()

def test_udownload_lib_methods_raise():
    dl = UDownload.__new__(UDownload)
    with pytest.raises(NotImplementedError):
        dl.Serialize(None)
    with pytest.raises(NotImplementedError):
        dl.TrySkipFile()
    with pytest.raises(NotImplementedError):
        dl.ReceiveFile(None, 0)

def test_uchannel_download_ch():
    cdl = UChannelDownload.__new__(UChannelDownload)
    assert cdl.Ch is None
