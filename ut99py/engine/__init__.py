"""Engine package - Game engine logic, actors, rendering, physics

Ported from Ut99PubSrc/Engine/
- AActor: Base actor class
- APlayerPawn, APawn: Player and AI pawns
- AWeapon, AInventory: Weapons and inventory
- ABrush, AZoneInfo: Brushes and zones  
- UEngine: Main engine
- ULevel: Level management
- UNetDriver, UChannel: Networking
- URenderDevice: Rendering device interface
- UTexture, UMaterial: Texture and material system
- UMesh, USkeletalMesh: Mesh systems
"""

from typing import TYPE_CHECKING, Optional, Any, ClassVar
from enum import IntEnum

from ..core import (
    UObject, UClass, UStruct, UFunction, UState, UPackage,
    FVector, FRotator, FPlane, FQuat, FMatrix,
    FName, FString, TArray, TMap,
    FArchive, FOutputDevice,
)

if TYPE_CHECKING:
    from .level import ULevel
    from .render import URenderDevice, UViewport


class EPhysics(IntEnum):
    PHYS_None = 0
    PHYS_Walking = 1
    PHYS_Falling = 2
    PHYS_Flying = 3
    PHYS_Projectile = 4
    PHYS_Rooted = 5
    PHYS_Vehicle = 8


class EActorFlags(IntEnum):
    bCanTeleport = 0
    bCollideWorld = 1
    bRender = 2
    bCullDistance = 3
    bNoDelete = 4
    bMovable = 5
    bAlwaysTick = 6
    bDemoRecording = 7


class FActorLink:
    __slots__ = ('actor', 'next')
    
    def __init__(self, actor: Optional['AActor'] = None, next: Optional['FActorLink'] = None):
        self.actor = actor
        self.next = next


class FPointRegion:
    __slots__ = ('zone', 'i_leaf', 'bbox')
    
    def __init__(self):
        self.zone: Optional['AZoneInfo'] = None
        self.i_leaf = 0
        self.bbox = None


