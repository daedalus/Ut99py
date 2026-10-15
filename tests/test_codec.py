"""Tests for core/codec.py (FCodec.h) and the UCC .uz wrapper.

GOLDEN VECTORS: hex blobs captured from a real UT99 install on 2026-10-15.
Provenance: `cd ~/Games/UnrealTournament/System && wine UCC.exe compress
zzg_<name>.bin` produced `zzg_<name>.bin.uz` for source file zzg_<name>.bin;
the .uz bytes are embedded here so tests stay deterministic without wine.
The real UCC confirmed the chain [RLE, BWT, MTF, Huffman] and magic 1234.
"""

import random

import pytest

from ut99py.core.codec import (
    FCodecBWT,
    FCodecFull,
    FCodecHuffman,
    FCodecMTF,
    FCodecRLE,
    UZ_SIGNATURE,
    compress_uz,
    decompress_uz,
)
from ut99py.core.system import FArchiveMemoryReader, FBufferWriter


def _run(codec, data, direction):
    """Pipe `data` through one codec; returns (input consumed, output)."""
    out = bytearray()
    src = FArchiveMemoryReader(data)
    dst = FBufferWriter(out)
    getattr(codec, direction)(src, dst)
    assert not src.is_error()
    return bytes(out)


def _roundtrip(codec, data):
    encoded = _run(codec, data, "encode")
    decoded = _run(codec, encoded, "decode")
    assert decoded == data
    return encoded


# Golden vectors from real UCC (see module docstring).
GOLDEN = {
    "abcd": (
        bytes(range(4)),
        bytes.fromhex(
            "d20400000d7a7a675f616263642e62696e00110000000b48200203008cc53f6e"
        ),
    ),
    "hello": (
        b"HELLO WORLD!",
        bytes.fromhex(
            "d20400000e7a7a675f68656c6c6f2e62696e00"
            "190000007f55a84c91ea8ad59c342d0a94a7152010f0ffffff95203142440810"
            "1f3c74e0b04143060c172c54a030414204080f1c3460e884c906087c0b1424407"
            "0c0e092208dc912a5ffffff8fc810214180fcf0d183c70e1d3970dcb05183c60c"
            "193160bc70d182c50a15295076c4481180d0af7ef1f39ed6c32219e5510b"
        ),
    ),
    "runs": (
        b"A" * 120 + b"B" * 30 + b"C",
        bytes.fromhex(
            "d20400000d7a7a675f72756e732e62696e00"
            "1a0000006f88d07f0c16284880e08081020406feffffffffff3f3b75e8cc911307"
            "ce1b376dd8ac519306cd193365c88c111306cc172f5db86cd19205cb152b55a84c"
            "911205ca13274d982c519204c911234588c2733781ffff03f1c143070e1b3464c0"
            "70c142050a13244480f0c041c3ffffffbf20407ef8e8c163878e1c386ed8a84163"
            "868c18305eb868c162858a14284e982841628488100100d49e3d7bc4f7259d45"
        ),
    ),
    "pat400": (
        bytes((i * 3) & 0xFF for i in range(400)),
        bytes.fromhex(
            "d20400000f7a7a675f7061743430302e62696e00"
            "9d01000001fc8b05db2cd9b562ed95ebe5c26d97ee6ad176cbf685026d94e83a7"
            "1f6c9f352a1b64a75a5483b65fa45836e9af49a31f7ccf9b261b74d7bd5a8bb66"
            "fd8201374c78bd78fbe57bc9905ba6bc62c41d33feb561eb8ddbd2a0b546edead"
            "075c76e71e09a23f7ba70f5c56b59b0daa27565c83a63b630608d11fb1a31f6c8"
            "7189105ba4789930dba4b94a945db27c7df8fae3b73c78edd1bb42841d325c20c"
            "00609fead50a905cb4e989402e566c85483662f5c8a01f33668d48163172cca807"
            "123442a41b20f1e8500f99628d58469478c4a827455a8ba62b528504d917a3b74"
            "eac1b31b36e5c0b921421521da0f9f8200fde2c1374f7eedd87be77ef9f0dba7bf"
            "7af4ddb37fe1c01b27be6edc7df3be74e8ad535f39f2ce997f0b146ac07005080c"
            "74c0e026485481620f1c8a0071fffc3749b27efcf7c4a948901310500284df7ff"
            "e78fe17f0edf3c3534f3cf3dfbfff1e7af0d8236fdf78efdd4b2fbc7e65aa29d3"
            "4d337182c926cd35c7fc79669a31db2c4387186ed840030c1e64ac31e38d33728"
            "4d1466db5c5f66d36dab0d9267bf7d86fdf4e3becde65a925cb2db37081c516fd"
            "f4c3da35d65bb7d20aab57a9aa4a75d554aca0b24a75d551bf9e9a6ad4564bd12"
            "28a2b565001850b29ab4c79e5942ca1b4525d75d1bd9b8e3a74d649df3efaebd7"
            "530fbd7b69aa4973cd346ca0b146bffdf2f58b2fdab6d15ebb965a68dd4a5451a"
            "28b26620491458a2b8ef8f1c41423b6588206115cb08001040e145698f0e1840c"
            "115aa8ac5964cf965186cc99e4cd935fbe9c39e4ce955492e4c9244c9058a2b46"
            "9a44f97528ad4a95cbd72ddb58b175cbe74d79dfbf7dcbc71dbada3471c3f76d0"
            "81c3879c3d73deb993279c3ef5ddb7cf0f3f00"
        ),
    ),
}


