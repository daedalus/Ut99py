"""Asset loading system - Unreal Engine package loader

Ported from Ut99PubSrc/Core/UPackage.cpp / UnPackage.h

Unreal uses .u/.unr files as packages containing serialized objects.
Loading flow:
1. Open package file (.u for scripts, .unr for levels, .utx for textures)
2. Read header (FPackageFileSummary)
3. Load import table (classes/objects referenced)
4. Load export table (objects defined in this package)
5. Deserialize each object, resolving internal references
"""

from typing import Optional, Dict, List, Any
from enum import IntEnum
import struct
import os

from ..core.types import (
    FName, FGuid, FVector, FRotator, FPlane,
    TArray,
)
from ..core.objects import UObject, UClass
from ..core.system import FArchive, FArchiveFileReader, GLog

SIGNATURE_UT = 0x9E2A83C1


class EPackageFlags(IntEnum):
    """Package flags stored in header"""
    PKG_Allowable = 0x00000001
    PKG_ClientRequired = 0x00000002
    PKG_ServerSideOnly = 0x00000004
    PKG_Cooked = 0x00000008
    PKG_NeedsLog = 0x00000010
    PKG_Compressed = 0x00000020
    PKG_Unprotected = 0x00000040
    PKG_Protected = 0x00000080
    PKG_Saving = 0x00000100
    PKG_Dirty = 0x00000200


class FPackageFileSummary:
    """Package file header - first thing read from any .u/.unr file"""
    
    def __init__(self):
        self._magic: int = 0x00000000
        self._file_version: int = 0
        self._licensee_version: int = 0
        self._package_flags: int = 0
        self._name_count: int = 0
        self._name_offset: int = 0
        self._export_count: int = 0
        self._export_offset: int = 0
        self._import_count: int = 0
        self._import_offset: int = 0
        self._dependency_table_offset: int = 0
        self._thumbnail_offset: int = 0
        self._guid: FGuid = FGuid()
        self._generations: List[Dict] = []
        self._saved_by_engine_version: int = 0
        self._compatible_with_engine_version: int = 0
    
    def serialize(self, ar: FArchive) -> 'FPackageFileSummary':
        """Load package header from archive"""
        self._magic = ar._read_uint32()
        
        # Check magic (0x9e2a83c1 for UT packages)
        if self._magic != 0x9e2a83c1:
            import warnings
            warnings.warn(f"Unknown package magic: 0x{self._magic:08x}")
        
        self._file_version = ar._read_uint32()
        self._licensee_version = ar._read_uint32()
        
        if self._file_version >= 68:
            self._package_flags = ar._read_int32()
        
        self._name_count = ar._read_int32()
        self._name_offset = ar._read_int32()
        
        self._export_count = ar._read_int32()
        self._export_offset = ar._read_int32()
        
        self._import_count = ar._read_int32()
        self._import_offset = ar._read_int32()
        
        if self._file_version >= 70:
            self._dependency_table_offset = ar._read_int32()
        
        if self._file_version >= 74:
            self._thumbnail_offset = ar._read_int64()
        
        # Read GUID
        self._guid._a = ar._read_uint32()
        self._guid._b = ar._read_uint32()
        self._guid._c = ar._read_uint32()
        self._guid._d = ar._read_uint32()
        
        # Read generations
        gen_count = ar._read_int32()
        for _ in range(gen_count):
            gen = {
                'export_count': ar._read_int32(),
                'name_count': ar._read_int32()
            }
            self._generations.append(gen)
        
        return self


class FObjectExport:
    """Single object export entry in package"""
    
    def __init__(self):
        self._class_index: int = 0          # Index into import/export table
        self._super_index: int = 0           # Parent class
        self._package_index: int = 0        # Package this object belongs to
        self._object_name: FName = FName()
        self._flags: int = 0
        self._serial_size: int = 0
        self._serial_offset: int = 0
        self._load_failed: bool = False
        self._object: Optional[UObject] = None


class FObjectImport:
    """Single object import entry (object referenced by this package)"""
    
    def __init__(self):
        self._class_package: FName = FName()
        self._class_name: FName = FName()
        self._package_index: int = 0
        self._object_name: FName = FName()
        self._x_level: bool = False