class AActor(UObject):
    _actor_count: ClassVar[int] = 0
    
    def __init__(self):
        super().__init__()
        self._level: Optional['ULevel'] = None
        self._role: FName = FName("ROLE_SimulatedProxy")
        self._remote_role: FName = FName("ROLE_Authority")
        
        self._location = FVector()
        self._rotation = FRotator()
        self._velocity = FVector()
        self._original_location = FVector()
        
        self._owner: Optional[AActor] = None
        self._base: Optional[AActor] = None
        self._attached: Optional[FActorLink] = None
        
        self._event: FName = FName("None")
        self._tag: FName = FName("None")
        
        self._collision_radius = 34.0
        self._collision_height = 88.0
        self._draw_scale = 1.0
        self._pre_pivot = FVector()
        
        self._draw_type = 0
        self._render_density = 1
        self._physics = EPhysics.PHYS_Walking
        
        self._life_span = 0.0
        self._life = 100.0
        self._max_encumbrance = 0
        
        self._sound_radius = 0
        self._sound_volume = 1.0
        
        self._light_type = 0
        self._light_effect = 0
        self._light_brightness = 0
        self._light_hue = 0
        self._light_saturation = 0
        
        self._ambient_sound: Optional['USound'] = None
        self._instigator: Optional[AActor] = None
        
        self._region = FPointRegion()
        
        self._x_level = None
        self._level_index = 0
        
        self._latent_function: Optional[UFunction] = None
        
        self._b_hidden = False
        self._b_delete_me = False
        self._b_ticked = False
        self._b_rotate_to_desired = False
        self._b_collide_world = True
        self._b_collide_actors = True
        self._b_block_actors = True
        self._b_block_players = True
        
        self._volume_radius = 0
        
        self._draw_matrix = None
        self._skin: Optional['UTexture'] = None
        self._mesh: Optional['UMesh'] = None
        self._brush: Optional['ABrush'] = None
        
        AActor._actor_count += 1
    
    @property
    def level(self) -> Optional['ULevel']:
        return self._level
    
    @property
    def location(self) -> FVector:
        return self._location
    
    @location.setter
    def location(self, value: FVector) -> None:
        self._location = value
    
    @property
    def rotation(self) -> FRotator:
        return self._rotation
    
    @rotation.setter
    def rotation(self, value: FRotator) -> None:
        self._rotation = value
    
    @property
    def velocity(self) -> FVector:
        return self._velocity
    
    @velocity.setter
    def velocity(self, value: FVector) -> None:
        self._velocity = value
    
    def get_level(self) -> Optional['ULevel']:
        return self._level
    
    def get_player_pawn(self) -> Optional['APlayerPawn']:
        if isinstance(self, APlayerPawn) and self._player:
            return self
        return None
    
    def is_player(self) -> bool:
        if isinstance(self, APawn):
            return self._b_is_player
        return False
    
    def is_owned_by(self, other: 'AActor') -> bool:
        actor = self
        while actor:
            if actor == other:
                return True
            actor = actor._owner
        return False
    
    def get_top_owner(self) -> 'AActor':
        top = self
        while top._owner:
            top = top._owner
        return top
    
    def is_in_zone(self, other: 'AZoneInfo') -> bool:
        if self._region.zone != self._level:
            return self._region.zone == other
        return True
    
    def get_view_rotation(self) -> FRotator:
        if isinstance(self, APawn):
            return self._view_rotation
        return self._rotation
    
    def is_brush(self) -> bool:
        return self._brush is not None and isinstance(self, ABrush)
    
    def is_static_brush(self) -> bool:
        return self._brush is not None and isinstance(self, ABrush) and self._b_static
    
    def is_moving_brush(self) -> bool:
        return self._brush is not None and isinstance(self, ABrush) and not self._b_static
    
    def set_owner(self, new_owner: Optional['AActor']) -> None:
        self._owner = new_owner
    
    def set_collision(self, new_collide_actors: bool, new_block_actors: bool, new_block_players: bool = False) -> None:
        self._b_collide_actors = new_collide_actors
        self._b_block_actors = new_block_actors
        self._b_block_players = new_block_players
    
    def set_collision_size(self, new_radius: float, new_height: float) -> None:
        self._collision_radius = new_radius
        self._collision_height = new_height
    
    def set_base(self, new_base: Optional['AActor'], notify: bool = True) -> None:
        self._base = new_base
    
    def set_location(self, new_location: FVector) -> bool:
        self._location = new_location
        return True
    
    def set_rotation(self, new_rotation: FRotator) -> bool:
        self._rotation = new_rotation
        return True
    
    def get_cylinder_extent(self) -> FVector:
        return FVector(self._collision_radius, self._collision_radius, self._collision_height)
    
    def world_sound_radius(self) -> float:
        return 25.0 * (self._sound_radius + 1)
    
    def world_volumetric_radius(self) -> float:
        return 25.0 * (self._volume_radius + 1)
    
    def is_blocked_by(self, other: 'AActor') -> bool:
        if other == self._level:
            return self._b_collide_world
        elif other.is_brush():
            return self._b_collide_world and (self.get_player_pawn() if other._b_block_players else other._b_block_actors)
        elif self.is_brush():
            return other._b_collide_world and (self._b_block_players if other.get_player_pawn() else self._b_block_actors)
        else:
            return (self.get_player_pawn() or isinstance(self, AProjectile)) and other._b_block_players and \
                   (other.get_player_pawn() or isinstance(self, AProjectile)) and self._b_block_players
    
    def is_based_on(self, other: 'AActor') -> bool:
        test = self
        while test:
            if test == other:
                return True
            test = test._base
        return False
    
    def tick(self, delta_time: float, tick_type: int) -> bool:
        return True
    
    def destroy(self) -> None:
        self._b_delete_me = True
        AActor._actor_count -= 1
    
    def is_pending_kill(self) -> bool:
        return self._b_delete_me
    
    def process_state(self, delta_seconds: float) -> None:
        pass
    
    def process_event(self, function: UFunction, parms: dict = None) -> None:
        pass
    
    def get_primitive(self) -> Optional['UPrimitive']:
        if self._brush:
            return self._brush
        if self._mesh:
            return self._mesh
        return None
    
    def get_skin(self, index: int = 0) -> Optional['UTexture']:
        return self._skin
    
    def to_local(self) -> 'FCoords':
        return FCoords()
    
    def to_world(self) -> 'FCoords':
        return FCoords()
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.get_full_name()} at {self._location}>"


