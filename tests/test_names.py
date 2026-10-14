"""Pin the hardcoded name table to Core/Inc/UnNames.h.

Every expected value below is read straight from the header, so a wrong index in
the port fails here rather than silently mis-resolving a package's name table.
"""

import keyword

from ut99py.core.names import EName, HARDCODED_NAMES, NAME_PROBEMAX, NAME_PROBEMIN


def test_property_type_indices_match_header():
    # REGISTER_NAME(1..15, *Property)
    assert EName.None_ == 0
    assert EName.ByteProperty == 1
    assert EName.IntProperty == 2
    assert EName.BoolProperty == 3
    assert EName.FloatProperty == 4
    assert EName.ObjectProperty == 5
    assert EName.ArrayProperty == 9
    assert EName.StructProperty == 10
    assert EName.FixedArrayProperty == 15


def test_package_indices_match_header():
    assert EName.Core == 20
    assert EName.Engine == 21
    assert EName.Editor == 22
    assert EName.UnrealI == 23
    assert EName.UnrealShare == 24


def test_python_keywords_are_mangled_not_dropped():
    # Header spellings None/True/False collide with Python keywords.
    assert EName.None_ == 0
    assert EName.True_ == 105
    assert EName.False_ == 106
    assert not any(keyword.iskeyword(n) for n in EName.__members__)


def test_message_range_matches_header():
    assert EName.Log == 760
    assert EName.Error == 789
    assert EName.UserPrompt == 794
    assert EName.All == 363
    assert NAME_PROBEMIN == 300
    assert NAME_PROBEMAX == 364


def test_table_spelling_is_exact():
    assert HARDCODED_NAMES[0] == "None"
    assert HARDCODED_NAMES[1] == "ByteProperty"
    assert HARDCODED_NAMES[760] == "Log"
    assert HARDCODED_NAMES[105] == "True"
    assert HARDCODED_NAMES[363] == "All"


def test_every_member_has_a_table_entry():
    missing = [m.name for m in EName if m.value not in HARDCODED_NAMES]
    assert not missing


def test_no_aliased_indices():
    # A duplicate index in the header would alias silently and shrink the table.
    canonical = {m.value for m in EName}
    assert len(EName.__members__) == len(canonical)
    assert len(HARDCODED_NAMES) == len(canonical)
