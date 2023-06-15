from __future__ import annotations

import builtins
import itertools
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from typing import Generic
from typing import overload
from typing import TYPE_CHECKING
from typing import TypeVar

from ._notset import NotSet
from ._notset import NotSetType
from ._option import Nil
from ._option import nil
from ._option import Option
from ._option import Some
from ._option import UnwrapNilError
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

# TODO: Idea! for double-ended iteretor functionality
# have Iter(...) return either an Iter or a DoubleEndedIter if input is a sequence
# Something similar to pathlib.Path
# then rev, rposition, etc can be implemented
# also size hint

# TODO: better to have __next__ be the abstractmethod or next?


class Iterum(Iterator[T_co]):
    def next(self) -> Option[T_co]:
        try:
            return Some(next(self))
        except StopIteration:
            return nil

    def all(self, f: Callable[[T_co], object], /) -> bool:
        return all(map(f, self))

    def any(self, f: Callable[[T_co], object], /) -> bool:
        return any(map(f, self))

    def chain(self: Iterum[T_co], other: Iterable[T_co], /) -> Chain[T_co]:
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
        return container(self)

    def count(self) -> int:
        last = self.enumerate().last()
        return last.map_or(0, lambda last: last[0] + 1)

    def cycle(self: Iterum[T_co], /) -> Cycle[T_co]:
        return Cycle(self)

    def enumerate(self: Iterum[T_co], /) -> Enumerate[T_co]:
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
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp == Ordering.Equal

    def filter(
        self: Iterum[T_co], predicate: Callable[[T_co], object], /
    ) -> Filter[T_co]:
        return Filter(self, predicate)

    def filter_map(
        self: Iterum[T_co], predicate: Callable[[T_co], Option[U]], /
    ) -> FilterMap[U]:
        return FilterMap(self, predicate)

    def find(self, predicate: Callable[[T_co], object], /) -> Option[T_co]:
        for x in self:
            if predicate(x):
                return Some(x)
        return nil

    def find_map(self, predicate: Callable[[T_co], Option[U]], /) -> Option[U]:
        return self.filter_map(predicate).next()

    def flat_map(self, f: Callable[[T_co], Iterable[U]], /) -> FlatMap[U]:
        return FlatMap(self, f)

    def flatten(self: Iterum[Iterable[U]]) -> Flatten[U]:
        return Flatten(self)

    def fold(self, init: U, f: Callable[[U, T_co], U], /) -> U:
        acc = init
        for x in self:
            acc = f(acc, x)
        return acc

    def for_each(self, f: Callable[[T_co], object], /) -> None:
        for x in self:
            f(x)

    def fuse(self) -> Fuse[T_co]:
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
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp == Ordering.Greater

    def inspect(self, f: Callable[[T_co], object], /) -> Inspect[T_co]:
        return Inspect(self, f)

    def last(self) -> Option[T_co]:
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
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp == Ordering.Less

    def map(self, f: Callable[[T_co], U], /) -> Map[U]:
        return Map(self, f)

    def map_while(self, predicate: Callable[[T_co], Option[U]], /) -> MapWhile[U]:
        return MapWhile(self, predicate)

    def max(
        self: Iterum[SupportsRichComparisonT],
    ) -> Option[SupportsRichComparisonT]:
        try:
            return Some(builtins.max(self))
        except ValueError:
            return nil

    def max_by(self, compare: Callable[[T_co, T_co], Ordering], /) -> Option[T_co]:
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
        def compare(x, y) -> Ordering:
            fx = f(x)
            fy = f(y)
            return Ordering.cmp(fx, fy)

        return self.max_by(compare)

    def min(
        self: Iterum[SupportsRichComparisonT],
    ) -> Option[SupportsRichComparisonT]:
        try:
            return Some(builtins.min(self))
        except ValueError:
            return nil

    def min_by(self, compare: Callable[[T_co, T_co], Ordering], /) -> Option[T_co]:
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
        eq = self.eq(other)  # type: ignore | reason: ask for forgiveness not permission
        return not eq

    def nth(self, n: int, /) -> Option[T_co]:
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
        matches, notmatches = [], []
        for x in self:
            matches.append(x) if f(x) else notmatches.append(x)

        return container(matches), container(notmatches)

    def peekable(self) -> Peekable[T_co]:
        return Peekable(self)

    def position(self, predicate: Callable[[T_co], object], /) -> Option[int]:
        for i, x in enumerate(self):
            if predicate(x):
                return Some(i)
        return nil

    def product(self: Iterum[SupportsMulT]) -> Option[SupportsMulT]:
        return self.reduce(lambda acc, x: acc * x)

    def reduce(self, f: Callable[[T_co, T_co], T_co], /) -> Option[T_co]:
        first = self.next()
        if first is nil:
            return nil
        else:
            return Some(self.fold(first.unwrap(), f))

    # TODO: def reversed ... , how do we include type information for whether we are reversible?
    # TODO: def rposition ... , how do we include type information for whether we are reversible?

    def scan(self, init: U, f: Callable[[State[U], T_co], Option[V]], /) -> Scan[V]:
        return Scan(self, init, f)

    # TODO: def size_hint ...

    def skip(self, n: int, /) -> Skip[T_co]:
        return Skip(self, n)

    def skip_while(self, predicate: Callable[[T_co], object], /) -> SkipWhile[T_co]:
        return SkipWhile(self, predicate)

    def step_by(self, step: int, /) -> StepBy[T_co]:
        return StepBy(self, step)

    def sum(self: Iterum[SupportsSumNoDefaultT]) -> Option[SupportsSumNoDefaultT]:
        # NOTE: This forces users to pick a default or suffer the unwrapping consequences
        # a more reasonable interface since an implicit default isn't a thing
        first = self.next()
        if first is nil:
            return nil

        return Some(sum(self, start=first.unwrap()))

    def take(self, n: int, /) -> Take[T_co]:
        return Take(self, n)

    def take_while(self, predicate: Callable[[T_co], object], /) -> TakeWhile[T_co]:
        return TakeWhile(self, predicate)

    def try_fold(
        self,
        init: U,
        f: Callable[[U, T_co], U],
        /,
        *,
        exception: type[BaseException] | tuple[type[BaseException], ...] = Exception,
    ) -> Option[U]:
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
        left, right = map(container, zip(*self))
        return left, right

    def zip(self, other: Iterable[U], /) -> Zip[T_co, U]:
        return Zip(self, other)


