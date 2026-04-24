"""UCC compiler - UnrealScript compiler

Ported from Ut99PubSrc/UCC/
- UCC: UnrealScript compiler entry point
- UCommandlet: Base commandlet class
- UScript parser and compilation
- Bytecode emission
- Class compilation
"""

from typing import TYPE_CHECKING, Optional, ClassVar, List
import os
import sys

from ..core import (
    UObject, UClass, UStruct, UFunction, UPackage,
    FName, FString, FArchive, FArchiveFileReader, FArchiveFileWriter,
    FOutputDevice, FOutputDeviceFile, FOutputDeviceStdout,
    TArray,
)
from ..engine import ULevel

if TYPE_CHECKING:
    from ..engine import AActor


class UCommandlet(UObject):
    _commandlets: ClassVar[TArray['UCommandlet']] = TArray()
    
    def __init__(self):
        super().__init__()
        self._help_text: str = ""
        self._usage: str = ""
        self._lazy_load: list = []
    
    def main(self, params: str) -> int:
        return 0
    
    def usage(self) -> str:
        return self._usage


class UCCMain:
    def __init__(self):
        self._script_output: Optional[FArchive] = None
        self._log: FOutputDevice = FOutputDeviceStdout()
        self._warn: FOutputDevice = FOutputDeviceStdout()
        
        self._package: Optional[UPackage] = None
        self._level: Optional[ULevel] = None
        
        self._files_open: int = 0
        self._files_opened: int = 0
    
    def main(self, argc: int, argv: List[str]) -> int:
        return 0
    
    def show_banner(self) -> None:
        self._warn.serialize("=======================================")
        self._warn.serialize("ucc.exe: UnrealOS execution environment")
        self._warn.serialize("Copyright 1999 Epic Games Inc")
        self._warn.serialize("=======================================")
        self._warn.serialize("")
    
    def find_commandlet(self, name: str) -> Optional[UCommandlet]:
        return None
    
    def exec_commandlet(self, cmd: str, params: str) -> int:
        cmdlet = self.find_commandlet(cmd)
        if cmdlet:
            return cmdlet.main(params)
        return -1
    
    def init_native_functions(self) -> None:
        pass
    
    def clean_native_functions(self) -> None:
        pass


class UMakeCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "_make [options]: compile UnrealScript packages"
        self._usage = "make [-silent] [-noinstall]"
    
    def main(self, params: str) -> int:
        return 0


class UBatchExportCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "batchexport: export all objects from UnrealScript packages"
        self._usage = "batchexport <classname> <path> <ext>"
    
    def main(self, params: str) -> int:
        return 0


class UBatchImportCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "batchimport: import files into Unreal packages"
        self._usage = "batchimport <package> <classname> <path>"
    
    def main(self, params: str) -> int:
        return 0


class UListCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "list: list objects in package"
        self._usage = "list <package> [class]"
    
    def main(self, params: str) -> int:
        return 0


class UDumpCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "dump: dump object to text"
        self._usage = "dump <package> <object> [type]"
    
    def main(self, params: str) -> int:
        return 0


class USelectCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "select: select game options"
        self._usage = "select"
    
    def main(self, params: str) -> int:
        return 0


class UServerCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "server: run as dedicated server"
        self._usage = "server <map>"
    
    def main(self, params: str) -> int:
        return 0


class UMasterCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "master: run as master server"
        self._usage = "master"
    
    def main(self, params: str) -> int:
        return 0


class UEditorCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "editor: run Unreal Editor"
        self._usage = "editor [option]"
    
    def main(self, params: str) -> int:
        return 0


class UPackageCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "package: create an UnrealScript package"
        self._usage = "package <package> <path>"
    
    def main(self, params: str) -> int:
        return 0


class UInfoCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "info: print system information"
        self._usage = "info"
    
    def main(self, params: str) -> int:
        return 0


class UCompressCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "compress: compress files"
        self._usage = "compress <files>"
    
    def main(self, params: str) -> int:
        return 0


class UUncompressCommandlet(UCommandlet):
    def __init__(self):
        super().__init__()
        self._help_text = "uncompress: uncompress files"
        self._usage = "uncompress <files>"
    
    def main(self, params: str) -> int:
        return 0


class UScriptParser:
    def __init__(self):
        self._text: str = ""
        self._pos: int = 0
        self._line: int = 1
        self._column: int = 1
    
    def parse_token(self) -> str:
        return ""
    
    def parse_expression(self) -> dict:
        return {}
    
    def parse_statement(self) -> dict:
        return {}
    
    def parse_function(self) -> dict:
        return {}
    
    def parse_class(self) -> dict:
        return {}


class FScriptCompiler:
    def __init__(self):
        self._output: Optional[FArchive] = None
        self._errors: list = []
        self._warnings: list = []
    
    def compile(self, text: str) -> bool:
        return True
    
    def emit_bytecode(self, code: list) -> None:
        pass
    
    def emit_opcode(self, opcode: int) -> None:
        pass
    
    def emit_int(self, value: int) -> None:
        pass
    
    def emit_float(self, value: float) -> None:
        pass
    
    def emit_name(self, name: FName) -> None:
        pass
    
    def error(self, message: str) -> None:
        self._errors.append(message)
    
    def warning(self, message: str) -> None:
        self._warnings.append(message)


class FScriptDumper:
    def __init__(self):
        self._output: str = ""
    
    def dump(self, data: bytes) -> str:
        return ""
    
    def dump_disassembly(self, data: bytes) -> str:
        return ""
    
    def dump_stack(self, data: bytes) -> str:
        return ""


class UScriptTokenizer:
    def __init__(self):
        self._input: str = ""
        self._pos: int = 0
        self._tokens: list = []
    
    def tokenize(self, text: str) -> list:
        return []
    
    def next_token(self) -> Optional[dict]:
        return None
    
    def peek_token(self) -> Optional[dict]:
        return None


class FScriptObject:
    def __init__(self):
        self._class: Optional[UClass] = None
        self._name: FName = FName("None")
        self._outer: Optional[UObject] = None
        self._props: dict = {}


class UScriptArchive:
    def __init__(self):
        super().__init__()
        self._objects: List[FScriptObject] = []
    
    def read_package(self, filename: str) -> bool:
        ar = FArchiveFileReader(filename)
        if ar.is_error():
            return False
        return True
    
    def write_package(self, filename: str) -> bool:
        ar = FArchiveFileWriter(filename)
        if ar.is_error():
            return False
        return True
    
    def add_object(self, obj: FScriptObject) -> None:
        self._objects.append(obj)


GMakeCommandlet = UMakeCommandlet()
GBatchExportCommandlet = UBatchExportCommandlet()
GBatchImportCommandlet = UBatchImportCommandlet()
UListCommandlet = UListCommandlet()
UDumpCommandlet = UDumpCommandlet()