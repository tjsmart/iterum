from __future__ import annotations

import builtins
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Generic
from typing import Iterable
from typing import Iterator
from typing import NoReturn
from typing import overload
from typing import TypeAlias
from typing import TypeVar
from typing import Union

from typing_extensions import Self
from typing_extensions import TypeGuard


_T = TypeVar("_T")
_U = TypeVar("_U")
_V = TypeVar("_V")
_R = TypeVar("_R")


@dataclass(frozen=True)
class Some(Generic[_T]):
    value: _T

    def unwrap(self) -> _T:
        ...


# @dataclass(frozen=True)
# class Nil(Generic[_T]):
#     def unwrap(self) -> NoReturn:
#         ...
#
#
# Option: TypeAlias = Union[Some, Nil]


class NilType:
    ...


Nil = NilType()


_C = TypeVar("_C", bound=type)


class Singleton:
    __slots__ = ()
    __instance = None

    def __new__(cls) -> Self:
        if cls.__instance is None:
            return cls()
        return cls.__instance


class NotSetType(Singleton):
    __slots__ = ()

    # def __instancecheck__(self, value: object | NotSetType) -> TypeGuard[Self]:
    def __instancecheck__(self, value):
        return value is self

    @classmethod
    def is_set(cls, value: _T | NotSetType) -> TypeGuard[_T]:
        return not value is cls()


NotSet = NotSetType()


@dataclass(frozen=True)
class Option(Generic[_T]):
    _option: Union[Some[_T], NilType]

    @overload
    def __init__(self, /) -> None:
        ...

    @overload
    def __init__(self, value: _T, /) -> None:
        ...

    def __init__(self, value: _T | NotSetType = NotSet, /) -> None:
        if isinstance(value, NotSetType):
            self._option: option[_T] = Option()
        else:
            reveal_type(value)

        self._option = Nil if isintance(value, NotSetType) else Some(value)

    def unwrap(self) -> _T | NoReturn:
        if isinstance(self, Some):
            return self.value

        raise ValueError("Attempted unwrap of nil value.")


import itertools


from enum import Enum, unique


def create_singleton(name: str) -> object:
    return type(name, (Singleton,), {})()


@unique
class Ordering(Enum):
    Less = create_singleton("Less")
    Equal = create_singleton("Equal")
    Greater = create_singleton("Greater")


