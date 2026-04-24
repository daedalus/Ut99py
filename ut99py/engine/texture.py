from typing import Optional, List
from ut99py.core import FName, FString, UObject, FArchive
from ut99py.core.types import FTime
from ut99py.graphics import URenderDevice

NUM_PAL_COLORS = 256
MAX_MIPS = 12

class FColor:
    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def brightness(self) -> int:
        return (2 * self.r + 3 * self.g + 1 * self.b) >> 3

    def fbrightness(self) -> float:
        return (2.0 * self.r + 3.0 * self.g + 1.0 * self.b) / (6.0 * 256.0)

    def true_color(self) -> int:
        return ((self.r & 0xff) << 16) | ((self.g & 0xff) << 8) | (self.b & 0xff)

    def plane(self) -> tuple:
        return (self.r / 255.0, self.g / 255.0, self.b / 255.0, self.a / 255.0)

    @staticmethod
    def from_plane(p: tuple) -> 'FColor':
        def clamp(v: float) -> int:
            return max(0, min(255, int(v)))
        return FColor(clamp(p[0] * 256), clamp(p[1] * 256), clamp(p[2] * 256), clamp(p[3] * 256))

    def __eq__(self, other: 'FColor') -> bool:
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    def __ne__(self, other: 'FColor') -> bool:
        return not self.__eq__(other)

    def brighten(self, amount: int) -> 'FColor':
        p = self.plane()
        return FColor.from_plane((p[0] * (1.0 - amount / 24.0), p[1] * (1.0 - amount / 24.0), p[2] * (1.0 - amount / 24.0), p[3]))

    def serialize(self, ar: FArchive) -> 'FColor':
        ar << self.r << self.g << self.b << self.a
        return self


class UPalette(UObject):
    def __init__(self):
        super().__init__()
        self.colors: List[FColor] = [FColor() for _ in range(NUM_PAL_COLORS)]

    def serialize(self, ar: FArchive) -> 'UPalette':
        super().serialize(ar)
        ar << self.colors
        return self


class FMipmapBase:
    def __init__(self, u_bits: int = 0, v_bits: int = 0):
        self.data_ptr = None
        self.u_size = 1 << u_bits
        self.v_size = 1 << v_bits
        self.u_bits = u_bits
        self.v_bits = v_bits


class FMipmap(FMipmapBase):
    def __init__(self, u_bits: int = 0, v_bits: int = 0, data_size: int = 0):
        super().__init__(u_bits, v_bits)
        self.data_array = bytearray(data_size)

    def clear(self) -> None:
        for i in range(len(self.data_array)):
            self.data_array[i] = 0


class ETextureFormat:
    P8 = 0x00
    RGBA7 = 0x01
    RGB16 = 0x02
    DXT1 = 0x03
    RGB8 = 0x04
    RGBA8 = 0x05
    MAX = 0xff


class ELODSet:
    NONE = 0
    WORLD = 1
    SKIN = 2
    MAX = 8


class UBitmap(UObject):
    format: int = ETextureFormat.P8
    palette: Optional['UPalette'] = None
    u_bits: int = 0
    v_bits: int = 0
    u_size: int = 0
    v_size: int = 0
    u_clamp: int = 0
    v_clamp: int = 0
    mip_zero: FColor = FColor()
    max_color: FColor = FColor()
    __last_update_time: FTime = FTime()

    def lock(self, texture_info: 'FTextureInfo', time: FTime, lod: int, ren_dev: URenderDevice) -> None:
        raise NotImplementedError

    def unlock(self, texture_info: 'FTextureInfo') -> None:
        raise NotImplementedError

    def get_mip(self, i: int) -> FMipmapBase:
        raise NotImplementedError


