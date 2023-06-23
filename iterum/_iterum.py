from __future__ import annotations

import builtins
import itertools
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic
from typing import overload
from typing import TYPE_CHECKING
from typing import TypeVar

from ._helpers import check_methods
from ._notset import NotSet
from ._notset import NotSetType
from ._option import Nil
from ._option import nil
from ._option import Option
from ._option import Some
from ._ordering import Ordering

if TYPE_CHECKING:
    from ._type_helpers import SupportsRichComparison
    from ._type_helpers import SupportsMulT
    from ._type_helpers import SupportsRichComparisonT
    from ._type_helpers import SupportsSumNoDefaultT


T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


# TODO: allow for a range syntax to iterum, e.g. `iterum(10)` or `iterum(1, ...)`
# If so, replace count_forever in test/docs
# finite ranges can be reversible -> diterum
# infinite ranges are not -> iterum


class Iterum(Iterator[T_co]):
    """
    Iterator-like abstract base class. To implement this, inherit from
    [Iterum][iterum.Iterum] and then define a [next][iterum.Iterum.next] method.
    See [iterum][iterum.iterum] for an example.
    """

    __slots__ = ()

    @abstractmethod
    def next(self) -> Option[T_co]:
        """
        Required method.

        Advances the iterum and returns the next value.

        Returns [nil][iterum.nil] when iteration is finished.
        Individual iterum implementations may choose to resume iteration,
        and so calling [next()][iterum.Iterum.next] again may or may not eventually start returning
        [Some(Item)][iterum.Some] again at some point.

        Examples:

            >>> itr = iterum([1, 2, 3])

            >>> # A call to next() returns the next value...
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == Some(2)
            >>> assert itr.next() == Some(3)

            >>> # ... and then `nil` once it's over.
            >>> assert itr.next() == nil

            >>> # More calls may or may not return `nil`. Here, they always will.
            >>> assert itr.next() == nil
            >>> assert itr.next() == nil
        """
        return nil

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Iterum:
            return check_methods(C, "next")
        return NotImplemented

    def __next__(self) -> T_co:
        return self.next().ok_or_else(StopIteration)

    def all(self, f: Callable[[T_co], object], /) -> bool:
        """
        Tests if every element of the iterum matches a predicate.

        [all()][iterum.Iterum.all] takes a closure that returns `True` or `False`.
        It applies this closure to each element of the iterum,
        and if they all return `True`, then so does [all()][iterum.Iterum.all].
        If any of them return `False`, it returns `False`.

        [all()][iterum.Iterum.all] is short-circuiting; in other words, it will
        stop processing as soon as it finds a `False`, given that no matter
        what else happens, the result will also be `False`.

        An empty iterum returns `True`.

        Examples:

            >>> # Basic usage:
            >>> a = [1, 2, 3]
            >>> assert iterum(a).all(lambda x: x > 0)
            >>> assert not iterum(a).all(lambda x: x > 2)

            >>> # Stopping at the first `False`:
            >>> itr = iterum([1, 2, 3])
            >>> assert not itr.all(lambda x: x != 2)
            >>> assert itr.next() == Some(3)
        """
        return all(map(f, self))

    def any(self, f: Callable[[T_co], object], /) -> bool:
        """
        Tests if any element of the iterum matches a predicate.

        [any()][iterum.Iterum.any] takes a closure that returns `True` or
        `False`. It applies this closure to each element of the iterum, and if
        any of them return `True`, then so does [any()][iterum.Iterum.any]. If
        they all return `False`, it returns `False`.

        [any()][iterum.Iterum.any] is short-circuiting; in other words, it will
        stop processing as soon as it finds a `True`, given that no matter what
        else happens, the result will also be `True`.

        An empty iterum returns `False`.

        Examples:

            >>> a = [1, 2, 3]
            >>> assert iterum(a).any(lambda x: x > 0)
            >>> assert not iterum(a).any(lambda x: x > 5)


            >>> # Stopping at teh first `True`:
            >>> itr = iterum([1, 2, 3])
            >>> assert itr.any(lambda x: x != 2)
            >>> # itr still has more elements.
            >>> assert itr.next() == Some(2)
        """
        return any(map(f, self))

    def chain(self: Iterum[T_co], other: Iterable[T_co], /) -> Chain[T_co]:
        """
        Takes two iterables and creates a new iterum over both in sequence.

        [chain()][iterum.Iterum.chain] will return a new iterum which will
        first iterate over values from the first iteerable and then over values
        from the second iterable.

        In other words, it links two iterables together, in a chain.

        Examples:

            >>> a1 = [1, 2, 3]
            >>> a2 = [4, 5, 6]
            >>> itr = iterum(a1).chain(a2)
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == Some(2)
            >>> assert itr.next() == Some(3)
            >>> assert itr.next() == Some(4)
            >>> assert itr.next() == Some(5)
            >>> assert itr.next() == Some(6)
            >>> assert itr.next() == nil
        """
        return Chain(self, other)

    @overload
    def cmp(
        self: Iterum[SupportsRichComparison], other: Iterable[object], /
    ) -> Ordering:
        ...

    @overload
    def cmp(
        self: Iterum[object], other: Iterable[SupportsRichComparison], /
    ) -> Ordering:
        ...

    def cmp(
        self: Iterum[SupportsRichComparison] | Iterum[object],
        other: Iterable[object] | Iterable[SupportsRichComparison],
        /,
    ) -> Ordering:
        """
        Lexicographically compares the elements of this Iterator with those of
        another.

        Examples:

            >>> assert iterum([1]).cmp([1]) == Ordering.Equal
            >>> assert iterum([1, 2]).cmp([1]) == Ordering.Greater
            >>> assert iterum([1]).cmp([1, 2]) == Ordering.Less
        """
        other = iterum(other)
        while True:
            match self.next(), other.next():
                case Some(left), Some(right):
                    if left > right:  # type: ignore | reason: ask for forgiveness not permission
                        return Ordering.Greater
                    if left < right:  # type: ignore | reason: ask for forgiveness not permission
                        return Ordering.Less
                    continue
                case Some(), Nil():
                    return Ordering.Greater

                case Nil(), Some():
                    return Ordering.Less

                case Nil(), Nil():
                    return Ordering.Equal

                case _:
                    raise AssertionError("Unreachable!")

    @overload
    def collect(self: Iterum[T_co], /) -> list[T_co]:
        ...

    @overload
    def collect(self: Iterum[T_co], container: type[list], /) -> list[T_co]:
        ...

    @overload
    def collect(self: Iterum[T_co], container: type[set], /) -> set[T_co]:
        ...

    @overload
    def collect(self: Iterum[T_co], container: type[tuple], /) -> tuple[T_co, ...]:
        ...

    @overload
    def collect(self: Iterum[tuple[U, V]], container: type[dict], /) -> dict[U, V]:
        ...

    @overload
    def collect(self: Iterum[T_co], container: Callable[[Iterable[T_co]], U], /) -> U:
        ...

    def collect(  # type: ignore
        self: Iterum[T_co], container: Callable[[Iterable[T_co]], U] = list, /
    ) -> U:
        """
        Transforms an iterum into a collection.

        [collect()][iterum.Iterum.collect] takes a container which is responsible
        for mapping an iterable into any type. Most commonly this is a collection
        type such as `list` or `set` but could also be a function such as `''.join`.

        Examples:

            >>> # basic usage
            >>> doubled = iterum([1, 2, 3]).map(lambda x: x * 2).collect(list)
            >>> assert doubled == [2, 4, 6]

            >>> # using `join` to collect an iterable of `str`
            >>> assert iterum("test").map(str.upper).collect("".join) == "TEST"
        """
        return container(self)

    def count(self) -> int:
        """
        Consumes the iterum, counting the number of iterations and returning it.

        This method will call next repeatedly until [nil][iterum.nil] is
        encountered, returning the number of times it saw [Some][iterum.Some].
        Note that next has to be called at least once even if the iterum does
        not have any elements.

        Examples:

            >>> assert iterum([1, 2, 3]).count() == 3
            >>> assert iterum([1, 2, 3, 4, 5]).count() == 5
        """
        last = self.enumerate().last()
        return last.map_or(0, lambda last: last[0] + 1)

    def cycle(self: Iterum[T_co], /) -> Cycle[T_co]:
        """
        Repeats an iterum endlessly.

        Instead of stopping at [nil][iterum.nil], the iterum will instead
        start again, from the beginning. After iterating again, it will start at
        the beginning again. And again. And again. Forever. Note that in case
        the original iterum is empty, the resulting iterum will also be empty.

        Examples:

            >>> a = [1, 2, 3]
            >>> it = iterum(a).cycle()
            >>> assert it.next() == Some(1)
            >>> assert it.next() == Some(2)
            >>> assert it.next() == Some(3)
            >>> assert it.next() == Some(1)
            >>> assert it.next() == Some(2)
            >>> assert it.next() == Some(3)
            >>> assert it.next() == Some(1)
        """
        return Cycle(self)

    def enumerate(self: Iterum[T_co], /) -> Enumerate[T_co]:
        """
        Creates an iterum which gives the current iteration count as well as
        the next value.

        The iterum returned yields pairs (i, val), where i is the current
        index of iteration and val is the value returned by the iterum.

        Examples:

            >>> a = ["a", "b", "c"]
            >>> it = iterum(a).enumerate()
            >>> assert it.next() == Some((0, "a"))
            >>> assert it.next() == Some((1, "b"))
            >>> assert it.next() == Some((2, "c"))
            >>> assert it.next() == nil
        """
        return Enumerate(self)

    @overload
    def eq(self: Iterum[SupportsRichComparison], other: Iterable[object], /) -> bool:
        ...

    @overload
    def eq(self: Iterum[object], other: Iterable[SupportsRichComparison], /) -> bool:
        ...

    def eq(
        self: Iterum[SupportsRichComparison] | Iterum[object],
        other: Iterable[object] | Iterable[SupportsRichComparison],
        /,
    ) -> bool:
        """
        Determines if the elements of this Iterator are equal to those of another.

        Examples:

            >>> assert iterum([1]).eq([1])
            >>> assert not iterum([1]).eq([1, 2])
        """
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp == Ordering.Equal

    def filter(
        self: Iterum[T_co], predicate: Callable[[T_co], object], /
    ) -> Filter[T_co]:
        """
        Creates an iterum which uses a closure to determine if an element
        should be yielded.

        Given an element the closure must return `True` or `False`. The returned
        iterum will yield only the elements for which the closure returns `True`.

        Examples:

            >>> a = [0, 1, 2]
            >>> it = iterum(a).filter(lambda x: x > 0)
            >>> assert it.next() == Some(1)
            >>> assert it.next() == Some(2)
            >>> assert it.next() == nil

        Note that `it.filter(f).next()` is equivalent to `it.find(f)`.
        """
        return Filter(self, predicate)

    def filter_map(
        self: Iterum[T_co], predicate: Callable[[T_co], Option[U]], /
    ) -> FilterMap[U]:
        """
        Creates an iterum that both filters and maps.

        The returned iterum yields only the values for which the supplied
        closure returns [Some(value)][iterum.Some].

        [filter_map][iterum.Iterum.filter_map] can be used to make chains of
        [filter][iterum.Iterum.filter] and [map][iterum.Iterum.map] more concise.

        Examples:

            >>> def parse2int(x: str) -> Option[int]:
            ...     try:
            ...         value = int(x)
            ...     except ValueError:
            ...         return nil
            ...     else:
            ...         return Some(value)
            ...
            >>> a = ["1", "two", "NaN", "four", "5"]
            >>> it = iterum(a).filter_map(parse2int)
            >>> assert it.next() == Some(1)
            >>> assert it.next() == Some(5)
            >>> assert it.next() == nil
        """
        return FilterMap(self, predicate)

    def find(self, predicate: Callable[[T_co], object], /) -> Option[T_co]:
        """
        Searches for an element of an iterum that satisfies a predicate.

        [find()][iterum.Iterum.find] takes a closure that returns `True` or
        `False`. It applies this closure to each element of the iterum, and if
        any of them return `True`, then [find()][iterum.Iterum.find] returns
        [Some(element)][iterum.Some]. If they all return `False`, it returns
        [nil][iterum.nil].

        [find()][iterum.Iterum.find] is short-circuiting; in other words, it
        will stop processing as soon as the closure returns `True`.

        If you need the index of the element, see [position()][iterum.Iterum.position].

        Examples:

            >>> a = [1, 2, 3]
            >>> assert iterum(a).find(lambda x: x == 2) == Some(2)
            >>> assert iterum(a).find(lambda x: x == 5) == nil

            >>> # Stopping at the first `True`:
            >>> it = iterum([1, 2, 3])
            >>> assert it.find(lambda x: x == 2) == Some(2)
            >>> assert it.next() == Some(3)

        Note that `it.find(f)` is equivalent to `it.filter(f).next()`.
        """
        for x in self:
            if predicate(x):
                return Some(x)
        return nil

    def find_map(self, predicate: Callable[[T_co], Option[U]], /) -> Option[U]:
        """
        Applies function to the elements of iterum and returns the first
        non-nil result.

        Examples:

            >>> def parse2int(x: str) -> Option[int]:
            ...     try:
            ...         value = int(x)
            ...     except ValueError:
            ...         return nil
            ...     else:
            ...         return Some(value)
            ...
            >>> a = ["lol", "NaN", "2", "5"]
            >>> first_number = iterum(a).find_map(parse2int)
            >>> assert first_number == Some(2)

        Note that `iter.find_map(f)` is equivalent to `iter.filter_map(f).next()`.
        """
        return self.filter_map(predicate).next()

    def flat_map(self, f: Callable[[T_co], Iterable[U]], /) -> FlatMap[U]:
        """
        Creates an iterum that works like map, but flattens nested structure.

        The [map][iterum.Iterum.map] adapter is very useful, but only when the
        closure argument produces values. If it produces an iterum instead,
        there’s an extra layer of indirection.
        [flat_map()][iterum.Iterum.flat_map] will remove this extra layer on its own.

        You can think of `flat_map(f)` as the semantic equivalent of mapping, and
        then flattening as in `map(f).flatten()`.

        Examples:

            >>> words = ["alpha", "beta", "gamma"]
            >>> merged = iterum(words).flat_map(iterum).collect("".join)
            >>> assert merged == "alphabetagamma"
        """
        return FlatMap(self, f)

    def flatten(self: Iterum[Iterable[U]]) -> Flatten[U]:
        """
        Creates an iterum that flattens nested structure.

        This is useful when you have an iterum of iterables and you want to
        remove one level of indirection.

        Examples:
            >>> data = [[1, 2, 3, 4], [5, 6]]
            >>> flattened = iterum(data).flatten().collect(list)
            >>> assert flattened == [1, 2, 3, 4, 5, 6]

            >>> # Mapping and then flattening:
            >>> words = ["alpha", "beta", "gamma"]
            >>> merged = iterum(words).map(iterum).flatten().collect("".join)
            >>> assert merged == "alphabetagamma"
        """
        return Flatten(self)

    def fold(self, init: U, f: Callable[[U, T_co], U], /) -> U:
        """
        Folds every element into an accumulator by applying an operation,
        returning the final result.

        [fold()][iterum.Iterum.fold] takes two arguments: an initial value, and
        a closure with two arguments: an ‘accumulator’, and an element. The
        closure returns the value that the accumulator should have for the next iteration.

        The initial value is the value the accumulator will have on the first call.

        After applying this closure to every element of the iterum, fold()
        returns the accumulator.

        Examples:

            >>> a = [1, 2, 3]
            >>> sum = iterum(a).fold(0, lambda acc, x: acc + x)
            >>> assert sum == 6

        Let's walk through each step of the iteration here:

        | element | acc | x | result |
        | ------- | --- | - | ------ |
        |         |  0  |   |        |
        |   1     |  0  | 1 |   1    |
        |   2     |  1  | 2 |   3    |
        |   3     |  3  | 3 |   6    |

        And so, our final result, 6.


        Fold is left-associative:

            >>> numbers = [1, 2, 3, 4, 5]
            >>> result = iterum(numbers).fold("0", lambda acc, x: f"({acc} + {x})")
            >>> assert result == "(((((0 + 1) + 2) + 3) + 4) + 5)"
        """
        acc = init
        for x in self:
            acc = f(acc, x)
        return acc

    def for_each(self, f: Callable[[T_co], object], /) -> None:
        """
        Calls a closure on each element of an iterum.

        For loops are more idiomatic... but who cares!

        Examples:

            >>> v = []
            >>> iterum(range(0, 5)).map(lambda x: x * 2 + 1).for_each(v.append)
            >>> assert v == [1, 3, 5, 7, 9]
        """
        for x in self:
            f(x)

    def fuse(self) -> Fuse[T_co]:
        """
        Creates an iterum which ends after the first [nil][iterum.nil].

        After an iterum returns [nil][iterum.nil], future calls may or may not
        yield [Some(T)][iterum.Some] again. [fuse()][iterum.Iterum.fuse] adapts
        an iterum, ensuring that after a [nil][iterum.nil] is given, it will
        always return [nil][iterum.nil] forever.

        Examples:

            >>> class Alternator(Iterator[int]):
            ...     def __init__(self) -> None:
            ...         self.i = 0
            ...     def __next__(self) -> int:
            ...         self.i += 1
            ...         if self.i % 5:
            ...             return self.i
            ...         else:
            ...             raise StopIteration()

            >>> it = iterum(Alternator())
            >>> assert list(it) == [1, 2, 3, 4]
            >>> assert list(it) == [6, 7, 8, 9]
            >>> assert list(it) == [11, 12, 13, 14]

            >>> it = it.fuse()
            >>> assert list(it) == [16, 17, 18, 19]
            >>> assert list(it) == []
            >>> assert list(it) == []
        """
        return Fuse(self)

    @overload
    def ge(self: Iterum[SupportsRichComparison], other: Iterable[object], /) -> bool:
        ...

    @overload
    def ge(self: Iterum[object], other: Iterable[SupportsRichComparison], /) -> bool:
        ...

    def ge(
        self: Iterum[SupportsRichComparison] | Iterum[object],
        other: Iterable[object] | Iterable[SupportsRichComparison],
        /,
    ) -> bool:
        """
        Determines if the elements of this Iterator are lexicographically
        greater than or equal to those of another.

        Examples:

            >>> assert iterum([1]).ge([1])
            >>> assert not iterum([1]).ge([1, 2])
            >>> assert iterum([1, 2]).ge([1])
            >>> assert iterum([1, 2]).ge([1, 2])
        """
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp in (Ordering.Greater, Ordering.Equal)

    @overload
    def gt(self: Iterum[SupportsRichComparison], other: Iterable[object], /) -> bool:
        ...

    @overload
    def gt(self: Iterum[object], other: Iterable[SupportsRichComparison], /) -> bool:
        ...

    def gt(
        self: Iterum[SupportsRichComparison] | Iterum[object],
        other: Iterable[object] | Iterable[SupportsRichComparison],
        /,
    ) -> bool:
        """
        Determines if the elements of this Iterator are lexicographically
        greater than those of another.

        Examples:

            >>> assert not iterum([1]).gt([1])
            >>> assert not iterum([1]).gt([1, 2])
            >>> assert iterum([1, 2]).gt([1])
            >>> assert not iterum([1, 2]).gt([1, 2])
        """
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp == Ordering.Greater

    def inspect(self, f: Callable[[T_co], object], /) -> Inspect[T_co]:
        """
        Does something with each element of an iterum, passing the value on.

        When using iterums, you’ll often chain several of them together. While
        working on such code, you might want to check out what’s happening at
        various parts in the pipeline. To do that, insert a call to
        [inspect()][iterum.Iterum.inspect].

        Examples:

            >>> s = (
            ...    iterum([1, 4, 2, 3])
            ...    .inspect(lambda x: print(f"about to filter: {x}"))
            ...    .filter(lambda x: x % 2 == 0)
            ...    .inspect(lambda x: print(f"made it through filter: {x}"))
            ...    .fold(0, lambda sum, i: sum + i)
            ... )
            ...
            about to filter: 1
            about to filter: 4
            made it through filter: 4
            about to filter: 2
            made it through filter: 2
            about to filter: 3
            >>> s
            6

            >>> a = [1, 2, 3]
            >>> b = []
            >>> c = (
            ...     iterum(a)
            ...     .map(lambda x: x * 2)
            ...     .inspect(b.append)
            ...     .take_while(lambda x: x < 5)
            ...     .collect(list)
            ... )
            >>> assert b == [2, 4, 6]
            >>> assert c == [2, 4]
        """
        return Inspect(self, f)

    def last(self) -> Option[T_co]:
        """
        Consumes the iterum, returning the last element.

        This method will evaluate the iterum until it returns
        [nil][iterum.nil]. While doing so, it keeps track of the current
        element. After [nil][iterum.nil] is returned, last() will then return
        the last element it saw.

        Examples:

            >>> assert iterum([1, 2, 3]).last() == Some(3)
            >>> assert iterum([1, 2, 3, 4, 5]).last() == Some(5)
        """
        last = nil
        while (nxt := self.next()) is not nil:
            last = nxt

        return last

    @overload
    def le(self: Iterum[SupportsRichComparison], other: Iterable[object], /) -> bool:
        ...

    @overload
    def le(self: Iterum[object], other: Iterable[SupportsRichComparison], /) -> bool:
        ...

    def le(
        self: Iterum[SupportsRichComparison] | Iterum[object],
        other: Iterable[object] | Iterable[SupportsRichComparison],
        /,
    ) -> bool:
        """
        Determines if the elements of this Iterator are lexicographically less
        or equal to those of another.

        Examples:

            >>> assert iterum([1]).le([1])
            >>> assert iterum([1]).le([1, 2])
            >>> assert not iterum([1, 2]).le([1])
            >>> assert iterum([1, 2]).le([1, 2])
        """
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp in (Ordering.Less, Ordering.Equal)

    @overload
    def lt(self: Iterum[SupportsRichComparison], other: Iterable[object], /) -> bool:
        ...

    @overload
    def lt(self: Iterum[object], other: Iterable[SupportsRichComparison], /) -> bool:
        ...

    def lt(
        self: Iterum[SupportsRichComparison] | Iterum[object],
        other: Iterable[object] | Iterable[SupportsRichComparison],
        /,
    ) -> bool:
        """
        Determines if the elements of this Iterator are lexicographically less
        than those of another.

        Examples:

            >>> assert not iterum([1]).lt([1])
            >>> assert iterum([1]).lt([1, 2])
            >>> assert not iterum([1, 2]).lt([1])
            >>> assert not iterum([1, 2]).lt([1, 2])
        """
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp == Ordering.Less

    def map(self, f: Callable[[T_co], U], /) -> Map[U]:
        """
        Takes a closure and creates an iterum which calls that closure on
        each element.

        [map()][iterum.Iterum.map] transforms one iterum into another, by
        means of its argument. It produces a new iterum which calls this
        closure on each element of the original iterum.

        Examples:

            >>> a = [1, 2, 3]
            >>> itr = iterum(a).map(lambda x: x * 2)
            >>> assert itr.next() == Some(2)
            >>> assert itr.next() == Some(4)
            >>> assert itr.next() == Some(6)
            >>> assert itr.next() == nil
        """
        return Map(self, f)

    def map_while(self, predicate: Callable[[T_co], Option[U]], /) -> MapWhile[U]:
        """
        Creates an iterum that both yields elements based on a predicate and maps.

        [map_while()][iterum.Iterum.map_while] takes a closure as an argument.
        It will call this closure on each element of the iterum, and yield
        elements while it returns [Some(_)][iterum.Some].

        Examples:

            >>> from functools import partial
            >>> def checked_div(num: int, dem: int) -> Option[int]:
            ...    try:
            ...        return Some(num // dem)
            ...    except ZeroDivisionError:
            ...        return nil
            ...
            >>> a = [-1, 4, 0, 1]
            >>> it = iterum(a).map_while(partial(checked_div, 16))
            >>> assert it.next() == Some(-16)
            >>> assert it.next() == Some(4)
            >>> assert it.next() == nil


            >>> # Stops after first `nil`:
            >>> a = [0, 1, 2, -3, 4, 5, -6]
            >>> it = iterum(a).map_while(lambda x: Some(x) if x >= 0 else nil)
            >>> vec = it.collect(list)
            >>> assert vec == [0, 1, 2]
            >>> assert it.next() == nil
        """
        return MapWhile(self, predicate)

    def max(
        self: Iterum[SupportsRichComparisonT],
    ) -> Option[SupportsRichComparisonT]:
        """
        Returns the maximum element of an iterum.

        If several elements are equally maximum, the last element is returned.
        If the iterum is empty, [nil][iterum.nil] is returned.

        Examples:

            >>> assert iterum([1, 2, 3]).max() == Some(3)
            >>> assert iterum([]).max() == nil
        """
        try:
            return Some(builtins.max(self))
        except ValueError:
            return nil

    def max_by(self, compare: Callable[[T_co, T_co], Ordering], /) -> Option[T_co]:
        """
        Returns the element that gives the maximum value with respect to the
        specified comparison function.

        If several elements are equally maximum, the last element is returned.
        If the iterum is empty, [nil][iterum.nil] is returned.

        Examples:
            >>> a = [-3, 0, 1, 5, -10]
            >>> assert iterum(a).max_by(Ordering.cmp).unwrap() == 5
        """
        max_ = self.next()
        if max_ is nil:
            return nil
        else:
            max_ = max_.unwrap()

        for nxt in self:
            if compare(max_, nxt) is Ordering.Less:
                max_ = nxt

        return Some(max_)

    def max_by_key(
        self, f: Callable[[T_co], SupportsRichComparison], /
    ) -> Option[T_co]:
        """
        Returns the element that gives the maximum value from the specified function.

        If several elements are equally maximum, the last element is returned.
        If the iterum is empty, [nil][iterum.nil] is returned.

        Examples:

            >>> a = [-3, 0, 1, 5, -10]
            >>> assert iterum(a).max_by_key(abs).unwrap() == -10
        """

        def compare(x, y) -> Ordering:
            fx = f(x)
            fy = f(y)
            return Ordering.cmp(fx, fy)

        return self.max_by(compare)

    def min(
        self: Iterum[SupportsRichComparisonT],
    ) -> Option[SupportsRichComparisonT]:
        """
        Returns the minimum element of an iterum.

        If several elements are equally minimum, the first element is returned.
        If the iterum is empty, [nil][iterum.nil] is returned.

        Examples:

            >>> assert iterum([1, 2, 3]).min() == Some(1)
            >>> assert iterum([]).min() == nil
        """
        try:
            return Some(builtins.min(self))
        except ValueError:
            return nil

    def min_by(self, compare: Callable[[T_co, T_co], Ordering], /) -> Option[T_co]:
        """
        Returns the element that gives the minimum value with respect to the
        specified comparison function.

        If several elements are equally minimum, the first element is returned.
        If the iterum is empty, [nil][iterum.nil] is returned.

        Examples:

            >>> a = [-3, 0, 1, 5, -10]
            >>> assert iterum(a).min_by(Ordering.cmp).unwrap() == -10
        """
        min_ = self.next()
        if min_ is nil:
            return nil
        else:
            min_ = min_.unwrap()

        for nxt in self:
            if compare(min_, nxt) is Ordering.Greater:
                min_ = nxt

        return Some(min_)

    def min_by_key(
        self, f: Callable[[T_co], SupportsRichComparison], /
    ) -> Option[T_co]:
        """
        Returns the element that gives the minimum value from the specified function.

        If several elements are equally minimum, the first element is returned.
        If the iterum is empty, [nil][iterum.nil] is returned.

        Examples:

            >>> a = [-3, 0, 1, 5, -10]
            >>> assert iterum(a).min_by_key(abs).unwrap() == 0
        """

        def compare(x, y) -> Ordering:
            fx = f(x)
            fy = f(y)
            return Ordering.cmp(fx, fy)

        return self.min_by(compare)

    @overload
    def ne(self: Iterum[SupportsRichComparison], other: Iterable[object], /) -> bool:
        ...

    @overload
    def ne(self: Iterum[object], other: Iterable[SupportsRichComparison], /) -> bool:
        ...

    def ne(
        self: Iterum[SupportsRichComparison] | Iterum[object],
        other: Iterable[object] | Iterable[SupportsRichComparison],
        /,
    ) -> bool:
        """
        Determines if the elements of this Iterator are not equal to those of another.

        Examples:

            >>> assert not iterum([1]).ne([1])
            >>> assert iterum([1]).ne([1, 2])
        """
        eq = self.eq(other)  # type: ignore | reason: ask for forgiveness not permission
        return not eq

    def nth(self, n: int, /) -> Option[T_co]:
        """
        Returns the nth element of the iterum.

        Like most indexing operations, the count starts from zero, so [nth(0)][iterum.Iterum.nth]
        returns the first value, [nth(1)][iterum.Iterum.nth] the second, and so on.

        Note that all preceding elements, as well as the returned element, will
        be consumed from the iterum. That means that the preceding elements
        will be discarded, and also that calling [nth(0)][iterum.Iterum.nth] multiple times on the
        same iterum will return different elements.

        [nth()][iterum.Iterum.nth] will return [nil][iterum.nil] if n is greater
        than or equal to the length of the iterum.

        Examples:

            >>> a = [1, 2, 3]
            >>> assert iterum(a).nth(1) == Some(2)

            >>> # Calling `nth` multiple times doesn't rewind the iterum:
            >>> itr = iterum([1, 2, 3])
            >>> assert itr.nth(1) == Some(2)
            >>> assert itr.nth(1) == nil

            >>> # Returns `nil` if there are less than `n + 1` elements:
            >>> itr = iterum([1, 2, 3])
            >>> assert itr.nth(3) == nil
        """
        for i, x in enumerate(self):
            if i > n:
                return nil
            if i == n:
                return Some(x)
        return nil

    @overload
    def partial_cmp(
        self: Iterum[SupportsRichComparison], other: Iterable[object], /
    ) -> Some[Ordering]:
        ...

    @overload
    def partial_cmp(
        self: Iterum[object], other: Iterable[SupportsRichComparison], /
    ) -> Some[Ordering]:
        ...

    @overload
    def partial_cmp(self: Iterum[object], other: Iterable[object], /) -> Nil:
        ...

    def partial_cmp(
        self: Iterum[SupportsRichComparison] | Iterum[object],
        other: Iterable[object] | Iterable[SupportsRichComparison],
        /,
    ) -> Option[Ordering]:
        """
        Lexicographically compares the PartialOrd elements of this Iterator with
        those of another. The comparison works like short-circuit evaluation,
        returning a result without comparing the remaining elements. As soon as
        an order can be determined, the evaluation stops and a result is returned.

        Examples:

            >>> assert iterum([1]).partial_cmp([1]) == Some(Ordering.Equal)
            >>> assert iterum([1, 2]).partial_cmp([1]) == Some(Ordering.Greater)
            >>> assert iterum([1]).partial_cmp([1, 2]) == Some(Ordering.Less)

            >>> # Results are determined by the order of evaluation:
            >>> assert iterum([1, None]).partial_cmp([2, nil]) == Some(Ordering.Less)
            >>> assert iterum([2, None]).partial_cmp([1, nil]) == Some(Ordering.Greater)
            >>> assert iterum([None, 1]).partial_cmp([2, None]) == nil
        """
        try:
            value = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        except TypeError:
            return nil
        else:
            return Some(value)

    @overload
    def partition(
        self, f: Callable[[T_co], object], /
    ) -> tuple[list[T_co], list[T_co]]:
        ...

    @overload
    def partition(
        self, f: Callable[[T_co], object], container: type[list], /
    ) -> tuple[list[T_co], list[T_co]]:
        ...

    @overload
    def partition(
        self, f: Callable[[T_co], object], container: type[set], /
    ) -> tuple[set[T_co], set[T_co]]:
        ...

    @overload
    def partition(
        self, f: Callable[[T_co], object], container: type[tuple], /
    ) -> tuple[tuple[T_co, ...], tuple[T_co, ...]]:
        ...

    @overload
    def partition(
        self: Iterum[tuple[U, V]], f: Callable[[T_co], object], container: type[dict], /
    ) -> tuple[dict[U, V], dict[U, V]]:
        ...

    @overload
    def partition(
        self, f: Callable[[T_co], object], container: Callable[[Iterable[T_co]], U], /
    ) -> tuple[U, U]:
        ...

    def partition(  # type: ignore
        self,
        f: Callable[[T_co], object],
        container: Callable[[Iterable[T_co]], U] = list,
        /,
    ) -> tuple[U, U]:
        """
        Consumes an iterum, creating two collections from it.

        The predicate passed to [partition()][iterum.Iterum.partition] can
        return `True`, or `False`. [partition()][iterum.Iterum.partition]
        returns a pair, all of the elements for which it returned `True`, and
        all of the elements for which it returned `False`.

        Examples:

            >>> a = [1, 2, 3]
            >>> even, odd = iterum(a).partition(lambda n: n % 2 == 0)
            >>> assert even == [2]
            >>> assert odd == [1, 3]
        """
        matches, notmatches = [], []
        for x in self:
            matches.append(x) if f(x) else notmatches.append(x)

        return container(matches), container(notmatches)

    def peekable(self) -> Peekable[T_co]:
        """
        Creates an iterum which provides a peek attribute for viewing
        and setting the next element of the iterum without consuming it.

        Examples:

            >>> xs = [1, 2, 3]
            >>> itr = iterum(xs).peekable()
            >>> assert itr.peek == Some(1)
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == Some(2)
            >>> assert itr.peek == Some(3)
            >>> assert itr.peek == Some(3)
            >>> assert itr.next() == Some(3)
            >>> assert itr.peek == nil
            >>> assert itr.next() == nil

            >>> xs = [1, 2, 3]
            >>> itr = iterum(xs).peekable()
            >>> assert itr.peek == Some(1)
            >>> assert itr.peek == Some(1)
            >>> assert itr.next() == Some(1)
            >>> assert itr.peek == Some(2)
            >>> itr.peek = 1000
            >>> assert list(itr) == [1000, 3]
        """
        return Peekable(self)

    def position(self, predicate: Callable[[T_co], object], /) -> Option[int]:
        """
        Searches for an element in an iterum, returning its index.

        [position()][iterum.Iterum.position] takes a closure that returns `True`
        or `False`. It applies this closure to each element of the iterum, and
        if one of them returns `True`, then [position()][iterum.Iterum.position]
        returns [Some(index)][iterum.Some]. If all of them return `False`, it
        returns [nil][iterum.nil].

        [position()][iterum.Iterum.position] is short-circuiting; in other
        words, it will stop processing as soon as it finds a `True`.

        Examples:

            >>> a = [1, 2, 3]
            >>> assert iterum(a).position(lambda x: x == 2) == Some(1)
            >>> assert iterum(a).position(lambda x: x == 5) == nil


            >>> it = iterum([1, 2, 3, 4])
            >>> assert it.position(lambda x: x >= 2) == Some(1)
            >>> assert it.next() == Some(3)
            >>> assert it.position(lambda x: x == 4) == Some(0)
        """
        for i, x in enumerate(self):
            if predicate(x):
                return Some(i)
        return nil

    def product(self: Iterum[SupportsMulT]) -> Option[SupportsMulT]:
        """
        Iterates over the entire iterum, multiplying all the elements

        An empty iterum returns [nil][iterum.nil].

        Examples:
            >>> def factorial(n: int) -> int:
            ...     return iterum(range(1, n + 1)).product().unwrap_or(1)
            ...
            >>> assert factorial(0) == 1
            >>> assert factorial(1) == 1
            >>> assert factorial(5) == 120
        """
        return self.reduce(lambda acc, x: acc * x)

    def reduce(self, f: Callable[[T_co, T_co], T_co], /) -> Option[T_co]:
        """
        Reduces the elements to a single one, by repeatedly applying a reducing operation.

        If the iterum is empty, returns [nil][iterum.nil]; otherwise, returns
        the result of the reduction.

        The reducing function is a closure with two arguments: an ‘accumulator’,
        and an element. For iterums with at least one element, this is the
        same as [fold()][iterum.Iterum.fold] with the first element of the
        iterum as the initial accumulator value, folding every subsequent
        element into it.

        Examples:
            >>> reduced = iterum(range(1, 10)).reduce(lambda acc, e: acc + e).unwrap()
            >>> assert reduced == 45
        """
        first = self.next()
        if first is nil:
            return nil
        else:
            return Some(self.fold(first.unwrap(), f))

    def scan(self, init: U, f: Callable[[State[U], T_co], Option[V]], /) -> Scan[V]:
        """
        An iterum adapter which, like fold, holds internal state, but unlike
        fold, produces a new iterum.

        [scan()][iterum.Iterum.scan] takes two arguments: an initial value which
        seeds the internal state, and a closure with two arguments, the first
        being the internal state and the second an iterum element.
        The closure can assign to the internal state to share state between iterations.

        Examples:

            >>> itr = iterum([1, 2, 3, 4])
            >>> def scanner(state: State, x: int) -> Option[int]:
            ...     state.value *= x
            ...     if state.value > 6:
            ...         return nil
            ...     return Some(-state.value)
            ...
            >>> scan = itr.scan(1, scanner)
            >>> assert scan.next() == Some(-1)
            >>> assert scan.next() == Some(-2)
            >>> assert scan.next() == Some(-6)
            >>> assert scan.next() == nil
        """
        return Scan(self, init, f)

    # def size_hint ..., don't plan on implementing this one. Just use diterum if size is important

    def skip(self, n: int, /) -> Skip[T_co]:
        """
        Creates an iterum that skips the first n elements.

        [skip(n)][iterum.Iterum.skip] skips elements until n elements are
        skipped or the end of the iterum is reached (whichever happens first).
        After that, all the remaining elements are yielded. In particular, if
        the original iterum is too short, then the returned iterum is empty.

        Examples:

            >>> itr = iterum([1, 2, 3]).skip(2)
            >>> assert itr.next() == Some(3)
            >>> assert itr.next() == nil

            >>> # Skipping past end:
            >>> itr = iterum([1, 2, 3]).skip(10)
            >>> assert itr.next() == nil
            >>> assert itr.next() == nil
        """
        return Skip(self, n)

    def skip_while(self, predicate: Callable[[T_co], object], /) -> SkipWhile[T_co]:
        """
        Creates an iterum that skips elements based on a predicate.

        [skip_while()][iterum.Iterum.skip_while] takes a closure as an argument.
        It will call this closure on each element of the iterum, and ignore
        elements until it returns `False`.

        After `False` is returned, [skip_while()][iterum.Iterum.skip_while]’s
        job is over, and the rest of the elements are yielded.

        Examples:

            >>> itr = iterum([-1, 0, 1]).skip_while(lambda x: x < 0)
            >>> assert itr.next() == Some(0)
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == nil

            >>> # After first `False` condition is hit, no further elements are checked:
            >>> itr = iterum([-1, 0, 1, -3]).skip_while(lambda x: x < 0)
            >>> assert itr.next() == Some(0)
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == Some(-3)
        """
        return SkipWhile(self, predicate)

    def step_by(self, step: int, /) -> StepBy[T_co]:
        """
        Creates an iterum starting at the same point, but stepping by the
        given amount at each iteration. This always includes the first element.

        Examples:

            >>> itr = iterum([0, 1, 2, 3, 4, 5]).step_by(2)
            >>> assert itr.next() == Some(0)
            >>> assert itr.next() == Some(2)
            >>> assert itr.next() == Some(4)
            >>> assert itr.next() == nil
        """
        return StepBy(self, step)

    def sum(self: Iterum[SupportsSumNoDefaultT]) -> Option[SupportsSumNoDefaultT]:
        """
        Sums the elements of an iterum.

        Takes each element, adds them together, and returns the result.

        An empty iterum returns [nil][iterum.nil].

        Examples:

            >>> a = [1, 2, 3]
            >>> sum_ = iterum(a).sum().unwrap_or(0)
            >>> assert sum_ == 6

            >>> sum_ = iterum([]).sum().unwrap_or(0)
            >>> assert sum_ == 0
        """
        # NOTE: This forces users to pick a default or suffer the unwrapping consequences
        # a more reasonable interface since an implicit default isn't a thing
        first = self.next()
        if first is nil:
            return nil

        return Some(sum(self, start=first.unwrap()))

    def take(self, n: int, /) -> Take[T_co]:
        """
        Creates an iterum that yields the first n elements, or fewer if the
        underlying iterum ends sooner.

        [take(n)][iterum.Iterum.take] yields elements until n elements are
        yielded or the end of the iterum is reached (whichever happens first).
        The returned iterum is a prefix of length n if the original iterum
        contains at least n elements, otherwise it contains all of the (fewer
        than n) elements of the original iterum.

        Examples:

            >>> a = [1, 2, 3]
            >>> itr = iterum(a).take(2)
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == Some(2)
            >>> assert itr.next() == nil


            >>> a = [1, 2, 3]
            >>> itr = iterum(a).take(2)
            >>> assert list(itr) == [1, 2]
            >>> assert itr.next() == nil


            >>> # Truncate an infinite iterum:
            >>> def count_forever():
            ...     i = 0
            ...     while True:
            ...         yield i
            ...         i += 1
            ...
            >>> itr = iterum(count_forever()).take(3)
            >>> assert itr.next() == Some(0)
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == Some(2)
            >>> assert itr.next() == nil

            >>> # Taking more than you have:
            >>> itr = iterum([1, 2]).take(5)
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == Some(2)
            >>> assert itr.next() == nil
        """
        return Take(self, n)

    def take_while(self, predicate: Callable[[T_co], object], /) -> TakeWhile[T_co]:
        """
        Creates an iterum that yields elements based on a predicate.

        [take_while()][iterum.Iterum.take_while] takes a closure as an argument.
        It will call this closure on each element of the iterum, and yield
        elements while it returns `True`.

        After `False` is returned, [take_while()][iterum.Iterum.take_while]’s
        job is over, and the rest of the elements are ignored.

        Examples:

            >>> a = [-1, 0, 1]
            >>> itr = iterum(a).take_while(lambda x: x < 0)
            >>> assert itr.next() == Some(-1)
            >>> assert itr.next() == nil

            >>> # Stop after first `False`:
            >>> a = [-1, 0, 1, -2]
            >>> itr = iterum(a).take_while(lambda x: x < 0)
            >>> assert itr.next() == Some(-1)
            >>> assert itr.next() == nil
        """
        return TakeWhile(self, predicate)

    def try_fold(
        self,
        init: U,
        f: Callable[[U, T_co], U],
        /,
        *,
        exception: type[BaseException] | tuple[type[BaseException], ...] = Exception,
    ) -> Option[U]:
        """
        An iterum method that applies a function as long as it returns
        successfully, producing a single, final value.

        [try_fold()][iterum.Iterum.try_fold] takes two arguments: an initial
        value, and a closure with two arguments: an ‘accumulator’, and an
        element. The closure either returns successfully, with the value that
        the accumulator should have for the next iteration, or it raises an
        exception which short-circuits the iteration.

        Examples:

            >>> def checked_add_i8(lhs: int, rhs: int) -> int:
            ...     value = lhs + rhs
            ...     if -128 <= value <= 127:
            ...         return value
            ...     else:
            ...         raise ValueError("Overflow!")
            ...
            >>> a = [1, 2, 3]
            >>> sum = iterum(a).try_fold(0, checked_add_i8)
            >>> assert sum == Some(6)

            >>> # short-circuit after a failure:
            >>> it = iterum([10, 20, 30, 100, 40, 50])
            >>> sum = it.try_fold(0, checked_add_i8)
            >>> assert sum == nil
            >>> assert list(it) == [40, 50]
        """
        acc = init
        for x in self:
            try:
                acc = f(acc, x)
            except exception:
                return nil

        return Some(acc)

    # This would be the same as a for each...
    # def try_for_each(self, f: Callable[[T], object], /) -> None:
    #     for x in self:
    #         try:
    #             f(x)
    #         except Exception:
    #             return

    @overload
    def unzip(self: Iterum[tuple[U, V]], /) -> tuple[list[U], list[V]]:
        ...

    @overload
    def unzip(
        self: Iterum[tuple[U, V]], container: type[list], /
    ) -> tuple[list[U], list[V]]:
        ...

    @overload
    def unzip(
        self: Iterum[tuple[U, V]], container: type[set], /
    ) -> tuple[set[U], set[V]]:
        ...

    @overload
    def unzip(
        self: Iterum[tuple[U, V]], container: type[tuple], /
    ) -> tuple[tuple[U, ...], tuple[V, ...]]:
        ...

    @overload
    def unzip(
        self: Iterum[tuple[object, object]],
        container: Callable[[Iterable[object]], U],
        /,
    ) -> tuple[U, U]:
        ...

    def unzip(
        self: Iterum[tuple[object, object]],
        container: Callable[[Iterable[object]], U] = list,
        /,
    ) -> tuple[U, U]:
        """
        Converts an iterum of pairs into a pair of containers.

        [unzip()][iterum.Iterum.unzip] consumes an entire iterum of pairs,
        producing two collections: one from the left elements of the pairs, and
        one from the right elements.

        This function is, in some sense, the opposite of [zip][iterum.Iterum.zip].

        Examples:

            >>> a = [(1, 2), (3, 4), (5, 6)]
            >>> left, right = iterum(a).unzip()
            >>> assert left == [1, 3, 5]
            >>> assert right == [2, 4, 6]
        """
        left, right = map(container, zip(*self))
        return left, right

    def zip(self, other: Iterable[U], /) -> Zip[T_co, U]:
        """
        ‘Zips up’ two iterables into a single iterum of pairs.

        [zip()][iterum.Iterum.zip] returns a new iterum that will iterate over
        two other iterables, returning a tuple where the first element comes
        from the first iterable, and the second element comes from the second iterable.

        If either iterable returns [nil][iterum.nil], next from the zipped
        iterum will return [nil][iterum.nil]. If the zipped iterum has no
        more elements to return then each further attempt to advance it will
        first try to advance the first iterable at most one time and if it still
        yielded an item try to advance the second iterable at most one time.

        To ‘undo’ the result of zipping up two iterables, see [unzip][iterum.Iterum.unzip].

        Examples:

            >>> a1 = [1, 2, 3]
            >>> a2 = [4, 5, 6]
            >>> itr = iterum(a1).zip(a2)
            >>> assert itr.next() == Some((1, 4))
            >>> assert itr.next() == Some((2, 5))
            >>> assert itr.next() == Some((3, 6))
            >>> assert itr.next() == nil

            >>> # zip smaller with larger:
            >>> def count_forever():
            ...     i = 0
            ...     while True:
            ...         yield i
            ...         i += 1
            ...
            >>> cf_itr = iterum(count_forever())
            >>> foo_itr = iterum("foo")
            >>> zip_itr = foo_itr.zip(cf_itr)
            >>> assert zip_itr.next() == Some(("f", 0))
            >>> assert zip_itr.next() == Some(("o", 1))
            >>> assert zip_itr.next() == Some(("o", 2))
            >>> assert zip_itr.next() == nil
            >>> assert foo_itr.next() == nil
            >>> assert cf_itr.next() == Some(3)

            >>> # zip larger with smaller:
            >>> cf_itr = iterum(count_forever())
            >>> foo_itr = iterum("foo")
            >>> zip_itr = cf_itr.zip(foo_itr)
            >>> assert zip_itr.next() == Some((0, "f"))
            >>> assert zip_itr.next() == Some((1, "o"))
            >>> assert zip_itr.next() == Some((2, "o"))
            >>> assert zip_itr.next() == nil
            >>> assert foo_itr.next() == nil
            >>> assert cf_itr.next() == Some(4)
        """
        return Zip(self, other)


