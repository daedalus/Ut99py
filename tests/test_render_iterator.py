"""Tests for Engine/Inc/UnRenderIteratorSupport.h."""
from ut99py.engine.render_iterator import ActorBuffer, FActorNode


def test_actor_buffer():
    buf = ActorBuffer()
    assert len(buf.Buffer) == 256
    assert isinstance(buf.Buffer, bytearray)


def test_factornode_defaults():
    node = FActorNode()
    assert isinstance(node.ActorProxy, ActorBuffer)
    assert node.NextNode is None


def test_factornode_link():
    n1 = FActorNode()
    n2 = FActorNode()
    n1.NextNode = n2
    assert n1.NextNode is n2