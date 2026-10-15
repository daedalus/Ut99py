"""Core/Inc/FCodec.h: data compression codecs (FCodec / RLE / BWT / MTF /
Huffman / Full) plus the UCC .uz wrapper.

C++ return convention kept: every shipped Encode returns 0 (FALSE) and every
Decode returns 1 -- the flag distinguishes direction, not success.

The .uz wrapper and the UCC codec chain are not in the source drop (the
compress commandlet source is absent); they were derived empirically from
real UCC output and validated byte-for-byte on 13 files (see
tests/test_codec.py golden vectors).
"""

import struct
from functools import cmp_to_key
from typing import List, Tuple

from .bits import FBitReader, FBitWriter
from .system import FArchive, FArchiveMemoryReader, FBufferWriter


class FCodec:
    """Coder/decoder base class (FCodec.h:13-18)."""

    def encode(self, inp: FArchive, out: FArchive) -> bool:
        raise NotImplementedError

    def decode(self, inp: FArchive, out: FArchive) -> bool:
        raise NotImplementedError


class _FHuffman:
    """FHuffman node (FCodec.h:185-231)."""

    __slots__ = ("ch", "count", "child", "bits")

    def __init__(self, ch: int):
        self.ch = ch
        self.count = 0
        self.child: List["_FHuffman"] = []
        self.bits: List[int] = []

    def prepend_bit(self, bit: int) -> None:
        self.bits.insert(0, bit)
        for child in self.child:
            child.prepend_bit(bit)

    def write_table(self, writer: FBitWriter) -> None:
        # FCodec.h:206-217: 1 bit flag, then children or an 8-bit char.
        writer.write_bit(1 if self.child else 0)
        if self.child:
            for child in self.child:
                child.write_table(writer)
        else:
            writer.write(bytes([self.ch & 0xFF]))

    def read_table(self, reader: FBitReader) -> None:
        # FCodec.h:218-230.
        if reader.read_bit():
            self.child = [_FHuffman(-1), _FHuffman(-1)]
            for child in self.child:
                child.read_table(reader)
        else:
            self.ch = reader.serialize_byte(0)


class FCodecRLE(FCodec):
    """RLE compressor (FCodec.h:118-176)."""

    RLE_LEAD = 5

    def _emit_run(self, out: FArchive, char: int, count: int) -> bool:
        # EncodeEmitRun (FCodec.h:122-129): up to RLE_LEAD literal copies,
        # then the full count if the run was longer.
        for _ in range(min(count, self.RLE_LEAD)):
            out.serialize_byte(char)
        if count >= self.RLE_LEAD:
            out.serialize_byte(count)
        return True

    def encode(self, inp: FArchive, out: FArchive) -> bool:
        prev_char = 0
        prev_count = 0
        while not inp.at_end():
            b = inp.serialize_byte(0)
            if b != prev_char or prev_count == 255:
                self._emit_run(out, prev_char, prev_count)
                prev_char = b
                prev_count = 0
            prev_count += 1
        self._emit_run(out, prev_char, prev_count)
        return False

    def decode(self, inp: FArchive, out: FArchive) -> bool:
        count = 0
        prev_char = 0
        while not inp.at_end():
            b = inp.serialize_byte(0)
            out.serialize_byte(b)
            if b != prev_char:
                prev_char = b
                count = 1
            else:
                count += 1
                if count == self.RLE_LEAD:
                    c = inp.serialize_byte(0)
                    if c < 2:
                        raise ValueError("FCodecRLE: corrupt run length")
                    # `while C-->RLE_LEAD` (FCodec.h:168): test before
                    # decrement, so emit while c > RLE_LEAD.
                    while c > self.RLE_LEAD:
                        out.serialize_byte(b)
                        c -= 1
                    count = 0
        return True


class FCodecMTF(FCodec):
    """Move-to-front encoder (FCodec.h:327-374)."""

    def encode(self, inp: FArchive, out: FArchive) -> bool:
        lst = list(range(256))
        while not inp.at_end():
            b = inp.serialize_byte(0)
            i = lst.index(b)
            out.serialize_byte(i)
            # Shift List[i..1] down; List[0] = B (FCodec.h:347-349).
            while i > 0:
                lst[i] = lst[i - 1]
                i -= 1
            lst[0] = b
        return False

    def decode(self, inp: FArchive, out: FArchive) -> bool:
        lst = list(range(256))
        while not inp.at_end():
            b = inp.serialize_byte(0)
            c = lst[b]
            out.serialize_byte(c)
            while b > 0:
                lst[b] = lst[b - 1]
                b -= 1
            lst[0] = c
        return True


