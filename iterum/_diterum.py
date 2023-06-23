from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Sequence

from ._iterum import Iterum
from ._iterum import T_co
from ._iterum import U
from ._option import nil
from ._option import Option
from ._option import Some


class Diterum(Iterum[T_co]):
    """
    Iterator-like abstract base class that is reversible and of known size.
    To implement this, inherit from [Diterum][iterum.Diterum] and then define
    a [next][iterum.Iterum.next], [next_back][iterum.Diterum.next_back], and
    [len][iterum.Diterum.len] method. See [diterum][iterum.diterum] for an
    example.
    """

    __slots__ = ()

    @abstractmethod
    def next_back(self) -> Option[T_co]:
        """
        Required method.

        Removes and returns an element from the end of the diterum.

        Returns [nil][iterum.nil] when there are no more elements.

        Examples:

            >>> di = diterum([1, 2, 3, 4, 5, 6])
            >>> assert di.next() == Some(1)
            >>> assert di.next_back() == Some(6)
            >>> assert di.next_back() == Some(5)
            >>> assert di.next() == Some(2)
            >>> assert di.next() == Some(3)
            >>> assert di.next() == Some(4)
            >>> assert di.next() == nil
            >>> assert di.next_back() == nil
        """
        ...

    @abstractmethod
    def len(self) -> int:
        """
        Required method.

        Returns the exact remaining length of the diterum.

        Examples:

            >>> di = diterum([1, 2, 3, 4])
            >>> assert di.len() == 4
            >>> assert di.next() == Some(1)
            >>> assert di.len() == 3
            >>> assert di.next_back() == Some(4)
            >>> assert di.len() == 2
            >>> assert di.collect() == [2, 3]
            >>> assert di.next() == nil
            >>> assert di.len() == 0
        """
        ...

    # Defined by Iterator
    def rev(self) -> Rev[T_co]:
        """
        Reverses an diterum’s direction.

        Usually, iterums iterate from left to right. After using
        [rev()][iterum.Diterum.rev], an iterum will instead iterate from
        right to left.

        Examples:

            >>> di = diterum([1, 2, 3]).rev()
            >>> assert di.next() == Some(3)
            >>> assert di.next() == Some(2)
            >>> assert di.next() == Some(1)
            >>> assert di.next() == nil
        """
        return Rev(self)

    def rposition(self, predicate: Callable[[T_co], object], /) -> Option[int]:
        """
        Searches for an element in a diterum from the right, returning its index.

        [rposition()][iterum.Diterum.rposition] takes a closure that returns
        `True` or `False`. It applies this closure to each element of the
        diterum, starting from the end, and if one of them returns `True`, then
        [rposition()][iterum.Diterum.rposition] returns [Some(index)][iterum.Some].
        If all of them return `False`, it returns [nil][iterum.nil].

        [rposition()][iterum.Diterum.rposition] is short-circuiting; in other
        words, it will stop processing as soon as it finds a `True`.

        Examples:

            >>> di = diterum([1, 2, 3])
            >>> assert di.rposition(lambda x: x == 3) == Some(2)
            >>> assert di.rposition(lambda x: x == 5) == nil

            >>> # Short-circuiting after first `True`:
            >>> di = diterum([-1, 2, 3, 4])
            >>> assert di.rposition(lambda x: x >= 2) == Some(3)
            >>> assert di.next() == Some(-1)
        """
        len = self.len()
        return self.rev().position(predicate).map(lambda x: len - x - 1)

    # Defined by DoubleEndedIterator
    def nth_back(self, n: int, /) -> Option[T_co]:
        """
        Returns the nth element from the end of the diterum.

        This is essentially the reversed version of [Iterum.nth()][iterum.Iterum.nth].
        Although like most indexing operations, the count starts from zero, so
        [nth_back(0)][iterum.Diterum.nth_back] returns the first value from the end,
        [nth_back(1)][iterum.Diterum.nth_back] the second, and so on.

        Note that all elements between the end and the returned element will be
        consumed, including the returned element. This also means that calling
        [nth_back(0)][iterum.Diterum.nth_back] multiple times on the same diterum
        will return different elements.

        [nth_back()][iterum.Diterum.nth_back] will return [nil][iterum.nil] if n
        is greater than or equal to the length of the diterum.

        Examples:

            >>> di = diterum([1, 2, 3])
            >>> assert di.nth_back(2) == Some(1)

            >>> # Does not rewind:
            >>> di = diterum([1, 2, 3])
            >>> assert di.nth_back(1) == Some(2)
            >>> assert di.nth_back(1) == nil

            >>> # Returns `nil` if there are less than `n + 1` elements:
            >>> di = diterum([1, 2, 3])
            >>> assert di.nth_back(10) == nil
        """
        return self.rev().nth(n)

    def rfind(self, predicate: Callable[[T_co], object], /) -> Option[T_co]:
        """
        Searches for an element of a diterum from the back that satisfies a predicate.

        [rfind()][iterum.Diterum.rfind] takes a closure that returns `True` or
        `False`. It applies this closure to each element of the diterum,
        starting at the end, and if any of them return `True`, then
        [rfind()][iterum.Diterum.rfind] returns [Some(element)][iterum.Some]. If
        they all return `False`, it returns [nil][iterum.nil].

        [rfind()][iterum.Diterum.rfind] is short-circuiting; in other words, it
        will stop processing as soon as the closure returns `True`.

        Examples:

            >>> di = diterum([1, 2, 3])
            >>> assert di.rfind(lambda x: x == 2) == Some(2)
            >>> assert di.rfind(lambda x: x == 5) == nil

            >>> # Stops at first `True`:
            >>> di = diterum([1, 2, 3])
            >>> assert di.rfind(lambda x: x == 2) == Some(2)
            >>> assert di.next_back() == Some(1)
        """
        return self.rev().find(predicate)

    def rfold(self, init: U, f: Callable[[U, T_co], U], /) -> U:
        """
        A diterum method that reduces the diterum’s elements to a single,
        final value, starting from the back.

        This is the reverse version of [Iterum.fold()][iterum.Iterum.fold]:
        it takes elements starting from the back of the diterum.

        [rfold()][iterum.Diterum.rfold] takes two arguments: an initial value,
        and a closure with two arguments: an ‘accumulator’, and an element. The
        closure returns the value that the accumulator should have for the next
        iteration.

        The initial value is the value the accumulator will have on the first call.

        After applying this closure to every element of the diterum,
        [rfold()][iterum.Diterum.rfold] returns the accumulator.

        Examples:

            >>> di = diterum([1, 2, 3])
            >>> sum = di.rfold(0, lambda acc, x: acc + x)
            >>> assert sum == 6

            >>> # `rfold` is right-associative:
            >>> numbers = [1, 2, 3, 4, 5]
            >>> zero = "0"
            >>> result = diterum(numbers).rfold(zero, lambda acc, x: f"({x} + {acc})")
            >>> assert result == "(1 + (2 + (3 + (4 + (5 + 0)))))"
        """
        return self.rev().fold(init, f)

    def try_rfold(
        self,
        init: U,
        f: Callable[[U, T_co], U],
        /,
        *,
        exception: type[BaseException] | tuple[type[BaseException], ...] = Exception,
    ) -> Option[U]:
        """
        This is the reverse version of [Iterum.try_fold()][iterum.Iterum.try_fold]:
        it takes elements starting from the back of the diterum.

        Examples:

            >>> di = diterum(["1", "2", "3"])
            >>> sum = di.try_rfold(0, lambda acc, x: acc + int(x), exception=TypeError)
            >>> assert sum == Some(6)
        """
        return self.rev().try_fold(init, f, exception=exception)


