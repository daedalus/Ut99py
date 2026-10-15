"""Core objects: UObject, UClass, UStruct, UProperty

Enums and inline object-model logic are ported from Core/Inc/UnObjBas.h,
Core/Inc/UnType.h and Core/Inc/UnClass.h. The class construction path
(StaticAllocateObject, UClass::Bind, property Link) lives in the prebuilt
Core.lib and is reconstructed or left stubbed; each case says so.
"""

from typing import TYPE_CHECKING, Type, Optional, Any, ClassVar, Iterator
from abc import ABC
from dataclasses import dataclass
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
    from .system import FArchive


# ---------------------------------------------------------------------------
# Core enums (Core/Inc/UnObjBas.h). These carry the bits that reach the file:
# FPackageFileSummary.PackageFlags and FObjectExport.ObjectFlags.
# ---------------------------------------------------------------------------

# ELoadFlags (UnObjBas.h:16).
LOAD_None = 0x0000
LOAD_NoFail = 0x0001
LOAD_NoWarn = 0x0002
LOAD_Throw = 0x0008
LOAD_Verify = 0x0010
LOAD_AllowDll = 0x0020
LOAD_DisallowFiles = 0x0040
LOAD_NoVerify = 0x0080
LOAD_Forgiving = 0x1000
LOAD_Quiet = 0x2000
LOAD_NoRemap = 0x4000
LOAD_Propagate = 0

# EPackageFlags (UnObjBas.h:35).
PKG_AllowDownload = 0x0001
PKG_ClientOptional = 0x0002
PKG_ServerSideOnly = 0x0004
PKG_BrokenLinks = 0x0008
PKG_Unsecure = 0x0010
PKG_Need = 0x8000

# EClassFlags (UnObjBas.h:67).
CLASS_Abstract = 0x00001
CLASS_Compiled = 0x00002
CLASS_Config = 0x00004
CLASS_Transient = 0x00008
CLASS_Parsed = 0x00010
CLASS_Localized = 0x00020
CLASS_SafeReplace = 0x00040
CLASS_RuntimeStatic = 0x00080
CLASS_NoExport = 0x00100
CLASS_NoUserCreate = 0x00200
CLASS_PerObjectConfig = 0x00400
CLASS_NativeReplication = 0x00800
CLASS_Inherit = (
    CLASS_Transient
    | CLASS_Config
    | CLASS_Localized
    | CLASS_SafeReplace
    | CLASS_RuntimeStatic
    | CLASS_PerObjectConfig
)
CLASS_RecompilerClear = (
    CLASS_Inherit | CLASS_Abstract | CLASS_NoExport | CLASS_NativeReplication
)

# EPropertyFlags (UnObjBas.h:92).
CPF_Edit = 0x00000001
CPF_Const = 0x00000002
CPF_Input = 0x00000004
CPF_ExportObject = 0x00000008
CPF_OptionalParm = 0x00000010
CPF_Net = 0x00000020
CPF_ConstRef = 0x00000040
CPF_Parm = 0x00000080
CPF_OutParm = 0x00000100
CPF_SkipParm = 0x00000200
CPF_ReturnParm = 0x00000400
CPF_CoerceParm = 0x00000800
CPF_Native = 0x00001000
CPF_Transient = 0x00002000
CPF_Config = 0x00004000
CPF_Localized = 0x00008000
CPF_Travel = 0x00010000
CPF_EditConst = 0x00020000
CPF_GlobalConfig = 0x00040000
CPF_OnDemand = 0x00100000
CPF_New = 0x00200000
CPF_NeedCtorLink = 0x00400000
CPF_ParmFlags = (
    CPF_OptionalParm
    | CPF_Parm
    | CPF_OutParm
    | CPF_SkipParm
    | CPF_ReturnParm
    | CPF_CoerceParm
)
CPF_PropagateFromStruct = CPF_Const | CPF_Native | CPF_Transient

