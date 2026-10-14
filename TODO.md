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
- [x] `core/linkers.py` tag bug fixed (`0x9E2A83C` → `PACKAGE_FILE_TAG`) and
      the guid/generations block reads real INTs.
- [x] `Core/Inc/UnLinker.h` struct serializers → `core/linkers.py`:
      `FPackageFileSummary` (incl. the oldver heritage path),
      `FGenerationInfo`, `FObjectExport`, `FObjectImport`, plus `AR_INDEX`.
      `ULinkerLoad` is now itself the archive the tables run against (it
      initialises its `FArchive` base and delegates `read`/`seek`/`tell` to the
      file reader), so `FObjectExport`/`FObjectImport` `operator<<` land
      1-to-1: compact `ClassIndex`/`SuperIndex`/`SerialSize`/`SerialOffset`,
      plain `INT` `PackageIndex`/`ObjectFlags`, `FName` references via
      `ULinkerLoad::operator<<(FName&)` resolving through the file name table
      with the C++ bounds check. `_load_name_table` decodes real entries
      (size-prefixed from `VER_SIZED_NAME_TABLE`, NUL-terminated below).
- [x] `Core/Inc/UnTemplate.h` serializers → `FArchive` in `core/system.py`:
      `TArray` (`:435`, plus the `TArray<BYTE>` raw specialization at `:686`) and
      `FString` (`:1403`). `str` is now dispatched, and the old no-op
      `serialize_str` stub is gone. `AR_INDEX` (`UnArc.h:234`) moved next to the
      class it belongs to; `core/linkers.py` imports it.
- [x] `FArchive.count_bytes` (`UnArc.h:37`) as the no-op the file archives use.

## Next
- [ ] `ULinkerLoad::operator<<(UObject*&)` / `IndexToObject` (needs
      `CreateExport`/`CreateImport`, i.e. the `UClass` construction path) and
      `ULinkerSave::operator<<(FName&/UObject*&)` (needs a live `Saver`).
- [ ] `engine/mesh.py`: `UMesh`/`ULodMesh` still hold plain `List[...]` and
      their `FMesh*` structs have no serializers, so `ar << self.verts` dies in
      `_serialize`. Needs the real `UMesh::Serialize` (Engine/Src is absent from
      the source drop) plus element types passed to `serialize_tarray`.
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
- `FArchive.serialize_str` reconstructs `operator<<(FArchive&, FString&)`
  (`UnTemplate.h:1403` is `CORE_API`, body in `Core.lib`) as NUL-terminated
  one-byte characters per `Help/PACKAGES.md:656`; `engine/ut_reader.py` decodes
  the same layout.
- `FArchive.serialize_tarray` takes an explicit `element` factory and
  `element_size`, because Python arrays carry no `T`; the C++ picks between the
  two paths with `sizeof(T)`. Loading a non-empty array without `element`
  raises rather than guess. `count_bytes` is a no-op here (only the memory
  archive overrides it) and gets `ArrayNum`, not the C++ `ArrayMax`.
- `core/linkers.py` `_load_name_table` reads and discards each name's INT32
  flags: the Python `FName` has no flags field (C++ keeps them on `FNameEntry`
  for the linker's own bookkeeping). The entry string layout follows
  `engine/ut_reader.py`; `FNameEntry::operator<<` is in the prebuilt `Core.lib`.
- `ULinkerLoad` does not push the summary's file version into `FArchive._ver`
  (`ULinkerLoad::ULinkerLoad` is in `Core.lib`), so `ar.ver()` reports the
  default `PACKAGE_FILE_VERSION` during object serialization.
- `engine/assets.py` has a third header/table decoder that still reads UTF-16
  `FString`s for names (UT99 uses ANSI). Reconcile it onto `core/linkers.py`.
- `assets.py FPackageFileSummary.serialize` reads `PackageFlags` only when
  `file_version >= 68`; C++ reads it unconditionally (see `UnLinker.h`).
