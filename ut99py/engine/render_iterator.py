"""Port of Engine/Inc/UnRenderIteratorSupport.h (2 declared symbols).

ActorBuffer + FActorNode structs/classes used by render iterator support.
Body of FActorNode destructor raises NotImplementedError; inline constructor
is preserved (sets NextNode to None).
"""
from __future__ import annotations
from typing import Any, Optional


class ActorBuffer:
    """ActorBuffer (UnRenderIteratorSupport.h:4-7)"""
    # Size derived from sizeof(AActor) but AActor class may vary.
    # We approximate with a fixed buffer size from C++ source.
    Buffer: bytearray = bytearray(256)  # sizeof(AActor) approximation


class FActorNode:
    """FActorNode (UnRenderIteratorSupport.h:11-21)"""

    def __init__(self) -> None:
        # Inline constructor: NextNode(NULL).
        self.ActorProxy: ActorBuffer = ActorBuffer()
        self.NextNode: Optional[FActorNode] = None

    def __del__(self) -> None:
        # C++ destructor: deletes linked list recursively; body in Engine.lib.
        # Python GC handles this; we don't need a custom destructor.
        pass


__all__ = ["ActorBuffer", "FActorNode"]