class Chain(Iterum[T_co]):
    __slots__ = ("_iter",)

    def __init__(self, *__iterables: Iterable[T_co]) -> None:
        self._iter = itertools.chain(*__iterables)

    def __next__(self) -> T_co:
        return next(self._iter)


class Cycle(Iterum[T_co]):
    __slots__ = ("_iter",)

    def __init__(self, __iterable: Iterable[T_co]) -> None:
        self._iter = itertools.cycle(__iterable)

    def __next__(self) -> T_co:
        return next(self._iter)


class Enumerate(Iterum[tuple[int, T_co]]):
    __slots__ = ("_iter",)

    def __init__(self, __iterable: Iterable[T_co], /) -> None:
        self._iter = builtins.enumerate(__iterable)

    def __next__(self) -> tuple[int, T_co]:
        return next(self._iter)


class Filter(Iterum[T_co]):
    __slots__ = ("_iter",)

    def __init__(
        self, __iterable: Iterable[T_co], predicate: Callable[[T_co], object], /
    ) -> None:
        self._iter = builtins.filter(predicate, __iterable)

    def __next__(self) -> T_co:
        return next(self._iter)


class FlatMap(Iterum[T_co]):
    __slots__ = ("_iter", "_f")

    def __init__(
        self, __iterable: Iterable[U], f: Callable[[U], Iterable[T_co]], /
    ) -> None:
        self._iter = iterum(__iterable).map(f).flatten()

    def __next__(self) -> T_co:
        return next(self._iter)


class FilterMap(Iterum[T_co]):
    __slots__ = ("_iter", "_predicate")

    def __init__(
        self, __iterable: Iterable[U], predicate: Callable[[U], Option[T_co]], /
    ) -> None:
        self._iter = iter(__iterable)
        self._predicate = predicate

    def __next__(self) -> T_co:
        while True:
            x = next(self._iter)
            r = self._predicate(x)
            if r.is_some():
                return r.unwrap()


class Flatten(Iterum[T_co]):
    __slots__ = ("_iter",)

    def __init__(self, __iterable: Iterable[Iterable[T_co]], /) -> None:
        self._iter = iter(y for x in __iterable for y in x)

    def __next__(self) -> T_co:
        return next(self._iter)


class Fuse(Iterum[T_co]):
    __slots__ = ("_iter", "_blown")

    def __init__(self, __iterable: Iterable[T_co]) -> None:
        self._iter = iterum(__iterable)
        self._blown = False

    def __next__(self) -> T_co:
        if self._blown:
            raise StopIteration()

        nxt = self._iter.next()
        if nxt is nil:
            self._blown = True
            raise StopIteration()

        return nxt.unwrap()


class Inspect(Iterum[T_co]):
    __slots__ = ("_iter", "_blown")

    def __init__(
        self, __iterable: Iterable[T_co], f: Callable[[T_co], object], /
    ) -> None:
        self._iter = iterum(__iterable)
        self._f = f

    def __next__(self) -> T_co:
        nxt = next(self._iter)
        self._f(nxt)
        return nxt


