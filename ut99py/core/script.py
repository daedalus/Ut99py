"""Port of Core/Inc/UnScript.h FFrame/FStateFrame inline methods.

Source: UnScript.h lines 103-178 (FFrame ctor, Step, ReadInt/ReadObject/
ReadFloat/ReadWord/ReadName) and 185-194 (FStateFrame ctor, Describe). The
FFrame/FStateFrame member declarations are in Core/Inc/UnStack.h:196-233.

Macro definitions (P_GET_UBOOL, etc.) are C++ preprocessor constructs and are
documented rather than ported. CORE_API functions (GInitRunaway, GNatives,
GRegisterNative) remain unimplemented (bodies in Core.lib).
"""

import struct

# FFrame/FStateFrame inline methods rely on UObject.get_class() and the
# UStruct script buffer, which live in core/objects.py.


class FFrame:
    """Port of UnStack.h:196 FFrame (inline bodies UnScript.h:103-178)."""

    def __init__(self, InObject=None, InNode=None, CodeOffset=0, Locals=None):
        # FFrame( UObject* InObject ) (UnScript.h:103-108) leaves Code NULL.
        # FFrame( UObject* InObject, UStruct* InNode, INT CodeOffset, void* InLocals )
        # (UnScript.h:109-114) sets Code = &InNode->Script(CodeOffset).
        self.Node = InObject.get_class() if InObject else None
        self.Object = InObject
        if InNode is None:
            self.Code = None
        else:
            self.Code = InNode._script[CodeOffset:]
        self.Locals = Locals

    # void FFrame::Step(...) (UnScript.h:115-121)
    # Dispatches via GNatives[B] (Core.lib); structural stub that advances past
    # the opcode byte as the C++ does (Code++).
    def step(self, Context, Result):
        """FFrame::Step (UnScript.h:115). The C++ is `INT B = *Code++;
        (Context->*GNatives[B])(*this, Result);`. GNatives lives in Core.lib and
        is not ported, so only the code advance is reproduced."""
        self.Code = self.Code[1:]  # advance past the opcode byte

    # INT FFrame::ReadInt() (UnScript.h:122-132)
    def read_int(self) -> int:
        """FFrame::ReadInt (UnScript.h:122): INT (32-bit signed) at Code."""
        result = int.from_bytes(self.Code[:4], "little", signed=True)
        self.Code = self.Code[4:]
        return result

    # UObject* FFrame::ReadObject() (UnScript.h:133-143)
    def read_object(self):
        """FFrame::ReadObject (UnScript.h:133): the C++ reads sizeof(INT) bytes
        as an object pointer; the port returns the raw index, which the caller
        resolves through an object table."""
        result = int.from_bytes(self.Code[:4], "little")
        self.Code = self.Code[4:]
        return result

    # FLOAT FFrame::ReadFloat() (UnScript.h:144-154)
    def read_float(self) -> float:
        """FFrame::ReadFloat (UnScript.h:144): IEEE-754 float at Code."""
        result = struct.unpack("<f", self.Code[:4])[0]
        self.Code = self.Code[4:]
        return result

    # INT FFrame::ReadWord() (UnScript.h:155-167)
    def read_word(self) -> int:
        """FFrame::ReadWord (UnScript.h:155): a _WORD (16-bit unsigned,
        UnGnuG.h:125) widened to INT."""
        result = int.from_bytes(self.Code[:2], "little")
        self.Code = self.Code[2:]
        return result

    # FName FFrame::ReadName() (UnScript.h:168-178)
    def read_name(self):
        """FFrame::ReadName (UnScript.h:168): sizeof(FName) is 4 bytes in UT99
        (a single NAME_INDEX, UnName.h:149). The port returns the index; the
        caller resolves it through the file's name table."""
        idx = struct.unpack("<I", self.Code[:4])[0]
        self.Code = self.Code[4:]
        return idx


class FStateFrame(FFrame):
    """Port of UnStack.h:222 FStateFrame (inline members UnScript.h:185-194)."""

    # ~(QWORD)0 -- all probe bits set (UnScript.h:189).
    PROBE_MASK_ALL: int = 0xFFFFFFFFFFFFFFFF

    def __init__(self, InObject=None):
        # FStateFrame( UObject* InObject ) (UnScript.h:185-190).
        super().__init__(InObject)
        self.CurrentFrame = None
        self.StateNode = InObject.get_class() if InObject else None
        self.ProbeMask = FStateFrame.PROBE_MASK_ALL
        self.LatentAction = 0

    def describe(self) -> str:
        """FStateFrame::Describe (UnScript.h:191-194): the Node's full name, or
        'None' when there is no Node."""
        return self.Node.get_full_name() if self.Node else "None"