class FCoords:
    __slots__ = ('origin', 'x', 'y', 'z')
    
    def __init__(self):
        self.origin = FVector()
        self.x = FVector(1, 0, 0)
        self.y = FVector(0, 1, 0)
        self.z = FVector(0, 0, 1)
    
    def __truediv__(self, other: FVector) -> 'FCoords':
        return FCoords()
    
    def __mul__(self, other: FVector) -> 'FCoords':
        return FCoords()


class ABrush(AActor):
    def __init__(self):
        super().__init__()
        self._brush: Optional['UModel'] = None
        self._poly_list: TArray['UPolys'] = TArray()
        self._b_static = False
        self._b_semisolid = False
        self._b_not_visible = False
        self._csg_reject: Optional[FArchive] = None
        self._valid_pre_cache = False


class AZoneInfo(AActor):
    def __init__(self):
        super().__init__()
        self._zone_priority = 0
        self._max_purchase = 0
        self._ambient_sound: Optional['USound'] = None
        self._entry_actor: Optional[AActor] = None
        self._exit_actor: Optional[AActor] = None
        
        self._zone_gravity = FVector(0, 0, -900)
        
        self._kill_z = 0
        
        self._terrain_type: Optional['ATerrainInfo'] = None
        
        self._last_enter_time = 0.0


class ALevelInfo(AZoneInfo):
    def __init__(self):
        super().__init__()
        self._time_seconds = 0.0
        self._game_sequence: Optional[AActor] = None
        self._pausing = False
        self._hr: FName = FName("None")
        self._mn = 0
        self._se = 0
        self._yr = 0
        self._dy = 0
        self._mo = 0
        self._lt = 0
        
        self._home_movie: FName = FName("None")
        
        self._allow_pausic = False
        
        self._net_flags = TArray()
        
        self._actors: TArray[AActor] = TArray()
        
        self._prerequisite: Optional[AActor] = None


class APawn(AActor):
    def __init__(self):
        super().__init__()
        self._player: Optional['UPlayer'] = None
        self._controller: Optional['AController'] = None
        
        self._view_rotation = FRotator()
        self._desired_rotation = FRotator()
        
        self._ground_roof = 0.0
        self._last_floor_z = 0.0
        
        self._b_is_player = False
        self._b_broadcast_to = False
        
        self._health = 100
        self._max_health = 100
        
        self._face: Optional['UTexture'] = None
        self._multi_skins: TArray['UTexture'] = TArray()
        self._head_bone = FName("head")
        self._mesh_name: FName = FName("None")
        
        self._sound_impact: Optional['USound'] = None
        self._sound_jump: Optional['USound'] = None
        self._sound_land: Optional['USound'] = None
        
        self._weapon: Optional[AWeapon] = None
        self._inventory: Optional['AInventory'] = None
        
        self._enemy: Optional[AActor] = None
        
        self._hits = 0
        self._stumps = 0
        
        self._b_can_jump = True
        self._b_can_walk = True
        self._b_can_swim = True
        
        self._move_direction = FVector()


class APlayerPawn(APawn):
    def __init__(self):
        super().__init__()
        self._player: Optional['UPlayer'] = None
        self._viewport: Optional['UViewport'] = None
        self._god_mode = False
        self._fov_angle = 90.0
        self._desired_fov = 90.0
        
        self._shot_time = 0.0
        
        self._flash_va = FVector()
        self._flash_vb = FVector()
        
        self._b_is_player = True


