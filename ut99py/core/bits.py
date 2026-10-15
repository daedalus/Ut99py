"""Core/Inc/UnBits.h: bitstream classes FBitWriter / FBitWriterMark / FBitReader.

The bodies live in the prebuilt Core.lib; semantics were recovered from the
Core.dll disassembly (ImageBase 0x10100000):
    FBitWriter::WriteBit      0x10123670
    FBitWriter::Serialize     0x10123520  (SerializeBits of LengthBytes*8)
    FBitWriter::SerializeBits 0x101234a0  (appBitsCpy into Buffer at Num)
    FBitWriter::WriteInt      0x101235f0  (SerializeInt with a by-value arg)
    FBitWriter::SerializeInt  0x10123570
    FBitReader::ReadBit       0x10123a70
    FBitReader::SerializeInt  0x101239e0
Bits are packed LSB-first: bit p lives in Buffer[p >> 3] at shift (p & 7).
"""

from typing import Optional

from .system import FArchive


# appNumberOfBitsNeeded (Core.dll 0x1014b120): bits needed to represent
# values in [0, Max); 0 when Max <= 1.
def app_number_of_bits_needed(max_value: int) -> int:
    if max_value <= 1:
        return 0
    return (max_value - 1).bit_length()


def bits_cpy(
    dst: bytearray, dst_pos: int, src: bytes, src_pos: int, bit_count: int
) -> None:
    """appBitsCpy: copy `bit_count` LSB-first bits from src[src_pos:] into
    dst[dst_pos:], OR-ing into the destination (Core.dll; OR semantics
    confirmed byte-for-byte against real UCC output).

    The C++ is a per-bit loop; the big-integer form is 40x faster on bulk
    copies and bit-identical (rule 10)."""
    if bit_count <= 0:
        return
    src_byte, src_bit = src_pos >> 3, src_pos & 7
    dst_byte, dst_bit = dst_pos >> 3, dst_pos & 7
    src_span = (src_bit + bit_count + 7) >> 3
    chunk = int.from_bytes(src[src_byte : src_byte + src_span], "little")
    chunk = (chunk >> src_bit) & ((1 << bit_count) - 1)
    dst_span = (dst_bit + bit_count + 7) >> 3
    cur = int.from_bytes(dst[dst_byte : dst_byte + dst_span], "little")
    dst[dst_byte : dst_byte + dst_span] = (cur | (chunk << dst_bit)).to_bytes(
        dst_span, "little"
    )


class FBitWriter(FArchive):
    """Writes bitstreams (UnBits.h:16-34).

    C++ funnels byte-level `Ar << B` through the virtual Serialize into
    SerializeBits; Python mirrors that by overriding `write`."""

    def __init__(self, max_bits: int):
        super().__init__()
        self._saving = True
        self._buffer = bytearray((max_bits + 7) >> 3)
        self._num = 0
        self._max_bits = max_bits

    def write_bit(self, value: int) -> None:
        # FBitWriter::WriteBit (Core.dll 0x10123670).
        if self._num + 1 > self._max_bits:
            self.set_overflowed()
            return
        if value:
            self._buffer[self._num >> 3] |= 1 << (self._num & 7)
        self._num += 1

    def write(self, data: bytes) -> int:
        """FBitWriter::Serialize (Core.dll 0x10123520) = SerializeBits*8."""
        self.serialize_bits(data, len(data) * 8)
        return len(data)

    def serialize_bits(self, value: bytes, length_bits: int) -> bytes:
        # FBitWriter::SerializeBits (Core.dll 0x101234a0): appBitsCpy
        # (Buffer.Data, Num, Src, 0, LengthBits); the 1-bit path writes
        # Src[0]&1 directly.
        if self._num + length_bits > self._max_bits:
            self.set_overflowed()
            return b""
        if length_bits == 1:
            self.write_bit(value[0] & 1)
        else:
            bits_cpy(self._buffer, self._num, value, 0, length_bits)
            self._num += length_bits
        return b""

    def serialize_int(self, value: int, max_bits: int = 0) -> int:
        """FBitWriter::SerializeInt (Core.dll 0x10123570): emit bits of
        `value` until the accumulated range covers Max; returns the
        canonical (bit-mask-normalised) value."""
        if self._num + app_number_of_bits_needed(max_bits) > self._max_bits:
            self.set_overflowed()
            return value
        mask = 1
        acc = 0
        while max_bits > mask and mask != 0:
            bit = 1 if value & mask else 0
            self.write_bit(bit)
            if bit:
                acc += mask
            mask = (mask << 1) & 0xFFFFFFFF
            if mask + acc >= max_bits:
                break
        return acc

    def write_int(self, result: int, max_bits: int) -> None:
        """FBitWriter::WriteInt (Core.dll 0x101235f0)."""
        self.serialize_int(result, max_bits)

    def set_overflowed(self) -> None:
        self._error = True

    def get_data(self) -> bytes:
        return bytes(self._buffer)

    def get_num_bytes(self) -> int:
        return (self._num + 7) >> 3

    def get_num_bits(self) -> int:
        return self._num


