"""Unreal object/package version constants.

Ported from Core/Inc/UnObjVer.h.
"""

# Earliest engine build that is network compatible with this one.
ENGINE_MIN_NET_VERSION = 400

# Engine build number, for displaying to end users.
ENGINE_VERSION = 430

# Base protocol version to negotiate in network play.
ENGINE_NEGOTIATION_VERSION = 400

# Prevents incorrect files from being loaded.
PACKAGE_FILE_TAG = 0x9E2A83C1

# The current Unrealfile version.
PACKAGE_FILE_VERSION = 69

# Licensee version WORD, packed into the upper two words of the version DWORD.
PACKAGE_FILE_VERSION_LICENSEE = 0x00
VERSION_ENGINE_ONLY = 0x00

# The earliest file version loadable with complete backwards compatibility.
PACKAGE_MIN_VERSION = 60

# Header-layout thresholds.
#
# VER_GUID_AND_GENERATIONS is gated in UnLinker.h: FPackageFileSummary writes
# Guid + Generations only from this file version on (UnLinker.h:148).
VER_GUID_AND_GENERATIONS = 68

# Size-prefixed name-table entries.  Not in UnObjVer.h; matches what UT99
# packages in the wild use (see engine/ut_reader.py).
VER_SIZED_NAME_TABLE = 64
