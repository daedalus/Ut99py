"""Port of Audio/Inc/AudioCore.h (audio core).

Classes and structures for audio core initialization and management.
"""

from __future__ import annotations


class AudioCore:
    """Audio core subsystem definitions."""

    AUDIO_TOTALVOICES = 64

    @staticmethod
    def Init() -> None:
        pass

    @staticmethod
    def Shutdown() -> None:
        pass