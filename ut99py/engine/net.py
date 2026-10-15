"""Port of Engine/Inc/UnNet.h (13 declared symbols).

Networking inline math functions: best_signed_difference, make_relative.
All other symbols (EChannelType, UChannel, UControlChannel, UActorChannel,
UFileChannel, FInBunch, FOutBunch, UNetDriver, UNetConnection, UPendingLevel,
UNetPendingLevel, UDemoPlayPendingLevel, UChannelIterator) are defined in
engine/__init__.py and exported from there.
"""
from typing import Any


def best_signed_difference(value: int, reference: int, max_val: int) -> int:
    """Return the value of Max/2 <= Value-Reference+some_integer*Max < Max/2."""
    return ((value - reference + max_val // 2) & (max_val - 1)) - max_val // 2


def make_relative(value: int, reference: int, max_val: int) -> int:
    return reference + best_signed_difference(value, reference, max_val)


__all__ = [
    "best_signed_difference",
    "make_relative",
]