class FCodecBWT(FCodec):
    """Burrows-Wheeler inspired compressor (FCodec.h:24-112).

    appQsort is not a stable sort, but ClampedBufferCompare's `*P1-*P2`
    index tiebreak makes the order fully determined, so Python's sorted()
    matches (validated byte-for-byte against real UCC output)."""

    MAX_BUFFER_SIZE = 0x40000  # Hand tuning suggests this is ideal (FCodec.h:27)

    @staticmethod
    def _clamped_compare(buf: bytes, length: int, p1: int, p2: int) -> int:
        # ClampedBufferCompare (FCodec.h:30-44): compare the overlapping
        # suffix windows, tie by ascending position.
        count = length - max(p1, p2)
        b1 = p1
        b2 = p2
        while count > 0:
            if buf[b1] != buf[b2]:
                return -1 if buf[b1] < buf[b2] else 1
            b1 += 1
            b2 += 1
            count -= 1
        return p1 - p2

    def encode(self, inp: FArchive, out: FArchive) -> bool:
        remaining = inp.total_size() - inp.tell()
        while remaining > 0:
            length = min(remaining, self.MAX_BUFFER_SIZE)
            buf = inp.read(length)
            remaining -= length
            order = sorted(
                range(length + 1),
                key=cmp_to_key(
                    lambda a, b, buf=buf, ln=length: self._clamped_compare(
                        buf, ln, a, b
                    )
                ),
            )
            first = 0
            last = 0
            for i, p in enumerate(order):
                if p == 1:
                    first = i
                elif p == 0:
                    last = i
            out.serialize_int32(length)
            out.serialize_int32(first)
            out.serialize_int32(last)
            serialize_byte = out.serialize_byte
            for p in order:
                serialize_byte(buf[p - 1] if p else buf[0])
        return False

    def decode(self, inp: FArchive, out: FArchive) -> bool:
        while not inp.at_end():
            length = inp.serialize_int32(0)
            first = inp.serialize_int32(0)
            last = inp.serialize_int32(0)
            if length > self.MAX_BUFFER_SIZE:
                raise ValueError("FCodecBWT: block too large")
            length += 1
            seq = inp.read(length)
            # Reconstruct via per-symbol count and run tables
            # (FCodec.h:88-105); index 256 stands for the virtual EOF
            # position Last.
            counts = [0] * 257
            for k in range(length):
                counts[256 if k == last else seq[k]] += 1
            run = [0] * 257
            total = 0
            for k in range(257):
                run[k] = total
                total += counts[k]
                counts[k] = 0
            temp = [0] * length
            for k in range(length):
                index = 256 if k == last else seq[k]
                temp[run[index] + counts[index]] = k
                counts[index] += 1
            pos = first
            for _ in range(length - 1):
                out.serialize_byte(seq[pos])
                pos = temp[pos]
        return True


class FCodecHuffman(FCodec):
    """Huffman codec (FCodec.h:182-321)."""

    def encode(self, inp: FArchive, out: FArchive) -> bool:
        saved_pos = inp.tell()
        total = 0

        # Compute character frequencies (FCodec.h:243-250).
        huff = [_FHuffman(i) for i in range(256)]
        index = list(huff)
        while not inp.at_end():
            huff[inp.serialize_byte(0)].count += 1
            total += 1
        inp.seek(saved_pos)
        out.serialize_int32(total)

        # Build compression table (FCodec.h:253-274): pop trailing
        # zero-count symbols, repeatedly merge the two most frequent (the
        # list is kept sorted descending, popped from the end), inserting
        # each new node before the first strictly-less-frequent one.
        while len(huff) > 1 and huff[-1].count == 0:
            huff.pop()
        bit_count = len(huff) * 9  # 8-bit char + internal flag per leaf.
        while len(huff) > 1:
            node = _FHuffman(-1)
            node.child = [None, None]  # type: ignore[list-item]
            for k in range(2):
                child = huff.pop()
                node.child[k] = child
                child.prepend_bit(k)
                node.count += child.count
            ins = 0
            while ins < len(huff) and not huff[ins].count < node.count:
                ins += 1
            huff.insert(ins, node)
            bit_count += 1  # One table flag bit per merge.
        root = huff.pop()

        # Calc stats (FCodec.h:277-279).
        while not inp.at_end():
            bit_count += len(index[inp.serialize_byte(0)].bits)
        inp.seek(saved_pos)

        # Save table and bitstream (FCodec.h:282-292).
        writer = FBitWriter(bit_count)
        root.write_table(writer)
        while not inp.at_end():
            for bit in index[inp.serialize_byte(0)].bits:
                writer.write_bit(bit)
        if writer.is_error() or writer.get_num_bits() != bit_count:
            raise ValueError(
                f"FCodecHuffman: bit count mismatch "
                f"{writer.get_num_bits()} != {bit_count}"
            )
        out.serialize_bytes(writer.get_data()[: writer.get_num_bytes()])
        return False

    def decode(self, inp: FArchive, out: FArchive) -> bool:
        total = inp.serialize_int32(0)
        payload = inp.read(inp.total_size() - inp.tell())
        reader = FBitReader(payload, len(payload) * 8)
        root = _FHuffman(-1)
        root.read_table(reader)
        while total > 0:
            total -= 1
            if reader.at_end():
                raise ValueError("FCodecHuffman: truncated stream")
            node = root
            while node.ch == -1:
                node = node.child[reader.read_bit()]
            out.serialize_byte(node.ch)
        return True


