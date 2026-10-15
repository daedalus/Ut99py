"""Pin the object-model enums and inline accessors to the Core headers.

Every expected value below is read straight from Core/Inc/UnObjBas.h,
Core/Inc/UnType.h and Core/Inc/UnClass.h. The enum bits matter because
FObjectExport.ObjectFlags and FPackageFileSummary.PackageFlags are written to
disk; tests/test_real_packages.py checks real packages against them.
"""

import pytest

from ut99py.core.objects import (
    CLASS_Abstract,
    CLASS_Config,
    CLASS_Inherit,
    CLASS_NativeReplication,
    CLASS_NoExport,
    CLASS_PerObjectConfig,
    CLASS_RecompilerClear,
    CLASS_RuntimeStatic,
    CLASS_SafeReplace,
    CLASS_Transient,
    CPF_CoerceParm,
    CPF_Config,
    CPF_Const,
    CPF_Edit,
    CPF_Net,
    CPF_Native,
    CPF_OptionalParm,
    CPF_OutParm,
    CPF_Parm,
    CPF_ParmFlags,
    CPF_PropagateFromStruct,
    CPF_ReturnParm,
    CPF_SkipParm,
    CPF_Transient,
    CPF_Travel,
    FDependency,
    LOAD_AllowDll,
    LOAD_DisallowFiles,
    LOAD_Forgiving,
    LOAD_NoFail,
    LOAD_NoRemap,
    LOAD_NoVerify,
    LOAD_NoWarn,
    LOAD_Propagate,
    LOAD_Quiet,
    LOAD_Throw,
    LOAD_Verify,
    PKG_AllowDownload,
    PKG_BrokenLinks,
    PKG_ClientOptional,
    PKG_Need,
    PKG_ServerSideOnly,
    PKG_Unsecure,
    PPF_Delimited,
    PPF_Localized,
    PROPERTY_ALIGNMENT,
    RF_ContextFlags,
    RF_Destroyed,
    RF_HasStack,
    RF_Keep,
    RF_Load,
    RF_LoadContextFlags,
    RF_LoadForClient,
    RF_LoadForEdit,
    RF_LoadForServer,
    RF_Marked,
    RF_Native,
    RF_NotForClient,
    RF_NotForEdit,
    RF_NotForServer,
    RF_Public,
    RF_ScriptMask,
    RF_SourceModified,
    RF_Standalone,
    RF_Transactional,
    RF_Transient,
    RF_Unreachable,
    UArrayProperty,
    UByteProperty,
    UClass,
    UField,
    UFloatProperty,
    UFunction,
    UIntProperty,
    UObject,
    UProperty,
    UState,
    UStruct,
    UStructProperty,
)
from ut99py.core.system import FArchive
from ut99py.core.types import FName


# --------------------------------------------------------------------------
# Enums.
# --------------------------------------------------------------------------


def test_load_flags_match_the_header():
    # ELoadFlags, UnObjBas.h:16. LOAD_Propagate is spelled 0.
    assert LOAD_NoFail == 0x0001
    assert LOAD_NoWarn == 0x0002
    assert LOAD_Throw == 0x0008
    assert LOAD_Verify == 0x0010
    assert LOAD_AllowDll == 0x0020
    assert LOAD_DisallowFiles == 0x0040
    assert LOAD_NoVerify == 0x0080
    assert LOAD_Forgiving == 0x1000
    assert LOAD_Quiet == 0x2000
    assert LOAD_NoRemap == 0x4000
    assert LOAD_Propagate == 0


def test_package_flags_match_the_header():
    # EPackageFlags, UnObjBas.h:35.
    assert PKG_AllowDownload == 0x0001
    assert PKG_ClientOptional == 0x0002
    assert PKG_ServerSideOnly == 0x0004
    assert PKG_BrokenLinks == 0x0008
    assert PKG_Unsecure == 0x0010
    assert PKG_Need == 0x8000


def test_class_flags_match_the_header():
    # EClassFlags, UnObjBas.h:67.
    assert CLASS_Abstract == 0x00001
    assert CLASS_Config == 0x00004
    assert CLASS_Transient == 0x00008
    assert CLASS_SafeReplace == 0x00040
    assert CLASS_RuntimeStatic == 0x00080
    assert CLASS_NoExport == 0x00100
    assert CLASS_PerObjectConfig == 0x00400
    assert CLASS_NativeReplication == 0x00800
    # UnObjBas.h:84-85.
    assert CLASS_Inherit == 0x4EC
    assert CLASS_RecompilerClear == 0xDED


