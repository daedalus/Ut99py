"""Tests for Engine/Inc/UnDemoRec.h."""
import pytest
from ut99py.engine.demorec import UDemoRecConnection, UDemoRecDriver

def test_udemo_rec_connection():
    with pytest.raises(NotImplementedError):
        UDemoRecConnection()
    # Check method existence
    conn = UDemoRecConnection.__new__(UDemoRecConnection)
    assert hasattr(conn, "LowLevelGetRemoteAddress")

def test_udemo_rec_driver():
    drv = UDemoRecDriver()
    assert drv.DemoFilename == ""
    # All method calls raise NotImplementedError
    with pytest.raises(NotImplementedError):
        drv.StaticConstructor()
    with pytest.raises(NotImplementedError):
        drv.LowLevelDestroy()
