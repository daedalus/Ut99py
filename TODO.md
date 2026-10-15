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
      operators (BYTE/WORD/DWORD/INT/FLOAT/QWORD/SQWORD), `FGuid`,
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
- [x] Validated against the real install at `/home/dclavijo/Games/UnrealTournament`
      (310 packages, 0 failures): name/import/export tables agree row for row
      with `engine/ut_reader.py`, and both version thresholds are exercised by
      real files — versions 61-66 take the pre-`VER_SIZED_NAME_TABLE` name table
      and the pre-`VER_GUID_AND_GENERATIONS` heritage header, 64 is the boundary,
      68/69 carry guid + generations. Pinned by `tests/test_real_packages.py`
      (skips when the install is absent; `UT99_GAME_DIR` overrides).
- [x] Runaway heritage loop bounded: `UnLinker.h:158` reads `HeritageCount`
      GUIDs from `HeritageOffset` whatever the file claims, so a bogus count
      spins. The port skips the list when it does not fit in the archive.
- [x] `Core/Inc/UnObjBas.h` enums → `core/objects.py`: `ELoadFlags`,
      `EPackageFlags`, `EClassFlags`, `EPropertyFlags`, `EObjectFlags`,
      `EGotoState`, plus `EPropertyPortFlags` (`UnType.h:11`) and
      `PROPERTY_ALIGNMENT` (`UnClass.h:14`). These replaced UE2-style constants
      left by the initial commit; the ousted `RF_Public=0x1` was not the UT99
      value (0x4). `core/__init__.py` re-exports the set and lists it in
      `__all__`.
- [x] `Core/Inc/UnObjBas.h`/`UnType.h`/`UnClass.h` inline logic →
      `core/objects.py`: `UObject.get_object_hash`/`is_in`,
      `UField.SuperField`/`HashNext`/`HASH_COUNT`,
      `UStruct.get_super_struct`/`get_inheritance_super`/`is_child_of`/
      `field_iterator` (`TFieldIterator`), `UClass.get_super_class`/
      `add_dependency` (+`FDependency`), `UEnum.get_super_enum`,
      `UConst.get_super_const`, `UFunction.get_inheritance_super`(NULL)/
      `get_super_function`, `UState.get_super_state`,
      `UProperty.get_size` (`ArrayDim*ElementSize`) / `should_serialize_value`.
      `FName.get_index` (`UnName.h:73`) added for the object hash.
- [x] `FArchive.serialize_qword`/`serialize_sqword` (`UnArc.h:182-191`). The old
      `serialize_double` claimed to be this operator but packed an IEEE-754
      `double`; `QWORD`/`SQWORD` are 64-bit ints (`UnGnuG.h:127,136`).

## Next
- [x] `ULinkerLoad::operator<<(UObject*&)` / `IndexToObject` (UnLinker.h:249-272)
      → `core/linkers.py`: the archive's `_serialize` now reads the compact
      index and resolves it through the export/import tables. `CreateExport`/
      `CreateImport` are structural stubs returning the table entry as the
      placeholder object, because the C++ construction bodies are in Core.lib.
- [ ] `ULinkerSave::operator<<(FName&/UObject*&)` (needs a live `Saver`).
- [ ] `engine/mesh.py`: `UMesh`/`ULodMesh` still hold plain `List[...]` and
      their `FMesh*` structs have no serializers, so `ar << self.verts` dies in
      `_serialize`. Needs the real `UMesh::Serialize` (Engine/Src is absent from
      the source drop) plus element types passed to `serialize_tarray`.
- [x] `Core/Inc/UnFile.h` inline utilities → `core/file_utils.py`: `GCRCTABLE`
      (256-entry IEEE-802.3 CRC-32 table reconstructed from polynomial),
      `appToUpper`/`appToLower`/`appIsAlpha`/`appIsDigit`/`appIsAlnum`
      (line 260-276), `appStrihash` (line 331-345). CORE_API declared
      functions documented as unimplemented (bodies in Core.lib). Validated:
      `len(GCRCTABLE) == 256`; `appStrihash('Hello')` produces consistent hash.
- [ ] `Core/Inc/UnFile.h` → file manager / `FArchiveFileReader` (appFindPackageFile,
      file-path utilities; full CORE_API bodies remain in Core.lib).
- [ ] `ut99py/core/objects.py` object-model gaps (there is no `UnObj.h`; the
      model is `UnObjBas.h` + `UnType.h` + `UnClass.h`):
      `UProperty::Matches`/`Identical` and `UStruct::StructCompare` operate on
      raw pointers and per-type `Identical` bodies that live in `Core.lib`, so
      they need a Python value model before they can be ported faithfully.
      `UClass::GetDefaultObject` still fabricates an empty object rather than
      reading `Defaults(0)`; `UObject::IsA` uses `isinstance` instead of the C++
      `UClass` walk; `UStruct::Link`/`UClass::Bind`/`StaticAllocateObject` are the
      `Core.lib` construction path.
- [x] `Core/Inc/UnCoreNet.h` inline members → `core/net.py`: `FFieldNetCache`
      (UnCoreNet.h:12), `FClassNetCache` inline `GetMaxIndex` (UnCoreNet.h:35) /
      `GetRepConditionCount` (:39) / `GetFromField` (:43) / `GetFromIndex` (:53),
      `FPackageInfo` (:76), the no-op `operator<<(FArchive&,FClassNetCache*)`
      (:132), and `FPropertyRetirement` (:140). The CORE_API ctors and
      `operator<<` bodies remain in Core.lib (documented); the `UPackageMap`
      stub stays in `core/objects.py`. Pinned by `tests/test_net.py`.
- [ ] `Core/Inc/UnClass.h`, `UnScript.h` → property/script metaclasses.

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
  Python has no static type to overload on. `serialize_qword`/`serialize_sqword`
  cover `QWORD`/`SQWORD` (`UnArc.h:182-191`); the port previously mislabelled an
  IEEE-754 `<d` packer as the QWORD/SQWORD operator.
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
- `FPackageFileSummary.serialize` only follows the pre-68 heritage GUID list
  when `HeritageOffset + HeritageCount * 16` fits in the archive. UnLinker.h:158
  runs the loop unconditionally, which a bogus count turns into an unbounded
  spin.
- `ULinkerLoad.is_error()` is always false: `read()` delegates to the underlying
  `FArchiveFileReader`, so the reader's error flag never reaches the linker's
  own `_error`. Nothing reads it yet, but a caller using it to detect a lost
  stream would never see one.
- `ULinker.get_import_full_name`/`get_export_full_name` are approximations: the
  C++ bodies (`UnLinker.h:207-208`) are in the prebuilt `Core.lib`, and
  `get_export_full_name` here ignores `PackageIndex` entirely.
- `core/objects.py` `RF_NoFlags`/`CPF_NoFlags` are Python-side zero aliases (the
  header spells "no flags" as `0` and does not name it). `FDependency.class_`
  carries the C++ `Class` member, a Python keyword.
- `UProperty._element_size` is a class attribute set on each concrete property
  type where the C++ `UProperty::Link` (in `Core.lib`) assigns `ElementSize`; the
  base class leaves it 0 because that body is unavailable. `UStrProperty`'s 16 is
  likewise the existing reconstruction.
