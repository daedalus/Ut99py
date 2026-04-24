"""Graphics drivers - OpenGL, D3D, XMesa

Ported from Ut99PubSrc/{OpenGLDrv,D3DDrv,XMesaGLDrv}/
- URenderDevice: Base rendering device
- FSceneNode: Scene frame for rendering
- FSpanBuffer: Span buffer for rendering
- FDynamicSprite: Sprite rendering
- UOpenGLRenderDevice: OpenGL renderer
- UDirect3DRenderDevice: Direct3D renderer
- UXMesaGLRenderDevice: XMesa OpenGL renderer
"""

from typing import TYPE_CHECKING, Optional, ClassVar
from enum import IntEnum

from ..core import (
    UObject, UClass,
    FVector, FRotator, FPlane,
    FName, FString, TArray,
    FOutputDevice,
)

try:
    from ..engine import FCoords
except ImportError:
    class FCoords:
        def __init__(self):
            self.origin = (0.0, 0.0, 0.0)
            self.axes = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]

if TYPE_CHECKING:
    from ..engine import AActor, ULevel, UViewport
    from ..audio import USound


class ERenderCaps(IntEnum):
    CAPS_NONE = 0
    CAPS_MODESET = 1
    CAPS_TEXNONPOW2 = 2
    CAPS_TEXPROCMASK = 4
    CAPS_TEXCF = 8
    CAPS_ZBIAS = 16
    CAPS_FOG = 32


class ESceneNodeState(IntEnum):
    STATE_Empty = 0
    STATE_All = 1
    STATE_Portal = 2
    STATE_OccludingBsp = 3


class FSpanBuffer:
    def __init__(self):
        self._span: list = []
        self._span_start: int = 0
        self._span_end: int = 0
        self._lock_count: int = 0
        self._color: int = 0


class FSpan:
    __slots__ = ('x1', 'x2', 'y', 'texture', 'light', 'specular')
    
    def __init__(self, x1: int = 0, x2: int = 0, y: int = 0):
        self.x1 = x1
        self.x2 = x2
        self.y = y
        self.texture = None
        self.light = None
        self.specular = None


class FScreenBounds:
    def __init__(self):
        self._x_min = 0
        self._x_max = 0
        self._y_min = 0
        self._y_max = 0


class FSurfaceInfo:
    def __init__(self):
        self._poly: Optional['UPolys'] = None
        self._texture: Optional['UTexture'] = None
        self._light_map: Optional[UObject] = None
        self._detail_texture: Optional['UTexture'] = None


class FSurfaceFacet:
    def __init__(self):
        self._source_bsp_node: int = 0
        self._index: int = 0
        self._surface_info = FSurfaceInfo()
        self._bounds = FScreenBounds()


class FSceneNode:
    def __init__(self):
        self._viewport: Optional['UViewport'] = None
        self._level: Optional['ULevel'] = None
        self._parent: Optional[FSceneNode] = None
        self._sibling: Optional[FSceneNode] = None
        self._child: Optional[FSceneNode] = None
        self._i_surf: int = 0
        self._zone_number: int = 0
        self._recursion: int = 0
        self._mirror: float = 1.0
        self._near_clip = FPlane()
        self._coords = FCoords()
        self._uncoords = FCoords()
        self._span: Optional[FSpanBuffer] = None
        
        self._draw: list = []
        self._sprite: Optional[FDynamicSprite] = None
        self._x = 0
        self._y = 0
        self._xb = 0
        self._yb = 0
        
        self._fx = 0.0
        self._fy = 0.0
        self._fx15 = 0.0
        self._fy15 = 0.0
        self._fx2 = 0.0
        self._fy2 = 0.0
        self._zoom = 1.0
        self._proj = FVector()
        self._r_proj = FVector()
        self._prj_xm = 0.0
        self._prj_xp = 0.0
        self._prj_ym = 0.0
        self._prj_yp = 0.0
        
        self._view_sides: list[FVector] = []
        self._view_planes: list[FPlane] = []
    
    def compute_render_size(self) -> None:
        pass
    
    def compute_render_coords(self, location: FVector, rotation: FRotator) -> None:
        pass


class FTransTexture:
    def __init__(self):
        self._x = 0
        self._y = 0
        self._z = 0
        self._u = 0.0
        self._v = 0.0
        self._u_clamp = 0.0
        self._v_clamp = 0.0
        self._frame_number: int = 0


class FOutVector:
    def __init__(self):
        self._point = FVector()
        self._flags: int = 0


class FTransform(FOutVector):
    def __init__(self):
        super().__init__()
        self._screen_x: float = 0.0
        self._screen_y: float = 0.0
        self._int_y: int = 0
        self._rz: float = 0.0
    
    def project(self, frame: FSceneNode) -> None:
        self._rz = frame._proj.z / self._point.z if frame._proj.z != 0 else 0
        self._screen_x = self._point.x * self._rz + frame._fx15
        self._screen_y = self._point.y * self._rz + frame._fy15
        self._int_y = int(self._screen_y)
    
    def compute_outcode(self, frame: FSceneNode) -> int:
        flags = 0
        if self._point.z < frame._prj_xm:
            flags |= 0x04
        if self._point.z > frame._prj_xp:
            flags |= 0x08
        if self._point.y < frame._prj_ym:
            flags |= 0x10
        if self._point.y > frame._prj_yp:
            flags |= 0x20
        self._flags = flags
        return flags