def _try_next(itr: Iterator[T], /) -> Option[T]:
    try:
        nxt = next(itr)
    except StopIteration:
        return nil
    else:
        return Some(nxt)


class _IterumAdapter(Iterum[T_co]):
    __slots__ = ()
    _iter: Iterator[T_co]

    def next(self) -> Option[T_co]:
        return _try_next(self._iter)


class Chain(_IterumAdapter[T_co]):
    __slots__ = ("_iter",)

    def __init__(self, *__iterables: Iterable[T_co]) -> None:
        self._iter = itertools.chain(*__iterables)


class Cycle(_IterumAdapter[T_co]):
    __slots__ = ("_iter",)

    def __init__(self, __iterable: Iterable[T_co]) -> None:
        self._iter = itertools.cycle(__iterable)


class Enumerate(_IterumAdapter[tuple[int, T_co]]):
    __slots__ = ("_iter",)

    def __init__(self, __iterable: Iterable[T_co], /) -> None:
        self._iter = builtins.enumerate(__iterable)


class Filter(_IterumAdapter[T_co]):
    __slots__ = ("_iter",)

    def __init__(
        self, __iterable: Iterable[T_co], predicate: Callable[[T_co], object], /
    ) -> None:
        self._iter = builtins.filter(predicate, __iterable)