class FCodecFull(FCodec):
    """General compressor codec (FCodec.h:380-436)."""

    def __init__(self):
        self._codecs: List[FCodec] = []

    def add_codec(self, codec: FCodec) -> None:
        self._codecs.append(codec)

    def _code(
        self, inp: FArchive, out: FArchive, step: int, first: int, func: str
    ) -> None:
        # FCodecFull::Code (FCodec.h:384-407): chain the codecs through
        # buffer archives, walking forward for Encode and backward for
        # Decode. Gap: the appSeconds/GWarn per-stage timing and logging
        # are omitted (GWarn/appSeconds unported); diagnostics only, they
        # do not affect the data.
        codec_count = len(self._codecs)
        in_data = None
        out_data = bytearray()
        for i in range(codec_count):
            last = i == codec_count - 1
            src = inp if i == 0 else FArchiveMemoryReader(bytes(in_data))
            dst = out if last else FBufferWriter(out_data)
            getattr(self._codecs[first + step * i], func)(src, dst)
            if not last:
                in_data = bytes(out_data)
                out_data = bytearray()

    def encode(self, inp: FArchive, out: FArchive) -> bool:
        self._code(inp, out, 1, 0, "encode")
        return False

    def decode(self, inp: FArchive, out: FArchive) -> bool:
        self._code(inp, out, -1, len(self._codecs) - 1, "decode")
        return True


# The UCC compress commandlet's chain and .uz wrapper, derived empirically
# from real UCC output (4 "stage" logs) -- NOT Setup's 5-codec chain
# (USetupDefinition.cpp:647-652, magic 5678).
UZ_SIGNATURE = 1234


def _uz_codec() -> FCodecFull:
    codec = FCodecFull()
    codec.add_codec(FCodecRLE())
    codec.add_codec(FCodecBWT())
    codec.add_codec(FCodecMTF())
    codec.add_codec(FCodecHuffman())
    return codec


def compress_uz(data: bytes, name: str) -> bytes:
    """Build a UCC .uz blob: INT Signature(1234) + size-prefixed
    NUL-terminated name (BYTE length incl. NUL, chars, NUL; the package
    FString layout, Help/PACKAGES.md) + FCodecFull stream."""
    out = bytearray(struct.pack("<i", UZ_SIGNATURE))
    encoded = name.encode("latin-1")
    out.append(len(encoded) + 1)
    out += encoded
    out.append(0)
    stream = bytearray()
    _uz_codec().encode(FArchiveMemoryReader(data), FBufferWriter(stream))
    out += stream
    return bytes(out)


def decompress_uz(blob: bytes) -> Tuple[str, bytes]:
    """Inverse of compress_uz; returns (name, original data)."""
    signature = struct.unpack_from("<i", blob, 0)[0]
    if signature != UZ_SIGNATURE:
        raise ValueError(f"bad .uz signature {signature}")
    length = blob[4]
    name = blob[5 : 5 + length - 1].decode("latin-1")
    stream = bytearray()
    _uz_codec().decode(
        FArchiveMemoryReader(blob[4 + 1 + length :]), FBufferWriter(stream)
    )
    return name, bytes(stream)