class UTexture(UBitmap):
    def __init__(self):
        super().__init__()
        self.bump_map: Optional['UTexture'] = None
        self.detail_texture: Optional['UTexture'] = None
        self.macro_texture: Optional['UTexture'] = None
        self.diffuse: float = 1.0
        self.specular: float = 0.0
        self.alpha: float = 0.0
        self.scale: float = 1.0
        self.friction: float = 1.0
        self.mip_mult: float = 1.0
        self.footstep_sound: Optional['USound'] = None
        self.hit_sound: Optional['USound'] = None
        self.poly_flags: int = 0
        self.b_high_color_quality: bool = False
        self.b_high_texture_quality: bool = False
        self.b_realtime: bool = False
        self.b_parametric: bool = False
        self.b_realtime_changed: bool = False
        self.b_has_comp: bool = False
        self.lod_set: int = ELODSet.NONE
        self.anim_next: Optional['UTexture'] = None
        self.anim_cur: Optional['UTexture'] = None
        self.prime_count: int = 0
        self.prime_current: int = 0
        self.min_frame_rate: float = 10.0
        self.max_frame_rate: float = 30.0
        self.accumulator: float = 0.0
        self.mips: List[FMipmap] = []
        self.comp_mips: List[FMipmap] = []
        self.comp_format: int = ETextureFormat.RGBA8

    def serialize(self, ar: FArchive) -> 'UTexture':
        super().serialize(ar)
        ar << self.bump_map
        ar << self.detail_texture
        ar << self.macro_texture
        ar << self.diffuse
        ar << self.specular
        ar << self.alpha
        ar << self.scale
        ar << self.friction
        ar << self.mip_mult
        ar << self.footstep_sound
        ar << self.hit_sound
        ar << self.poly_flags
        ar << self.b_high_color_quality
        ar << self.b_high_texture_quality
        ar << self.b_realtime
        ar << self.b_parametric
        ar << self.b_realtime_changed
        ar << self.b_has_comp
        ar << self.lod_set
        ar << self.anim_next
        ar << self.anim_cur
        ar << self.prime_count
        ar << self.prime_current
        ar << self.min_frame_rate
        ar << self.max_frame_rate
        ar << self.accumulator
        ar << self.mips
        ar << self.comp_mips
        ar << self.comp_format
        return self

    def post_load(self) -> None:
        super().post_load()
        if self.anim_cur is None:
            self.anim_cur = self

    def get_mip(self, i: int) -> Optional[FMipmapBase]:
        if 0 <= i < len(self.mips):
            return self.mips[i]
        return None

    def default_lod(self) -> int:
        return 1

    def get(self, time: FTime) -> 'UTexture':
        self.update(time)
        return self.anim_cur if self.anim_cur else self

    def clear(self, clear_flags: int) -> None:
        pass

    def init(self, u_size: int, v_size: int) -> None:
        self.u_size = u_size
        self.v_size = v_size
        self.u_bits = (u_size - 1).bit_length()
        self.v_bits = (v_size - 1).bit_length()
        self.u_clamp = u_size
        self.v_clamp = v_size

    def tick(self, delta_seconds: float) -> None:
        pass

    def constant_time_tick(self) -> None:
        pass

    def update(self, time: FTime) -> None:
        pass

    def prime(self) -> None:
        pass


class FTextureInfo:
    def __init__(self):
        self.texture: Optional[UTexture] = None
        self.cache_id: int = 0
        self.palette_cache_id: int = 0
        self.pan: tuple = (0.0, 0.0, 0.0)
        self.max_color: Optional[FColor] = None
        self.format: int = ETextureFormat.P8
        self.u_scale: float = 1.0
        self.v_scale: float = 1.0
        self.u_size: int = 0
        self.v_size: int = 0
        self.u_clamp: int = 0
        self.v_clamp: int = 0
        self.num_mips: int = 0
        self.lod: int = 0
        self.palette: Optional[List[FColor]] = None
        self.b_high_color_quality: bool = False
        self.b_high_texture_quality: bool = False
        self.b_realtime: bool = False
        self.b_parametric: bool = False
        self.b_realtime_changed: bool = False
        self.mips: List[Optional[FMipmapBase]] = [None] * MAX_MIPS

    def load(self) -> None:
        pass

    def unload(self) -> None:
        pass

    def cache_max_color(self) -> None:
        pass


class FFontCharacter:
    def __init__(self):
        self.start_u: int = 0
        self.start_v: int = 0
        self.u_size: int = 0
        self.v_size: int = 0


class FFontPage:
    def __init__(self):
        self.texture: Optional[UTexture] = None
        self.characters: List[FFontCharacter] = []


class UFont(UObject):
    def __init__(self):
        super().__init__()
        self.characters_per_page: int = 0
        self.pages: List[FFontPage] = []
        self.char_remap: dict = {}
        self.is_remapped: bool = False

    def serialize(self, ar: FArchive) -> 'UFont':
        super().serialize(ar)
        ar << self.characters_per_page
        ar << self.pages
        ar << self.char_remap
        ar << self.is_remapped
        return self

    def remap_char(self, ch: str) -> str:
        if not self.is_remapped:
            return ch
        return self.char_remap.get(ch, ' ')


__all__ = [
    'FColor',
    'UPalette',
    'FMipmapBase',
    'FMipmap',
    'ETextureFormat',
    'ELODSet',
    'UBitmap',
    'UTexture',
    'FTextureInfo',
    'FFontCharacter',
    'FFontPage',
    'UFont',
    'NUM_PAL_COLORS',
    'MAX_MIPS',
]