class FlatMap(_IterumAdapter[T_co]):
    __slots__ = ("_iter",)

    def __init__(
        self, __iterable: Iterable[U], f: Callable[[U], Iterable[T_co]], /
    ) -> None:
        self._iter = iterum(__iterable).map(f).flatten()


class FilterMap(Iterum[T_co]):
    __slots__ = ("_iter", "_predicate")

    def __init__(
        self, __iterable: Iterable[U], predicate: Callable[[U], Option[T_co]], /
    ) -> None:
        self._iter = iterum(__iterable)
        self._predicate = predicate

    def next(self) -> Option[T_co]:
        while True:
            x = self._iter.next()
            if x.is_nil():
                return nil

            r = self._predicate(x.unwrap())
            if r.is_some():
                return r


class Flatten(_IterumAdapter[T_co]):
    __slots__ = ("_iter",)

    def __init__(self, __iterable: Iterable[Iterable[T_co]], /) -> None:
        self._iter = iter(y for x in __iterable for y in x)


class Fuse(Iterum[T_co]):
    __slots__ = ("_iter", "_fuse")

    def __init__(self, __iterable: Iterable[T_co]) -> None:
        self._iter = iterum(__iterable)
        self._fuse = True

    def next(self) -> Option[T_co]:
        if not self._fuse:
            return nil

        nxt = self._iter.next()
        if nxt.is_nil():
            self._fuse = False
            return nil

        return nxt


