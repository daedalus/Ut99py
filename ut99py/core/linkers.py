from typing import Optional, List, Dict, Any
from ut99py.core import FName, FString, UObject, UStruct, FArchive, FArchiveFileReader
from ut99py.core.types import FTime, FGuid, FVector, FRotator


class FObjectExport:
    def __init__(self):
        self.class_index: int = 0
        self.super_index: int = 0
        self.package_index: int = 0
        self.object_name: FName = FName()
        self.object_flags: int = 0
        self.serial_size: int = 0
        self.serial_offset: int = 0
        self.obj: Optional[UObject] = None
        self._hash_next: int = -1


class FObjectImport:
    def __init__(self):
        self.class_package: FName = FName()
        self.class_name: FName = FName()
        self.package_index: int = 0
        self.object_name: FName = FName()
        self.x_object: Optional[UObject] = None
        self.source_linker: Optional['ULinkerLoad'] = None
        self.source_index: int = -1


class FGenerationInfo:
    def __init__(self, export_count: int = 0, name_count: int = 0):
        self.export_count: int = export_count
        self.name_count: int = name_count


class FPackageFileSummary:
    def __init__(self):
        self.tag: int = 0
        self.file_version: int = 0
        self.package_flags: int = 0
        self.name_count: int = 0
        self.name_offset: int = 0
        self.export_count: int = 0
        self.export_offset: int = 0
        self.import_count: int = 0
        self.import_offset: int = 0
        self.guid: FGuid = FGuid()
        self.generations: List[FGenerationInfo] = []

    def get_file_version(self) -> int:
        return self.file_version & 0xffff

    def get_file_version_licensee(self) -> int:
        return (self.file_version >> 16) & 0xffff


class ULinker(UObject):
    def __init__(self):
        super().__init__()
        self.linker_root: Optional[UObject] = None
        self.summary: FPackageFileSummary = FPackageFileSummary()
        self.name_map: List[FName] = []
        self.import_map: List[FObjectImport] = []
        self.export_map: List[FObjectExport] = []
        self.success: bool = False
        self.filename: str = ""
        self._context_flags: int = 0

    def get_import_full_name(self, i: int) -> str:
        if 0 <= i < len(self.import_map):
            imp = self.import_map[i]
            return f"{imp.class_package}.{imp.object_name}"
        return ""

    def get_export_full_name(self, i: int, fake_root: Optional[str] = None) -> str:
        if 0 <= i < len(self.export_map):
            exp = self.export_map[i]
            name = exp.object_name
            if fake_root:
                return f"{fake_root}.{name}"
            return name
        return ""


