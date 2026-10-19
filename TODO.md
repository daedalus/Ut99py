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
- [x] `Core/Inc/UnClass.h` remaining inline accessors → `core/objects.py`:
      `UStruct.get_properties_size`/`set_properties_size` (UnClass.h:240,248)/
      `get_name_cpp` (:261), `UFunction.merge_bools` (:316),
      `UState.merge_bools` (:360), `UClass.merge_bools` (:451)/
      `get_name_cpp` (:453, the Actor-prefix variant)/`get_default_actor`
      (:490). `UClass.get_default_object` (:483, the raw `&Defaults(0)` pointer)
      now raises `NotImplementedError` instead of fabricating an object.
- [x] `FArchive.serialize_qword`/`serialize_sqword` (`UnArc.h:182-191`). The old
      `serialize_double` claimed to be this operator but packed an IEEE-754
      `double`; `QWORD`/`SQWORD` are 64-bit ints (`UnGnuG.h:127,136`).

## Audit (Oct 2026)

*   **Ported Core Headers**: 16/20 (FCodec.h, FRiffChunk.h, UnArc.h, UnBits.h, UnClass.h, UnCoreNet.h, UnFile.h, UnNames.h, UnObjBas.h, UnObjVer.h, UnScript.h, UnStack.h, UnType.h, FConfigCacheIni.h, FFeedbackContextAnsi.h, FMallocAnsi.h).
*   **Partially Ported Engine**: 3/40+ (UnMesh.h, UnTex.h, UPackage/UnPackage.h).
*   **Reconciled**: `engine/assets.py` now delegates the on-disk format to
    `core/linkers.py` (UPackage wraps the linker's tables).
*   **Missing Metadata**: Fixed — `engine/mesh.py`, `engine/texture.py` and
    `core/types.py` now cite their source headers (UnMesh.h/UnAnim.h,
    UnTex.h, UnMath.h/UnArc.h), so `tools/port_survey.py` tracks them.

## Next
- [x] `ULinkerLoad::operator<<(UObject*&)` / `IndexToObject` (UnLinker.h:249-272)
      → `core/linkers.py`: the archive's `_serialize` now reads the compact
      index and resolves it through the export/import tables. `CreateExport`/
      `CreateImport` are structural stubs returning the table entry as the
      placeholder object, because the C++ construction bodies are in Core.lib.
- [x] `ULinkerSave::operator<<(FName&)` (:317) / `operator<<(UObject*&)` (:324) →
      `core/linkers.py`: the two operators map the operand's global index through
      `NameIndices`/`ObjectIndices` and write it as a compact index (a NULL object
      maps to 0). `ULinkerSave` now initialises the `FArchive` base and forwards
      `write` to `Saver` (UnLinker.h:333), raising if there is no Saver. Added
      `UObject.get_index` (UnObjBas.h:651) and wired the previously-dead
      `__post_init__` object-table registration (GObjObjects/`AddObject`,
      UnObjBas.h:494), so `GetIndex` now returns a real slot. Pinned by
      `tests/test_linkers_save.py`.
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
- [x] `Core/Inc/FRiffChunk.h` → `core/riff.py`: the whole header is inline.
      `app_four_cc` (FRiffChunk.h:14) plus the chunk tree `FRiffChunk`/
      `FRiffChunk_RIFF`/`FRiffChunk_fmt`/`FRiffChunk_data`/`FRiffChunk_WAVE`
      (`SerializeChunk`/`CreateSubChunk`/`Load`/`Save`), and
      `load_riff_file`/`save_riff_file`. `FBufferReader` (UnTemplate.h:1534) is
      `FArchiveMemoryReader`; `appLoadFileToArray`/`FFileManager` bodies are in
      Core.lib, so the file helpers open the file directly. `FArchiveFileWriter`
      gained a `seek` (the C++ writer is seekable; `Save` patches the chunk size
      in place). Pinned by `tests/test_riff.py`.
- [x] `Core/Inc/FConfigCacheIni.h` → `core/system.py` (replacing the initial
      commit's stub, which ignored `Filename` and returned `""`/`0` for missing
      keys): `FConfigSection` (TMultiMap<FString,FString>, insertion-ordered
      pairs; `Find` yields the newest duplicate per UnTemplate.h:1634,1718),
      `FConfigFile` (TMap<FString,FConfigSection> + `Dirty`/`NoSave`;
      `Read`/`Write`), and the full `FConfigCacheIni` interface. `Read` splits
      `[Section]` headers and `Key=Value` after the first `=` with one quote
      pair stripped; `Write` emits `[Section]\r\n`, `Key=Value\r\n` per pair,
      then a blank line. The numeric accessors use C `atoi`/`atof` and
      `appStricmp`/"True" semantics; `GetString`/`GetInt`/`GetFloat`/`GetBool`
      return `None` where the C++ buffer-out functions return 0. The
      `appLoadFileToString`/`appSaveStringToFile` bodies are in Core.lib, so the
      file is read/written directly (as `core/riff.py` does). Pinned by
      `tests/test_config.py`.
- [x] Fixed `core/file_utils.py` `appToUpper`/`appToLower` (UnFile.h:260-267):
      the port had the branch condition inverted, so neither ever changed case
      (and `appStrihash` hashed the wrong bytes). Pinned by
      `tests/test_file_utils.py`.
- [x] `Core/Inc/UnBits.h` → `core/bits.py`: `FBitWriter`/`FBitWriterMark`/
      `FBitReader`. Bodies are in Core.lib; semantics recovered from the
      Core.dll disassembly (LSB-first packing, appBitsCpy OR-into-dest,
      variable-length SerializeInt). `bits_cpy` uses a big-integer form 40x
      faster than the per-bit loop. `FBufferWriter` (UnTemplate.h:1484) added
      to `core/system.py`. Pinned by `tests/test_bits.py`.
- [x] `Core/Inc/FCodec.h` → `core/codec.py`: `FCodec`/`FCodecRLE`/
      `FCodecMTF`/`FCodecBWT`/`FCodecHuffman`/`FCodecFull`, plus the UCC `.uz`
      wrapper (`compress_uz`/`decompress_uz`, magic 1234; chain
      [RLE, BWT, MTF, Huffman]) derived empirically from real UCC output --
      the compress commandlet source is absent from the source drop, and
      Setup's 5-codec chain (USetupDefinition.cpp:647-652, magic 5678) is a
      different format. FCodecFull's appSeconds/GWarn stage timing is omitted
      (unported Core.lib diagnostics; no data effect). Byte-for-byte
      validated against real UCC `.uz` output via golden vectors in
      `tests/test_codec.py`.
- [x] `Core/Inc/FMallocAnsi.h` → `core/system.py` (replacing the initial
      commit's stub, which called `ctypes.windll.kernel32.LocalAlloc` -- that is
      `FMallocWindows` behaviour, and it returned `0` on a non-Windows host):
      `FMalloc` base per `Core.h:210-219` (all pure virtual; the stub's
      non-C++ `get_size`/`get_physical_size` are gone), and `FMallocAnsi` over
      the process C library with pointer-width retypes (`c_int` truncates the
      address to 32 bits and segfaults on use). `check(Size>0)` raises
      `ValueError`; a failed `malloc` raises `MemoryError`; `Realloc`'s result
      is unchecked in the C++ too, so NULL propagates as `0`. `DumpAllocs`'s
      `debugf(NAME_Exit, ...)` goes to `GLog` (`debugf` unported); `HeapCheck`
      is a no-op (its C++ body is `#if _MSC_VER` only); `Init`/`Exit` are no-ops
      in the C++ too. Pinned by `tests/test_alloc.py`.
- [x] `Core/Inc/FFeedbackContextAnsi.h` → `core/system.py`:
      `FFeedbackContextAnsi` (`Serialize`'s Event chain -- Title suppressed,
      Heading/SubHeading rewrites, warning count plus `Context` prefix,
      Progress's `\r` with no forwarding, else LocalPrint + `GLog`/`AuxOut`
      copies; `YesNof`; `BeginSlowTask`/`EndSlowTask` with
      `check(SlowTaskCount>0)`; `StatusUpdatef`; `SetContext`), plus the
      `FFeedbackContext` abstract (`Core.h:271-280`) and `FContextSupplier`
      (`Core.h:264-269`) interfaces in `core/objects.py` -- the stub base carried
      unrelated `status_update`/`progress_*` methods with no C++ counterpart.
      Deviations: `appSprintf`/`GET_VARARGS` become `%`/`*args`; the unported
      `ParseParam(appCmdLine(),"Silent")` test becomes the `silent` ctor flag;
      the unported `GIsEditor`/`GIsClient`/`GIsSlowTask` globals
      (`Core.h:366-372`) default false (headless). Pinned by
      `tests/test_feedback.py`.
- [ ] `Core/Inc/UnFile.h` → file manager / `FArchiveFileReader` (appFindPackageFile,
      file-path utilities; full CORE_API bodies remain in Core.lib).
- [ ] `ut99py/core/objects.py` object-model gaps (there is no `UnObj.h`; the
      model is `UnObjBas.h` + `UnType.h` + `UnClass.h`):
      `UProperty::Matches`/`Identical` and `UStruct::StructCompare` operate on
      raw pointers and per-type `Identical` bodies that live in `Core.lib`, so
      they need a Python value model before they can be ported faithfully.
      `UClass::GetDefaultObject` (UnClass.h:483) returns a raw `&Defaults(0)`
      pointer, so it now raises `NotImplementedError` rather than fabricating;
      `UObject::IsA` uses `isinstance` instead of the C++
      `UClass` walk; `UStruct::Link`/`UClass::Bind`/`StaticAllocateObject` are the
      `Core.lib` construction path.
- [x] `Core/Inc/UnCoreNet.h` inline members → `core/net.py`: `FFieldNetCache`
      (UnCoreNet.h:12), `FClassNetCache` inline `GetMaxIndex` (UnCoreNet.h:35) /
      `GetRepConditionCount` (:39) / `GetFromField` (:43) / `GetFromIndex` (:53),
      `FPackageInfo` (:76), the no-op `operator<<(FArchive&,FClassNetCache*)`
      (:132), and `FPropertyRetirement` (:140). The CORE_API ctors and
      `operator<<` bodies remain in Core.lib (documented); the `UPackageMap`
      stub stays in `core/objects.py`. Pinned by `tests/test_net.py`.
- [x] `Core/Inc/UnScript.h` FFrame inline members → `core/script.py`
      (`FFrame` ctor/`step`/`read_int`/`read_object`/`read_float`/`read_word`/
      `read_name`, UnScript.h:103-178) plus the previously missing `FStateFrame`
      (UnScript.h:185-194, declared in UnStack.h:222) with its ctor and
      `describe`. Fixed two latent bugs the earlier port left: `InObject.GetClass()`
      → `get_class()` and `InNode.Script(CodeOffset)` → the script-buffer slice;
      `read_word` now reads an unsigned `_WORD` (UnGnuG.h:125), not a signed
      value. Pinned by `tests/test_script.py`. `GNatives`/`GRegisterNative` and
      the `P_GET_*` macros remain undocumented C++ preprocessor/dispatch details.
- [ ] `Core/Inc/UnType.h` property metaclasses: `UProperty::Matches`/`Identical`
      and the concrete `Identical`/`SerializeItem`/`ExportTextItem`/`ImportText`
      bodies are in `Core.lib` and need the Python value model (see object-model
      gaps above); `UClassProperty.GetID` (UnType.h:286) needs `UClassProperty`.
- [x] **Metadata Compliance**: Add "Ported from" docstrings to `engine/mesh.py` and `engine/texture.py`.
      Also cite UnMath.h/UnArc.h in `core/types.py` so the survey tool sees them.
- [x] **Reconciliation**: `engine/assets.py` now delegates to `core/linkers.py`
      (`AssetLoader.load_package` wraps a `ULinkerLoad` in `UPackage`); the
      duplicate summary/name/import/export decoders are deleted.
- [x] `Engine/Inc/UnAudio.h` → `ut99py/engine/audio.py` (10 declared symbols):
      `UAudioSubsystem` (abstract; pure virtuals raise, `CleanUp` empty inline
      per UnAudio.h:51), `FSoundData` (`TLazyArray<BYTE>` + `Owner`),
      `USound` (ctor/`GetDuration` inline, UnAudio.h:88,95; static `Audio`),
      `UMusic`, the `MAKEFOURCC`/`mmioFOURCC` macro, and `FWaveModInfo` with
      `FRiffWaveHeader`/`FRiffChunkOld`/`FFormatChunk`/`FSampleChunk`/
      `FSampleLoop`. The bodies absent from the header (FSoundData
      `Load`/`GetPeriod`, USound/UMusic `Serialize`/`Destroy`/`PostLoad`,
      FWaveModInfo readers/reducers/filters) exist only in the prebuilt
      `Engine.lib` (msvc symbols verified) and raise. Pinned by
      `tests/test_audio.py`.
- [x] `Engine/Inc/UnAudio.h` port reconciled into `ut99py/audio/__init__.py`:
      the invented `USound`/`UMusic`/`UAudioSubsystem` stand-ins are deleted
      and re-exported from `ut99py/engine/audio.py`, so `ut99py.USound`,
      `ut99py.audio.USound`, `ut99py.engine.USound` and
      `engine.assets.USound` are one class object. `Voice`/`Sample`/
      `FPlayingSound`/mixer placeholders stay pending the `Audio/` module;
      `__main__.py`'s prints of the invented `_channels`/`_duration`/
      `_sample_rate` fields now use the header field set. Pinned by
      `tests/test_audio.py`.

## Engine Subsystems Pending
- [ ] **Networking**: `UnNet.h`, `UnNetDrv.h`, `UnChan.h`, `UnBunch.h`, `UnConn.h`, `UnDownload.h`, `UnDemoRec.h`.
- [ ] **Actors & Game Logic**: `AActor.h`, `APawn.h`, `APlayerPawn.h`, `AWeapon.h`, `AInventory.h`, `APickup.h`, `AAmmo.h`, `AMover.h`, `ABrush.h`, `ACarcass.h`, `AZoneInfo.h`, `ALevelInfo.h`, `AGameReplicationInfo.h`, `APlayerReplicationInfo.h`.
- [ ] **World/Bsp**: `UnLevel.h`, `UnModel.h`, `UnDynBsp.h`, `UnReach.h`, `ULevelSummary.h`.
- [ ] **Rendering**: `UnRender.h`, `UnRenDev.h`, `Palette.h`, `S3tc.h`.
- [ ] **Audio**: `Audio/Inc/*` (the B audio module: `AudioSubsystem.h`, `AudioMixer.h`, ...).
      `UnAudio.h` is ported (`ut99py/engine/audio.py`).
- [ ] **Input & Engine Core**: `UnIn.h`, `UnCamera.h`, `UnEngine.h`, `UnGame.h`, `UnPlayer.h`, `UnURL.h`.

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
- `FConfigCache` (the pure-virtual config interface, Core.h:223) is not ported as
  a separate base; `FConfigCacheIni` implements the whole interface directly, as
  the repo did for the pure-virtual `FFileManager`.
- `FConfigCacheIni.GetString`/`GetInt`/`GetFloat`/`GetBool`/`GetSection` return
  the value or `None`, collapsing the C++ `UBOOL` + out-parameter pair; the
  `GetStr`/`SetX` helpers keep the C++ buffer-string behaviour (`GetStr` yields
  `""` when missing). `GetSection` returns the C++ NUL-separated
  `key=value\0...\0` buffer as a `str`. `appAtoi`/`appAtof`/`appStricmp`/
  `appStrcmp` are reconstructed from UnFile.h prototypes (bodies in Core.lib)
  with C `atoi`/`atof` leading-number parsing.
- `FConfigFile.Read` drops the degenerate single-`"` value case the C++ handles
  by writing past the buffer (`FConfigCacheIni.h:60`): a value that is exactly
  one `"` is kept verbatim instead of becoming empty.
- `core/system.py` `FOutputDeviceFile` is still the initial stub (eager `open`
  from an explicit filename, no Event routing). `FOutputDeviceFile.h` lazily
  makes the log from `appBaseDir`/`appCmdLine`'s `LOG=`/`ABSLOG=`/`appPackage`,
  suppresses `NAME_Title`, and needs the unported `appTimestamp`/
  `GFileManager.CreateFileWriter`/`GLogHook`/`GIsCriticalError`. Nothing
  constructs it yet, so it waits for `UnFile.h`.
- `core/system.py` `FMemCache` is an initial-commit hit/miss counter, not
  `UnCache.h`'s `FMemCache`; the real class is mostly `Core.lib` bodies
  (`Init`/`Create`/`Tick`/`FlushItem`), leaving only the accessors portable.
- `Core/Inc/UnMsg.h` (Win32 editor `WM_USER` message ids) is not ported: no
  Python consumer and no headless meaning.
- `Core/Inc/UnCorObj.h`: `ULanguage` is still missing and `UTextBuffer`'s
  ctor/`Serialize` bodies are in `Core.lib`.