class Inspect(Iterum[T_co]):
    __slots__ = ("_iter", "_f")

    def __init__(
        self, __iterable: Iterable[T_co], f: Callable[[T_co], object], /
    ) -> None:
        self._iter = iterum(__iterable)
        self._f = f

    def next(self) -> Option[T_co]:
        nxt = self._iter.next()
        nxt.map(self._f)
        return nxt


class Map(Iterum[T_co]):
    __slots__ = ("_iter", "_f")

    def __init__(self, __iterable: Iterable[U], f: Callable[[U], T_co], /) -> None:
        self._iter = iterum(__iterable)
        self._f = f

    def next(self) -> Option[T_co]:
        return self._iter.next().map(self._f)


class MapWhile(Iterum[T_co]):
    __slots__ = ("_iter", "_predicate", "_fuse")

    def __init__(
        self, __iterable: Iterable[U], predicate: Callable[[U], Option[T_co]], /
    ) -> None:
        self._iter = iterum(__iterable)
        self._predicate = predicate
        self._fuse = True

    def next(self) -> Option[T_co]:
        if not self._fuse:
            return nil

        r = self._iter.next().map(self._predicate).flatten()
        if r.is_nil():
            self._fuse = False

        return r


class Peekable(Iterum[T_co]):
    __slots__ = ("_iter", "_peek")

    def __init__(self, __iterable: Iterable[T_co], /) -> None:
        self._iter = iterum(__iterable)
        self._peek: Option[T_co] | NotSetType = NotSet

    def next(self) -> Option[T_co]:
        if isinstance(self._peek, NotSetType):
            return self._iter.next()
        elif self._peek is nil:
            return nil
        else:
            nxt, self._peek = self._peek, NotSet
            return nxt

    @property
    def peek(self) -> Option[T_co]:
        if isinstance(self._peek, NotSetType):
            self._peek = self.next()

        return self._peek

    @peek.setter
    def peek(self, value: T_co) -> None:  # type: ignore | reason: still need to constrain input param type
        if self.peek.is_nil():
            raise IndexError("Cannot set peek value past end of the iterum")

        self._peek = Some(value)


