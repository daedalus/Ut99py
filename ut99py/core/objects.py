"""Core objects: UObject, UClass, UStruct, UProperty"""

from typing import TYPE_CHECKING, Type, Optional, Any, ClassVar
from abc import ABC
from dataclasses import dataclass, field
import sys

from .types import FName, FString, TArray, INDEX_NONE

from .types import (
    NAME_ByteProperty, NAME_IntProperty, NAME_BoolProperty,
    NAME_FloatProperty, NAME_ObjectProperty, NAME_NameProperty,
    NAME_StringProperty, NAME_ClassProperty, NAME_ArrayProperty,
    NAME_StructProperty, NAME_VectorProperty, NAME_RotatorProperty,
    ENAME_Log,
)

if TYPE_CHECKING:
    from .package import UPackage


class UObject(ABC):
    _all_objects: ClassVar[TArray['UObject']] = TArray()
    _gc_lock_count: ClassVar[int] = 0
    
    _app_entry: ClassVar[Optional['UObject']] = None
    
    def __init__(self):
        self._outer: Optional['UObject'] = None
        self._name: FName = FName("None")
        self._internal_index: int = INDEX_NONE
        self._flags: int = 0
        self._index: int = INDEX_NONE
    
    def __post_init__(self):
        UObject._all_objects.append(self)
        self._internal_index = len(UObject._all_objects) - 1
        if UObject._app_entry is None:
            UObject._app_entry = self
    
    @property
    def outer(self) -> Optional['UObject']:
        return self._outer
    
    @property
    def name(self) -> FName:
        return self._name
    
    @property
    def internal_index(self) -> int:
        return self._internal_index
    
    @property
    def flags(self) -> int:
        return self._flags
    
    def get_full_name(self) -> str:
        full_name = str(self._name)
        if self._outer:
            full_name = f"{self._outer.get_full_name()}.{full_name}"
        return full_name
    
    def get_outer_most(self) -> 'UObject':
        obj = self
        while obj._outer:
            obj = obj._outer
        return obj
    
    def is_a(self, other_class: Type['UObject']) -> bool:
        return isinstance(self, other_class)
    
    def destroy(self) -> bool:
        raise NotImplementedError
    
    def shutdown(self) -> None:
        pass
    
    @classmethod
    def get_class(cls) -> 'UClass':
        raise NotImplementedError
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.get_full_name()}>"


class USubsystem(UObject):
    def __init__(self):
        super().__init__()


class USystem(USubsystem):
    def __init__(self):
        super().__init__()
        self._config_cache = None
        self._language = FName("None")
        self._titles = TArray()
    
    def init(self) -> None:
        pass
    
    def exit(self) -> None:
        pass


class UField(UObject):
    def __init__(self):
        super().__init__()
        self._next: Optional['UField'] = None
    
    @property
    def next(self) -> Optional['UField']:
        return self._next
    
    @next.setter
    def next(self, value: Optional['UField']) -> None:
        self._next = value


class UEnum(UField):
    def __init__(self):
        super().__init__()
        self._names = TArray()


class UConst(UField):
    def __init__(self):
        super().__init__()
        self._value = FString()
    
    @property
    def value(self) -> FString:
        return self._value
    
    @value.setter
    def value(self, val: FString) -> None:
        self._value = val


class UStruct(UField):
    def __init__(self):
        super().__init__()
        self._children: Optional[UField] = None
        self._property_size: int = 0
        self._min_alignment: int = 0
        self._script: bytes = b''
    
    @property
    def children(self) -> Optional[UField]:
        return self._children
    
    @children.setter
    def children(self, value: Optional[UField]) -> None:
        self._children = value
    
    def get_script_size(self) -> int:
        return len(self._script)
    
    def serialize(self, ar: 'FArchive') -> None:
        pass


class UFunction(UStruct):
    def __init__(self):
        super().__init__()
        self._func: int = 0
        self._num_parms: int = 0
        self._parms_size: int = 0
        self._return_value_offset: int = 0
        self._native: bool = False
        self._operator: int = 0
        self._inline_doc: str = ""
    
    @property
    def func(self) -> int:
        return self._func
    
    @property
    def native(self) -> bool:
        return self._native


class UState(UStruct):
    def __init__(self):
        super().__init__()
        self._actor_key: int = 0
        self._label_table: TArray() = TArray()


RF_NoFlags = 0x00000000
RF_Public = 0x00000001
RF_Standalone = 0x00000002
RF_HasStack = 0x00000004
RF_Marked = 0x00000008
RF_InEdit = 0x00000020
RF_Archetype = 0x00000040
RF_TextureTransient = 0x00000080
RF_NONPINKER_SCRIPT = 0x00000100
RF_ScriptMask = 0x00000100
RF_DisallowServerSidePhysics = 0x00000400

RF_LoadForClient = 0x00010000
RF_LoadForServer = 0x00020000
RF_LoadForEdit = 0x00040000

RF_OuterMask = 0xF8000000
RF_IsChunkMask = 0x07FFFFFF

class UClass(UStruct):
    _class_map: ClassVar[dict[str, Type['UClass']]] = {}
    
    def __init__(self):
        super().__init__()
        self._default_object: Optional[UObject] = None
        self._defaults: list[bytes] = []
    
    def get_default_object(self) -> UObject:
        if self._default_object is None:
            self._default_object = object.__new__(self)
        return self._default_object
    
    def static_config_name(self) -> FName:
        return FName(f"{str(self.name)}_Default")
    
    def __repr__(self) -> str:
        return f"UClass({self.get_full_name()})"


