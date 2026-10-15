"""Tests for Core/Inc/UnCoreNet.h inline members (core/net.py)."""

from ut99py.core.net import (
    FClassNetCache,
    FFieldNetCache,
    FPackageInfo,
    FPropertyRetirement,
    serialize_class_net_cache_ptr,
)
from ut99py.core.types import INDEX_NONE, TArray


def _cache(fields_base, names, super_cache=None):
    """Build a FClassNetCache with contiguous indices starting at fields_base."""
    cache = FClassNetCache()
    cache._fields_base = fields_base
    cache._super = super_cache
    cache._fields = TArray()
    for offset, name in enumerate(names):
        entry = FFieldNetCache(name, fields_base + offset)
        cache._fields.add(entry)
        cache._field_map[name] = entry
    return cache


def test_get_max_index_adds_base_and_count():
    # UnCoreNet.h:35: return FieldsBase + Fields.Num().
    cache = _cache(5, ["a", "b", "c"])
    assert cache.get_max_index() == 8


def test_get_rep_condition_count_returns_the_field():
    # UnCoreNet.h:39.
    cache = FClassNetCache()
    cache._rep_condition_count = 7
    assert cache.get_rep_condition_count() == 7


def test_get_from_field_walks_the_super_chain():
    # UnCoreNet.h:43: the field may live on any ancestor.
    base = _cache(0, ["a", "b"])
    sub = _cache(2, ["c"], super_cache=base)
    assert sub.get_from_field("c") is sub._fields[0]
    assert sub.get_from_field("a") is base._fields[0]
    assert sub.get_from_field("b") is base._fields[1]
    assert sub.get_from_field("missing") is None


def test_get_from_index_resolves_contiguous_ranges():
    # UnCoreNet.h:53: [FieldsBase, FieldsBase+Num) selects within that cache.
    base = _cache(0, ["a", "b"])
    sub = _cache(2, ["c"], super_cache=base)
    assert sub.get_from_index(0) is base._fields[0]
    assert sub.get_from_index(1) is base._fields[1]
    assert sub.get_from_index(2) is sub._fields[0]
    assert sub.get_from_index(3) is None
    assert sub.get_from_index(-1) is None


def test_class_net_cache_ptr_operator_is_a_noop():
    # UnCoreNet.h:132: the operator returns Ar unchanged.
    cache = FClassNetCache()
    assert serialize_class_net_cache_ptr("ARCHIVE", cache) == "ARCHIVE"


def test_property_retirement_ctor_defaults_packet_ids():
    # UnCoreNet.h:145: both packet ids default to INDEX_NONE.
    retired = FPropertyRetirement()
    assert retired.in_packet_id == INDEX_NONE
    assert retired.out_packet_id == INDEX_NONE


def test_package_info_holds_unloaded_defaults():
    info = FPackageInfo()
    assert info.linker is None
    assert info.file_size == 0
    assert info.object_base == 0
    assert info.package_flags == 0