class FDynamicItem:
    def __init__(self):
        self._actor: Optional['AActor'] = None
        self._lod: int = 0
        self._position = FVector()


class FDynamicSprite:
    def __init__(self):
        self._items: list[FDynamicItem] = []
        self._next: Optional[FDynamicSprite] = None


class FBspDrawList:
    def __init__(self):
        self._bsp: list = []
        self._next: Optional[FBspDrawList] = None


class FDummyRenderer(UObject):
    def __init__(self):
        super().__init__()
        self._viewport: Optional['UViewport'] = None
    
    def set_viewport(self, viewport: 'UViewport') -> None:
        self._viewport = viewport
    
    def pre_render(self) -> None:
        pass
    
    def render(self, scene: FSceneNode) -> None:
        pass
    
    def post_render(self) -> None:
        pass


class FRenderHitIndicator:
    def __init__(self):
        self._x: int = 0
        self._y: int = 0
        self._size: int = 0


class URenderDevice(UObject):
    _render_devices: ClassVar[TArray['URenderDevice']] = TArray()
    
    def __init__(self):
        super().__init__()
        self._renderer_class: Optional[UClass] = None
        self._viewport: Optional['UViewport'] = None
        
        self._b_use_hardware: bool = False
        self._b_supports_video_memory_texture: bool = False
        self._b_waits_for_video: bool = False
        
        self._brightness: float = 0.0
        self._contrast: float = 0.0
        self._gamma: float = 0.0
        
        self._delta_pan: float = 0.0
    
    def init(self, engine: 'UEngine') -> bool:
        return True
    
    def shutdown(self) -> None:
        pass
    
    def set_resize(self, render_width: int, render_height: int, is_fullscreen: bool) -> bool:
        return True
    
    def exec_cmd(self, cmd: str, out: FOutputDevice) -> bool:
        return False
    
    def get_depth_bits(self) -> int:
        return 16
    
    def get_caps(self) -> int:
        return ERenderCaps.CAPS_NONE
    
    def locked(self, viewport: 'UViewport') -> bool:
        return False
    
    def unlock(self) -> None:
        pass
    
    def flush(self) -> None:
        pass
    
    def present(self, viewport: 'UViewport') -> None:
        pass
    
    def check_advanced_caps(self) -> bool:
        return False


class UOpenGLRenderDevice(URenderDevice):
    def __init__(self):
        super().__init__()
        self._opengl_dll_name: str = "opengl32.dll"
        self._gl_id: int = 0
    
    def init(self, engine: 'UEngine') -> bool:
        return super().init(engine)
    
    def shutdown(self) -> None:
        super().shutdown()


class UDirect3DRenderDevice(URenderDevice):
    def __init__(self):
        super().__init__()
        self._d3d_driver: int = 0
        self._d3d_device: int = 0
    
    def init(self, engine: 'UEngine') -> bool:
        return super().init(engine)


class UXMesaGLRenderDevice(URenderDevice):
    def __init__(self):
        super().__init__()
        self._display: int = 0
        self._context: int = 0
    
    def init(self, engine: 'UEngine') -> bool:
        return super().init(engine)


class UPolys(UObject):
    def __init__(self):
        super().__init__()
        self._elements: list = []


class UTexture(UObject):
    def __init__(self):
        super().__init__()
        self._format: int = 0
        self._usize: int = 256
        self._vsize: int = 256
        self._u_clamp: int = 0
        self._v_clamp: int = 0
        self._outer_frame: int = 0
        self._render_command_number: int = 0
        self._cache_id: int = 0
        self._last_frame: int = 0
        self._b_realize_72: bool = True
    
    def get_name(self) -> FName:
        return self._name


class UMaterial(UTexture):
    def __init__(self):
        super().__init__()


class UUnrealMaterial(UMaterial):
    def __init__(self):
        super().__init__()


class UModifier(UMaterial):
    def __init__(self):
        super().__init__()
        self._material: Optional[UMaterial] = None


class UScriptedTexture(UTexture):
    def __init__(self):
        super().__init__()
        self._target: Optional[UTexture] = None
        self._source: Optional[UTexture] = None
        self._color_start: int = 0
        self._color_end: int = 0
        self._b_no_scale: bool = False
        self._b_huge: bool = False


class UMesh(UObject):
    def __init__(self):
        super().__init__()
        self._points: list[FVector] = []
        self._faces: list = []
        self._skin_faces: list = []
        self._max_lods: int = 0
        self._lods: list = []
        self._bounding_sphere = FVector()


class USkeletalMesh(UMesh):
    def __init__(self):
        super().__init__()
        self._ref_bones: list = []
        self._ref_poses: list = []
        self._skeletal_depths: list = []


class UModel(UObject):
    def __init__(self):
        super().__init__()
        self._bounds = FVector()
        self._bounds_quasi: FVector()
        self._root: int = 0
        self._nodes: list = []
        self._polys: Optional[UPolys] = None
        self._light_map: list = []
        self._vertex_index: list = []


UEngine = None