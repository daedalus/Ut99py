"""Port of Audio/Inc/AudioMixer.h (audio mixer).

Defines audio mixing functionality.
"""

from __future__ import annotations


class AudioMixer:
    """Audio mixer interface."""

    @staticmethod
    def Mix() -> None:
        pass

    @staticmethod
    def StopMixing() -> None:
        pass