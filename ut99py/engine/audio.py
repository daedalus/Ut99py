"""Port of Engine/Inc/UnAudio.h (10 declared symbols).

Audio objects of the Engine package: the abstract UAudioSubsystem
interface, USound/UMusic with their FSoundData/TLazyArray payloads, and
FWaveModInfo with the RIFF-WAVE header structs (FRiffWaveHeader,
FRiffChunkOld, FFormatChunk, FSampleChunk, FSampleLoop).

Inline bodies ported 1-to-1: USound ctor/GetDuration (UnAudio.h:88,95),
FSoundData ctor (:67), UMusic ctor (:129), MAKEFOURCC/mmioFOURCC
(:145-150), FWaveModInfo ctor (:233) and Pad16Bit (:240). Every declared
without a body (FSoundData Load/GetPeriod, USound/UMusic
Serialize/Destroy/PostLoad, FWaveModInfo ReadWaveInfo/UpdateWaveData/
reducers/filters) lives in the prebuilt Engine.lib -- Engine/Src is
absent from the source drop -- so they raise NotImplementedError.
"""

from typing import TYPE_CHECKING, ClassVar, Optional

from ..core import (
    FArchive,
    FName,
    FOutputDevice,
    FVector,
    FCoords,
    GLog,
    USubsystem,
    UObject,
)
from ..core.template import TLazyArray

if TYPE_CHECKING:
    from .camera import UViewport
    from .classes import AActor
    from .render_structs import FSceneNode
    from .un_obj import FPointRegion

# HAVE_VAG (UnAudio.h:18): the Sony VAG encoder includes are disabled.
HAVE_VAG = 0

_ENGINE_LIB = "Engine.lib (Engine/Src absent from the source drop)"


def make_four_cc(ch0: str, ch1: str, ch2: str, ch3: str) -> int:
    """MAKEFOURCC/mmioFOURCC (UnAudio.h:145-150): pack 4 bytes into a DWORD.

    Little-endian, matching the C++ macro's per-character byte shifts; the
    header notes it is not endian independent. Same packing as
    core.riff.app_four_cc for exact four-character input.
    """
    return (
        (ord(ch0) & 0xFF)
        | ((ord(ch1) & 0xFF) << 8)
        | ((ord(ch2) & 0xFF) << 16)
        | ((ord(ch3) & 0xFF) << 24)
    )