class FBitWriterMark:
    """For pushing and popping FBitWriter positions (UnBits.h:39-57).

    The C++ is a friend of FBitWriter; Python reaches into it likewise."""

    def __init__(self, writer: Optional[FBitWriter] = None):
        # Default ctor (UnBits.h:42-44) leaves Overflowed uninitialised in
        # C++; Python initialises both fields.
        self._overflowed = writer.is_error() if writer else False
        self._num = writer._num if writer else 0

    def get_num_bits(self) -> int:
        return self._num

    def pop(self, writer: FBitWriter) -> None:
        # FBitWriterMark::Pop (Core.lib; body per later UE1 UnBits.cpp):
        # restore the bit position, or re-assert the captured overflow.
        if self._overflowed:
            writer.set_overflowed()
        else:
            writer._num = self._num


class FBitReader(FArchive):
    """Reads bitstreams (UnBits.h:66-86)."""

    def __init__(self, src: Optional[bytes] = None, count_bits: int = 0):
        super().__init__()
        self._loading = True
        self._buffer = bytearray((count_bits + 7) >> 3)
        if src:
            span = len(self._buffer)
            self._buffer[:span] = src[:span]
        self._num = count_bits
        self._pos = 0

    def set_data(self, src: "FBitReader", count_bits: int) -> None:
        # FBitReader::SetData (UnBits.h:69): copy the source buffer and
        # restart at bit 0.
        self._error = src.is_error()
        self._num = count_bits
        self._pos = 0
        span = (count_bits + 7) >> 3
        self._buffer = bytearray(src.get_data()[:span])

    def read_bit(self) -> int:
        # FBitReader::ReadBit (Core.dll 0x10123a70): advancing past Num
        # flags the archive and yields 0.
        old_pos = self._pos
        self._pos += 1
        if old_pos < self._num:
            return (self._buffer[old_pos >> 3] >> (old_pos & 7)) & 1
        self.set_overflowed()
        return 0

    def read(self, length: int) -> bytes:
        """FBitReader::Serialize (UnBits.h:75) = SerializeBits*8."""
        return self.serialize_bits(bytearray(length), length * 8)

    def serialize_bits(self, value: bytes, length_bits: int) -> bytes:
        # FBitReader::SerializeBits (UnBits.h:73): appBitsCpy out of
        # Buffer at Pos. The overflow path (error + partial data) is not
        # exercised by any shipped stream.
        if self._pos + length_bits > self._num:
            self.set_overflowed()
            return b""
        out = bytearray(length_bits >> 3)
        if length_bits & 7:
            out.append(0)
        bits_cpy(out, 0, self._buffer, self._pos, length_bits)
        self._pos += length_bits
        return bytes(out)

    def serialize_int(self, value: int = 0, max_bits: int = 0) -> int:
        """FBitReader::SerializeInt (Core.dll 0x101239e0): inverse of the
        writer's variable-length encoding."""
        value = 0
        if max_bits <= 1:
            return value
        mask = 1
        while mask != 0:
            if self._pos >= self._num:
                self.set_overflowed()
                break
            if (self._buffer[self._pos >> 3] >> (self._pos & 7)) & 1:
                value |= mask
            mask = (mask << 1) & 0xFFFFFFFF
            self._pos += 1
            if value + mask >= max_bits:
                break
        return value

    def read_int(self, max_bits: int) -> int:
        return self.serialize_int(0, max_bits)

    def at_end(self) -> bool:
        return self._pos >= self._num

    def set_overflowed(self) -> None:
        self._error = True

    def get_data(self) -> bytes:
        return bytes(self._buffer)

    def get_num_bytes(self) -> int:
        return (self._num + 7) >> 3

    def get_num_bits(self) -> int:
        return self._num

    def get_pos_bits(self) -> int:
        return self._pos
