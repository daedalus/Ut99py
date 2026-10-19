"""Asset loading system - Unreal Engine package loader

Ported from Ut99PubSrc/Core/UPackage.cpp / UnPackage.h

Unreal uses .u/.unr files as packages containing serialized objects.
Loading flow:
1. Open package file (.u for scripts, .unr for levels, .utx for textures)
2. Read header (FPackageFileSummary)
3. Load import table (classes/objects referenced)
4. Load export table (objects defined in this package)
5. Deserialize each object, resolving internal references

Steps 2-4 (the on-disk format) are owned by core/linkers.py; UPackage adds
the asset view on top of the linker's tables.
"""

from typing import Optional, Dict, List, Any
from enum import IntEnum
import os

from ..core.types import FName, FGuid, FVector
from ..core.objects import UObject
from ..core.system import FArchive, GLog
from ..core.objver import PACKAGE_FILE_TAG
from ..core import linkers as core_linkers
from ..core.linkers import FPackageFileSummary, FObjectExport, FObjectImport
from .texture import UTexture
from .mesh import UMesh
from .texload import is_texture_export, load_texture, texture_to_rgba
from ..audio import USound

SIGNATURE_UT = PACKAGE_FILE_TAG


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


class UPackage(UObject):
    """Unreal package (.u/.unr/.utx/.usx files)

    Contains serialized game assets: textures, meshes, sounds, levels, etc.
    """

    def __init__(self, name: str = ""):
        super().__init__()
        self._name = FName(name)
        self._guid: FGuid = FGuid()
        self._flags: int = 0
        self._file_version: int = 0
        self._licensee_version: int = 0

        self._summary: Optional[FPackageFileSummary] = None
        self._linker: Optional[core_linkers.ULinkerLoad] = None
        self._name_table: List[FName] = []
        self._imports: List[FObjectImport] = []
        self._exports: List[FObjectExport] = []

        self._fully_loaded: bool = False
        self._source_package: Optional["UPackage"] = None

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
        self._package_path = path.rstrip("/\\")

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

        # core/linkers.py owns the on-disk format (summary, name/import/export
        # tables, all AR_INDEX-based); UPackage only wraps its tables.
        linker = core_linkers.load_package(full_path)
        if linker is None:
            GLog.serialize(f"Failed to load package {filename}")
            return None

        summary = linker.summary
        package = UPackage(filename)
        package._linker = linker
        package._summary = summary
        package._file_version = summary.get_file_version()
        package._licensee_version = summary.get_file_version_licensee()
        package._guid = summary.guid
        package._flags = summary.package_flags
        package._filename = full_path
        package._name_table = list(linker.name_map)
        package._imports = list(linker.import_map)
        package._exports = list(linker.export_map)

        self._loaded_packages[filename] = package

        GLog.serialize(
            f"Loaded package: {filename} ({package.get_export_count()} exports)"
        )
        return package

    def _deserialize_exports(self, package: UPackage, ar: FArchive) -> None:
        """Deserialize exported objects from package archive"""
        # Object references resolve through the linker that read the tables.
        ar._loading = True
        ar._linker = package._linker

        # Deserialize each exported object
        for exp in package._exports:
            # Seek to object's serialized data
            ar.seek(exp.serial_offset)

            # Determine object class from export entry
            class_index = exp.class_index
            if class_index == 0:
                # Index 0 means UObject (usually indicates an error or placeholder)
                continue

            # For now, we'll create placeholder objects
            # Full implementation would resolve class_index to actual UClass
            # and instantiate the correct object type
            name = exp.object_name.name
            if name.lower().endswith("_tex") or name.lower().endswith("texture"):
                # Likely a texture
                texture = UTexture()
                texture._name = exp.object_name
                texture._package = package
                texture.serialize(ar)  # This will deserialize texture properties
                exp.obj = texture
            elif "level" in name.lower():
                # Likely a level
                from ..engine.level import ULevel

                level = ULevel()
                level._name = exp.object_name
                level._package = package
                level.serialize_level(ar)  # This will deserialize level data
                exp.obj = level
            else:
                # Generic object - create UObject placeholder
                obj = UObject()
                obj._name = exp.object_name
                obj._package = package
                # Skip serialization for now
                exp.obj = obj

    def get_texture(
        self, package_name: str, texture_name: str
    ) -> Optional["UTextureAsset"]:
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
            if exp.object_name.name != texture_name:
                continue
            if not is_texture_export(package._linker, exp):
                continue
            texture = load_texture(package._linker, exp)
            texture._package = package_name
            self._texture_cache[cache_key] = texture
            return texture

        return None

    def get_texture_rgba(self, package_name: str, texture_name: str) -> Optional[Any]:
        """Load texture and decode mip 0 through its palette to (V, U, 4)
        uint8 RGBA; None for textures without stored pixels."""
        texture = self.get_texture(package_name, texture_name)
        if not texture:
            return None
        return texture_to_rgba(texture)

    def get_sound(self, package_name: str, sound_name: str) -> Optional["USoundAsset"]:
        """Load sound from package"""
        cache_key = f"{package_name}.{sound_name}"
        if cache_key in self._sound_cache:
            return self._sound_cache[cache_key]

        package = self.load_package(package_name)
        if not package:
            return None

        for exp in package._exports:
            if exp.object_name.name == sound_name:
                sound = USound()
                sound._name = FName(sound_name)
                sound._package = package_name
                self._sound_cache[cache_key] = sound
                return sound

        return None

    def get_mesh(self, package_name: str, mesh_name: str) -> Optional["UMeshAsset"]:
        """Load mesh from package"""
        cache_key = f"{package_name}.{mesh_name}"
        if cache_key in self._mesh_cache:
            return self._mesh_cache[cache_key]

        package = self.load_package(package_name)
        if not package:
            return None

        for exp in package._exports:
            if exp.object_name.name == mesh_name:
                mesh = UMesh()
                mesh._name = FName(mesh_name)
                mesh._package = package_name
                self._mesh_cache[cache_key] = mesh
                return mesh

        return None

    def load_level(self, level_name: str) -> Optional[UPackage]:
        """Load level package (.unr file)

        Args:
            level_name: Level name (e.g., "DM-Turbine", "CTF-Command")
        """
        if not level_name.endswith(".unr"):
            level_name = level_name + ".unr"

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
