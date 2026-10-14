# TODO — UT99 port

Source of truth: `~/code/Ut99PubSrc` (read-only).

## Done
- [x] `Core/Inc/UnMath.h` → `ut99py/core/types.py` (vectors, rotators, quats,
      matrices, coords, geometry free functions, global trig tables).
- [x] `Core/Inc/UnObjVer.h` → `ut99py/core/objver.py` (version constants, wired
      into `engine/ut_reader.py` and `engine/assets.py`).
- [x] `Core/Inc/UnNames.h` → `ut99py/core/names.py` (EName + `HARDCODED_NAMES`
      index→string table + probe range).

## Next
- [ ] `Core/Inc/UnArc.h` → `FArchive` operators. **Blocks `core/linkers.py`.**
      `ULinkerLoad` calls `ar << x` / `ar >> x`, but `FArchive` defines no
      `__lshift__`/`__rshift__`, so every `load_package()` fails at
      `except Exception`. Port `Serialize`/`ByteOrderSerialize` + the primitive
      overloads (ANSICHAR/BYTE/SBYTE/_WORD/SWORD/DWORD/INT/FLOAT/QWORD/SQWORD,
      FTime, FCompactIndex) and the TArray/FString overloads from
      `UnTemplate.h`.
- [ ] Bug found while wiring (fix with the UnArc.h port + a regression test):
      `core/linkers.py:118` compares the raw 4 tag *bytes* against the literal
      `0x9E2A83C` — one hex digit short of `0x9E2A83C1`, and the wrong type.
      Use `PACKAGE_FILE_TAG` and `int.from_bytes(...)`.
- [ ] `Core/Inc/UnFile.h` → file manager / `FArchiveFileReader`.
- [ ] `Core/Inc/UnObj.h` gaps in `ut99py/core/objects.py`.
- [ ] `Core/Inc/UnClass.h`, `UnScript.h` → property/script metaclasses.
- [ ] `Core/Inc/UnCoreNet.h` → `ut99py/core/net.py` (FArchive net serialization).

## Known deviations to reconcile
- Python `NAME_*` in `core/types.py` are `FName` objects, not the C++ `EName`
  ints. Keep for compatibility; `core/names.py` supplies the numeric enum +
  index→string table the linker needs.
- `assets.py FPackageFileSummary.serialize` reads `PackageFlags` only when
  `file_version >= 68`; C++ reads it unconditionally (see `UnLinker.h`).
