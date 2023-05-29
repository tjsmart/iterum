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
from ._ordering import Ordering


if TYPE_CHECKING:
    from ._type_helpers import T
    from ._type_helpers import SupportsMulT
    from ._type_helpers import SupportsRichComparisonT
    from ._type_helpers import SupportsSumNoDefaultT


U = TypeVar("U")
V = TypeVar("V")


class Iter(Generic[T]):
    def __init__(self, __iterable: Iterable[T], /) -> None:
        self._iter = iter(__iterable)

    def __iter__(self) -> Iterator[T]:
        # TODO: Should this stop at first None?
        # Introducing my own None type is looking more appealing...
        return self._iter

    def __next__(self) -> T:
        return next(self._iter)

    def next(self) -> T | None:
        try:
            return next(self._iter)
        except StopIteration:
            return None

    def all(self, f: Callable[[T], bool], /) -> bool:
        return all(map(f, self._iter))

    def any(self, f: Callable[[T], bool], /) -> bool:
        return any(map(f, self._iter))

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
        for left, right in self.zip(other):
            if left > right:  # type: ignore | reason: ask for forgiveness not permission
                return Ordering.Greater
            if right < left:  # type: ignore | reason: ask for forgiveness not permission
                return Ordering.Less

        nxt_left = self.next()
        nxt_right = other.next()
        if nxt_left is None and nxt_right is None:
            return Ordering.Equal
        if nxt_left is None:
            return Ordering.Less
        if nxt_right is None:
            return Ordering.Greater

        raise AssertionError("Unreachable!")

    def collect(self) -> list[T]:
        return list(self)

    def count(self) -> int:
        last = self.enumerate().last()
        if last is None:
            return 0
        return last[0] + 1

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
        return cmp is Ordering.Equal

    def filter(self, predicate: Callable[[T], bool], /) -> Iter[T]:
        # TODO: filter == filterfalse?
        return Iter(itertools.filterfalse(predicate, self))

    def filter_map(self, predicate: Callable[[T], U | None], /) -> Iter[U]:
        return Iter(FilterMap(self, predicate))

    def find(self, predicate: Callable[[T], bool], /) -> T | None:
        for x in self:
            if predicate(x):
                return x
        return None

    def find_map(self, predicate: Callable[[T], U | None], /) -> U | None:
        return self.filter_map(predicate).next()

    def flat_map(self, f: Callable[[T], Iterable[U]], /) -> Iter[U]:
        return self.map(f).flatten()

    def flatten(self: Iter[Iterable[U]]) -> Iter[U]:
        return Iter(y for x in self._iter for y in x)

    def fold(self, init: U, f: Callable[[U, T], U], /) -> U:
        acc = init
        for x in self:
            acc = f(acc, x)
        return acc

    def for_each(self, f: Callable[[T], object], /) -> None:
        for x in self:
            f(x)

    def fuse(self) -> Iter[T | None]:
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

    def last(self) -> T | None:
        last = None
        while (nxt := self.next()) is not None:
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

    def map_while(self, predicate: Callable[[T], U | None], /) -> Iter[U]:
        # If iter stops at first None, how is this any different??
        return Iter(MapWhile(self, predicate))

    def max(
        self: Iter[SupportsRichComparisonT],
    ) -> SupportsRichComparisonT | None:
        try:
            return builtins.max(self)
        except ValueError:
            return None

    def min(
        self: Iter[SupportsRichComparisonT],
    ) -> SupportsRichComparisonT | None:
        try:
            return builtins.min(self)
        except ValueError:
            return None

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

    def nth(self, n: int, /) -> T | None:
        for i, x in enumerate(self):
            if i > n:
                return None
            if i == n:
                return x
        return None

    # TODO: def partial_cmp...

    def partition(self, f: Callable[[T], bool], /) -> tuple[list[T], list[T]]:
        matches, notmatches = [], []
        for x in self:
            matches.append(x) if f(x) else notmatches.append(x)

        return matches, notmatches

    def peekable(self) -> Peekable[T]:
        return Peekable(self)

    def position(self, predicate: Callable[[T], bool], /) -> int | None:
        for i, x in enumerate(self):
            if predicate(x):
                return i
        return None

    def product(self: Iter[SupportsMulT]) -> SupportsMulT | None:
        return self.reduce(lambda acc, x: acc * x)

    def reduce(self, f: Callable[[T, T], T], /) -> T | None:
        first = self.next()
        if first is None:
            return None
        return self.fold(first, f)

    # TODO: def reversed ... , how do we include type information for whether we are reversible?
    # TODO: def rposition ... , how do we include type information for whether we are reversible?

    def scan(self, init: U, f: Callable[[U, T], U], /) -> Iter[U]:
        return Iter(Scan(self._iter, init, f))

    # TODO: def size_hint ...

    def skip(self, n: int, /) -> Iter[T]:
        for _ in range(n):
            if self.next() is None:
                break
        return self

    def skip_while(self, predicate: Callable[[T], bool], /) -> Iter[T]:
        return Iter(SkipWhile(self, predicate))

    def step_by(self, step: int, /) -> Iter[T]:
        return Iter(StepBy(self, step))

    @overload
    def sum(
        self: Iter[SupportsSumNoDefaultT],
    ) -> SupportsSumNoDefaultT | None:
        ...

    @overload
    def sum(
        self: Iter[SupportsSumNoDefaultT], *, default: U
    ) -> SupportsSumNoDefaultT | U:
        ...

    def sum(
        self: Iter[SupportsSumNoDefaultT], *, default: U | None = None
    ) -> SupportsSumNoDefaultT | U | None:
        first = self.next()
        if first is None:
            return default

        return sum(self, start=first)

    def take(self, n: int, /) -> Iter[T]:
        return Iter(Take(self, n))

    def take_while(self, predicate: Callable[[T], bool], /) -> Iter[T]:
        return Iter(TakeWhile(self, predicate))

    def try_fold(self, init: U, f: Callable[[U, T], U], /) -> U | None:
        # TODO: this feels unsafe
        try:
            return self.fold(init, f)
        except Exception:
            return None

    def try_for_each(self, f: Callable[[T], object], /) -> None:
        for x in self:
            try:
                f(x)
            except Exception:
                return

    def unzip(self: Iter[tuple[U, V]], /) -> tuple[Iter[U], Iter[V]]:
        return tuple(zip(*self))

    def zip(self, other: Iterable[U], /) -> Iter[tuple[T, U]]:
        return Iter(zip(self, other))