class UPackage(UObject):
    """Unreal package (.u/.unr/.utx/.usx files)
    
    Contains serialized game assets: textures, meshes, sounds, levels, etc.
    """
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self._guid: FGuid = FGuid()
        self._flags: int = 0
        self._file_version: int = 0
        self._licensee_version: int = 0
        
        self._name_table: List[FName] = []
        self._imports: List[FObjectImport] = []
        self._exports: List[FObjectExport] = []
        
        self._fully_loaded: bool = False
        self._source_package: Optional['UPackage'] = None
        
        self._filename: str = ""
    
    def get_header(self) -> FPackageFileSummary:
        return self._summary
    
    def get_export_count(self) -> int:
        return len(self._exports)
    
    def get_import_count(self) -> int:
        return len(self._imports)


class UTextureAsset(UObject):
    """Texture asset (.utx files)"""
    
    def __init__(self):
        super().__init__()
        self._format: int = 0
        self._size_x: int = 0
        self._size_y: int = 0
        self._u_clamp: int = 0
        self._v_clamp: int = 0
        self._b_linear: bool = False
        self._b_two_component: bool = False
        self._b_alpha: bool = False
        self._b_hi_color: bool = False
        self._b_compressed: bool = False
        self._b_realtime: bool = False
        self._cache: Any = None
        self._last_update_time: float = 0.0


class USoundAsset(UObject):
    """Sound asset (.uax files)"""
    
    def __init__(self):
        super().__init__()
        self._sample_rate: int = 22050
        self._sample_size: int = 0
        self._duration: float = 0.0
        self._channels: int = 1
        self._b_compressed: bool = False
        self._b_stereo: bool = False
        self._compression_type: int = 0


class UMeshAsset(UObject):
    """Mesh asset (.usx files)"""
    
    def __init__(self):
        super().__init__()
        self._vertex_count: int = 0
        self._face_count: int = 0
        self._radius: float = 0.0
        self._bounding_box_min: FVector = FVector()
        self._bounding_box_max: FVector = FVector()
        self._lod_levels: List[Dict] = []


class FLevelSummary:
    """Level summary stored in .unr files"""
    
    def __init__(self):
        self._title: FName = FName()
        self._author: FName = FName()
        self._recommended_players: str = ""
        self._description: str = ""
        self._music: Optional[USound] = None
        self._typical_player_start: FVector = FVector()
        self._flags: int = 0


