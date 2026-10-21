"""Port of Audio/Inc/AudioNative.h (native audio functions).

Includes AudioTypes.h and AudioSubsystem.h.
Defines AUTO_INITIALIZE_REGISTRANTS_AUDIO macro equivalent.
"""

from __future__ import annotations

from .audio_types import AudioTypes
from .audio_subsystem import AudioSubsystem


def AUTO_INITIALIZE_REGISTRANTS_AUDIO() -> None:
    AudioSubsystem.InitAudio()