"""Tests for Core/Inc/UnScript.h FFrame/FStateFrame inline methods."""

import struct

from ut99py.core.objects import UStruct
from ut99py.core.script import FFrame, FStateFrame


class _FakeNode:
    """Stands in for a UStruct whose get_class/get_full_name are wired."""

    def get_full_name(self):
        return "Core.MyState"


class _FakeObject:
    """Stands in for a UObject: get_class() returns a node."""

    def __init__(self, node):
        self._node = node

    def get_class(self):
        return self._node


def test_read_int_is_signed_32bit():
    # UnScript.h:122: INT is 32-bit signed (UnGnuG.h).
    frame = FFrame()
    frame.Code = struct.pack("<i", -5) + b"\xff"
    assert frame.read_int() == -5
    assert frame.Code == b"\xff"


def test_read_word_is_unsigned_16bit():
    # UnScript.h:155: a _WORD is 16-bit unsigned (UnGnuG.h:125), widened to INT.
    frame = FFrame()
    frame.Code = struct.pack("<H", 0xFFFF) + b"\x01"
    assert frame.read_word() == 0xFFFF
    assert frame.Code == b"\x01"


def test_read_float_matches_ieee754():
    # UnScript.h:144.
    frame = FFrame()
    frame.Code = struct.pack("<f", 1.5) + b"\x01"
    assert frame.read_float() == 1.5
    assert frame.Code == b"\x01"


def test_read_object_consumes_four_bytes():
    # UnScript.h:133: reads sizeof(INT); the port returns the raw index.
    frame = FFrame()
    frame.Code = struct.pack("<I", 1234) + b"\x01"
    assert frame.read_object() == 1234
    assert frame.Code == b"\x01"


def test_read_name_returns_a_four_byte_index():
    # UnScript.h:168: sizeof(FName) is 4 bytes (a single NAME_INDEX, UnName.h).
    frame = FFrame()
    frame.Code = struct.pack("<I", 42) + b"\x01"
    assert frame.read_name() == 42
    assert frame.Code == b"\x01"


def test_fframe_from_node_slices_the_script_at_code_offset():
    # UnScript.h:109: Code = &InNode->Script(CodeOffset).
    node = UStruct()
    node._script = b"\x01\x02\x03\x04\x05"
    frame = FFrame(InNode=node, CodeOffset=2)
    assert frame.Code == b"\x03\x04\x05"
    assert frame.Object is None


def test_fframe_from_object_leaves_code_null():
    # UnScript.h:103: the single-arg ctor leaves Code NULL.
    node = _FakeNode()
    frame = FFrame(InObject=_FakeObject(node))
    assert frame.Node is node
    assert frame.Object is not None
    assert frame.Code is None


def test_state_frame_ctor_defaults():
    # UnScript.h:185: Node/StateNode = class, ProbeMask = ~(QWORD)0.
    node = _FakeNode()
    frame = FStateFrame(_FakeObject(node))
    assert frame.Node is node
    assert frame.StateNode is node
    assert frame.ProbeMask == 0xFFFFFFFFFFFFFFFF
    assert frame.CurrentFrame is None
    assert frame.LatentAction == 0


def test_state_frame_describe_uses_the_node_full_name():
    # UnScript.h:191: Node ? Node->GetFullName() : "None".
    with_node = FStateFrame(_FakeObject(_FakeNode()))
    assert with_node.describe() == "Core.MyState"
    assert FStateFrame().describe() == "None"
