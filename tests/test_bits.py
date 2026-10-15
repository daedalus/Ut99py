"""Tests for core/bits.py (UnBits.h).

Expected values derive from the Core.dll disassembly semantics (LSB-first
packing, OR-into-dest appBitsCpy, variable-length SerializeInt), not from
the Python implementation.
"""

import random

import pytest

from ut99py.core.bits import (
    FBitReader,
    FBitWriter,
    FBitWriterMark,
    app_number_of_bits_needed,
    bits_cpy,
)
from ut99py.core.system import FArchiveMemoryReader


def naive_bits_cpy(dst, dst_pos, src, src_pos, bit_count):
    """Reference per-bit appBitsCpy: LSB-first copy, OR into dst."""
    for i in range(bit_count):
        if (src[(src_pos + i) >> 3] >> ((src_pos + i) & 7)) & 1:
            dst[(dst_pos + i) >> 3] |= 1 << ((dst_pos + i) & 7)


def test_app_number_of_bits_needed():
    # appNumberOfBitsNeeded (Core.dll 0x1014b120): 0 for Max<=1, else
    # bits of Max-1.
    assert app_number_of_bits_needed(0) == 0
    assert app_number_of_bits_needed(1) == 0
    assert app_number_of_bits_needed(2) == 1
    assert app_number_of_bits_needed(3) == 2
    assert app_number_of_bits_needed(5) == 3
    assert app_number_of_bits_needed(256) == 8
    assert app_number_of_bits_needed(257) == 9


def test_bits_cpy_aligned():
    dst = bytearray(4)
    bits_cpy(dst, 0, b"\xa5", 0, 8)
    assert bytes(dst) == b"\xa5\x00\x00\x00"


def test_bits_cpy_or_into_dst():
    # appBitsCpy ORs; a second copy over an occupied region merges bits.
    dst = bytearray(b"\x0f")
    bits_cpy(dst, 0, b"\xf0", 0, 8)
    assert dst[0] == 0xFF


