from __future__ import annotations

from enum import Enum
from enum import unique

from ._singleton import create_singleton


@unique
class Ordering(Enum):
    Less = create_singleton("Less")
    Equal = create_singleton("Equal")
    Greater = create_singleton("Greater")

    @staticmethod
    def cmp(lhs, rhs) -> Ordering:
        if lhs > rhs:
            return Ordering.Greater
        if lhs == rhs:
            return Ordering.Equal
        if lhs < rhs:
            return Ordering.Less
        raise ValueError(f"Unable to compare {lhs!r} with {rhs!r}")
