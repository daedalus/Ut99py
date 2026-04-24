"""Window/X11 - Window management and input

Ported from Ut99PubSrc/{Window,XDrv,XLaunch}/
- UWindow: Window management
- UViewport: Viewport/window rendering surface
- UClient: Client connection to engine
- UInput: Input handling (keyboard, mouse)
- UConsole: Console/text output
- UXWindow: X11 platform
- UXLaunch: X11 launcher
"""

from typing import TYPE_CHECKING, Optional, ClassVar
from enum import IntEnum

from ..core import (
    UObject, UClass,
    FVector, FRotator, FPlane,
    FName, FString, TArray,
    FOutputDevice,
    RF_NoFlags,
)

if TYPE_CHECKING:
    from ..engine import UEngine, AActor
    from ..graphics import URenderDevice, FSceneNode


class EViewportStatus(IntEnum):
    ViewportOpening = 0
    ViewportNormal = 1
    ViewportClosing = 2


class EInputKey(IntEnum):
    IK_None = 0
    IK_LeftMouse = 1
    IK_RightMouse = 2
    IK_Cancel = 3
    IK_MiddleMouse = 4
    IK_Unknown = 5
    IK_Backspace = 8
    IK_Tab = 9
    IK_Unknown2 = 10
    IK_Enter = 13
    IK_Shift = 16
    IK_Control = 17
    IK_Alt = 18
    IK_Pause = 19
    IK_CapsLock = 20
    IK_Escape = 27
    IK_Space = 32
    IK_PageUp = 33
    IK_PageDown = 34
    IK_End = 35
    IK_Home = 36
    IK_Left = 37
    IK_Up = 38
    IK_Right = 39
    IK_Down = 40
    IK_Insert = 45
    IK_Delete = 46
    IK_0 = 48
    IK_1 = 49
    IK_2 = 50
    IK_3 = 51
    IK_4 = 52
    IK_5 = 53
    IK_6 = 54
    IK_7 = 55
    IK_8 = 56
    IK_9 = 57
    IK_A = 65
    IK_B = 66
    IK_C = 67
    IK_D = 68
    IK_E = 69
    IK_F = 70
    IK_G = 71
    IK_H = 72
    IK_I = 73
    IK_J = 74
    IK_K = 75
    IK_L = 76
    IK_M = 77
    IK_N = 78
    IK_O = 79
    IK_P = 80
    IK_Q = 81
    IK_R = 82
    IK_S = 83
    IK_T = 84
    IK_U = 85
    IK_V = 86
    IK_W = 87
    IK_X = 88
    IK_Y = 89
    IK_Z = 90
    IK_Tilde = 96
    IK_Multiply = 106
    IK_Add = 107
    IK_Subtract = 109
    IK_Decimal = 110
    IK_Divide = 111
    IK_F1 = 112
    IK_F2 = 113
    IK_F3 = 114
    IK_F4 = 115
    IK_F5 = 116
    IK_F6 = 117
    IK_F7 = 118
    IK_F8 = 119
    IK_F9 = 120
    IK_F10 = 121
    IK_F11 = 122
    IK_F12 = 123
    IK_NumLock = 144
    IK_Scroll = 145


class EInputAction(IntEnum):
    IST_None = 0
    IST_Press = 1
    IST_Hold = 2
    IST_Release = 3
    IST_Repeat = 4


class EMouseButtons(IntEnum):
    MB_Left = 0
    MB_Right = 1
    MB_Middle = 2
    MB_AbsoluteZ = 3
    MB_WheelUp = 4
    MB_WheelDown = 5


class FHitIndicator:
    def __init__(self):
        self._x: int = 0
        self._y: int = 0
        self._size: int = 0


