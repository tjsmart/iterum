from __future__ import annotations

from dataclasses import dataclass
from typing import Generic
from typing import NoReturn
from typing import overload
from typing import TypeGuard
from typing import TypeVar
from typing import Union

from typing_extensions import Self

from ._type_helpers import T

C = TypeVar("C", bound=type)


@dataclass(frozen=True)
class Some(Generic[T]):
    value: T

    def unwrap(self) -> T:
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
    def is_set(cls, value: T | NotSetType) -> TypeGuard[T]:
        return not value is cls()


NotSet = NotSetType()


@dataclass(frozen=True)
class Option(Generic[T]):
    _option: Union[Some[T], NilType]

    @overload
    def __init__(self, /) -> None:
        ...

    @overload
    def __init__(self, value: T, /) -> None:
        ...

    def __init__(self, value: T | NotSetType = NotSet, /) -> None:
        if isinstance(value, NotSetType):
            self._option: option[T] = Option()
        else:
            reveal_type(value)

        self._option = Nil if isintance(value, NotSetType) else Some(value)

    def unwrap(self) -> T | NoReturn:
        if isinstance(self, Some):
            return self.value

        raise ValueError("Attempted unwrap of nil value.")
