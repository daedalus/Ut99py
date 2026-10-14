"""FCompactIndex must match the serializer declared in Core/Inc/UnArc.h:220.

Expected byte sequences are derived from the algorithm documented in
Help/PACKAGES.md ("Compact Indices", the disassembled Core.lib implementation),
not from the Python code under test.
"""

import pytest

from ut99py.core.types import FCompactIndex

# (value, expected on-disk bytes)
ENCODINGS = [
    (0, b"\x00"),
    (1, b"\x01"),
    (63, b"\x3f"),          # largest single-byte positive value
    (64, b"\x40\x01"),      # first value that needs a continuation byte
    (127, b"\x7f\x01"),
    (128, b"\x40\x02"),
    (1000, b"\x68\x0f"),
    (16384, b"\x40\x80\x02"),
    (-1, b"\x81"),
    (-65, b"\xc1\x01"),
    (-128, b"\xc0\x02"),
]


@pytest.mark.parametrize("value,expected", ENCODINGS)
def test_encode_matches_cpp_serializer(value, expected):
    assert FCompactIndex(value).encode() == expected


@pytest.mark.parametrize("value,expected", ENCODINGS)
def test_decode_matches_cpp_serializer(value, expected):
    index, consumed = FCompactIndex.decode(expected)
    assert index.value == value
    assert consumed == len(expected)


def test_decode_honours_offset_and_reports_consumed_bytes():
    data = b"\xff\xff" + b"\x40\x02" + b"\xff"
    index, consumed = FCompactIndex.decode(data, 2)
    assert index.value == 128
    assert consumed == 4


@pytest.mark.parametrize("value", [0, 1, 63, 64, 1000, 2**31 - 1, -2**31])
def test_roundtrip_at_int32_boundaries(value):
    index, consumed = FCompactIndex.decode(FCompactIndex(value).encode())
    assert index.value == value
    assert consumed > 0


def test_encode_rejects_values_that_do_not_survive_the_roundtrip():
    # The C++ serializer appErrorf()s when saving changes the value; 2**31 does
    # not fit a 32-bit INT and wraps negative.
    with pytest.raises(ValueError):
        FCompactIndex(2**31).encode()