@pytest.mark.parametrize("name", sorted(GOLDEN))
def test_golden_encode_matches_real_ucc(name):
    data, uz = GOLDEN[name]
    assert compress_uz(data, f"zzg_{name}.bin") == uz


@pytest.mark.parametrize("name", sorted(GOLDEN))
def test_golden_decode_real_ucc(name):
    data, uz = GOLDEN[name]
    decoded_name, decoded = decompress_uz(uz)
    assert decoded_name == f"zzg_{name}.bin"
    assert decoded == data


def test_uz_signature():
    assert UZ_SIGNATURE == 1234  # Setup's chain uses 5678; UCC uses 1234.


def test_decompress_uz_bad_signature():
    with pytest.raises(ValueError):
        decompress_uz(b"\x00\x00\x00\x00")


def test_rle_short_runs_are_literal():
    # RLE_LEAD=5: runs shorter than 5 stay literal (FCodec.h:122-129).
    encoded = _roundtrip(FCodecRLE(), b"\x00\x00\x00\x01\x02\x02")
    assert encoded == b"\x00\x00\x00\x01\x02\x02"


def test_rle_long_run_emits_count():
    encoded = _roundtrip(FCodecRLE(), b"A" * 7)
    # min(7,5) copies + the count byte 7.
    assert encoded == b"A" * 5 + bytes([7])


def test_rle_run_of_255_flushes():
    # PrevCount==255 forces a flush (FCodec.h:138).
    encoded = _roundtrip(FCodecRLE(), b"X" * 300)
    assert len(encoded) < 300


def test_rle_roundtrip_sweep():
    rnd = random.Random(11)
    for _ in range(20):
        data = bytes(rnd.randrange(4) for _ in range(rnd.randrange(0, 300)))
        _roundtrip(FCodecRLE(), data)


def test_rle_empty():
    assert _roundtrip(FCodecRLE(), b"") == b""


def test_mtf_roundtrip_sweep():
    rnd = random.Random(13)
    for _ in range(10):
        data = bytes(rnd.randrange(256) for _ in range(rnd.randrange(0, 500)))
        _roundtrip(FCodecMTF(), data)