class AWeapon(AActor):
    def __init__(self):
        super().__init__()
        self._player: Optional[APlayerPawn] = None
        
        self._ammo_removed = 0
        self._fire_count = 0
        
        self._pickup_uses = 0
        
        self._item_name: FName = FName("None")
        
        self._fire_anim: FName = FName("None")
        self._select_anim: FName = FName("None")
        
        self._projectile_class: Optional[UClass] = None
        self._alt_projectile_class: Optional[UClass] = None
        
        self._fire_sound: Optional['USound'] = None
        self._alt_fire_sound: Optional['USound'] = None
        self._select_sound: Optional['USound'] = None
        
        self._reload_sound: Optional['USound'] = None
        self._muzzle_smoke: Optional['UEmitter'] = None
        
        self._ammo_type: Optional['AInventory'] = None
        self._alt_ammo_type: Optional['AInventory'] = None
        
        self._aim = FVector()
        
        self._b_point_accurate = False
        self._b_burst_fire = False
        self._b_aim_offset = False


class AInventory(AActor):
    def __init__(self):
        super().__init__()
        self._original_actor: Optional[AActor] = None
        
        self._item_name: FName = FName("None")
        self._item_article = 1
        
        self._pickup_sound: Optional['USound'] = None
        
        self._player: Optional[APlayerPawn] = None
        
        self._next_inventory: Optional[AInventory] = None
        
        self._b_active_inventory = False


class AAmmo(AInventory):
    def __init__(self):
        super().__init__()
        self._ammo_amount = 0
        self._max_ammo = 0
        
        self._ammo_class: Optional[UClass] = None


class APickup(AInventory):
    def __init__(self):
        super().__init__()
        self._b_instant_respawn = False
        self._b_allowed_to_cull = True
        self._life_count = 0
        self._respawn_time = 0.0


class ACamera(AActor):
    def __init__(self):
        super().__init__()
        self._viewport: Optional['UViewport'] = None
        self._camera_mesh: Optional['UMesh'] = None
        self._camera_actor: Optional[AActor] = None
        
        self._shake_timer = 0.0
        self._shake_magnitude = FVector()
        
        self._default_fov = 90.0
        self._fov = 90.0
        
        self._b_static = False
        self._b_show_debug = False
        
        self._view_target: Optional[AActor] = None


class AProjectile(AActor):
    def __init__(self):
        super().__init__()
        self._speed = 0.0
        self._max_wanted_speed = 0.0
        
        self._damage = 0.0
        self._damage_radius = 0.0
        
        self._momentum = 0.0
        
        self._damage_type: FName = FName("None")
        self._spawner: Optional[AActor] = None
        
        self._b_net_on_header = False
        self._b_alt_keep = False


class AController(UObject):
    def __init__(self):
        super().__init__()
        self._pawn: Optional[APawn] = None
        self._player: Optional['UPlayer'] = None
        
        self._order: FName = FName("None")
        self._focus: Optional[AActor] = None
        self._target: Optional[AActor] = None
        
        self._location = FVector()
        
        self._damage_type: FName = FName("None")
        
        self._b_delayed = False
        self._b_notify_log = False
        self._b_bot = False


class APlayerController(AController):
    def __init__(self):
        super().__init__()
        self._player = None
        self._viewport: Optional['UViewport'] = None
        self._interactions = TArray()
        
        self._key_0: int = 0
        self._key_1: int = 0
        self._key_2: int = 0
        
        self._fov_desired_angle = 90.0
        
        self._b_a_i_l_ing = False


class AGameInfo(UObject):
    def __init__(self):
        super().__init__()
        self._game_type: FName = FName("None")
        
        self._admin: Optional['APlayer'] = None
        
        self._game_options: FString = FString()
        
        self._current_team = 0
        
        self._rules_list: TArray = TArray()
        
        self._eligible_players: TArray = TArray()
        
        self._scoreboard_class: Optional[UClass] = None
        self._scoring_class: Optional[UClass] = None
        
        self._death_match_class: Optional[UClass] = None
        
        self._b_balanced_teams = False
        self._b_allow_death_message = True
        
        self._b_no_cheating = False
        
        self._b_allow_join_in_progress = False


