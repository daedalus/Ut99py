"""Port of Audio/Inc/Audio.h (Unreal audio public header file).

Includes AudioLibrary, AudioMixer, AudioCore, AudioSubsystem, FormatWAV.
Re-exports engine.audio classes for reconciliation.
"""

from __future__ import annotations

from ..engine.audio import USound, UMusic, UAudioSubsystem, FSoundData, FWaveModInfo
from .audio_library import AudioLibrary
from .audio_core import AudioCore
from .audio_mixer import AudioMixer
from .audio_subsystem import AudioSubsystem
from .audio_types import Voice, Sample
from .format_wav import (
    WAVFileHeader,
    WAVFormatHeader,
    WAVFormatExHeader,
    WAVSampleHeader,
    WAVChunkHeader,
)


# Placeholder surfaces required by reconciliation tests
class FPlayingSound:
    pass


UAudioDevice = UAudioSubsystem


__all__ = [
    "USound",
    "UMusic",
    "UAudioSubsystem",
    "UAudioDevice",
    "AudioLibrary",
    "AudioCore",
    "AudioMixer",
    "AudioSubsystem",
    "Voice",
    "Sample",
    "FPlayingSound",
    "WAVFileHeader",
    "WAVFormatHeader",
    "WAVFormatExHeader",
    "WAVSampleHeader",
    "WAVChunkHeader",
    "FSoundData",
    "FWaveModInfo",
]