# EObjectFlags (UnObjBas.h:126). Several bits carry two names by design.
RF_Transactional = 0x00000001
RF_Unreachable = 0x00000002
RF_Public = 0x00000004
RF_TagImp = 0x00000008
RF_TagExp = 0x00000010
RF_SourceModified = 0x00000020
RF_TagGarbage = 0x00000040
RF_NeedLoad = 0x00000200
RF_HighlightedName = 0x00000400
RF_EliminateObject = 0x00000400
RF_InSingularFunc = 0x00000800
RF_RemappedName = 0x00000800
RF_Suppress = 0x00001000
RF_StateChanged = 0x00001000
RF_InEndState = 0x00002000
RF_Transient = 0x00004000
RF_Preloading = 0x00008000
RF_LoadForClient = 0x00010000
RF_LoadForServer = 0x00020000
RF_LoadForEdit = 0x00040000
RF_Standalone = 0x00080000
RF_NotForClient = 0x00100000
RF_NotForServer = 0x00200000
RF_NotForEdit = 0x00400000
RF_Destroyed = 0x00800000
RF_NeedPostLoad = 0x01000000
RF_HasStack = 0x02000000
RF_Native = 0x04000000
RF_Marked = 0x08000000
RF_ErrorShutdown = 0x10000000
RF_DebugPostLoad = 0x20000000
RF_DebugSerialize = 0x40000000
RF_DebugDestroy = 0x80000000
RF_ContextFlags = RF_NotForClient | RF_NotForServer | RF_NotForEdit
RF_LoadContextFlags = RF_LoadForClient | RF_LoadForServer | RF_LoadForEdit
RF_Load = (
    RF_ContextFlags
    | RF_LoadContextFlags
    | RF_Public
    | RF_Standalone
    | RF_Native
    | RF_SourceModified
    | RF_Transactional
    | RF_HasStack
)
RF_Keep = RF_Native | RF_Marked
RF_ScriptMask = (
    RF_Transactional
    | RF_Public
    | RF_Transient
    | RF_NotForClient
    | RF_NotForServer
    | RF_NotForEdit
)

# EGotoState (UnObjBas.h:57).
GOTOSTATE_NotFound = 0
GOTOSTATE_Success = 1
GOTOSTATE_Preempted = 2

# EPropertyPortFlags (UnType.h:11).
PPF_Localized = 1
PPF_Delimited = 2

# Zero aliases used as default arguments in this package; the header spells
# "no flags" as 0 rather than naming it.
RF_NoFlags = 0
CPF_NoFlags = 0


class UObject(ABC):
    _all_objects: ClassVar[TArray['UObject']] = TArray()
    _gc_lock_count: ClassVar[int] = 0
    
    # ARRAY_COUNT(GObjHash) (UnObjBas.h:478).
    OBJECT_HASH_COUNT: ClassVar[int] = 4096
    
    _app_entry: ClassVar[Optional['UObject']] = None
    
    def __init__(self):
        self._outer: Optional['UObject'] = None
        self._name: FName = FName("None")
        self._internal_index: int = INDEX_NONE
        self._flags: int = 0
        self._index: int = INDEX_NONE
        self.__post_init__()
    
    def __post_init__(self):
        # Registration into the global object table (GObjObjects); the C++
        # does this via UObject::AddObject (UnObjBas.h:494), with no
        # StaticAllocateObject in the port yet. UObject::GetIndex
        # (UnObjBas.h:651) reports the slot assigned here.
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
    
    def get_index(self) -> int:
        """UObject::GetIndex (UnObjBas.h:651): the object's index in the global
        object table GObjObjects, which the port assigns in __post_init__ and
        exposes as internal_index."""
        return self._internal_index
    
    def get_outer_most(self) -> 'UObject':
        obj = self
        while obj._outer:
            obj = obj._outer
        return obj
    
    def is_a(self, other_class: Type['UObject']) -> bool:
        return isinstance(self, other_class)
    
    def is_in(self, some_outer: Optional['UObject']) -> bool:
        """UObject::IsIn (UnType.h:545): walk the Outer chain. A NULL Outer
        matches everything, as in the C++."""
        outer = self._outer
        while outer is not None:
            if outer is some_outer:
                return True
            outer = outer._outer
        return some_outer is None
    
    @staticmethod
    def get_object_hash(obj_name: FName, outer_index: int) -> int:
        """UObject::GetObjectHash (UnObjBas.h:586)."""
        return (obj_name.get_index() ^ outer_index) & (
            UObject.OBJECT_HASH_COUNT - 1
        )
    
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


@dataclass
class FDependency:
    """FDependency (UnClass.h:39): one incremental-compilation dependency.
    `class_` carries the C++ `Class` member (a Python keyword)."""

    class_: Optional['UClass'] = None
    deep: bool = False
    script_text_crc: int = 0


class UField(UObject):
    # enum {HASH_COUNT = 256} (UnClass.h:103).
    HASH_COUNT: ClassVar[int] = 256
    
    def __init__(self):
        super().__init__()
        self._super_field: Optional['UField'] = None
        self._next: Optional['UField'] = None
        self._hash_next: Optional['UField'] = None
    
    @property
    def super_field(self) -> Optional['UField']:
        return self._super_field
    
    @super_field.setter
    def super_field(self, value: Optional['UField']) -> None:
        self._super_field = value
    
    @property
    def next(self) -> Optional['UField']:
        return self._next
    
    @next.setter
    def next(self, value: Optional['UField']) -> None:
        self._next = value

    @property
    def hash_next(self) -> Optional['UField']:
        return self._hash_next

    @hash_next.setter
    def hash_next(self, value: Optional['UField']) -> None:
        self._hash_next = value