def test_property_flags_match_the_header():
    # EPropertyFlags, UnObjBas.h:92.
    assert CPF_Edit == 0x00000001
    assert CPF_Const == 0x00000002
    assert CPF_Net == 0x00000020
    assert CPF_Parm == 0x00000080
    assert CPF_Native == 0x00001000
    assert CPF_Transient == 0x00002000
    assert CPF_Config == 0x00004000
    assert CPF_Travel == 0x00010000
    # UnObjBas.h:119-120.
    assert CPF_ParmFlags == (
        CPF_OptionalParm
        | CPF_Parm
        | CPF_OutParm
        | CPF_SkipParm
        | CPF_ReturnParm
        | CPF_CoerceParm
    )
    assert CPF_ParmFlags == 0xF90
    assert CPF_PropagateFromStruct == CPF_Const | CPF_Native | CPF_Transient
    assert CPF_PropagateFromStruct == 0x3002


def test_object_flags_match_the_header():
    # EObjectFlags, UnObjBas.h:126. Note RF_Public is 0x4 here, not 0x1: the
    # bits that reach the file are these, not the UT2003 layout.
    assert RF_Transactional == 0x00000001
    assert RF_Unreachable == 0x00000002
    assert RF_Public == 0x00000004
    assert RF_SourceModified == 0x00000020
    assert RF_Transient == 0x00004000
    assert RF_LoadForClient == 0x00010000
    assert RF_LoadForServer == 0x00020000
    assert RF_LoadForEdit == 0x00040000
    assert RF_Standalone == 0x00080000
    assert RF_NotForClient == 0x00100000
    assert RF_NotForServer == 0x00200000
    assert RF_NotForEdit == 0x00400000
    assert RF_Destroyed == 0x00800000
    assert RF_HasStack == 0x02000000
    assert RF_Native == 0x04000000
    assert RF_Marked == 0x08000000
    # UnObjBas.h:163-167.
    assert RF_ContextFlags == 0x700000
    assert RF_LoadContextFlags == 0x70000
    assert RF_Load == 0x067F0025
    assert RF_Keep == 0x0C000000
    assert RF_ScriptMask == 0x704005


def test_property_port_flags_match_the_header():
    # EPropertyPortFlags, UnType.h:11.
    assert PPF_Localized == 1
    assert PPF_Delimited == 2


def test_property_alignment_matches_the_header():
    # UnClass.h:14.
    assert PROPERTY_ALIGNMENT == 4


# --------------------------------------------------------------------------
# Inline accessors.
# --------------------------------------------------------------------------


def test_fname_get_index_is_stable_and_small():
    # FName::GetIndex (UnName.h:73) is a table index: names are interned, so
    # the same spelling always resolves to the same slot.
    name = FName("Object")
    assert name.get_index() == FName("Object").get_index()
    assert name.get_index() != FName("Actor").get_index()


def test_get_object_hash_uses_the_bucket_count():
    # UObject::GetObjectHash (UnObjBas.h:586):
    # (ObjName.GetIndex() ^ Outer) & (ARRAY_COUNT(GObjHash)-1).
    assert UObject.OBJECT_HASH_COUNT == 4096
    name = FName("Object")
    for outer in (0, 1, 255, 4095, 4096):
        bucket = UObject.get_object_hash(name, outer)
        assert 0 <= bucket < UObject.OBJECT_HASH_COUNT
        assert bucket == (name.get_index() ^ outer) & (4096 - 1)


def test_is_in_walks_the_outer_chain():
    # UObject::IsIn (UnType.h:545). The loop starts at GetOuter(), so an
    # object is never in itself.
    outer = UStruct()
    middle = UStruct()
    inner = UStruct()
    middle._outer = outer
    inner._outer = middle

    assert inner.is_in(outer)
    assert inner.is_in(middle)
    assert not inner.is_in(inner)
    assert not outer.is_in(inner)
    # A NULL Outer matches everything, as the C++ returns SomeOuter==NULL.
    assert inner.is_in(None)


def test_is_child_of_walks_the_super_chain():
    # UStruct::IsChildOf (UnClass.h:252).
    base = UClass()
    derived = UClass()
    derived.super_field = base

    assert derived.is_child_of(base)
    assert derived.is_child_of(derived)
    assert not base.is_child_of(derived)
    assert not base.is_child_of(None)