def test_bits_cpy_unaligned_matches_naive():
    # Scripted RNG: fixed seed, exact-output comparison against the
    # per-bit reference (test rule: no retry loops, deterministic).
    rnd = random.Random(7)
    for _ in range(500):
        dst_pos = rnd.randrange(0, 64)
        src_pos = rnd.randrange(0, 64)
        count = rnd.randrange(0, 200)
        src = bytes(rnd.randrange(256) for _ in range((src_pos + count + 7) // 8 + 2))
        span = (dst_pos + count + 7) // 8 + 2
        fast = bytearray(span)
        naive = bytearray(span)
        bits_cpy(fast, dst_pos, src, src_pos, count)
        naive_bits_cpy(naive, dst_pos, src, src_pos, count)
        assert fast == naive


def test_write_bit_lsb_first():
    # WriteBit (Core.dll 0x10123670): bit p in byte p>>3 at shift p&7.
    w = FBitWriter(16)
    for bit in (1, 0, 1):
        w.write_bit(bit)
    assert w.get_num_bits() == 3
    assert w.get_num_bytes() == 1
    assert w.get_data()[0] == 0b101


def test_write_across_byte_boundary():
    # 0x02 = bits 0,1,0,0,0,0,0,0; starting at bit 1 it lands at
    # positions 1..8, i.e. byte0=0b00000101, byte1 bit8=src bit7=0.
    w = FBitWriter(24)
    w.write_bit(1)
    w.write(b"\x02")
    assert w.get_num_bits() == 9
    assert w.get_data()[:2] == b"\x05\x00"


def test_serialize_byte_routes_through_bits():
    # C++ `Ar << B` funnels through virtual Serialize -> SerializeBits;
    # the Python override of `write` must reproduce that packing.
    w = FBitWriter(32)
    w.serialize_byte(0xDE)
    w.serialize_byte(0xAD)
    assert w.get_data()[:2] == b"\xde\xad"
    assert w.get_num_bits() == 16


def test_overflow_sets_error():
    w = FBitWriter(4)
    w.write(b"\xff")  # 8 bits into a 4-bit writer
    assert w.is_error()
    w2 = FBitWriter(1)
    w2.write_bit(1)
    assert not w2.is_error()
    w2.write_bit(1)
    assert w2.is_error()


def test_reader_roundtrip_bits():
    payload = bytes(range(64))
    w = FBitWriter(64 * 8)
    w.write(payload)
    r = FBitReader(w.get_data(), w.get_num_bits())
    assert r.read(64) == payload
    assert r.at_end()
    assert not r.is_error()


def test_reader_partial_byte_bits():
    # 12 bits packed LSB-first: value 0xabc -> low byte 0xbc, high nibble a.
    data = bytes([0xBC, 0x0A])
    r = FBitReader(data, 12)
    assert r.serialize_bits(b"\x00\x00", 12) == b"\xbc\x0a"
    assert r.at_end()


def test_reader_read_past_end_flags_error():
    r = FBitReader(b"\xff", 8)
    assert r.read(1) == b"\xff"  # read takes bytes; the stream is 8 bits.
    assert r.read_bit() == 0
    assert r.is_error()


@pytest.mark.parametrize("max_bits", [2, 3, 5, 10, 256, 257, 65537])
def test_serialize_int_roundtrip(max_bits):
    # SerializeInt (writer 0x10123570 / reader 0x101239e0): encode any
    # value < Max and recover it exactly.
    values = list(range(max_bits))
    if max_bits > 64:
        rnd = random.Random(max_bits)
        values += [rnd.randrange(max_bits) for _ in range(64)]
    for value in values:
        w = FBitWriter(64)
        encoded = w.serialize_int(value, max_bits)
        assert encoded == value  # Value < Max is already canonical.
        r = FBitReader(w.get_data(), w.get_num_bits())
        assert r.serialize_int(0, max_bits) == value


def test_serialize_int_max_one_writes_nothing():
    w = FBitWriter(8)
    assert w.serialize_int(0, 1) == 0
    assert w.get_num_bits() == 0
    r = FBitReader(b"", 0)
    assert r.serialize_int(0, 1) == 0
    assert not r.is_error()


def test_write_int_matches_serialize_int():
    w = FBitWriter(64)
    w.write_int(3, 5)
    w2 = FBitWriter(64)
    w2.serialize_int(3, 5)
    assert w.get_data() == w2.get_data()
    assert w.get_num_bits() == w2.get_num_bits()


def test_mark_pop_restores_position():
    w = FBitWriter(64)
    w.write(b"\x01\x02")
    mark = FBitWriterMark(w)
    assert mark.get_num_bits() == 16
    w.write(b"\x03\x04")
    assert w.get_num_bits() == 32
    mark.pop(w)
    assert w.get_num_bits() == 16
    assert w.get_num_bytes() == 2
    w.write(b"\x03\x04")
    # GetData returns the whole buffer (C++ TArray<BYTE>&), which still
    # holds the overwritten bytes; the re-written bits land on top.
    assert w.get_data()[:4] == b"\x01\x02\x03\x04"


def test_mark_pop_reasserts_overflow():
    w = FBitWriter(8)
    w.write(b"\xff\xff")  # Overflow the 8-bit writer.
    assert w.is_error()
    bad = FBitWriterMark(w)
    fresh = FBitWriter(8)
    bad.pop(fresh)
    # The mark captured Overflowed=True; Pop re-asserts it on the writer.
    assert fresh.is_error()


def test_reader_set_data():
    src = FBitReader(b"\x5a\xff", 12)
    src.read_bit()  # Advance Pos; SetData copies the buffer and resets it.
    r = FBitReader()
    r.set_data(src, 12)
    assert r.get_pos_bits() == 0
    assert r.serialize_bits(b"\x00", 12) == b"\x5a\x0f"


def test_reader_at_end_and_counts():
    r = FBitReader(b"\x01\x02", 12)
    assert r.get_num_bits() == 12
    assert r.get_num_bytes() == 2
    assert not r.at_end()
    r.read(1)  # 8 bits
    assert not r.at_end()
    r.serialize_bits(b"\x00", 4)  # The final nibble.
    assert r.at_end()
    assert r.get_pos_bits() == 12


def test_memory_reader_feeds_bit_reader():
    # The Huffman codec path: byte archive -> raw bits -> FBitReader.
    # 8 bits starting at bit 1 of ff 0f = 1111111_1 -> 0xff.
    ar = FArchiveMemoryReader(b"\xff\x0f")
    r = FBitReader(ar.read(2), 12)
    assert r.read_bit() == 1
    assert r.serialize_byte(0) == 0xFF
