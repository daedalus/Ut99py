"""Tests for Engine/Inc/UnReach.h port (engine/unreach.py)."""

import pytest

from ut99py.engine.unreach import FReachSpec

# EReachSpecFlags (APawn.h): the move flags a reach spec can require.
R_WALK = 1
R_FLY = 2
R_JUMP = 8


class RecordingArchive:
    """Double that records what the reach spec serializer writes."""

    def __init__(self):
        self.written = []

    def __lshift__(self, value):
        self.written.append(value)
        return value


def test_reach_spec_defaults():
    reach = FReachSpec()
    assert reach.distance == 0
    assert reach.Start is None
    assert reach.End is None
    assert reach.CollisionRadius == 0
    assert reach.CollisionHeight == 0
    assert reach.reachFlags == 0
    assert reach.bPruned == 0


def test_supports_matches_inline_cpp_body():
    reach = FReachSpec()
    reach.CollisionRadius = 34
    reach.CollisionHeight = 88
    reach.reachFlags = R_WALK

    # CollisionRadius >= iRadius && CollisionHeight >= iHeight
    assert reach.supports(34, 88, R_WALK) is True
    assert reach.supports(33, 88, R_WALK) is True
    assert reach.supports(35, 88, R_WALK) is False
    assert reach.supports(34, 89, R_WALK) is False

    # (reachFlags & moveFlags) == reachFlags
    assert reach.supports(34, 88, R_WALK | R_FLY) is True
    assert reach.supports(34, 88, R_JUMP) is False
    assert reach.supports(34, 88, 0) is False


def test_supports_ignores_distance():
    reach = FReachSpec()
    reach.CollisionRadius = 34
    reach.CollisionHeight = 88
    reach.reachFlags = R_WALK
    reach.distance = 10000
    assert reach.supports(34, 88, R_WALK) is True


def test_init_zeroes_every_member():
    reach = FReachSpec()
    reach.distance = 5
    reach.Start = object()
    reach.End = object()
    reach.CollisionRadius = 10
    reach.CollisionHeight = 20
    reach.reachFlags = R_FLY
    reach.bPruned = 1

    reach.Init()

    assert reach.distance == 0
    assert reach.Start is None
    assert reach.End is None
    assert reach.CollisionRadius == 0
    assert reach.CollisionHeight == 0
    assert reach.reachFlags == 0
    assert reach.bPruned == 0


def test_serialize_writes_members_in_cpp_order():
    reach = FReachSpec()
    reach.distance = 7
    reach.Start = "start"
    reach.End = "end"
    reach.CollisionRadius = 34
    reach.CollisionHeight = 88
    reach.reachFlags = R_WALK
    reach.bPruned = 1

    archive = RecordingArchive()
    reach.serialize(archive)

    assert archive.written == [7, "start", "end", 34, 88, R_WALK, 1]


def test_lib_bodies_raise():
    reach = FReachSpec()
    other = FReachSpec()
    with pytest.raises(NotImplementedError):
        reach + other
    with pytest.raises(NotImplementedError):
        reach <= other
    with pytest.raises(NotImplementedError):
        reach == other
    with pytest.raises(NotImplementedError):
        reach.defineFor(None, None, None)
    with pytest.raises(NotImplementedError):
        reach.MonsterPath()
    with pytest.raises(NotImplementedError):
        reach.BotOnlyPath()
    with pytest.raises(NotImplementedError):
        reach.findBestReachable(None, None, None)
