"""UnFile.h inline character helpers (ut99py/core/file_utils.py).

Expected values come from UnFile.h:260-267 (appToUpper uppercases only 'a'..'z',
appToLower lowercases only 'A'..'Z') and appStrihash (UnFile.h:331).
"""

from ut99py.core.file_utils import (
    appIsAlnum,
    appIsAlpha,
    appIsDigit,
    appStrihash,
    appToLower,
    appToUpper,
)


def test_app_to_upper_uppercases_lowercase_letters():
    assert appToUpper("a") == "A"
    assert appToUpper("z") == "Z"
    assert appToUpper("m") == "M"


def test_app_to_upper_passes_everything_else_through():
    assert appToUpper("A") == "A"
    assert appToUpper("1") == "1"
    assert appToUpper("!") == "!"


def test_app_to_lower_lowercases_uppercase_letters():
    assert appToLower("A") == "a"
    assert appToLower("Z") == "z"
    assert appToLower("M") == "m"


def test_app_to_lower_passes_everything_else_through():
    assert appToLower("a") == "a"
    assert appToLower("1") == "1"
    assert appToLower("!") == "!"


def test_char_class_predicates():
    assert appIsAlpha("a") and appIsAlpha("Z")
    assert not appIsAlpha("0")
    assert appIsDigit("0") and appIsDigit("9")
    assert not appIsDigit("a")
    assert appIsAlnum("a") and appIsAlnum("9")
    assert not appIsAlnum("_")


def test_strihash_is_case_insensitive():
    # appStrihash folds through appToUpper, so case never changes the hash.
    assert appStrihash("Hello") == appStrihash("hELLo")


def test_strihash_depends_on_content():
    assert appStrihash("Hello") != appStrihash("World")