class FilterMap(Generic[T, U]):
    def __init__(
        self,
        __iterable: Iterable[T],
        predicate: Callable[[T], U | None],
        /,
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate

    def __iter__(self) -> Iterator[U]:
        for x in self._iter:
            r = self._predicate(x)
            if r is not None:
                yield r


class Fuse(Generic[T]):
    def __init__(self, __iterable: Iterable[T]) -> None:
        self._iter = Iter(__iterable)
        self._found_none = False

    def __iter__(self) -> Iterator[T | None]:
        while not self._found_none:
            nxt = self._iter.next()
            self._found_none = nxt is None
            yield nxt

        while True:
            yield None


class MapWhile(Generic[T, U]):
    def __init__(
        self, __iterable: Iterable[T], predicate: Callable[[T], U | None], /
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate

    def __iter__(self) -> Iterator[U]:
        for x in self._iter:
            r = self._predicate(x)
            if r is None:
                return
            yield r


class Peekable(Iter[T]):
    def __init__(self, __iterable: Iterable[T], /) -> None:
        self._iter = Iter(__iterable)
        self._peek: T | None | NotSetType = NotSet

    def __iter__(self) -> Iterator[T]:
        while True:
            if isinstance(self._peek, NotSetType):
                yield next(self._iter)
            elif self._peek is None:
                return
            else:
                yield self._peek
                self._peek = NotSet

    def peek(self) -> T | None:
        if isinstance(self._peek, NotSetType):
            try:
                self._peek = next(self._iter)
            except:
                self._peek = None

        return self._peek


class Scan(Generic[T, U]):
    def __init__(
        self,
        __iterable: Iterable[T],
        init: U,
        predicate: Callable[[U, T], U],
        /,
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate
        self._acc = init

    def __iter__(self) -> Iterator[U]:
        for x in self._iter:
            self._acc = self._predicate(self._acc, x)
            yield self._acc


class SkipWhile(Generic[T]):
    def __init__(
        self,
        __iterable: Iterable[T],
        predicate: Callable[[T], bool],
        /,
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate

    def __iter__(self) -> Iterator[T]:
        for x in self._iter:
            if self._predicate(x):
                yield x
                break

        return self._iter


class StepBy(Generic[T]):
    def __init__(self, __iterable: Iterable[T], step: int, /) -> None:
        if step <= 0:
            raise ValueError(f"Step must be positive, provided: {step}")

        self._iter = Iter(__iterable)
        self._step = step

    def __iter__(self) -> Iterator[T]:
        for i, x in enumerate(self._iter):
            if i % self._step:
                yield x


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