class UViewport(UObject):
    _viewports: ClassVar[TArray['UViewport']] = TArray()
    
    def __init__(self):
        super().__init__()
        self._size_x: int = 640
        self._size_y: int = 480
        self._color_bytes: int = 32
        self._stride: int = 0
        self._b_is_fullscreen: bool = True
        self._b_locks_renderer: bool = False
        self._b_has_mouse_capture: bool = False
        
        self._current_preset: int = 0
        self._window_width: int = 640
        self._window_height: int = 480
        
        self._screen_pointer: Optional[bytes] = None
        self._flash_scale = FPlane()
        self._flash_fog = FPlane()
        self._clear_color = FPlane(0, 0, 0, 1)
        
        self._hit_data: Optional[bytes] = None
        self._hit_size: int = 0
        
        self._mouse_x: int = 0
        self._mouse_y: int = 0
        self._mouse_z: int = 0
        
        self._actor: Optional['AActor'] = None
        self._camera: Optional['AActor'] = None
        
        self._pending_delete: bool = False
    
    def get_size_x(self) -> int:
        return self._size_x
    
    def get_size_y(self) -> int:
        return self._size_y
    
    def lock(self, flash_scale: FPlane, flash_fog: FPlane, screen_clear: FPlane, render_lock_flags: int, hit_data: bytes = None, hit_size: int = 0) -> bool:
        self._hit_data = hit_data
        self._hit_size = hit_size
        return True
    
    def unlock(self) -> None:
        pass
    
    def present(self) -> None:
        pass
    
    def update_cursor(self) -> None:
        pass
    
    def set_capture(self, capture: bool) -> None:
        self._b_has_mouse_capture = capture
    
    def has_mouse_capture(self) -> bool:
        return self._b_has_mouse_capture
    
    def get_hit_coords(self) -> tuple[int, int]:
        return (self._mouse_x, self._mouse_y)


class UClient(UObject):
    def __init__(self):
        super().__init__()
        self._viewport: Optional[UViewport] = None
    
    def init(self, engine: 'UEngine') -> None:
        pass
    
    def shutdown(self) -> None:
        pass
    
    def tick(self, delta_time: float) -> None:
        pass
    
    def new_viewport(self, name: FName) -> Optional[UViewport]:
        return UViewport()
    
    def make_current(self, viewport: UViewport) -> None:
        pass


class FInputEvent:
    def __init__(self):
        self._key: EInputKey = EInputKey.IK_None
        self._action: EInputAction = EInputAction.IST_None
        self._x: float = 0.0
        self._y: float = 0.0
        self._delta: float = 0.0


class UInput(object):
    def __init__(self, owner: UObject):
        self._owner = owner
        self._bindings: dict = {}
        self._captured_viewport: Optional[UViewport] = None
        self._input_events: list = []
    
    def init(self) -> None:
        pass
    
    def exit(self) -> None:
        pass
    
    def bind_command(self, command: str, handler: str) -> None:
        self._bindings[command] = handler
    
    def exec_command(self, cmd: str) -> bool:
        return False
    
    def input_event(self, viewport: UViewport, key: EInputKey, action: EInputAction, x: float = 0.0, y: float = 0.0, delta: float = 0.0) -> None:
        event = FInputEvent()
        event._key = key
        event._action = action
        event._x = x
        event._y = y
        event._delta = delta
        self._input_events.append(event)
    
    def get_input_events(self) -> list:
        return self._input_events
    
    def clear_input_events(self) -> None:
        self._input_events.clear()


class UConsole(UObject):
    def __init__(self):
        super().__init__()
        self._history: list = []
        self._history_pos: int = 0
        self._cur_pos: int = 0
        self._top_line: int = 0
        self._no_rendering: bool = False
        self._console_speed: float = 1.0
        self._console_text_color: int = 0
    
    def type(self, text: str) -> None:
        self._history.append(text)
    
    def key_down(self, key: int) -> bool:
        return False
    
    def key_up(self, key: int) -> bool:
        return False
    
    def draw_console(self, viewport: UViewport) -> None:
        pass


class UXClient(UClient):
    def __init__(self):
        super().__init__()
        self._startup_fullscreen: bool = True
        self._slow_video_buffering: bool = False
        self._dga_mouse_enabled: bool = False
        
        self._x_display: int = 0
        self._in_menu_loop: bool = False
        
        self._normal_mouse_info: list = [0, 0, 0]
        self._capture_mouse_info: list = [0, 0, 0]
    
    def init(self, engine: 'UEngine') -> None:
        super().init(engine)
    
    def exec(self, cmd: str, out: FOutputDevice) -> bool:
        return False
    
    def tick(self, delta_time: float) -> None:
        super().tick(delta_time)
    
    def new_viewport(self, name: FName) -> Optional[UViewport]:
        return super().new_viewport(name)


