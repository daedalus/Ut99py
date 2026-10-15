"""Port of Core/Inc/UnScript.h FFrame inline methods (UnScript.h ~120-170).

Macro definitions (P_GET_UBOOL, etc.) are C++ preprocessor constructs;
translated to Python helper patterns below. CORE_API functions (GInitRunaway,
GNatives, GRegisterNative) remain unimplemented (bodies in Core.lib).
Source: UnScript.h lines 120-170 (FFrame::Step/ReadInt/ReadFloat/ReadObject/
ReadWord/ReadName); line ~158 (FStateFrame inline ctor).
"""

# FFrame inline translations (UnScript.h ~120-170): these are the inline
# methods of FFrame and FStateFrame. They rely on UObject.GetClass() / Script()
# which already live in core/objects.py.

class FFrame:
    """Port of UnScript.h FFrame (lines 103-170)."""
    def __init__(self, InObject=None, InNode=None, CodeOffset=0, Locals=None):
        # FFrame( UObject* InObject ) (UnScript.h:103)
        # FFrame( UObject* InObject, UStruct* InNode, INT CodeOffset, void* InLocals ) (UnScript.h:109)
        self.Node = InObject.GetClass() if InObject else None
        self.Object = InObject
        self.Code = (InNode.Script(CodeOffset) if InNode else None) if InNode else None
        self.Locals = Locals

    # void FFrame::Step(...) (UnScript.h:115)
    # Dispatches via GNatives (Core.lib); structural stub only.
    def step(self, Context, Result):
        B = self.Code[0]  # opcode byte
        # GNatives[B] lookup lives in Core.lib; Python equivalent needs dispatch table.
        self.Code = self.Code[1:]  # advance past opcode

    # INT FFrame::ReadInt() (UnScript.h:122)
    def read_int(self) -> int:
        # Reads 4-byte INT; advances Code.
        result = int.from_bytes(self.Code[:4], 'little', signed=True)
        self.Code = self.Code[4:]
        return result

    # UObject* FFrame::ReadObject() (UnScript.h:133)
    def read_object(self):
        # Reads 4-byte index/pointer; advances.
        result = int.from_bytes(self.Code[:4], 'little')
        self.Code = self.Code[4:]
        return result

    # FLOAT FFrame::ReadFloat() (UnScript.h:144)
    def read_float(self) -> float:
        import struct as _struct
        result = _struct.unpack('<f', self.Code[:4])[0]
        self.Code = self.Code[4:]
        return result

    # INT FFrame::ReadWord() (UnScript.h:155)
    def read_word(self) -> int:
        # Reads 2-byte _WORD; advances.
        result = int.from_bytes(self.Code[:2], 'little', signed=True)
        self.Code = self.Code[2:]
        return result

    # FName FFrame::ReadName() (UnScript.h:168)
    def read_name(self):
        # Reads sizeof(FName)=4 bytes (INT32 index in UT99); advances.
        import struct as _struct
        idx = _struct.unpack('<I', self.Code[:4])[0]
        self.Code = self.Code[4:]
        return idx  # caller resolves via name table