def test_get_inheritance_super_overrides():
    # UStruct/UClass/UState/UFunction dispatch to their own super accessors
    # (UnClass.h:234, 317, 361, 452).
    base = UClass()
    derived = UClass()
    derived.super_field = base
    assert derived.get_inheritance_super() is base
    assert derived.get_super_class() is base

    state = UState()
    super_state = UState()
    state.super_field = super_state
    assert state.get_inheritance_super() is super_state

    function = UFunction()
    super_function = UFunction()
    function.super_field = super_function
    # UFunction::GetInheritanceSuper returns NULL: functions do not inherit
    # properties, but they do have a super function.
    assert function.get_inheritance_super() is None
    assert function.get_super_function() is super_function


def test_super_accessors_reject_a_wrong_super_field_type():
    # Each GetSuper* with a checkSlow casts SuperField. The C++ only runs the
    # check in debug builds; the port enforces it unconditionally.
    struct = UStruct()
    struct.super_field = UField()  # a UField, not a UStruct
    with pytest.raises(TypeError):
        struct.get_super_struct()
    with pytest.raises(TypeError):
        struct.get_inheritance_super()


def test_get_super_class_does_not_check_the_super_field_type():
    # UClass::GetSuperClass has no checkSlow (UnClass.h:477), so it returns
    # SuperField as-is.
    uclass = UClass()
    wrong = UStruct()
    uclass.super_field = wrong
    assert uclass.get_super_class() is wrong


def test_field_iterator_is_derived_children_then_base_children():
    # TFieldIterator (UnClass.h:135) yields the struct's own Children first,
    # then walks GetInheritanceSuper().
    base = UClass()
    derived = UClass()
    derived.super_field = base

    prop_a = UIntProperty()
    prop_b = UFloatProperty()
    struct_prop = UStructProperty()  # filtered out by field_class
    prop_c = UByteProperty()

    base.children = prop_a
    prop_a.next = prop_b
    derived.children = struct_prop
    struct_prop.next = prop_c

    assert list(derived.field_iterator(UProperty)) == [
        struct_prop,
        prop_c,
        prop_a,
        prop_b,
    ]
    assert list(derived.field_iterator(UStructProperty)) == [struct_prop]


def test_property_get_size_is_array_dim_times_element_size():
    # UProperty::GetSize (UnType.h:71).
    assert UByteProperty().get_size() == 1
    assert UIntProperty().get_size() == 4
    assert UFloatProperty().get_size() == 4
    assert UArrayProperty().get_size() == 16

    array = UIntProperty()
    array._array_dim = 3
    assert array.get_size() == 12


def test_struct_property_size_follows_its_struct():
    # UStructProperty::Link sets ElementSize = Struct->PropertiesSize.
    struct = UStruct()
    struct._property_size = 8
    prop = UStructProperty()
    prop._struct = struct
    assert prop.get_size() == 8

    prop._array_dim = 2
    assert prop.get_size() == 16


def test_should_serialize_value_follows_native_and_transient():
    # UProperty::ShouldSerializeValue (UnType.h:77).
    persistent = FArchive()
    persistent._persistent = True
    transient_archive = FArchive()  # _persistent defaults to False

    def prop(flags):
        p = UIntProperty()
        p._property_flags = flags
        return p

    assert prop(0).should_serialize_value(persistent)
    assert not prop(CPF_Native).should_serialize_value(persistent)
    assert not prop(CPF_Transient).should_serialize_value(persistent)
    assert prop(CPF_Transient).should_serialize_value(transient_archive)


def test_add_dependency_ors_the_deep_flag():
    # UClass::AddDependency (UnClass.h:466).
    owner = UClass()
    other = UClass()

    owner.add_dependency(other, deep=False)
    assert [(d.class_, d.deep) for d in owner._dependencies] == [(other, False)]

    owner.add_dependency(other, deep=True)
    assert len(owner._dependencies) == 1
    assert owner._dependencies[0].deep is True

    third = UClass()
    owner.add_dependency(third, deep=False)
    assert [d.class_ for d in owner._dependencies] == [other, third]


def test_add_dependency_updates_every_matching_record():
    # The C++ loop has no break, so a duplicated record is updated too and no
    # new record is appended.
    owner = UClass()
    other = UClass()
    owner._dependencies = [FDependency(other, False), FDependency(other, False)]

    owner.add_dependency(other, deep=True)

    assert len(owner._dependencies) == 2
    assert [d.deep for d in owner._dependencies] == [True, True]


def test_dependency_defaults_are_zeroed():
    dep = FDependency()
    assert dep.class_ is None
    assert dep.deep is False
    assert dep.script_text_crc == 0
