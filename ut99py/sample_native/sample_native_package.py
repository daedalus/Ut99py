"""Port of SampleNativePackage/Inc/SampleNativePackage.h (sample native package).

Defines SAMPLENATIVEPACKAGE_API glue for mixing UnrealScript and C++ code.
"""

from __future__ import annotations

SAMPLENATIVEPACKAGE_API = "DLL_EXPORT"


def AUTO_INITIALIZE_REGISTRANTS_SAMPLENATIVEPACKAGE() -> None:
    pass