class UProperty(UField):
    _property_type: ClassVar[Optional[FName]] = None
    
    def __init__(self):
        super().__init__()
        self._array_dim: int = 1
        self._property_flags: int = 0
        self._category: FName = FName("None")
        self._array_inner_property: Optional['UProperty'] = None
    
    @property
    def array_dim(self) -> int:
        return self._array_dim
    
    @property
    def property_flags(self) -> int:
        return self._property_flags
    
    def get_size(self) -> int:
        return self._array_dim * 4
    
    def get_min_alignment(self) -> int:
        return 1
    
    def is_a_native_type(self) -> bool:
        return False


class UByteProperty(UProperty):
    _property_type = NAME_ByteProperty
    
    def get_size(self) -> int:
        return 1


class UIntProperty(UProperty):
    _property_type = NAME_IntProperty
    
    def get_size(self) -> int:
        return 4


class UBoolProperty(UProperty):
    _property_type = NAME_BoolProperty
    
    def __init__(self):
        super().__init__()
        self._bit_mask: int = 0
    
    def get_size(self) -> int:
        return 4


class UFloatProperty(UProperty):
    _property_type = NAME_FloatProperty
    
    def get_size(self) -> int:
        return 4


class UObjectProperty(UProperty):
    _property_type = NAME_ObjectProperty
    
    def __init__(self):
        super().__init__()
        self._property_class: Optional[UClass] = None
    
    def get_size(self) -> int:
        return 4


class UNameProperty(UProperty):
    _property_type = NAME_NameProperty
    
    def get_size(self) -> int:
        return 4


class UStrProperty(UProperty):
    _property_type = FName("StrProperty")
    
    def get_size(self) -> int:
        return 16


class UStructProperty(UProperty):
    _property_type = NAME_StructProperty
    
    def __init__(self):
        super().__init__()
        self._struct: Optional[UStruct] = None
    
    def get_size(self) -> int:
        return self._struct._property_size if self._struct else 0


class UArrayProperty(UProperty):
    _property_type = NAME_ArrayProperty
    
    def __init__(self):
        super().__init__()
        self._inner: Optional[UProperty] = None
    
    def get_size(self) -> int:
        return 16


CPF_NoFlags = 0x00000000
CPF_EditConst = 0x00000001
CPF_Const = 0x00000002
CPF_Export = 0x00000004
CPF_EditInline = 0x00000008
CPF_EditInlineUse = 0x00000010
CPF_BlueprintReadOnly = 0x00000020
CPF_Net = 0x00000100
CPF_EditAnywhere = 0x00000200
CPF_ArchetypeSStable = 0x00000400
CPF_Transient = 0x00000800
CPF_Config = 0x00001000
CPF_Localized = 0x00008000
CPF_Travel = 0x00010000
CPF_RepRetry = 0x00100000


class ULinker(UObject):
    def __init__(self):
        super().__init__()
        self._linker_verbose: int = 0
    
    def convert_index(self, index: int) -> int:
        return -1
    
    def convert_name(self, name: FName) -> FName:
        return name


class ULinkerLoad(ULinker):
    def __init__(self):
        super().__init__()
        self._exports: TArray() = TArray()
        self._imports: TArray() = TArray()
        self._depends: TArray() = TArray()


class ULinkerSave(ULinker):
    def __init__(self):
        super().__init__()
        self._producer: Optional[UPackage] = None


class UPackage(UObject):
    def __init__(self, filename: str = ""):
        super().__init__()
        self._guid: 'FGuid' = None
        self._flags: int = 0
        self._source_linker: Optional[ULinkerLoad] = None
        self._detach_linker: bool = False
        self._filename: str = filename


class UPackageMap(UObject):
    def __init__(self):
        super().__init__()
        self._stack: TArray() = TArray()
    
    def serialize_object(self, obj: UObject) -> bool:
        return False


class UTextBuffer(UObject):
    def __init__(self):
        super().__init__()
        self._data: str = ""
        self._pos: int = 0
        self._line: int = 0
    
    def get_text(self) -> str:
        return self._data
    
    def __repr__(self) -> str:
        return f"UTextBuffer({self._data[:50]}...)"


class UFactory(UObject):
    def __init__(self):
        super().__init__()
        self._factory_class: Optional[UClass] = None
    
    @property
    def factory_class(self) -> Optional[UClass]:
        return self._factory_class


class UExporter(UObject):
    def __init__(self):
        super().__init__()
        self._exporter_class: Optional[UClass] = None
    
    def export_object(self, obj: UObject) -> bool:
        return False


class FOutputDevice:
    def serialize(self, v: str, event: FName = ENAME_Log) -> None:
        pass
    
    def flush(self) -> None:
        pass
    
    def shutdown(self) -> None:
        pass
    
    def is_tty(self) -> bool:
        return False


class FFeedbackContext(FOutputDevice):
    def __init__(self):
        self._map: bool = True
    
    def status_update(self, current: int, max: int, label: str = "") -> None:
        pass
    
    def progress_start(self, max: int, label: str = "") -> None:
        pass
    
    def progress_update(self, current: int = 0) -> None:
        pass
    
    def progress_end(self) -> None:
        pass


def app_error(text: str) -> None:
    print(f"ERROR: {text}", file=sys.stderr)
    raise SystemExit(1)


def app_warning(text: str) -> None:
    print(f"WARNING: {text}", file=sys.stderr)