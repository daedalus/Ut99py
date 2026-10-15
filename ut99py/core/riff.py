"""Port of Core/Inc/FRiffChunk.h (RIFF / WAVE chunk management).

The whole header is inline except the file-level helpers: `appStrlen`
(UnFile.h:293), `appLoadFileToArray` (UnFile.h:415) and the `FFileManager`
bodies live in the prebuilt Core.lib, so `load_riff_file`/`save_riff_file` use
the port's `FArchiveMemoryReader`/`FArchiveFileWriter` directly.  `FBufferReader`
(UnTemplate.h:1534) is `FArchiveMemoryReader` here.

`Ar << X` selects the DWORD/INT/_WORD operator by the operand's static type in
C++; Python has no static type, so the tagged reads/writes call
`serialize_dword`/`serialize_int32`/`serialize_word` explicitly.

Source line numbers refer to Core/Inc/FRiffChunk.h.
"""

from typing import List, Optional

from .system import (
    FArchive,
    FArchiveFileWriter,
    FArchiveMemoryReader,
)

__all__ = [
    "app_four_cc",
    "FRiffChunk",
    "FRiffChunk_RIFF",
    "FRiffChunk_fmt",
    "FRiffChunk_data",
    "FRiffChunk_WAVE",
    "load_riff_file",
    "save_riff_file",
]

# sizeof(INT): the RIFF chunk-size field (FRiffChunk.h:93).
SIZE_FIELD_BYTES = 4

# The pad byte appFourCC substitutes for missing characters (space, 32).
_FOUR_CC_PAD = 0x20


def app_four_cc(ch: Optional[str]) -> int:
    """appFourCC (FRiffChunk.h:14): pack up to four characters into a DWORD.

    Characters past the fourth are ignored and a short string is padded with
    spaces, so ``"fmt"`` and ``"fmt "`` yield the same code.
    """
    if not ch:
        return 0
    length = len(ch)
    result = 0
    for i in range(4):
        byte = ord(ch[i]) if i < length else _FOUR_CC_PAD
        result |= (byte & 0xFF) << (8 * i)
    return result


class FRiffChunk:
    """FRiffChunk (FRiffChunk.h:31): base RIFF chunk."""

    def __init__(self, in_four_cc: int):
        self.four_cc: int = in_four_cc
        self.unknown: bytes = b""
        self.sub_chunks: List["FRiffChunk"] = []

    def serialize_chunk(self, ar: FArchive, size: int) -> None:
        """FRiffChunk::SerializeChunk (FRiffChunk.h:43): raw `size` bytes.

        The C++ keeps the payload in `Unknown`; on save it is called with
        ``size`` 0 (FRiffChunk.h:89) so an unknown chunk writes no body.
        """
        if ar.is_loading():
            self.unknown = ar.read(size)
        else:
            ar.write(self.unknown[:size])

    def create_sub_chunk(self, four_cc: int) -> Optional["FRiffChunk"]:
        """FRiffChunk::CreateSubChunk (FRiffChunk.h:51)."""
        return FRiffChunk(four_cc)

    def load(self, ar: FArchive, size: int) -> None:
        """FRiffChunk::Load (FRiffChunk.h:57)."""
        data_pos = ar.tell()
        self.serialize_chunk(ar, size)
        # Bytes of the chunk body left after SerializeChunk (FRiffChunk.h:65).
        remaining = size - (ar.tell() - data_pos)
        sub_ar = FArchiveMemoryReader(ar.read(remaining))
        while not sub_ar.at_end():
            sub_four_cc = sub_ar.serialize_dword(0)
            sub_size = sub_ar.serialize_int32(0)
            sub_start = sub_ar.tell()
            sub_chunk = self.create_sub_chunk(sub_four_cc)
            if sub_chunk is not None:
                self.sub_chunks.append(sub_chunk)
                sub_chunk.load(sub_ar, sub_size)
            sub_ar.seek(sub_start + sub_size)

    def save(self, ar: FArchive) -> None:
        """FRiffChunk::Save (FRiffChunk.h:83): FourCC, a size placeholder, the
        body and sub-chunks, then the size patched in place."""
        ar.serialize_dword(self.four_cc)
        start_pos = ar.tell()
        ar.serialize_int32(0)
        self.serialize_chunk(ar, 0)
        for sub in self.sub_chunks:
            sub.save(ar)
        end_pos = ar.tell()
        ar.seek(start_pos)
        ar.serialize_int32(end_pos - start_pos - SIZE_FIELD_BYTES)
        ar.seek(end_pos)


