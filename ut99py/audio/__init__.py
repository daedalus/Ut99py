"""Port of Audio/Inc/Audio.h (Unreal audio public header file).
Includes AudioLibrary, AudioMixer, AudioCore, AudioSubsystem, FormatWAV.
"""
from __future__ import annotations

# Audio module aggregates audio-related headers.
# Source: Audio/Inc/Audio.h

# Minimal stubs; sound playback is not implemented in this port.
class USound:
    pass


class UAudioSubsystem:
    pass


Voice = None
Sample = None
FPlayingSound = None