@dataclass
class State(Generic[T]):
    """
    Simple class which holds some mutable state.
    """

    value: T
    """
    current value of the state
    """


class Scan(Iterum[T_co]):
    __slots__ = ("_iter", "_state", "_f")

    def __init__(
        self,
        __iterable: Iterable[U],
        init: V,
        f: Callable[[State[V], U], Option[T_co]],
        /,
    ):
        self._iter = iterum(__iterable)
        self._state = State(init)
        self._f = f

    def next(self) -> Option[T_co]:
        return self._iter.next().map(lambda val: self._f(self._state, val)).flatten()


class Skip(Iterum[T_co]):
    __slots__ = ("_iter", "_n")

    def __init__(
        self,
        __iterable: Iterable[T_co],
        n: int,
        /,
    ) -> None:
        self._iter = iterum(__iterable)
        self._n = n

    def next(self) -> Option[T_co]:
        if self._n:
            self._iter.nth(self._n - 1)
            self._n = 0

        return self._iter.next()


class SkipWhile(Iterum[T_co]):
    __slots__ = ("_iter", "_predicate", "_fuse")

    def __init__(
        self,
        __iterable: Iterable[T_co],
        predicate: Callable[[T_co], object],
        /,
    ) -> None:
        self._iter = iterum(__iterable)
        self._predicate = predicate
        self._fuse = True

    def next(self) -> Option[T_co]:
        if not self._fuse:
            return self._iter.next()

        nxt = nil
        while self._fuse:
            nxt = self._iter.next()
            self._fuse = nxt.is_some_and(self._predicate)

        return nxt