class FRiffChunk_RIFF(FRiffChunk):
    """FRiffChunk_RIFF (FRiffChunk.h:105): root of a RIFF file."""

    def __init__(self, in_file_type: int):
        super().__init__(app_four_cc("RIFF"))
        self.file_type: int = in_file_type

    def serialize_chunk(self, ar: FArchive, size: int) -> None:
        """FRiffChunk_RIFF::SerializeChunk (FRiffChunk.h:111): read/write the
        file-type DWORD and reject a mismatched one (`check` in the C++)."""
        expected = self.file_type
        self.file_type = ar.serialize_dword(self.file_type)
        if self.file_type != expected:
            raise ValueError(
                f"RIFF file type mismatch: expected {expected:#x}, "
                f"got {self.file_type:#x}"
            )


class FRiffChunk_fmt(FRiffChunk):
    """FRiffChunk_fmt (FRiffChunk.h:125): the WAVE `fmt ` chunk."""

    def __init__(self):
        super().__init__(app_four_cc("fmt"))
        self.w_format_tag: int = 0
        self.n_channels: int = 0
        self.n_samples_per_sec: int = 0
        self.n_avg_bytes_per_sec: int = 0
        self.n_block_align: int = 0
        self.n_bits_per_sample: int = 0

    def serialize_chunk(self, ar: FArchive, size: int) -> None:
        """FRiffChunk_fmt::SerializeChunk (FRiffChunk.h:130): the WAVEFORMATEX
        fields in declaration order (the C++ `debugf` diagnostics are dropped)."""
        self.w_format_tag = ar.serialize_word(self.w_format_tag)
        self.n_channels = ar.serialize_word(self.n_channels)
        self.n_samples_per_sec = ar.serialize_int32(self.n_samples_per_sec)
        self.n_avg_bytes_per_sec = ar.serialize_int32(self.n_avg_bytes_per_sec)
        self.n_block_align = ar.serialize_word(self.n_block_align)
        self.n_bits_per_sample = ar.serialize_word(self.n_bits_per_sample)


class FRiffChunk_data(FRiffChunk):
    """FRiffChunk_data (FRiffChunk.h:149): the WAVE `data` chunk."""

    def __init__(self):
        super().__init__(app_four_cc("data"))
        self.bits: bytes = b""

    def serialize_chunk(self, ar: FArchive, size: int) -> None:
        """FRiffChunk_data::SerializeChunk (FRiffChunk.h:154): on load read
        `size` bytes, on save write every stored byte."""
        if ar.is_loading():
            self.bits = ar.read(size)
        else:
            ar.write(self.bits)


class FRiffChunk_WAVE(FRiffChunk_RIFF):
    """FRiffChunk_WAVE (FRiffChunk.h:164): a WAVE file's root chunk."""

    def __init__(self):
        super().__init__(app_four_cc("WAVE"))

    def serialize_chunk(self, ar: FArchive, size: int) -> None:
        """FRiffChunk_WAVE::SerializeChunk (FRiffChunk.h:169)."""
        FRiffChunk_RIFF.serialize_chunk(self, ar, size)

    def create_sub_chunk(self, four_cc: int) -> Optional[FRiffChunk]:
        """FRiffChunk_WAVE::CreateSubChunk (FRiffChunk.h:173)."""
        if four_cc == app_four_cc("fmt"):
            return FRiffChunk_fmt()
        if four_cc == app_four_cc("data"):
            return FRiffChunk_data()
        return FRiffChunk(four_cc)


def load_riff_file(root: FRiffChunk, filename: str) -> FRiffChunk:
    """LoadRiffFile (FRiffChunk.h:185): read the file, verify the root FourCC,
    then load the root chunk.

    The C++ is a template that instantiated `T` and read through
    `appLoadFileToArray`/`FFileManager`; neither is ported, so the caller
    supplies the root chunk and the file is read directly.
    """
    with open(filename, "rb") as handle:
        data = handle.read()
    sub_ar = FArchiveMemoryReader(data)
    riff_four_cc = sub_ar.serialize_dword(0)
    if riff_four_cc != root.four_cc:
        raise ValueError(f"not a {root.four_cc:#x} RIFF file: got {riff_four_cc:#x}")
    size = sub_ar.serialize_int32(0)
    root.load(sub_ar, size)
    return root


def save_riff_file(root: FRiffChunk, filename: str) -> bool:
    """SaveRiffFile (FRiffChunk.h:206): write the chunk tree to `filename`.

    The C++ routes through `FFileManager->CreateFileWriter`; the port uses
    `FArchiveFileWriter` and returns True once the file is closed.
    """
    ar = FArchiveFileWriter(filename)
    try:
        root.save(ar)
    finally:
        ar.close()
    return True
