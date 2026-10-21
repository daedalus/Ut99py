"""Port of Setup/Inc/Setup.h (Filer public definitions).

Classes: USetupObject, USetupGroup, USetupProduct, USetupDefinition, USetupDefinitionWindows, FInstallPoll.
"""

from __future__ import annotations


class FInstallPoll:
    def Poll(
        self,
        label: str,
        local_bytes: int,
        local_total: int,
        running_bytes: int,
        total_bytes: int,
    ) -> bool:
        return False


class USetupObject:
    pass


class USetupGroup:
    pass


class USetupProduct:
    pass


class USetupDefinition:
    pass


class USetupDefinitionWindows(USetupDefinition):
    pass


# Setup constants
PER_FILE_OVERHEAD = 65536 + 16384
PER_INSTALL_OVERHEAD = 16 * 1024 * 1024
MANIFEST_FILE = "Manifest"
MANIFEST_EXT = ".ini"
SFX_STUB = "RunSFX.exe"
MOD_EXT = ".umod"
SETUP_INI = MANIFEST_FILE + MANIFEST_EXT