class ULevel(UObject):
    def __init__(self):
        super().__init__()
        self._actors: TArray[AActor] = TArray()
        self._fruit: TArray[AActor] = TArray()
        
        self._level_info: Optional[ALevelInfo] = None
        self._engine: Optional['UEngine'] = None
        
        self._url: Optional['UURL'] = None
        
        self._model: Optional['UModel'] = None
        
        self._polys: Optional['UPolys'] = None
        
        self._first_search_actor: Optional[AActor] = None
        self._last_stale_referenced_actor: Optional[AActor] = None
        
        self._b_allow_path_building = True
        
        self._b_fully_loaded = False
        self._b_requested_full_update = False
        
        self._b_world_compose_event_found = False
        
        self._tick_started = False
        
        self._last_render_time = 0.0
        
        self._hunt_list: TArray[AActor] = TArray()
        
        self._note_list: TArray[AActor] = TArray()
        
        self._block_bsp = 0


class UGameEngine(UObject):
    def __init__(self):
        super().__init__()
        self._game: Optional[AGameInfo] = None
        self._client: Optional['UClient'] = None
        self._server: Optional['UServer'] = None
        
        self._b_enable_stats = False
        self._b_show_debug = False


class URenderDevice(UObject):
    def __init__(self):
        super().__init__()
        self._renderer_class: Optional[UClass] = None
        self._b_use_hardware = False
        self._b_supports_video_memory_texture = False
        self._b_waits_for_video = False
    
    def init(self, engine: 'UEngine') -> bool:
        return True
    
    def shutdown(self) -> None:
        pass
    
    def set_resize(self, render_width: int, render_height: int, is_fullscreen: bool) -> bool:
        return True
    
    def exec(self, cmd: str, out: FOutputDevice) -> bool:
        return False


class AEmitter(AActor):
    def __init__(self):
        super().__init__()
        self._particle_template: Optional['UEmitter'] = None


class ATerrainInfo(AZoneInfo):
    def __init__(self):
        super().__init__()
        self._terrain_alpha: list = []
        self._terrain_heightmap: list = []


class UPlayer(UObject):
    def __init__(self):
        super().__init__()
        self._player_name: str = "Player"
        self._id: int = 0


class UServer(UObject):
    def __init__(self):
        super().__init__()
        self._max_connections = 0


class UClient(UObject):
    def __init__(self):
        super().__init__()
        self._viewport: Optional['UViewport'] = None


class UURL(UObject):
    def __init__(self):
        super().__init__()
        self._protocol: str = ""
        self._host: str = ""
        self._port: int = 0
        self._map: str = ""
        self._options: dict = {}
        self._portal: str = ""
        self._valid: bool = False
    
    def is_internal(self) -> bool:
        return self._protocol.lower() in ("unreal", "local")
    
    def is_local_internal(self) -> bool:
        return self._protocol.lower() == "local" and not self._host
    
    def has_option(self, name: str) -> bool:
        return name in self._options
    
    def get_option(self, name: str, default: str = "") -> str:
        return self._options.get(name, default)
    
    def add_option(self, option: str) -> None:
        if "=" in option:
            key, value = option.split("=", 1)
            self._options[key] = value
        else:
            self._options[option] = ""
    
    def url_string(self, fully_qualified: bool = False) -> str:
        result = f"{self._protocol}://"
        if self._host:
            result += self._host
        if self._port:
            result += f":{self._port}"
        result += f"/{self._map}"
        for key, value in self._options.items():
            if value:
                result += f"?{key}={value}"
            else:
                result += f"?{key}"
        return result
    
    def __eq__(self, other: 'UURL') -> bool:
        return (self._protocol == other._protocol and 
                self._host == other._host and 
                self._port == other._port and 
                self._map == other._map)


class EConnectionState(IntEnum):
    USOCK_Invalid = 0
    USOCK_Closed = 1
    USOCK_Pending = 2
    USOCK_Open = 3


class EChannelType(IntEnum):
    CHTYPE_None = 0
    CHTYPE_Control = 1
    CHTYPE_Actor = 2
    CHTYPE_File = 3
    CHTYPE_MAX = 8