class AssetLoader:
    """Main asset loading system
    
    Handles loading packages (.u/.unr/.utx/.uax/.usx) and
    extracting textures, sounds, meshes, and level data.
    """
    
    def __init__(self):
        self._loaded_packages: Dict[str, UPackage] = {}
        self._package_path: str = ""
        
        self._texture_cache: Dict[str, UTexture] = {}
        self._sound_cache: Dict[str, USound] = {}
        self._mesh_cache: Dict[str, UMesh] = {}
        
        self._pending_packages: List[str] = []
        self._b_async_loading: bool = False
        self._async_load_complete_callbacks: Dict[str, list] = {}
    
    def set_package_path(self, path: str) -> None:
        """Set base path for package files"""
        self._package_path = path.rstrip('/\\')
    
    def _get_package_path(self, filename: str) -> str:
        """Get full path to package file"""
        if os.path.isabs(filename):
            return filename
        if self._package_path:
            return os.path.join(self._package_path, filename)
        return filename
    
    def load_package(self, filename: str) -> Optional[UPackage]:
        """Load a complete package file
        
        Args:
            filename: Package filename (e.g., "Botpack.u", "DM-Turbine.unr")
            
        Returns:
            Loaded UPackage or None on failure
        """
        full_path = self._get_package_path(filename)
        
        if not os.path.exists(full_path):
            GLog.serialize(f"Package not found: {full_path}")
            return None
        
        if filename in self._loaded_packages:
            return self._loaded_packages[filename]
        
        try:
            ar = FArchiveFileReader(full_path)
            package = UPackage(filename)
            self._load_package_header(package, ar)
            self._load_name_table(package, ar)
            self._load_import_table(package, ar)
            self._load_export_table(package, ar)
            
            self._loaded_packages[filename] = package
            ar.close()
            
            GLog.serialize(f"Loaded package: {filename} ({package.get_export_count()} exports)")
            return package
        except Exception as e:
            GLog.serialize(f"Failed to load package {filename}: {e}")
            return None
    
    def _load_package_header(self, package: UPackage, ar: FArchive) -> None:
        """Load package file header (FPackageFileSummary)"""
        package._summary = FPackageFileSummary()
        package._summary.serialize(ar)
        package._file_version = package._summary._file_version
        package._licensee_version = package._summary._licensee_version
        package._guid = package._summary._guid
        package._flags = package._summary._package_flags
        package._filename = ar._file.name if hasattr(ar, '_file') else ""
    
    def _load_name_table(self, package: UPackage, ar: FArchive) -> None:
        """Load name table (FName entries)"""
        ar.seek(package._summary._name_offset)
        
        for _ in range(package._summary._name_count):
            name = ar._read_string()
            flags = ar._read_int32()
            fname = FName(name, flags)
            package._name_table.append(fname)
    
    def _load_import_table(self, package: UPackage, ar: FArchive) -> None:
        """Load import table (objects this package depends on)"""
        ar.seek(package._summary._import_offset)
        
        for _ in range(package._summary._import_count):
            imp = FObjectImport()
            imp._class_package = FName(ar._read_string())
            imp._class_name = FName(ar._read_string())
            imp._package_index = ar._read_int32()
            imp._object_name = FName(ar._read_string())
            if package._file_version >= 68:
                imp._x_level = ar._read_bool()
            package._imports.append(imp)
    
    def _load_export_table(self, package: UPackage, ar: FArchive) -> None:
        """Load export table (objects defined in this package)"""
        ar.seek(package._summary._export_offset)
        
        for _ in range(package._summary._export_count):
            exp = FObjectExport()
            exp._class_index = ar._read_int32()
            exp._super_index = ar._read_int32()
            exp._package_index = ar._read_int32()
            exp._object_name = FName(ar._read_string())
            exp._flags = ar._read_int32()
            exp._serial_size = ar._read_int32()
            exp._serial_offset = ar._read_int32()
            package._exports.append(exp)
    
    def get_texture(self, package_name: str, texture_name: str) -> Optional['UTextureAsset']:
        """Load texture from package
        
        Args:
            package_name: Package containing texture (e.g., "GenIn.u")
            texture_name: Texture object name
        """
        cache_key = f"{package_name}.{texture_name}"
        if cache_key in self._texture_cache:
            return self._texture_cache[cache_key]
        
        package = self.load_package(package_name)
        if not package:
            return None
        
        for exp in package._exports:
            if exp._object_name.get_text() == texture_name:
                texture = UTexture()
                texture._name = texture_name
                texture._package = package_name
                self._texture_cache[cache_key] = texture
                return texture
        
        return None
    
    def get_sound(self, package_name: str, sound_name: str) -> Optional['USoundAsset']:
        """Load sound from package"""
        cache_key = f"{package_name}.{sound_name}"
        if cache_key in self._sound_cache:
            return self._sound_cache[cache_key]
        
        package = self.load_package(package_name)
        if not package:
            return None
        
        for exp in package._exports:
            if exp._object_name.get_text() == sound_name:
                sound = USound()
                sound._name = sound_name
                sound._package = package_name
                self._sound_cache[cache_key] = sound
                return sound
        
        return None
    
    def get_mesh(self, package_name: str, mesh_name: str) -> Optional['UMeshAsset']:
        """Load mesh from package"""
        cache_key = f"{package_name}.{mesh_name}"
        if cache_key in self._mesh_cache:
            return self._mesh_cache[cache_key]
        
        package = self.load_package(package_name)
        if not package:
            return None
        
        for exp in package._exports:
            if exp._object_name.get_text() == mesh_name:
                mesh = UMesh()
                mesh._name = mesh_name
                mesh._package = package_name
                self._mesh_cache[cache_key] = mesh
                return mesh
        
        return None
    
    def load_level(self, level_name: str) -> Optional[UPackage]:
        """Load level package (.unr file)
        
        Args:
            level_name: Level name (e.g., "DM-Turbine", "CTF-Command")
        """
        if not level_name.endswith('.unr'):
            level_name = level_name + '.unr'
        
        return self.load_package(level_name)
    
    def preload_package(self, filename: str) -> None:
        """Preload package header for streaming"""
        full_path = self._get_package_path(filename)
        if not os.path.exists(full_path):
            return
        
        self._pending_packages.append(filename)
    
    def process_async_loads(self) -> None:
        """Process pending async package loads"""
        if not self._pending_packages:
            return
        
        filename = self._pending_packages.pop(0)
        package = self.load_package(filename)
        
        if package and filename in self._async_load_complete_callbacks:
            for callback in self._async_load_complete_callbacks[filename]:
                callback(package)
    
    def flush_cache(self) -> None:
        """Flush all asset caches"""
        self._texture_cache.clear()
        self._sound_cache.clear()
        self._mesh_cache.clear()
        self._loaded_packages.clear()
    
    def get_loaded_packages(self) -> List[str]:
        """Get list of loaded package names"""
        return list(self._loaded_packages.keys())


# Global asset loader instance
GAssetLoader = AssetLoader()