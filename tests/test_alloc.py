"""Tests for FMalloc/FMallocAnsi (Core.h:210-220, FMallocAnsi.h).

FMallocAnsi hands out real C-library pointers, represented as int
addresses via ctypes; the tests exercise actual malloc/realloc/free.
"""

import ctypes

import pytest

from ut99py.core.system import FMalloc, FMallocAnsi


def test_base_interface_is_abstract():
    # All seven methods are pure virtual in Core.h:214-219.
    base = FMalloc()
    calls = (
        lambda: base.malloc(4),
        lambda: base.realloc(0, 4),
        lambda: base.free(0),
        lambda: base.dump_allocs(),
        lambda: base.heap_check(),
        lambda: base.init(),
        lambda: base.exit(),
    )
    for call in calls:
        with pytest.raises(NotImplementedError):
            call()


def test_malloc_write_free():
    m = FMallocAnsi()
    ptr = m.malloc(16)
    assert ptr != 0
    ctypes.memset(ptr, 0xAB, 16)
    assert ctypes.string_at(ptr, 16) == b"\xab" * 16
    m.free(ptr)


def test_malloc_zero_size_fails():
    # check(Size>0) (FMallocAnsi.h:18).
    with pytest.raises(ValueError):
        FMallocAnsi().malloc(0)


def test_malloc_accepts_tag():
    # Tag is only used by C++ unguardf diagnostics.
    assert FMallocAnsi().malloc(4, "Test") != 0


def test_realloc_grows_and_preserves():
    m = FMallocAnsi()
    ptr = m.malloc(8)
    ctypes.memset(ptr, 0x5A, 8)
    grown = m.realloc(ptr, 64)
    assert ctypes.string_at(grown, 8) == b"\x5a" * 8
    m.free(grown)


def test_realloc_null_pointer_mallocs():
    # `else if( NewSize )` branch (FMAllocAnsi.h:34-37).
    m = FMallocAnsi()
    ptr = m.realloc(0, 8)
    assert ptr != 0
    m.free(ptr)


def test_realloc_zero_size_frees():
    # `else` branch: free(Ptr), Result=NULL (FMallocAnsi.h:39-43).
    m = FMallocAnsi()
    ptr = m.malloc(8)
    assert m.realloc(ptr, 0) == 0


def test_realloc_negative_size_fails():
    # check(NewSize>=0) (FMallocAnsi.h:27).
    with pytest.raises(ValueError):
        FMallocAnsi().realloc(0, -1)


def test_free_null_is_noop():
    FMallocAnsi().free(0)


def test_dump_allocs_logs_disabled(capsys):
    # debugf(NAME_Exit, "Allocation checking disabled")
    # (FMallocAnsi.h:53-58); debugf is unported, so it goes to GLog.
    FMallocAnsi().dump_allocs()
    assert "Allocation checking disabled" in capsys.readouterr().out


def test_heap_check_is_noop():
    # The C++ body runs only under _MSC_VER (FMallocAnsi.h:62-69).
    FMallocAnsi().heap_check()


def test_init_exit_are_noops():
    m = FMallocAnsi()
    m.init()
    m.exit()
