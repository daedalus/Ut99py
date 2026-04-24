"""Audio package - Sound playback and mixing

Ported from Ut99PubSrc/Audio/
- UAudioSubsystem: Base audio subsystem
- USound: Sound data
- Voice: Audio voice/channel
- Audio mixing
"""

from typing import TYPE_CHECKING, Optional, ClassVar
from enum import IntEnum

from ..core import (
    UObject, UClass,
    FVector, FName, FString, TArray,
    RF_NoFlags,
)

if TYPE_CHECKING:
    from ..engine import AActor


class EAudioFlags(IntEnum):
    AUDIO_MONO = 0
    AUDIO_STEREO = 1
    AUDIO_8BIT = 0
    AUDIO_16BIT = 2
    AUDIO_SHOLD = 0
    AUDIO_COSINE = 4
    AUDIO_2DAUDIO = 0
    AUDIO_3DAUDIO = 8


class EVoiceFlags(IntEnum):
    VOICE_AUTO = 0
    VOICE_DISABLED = 0
    VOICE_ENABLED = 1
    VOICE_ACTIVE = 2
    VOICE_FINISHED = 4


AUDIO_TOTALCHANNELS = 32
AUDIO_TOTALVOICES = 256
AUDIO_MINPAN = 0
AUDIO_MIDPAN = 16384
AUDIO_MAXPAN = 32767
AUDIO_MINVOLUME = 0
AUDIO_MAXVOLUME = 256


class AudioVector:
    __slots__ = ('x', 'y', 'z', 'w')
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w


class MemChunk:
    __slots__ = ('data', 'data_length', 'position')
    
    def __init__(self):
        self.data: bytes = b''
        self.data_length: int = 0
        self.position: int = 0


class Sample:
    __slots__ = ('size', 'panning', 'volume', 'type', 'length', 'loop_start', 'loop_end', 'samples_per_sec')
    
    def __init__(self):
        self.size: int = 0
        self.panning: int = AUDIO_MIDPAN
        self.volume: int = AUDIO_MAXVOLUME
        self.type: int = 0
        self.length: int = 0
        self.loop_start: int = 0
        self.loop_end: int = 0
        self.samples_per_sec: int = 22050


class Voice:
    __slots__ = ('sample', 'base_volume', 'volume', 'pan', 'pitch', 'sample_position', 'voice_number', 'source', 'flags')
    
    def __init__(self):
        self.sample: Optional[Sample] = None
        self.base_volume: int = AUDIO_MAXVOLUME
        self.volume: int = 0
        self.pan: int = AUDIO_MIDPAN
        self.pitch: float = 1.0
        self.sample_position: int = 0
        self.voice_number: int = 0
        self.source: Optional[AActor] = None
        self.flags: int = EVoiceFlags.VOICE_AUTO


class FPlayingSound:
    __slots__ = ('channel', 'actor', 'id', 'is_3d', 'sound', 'location', 'volume', 'radius', 'pitch', 'priority')
    
    def __init__(self):
        self.channel: Optional[Voice] = None
        self.actor: Optional[AActor] = None
        self.id: int = 0
        self.is_3d: bool = False
        self.sound: Optional['USound'] = None
        self.location = FVector()
        self.volume: float = 0.0
        self.radius: float = 0.0
        self.pitch: float = 1.0
        self.priority: float = 0.0


class USound(UObject):
    _sounds: ClassVar[TArray['USound']] = TArray()
    
    def __init__(self):
        super().__init__()
        self._data: bytes = b''
        self._format: int = 0
        self._size: int = 0
        self._duration: float = 0.0
        self._sample_rate: int = 22050
    
    @property
    def data(self) -> bytes:
        return self._data
    
    @property
    def duration(self) -> float:
        return self._duration
    
    @property
    def sample_rate(self) -> int:
        return self._sample_rate
    
    def __repr__(self) -> str:
        return f"<USound {self.get_full_name()} duration={self._duration:.2f}>"


class UAudioSubsystem(UObject):
    _audio_subsystems: ClassVar[TArray['UAudioSubsystem']] = TArray()
    
    def __init__(self):
        super().__init__()
        self._use_filter: bool = True
        self._use_surround: bool = False
        self._use_stereo: bool = True
        self._use_cd_music: bool = True
        self._use_digital_music: bool = True
        self._reverse_stereo: bool = False
        self._initialized: bool = False
        self._ambient_factor: float = 1.0
        self._doppler_speed: float = 1.0
        self._latency: int = 50
        self._channels: int = AUDIO_TOTALCHANNELS
        self._output_rate: int = 22050
        self._music_volume: int = 128
        self._sound_volume: int = 200
    
    def init(self) -> bool:
        return True
    
    def shutdown(self) -> None:
        pass
    
    def set_master_volume(self, volume: int) -> None:
        self._sound_volume = volume
    
    def set_music_volume(self, volume: int) -> None:
        self._music_volume = volume
    
    def play_sound(self, actor: 'AActor', id: int, sound: USound, location: FVector, volume: float, radius: float, pitch: float, priority: float = 0.0) -> FPlayingSound:
        return FPlayingSound()
    
    def stop_sound(self, sound: FPlayingSound) -> None:
        pass
    
    def pause_sound(self, sound: FPlayingSound, paused: bool) -> None:
        pass
    
    def get_duration(self, sound: USound) -> float:
        return sound.duration
    
    def play_music(self, song: USound, offset: int = 0) -> None:
        pass
    
    def stop_music(self) -> None:
        pass
    
    def is_music_playing(self) -> bool:
        return False


class UMusic(UObject):
    def __init__(self):
        super().__init__()
        self._data: bytes = b''
        self._title: str = ""
        self._artist: str = ""
        self._album: str = ""
        self._duration: float = 0.0


class AudioLibrary:
    def __init__(self):
        self._sounds: Optional[TArray[USound]] = None
    
    def load(self, filename: str) -> bool:
        return False
    
    def free(self) -> None:
        pass


class UAudioDevice(UObject):
    def __init__(self):
        super().__init__()
        self._audio_subsystem: Optional[UAudioSubsystem] = None
        self._max_voices: int = AUDIO_TOTALVOICES
    
    def init(self) -> bool:
        return True
    
    def update(self, delta_time: float) -> None:
        pass
    
    def get_audio_subsystem(self) -> Optional[UAudioSubsystem]:
        return self._audio_subsystem