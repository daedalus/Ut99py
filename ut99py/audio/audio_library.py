"""Port of Audio/Inc/AudioLibrary.h (audio management functions).

Globals: AudioBuffer, MixBuffer, BufferSize, AudioFormat, AudioRate,
         AudioInitialized, AudioPaused, MusicVoices, SampleVoices,
         Voices[AUDIO_TOTALVOICES], SampleVolume, MixingThread, Mutex.
"""

from __future__ import annotations


class AudioLibrary:
    """Unreal audio library globals and interface."""

    AudioBuffer: bytes | None = None
    MixBuffer: bytes | None = None
    BufferSize: int = 0
    AudioFormat: int = 0
    AudioRate: int = 0
    AudioInitialized: int = 0
    AudioPaused: int = 0
    MusicVoices: int = 0
    SampleVoices: int = 0
    Voices: list = []
    SampleVolume: int = 100
    MixingThread: object | None = None
    Mutex: object | None = None
