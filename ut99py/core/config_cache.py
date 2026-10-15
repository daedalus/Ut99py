"""Port of Core/Inc/FConfigCacheIni.h (INI-style config cache).

Classes:
- FConfigCacheIni : FArchive
- FConfigCacheIniEntry : config entry
- FConfigCacheIniGroup : group of entries
- FConfigCacheIniParser : parser
"""

from __future__ import annotations


class FConfigCacheIniEntry:
    def __init__(self) -> None:
        self.Key: str = ""
        self.Value: str = ""


class FConfigCacheIniGroup:
    def __init__(self) -> None:
        self.Name: str = ""
        self.Entries: list[FConfigCacheIniEntry] = []


class FConfigCacheIniParser:
    def __init__(self) -> None:
        self.Groups: list[FConfigCacheIniGroup] = []


class FConfigCacheIni:
    def __init__(self) -> None:
        self.Parser: FConfigCacheIniParser = FConfigCacheIniParser()
