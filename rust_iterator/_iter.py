from __future__ import annotations

import builtins
import itertools
from typing import Callable
from typing import Generic
from typing import Iterable
from typing import Iterator
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
    from ._type_helpers import SupportsMulT
    from ._type_helpers import SupportsRichComparisonT
    from ._type_helpers import SupportsSumNoDefaultT


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


# TODO: Idea! for double-ended iteretor functionality
# have Iter(...) return either an Iter or a DoubleEndedIter if input is a sequence
# Something similar to pathlib.Path
# then rev, rposition, etc can be implemented
# also size hint


class Iter(Generic[T]):
    def __init__(self, __iterable: Iterable[T], /) -> None:
        self._iter = iter(__iterable)

    def __iter__(self) -> Iterator[T]:
        return self._iter

    def __next__(self) -> T:
        return next(self._iter)

    def next(self) -> Option[T]:
        try:
            return Some(next(self))
        except StopIteration:
            return nil

    def all(self, f: Callable[[T], bool], /) -> bool:
        return all(map(f, self))

    def any(self, f: Callable[[T], bool], /) -> bool:
        return any(map(f, self))

    def chain(self, other: Iterable[T], /) -> Iter[T]:
        return Iter(itertools.chain(self, other))

    @overload
    def cmp(
        self: Iter[SupportsRichComparisonT], other: Iterable[object], /
    ) -> Ordering:
        ...

    @overload
    def cmp(
        self: Iter[object], other: Iterable[SupportsRichComparisonT], /
    ) -> Ordering:
        ...

    def cmp(
        self: Iter[SupportsRichComparisonT] | Iter[object],
        other: Iterable[object] | Iterable[SupportsRichComparisonT],
        /,
    ) -> Ordering:
        other = Iter(other)
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
    def collect(self, container: type[list], /) -> list[T]:
        ...

    @overload
    def collect(self, container: type[set], /) -> set[T]:
        ...

    @overload
    def collect(self, container: type[tuple], /) -> tuple[T]:
        ...

    @overload
    def collect(self, container: Callable[[Iterable[T]], U], /) -> U:
        ...

    def collect(self, container: Callable[[Iterable[T]], U], /) -> U:
        return container(self)

    def count(self) -> int:
        last = self.enumerate().last()
        return last.map_or(0, lambda last: last[0] + 1)

    def cycle(self) -> Iter[T]:
        return Iter(itertools.cycle(self))

    def enumerate(self) -> Iter[tuple[int, T]]:
        return Iter(enumerate(self))

    @overload
    def eq(self: Iter[SupportsRichComparisonT], other: Iterable[object], /) -> bool:
        ...

    @overload
    def eq(self: Iter[object], other: Iterable[SupportsRichComparisonT], /) -> bool:
        ...

    def eq(
        self: Iter[SupportsRichComparisonT] | Iter[object],
        other: Iterable[object] | Iterable[SupportsRichComparisonT],
        /,
    ) -> bool:
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp == Ordering.Equal

    def filter(self, predicate: Callable[[T], bool], /) -> Iter[T]:
        return Iter(filter(predicate, self))

    def filter_map(self, predicate: Callable[[T], Option[U]], /) -> Iter[U]:
        return Iter(FilterMap(self, predicate))

    def find(self, predicate: Callable[[T], bool], /) -> Option[T]:
        for x in self:
            if predicate(x):
                return Some(x)
        return nil

    def find_map(self, predicate: Callable[[T], Option[U]], /) -> Option[U]:
        return self.filter_map(predicate).next()

    def flat_map(self, f: Callable[[T], Iterable[U]], /) -> Iter[U]:
        return self.map(f).flatten()

    def flatten(self: Iter[Iterable[U]]) -> Iter[U]:
        return Iter(y for x in self for y in x)

    def fold(self, init: U, f: Callable[[U, T], U], /) -> U:
        acc = init
        for x in self:
            acc = f(acc, x)
        return acc

    def for_each(self, f: Callable[[T], object], /) -> None:
        for x in self:
            f(x)

    def fuse(self) -> Iter[T]:
        return Iter(Fuse(self))

    @overload
    def ge(self: Iter[SupportsRichComparisonT], other: Iterable[object], /) -> bool:
        ...

    @overload
    def ge(self: Iter[object], other: Iterable[SupportsRichComparisonT], /) -> bool:
        ...

    def ge(
        self: Iter[SupportsRichComparisonT] | Iter[object],
        other: Iterable[object] | Iterable[SupportsRichComparisonT],
        /,
    ) -> bool:
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp in (Ordering.Greater, Ordering.Equal)

    @overload
    def gt(self: Iter[SupportsRichComparisonT], other: Iterable[object], /) -> bool:
        ...

    @overload
    def gt(self: Iter[object], other: Iterable[SupportsRichComparisonT], /) -> bool:
        ...

    def gt(
        self: Iter[SupportsRichComparisonT] | Iter[object],
        other: Iterable[object] | Iterable[SupportsRichComparisonT],
        /,
    ) -> bool:
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp == Ordering.Greater

    def inspect(self, f: Callable[[T], object], /) -> Iter[T]:
        def predicate(x: T) -> T:
            f(x)
            return x

        return self.map(predicate)

    def last(self) -> Option[T]:
        last = nil
        while (nxt := self.next()) is not nil:
            last = nxt

        return last

    @overload
    def le(self: Iter[SupportsRichComparisonT], other: Iterable[object], /) -> bool:
        ...

    @overload
    def le(self: Iter[object], other: Iterable[SupportsRichComparisonT], /) -> bool:
        ...

    def le(
        self: Iter[SupportsRichComparisonT] | Iter[object],
        other: Iterable[object] | Iterable[SupportsRichComparisonT],
        /,
    ) -> bool:
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp in (Ordering.Less, Ordering.Equal)

    @overload
    def lt(self: Iter[SupportsRichComparisonT], other: Iterable[object], /) -> bool:
        ...

    @overload
    def lt(self: Iter[object], other: Iterable[SupportsRichComparisonT], /) -> bool:
        ...

    def lt(
        self: Iter[SupportsRichComparisonT] | Iter[object],
        other: Iterable[object] | Iterable[SupportsRichComparisonT],
        /,
    ) -> bool:
        cmp = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        return cmp == Ordering.Less

    def map(self, f: Callable[[T], U], /) -> Iter[U]:
        return Iter(map(f, self))

    def map_while(self, predicate: Callable[[T], Option[U]], /) -> Iter[U]:
        return Iter(MapWhile(self, predicate))

    def max(
        self: Iter[SupportsRichComparisonT],
    ) -> Option[SupportsRichComparisonT]:
        try:
            return Some(builtins.max(self))
        except ValueError:
            return nil

    def max_by(self, compare: Callable[[T, T], Ordering], /) -> Option[T]:
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
        self, f: Callable[[T], SupportsRichComparisonT], /
    ) -> Option[SupportsRichComparisonT]:
        return self.map(f).max()

    def min(
        self: Iter[SupportsRichComparisonT],
    ) -> Option[SupportsRichComparisonT]:
        try:
            return Some(builtins.min(self))
        except ValueError:
            return nil

    def min_by(self, compare: Callable[[T, T], Ordering], /) -> Option[T]:
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
        self, f: Callable[[T], SupportsRichComparisonT], /
    ) -> Option[SupportsRichComparisonT]:
        return self.map(f).min()

    @overload
    def ne(self: Iter[SupportsRichComparisonT], other: Iterable[object], /) -> bool:
        ...

    @overload
    def ne(self: Iter[object], other: Iterable[SupportsRichComparisonT], /) -> bool:
        ...

    def ne(
        self: Iter[SupportsRichComparisonT] | Iter[object],
        other: Iterable[object] | Iterable[SupportsRichComparisonT],
        /,
    ) -> bool:
        eq = self.eq(other)  # type: ignore | reason: ask for forgiveness not permission
        return not eq

    def nth(self, n: int, /) -> Option[T]:
        for i, x in enumerate(self):
            if i > n:
                return nil
            if i == n:
                return Some(x)
        return nil

    @overload
    def partial_cmp(
        self: Iter[SupportsRichComparisonT], other: Iterable[object], /
    ) -> Some[Ordering]:
        ...

    @overload
    def partial_cmp(
        self: Iter[object], other: Iterable[SupportsRichComparisonT], /
    ) -> Some[Ordering]:
        ...

    @overload
    def partial_cmp(self: Iter[object], other: Iterable[object], /) -> Option[Ordering]:
        ...

    def partial_cmp(
        self: Iter[SupportsRichComparisonT] | Iter[object],
        other: Iterable[object] | Iterable[SupportsRichComparisonT],
        /,
    ) -> Option[Ordering]:
        try:
            value = self.cmp(other)  # type: ignore | reason: ask for forgiveness not permission
        except TypeError:
            return nil
        else:
            return Some(value)

    def partition(self, f: Callable[[T], bool], /) -> tuple[list[T], list[T]]:
        matches, notmatches = [], []
        for x in self:
            matches.append(x) if f(x) else notmatches.append(x)

        return matches, notmatches

    def peekable(self) -> Peekable[T]:
        return Peekable(self)

    # TODO: should this simply map to an object and just rely on truthy/falsey behavior?
    def position(self, predicate: Callable[[T], bool], /) -> Option[int]:
        for i, x in enumerate(self):
            if predicate(x):
                return Some(i)
        return nil

    def product(self: Iter[SupportsMulT]) -> Option[SupportsMulT]:
        return self.reduce(lambda acc, x: acc * x)

    def reduce(self, f: Callable[[T, T], T], /) -> Option[T]:
        first = self.next()
        if first is nil:
            return nil
        else:
            return Some(self.fold(first.unwrap(), f))

    # TODO: def reversed ... , how do we include type information for whether we are reversible?
    # TODO: def rposition ... , how do we include type information for whether we are reversible?

    def scannable(self, init: U, /) -> Scannable[T, U]:
        return Scannable(self, init)

    # TODO: def size_hint ...

    def skip(self, n: int, /) -> Iter[T]:
        for _ in range(n):
            if self.next() is nil:
                break
        return self

    def skip_while(self, predicate: Callable[[T], bool], /) -> Iter[T]:
        return Iter(SkipWhile(self, predicate))

    def step_by(self, step: int, /) -> Iter[T]:
        return Iter(StepBy(self, step))

    def sum(self: Iter[SupportsSumNoDefaultT]) -> Option[SupportsSumNoDefaultT]:
        # NOTE: This forces users to pick a default or suffer the unwrapping consequences
        # a more reasonable interface since an implicit default isn't a thing
        first = self.next()
        if first is nil:
            return nil

        return Some(sum(self, start=first.unwrap()))

    def take(self, n: int, /) -> Iter[T]:
        return Iter(Take(self, n))

    def take_while(self, predicate: Callable[[T], bool], /) -> Iter[T]:
        return Iter(TakeWhile(self, predicate))

    def try_fold(
        self,
        init: U,
        f: Callable[[U, T], U],
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

    def unzip(self: Iter[tuple[U, V]], /) -> tuple[Iter[U], Iter[V]]:
        return tuple(zip(*self))

    def zip(self, other: Iterable[U], /) -> Iter[tuple[T, U]]:
        return Iter(zip(self, other))


# TODO: More careful consideration about overloading iter and/or next needs to be done


class FilterMap(Generic[T, U]):
    def __init__(
        self,
        __iterable: Iterable[T],
        predicate: Callable[[T], Option[U]],
        /,
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate

    def __iter__(self) -> Iterator[U]:
        for x in self._iter:
            r = self._predicate(x)
            if isinstance(r, Some):
                yield r.unwrap()


class Fuse(Generic[T]):
    def __init__(self, __iterable: Iterable[T]) -> None:
        self._iter = Iter(__iterable)
        self._found_nil = False

    def __iter__(self) -> Iterator[T]:
        while True:
            nxt = self._iter.next()
            if nxt is nil:
                break
            yield nxt.unwrap()


class MapWhile(Generic[T, U]):
    def __init__(
        self, __iterable: Iterable[T], predicate: Callable[[T], Option[U]], /
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate

    def __iter__(self) -> Iterator[U]:
        for x in self._iter:
            r = self._predicate(x)
            if r is nil:
                return
            yield r.unwrap()


class Peekable(Iter[T]):
    def __init__(self, __iterable: Iterable[T], /) -> None:
        self._iter = iter(__iterable)
        self._peek: Option[T] | NotSetType = NotSet

    def __iter__(self) -> Iterator[T]:
        while True:
            try:
                yield next(self)
            except StopIteration:
                return

    def __next__(self) -> T:
        if isinstance(self._peek, NotSetType):
            return next(self._iter)
        elif self._peek is nil:
            raise StopIteration()
        else:
            nxt = self._peek.unwrap()
            self._peek = NotSet
            return nxt

    @property
    def peek(self) -> Option[T]:
        if isinstance(self._peek, NotSetType):
            self._peek = self.next()

        return self._peek

    @peek.setter
    def peek(self, value: T) -> None:
        if self.peek.is_none():
            raise IndexError("Cannot set peek value past end of the iterator")

        self._peek = Some(value)


# TODO: These helper classes should be using slots


class Scannable(Iter[T], Generic[T, U]):
    def __init__(
        self,
        __iterable: Iterable[T],
        init: U,
        /,
    ) -> None:
        self._state = init
        self._iter = Iter(__iterable)

    @property
    def state(self) -> U:
        return self._state

    @state.setter
    def state(self, value: U) -> None:
        self._state = value

    def scan(self, f: Callable[[U, T], Option[V]], /) -> Scan[T, U, V]:
        return Scan(self, f)


class Scan(Iter[T], Generic[T, U, V]):
    def __init__(self, scannable: Scannable, f: Callable[[U, T], Option[V]], /):
        self._scannable = scannable
        self._f = f

    def __iter__(self) -> Iterator[V]:
        while True:
            try:
                yield next(self)
            except StopIteration:
                return

    def __next__(self) -> V:
        nxt = self._f(self._scannable.state, next(self._scannable))
        try:
            return nxt.unwrap()
        except UnwrapNilError:
            raise StopIteration()


class SkipWhile(Generic[T]):
    def __init__(
        self,
        __iterable: Iterable[T],
        predicate: Callable[[T], bool],
        /,
    ) -> None:
        self._iter = iter(__iterable)
        self._predicate = predicate

    def __iter__(self) -> Iterator[T]:
        failhit = False
        for x in self._iter:
            if failhit or (failhit := not self._predicate(x)):
                yield x

    def __next__(self) -> T:
        return next(iter(self))


class StepBy(Generic[T]):
    def __init__(self, __iterable: Iterable[T], step: int, /) -> None:
        if step <= 0:
            raise ValueError(f"Step must be positive, provided: {step}")

        self._iter = Iter(__iterable)
        self._step = step

    def __iter__(self) -> Iterator[T]:
        for i, x in enumerate(self._iter):
            if i % self._step == 0:
                yield x

    def __next__(self) -> T:
        return next(iter(self))


class Take(Generic[T]):
    def __init__(self, __iterable: Iterable[T], n: int, /) -> None:
        self._iter = Iter(__iterable)
        self._n = n

    def __iter__(self) -> Iterator[T]:
        for i, x in enumerate(self._iter):
            if i >= self._n:
                return
            yield x


class TakeWhile(Generic[T]):
    def __init__(
        self, __iterable: Iterable[T], predicate: Callable[[T], bool], /
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate

    def __iter__(self) -> Iterator[T]:
        for x in self._iter:
            if not self._predicate(x):
                return
            yield x
