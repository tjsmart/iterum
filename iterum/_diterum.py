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
from ._option import UnwrapNilError


class Diterum(Iterum[T_co]):
    __slots__ = ()

    @abstractmethod
    def next_back(self) -> Option[T_co]:
        ...

    @abstractmethod
    def len(self) -> int:
        ...

    # Defined by Iterator
    def rev(self) -> Rev[T_co]:
        return Rev(self)

    def rposition(self, predicate: Callable[[T_co], object], /) -> Option[int]:
        len = self.len()
        return self.rev().position(predicate).map(lambda x: len - x - 1)

    # Defined by DoubleEndedIterator
    def nth_back(self, n: int, /) -> Option[T_co]:
        return self.rev().nth(n)

    def rfind(self, predicate: Callable[[T_co], object], /) -> Option[T_co]:
        return self.rev().find(predicate)

    def rfold(self, init: U, f: Callable[[U, T_co], U], /) -> U:
        return self.rev().fold(init, f)

    def try_rfold(
        self,
        init: U,
        f: Callable[[U, T_co], U],
        /,
        *,
        exception: type[BaseException] | tuple[type[BaseException], ...] = Exception,
    ) -> Option[U]:
        return self.rev().try_fold(init, f, exception=exception)

    # Defined by ExactSizeIterator...
    def is_empty(self) -> bool:
        return self.len() == 0


class Rev(Diterum[T_co]):
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
    __slots__ = ("_seq", "_front", "_back")

    def __init__(self, __seq: Sequence[T_co], /) -> None:
        self._seq = __seq
        self._front = 0
        self._back = len(__seq) - 1

    def next(self) -> Option[T_co]:
        if self._back < self._front:
            return nil

        nxt = self._seq[self._front]
        self._front += 1
        return Some(nxt)

    def next_back(self) -> Option[T_co]:
        if self._back < self._front:
            return nil

        nxt = self._seq[self._back]
        self._back -= 1
        return Some(nxt)

    def len(self) -> int:
        if self._back < self._front:
            return 0

        return self._back + 1 - self._front