class Map(Iterum[T_co]):
    __slots__ = ("_iter", "_f")

    def __init__(self, __iterable: Iterable[U], f: Callable[[U], T_co], /) -> None:
        self._iter = iterum(__iterable)
        self._f = f

    def __next__(self) -> T_co:
        nxt = next(self._iter)
        return self._f(nxt)


class MapWhile(Iterum[T_co]):
    __slots__ = ("_iter", "_predicate")

    def __init__(
        self, __iterable: Iterable[U], predicate: Callable[[U], Option[T_co]], /
    ) -> None:
        self._iter = iterum(__iterable)
        self._predicate = predicate

    def __next__(self) -> T_co:
        nxt = next(self._iter)
        r = self._predicate(nxt)
        if r is nil:
            raise StopIteration()
        return r.unwrap()


class Peekable(Iterum[T_co]):
    __slots__ = ("_iter", "_peek")

    def __init__(self, __iterable: Iterable[T_co], /) -> None:
        self._iter = iter(__iterable)
        self._peek: Option[T_co] | NotSetType = NotSet

    def __next__(self) -> T_co:
        if isinstance(self._peek, NotSetType):
            return next(self._iter)
        elif self._peek is nil:
            raise StopIteration()
        else:
            nxt = self._peek.unwrap()
            self._peek = NotSet
            return nxt

    @property
    def peek(self) -> Option[T_co]:
        if isinstance(self._peek, NotSetType):
            self._peek = self.next()

        return self._peek

    @peek.setter
    def peek(self, value: T_co) -> None:  # type: ignore | reason: still need to constrain input param type
        if self.peek.is_nil():
            raise IndexError("Cannot set peek value past end of the iterator")

        self._peek = Some(value)


class State(Generic[T]):
    __slots__ = ("_value",)

    def __init__(self, value: T, /) -> None:
        self._value = value

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, value: T) -> None:
        self._value = value


class Scan(Iterum[T_co]):
    __slots__ = ("_iter", "_state", "_f")

    def __init__(
        self,
        __iterable: Iterable[U],
        init: V,
        f: Callable[[State[V], U], Option[T_co]],
        /,
    ):
        self._iter = iter(__iterable)
        self._state = State(init)
        self._f = f

    def __next__(self) -> T_co:
        nxt = next(self._iter)
        r = self._f(self._state, nxt)
        try:
            return r.unwrap()
        except UnwrapNilError:
            raise StopIteration()


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

    def __next__(self) -> T_co:
        if self._n:
            self._iter.nth(self._n - 1)
            self._n = 0

        return next(self._iter)


class SkipWhile(Iterum[T_co]):
    __slots__ = ("_iter", "_predicate", "_fuse")

    def __init__(
        self,
        __iterable: Iterable[T_co],
        predicate: Callable[[T_co], object],
        /,
    ) -> None:
        self._iter = iter(__iterable)
        self._predicate = predicate
        self._fuse = True

    def __next__(self) -> T_co:
        if not self._fuse:
            return next(self._iter)

        while self._fuse:
            nxt = next(self._iter)
            self._fuse = bool(self._predicate(nxt))

        return nxt  # type: ignore | reason: incorrectly reports unbound variable


class StepBy(Iterum[T_co]):
    __slots__ = ("_iter", "_step")

    def __init__(self, __iterable: Iterable[T_co], step: int, /) -> None:
        if step <= 0:
            raise ValueError(f"Step must be positive, provided: {step}")

        self._iter = enumerate(__iterable)
        self._step = step

    def __next__(self) -> T_co:
        idx, nxt = next(self._iter)
        while idx % self._step:
            idx, nxt = next(self._iter)

        return nxt


class Take(Iterum[T_co]):
    __slots__ = ("_iter", "_max", "_idx")

    def __init__(self, __iterable: Iterable[T_co], n: int, /) -> None:
        self._iter = iterum(__iterable)
        self._max = n
        self._idx = 0

    def __next__(self) -> T_co:
        if self._idx >= self._max:
            raise StopIteration()

        self._idx += 1
        return next(self._iter)


class TakeWhile(Iterum[T_co]):
    __slots__ = ("_iter", "_predicate")

    def __init__(
        self, __iterable: Iterable[T_co], predicate: Callable[[T_co], object], /
    ) -> None:
        self._iter = iterum(__iterable)
        self._predicate = predicate

    def __next__(self) -> T_co:
        nxt = next(self._iter)
        if not self._predicate(nxt):
            raise StopIteration()
        return nxt


class Zip(Iterum[tuple[U, V]]):
    __slots__ = ("_iter",)

    def __init__(self, __iterable: Iterable[U], other: Iterable[V], /) -> None:
        self._iter = zip(__iterable, other)

    def __next__(self) -> tuple[U, V]:
        return next(self._iter)


class iterum(Iterum[T_co]):
    def __init__(self, __iterable: Iterable[T_co], /) -> None:
        self._iter = iter(__iterable)

    def __next__(self) -> T_co:
        return next(self._iter)