class UXViewport(UViewport):
    def __init__(self):
        super().__init__()
        self._x_display: int = 0
        self._x_window: int = 0
        self._viewport_status: EViewportStatus = EViewportStatus.ViewportOpening
        self._hold_count: int = 0
        self._blit_flags: int = 0
        self._borderless: bool = False
        self._restore_auto_repeat: bool = False
        self._last_key: bool = False
        self._use_dga: bool = False
        self._mapped: bool = False
        self._iconified: bool = False
        
        self._mouse_accel_n: int = 5
        self._mouse_accel_d: int = 1
        self._mouse_threshold: int = 10
        
        self._saved_color_bytes: int = 0
        self._saved_caps: int = 0
        
        self._keysym_map: list = [0] * 65536
        self._shift_mask_map: list = [0] * 256
        self._key_repeat_map: list = [0] * 256
        self._wmchar_map: list = [0] * 256
    
    def destroy(self) -> None:
        super().destroy()
    
    def lock(self, flash_scale: FPlane, flash_fog: FPlane, screen_clear: FPlane, render_lock_flags: int, hit_data: bytes = None, hit_size: int = 0) -> bool:
        return super().lock(flash_scale, flash_fog, screen_clear, render_lock_flags, hit_data, hit_size)


class UXLaunch(UObject):
    def __init__(self):
        super().__init__()
        self._display_name: str = ":0.0"
        self._window_name: str = "Unreal Tournament"
    
    def init(self) -> bool:
        return True
    
    def run(self) -> None:
        pass
    
    def shutdown(self) -> None:
        pass


class FNotifyHook(UObject):
    def notify_destroy(self, src: UObject) -> None:
        pass


class FWindowHelper:
    def __init__(self):
        self._hwnd: int = 0
    
    def get_hwnd(self) -> int:
        return self._hwnd
    
    def set_window_text(self, text: str) -> None:
        pass
    
    def get_client_rect(self) -> tuple[int, int, int, int]:
        return (0, 0, 640, 480)


class UWindows(UClient):
    def __init__(self):
        super().__init__()
    
    def init(self, engine: 'UEngine') -> None:
        super().init(engine)
    
    def exec(self, cmd: str, out: FOutputDevice) -> bool:
        return False


class UWindow(UObject):
    def __init__(self):
        super().__init__()
        self._parent: Optional[UWindow] = None
        self._children: list = []
    
    def show(self) -> None:
        pass
    
    def hide(self) -> None:
        pass
    
    def minimize(self) -> None:
        pass
    
    def maximize(self) -> None:
        pass
    
    def restore(self) -> None:
        pass
    
    def set_focus(self) -> None:
        pass
    
    def set_text(self, text: str) -> None:
        pass
    
    def get_text(self) -> str:
        return ""


class UDialog(UWindow):
    def __init__(self):
        super().__init__()
        self._modal: bool = False
        self._result: int = 0
    
    def show_modal(self) -> int:
        return self._result
    
    def end_dialog(self, result: int) -> None:
        self._result = result


class UButton(UDialog):
    def __init__(self):
        super().__init__()
        self._default: bool = False
        self._cancel: bool = False
    
    def on_click(self) -> None:
        pass


class UEdit(UDialog):
    def __init__(self):
        super().__init__()
        self._text: str = ""
        self._max_length: int = 256
    
    def get_text(self) -> str:
        return self._text
    
    def set_text(self, text: str) -> None:
        self._text = text


class UListBox(UDialog):
    def __init__(self):
        super().__init__()
        self._items: list = []
        self._selected_index: int = 0
    
    def add_string(self, text: str) -> None:
        self._items.append(text)
    
    def get_string(self, index: int) -> str:
        return self._items[index] if 0 <= index < len(self._items) else ""


class UComboBox(UDialog):
    def __init__(self):
        super().__init__()
        self._items: list = []
        self._text: str = ""
    
    def add_string(self, text: str) -> None:
        self._items.append(text)


class UProgressBar(UDialog):
    def __init__(self):
        super().__init__()
        self._position: float = 0.0
        self._max_position: float = 100.0
    
    def set_progress(self, position: float) -> None:
        self._position = position
    
    def get_progress(self) -> float:
        return self._position


class UMessageBox(UDialog):
    def __init__(self):
        super().__init__()
        self._message: str = ""
        self._caption: str = ""
    
    def message_box(self, message: str, caption: str = "Confirm") -> int:
        self._message = message
        self._caption = caption
        return self.show_modal()


def MessageBox(message: str, caption: str = "Confirm") -> int:
    mb = UMessageBox()
    return mb.message_box(message, caption)


def InputBox(prompt: str, default: str = "") -> str:
    return default