class StepBy(Iterum[T_co]):
    __slots__ = ("_iter", "_step")

    def __init__(self, __iterable: Iterable[T_co], step: int, /) -> None:
        if step <= 0:
            raise ValueError(f"Step must be positive, provided: {step}")

        self._iter = iterum(__iterable).enumerate()
        self._step = step

    def next(self) -> Option[T_co]:
        idx, nxt = self._iter.next().unzip()
        while nxt.is_some() and idx.is_some_and(lambda idx: idx % self._step):
            idx, nxt = self._iter.next().unzip()

        return nxt


class Take(Iterum[T_co]):
    __slots__ = ("_iter", "_max", "_idx")

    def __init__(self, __iterable: Iterable[T_co], n: int, /) -> None:
        self._iter = iterum(__iterable)
        self._max = n
        self._idx = 0

    def next(self) -> Option[T_co]:
        if self._idx >= self._max:
            return nil

        self._idx += 1
        return self._iter.next()


class TakeWhile(Iterum[T_co]):
    __slots__ = ("_iter", "_predicate")

    def __init__(
        self, __iterable: Iterable[T_co], predicate: Callable[[T_co], object], /
    ) -> None:
        self._iter = iterum(__iterable)
        self._predicate = predicate

    def next(self) -> Option[T_co]:
        nxt = self._iter.next()
        if nxt.is_some_and(self._predicate):
            return nxt
        return nil


