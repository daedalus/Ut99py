"""Port of Audio/Inc/FormatWAV.h (WAV file format).

Structs: WAVFileHeader, WAVFormatHeader, WAVFormatExHeader,
         WAVSampleHeader, WAVChunkHeader.
"""

from __future__ import annotations


class WAVFileHeader:
    def __init__(self) -> None:
        self.ID: bytes = b""
        self.Size: int = 0
        self.Type: bytes = b""


class WAVFormatHeader:
    def __init__(self) -> None:
        self.Format: int = 0
        self.Channels: int = 0
        self.SamplesPerSec: int = 0
        self.BytesPerSec: int = 0
        self.BlockAlign: int = 0
        self.BitsPerSample: int = 0


class WAVFormatExHeader:
    def __init__(self) -> None:
        self.Size: int = 0
        self.SamplesPerBlock: int = 0


class WAVSampleHeader:
    class Loop:
        def __init__(self) -> None:
            self.Identifier: int = 0
            self.Type: int = 0
            self.Start: int = 0
            self.End: int = 0
            self.Fraction: int = 0
            self.Count: int = 0

    def __init__(self) -> None:
        self.Manufacturer: int = 0
        self.Product: int = 0
        self.SamplePeriod: int = 0
        self.Note: int = 0
        self.FineTune: int = 0
        self.SMPTEFormat: int = 0
        self.SMPTEOffset: int = 0
        self.Loops: int = 0
        self.SamplerData: int = 0
        self.Loop: list[WAVSampleHeader.Loop] = []


class WAVChunkHeader:
    def __init__(self) -> None:
        self.ID: bytes = b""
        self.Size: int = 0