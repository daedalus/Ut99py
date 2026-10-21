"""Port of Audio/Inc/AudioTypes.h (Unreal general audio types).

Structs: AudioVector, MemChunk, Sample, Voice, VoiceStats, AudioThread, AudioMutex.
"""

from __future__ import annotations


class AudioVector:
    def __init__(self) -> None:
        self.X: float = 0.0
        self.Y: float = 0.0
        self.Z: float = 0.0
        self.W: float = 0.0


class MemChunk:
    def __init__(self) -> None:
        self.Data: bytes | None = None
        self.DataLength: int = 0
        self.Position: int = 0


class Sample:
    def __init__(self) -> None:
        self.Size: int = 0
        self.Panning: int = 0
        self.Volume: int = 0
        self.Type: int = 0
        self.Length: int = 0
        self.LoopStart: int = 0
        self.LoopEnd: int = 0
        self.SamplesPerSec: int = 0
        self.Data: bytes | None = None


class Voice:
    def __init__(self) -> None:
        self.State: int = 0
        self.pSample: Sample | None = None
        self.PlayPosition: int = 0
        self.StartTime: float = 0.0
        self.LastTime: float = 0.0
        self.StereoVoice: "Voice | None" = None
        self.Panning: int = 0
        self.BasePanning: int = 0
        self.Volume: int = 0


class VoiceStats:
    def __init__(self) -> None:
        self.CompletionString: str = ""
        self.Completion: float = 0.0


class AudioThread:
    def __init__(self) -> None:
        self.Thread: object | None = None
        self.Valid: int = 0
        self.Exited: int = 0


class AudioMutex:
    def __init__(self) -> None:
        self.Mutex: object | None = None