class Zip(_IterumAdapter[tuple[U, V]]):
    __slots__ = ("_iter",)

    def __init__(self, __iterable: Iterable[U], other: Iterable[V], /) -> None:
        self._iter = zip(__iterable, other)


class iterum(Iterum[T_co]):
    """
    Implements an [Iterum][iterum.Iterum] interface from an iterable object.

    Examples:
        >>> itr = iterum([1, 2])
        >>> assert itr.next() == Some(1)
        >>> assert itr.next() == Some(2)
        >>> assert itr.next() == nil

        >>> itr = iterum([1, 2, 3, 4])
        >>> assert itr.fold(0, lambda acc, x: acc + x) == 10

        >>> x = range(5)
        >>> y = (
        ...     iterum(x)
        ...     .map(lambda x: x**2 + 1)
        ...     .filter(lambda x: x % 2)
        ...     .collect()
        ... )
        >>> assert y == [1, 5, 17]
    """

    __slots__ = ("_iter",)

    def __init__(self, __iterable: Iterable[T_co], /) -> None:
        self._iter = iter(__iterable)

    def next(self) -> Option[T_co]:
        """
        Returns the next value in the iterable if present, otherwise [nil][iterum.nil].

        Examples:
            >>> itr = iterum([1, 2])
            >>> assert itr.next() == Some(1)
            >>> assert itr.next() == Some(2)
            >>> assert itr.next() == nil
        """
        return _try_next(self._iter)
