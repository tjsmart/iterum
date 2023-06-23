from __future__ import annotations

from enum import Enum
from enum import unique

from ._singleton import create_singleton


@unique
class Ordering(Enum):
    """
    An [Ordering][iterum.Ordering] is the result of a comparison between
    two values.
    """

    Less = create_singleton("Less")
    """
    An ordering where a compared value is less than another.
    """

    Equal = create_singleton("Equal")
    """
    An ordering where a compared value is equal to another.
    """

    Greater = create_singleton("Greater")
    """
    An ordering where a compared value is greater than another.
    """

    @staticmethod
    def cmp(lhs, rhs, /) -> Ordering:
        """
        Compare two values.

        Examples:

            >>> Ordering.cmp(1, 2)
            Ordering.Less
            >>> Ordering.cmp(1, 1)
            Ordering.Equal
            >>> Ordering.cmp(2, 1)
            Ordering.Greater

        A `TypeError` will be raised if the two objects are not comparable:

            >>> try:
            ...     Ordering.cmp(1, "two")
            ... except TypeError as ex:
            ...     print(f"exception received: {ex}")
            ...
            exception received: '>' not supported between instances of 'int' and 'str'
        """

        if lhs == rhs:
            return Ordering.Equal
        if lhs > rhs:
            return Ordering.Greater
        if lhs < rhs:
            return Ordering.Less
        raise ValueError(f"Unable to compare {lhs!r} with {rhs!r}")

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"