RELIABLE_BUFFER = 128
MAX_PACKETID = 16384
MAX_CHSEQUENCE = 1024
MAX_BUNCH_HEADER_BITS = 64
MAX_PACKET_HEADER_BITS = 16
MAX_PACKET_TRAILER_BITS = 1


class FOutBunch:
    def __init__(self, connection: Optional['UNetConnection'] = None):
        self._connection = connection
        self._data: bytes = b''
        self._b_reliable: bool = False
        self._b_acked: bool = False
        self._ch_index: int = 0
        self._packet_id: int = 0


class FInBunch:
    def __init__(self, connection: Optional['UNetConnection'] = None):
        self._connection = connection
        self._data: bytes = b''
        self._b_reliable: bool = False
        self._ch_index: int = 0
        self._packet_id: int = 0


class UChannel(UObject):
    def __init__(self):
        super().__init__()
        self._connection: Optional['UNetConnection'] = None
        self._open_acked: bool = False
        self._closing: bool = False
        self._ch_index: int = 0
        self._opened_locally: bool = False
        self._open_packet_id: int = 0
        self._open_temporary: bool = False
        self._ch_type: EChannelType = EChannelType.CHTYPE_None
        self._num_in_rec: int = 0
        self._num_out_rec: int = 0
        self._negotiated_ver: int = 0
        self._in_rec: Optional[FInBunch] = None
        self._out_rec: Optional[FOutBunch] = None
        self._broken: bool = False
    
    def init(self, connection: 'UNetConnection', ch_index: int, opened_locally: bool) -> None:
        self._connection = connection
        self._ch_index = ch_index
        self._opened_locally = opened_locally
    
    def set_closing_flag(self) -> None:
        self._closing = True
    
    def close(self) -> None:
        self._closing = True
    
    def describe(self) -> str:
        return f"Channel {self._ch_index}"
    
    def received_bunch(self, bunch: FInBunch) -> None:
        pass
    
    def received_nak(self, nak_packet_id: int) -> None:
        pass
    
    def tick(self, delta_time: float) -> None:
        pass


class UControlChannel(UChannel, FOutputDevice):
    def __init__(self):
        super().__init__()
        self._ch_type = EChannelType.CHTYPE_Control
    
    def init(self, connection: 'UNetConnection', ch_index: int, opened_locally: bool) -> None:
        super().init(connection, ch_index, opened_locally)
    
    def received_bunch(self, bunch: FInBunch) -> None:
        data = bunch._data.decode('utf-8', errors='replace')
        self.serialize(data)
    
    def serialize(self, data: str, event: FName = FName("Log")) -> None:
        pass


class UActorChannel(UChannel):
    def __init__(self):
        super().__init__()
        self._ch_type = EChannelType.CHTYPE_Actor
        self._actor: Optional[AActor] = None
    
    def received_bunch(self, bunch: FInBunch) -> None:
        pass


class UFileChannel(UChannel):
    def __init__(self):
        super().__init__()
        self._ch_type = EChannelType.CHTYPE_File
    
    def received_bunch(self, bunch: FInBunch) -> None:
        pass


