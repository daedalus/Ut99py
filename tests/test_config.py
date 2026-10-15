"""FConfigCacheIni (ut99py/core/system.py): INI read/write.

Expected values come from FConfigCacheIni.h: Read splits `[Section]` headers and
`Key=Value` pairs after the first `=`, stripping one surrounding quote pair
(:46-66); Write emits `[Section]\\r\\n`, `Key=Value\\r\\n` per pair, then a blank
line (:79-85); the numeric accessors use appAtoi/appAtof and appStricmp/"True"
(:286-345).
"""

import os

from ut99py.core.system import (
    FConfigCacheIni,
    FConfigFile,
    FConfigSection,
)

SAMPLE = (
    "[Section1]\r\n"
    "Key1=Value1\r\n"
    'Key2="quoted"\r\n'
    "\r\n"
    "[Section2]\r\n"
    "A=1\r\n"
    "B=True\r\n"
    "C=2.5\r\n"
)


def _ini(tmp_path, name="test.ini", text=SAMPLE):
    path = tmp_path / name
    path.write_bytes(text.encode("latin-1"))
    return str(path)


def test_read_parses_sections_and_pairs(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    assert cache.get_string("Section1", "Key1", ini) == "Value1"
    assert cache.get_string("Section2", "B", ini) == "True"
    assert cache.get_section("Section2", ini) == "A=1\0B=True\0C=2.5\0\0"


def test_read_strips_surrounding_quotes(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    assert cache.get_string("Section1", "Key2", ini) == "quoted"


def test_last_line_without_terminator(tmp_path):
    ini = _ini(tmp_path, text="[S]\r\nk=v")
    cache = FConfigCacheIni()
    assert cache.get_string("S", "k", ini) == "v"


def test_orphan_lines_ignored(tmp_path):
    # A pair before any section, and a pair with no '=', is dropped (:43-67).
    ini = _ini(tmp_path, text="orphan=1\r\n[S]\r\nnovalue\r\nk=v\r\n")
    cache = FConfigCacheIni()
    assert cache.get_string("orphan", "orphan", ini) is None
    assert cache.get_string("S", "novalue", ini) is None
    assert cache.get_string("S", "k", ini) == "v"


def test_duplicate_keys_last_wins(tmp_path):
    # TMapBase::Find walks the LIFO bucket, so the newest pair wins
    # (UnTemplate.h:1718); iteration still yields both in file order.
    ini = _ini(tmp_path, text="[S]\r\nk=1\r\nk=2\r\n")
    cache = FConfigCacheIni()
    assert cache.get_string("S", "k", ini) == "2"
    assert cache.get_section("S", ini) == "k=1\0k=2\0\0"


def test_missing_returns_none(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    assert cache.get_string("Section1", "Nope", ini) is None
    assert cache.get_string("Nope", "Key1", ini) is None
    assert cache.get_string("Section1", "Key1", str(tmp_path / "no.ini")) is None


def test_get_str_returns_empty_on_missing(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    assert cache.get_str("Section1", "Key1", ini) == "Value1"
    assert cache.get_str("Section1", "Nope", ini) == ""


def test_get_section_missing_is_none(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    assert cache.get_section("Nope", ini) is None


def test_get_int_parses_leading_number(tmp_path):
    ini = _ini(tmp_path, text="[S]\r\nI=12abc\r\nN=abc\r\n")
    cache = FConfigCacheIni()
    assert cache.get_int("S", "I", ini) == 12
    assert cache.get_int("S", "N", ini) == 0
    assert cache.get_int("S", "Missing", ini) is None


def test_get_float_parses_leading_number(tmp_path):
    ini = _ini(tmp_path, text="[S]\r\nF=2.5e3xyz\r\nN=abc\r\n")
    cache = FConfigCacheIni()
    assert cache.get_float("S", "F", ini) == 2500.0
    assert cache.get_float("S", "N", ini) == 0.0


def test_get_bool_cpp_semantics(tmp_path):
    # GetBool: "True" (case-insensitive) or appAtoi(Text)==1 (:334-341).
    ini = _ini(
        tmp_path,
        text="[S]\r\nT=True\r\nL=true\r\nOne=1\r\nTwo=2\r\nZero=0\r\n",
    )
    cache = FConfigCacheIni()
    assert cache.get_bool("S", "T", ini) is True
    assert cache.get_bool("S", "L", ini) is True
    assert cache.get_bool("S", "One", ini) is True
    assert cache.get_bool("S", "Two", ini) is False
    assert cache.get_bool("S", "Zero", ini) is False
    assert cache.get_bool("S", "Missing", ini) is None


def test_set_string_marks_dirty(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    cache.find(ini, False)
    cache.set_string("Section1", "New", "x", ini)
    assert cache.find(ini, False).dirty is True
    assert cache.get_string("Section1", "New", ini) == "x"


def test_set_string_case_only_noop(tmp_path):
    # appStricmp equal -> the else-if body is skipped, so the stored value and
    # Dirty are untouched (FConfigCacheIni.h:219-223).
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    cache.set_string("Section1", "Key1", "value1", ini)
    assert cache.find(ini, False).dirty is False
    assert cache.get_string("Section1", "Key1", ini) == "Value1"


def test_set_float_six_decimals(tmp_path):
    ini = _ini(tmp_path, text="")
    cache = FConfigCacheIni()
    cache.set_float("S", "F", 1.5, ini)
    assert cache.get_string("S", "F", ini) == "1.500000"


def test_set_int_and_bool_format(tmp_path):
    ini = _ini(tmp_path, text="")
    cache = FConfigCacheIni()
    cache.set_int("S", "I", 42, ini)
    cache.set_bool("S", "B", True, ini)
    assert cache.get_string("S", "I", ini) == "42"
    assert cache.get_string("S", "B", ini) == "True"


def test_flush_writes_dirty_file(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    cache.find(ini, False)
    cache.set_string("Section1", "New", "x", ini)
    cache.flush(False)
    expected = (
        "[Section1]\r\nKey1=Value1\r\nKey2=quoted\r\nNew=x\r\n\r\n"
        "[Section2]\r\nA=1\r\nB=True\r\nC=2.5\r\n\r\n"
    )
    assert (tmp_path / "test.ini").read_bytes() == expected.encode("latin-1")


def test_flush_skips_clean_file(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    cache.find(ini, False)  # Read leaves Dirty false
    (tmp_path / "test.ini").write_bytes(b"junk")
    cache.flush(False)
    assert (tmp_path / "test.ini").read_bytes() == b"junk"


def test_detach_suppresses_write(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    cache.find(ini, False)
    cache.set_string("S", "k", "v", ini)  # dirty
    cache.detach(ini)
    (tmp_path / "test.ini").write_bytes(b"junk")
    cache.flush(False)
    assert (tmp_path / "test.ini").read_bytes() == b"junk"


def test_find_creates_missing_file(tmp_path):
    name = str(tmp_path / "new.ini")
    cache = FConfigCacheIni()
    cfg = cache.find(name, True)
    assert isinstance(cfg, FConfigFile)
    assert not os.path.exists(name)  # creation is lazy; only Flush writes
    assert cache.find(name, False) is cfg


def test_find_missing_returns_none(tmp_path):
    cache = FConfigCacheIni()
    assert cache.find(str(tmp_path / "nope.ini"), False) is None


def test_find_appends_ini_extension(tmp_path):
    _ini(tmp_path, name="app.ini")
    cache = FConfigCacheIni()
    assert cache.get_string("Section1", "Key1", str(tmp_path / "app")) == "Value1"


def test_find_translates_user_system(tmp_path):
    system = _ini(tmp_path, name="UT.ini")
    user = _ini(tmp_path, name="Player.ini", text="[U]\r\nk=v\r\n")
    cache = FConfigCacheIni()
    cache.init(system, user)
    assert cache.get_string("Section1", "Key1") == "Value1"  # None -> SystemIni
    assert cache.get_string("Section2", "A", "System.ini") == "1"
    assert cache.get_string("U", "k", "User.ini") == "v"


def test_get_section_private_force(tmp_path):
    ini = str(tmp_path / "p.ini")
    cache = FConfigCacheIni()
    sec = cache.get_section_private("New", True, False, ini)
    assert isinstance(sec, FConfigSection)
    assert cache.find(ini, False).dirty is True
    assert cache.get_section_private("Other", False, False, ini) is None


def test_empty_section_clears(tmp_path):
    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    cache.empty_section("Section2", ini)
    assert cache.get_string("Section2", "A", ini) is None
    assert cache.get_section("Section2", ini) == "\0"  # section kept, empty


def test_round_trip_flush_reload(tmp_path):
    ini = str(tmp_path / "rt.ini")
    cache = FConfigCacheIni()
    cache.set_string("A", "x", "1", ini)
    cache.set_string("A", "y", "2", ini)
    cache.set_string("B", "z", "3", ini)
    cache.flush(False)

    reloaded = FConfigCacheIni()
    assert reloaded.get_string("A", "x", ini) == "1"
    assert reloaded.get_string("A", "y", ini) == "2"
    assert reloaded.get_string("B", "z", ini) == "3"
    assert reloaded.get_section("A", ini) == "x=1\0y=2\0\0"


def test_flush_read_clears_cache(tmp_path):
    name = str(tmp_path / "ghost.ini")
    cache = FConfigCacheIni()
    cache.find(name, True)
    cache.flush(True)
    assert cache.find(name, False) is None


def test_dump_lists_cached_files(tmp_path):
    class Recorder:
        def __init__(self):
            self.lines = []

        def serialize(self, value, event=None):
            self.lines.append(value)

    ini = _ini(tmp_path)
    cache = FConfigCacheIni()
    cache.find(ini, False)
    rec = Recorder()
    cache.dump(rec)
    assert rec.lines[0] == "Files map:"
    assert any("2 sections" in line for line in rec.lines)


def test_factory_returns_instance():
    assert isinstance(FConfigCacheIni.factory(), FConfigCacheIni)
