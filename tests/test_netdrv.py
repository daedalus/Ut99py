"""Tests for Engine/Inc/UnNetDrv.h port (engine/netdrv.py)."""

import pytest

from ut99py.engine.netdrv import UNetDriver, UPackageMapLevel
from ut99py.engine import UNetConnection
from ut99py.core.types import FTime


def test_package_map_level():
    pml = UPackageMapLevel()
    assert pml.Connection is None

    conn = UNetConnection()
    pml2 = UPackageMapLevel(conn)
    assert pml2.Connection is conn


def test_package_map_level_lib_bodies_raise():
    pml = UPackageMapLevel()
    with pytest.raises(NotImplementedError):
        pml.CanSerializeObject(None)
    with pytest.raises(NotImplementedError):
        pml.SerializeObject(None, None, None)


def test_net_driver_defaults():
    drv = UNetDriver()
    assert drv.ClientConnections == []
    assert drv.ServerConnection is None
    assert drv.Notify is None
    assert drv.MasterMap is None
    assert isinstance(drv.Time, FTime)
    assert drv.ConnectionTimeout == 0.0
    assert drv.MaxClientRate == 0
    assert drv.AllowDownloads is False
    assert drv.ProfileStats is False
    assert drv.SendCycles == 0
    assert drv.RecvCycles == 0
    assert drv.MaxDownloadSize == 0
    assert drv.DownloadManagers == []


def test_net_driver_lib_bodies_raise():
    drv = UNetDriver()
    with pytest.raises(NotImplementedError):
        drv.StaticConstructor()
    with pytest.raises(NotImplementedError):
        drv.Destroy()
    with pytest.raises(NotImplementedError):
        drv.Serialize(None)
    with pytest.raises(NotImplementedError):
        drv.LowLevelDestroy()
    with pytest.raises(NotImplementedError):
        drv.LowLevelGetNetworkNumber()
    with pytest.raises(NotImplementedError):
        drv.AssertValid()
    with pytest.raises(NotImplementedError):
        drv.InitConnect(None, None, None)
    with pytest.raises(NotImplementedError):
        drv.InitListen(None, None, None)
    with pytest.raises(NotImplementedError):
        drv.TickFlush()
    with pytest.raises(NotImplementedError):
        drv.TickDispatch(0.0)
    with pytest.raises(NotImplementedError):
        drv.Exec("cmd")
    with pytest.raises(NotImplementedError):
        drv.NotifyActorDestroyed(None)
