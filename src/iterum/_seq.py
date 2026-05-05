from __future__ import annotations

import operator
from types import EllipsisType
from typing import Literal
from typing import overload
from typing import SupportsIndex

from ._diterum import Diterum
from ._iterum import Iterum
from ._notset import NotSet
from ._notset import NotSetType
from ._option import nil
from ._option import Option
from ._option import Some


@overload
def seq(
    start: SupportsIndex,
    end: SupportsIndex,
    /,
    step: SupportsIndex = 1,
) -> Seq:
    ...


@overload
def seq(
    start: SupportsIndex,
    end: EllipsisType,
    /,
    step: SupportsIndex = 1,
) -> InfSeq:
    ...


@overload
def seq(
    end: SupportsIndex,
    /,
    *,
    step: SupportsIndex = 1,
) -> Seq:
    ...


@overload
def seq(
    end: EllipsisType,
    /,
    *,
    step: SupportsIndex = 1,
) -> InfSeq:
    ...


def seq(
    start: SupportsIndex | EllipsisType,
    end: SupportsIndex | EllipsisType | NotSetType = NotSet,
    /,
    step: SupportsIndex = 1,
) -> Seq | InfSeq:
    """
    Count sequentially from start to end in step sizes.

    If a finite end is provided, an instance of [Seq][iterum.Seq] is returned.

    If an infinite end is provided (using ellipsis `...`), an instance of
    [InfSeq][iterum.InfSeq] is returned.

    Examples:

        >>> itr = seq(3)
        >>> assert itr.next() == Some(0)
        >>> assert itr.next() == Some(1)
        >>> assert itr.next() == Some(2)
        >>> assert itr.next() == nil

        Can also specify a start and step:
        >>> itr = seq(3, 9, 3)
        >>> assert itr.next() == Some(3)
        >>> assert itr.next() == Some(6)
        >>> assert itr.next() == nil

        Finite ranges implement [Diterum][iterum.Diterum]:
        >>> itr = seq(3)
        >>> assert itr.len() == 3
        >>> assert itr.next_back() == Some(2)
        >>> assert itr.next() == Some(0)

        Specify an infinite range using `...`:
        >>> itr = seq(...)
        >>> assert itr.next() == Some(0)
        >>> assert itr.next() == Some(1)
        >>> assert itr.next() == Some(2)
        >>> # will continue forever!

        Similarly a start and step can be specified:
        >>> itr = seq(-10, ..., -1)
        >>> assert itr.next() == Some(-10)
        >>> assert itr.next() == Some(-11)
        >>> assert itr.next() == Some(-12)
        >>> # will continue forever!
    """

    if isinstance(end, NotSetType):
        start, end = 0, start

    elif start is ...:
        raise TypeError("Start cannot be set to '...'")

    start = operator.index(start)
    end = ... if end is ... else operator.index(end)
    step = operator.index(step)

    if end is ...:
        return InfSeq(start=start, step=step)
    else:
        return Seq(start=start, end=end, step=step)


def _compute_back(start: int, end: int, step: int) -> int:
    if rem := (end - start) % step:
        return end - rem
    else:
        return end - step


def _sign(step: int) -> Literal[1, 0, -1]:
    return 1 if step > 0 else -1 if step < 0 else 0


class Seq(Diterum[int]):
    __slots__ = ("_front", "_back", "_step", "_dir")

    def __init__(self, *, start: int, end: int, step: int) -> None:
        self._front = start
        self._back = _compute_back(start, end, step)
        self._step = step
        self._dir = _sign(step)

    def next(self) -> Option[int]:
        if self._dir * (self._back - self._front) < 0:
            return nil

        nxt = Some(self._front)
        self._front += self._step
        return nxt

    def next_back(self) -> Option[int]:
        if self._dir * (self._back - self._front) < 0:
            return nil

        nxt_bk = Some(self._back)
        self._back -= self._step
        return nxt_bk

    def len(self) -> int:
        if self._dir * (self._back - self._front) < 0:
            return 0

        return (self._back + self._step - self._front) // self._step

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"start={self._front}"
            f", end={self._back + self._step}"
            f", step={self._step}"
            ")"
        )

    def __bool__(self) -> bool:
        return self.len() != 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Seq):
            return NotImplemented
        return (
            (self._front == other._front)
            and (self._back == other._back)
            and (self._step == other._step)
        )


class InfSeq(Iterum[int]):
    __slots__ = ("_front", "_step")

    def __init__(self, *, start: int, step: int) -> None:
        self._front = start
        self._step = step

    def next(self) -> Option[int]:
        nxt = Some(self._front)
        self._front += self._step
        return nxt

    def __repr__(self) -> str:
        return f"{type(self).__name__}(start={self._front}, step={self._step})"

    def __bool__(self) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InfSeq):
            return NotImplemented
        return (self._front == other._front) and (self._step == other._step)
