"""Port of Audio/Inc/AudioSubsystem.h (audio subsystem)."""

from __future__ import annotations


class AudioSubsystem:
    """Audio subsystem management."""

    @staticmethod
    def InitAudio() -> None:
        pass

    @staticmethod
    def ShutdownAudio() -> None:
        pass

    @staticmethod
    def SetMusicVolume(volume: int) -> None:
        pass

    @staticmethod
    def SetSampleVolume(volume: int) -> None:
        pass

    @staticmethod
    def PauseAudio(pause: bool) -> None:
        pass