class UEnum(UField):
    def __init__(self):
        super().__init__()
        self._names = TArray()
    
    def get_super_enum(self) -> Optional['UEnum']:
        """UEnum::GetSuperEnum (UnClass.h:397); checkSlow note in
        UStruct.get_super_struct."""
        super_field = self._super_field
        if super_field is not None and not isinstance(super_field, UEnum):
            raise TypeError(
                f"{self!r} SuperField is {type(super_field).__name__}, not UEnum"
            )
        return super_field


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
    
    def get_super_const(self) -> Optional['UConst']:
        """UConst::GetSuperConst (UnClass.h:527); checkSlow note in
        UStruct.get_super_struct."""
        super_field = self._super_field
        if super_field is not None and not isinstance(super_field, UConst):
            raise TypeError(
                f"{self!r} SuperField is {type(super_field).__name__}, not UConst"
            )
        return super_field


# Boundary to align class properties on (UnClass.h:14).
PROPERTY_ALIGNMENT = 4


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
    
    def get_super_struct(self) -> Optional['UStruct']:
        """UStruct::GetSuperStruct (UnClass.h:267). The C++ checkSlow that
        SuperField is a UStruct runs only in debug builds; Python always checks
        it, since there is no release build to fall back to."""
        super_field = self._super_field
        if super_field is not None and not isinstance(super_field, UStruct):
            raise TypeError(
                f"{self!r} SuperField is {type(super_field).__name__}, not UStruct"
            )
        return super_field
    
    def get_inheritance_super(self) -> Optional['UStruct']:
        """UStruct::GetInheritanceSuper (UnClass.h:234)."""
        return self.get_super_struct()
    
    def get_properties_size(self) -> int:
        """UStruct::GetPropertiesSize (UnClass.h:240): overrides the UField
        virtual (whose body is in Core.lib)."""
        return self._property_size
    
    def set_properties_size(self, new_size: int) -> None:
        """UStruct::SetPropertiesSize (UnClass.h:248)."""
        self._property_size = new_size
    
    def get_name_cpp(self) -> str:
        """UStruct::GetNameCPP (UnClass.h:261): the C++ name prefixed with 'F'."""
        return f"F{self.name}"
    
    def is_child_of(self, some_base: Optional['UStruct']) -> bool:
        """UStruct::IsChildOf (UnClass.h:252)."""
        struct: Optional[UStruct] = self
        while struct is not None:
            if struct is some_base:
                return True
            struct = struct.get_super_struct()
        return False
    
    def field_iterator(self, field_class: Type[UField]) -> Iterator[UField]:
        """TFieldIterator<T> (UnClass.h:135): this struct's Children, then each
        inheritance super's Children, keeping only instances of field_class."""
        struct: Optional[UStruct] = self
        while struct is not None:
            field = struct._children
            while field is not None:
                if isinstance(field, field_class):
                    yield field
                field = field._next
            struct = struct.get_inheritance_super()
    
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
    
    def get_inheritance_super(self) -> Optional[UStruct]:
        """UFunction::GetInheritanceSuper (UnClass.h:317): functions do not
        inherit properties."""
        return None
    
    def merge_bools(self) -> bool:
        """UFunction::MergeBools (UnClass.h:316)."""
        return False
    
    def get_super_function(self) -> Optional['UFunction']:
        """UFunction::GetSuperFunction (UnClass.h:321); checkSlow note in
        UStruct.get_super_struct."""
        super_field = self._super_field
        if super_field is not None and not isinstance(super_field, UFunction):
            raise TypeError(
                f"{self!r} SuperField is {type(super_field).__name__}, "
                "not UFunction"
            )
        return super_field


class UState(UStruct):
    def __init__(self):
        super().__init__()
        self._actor_key: int = 0
        self._label_table: TArray() = TArray()
    
    def get_inheritance_super(self) -> Optional[UStruct]:
        """UState::GetInheritanceSuper (UnClass.h:361)."""
        return self.get_super_state()
    
    def merge_bools(self) -> bool:
        """UState::MergeBools (UnClass.h:360)."""
        return True
    
    def get_super_state(self) -> Optional['UState']:
        """UState::GetSuperState (UnClass.h:365); checkSlow note in
        UStruct.get_super_struct."""
        super_field = self._super_field
        if super_field is not None and not isinstance(super_field, UState):
            raise TypeError(
                f"{self!r} SuperField is {type(super_field).__name__}, not UState"
            )
        return super_field


