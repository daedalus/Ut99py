"""FRiffChunk: four-character codes and the RIFF chunk framing.

Expected values come from FRiffChunk.h: appFourCC packs Ch[0..3] into a DWORD
little-endian (padding short codes with spaces, FRiffChunk.h:14-24), and
Save/Load frame each chunk as FourCC (DWORD), Size (INT), then the body
(FRiffChunk.h:57-98).
"""

import struct

import pytest

from ut99py.core.riff import (
    FRiffChunk,
    FRiffChunk_WAVE,
    FRiffChunk_data,
    FRiffChunk_fmt,
    app_four_cc,
    load_riff_file,
    save_riff_file,
)

# "RIFF" = 'R' | 'I'<<8 | 'F'<<16 | 'F'<<24.
RIFF = 0x46464952
WAVE = 0x45564157
FMT = 0x20746D66  # "fmt" padded with a space
DATA = 0x61746164


def test_app_four_cc_packs_little_endian():
    assert app_four_cc("RIFF") == RIFF
    assert app_four_cc("WAVE") == WAVE
    assert app_four_cc("data") == DATA


def test_app_four_cc_pads_short_codes_with_spaces():
    assert app_four_cc("fmt") == FMT
    assert app_four_cc("fmt ") == FMT


def test_app_four_cc_ignores_null_and_extra_characters():
    assert app_four_cc(None) == 0
    assert app_four_cc("") == 0
    assert app_four_cc("ABCDE") == app_four_cc("ABCD")


def _build_wave() -> FRiffChunk_WAVE:
    wave = FRiffChunk_WAVE()
    fmt = FRiffChunk_fmt()
    fmt.w_format_tag = 1
    fmt.n_channels = 2
    fmt.n_samples_per_sec = 44100
    fmt.n_avg_bytes_per_sec = 176400
    fmt.n_block_align = 4
    fmt.n_bits_per_sample = 16
    data = FRiffChunk_data()
    data.bits = bytes([1, 2, 3, 4])
    wave.sub_chunks.extend([fmt, data])
    return wave


def test_save_writes_the_riff_framing(tmp_path):
    out = tmp_path / "test.wav"
    save_riff_file(_build_wave(), str(out))

    fmt_body = struct.pack("<HHIIHH", 1, 2, 44100, 176400, 4, 16)
    expected = (
        struct.pack("<I", RIFF)
        + struct.pack("<i", 40)  # "WAVE" (4) + fmt (24) + data (12)
        + struct.pack("<I", WAVE)
        + struct.pack("<I", FMT)
        + struct.pack("<i", 16)
        + fmt_body
        + struct.pack("<I", DATA)
        + struct.pack("<i", 4)
        + bytes([1, 2, 3, 4])
    )
    assert out.read_bytes() == expected


def test_wave_round_trips(tmp_path):
    out = tmp_path / "roundtrip.wav"
    save_riff_file(_build_wave(), str(out))

    loaded = load_riff_file(FRiffChunk_WAVE(), str(out))

    assert loaded.file_type == WAVE
    assert len(loaded.sub_chunks) == 2
    fmt, data = loaded.sub_chunks
    assert isinstance(fmt, FRiffChunk_fmt)
    assert (
        fmt.w_format_tag,
        fmt.n_channels,
        fmt.n_samples_per_sec,
        fmt.n_avg_bytes_per_sec,
        fmt.n_block_align,
        fmt.n_bits_per_sample,
    ) == (1, 2, 44100, 176400, 4, 16)
    assert isinstance(data, FRiffChunk_data)
    assert data.bits == bytes([1, 2, 3, 4])


def test_unknown_sub_chunk_round_trips_as_an_empty_body(tmp_path):
    # FRiffChunk::Save calls SerializeChunk with size 0 (FRiffChunk.h:89), so a
    # base chunk has no body to preserve.
    wave = FRiffChunk_WAVE()
    wave.sub_chunks.append(FRiffChunk(app_four_cc("xtra")))
    out = tmp_path / "unknown.wav"
    save_riff_file(wave, str(out))

    loaded = load_riff_file(FRiffChunk_WAVE(), str(out))

    assert len(loaded.sub_chunks) == 1
    assert loaded.sub_chunks[0].four_cc == app_four_cc("xtra")
    assert loaded.sub_chunks[0].unknown == b""


def test_load_rejects_a_mismatched_root_code(tmp_path):
    out = tmp_path / "notriff.bin"
    out.write_bytes(
        struct.pack("<i", app_four_cc("AVI "))
        + struct.pack("<i", 4)
        + struct.pack("<I", WAVE)
    )
    with pytest.raises(ValueError):
        load_riff_file(FRiffChunk_WAVE(), str(out))


def test_wave_root_rejects_a_mismatched_file_type(tmp_path):
    # A WAVE root read from a non-WAVE RIFF body fails the
    # `check(FileType==ExpectedRiffFileType)` at FRiffChunk.h:115.
    out = tmp_path / "wrongtype.wav"
    out.write_bytes(
        struct.pack("<I", RIFF)
        + struct.pack("<i", 4)
        + struct.pack("<I", app_four_cc("AVI "))
    )
    with pytest.raises(ValueError):
        load_riff_file(FRiffChunk_WAVE(), str(out))
