# TODO — UT99 port

Source of truth: `~/code/Ut99PubSrc` (read-only).

## Done
- [x] `Core/Inc/UnMath.h` → `ut99py/core/types.py` (vectors, rotators, quats,
      matrices, coords, geometry free functions, global trig tables).
- [x] `Core/Inc/UnObjVer.h` → `ut99py/core/objver.py` (version constants, wired
      into `engine/ut_reader.py` and `engine/assets.py`).
- [x] `Core/Inc/UnNames.h` → `ut99py/core/names.py` (EName + `HARDCODED_NAMES`
      index→string table + probe range).
- [x] `Core/Inc/UnArc.h` → `FArchive` in `core/system.py`: status flags and
      accessors, `__lshift__`/`__rshift__` dispatch, the primitive friend
      operators (BYTE/WORD/DWORD/INT/FLOAT/QWORD-as-double), `FGuid`,
      `FCompactIndex`, `serialize_bits`, and the virtual `serialize_name` /
      `serialize_object` hooks. Direction (`_loading`/`_saving`) is set by
      `FArchiveFileReader`/`FArchiveMemoryReader`/`FArchiveFileWriter` as in
      `FFileManagerLinux.h`.
- [x] `FCompactIndex` serializer (declared in `UnArc.h:216`, impl in
      `Core.lib`) rewritten to the real format from `Help/PACKAGES.md`;
      `encode` now guards the C++ save-time mismatch, `decode` added.
- [x] `core/linkers.py` tag bug fixed (`0x9E2A83C` → `PACKAGE_FILE_TAG`,
      read as uint32) and the guid/generations block reads real INTs.

## Next
- [ ] `core/linkers.py` `_load_name_table`/`_load_import_table`/
      `_load_export_table` still use the linker `<<FName` operator against the
      on-disk name/import/export tables, which are not FName references.
      `engine/ut_reader.py` already decodes the real layout (size-prefixed names
      + `int` flags; compact indices for Class/Super/SerialSize/SerialOffset and
      a plain `int` PackageIndex) — reconcile the two.
- [ ] `Core/Inc/UnTemplate.h` `TArray`/`FString` operators (needed by
      `engine/mesh.py`) and `Core/Inc/UnLinker.h` `ULinkerLoad`/`ULinkerSave`
      `MapName`/`MapObject` + `FObjectExport`/`FObjectImport` serializers.
- [ ] `Core/Inc/UnObjBas.h` QWORD/SQWORD operators (currently only `double`).
- [ ] `Core/Inc/UnFile.h` → file manager / `FArchiveFileReader`.
- [ ] `Core/Inc/UnObj.h` gaps in `ut99py/core/objects.py`.
- [ ] `Core/Inc/UnClass.h`, `UnScript.h` → property/script metaclasses.
- [ ] `Core/Inc/UnCoreNet.h` → `ut99py/core/net.py` (FArchive net serialization).

## Known deviations to reconcile
- Python `NAME_*` in `core/types.py` are `FName` objects, not the C++ `EName`
  ints. Keep for compatibility; `core/names.py` supplies the numeric enum +
  index→string table the linker needs.
- `FArchive.serialize_name`/`serialize_object` raise `NotImplementedError`
  where the C++ virtuals return `*this`; a silent no-op would desynchronise the
  stream when the subclass override is missing.
- `FArchive.serialize` primitives are chosen by the operand's runtime type, so
  a bare Python `int` serialises as `INT` (4 bytes). Other widths need the
  explicit `serialize_byte`/`serialize_word`/`serialize_dword` methods, since
  Python has no static type to overload on. QWORD/SQWORD reuse
  `serialize_double`.
- `FCompactIndex`/`ut_reader._read_compact_index` are two implementations of
  the same format; `FCompactIndex.decode` is the verified one.
- `assets.py FPackageFileSummary.serialize` reads `PackageFlags` only when
  `file_version >= 68`; C++ reads it unconditionally (see `UnLinker.h`).