class Rev(Diterum[T_co]):
    """
    Implements a [Diterum][iterum.Diterum] interface that wraps
    a [diterum][iterum.diterum] object and swaps calls to
    [next][iterum.Diterum.next_back] with [next_back][iterum.Iterum.next]
    and vice versa.
    """

    __slots__ = ("_x",)

    def __init__(self, __x: Diterum[T_co] | Sequence[T_co]) -> None:
        self._x = __x if isinstance(__x, Diterum) else diterum(__x)

    def next(self) -> Option[T_co]:
        return self._x.next_back()

    def next_back(self) -> Option[T_co]:
        return self._x.next()

    def len(self) -> int:
        return self._x.len()


class diterum(Diterum[T_co]):
    """
    Implements a [Diterum][iterum.Diterum] interface from a sequence.

    Examples:
        >>> itr = diterum([1, 2, 3])
        >>> assert itr.next() == Some(1)
        >>> assert itr.next_back() == Some(3)
        >>> assert itr.next() == Some(2)
        >>> assert itr.next_back() == nil
        >>> assert itr.next() == nil

        >>> itr = diterum([1, 2, 3])
        >>> assert itr.rfold(0, lambda acc, x: acc*2 + x) == 17

        >>> x = range(5)
        >>> y = (
        ...     diterum(x)
        ...     .rev()
        ...     .map(lambda x: x**2 + 1)
        ...     .filter(lambda x: x % 2)
        ...     .collect()
        ... )
        >>> assert y == [17, 5, 1]
    """

    __slots__ = ("_seq", "_front", "_back")

    def __init__(self, __seq: Sequence[T_co], /) -> None:
        self._seq = __seq
        self._front = 0
        self._back = len(__seq) - 1

    def next(self) -> Option[T_co]:
        """
        Returns the next value in the sequence from the front if present,
        otherwise [nil][iterum.nil].

        Examples:
            >>> itr = diterum([1, 2])
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == Some(2)
            >>> assert itr.next() == nil
        """

        if self._back < self._front:
            return nil

        nxt = self._seq[self._front]
        self._front += 1
        return Some(nxt)

    def next_back(self) -> Option[T_co]:
        """
        Returns the next value in the sequence from the back if present,
        otherwise [nil][iterum.nil].

        Examples:
            >>> itr = diterum([1, 2])
            >>> assert itr.next_back() == Some(2)
            >>> assert itr.next_back() == Some(1)
            >>> assert itr.next_back() == nil
        """

        if self._back < self._front:
            return nil

        nxt = self._seq[self._back]
        self._back -= 1
        return Some(nxt)

    def len(self) -> int:
        """
        Returns the remaining length of the sequence.

        Examples:
            >>> itr = diterum([1, 2])
            >>> assert itr.len() == 2
            >>> assert itr.next() == Some(1)
            >>> assert itr.len() == 1
            >>> assert itr.next_back() == Some(2)
            >>> assert itr.len() == 0
            >>> assert itr.next() == nil
            >>> assert itr.len() == 0
        """

        if self._back < self._front:
            return 0

        return self._back + 1 - self._front
