"""UnAudio.h: four-CC macro, inline ctors, pure-virtual/audio interface.

Expected values come from the C++ header semantics: MAKEFOURCC
(UnAudio.h:145) packs ch0 | ch1<<8 | ch2<<16 | ch3<<24 into a DWORD, so
'R','I','F','F' yields the RIFF tag the RIFF framing uses
(tests/test_riff.py: 0x46464952); Pad16Bit (UnAudio.h:240) is
((InDW + 1) & ~1); the USound ctor (UnAudio.h:88-90) sets Duration to
-1 so GetDuration recomputes via Data.GetPeriod (UnAudio.h:95-99).
"""

import pytest

from ut99py.core.template import TLazyArray
from ut99py.engine.audio import (
    FFormatChunk,
    FRiffChunkOld,
    FRiffWaveHeader,
    FSampleChunk,
    FSampleLoop,
    FSoundData,
    FWaveModInfo,
    UAudioSubsystem,
    UMusic,
    USound,
    make_four_cc,
)

RIFF = 0x46464952
WAVE = 0x45564157


def test_make_four_cc_matches_cpp_macro_order():
    # MAKEFOURCC: (BYTE)ch0 | (BYTE)ch1<<8 | (BYTE)ch2<<16 | (BYTE)ch3<<24.
    assert make_four_cc("R", "I", "F", "F") == RIFF
    assert make_four_cc("W", "A", "V", "E") == WAVE
    assert make_four_cc("d", "a", "t", "a") == 0x61746164


def test_make_four_cc_masks_bytes():
    # Each operand is cast to (BYTE) before the shift.
    assert make_four_cc(*"ÿÿÿÿ") == 0xFFFFFFFF


def test_pad16_bit_rounds_up_to_even():
    # ((InDW + 1) & ~1)
    assert FWaveModInfo.pad16_bit(0) == 0
    assert FWaveModInfo.pad16_bit(1) == 2
    assert FWaveModInfo.pad16_bit(3) == 4
    assert FWaveModInfo.pad16_bit(4) == 4
    assert FWaveModInfo.pad16_bit(65535) == 65536


def test_wave_mod_info_ctor_defaults():
    # FWaveModInfo() (UnAudio.h:233-237): NoiseGate off, no loops.
    info = FWaveModInfo()
    assert info.NoiseGate is False
    assert info.SampleLoopsNum == 0
    # ReadWaveInfo not called: the p* view pointers stay unset.
    assert info.pSamplesPerSec is None


def test_usound_ctor_sets_negative_duration():
    # USound() (UnAudio.h:88-90): Duration = -1.f, Data bound to this.
    sound = USound()
    assert sound.Duration == -1.0
    assert isinstance(sound.Data, FSoundData)
    assert sound.Data.Owner is sound


def test_usound_duration_recompute_needs_engine_lib():
    # GetDuration caches Data.GetPeriod(); the period body is Engine.lib.
    sound = USound()
    with pytest.raises(NotImplementedError, match="GetPeriod|get_period"):
        sound.get_duration()


def test_fsound_data_is_a_lazy_byte_array():
    # FSoundData : TLazyArray<BYTE> (UnAudio.h:61).
    sound = USound()
    assert isinstance(sound.Data, TLazyArray)
    assert isinstance(sound.Data, list)


def test_fsound_data_load_override_is_engine_lib():
    # FSoundData::Load (UnAudio.h:65) is overridden in Engine.lib, so the
    # inherited TLazyArray reconstruction is not silently used.
    data = FSoundData(USound())
    with pytest.raises(NotImplementedError, match="Engine.lib"):
        data.load()


def test_umusic_ctor_matches_header_field_set():
    # UMusic() (UnAudio.h:129-130) initialises nothing; Data is a
    # TLazyArray<BYTE> member (UnAudio.h:122).
    music = UMusic()
    assert isinstance(music.Data, TLazyArray)
    assert len(music.Data) == 0
    # UMusic declares no Duration member (that is USound-only, :83).
    assert not hasattr(music, "Duration")


def test_audio_subsystem_pure_virtuals_raise():
    audio = UAudioSubsystem()
    with pytest.raises(NotImplementedError):
        audio.init()
    with pytest.raises(NotImplementedError):
        audio.play_sound(None, 0, None, None, 1.0, 1.0, 1.0)
    with pytest.raises(NotImplementedError):
        audio.get_viewport()


def test_audio_subsystem_cleanup_is_empty_inline():
    # CleanUp() {} (UnAudio.h:51) has a body, unlike the pure virtuals.
    assert UAudioSubsystem().clean_up() is None


def test_wave_struct_field_layouts_match_header():
    # Field presence mirrors the header structs (UnAudio.h:153-201).
    assert vars(FRiffWaveHeader()) == {"rID": 0, "ChunkLen": 0, "wID": 0}
    assert vars(FRiffChunkOld()) == {"ChunkID": 0, "ChunkLen": 0}
    assert vars(FFormatChunk()) == {
        "wFormatTag": 0,
        "nChannels": 0,
        "nSamplesPerSec": 0,
        "nAvgBytesPerSec": 0,
        "nBlockAlign": 0,
        "wBitsPerSample": 0,
        "cbSize": 0,
    }
    assert set(vars(FSampleChunk())) == {
        "dwManufacturer",
        "dwProduct",
        "dwSamplePeriod",
        "dwMIDIUnityNote",
        "dwMIDIPitchFraction",
        "dwSMPTEFormat",
        "dwSMPTEOffset",
        "cSampleLoops",
        "cbSamplerData",
    }
    assert set(vars(FSampleLoop())) == {
        "dwIdentifier",
        "dwType",
        "dwStart",
        "dwEnd",
        "dwFraction",
        "dwPlayCount",
    }