class UAudioSubsystem(USubsystem):
    """Abstract game audio backend (UnAudio.h:31).

    DECLARE_ABSTRACT_CLASS + NO_DEFAULT_CONSTRUCTOR: the C++ only ever
    instantiates a concrete subclass (the unported audio device), so the
    pure virtuals here raise like the other Engine.lib dispatch points.
    """

    def init(self) -> bool:
        """UAudioSubsystem::Init (UnAudio.h:37, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.init pure virtual")

    def set_viewport(self, viewport: "UViewport") -> None:
        """UAudioSubsystem::SetViewport (UnAudio.h:38, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.set_viewport pure virtual")

    def exec(self, cmd: str, ar: FOutputDevice = GLog) -> bool:
        """UAudioSubsystem::Exec (UnAudio.h:39, pure virtual; Ar defaults to GLog)."""
        raise NotImplementedError("UAudioSubsystem.exec pure virtual")

    def update(self, region: "FPointRegion", listener: FCoords) -> None:
        """UAudioSubsystem::Update (UnAudio.h:40, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.update pure virtual")

    def register_music(self, music: "UMusic") -> None:
        """UAudioSubsystem::RegisterMusic (UnAudio.h:41, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.register_music pure virtual")

    def register_sound(self, sound: "USound") -> None:
        """UAudioSubsystem::RegisterSound (UnAudio.h:42, pure virtual).

        The header spells the parameter ``Music`` but types it USound*.
        """
        raise NotImplementedError("UAudioSubsystem.register_sound pure virtual")

    def unregister_sound(self, sound: "USound") -> None:
        """UAudioSubsystem::UnregisterSound (UnAudio.h:43, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.unregister_sound pure virtual")

    def unregister_music(self, music: "UMusic") -> None:
        """UAudioSubsystem::UnregisterMusic (UnAudio.h:44, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.unregister_music pure virtual")

    def play_sound(
        self,
        actor: "AActor",
        id: int,
        sound: "USound",
        location: FVector,
        volume: float,
        radius: float,
        pitch: float,
    ) -> bool:
        """UAudioSubsystem::PlaySound (UnAudio.h:45, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.play_sound pure virtual")

    def note_destroy(self, actor: "AActor") -> None:
        """UAudioSubsystem::NoteDestroy (UnAudio.h:46, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.note_destroy pure virtual")

    def get_low_quality_setting(self) -> bool:
        """UAudioSubsystem::GetLowQualitySetting (UnAudio.h:47, pure virtual)."""
        raise NotImplementedError(
            "UAudioSubsystem.get_low_quality_setting pure virtual"
        )

    def get_viewport(self) -> "UViewport":
        """UAudioSubsystem::GetViewport (UnAudio.h:48, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.get_viewport pure virtual")

    def render_audio_geometry(self, frame: "FSceneNode") -> None:
        """UAudioSubsystem::RenderAudioGeometry (UnAudio.h:49, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.render_audio_geometry pure virtual")

    def post_render(self, frame: "FSceneNode") -> None:
        """UAudioSubsystem::PostRender (UnAudio.h:50, pure virtual)."""
        raise NotImplementedError("UAudioSubsystem.post_render pure virtual")

    def clean_up(self) -> None:
        """UAudioSubsystem::CleanUp (UnAudio.h:51, empty inline body)."""


class FSoundData(TLazyArray[int]):
    """FSoundData (UnAudio.h:61): TLazyArray<BYTE> owned by a USound.

    Load (:65) and GetPeriod (:66) have no inline bodies; the Engine.lib
    overrides are unavailable, so they raise instead of reusing the
    TLazyArray reconstruction (whose behaviour the real override may
    extend).
    """

    def __init__(self, in_owner: "USound") -> None:
        super().__init__()
        self.Owner: "USound" = in_owner

    def load(self) -> None:
        """FSoundData::Load (UnAudio.h:65, Engine.lib override)."""
        raise NotImplementedError(f"FSoundData.load: {_ENGINE_LIB}")

    def get_period(self) -> float:
        """FSoundData::GetPeriod (UnAudio.h:66, Engine.lib)."""
        raise NotImplementedError(f"FSoundData.get_period: {_ENGINE_LIB}")


class USound(UObject):
    """A sound effect (UnAudio.h:75, DECLARE_CLASS)."""

    Audio: ClassVar[Optional[UAudioSubsystem]] = None

    def __init__(self) -> None:
        super().__init__()
        self.Data = FSoundData(self)
        # UnAudio.h:82-84; the C++ ctor only initialises Data and Duration,
        # leaving FileType/OriginalSize/Handle untouched.
        self.FileType = FName("None")
        self.OriginalSize = 0
        self.Duration = -1.0  # UnAudio.h:89
        self.Handle: Optional[object] = None

    def get_duration(self) -> float:
        """USound::GetDuration (UnAudio.h:95): cached Data.GetPeriod()."""
        if self.Duration < 0.0:
            self.Duration = self.Data.get_period()
        return self.Duration

    def ps2_convert(self) -> None:
        """USound::PS2Convert (UnAudio.h:102, Engine.lib)."""
        raise NotImplementedError(f"USound.ps2_convert: {_ENGINE_LIB}")

    def serialize(self, ar: FArchive) -> None:
        """USound::Serialize (UnAudio.h:105, Engine.lib)."""
        raise NotImplementedError(f"USound.serialize: {_ENGINE_LIB}")

    def destroy(self) -> None:
        """USound::Destroy (UnAudio.h:106, Engine.lib; void, UnObjBas.h:535)."""
        raise NotImplementedError(f"USound.destroy: {_ENGINE_LIB}")

    def post_load(self) -> None:
        """USound::PostLoad (UnAudio.h:107, Engine.lib)."""
        raise NotImplementedError(f"USound.post_load: {_ENGINE_LIB}")


class UMusic(UObject):
    """A song (UnAudio.h:117, DECLARE_CLASS)."""

    Audio: ClassVar[Optional[UAudioSubsystem]] = None

    def __init__(self) -> None:
        super().__init__()
        self.Data: TLazyArray[int] = TLazyArray()
        # UnAudio.h:123-125; the C++ ctor initialises nothing.
        self.FileType = FName("None")
        self.OriginalSize = 0
        self.Handle: Optional[object] = None

    def serialize(self, ar: FArchive) -> None:
        """UMusic::Serialize (UnAudio.h:133, Engine.lib)."""
        raise NotImplementedError(f"UMusic.serialize: {_ENGINE_LIB}")

    def destroy(self) -> None:
        """UMusic::Destroy (UnAudio.h:134, Engine.lib; void, UnObjBas.h:535)."""
        raise NotImplementedError(f"UMusic.destroy: {_ENGINE_LIB}")

    def post_load(self) -> None:
        """UMusic::PostLoad (UnAudio.h:135, Engine.lib)."""
        raise NotImplementedError(f"UMusic.post_load: {_ENGINE_LIB}")


# ---------------------------------------------------------------------------
# RIFF-WAVE header structs (UnAudio.h:153-201)
# ---------------------------------------------------------------------------
class FRiffWaveHeader:
    """Main RIFF-WAVE header (UnAudio.h:153)."""

    def __init__(self) -> None:
        self.rID: int = 0  # 'RIFF'
        self.ChunkLen: int = 0
        self.wID: int = 0  # 'WAVE'


class FRiffChunkOld:
    """General chunk header (UnAudio.h:161): 'fmt ', 'data', ..."""

    def __init__(self) -> None:
        self.ChunkID: int = 0
        self.ChunkLen: int = 0


class FFormatChunk:
    """'fmt ' chunk, WaveFormatEx (UnAudio.h:168)."""

    def __init__(self) -> None:
        self.wFormatTag: int = 0  # 1 = PCM
        self.nChannels: int = 0
        self.nSamplesPerSec: int = 0
        self.nAvgBytesPerSec: int = 0
        self.nBlockAlign: int = 0
        self.wBitsPerSample: int = 0
        self.cbSize: int = 0


class FSampleChunk:
    """'smpl' chunk (UnAudio.h:180)."""

    def __init__(self) -> None:
        self.dwManufacturer: int = 0
        self.dwProduct: int = 0
        self.dwSamplePeriod: int = 0
        self.dwMIDIUnityNote: int = 0
        self.dwMIDIPitchFraction: int = 0
        self.dwSMPTEFormat: int = 0
        self.dwSMPTEOffset: int = 0
        self.cSampleLoops: int = 0
        self.cbSamplerData: int = 0


class FSampleLoop:
    """Loop record following cbSamplerData in the 'smpl' chunk (UnAudio.h:193)."""

    def __init__(self) -> None:
        self.dwIdentifier: int = 0
        self.dwType: int = 0
        self.dwStart: int = 0  # samples
        self.dwEnd: int = 0  # samples
        self.dwFraction: int = 0
        self.dwPlayCount: int = 0


# ---------------------------------------------------------------------------
# FWaveModInfo (UnAudio.h:206)
# ---------------------------------------------------------------------------
class FWaveModInfo:
    """In-memory view of a WAVE file for modification (UnAudio.h:206).

    ReadWaveInfo (:248) fills the ``p*`` pointers into the caller's byte
    buffer; its body and every mutator are in Engine.lib, so the pointers
    stay None here.
    """

    def __init__(self) -> None:
        # Format fields, pointers into WavData (UnAudio.h:209-223).
        self.pSamplesPerSec: Optional[int] = None
        self.pAvgBytesPerSec: Optional[int] = None
        self.pBlockAlign: Optional[int] = None
        self.pBitsPerSample: Optional[int] = None
        self.pChannels: Optional[int] = None
        self.OldBitsPerSample: int = 0
        self.pWaveDataSize: Optional[int] = None
        self.pMasterSize: Optional[int] = None
        self.SampleDataStart: Optional[bytes] = None
        self.SampleDataEnd: Optional[bytes] = None
        self.SampleDataSize: int = 0
        self.WaveDataEnd: Optional[bytes] = None
        # Loop/size state (UnAudio.h:226-230).
        self.SampleLoopsNum: int = 0
        self.pSampleLoop: Optional[FSampleLoop] = None
        self.NewDataSize: int = 0
        self.NoiseGate: bool = False  # UnAudio.h:235,236 (ctor init order)

    @staticmethod
    def pad16_bit(in_dw: int) -> int:
        """FWaveModInfo::Pad16Bit (UnAudio.h:240): round up to even."""
        return (in_dw + 1) & ~1

    def read_wave_info(self, wav_data: bytearray) -> bool:
        """FWaveModInfo::ReadWaveInfo (UnAudio.h:248, Engine.lib)."""
        raise NotImplementedError(f"FWaveModInfo.read_wave_info: {_ENGINE_LIB}")

    def update_wave_data(self, wav_data: bytearray) -> bool:
        """FWaveModInfo::UpdateWaveData (UnAudio.h:252, Engine.lib)."""
        raise NotImplementedError(f"FWaveModInfo.update_wave_data: {_ENGINE_LIB}")

    def reduce_16to8(self) -> None:
        """FWaveModInfo::Reduce16to8 (UnAudio.h:255, Engine.lib)."""
        raise NotImplementedError(f"FWaveModInfo.reduce_16to8: {_ENGINE_LIB}")

    def halve_data(self) -> None:
        """FWaveModInfo::HalveData (UnAudio.h:256, Engine.lib)."""
        raise NotImplementedError(f"FWaveModInfo.halve_data: {_ENGINE_LIB}")

    def halve_reduce_16to8(self) -> None:
        """FWaveModInfo::HalveReduce16to8 (UnAudio.h:257, Engine.lib)."""
        raise NotImplementedError(f"FWaveModInfo.halve_reduce_16to8: {_ENGINE_LIB}")

    def noise_gate_filter(self) -> None:
        """FWaveModInfo::NoiseGateFilter (UnAudio.h:260, Engine.lib)."""
        raise NotImplementedError(f"FWaveModInfo.noise_gate_filter: {_ENGINE_LIB}")


__all__ = [
    "HAVE_VAG",
    "make_four_cc",
    "UAudioSubsystem",
    "FSoundData",
    "USound",
    "UMusic",
    "FRiffWaveHeader",
    "FRiffChunkOld",
    "FFormatChunk",
    "FSampleChunk",
    "FSampleLoop",
    "FWaveModInfo",
]