class Iter(Generic[_T]):
    def __init__(self, __iterable: Iterable[_T], /) -> None:
        self._iter = iter(__iterable)

    def __iter__(self) -> Iterator[_T]:
        # TODO: Should this stop at first None?
        # Introducing my own None type is looking more appealing...
        return self._iter

    def next(self) -> _T | None:
        try:
            return next(self._iter)
        except StopIteration:
            return None

    def all(self, f: Callable[[_T], bool], /) -> bool:
        return all(map(f, self._iter))

    def any(self, f: Callable[[_T], bool], /) -> bool:
        return any(map(f, self._iter))

    def chain(self, other: Iterable[_T], /) -> Self:
        return type(self)(itertools.chain(self, other))

    def cmp(self, other: Iterable[object], /) -> Ordering:
        # TODO: https://doc.rust-lang.org/std/cmp/trait.Ord.html#lexicographical-comparison
        ...

    def collect(self) -> list[_T]:
        return list(self)

    def count(self) -> int:
        last = self.enumerate().last()
        if last is None:
            return 0
        return last[0] + 1

    def cycle(self) -> Self:
        return type(self)(itertools.cycle(self))

    def enumerate(self) -> Iter[tuple[int, _T]]:
        return type(self)(enumerate(self))

    def eq(self, other: Iter[object], /) -> bool:
        return all(lambda x, y: x == y for (x, y) in self.zip(other))

    def filter(self, predicate: Callable[[_T], bool], /) -> Self:
        # TODO: filter == filterfalse?
        return type(self)(itertools.filterfalse(predicate, self))

    def filter_map(self, predicate: Callable[[_T], _R | None], /) -> Iter[_R]:
        return self.map(predicate).filter(lambda x: x is None)

    def find(self, predicate: Callable[[_T], bool], /) -> _T | None:
        for x in self:
            if predicate(x):
                return x
        return None

    def find_map(self, predicate: Callable[[_T], _R | None], /) -> _R | None:
        return self.filter_map(predicate).next()

    def flat_map(
        self, f: Callable[[Iterable[_T]], Iterable[Iterable[_U]]], /
    ) -> Iter[_U]:
        return self.map(f).flatten()

    def flatten(self: Iter[Iterable[_U]]) -> Iter[_U]:
        return Iter(y for x in self._iter for y in x)

    def fold(self, init: _U, f: Callable[[_U, _T], _U], /) -> _U:
        acc = init
        for x in self:
            acc = f(acc, x)
        return acc

    def for_each(self, f: Callable[[_T], object], /) -> None:
        for x in self:
            f(x)

    def fuse(self) -> Self:
        return type(self)(Fuse(self))

    def ge(self, other: Iterable[object], /) -> bool:
        return self.cmp(other) in (Ordering.Greater, Ordering.Equal)

    def gt(self, other: Iterable[object], /) -> bool:
        return self.cmp(other) == Ordering.Greater

    def inspect(self, f: Callable[[_T], object], /) -> Self:
        def predicate(x: _T) -> _T:
            f(x)
            return x

        return self.map(predicate)

    def last(self) -> _T | None:
        last = None
        while (nxt := self.next()) is not None:
            last = nxt

        return last

    def le(self, other: Iterable[object], /) -> bool:
        return self.cmp(other) in (Ordering.Less, Ordering.Equal)

    def lt(self, other: Iterable[object], /) -> bool:
        return self.cmp(other) == Ordering.Less

    def map(self, f: Callable[[_T], _U], /) -> Iter[_U]:
        return Iter(map(f, self))

    def map_while(self, predicate: Callable[[_T], _U | None], /) -> Iter[_U]:
        # If iter stops at first None, how is this any different??
        return self.map(predicate).take_while(lambda x: x is not None)

    def max(self) -> _T | None:
        try:
            return builtins.max(self)
        except ValueError:
            return None

    def min(self) -> _T | None:
        try:
            return builtins.min(self)
        except ValueError:
            return None

    def ne(self, other: Iterable[object], /) -> bool:
        return not self.eq(other)

    def nth(self, n: int, /) -> _T | None:
        return self.enumerate().find_map(lambda i, x: x if i == n else None)

    # TODO: def partial_cmp...

    def partition(self, f: Callable[[_T], bool], /) -> tuple[list[_T], list[_T]]:
        matches, notmatches = [], []
        for x in self:
            matches.append(x) if f(x) else notmatches.append(x)

        return matches, notmatches

    def peekable(self) -> Peekable[_T]:
        return Peekable(self)

    def position(self, predicate: Callable[[_T], bool], /) -> int:
        return self.enumerate().find_map(lambda i, x: i if f(x) else None)

    def product(self) -> _T | None:
        return self.reduce(lambda acc, x: acc * x)

    def reduce(self, f: Callable[[_T, _T], _T], /) -> _T | None:
        first = self.next()
        if first is None:
            return None
        return self.fold(first, f)

    def reversed(self) -> Self:
        return type(self)(reversed(self))

    def rposition(self, predicate: Callable[[_T], bool], /) -> int | None:
        return self.reversed().position(predicate)

    def scan(self, init: _U, f: Callable[[_U, _T], _U], /) -> Iter[_U]:
        return Iter(Scan(self._iter, init, f))

    # TODO: def size_hint ...

    def skip(self, n: int, /) -> Self:
        for _ in range(n):
            if self.next() is None:
                break
        return self

    def skip_while(self, predicate: Callable[[_T], bool], /) -> Self:
        return Iter(SkipWhile(self, predicate))

    def step_by(self, step: int, /) -> Self:
        return Iter(StepBy(self, step))

    def sum(self) -> _T:
        return sum(self)

    def take(self, n: int, /) -> Self:
        return Iter(Take(self, n))

    def take_while(self, predicate: Callable[[_T], bool], /) -> Self:
        return Iter(TakeWhile(self, predicate))

    def try_fold(self, init: _U, f: Callable[[_U, _T], _U], /) -> _U | None:
        # TODO: this feels unsafe
        try:
            return self.fold(init, f)
        except Exception:
            return None

    def try_for_each(self, f: Callable[[_T], object], /) -> None:
        for x in self:
            try:
                f(x)
            except Exception:
                return

    def unzip(self: Iter[tuple[_U, _V]], /) -> tuple[Iter[_U], Iter[_V]]:
        return tuple(zip(*self))

    def zip(self, other: Iterable[_U], /) -> Iter[tuple[_T, _U]]:
        return Iter(zip(self, other))