class UNetConnection(UPlayer):
    def __init__(self):
        super().__init__()
        self._driver: Optional['UNetDriver'] = None
        self._state: EConnectionState = EConnectionState.USOCK_Invalid
        self._url: Optional[UURL] = None
        self._package_map: Optional[UPackageMap] = None
        
        self._protocol_version: int = 1
        self._remote_version: int = 0
        self._max_packet: int = 256
        self._packet_overhead: int = 0
        self._internal_ack: bool = False
        self._challenge: int = 0
        self._negotiated_ver: int = 0
        self._user_flags: int = 0
        self._request_url: FString = FString()
        
        self._last_receive_time: float = 0.0
        self._last_send_time: float = 0.0
        self._last_tick_time: float = 0.0
        self._last_rep_time: float = 0.0
        self._queued_bytes: int = 0
        self._tick_count: int = 0
        
        self._allow_merge: bool = True
        self._time_sensitive: bool = False
        self._last_out_bunch: Optional[FOutBunch] = None
        
        self._in_rate: float = 0.0
        self._out_rate: float = 0.0
        self._in_packets: float = 0.0
        self._out_packets: float = 0.0
        self._in_bunches: float = 0.0
        self._out_bunches: float = 0.0
        
        self._channels: list = []
    
    def init(self, driver: 'UNetDriver', url: UURL) -> None:
        self._driver = driver
        self._url = url
    
    def close(self) -> None:
        self._state = EConnectionState.USOCK_Closed
    
    def tick(self, delta_time: float) -> None:
        pass
    
    def send_bunch(self, bunch: FOutBunch) -> int:
        return 0
    
    def is_net_ready(self, saturate: bool) -> bool:
        return True
    
    def channel_for_index(self, index: int) -> Optional[UChannel]:
        if 0 <= index < len(self._channels):
            return self._channels[index]
        return None


class UNetDriver(UObject):
    def __init__(self):
        super().__init__()
        self._clientconnections: list = []
        self._serverconnections: list = []
        
        self._max_channels: int = 1023
        self._max_connections: int = 16
        
        self._time_slice: float = 0.05
        self._allow_latent_transfer: bool = True
        
        self._net_speed: int = 10000
        self._initial_bandwidth: float = 0.0
        self._requested_channels: int = 0
    
    def init(self, engine: 'UEngine') -> bool:
        return True
    
    def shutdown(self) -> None:
        pass
    
    def tick(self, delta_time: float) -> None:
        pass
    
    def notify_player(self, connection: UNetConnection) -> None:
        pass
    
    def notify_postplayer(self, connection: UNetConnection) -> None:
        pass
    
    def close_connection(self, connection: UNetConnection) -> None:
        pass
    
    def verify_checksum(self, data: bytes) -> int:
        return 0


class UChannelIterator:
    def __init__(self, driver: UNetDriver):
        self._driver = driver
    
    def __iter__(self):
        return iter(self._driver._serverconnections + self._driver._clientconnections)


class DelayedPacket:
    def __init__(self):
        self._data: bytes = b''
        self._send_time: float = 0.0


class FDownloadInfo:
    def __init__(self):
        self._class: Optional[UClass] = None
        self._class_name: str = ""
        self._params: str = ""
        self._compression: bool = False


class UPendingLevel(UObject):
    def __init__(self):
        super().__init__()
        self._url: Optional[UURL] = None
        self._net_connection: Optional[UNetConnection] = None
        self._download_info: list = []
        self._failed_reason: str = ""
        self._completed: bool = False
    
    def tick(self, delta_time: float) -> None:
        pass
    
    def aborted(self, reason: str) -> None:
        self._failed_reason = reason
        self._completed = True


class UNetPendingLevel(UPendingLevel):
    def __init__(self):
        super().__init__()


class UDemoPlayPendingLevel(UPendingLevel):
    def __init__(self):
        super().__init__()
        self._demo_file: str = ""


class UPlayer(UObject):
    def __init__(self):
        super().__init__()
        self._player_name: str = "Player"
        self._id: int = 0


class UServer(UObject):
    def __init__(self):
        super().__init__()
        self._max_connections = 0


class UClient(UObject):
    def __init__(self):
        super().__init__()
        self._viewport: Optional['UViewport'] = None


class FDownload:
    def __init__(self):
        self._class: Optional[UClass] = None
        self._package_name: str = ""
        self._package_guid: FGuid = FGuid()
        self._data: list = []
        self._compressed: bool = False
        self._offset: int = 0


class UDownloadNotify:
    def __init__(self):
        self._downloads: list = []
    
    def set_guarded_correspondence(self) -> None:
        pass
    
    def callback(self, frame: int) -> None:
        pass


from .assets import (
    AssetLoader, GAssetLoader,
    UPackage as UPackageAsset, UTextureAsset, USoundAsset, UMeshAsset,
    FPackageFileSummary, FObjectExport, FObjectImport,
)