def test_mtf_encode_known_value():
    # MTF: index in the evolving 256-list, moved to front (FCodec.h:330-351).
    encoded = _roundtrip(FCodecMTF(), bytes([0, 1, 0, 2, 0]))
    # 0 -> front unchanged; 1 -> idx 1; 0 -> idx 1 (now behind 1);
    # 2 -> idx 2; 0 -> idx 1 again after 2 moved to front.
    assert encoded == bytes([0, 1, 1, 2, 1])


def test_bwt_roundtrip_sweep():
    rnd = random.Random(17)
    for _ in range(10):
        data = bytes(rnd.randrange(4) for _ in range(rnd.randrange(0, 400)))
        _roundtrip(FCodecBWT(), data)


def test_bwt_empty():
    assert _roundtrip(FCodecBWT(), b"") == b""


def test_bwt_multi_block():
    # Block size is a class attribute; shrink it to exercise the loop
    # without a 256KB fixture (real UCC output covers single-block only).
    class SmallBWT(FCodecBWT):
        MAX_BUFFER_SIZE = 16

    data = bytes((i * 7 + 1) & 0xFF for i in range(40))
    encoded = _roundtrip(SmallBWT(), data)
    # Two full blocks (16+16 bytes) plus a partial (8): three headers.
    assert encoded.count(bytes([16, 0, 0, 0])) >= 2


def test_bwt_emits_block_header():
    # Block format (FCodec.h:65-67): INT length, INT first, INT last,
    # then length+1 transformed bytes.
    data = b"banana"
    encoded = _run(FCodecBWT(), data, "encode")
    length = int.from_bytes(encoded[0:4], "little")
    assert length == len(data)
    assert len(encoded) == 12 + length + 1


def test_huffman_single_symbol():
    # One distinct symbol: the tree is a lone leaf; table = flag + char.
    _roundtrip(FCodecHuffman(), b"z" * 100)


def test_huffman_empty():
    # Empty input: Total=0, a lone-leaf table; decoding yields nothing.
    _roundtrip(FCodecHuffman(), b"")


def test_huffman_roundtrip_sweep():
    rnd = random.Random(19)
    for _ in range(10):
        data = bytes(rnd.randrange(8) for _ in range(rnd.randrange(1, 400)))
        _roundtrip(FCodecHuffman(), data)


def test_huffman_all_byte_values():
    data = bytes(range(256)) * 2
    _roundtrip(FCodecHuffman(), data)


def test_full_chain_roundtrip():
    # The UCC chain: RLE -> BWT -> MTF -> Huffman (FCodecFull walks it
    # forward for Encode, backward for Decode).
    codec = FCodecFull()
    for cls in (FCodecRLE, FCodecBWT, FCodecMTF, FCodecHuffman):
        codec.add_codec(cls())
    rnd = random.Random(23)
    data = bytes(rnd.randrange(4) for _ in range(600))
    out = bytearray()
    codec.encode(FArchiveMemoryReader(data), FBufferWriter(out))
    back = bytearray()
    codec.decode(FArchiveMemoryReader(bytes(out)), FBufferWriter(back))
    assert bytes(back) == data


def test_full_chain_preserves_source_fa_archive():
    # _code must not consume the caller's In when the first stage reads it.
    codec = FCodecFull()
    codec.add_codec(FCodecRLE())
    src = FArchiveMemoryReader(b"AAAABBBB")
    out = bytearray()
    codec.encode(src, FBufferWriter(out))
    assert src.tell() == 8


def test_compress_uz_layout():
    blob = compress_uz(b"hi", "f.bin")
    assert int.from_bytes(blob[0:4], "little") == UZ_SIGNATURE
    assert blob[4] == len("f.bin") + 1  # Length includes the NUL.
    assert blob[5 : 5 + 5] == b"f.bin"
    assert blob[10] == 0
    assert decompress_uz(blob) == ("f.bin", b"hi")


def test_compress_uz_scripted_random():
    rnd = random.Random(29)
    for size in (0, 1, 2, 151, 1000):
        data = bytes(rnd.randrange(256) for _ in range(size))
        blob = compress_uz(data, "zz.bin")
        assert decompress_uz(blob) == ("zz.bin", data)