class Fuse(Generic[_T]):
    def __init__(self, __iterable: Iterable[_T]) -> None:
        self._iter = Iter(__iterable)
        self._found_none = False

    def __iter__(self) -> Iterator[_T | None]:
        while not self._found_none:
            nxt = self._iter.next()
            self._found_none = nxt is None
            yield nxt

        while True:
            yield None


class Peekable(Iter[_T]):
    def __init__(self, __iterable: Iterable[_T], /) -> None:
        self._iter = Iter(__iterable)
        self._peek: _T | None | NotSetType = NotSet

    def __iter__(self) -> Iterator[_T]:
        while True:
            if isinstance(self._peek, NotSet):
                yield next(self._iter)
            else:
                yield self._peek
                self._peek = NotSet

    def peek(self) -> _T | None:
        if isinstance(self._peek, NotSetType):
            try:
                self._peek = next(self._iter)
            except:
                self._peek = None

        return self._peek


class Scan(Generic[_T, _U]):
    def __init__(
        self,
        __iterable: Iterable[_T],
        init: _U,
        predicate: Callable[[_U, _T], _U],
        /,
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate
        self._acc = init

    def __iter__(self) -> Iterator[_U]:
        for x in self._iter:
            self._acc = self._predicate(self._acc, x)
            yield self._acc


class SkipWhile(Generic[_T]):
    def __init__(
        self,
        __iterable: Iterable[_T],
        predicate: Callable[[_T], bool],
        /,
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate

    def __iter__(self) -> Iterator[_T]:
        for x in self._iter:
            if self._predicate(x):
                yield x
                break

        return self._iter


class StepBy(Generic[_T]):
    def __init__(self, __iterable: Iterable[_T], step: int, /) -> None:
        if step <= 0:
            raise ValueError(f"Step must be positive, provided: {step}")

        self._iter = Iter(__iterable)
        self._step = step

    def __iter__(self) -> Iterator[_T]:
        for i, x in enumerate(self._iter):
            if i % self._step:
                yield x


class Take(Generic[_T]):
    def __init__(self, __iterable: Iterable[_T], n: int, /) -> None:
        self._iter = Iter(__iterable)
        self._n = n

    def __iter__(self) -> Iterator[_T]:
        for i, x in enumerate(self._iter):
            if i >= self._n:
                return
            yield x


class TakeWhile(Generic[_T]):
    def __init__(
        self, __iterable: Iterable[_T], predicate: Callable[[_T], bool], /
    ) -> None:
        self._iter = Iter(__iterable)
        self._predicate = predicate

    def __iter__(self) -> Iterator[_T]:
        for x in self._iter:
            if not self._predicate(x):
                return
            yield x


#     def collect(self, _type: type[_Type]) -> _Type[_T]:
#         ...
#
#
# from typing import Protocol
#
#
# class CanInitFromIterable(Protocol[_T]):
#     def __init__(self, __iterable: Iterable[_T]) -> None:
#         ...
#
#
# _Type = TypeVar("_Type", bound=CanInitFromIterable)


it = Iter([1, 2, 3])