class ULinkerLoad(ULinker, FArchive):
    LOADF_None: int = 0x00000000
    LOADF_NoFail: int = 0x00000001
    LOADF_Quiet: int = 0x00000002
    LOADF_FindFirst: int = 0x00000004
    LOADF_Merge: int = 0x00000008
    LOADF_Existing: int = 0x00000010
    LOADF_NoVerify: int = 0x00000020
    LOADF_DisallowShaderCompiling: int = 0x00000040

    def __init__(self, parent: Optional[UObject], filename: str, load_flags: int = 0):
        super().__init__()
        self.load_flags: int = load_flags
        self.verified: bool = False
        self.export_hash: List[int] = [0] * 256
        self.lazy_loaders: List['FLazyLoader'] = []
        self.loader: Optional[FArchive] = None
        self.filename = filename

        try:
            self.loader = FArchiveFileReader(filename)
            self._load_summary()
            self.success = True
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            self.success = False

    def _load_summary(self) -> None:
        if not self.loader:
            return

        ar = self.loader
        self.summary.tag = ar.read(4)
        if self.summary.tag != 0x9E2A83C:
            raise ValueError(f"Invalid package tag: {hex(self.summary.tag)}")

        self.summary.file_version = int.from_bytes(ar.read(4), 'little')
        self.summary.package_flags = int.from_bytes(ar.read(4), 'little')
        self.summary.name_count = int.from_bytes(ar.read(4), 'little')
        self.summary.name_offset = int.from_bytes(ar.read(4), 'little')
        self.summary.export_count = int.from_bytes(ar.read(4), 'little')
        self.summary.export_offset = int.from_bytes(ar.read(4), 'little')
        self.summary.import_count = int.from_bytes(ar.read(4), 'little')
        self.summary.import_offset = int.from_bytes(ar.read(4), 'little')

        if self.summary.get_file_version() >= 68:
            self.summary.guid = FGuid()
            ar << self.summary.guid
            gen_count = 0
            ar << gen_count
            self.summary.generations = [FGenerationInfo() for _ in range(gen_count)]
            for gen in self.summary.generations:
                ar << gen.export_count << gen.name_count

        self._load_name_table()
        self._load_import_table()
        self._load_export_table()

    def _load_name_table(self) -> None:
        if not self.loader or self.summary.name_offset == 0:
            return
        
        self.loader.seek(self.summary.name_offset)
        self.name_map = []
        for _ in range(self.summary.name_count):
            name = FName()
            self.loader >> name
            self.name_map.append(name)

    def _load_import_table(self) -> None:
        if not self.loader or self.summary.import_offset == 0:
            return
        
        self.loader.seek(self.summary.import_offset)
        self.import_map = []
        for _ in range(self.summary.import_count):
            imp = FObjectImport()
            self.loader >> imp.class_package >> imp.class_name >> imp.package_index >> imp.object_name
            self.import_map.append(imp)

    def _load_export_table(self) -> None:
        if not self.loader or self.summary.export_offset == 0:
            return
        
        self.loader.seek(self.summary.export_offset)
        self.export_map = []
        for _ in range(self.summary.export_count):
            exp = FObjectExport()
            self.loader >> exp.class_index >> exp.super_index >> exp.package_index >> exp.object_name >> exp.object_flags >> exp.serial_size
            if exp.serial_size > 0:
                self.loader >> exp.serial_offset
            self.export_map.append(exp)

    def verify(self) -> None:
        if self.verified:
            return
        
        for i in range(len(self.import_map)):
            self.verify_import(i)
        
        self.verified = True

    def verify_import(self, i: int) -> None:
        if not (0 <= i < len(self.import_map)):
            return
        
        imp = self.import_map[i]
        if imp.source_index >= 0:
            return
        
        pkg_name = imp.class_package
        obj_name = imp.object_name
        
        print(f"Resolving import: {pkg_name}.{obj_name}")

    def load_all_objects(self) -> None:
        for exp in self.export_map:
            if exp.obj is None and exp.serial_size > 0:
                self.create(exp.package_index, None, exp.object_name, 0, False)

    def find_export_index(self, class_name: FName, class_package: FName, object_name: FName, package_index: int) -> int:
        for i, exp in enumerate(self.export_map):
            if (exp.object_name == object_name and 
                exp.package_index == package_index):
                return i
        return -1

    def create(self, object_class: Optional[type], object_name: FName, load_flags: int, checked: bool) -> Optional[UObject]:
        return None

    def preload(self, obj: UObject) -> None:
        pass

    def seek(self, pos: int) -> None:
        if self.loader:
            self.loader.seek(pos)

    def tell(self) -> int:
        if self.loader:
            return self.loader.tell()
        return 0

    def total_size(self) -> int:
        if self.loader:
            return self.loader.size()
        return 0

    def serialize(self, data: bytes, length: int) -> int:
        if self.loader:
            return self.loader.read(length)
        return 0


class ULinkerSave(ULinker, FArchive):
    def __init__(self, parent: Optional[UObject], filename: str):
        super().__init__()
        self.saver: Optional[FArchive] = None
        self.filename = filename
        self.object_indices: List[int] = []
        self.name_indices: List[int] = []

    def map_name(self, name: FName) -> int:
        for i, n in enumerate(self.name_map):
            if n == name:
                return i
        return -1

    def map_object(self, obj: UObject) -> int:
        for i, exp in enumerate(self.export_map):
            if exp.obj is obj:
                return i
        return -1

    def seek(self, pos: int) -> None:
        if self.saver:
            self.saver.seek(pos)

    def tell(self) -> int:
        if self.saver:
            return self.saver.tell()
        return 0


class FLazyLoader:
    def __init__(self, link: ULinkerLoad, index: int):
        self.linker = link
        self.index = index
        self.data: Optional[bytes] = None

    def load(self) -> bytes:
        if self.data:
            return self.data
        
        exp = self.linker.export_map[self.index]
        if exp.serial_size > 0 and self.linker.loader:
            self.linker.seek(exp.serial_offset)
            self.data = self.linker.loader.read(exp.serial_size)
        
        return self.data or b''


def load_package(filename: str, parent: Optional[UObject] = None, load_flags: int = 0) -> Optional[ULinkerLoad]:
    try:
        linker = ULinkerLoad(parent, filename, load_flags)
        if linker.success:
            return linker
    except Exception as e:
        print(f"Error loading package {filename}: {e}")
    return None


__all__ = [
    'FObjectExport',
    'FObjectImport',
    'FGenerationInfo',
    'FPackageFileSummary',
    'ULinker',
    'ULinkerLoad',
    'ULinkerSave',
    'FLazyLoader',
    'load_package',
]