class UClass(UStruct):
    _class_map: ClassVar[dict[str, Type['UClass']]] = {}
    
    def __init__(self):
        super().__init__()
        self._defaults: list[bytes] = []
        self._dependencies: list['FDependency'] = []
    
    def get_inheritance_super(self) -> Optional[UStruct]:
        """UClass::GetInheritanceSuper (UnClass.h:452)."""
        return self.get_super_class()
    
    def merge_bools(self) -> bool:
        """UClass::MergeBools (UnClass.h:451)."""
        return True
    
    def get_name_cpp(self) -> str:
        """UClass::GetNameCPP (UnClass.h:453): 'A' when the class or an ancestor
        is named Actor, otherwise 'U'."""
        cls: Optional[UClass] = self
        while cls is not None:
            if str(cls.name).casefold() == "actor":
                break
            cls = cls.get_super_class()
        prefix = "A" if cls is not None else "U"
        return f"{prefix}{self.name}"
    
    def get_super_class(self) -> Optional['UClass']:
        """UClass::GetSuperClass (UnClass.h:477). Unlike the other GetSuper*
        accessors, the C++ has no checkSlow here, so the port does not check
        either; the result is whatever SuperField holds."""
        return self._super_field
    
    def add_dependency(self, in_class: 'UClass', deep: bool) -> None:
        """UClass::AddDependency (UnClass.h:466). The C++ loop has no break, so
        every matching record is updated, and only a missing record is added."""
        found = False
        for dep in self._dependencies:
            if dep.class_ is in_class:
                dep.deep |= deep
                found = True
        if not found:
            self._dependencies.append(FDependency(in_class, deep))
    
    def get_default_object(self) -> UObject:
        """UClass::GetDefaultObject (UnClass.h:483): the C++ returns
        `(UObject*)&Defaults(0)` -- a raw pointer into the Defaults byte buffer
        reinterpreted as a UObject. The port has no per-type value model to
        materialise one, so this is unimplemented rather than fabricated."""
        raise NotImplementedError(
            "UClass.GetDefaultObject needs a Python value model for the raw "
            "Defaults buffer (see TODO.md object-model gaps)"
        )
    
    def get_default_actor(self) -> UObject:
        """UClass::GetDefaultActor (UnClass.h:490): the C++ returns the same
        `&Defaults(0)` pointer as GetDefaultObject, cast to AActor*."""
        return self.get_default_object()
    
    def static_config_name(self) -> FName:
        return FName(f"{str(self.name)}_Default")
    
    def __repr__(self) -> str:
        return f"UClass({self.get_full_name()})"


class UProperty(UField):
    _property_type: ClassVar[Optional[FName]] = None
    
    # ElementSize is assigned per type by UProperty::Link (Core.lib); the
    # abstract base declares no size of its own.
    _element_size: ClassVar[int] = 0
    
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
        """UProperty::GetSize (UnType.h:71)."""
        return self._array_dim * self._element_size
    
    def should_serialize_value(self, ar: 'FArchive') -> bool:
        """UProperty::ShouldSerializeValue (UnType.h:77): native properties are
        never serialized here, and transient ones only in non-persistent
        archives."""
        skip = bool(self._property_flags & CPF_Native) or (
            bool(self._property_flags & CPF_Transient) and ar.is_persistent()
        )
        return not skip
    
    def get_min_alignment(self) -> int:
        return 1
    
    def is_a_native_type(self) -> bool:
        return False


class UByteProperty(UProperty):
    _property_type = NAME_ByteProperty
    _element_size = 1


class UIntProperty(UProperty):
    _property_type = NAME_IntProperty
    _element_size = 4


class UBoolProperty(UProperty):
    _property_type = NAME_BoolProperty
    _element_size = 4
    
    def __init__(self):
        super().__init__()
        self._bit_mask: int = 0


class UFloatProperty(UProperty):
    _property_type = NAME_FloatProperty
    _element_size = 4


class UObjectProperty(UProperty):
    _property_type = NAME_ObjectProperty
    _element_size = 4
    
    def __init__(self):
        super().__init__()
        self._property_class: Optional[UClass] = None


class UNameProperty(UProperty):
    _property_type = NAME_NameProperty
    _element_size = 4


class UStrProperty(UProperty):
    _property_type = FName("StrProperty")
    _element_size = 16


class UStructProperty(UProperty):
    _property_type = NAME_StructProperty
    
    def __init__(self):
        super().__init__()
        self._struct: Optional[UStruct] = None
    
    def get_size(self) -> int:
        # UStructProperty::Link sets ElementSize = Struct->PropertiesSize.
        return self._array_dim * (
            self._struct._property_size if self._struct else 0
        )


class UArrayProperty(UProperty):
    _property_type = NAME_ArrayProperty
    _element_size = 16
    
    def __init__(self):
        super().__init__()
        self._inner: Optional[UProperty] = None


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