from __future__ import annotations

from typing import Callable
from typing import Generic
from typing import Literal
from typing import NoReturn
from typing import overload
from typing import TYPE_CHECKING
from typing import TypeVar

from typing_extensions import TypeAlias

from ._singleton import Singleton


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

S = TypeVar("S", bound="Some")
O = TypeVar("O", bound="Option")

if TYPE_CHECKING:
    from ._iter import Iter


class UnwrapNilError(RuntimeError):
    def __init__(self, msg: str = "Attempted to unwrap nil") -> None:
        super().__init__(msg)


class ExpectNilError(RuntimeError):
    def __init__(self, msg: str = "Expected some but option is nil") -> None:
        super().__init__(msg)


class Nil(Singleton):
    __slots__ = ()

    def also(self, optb: Option[U], /) -> Nil:
        # 'and' is a keyword, so instead we use 'also'
        return self

    def also_then(self, f: Callable[[T], Option[U]], /) -> Nil:
        return self

    def expect(self, msg: str, /) -> NoReturn:
        raise ExpectNilError(msg)

    def filter(self, predicate: Callable[[T], bool], /) -> Nil:
        return self

    def flatten(self) -> Nil:
        return self

    def get_or_insert(self, value: T, /) -> T:
        # TODO: this is a problem...
        # perhaps these will have to become standalone functions...
        return value

    def get_or_insert_with(self, f: Callable[[], T], /) -> T:
        # TODO: this is a problem...
        return f()

    def insert(self, value: T, /) -> T:
        # TODO: this is a problem...
        return value

    def is_none(self) -> Literal[True]:
        return True

    def is_some(self) -> Literal[False]:
        return False

    def iter(self) -> Iter[T]:
        from ._iter import Iter

        return Iter([])

    def map(self, f: Callable[[T], U], /) -> Nil:
        return self

    def map_or(self, default: U, f: Callable[[T], U], /) -> U:
        return default

    def map_or_else(self, default: Callable[[], U], f: Callable[[T], U], /) -> U:
        return default()

    def either(self, optb: O, /) -> O:
        # 'or' is a keyword, so instead we use 'either'
        return optb

    def either_else(self, f: Callable[[], O], /) -> O:
        return f()

    def replace(self, value: T, /) -> Nil:
        # TODO: this is a problem...
        return nil

    def take(self) -> Nil:
        return self

    def unwrap(self) -> NoReturn:
        raise UnwrapNilError()

    def unwrap_or(self, default: T, /) -> T:
        return default

    def unwrap_or_else(self, f: Callable[[], T], /) -> T:
        return f()

    def unzip(self) -> tuple[Nil, Nil]:
        return (nil, nil)

    @overload
    def xor(self, optb: S, /) -> S:
        ...

    @overload
    def xor(self, optb: Nil, /) -> Nil:
        ...

    def xor(self, optb: O, /) -> O | Nil:
        # TODO: some things, like this can be overloaded to give a smarter type hint
        return nil if isinstance(optb, Nil) else optb

    def zip(self, other: Option[U], /) -> Nil:
        return self


nil = Nil()


class Some(Generic[T]):
    __match_args__ = ("_value",)

    def __init__(self, value: T, /) -> None:
        self._value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Some):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"{Some.__name__}({self._value!r})"

    def also(self, optb: O, /) -> O:
        # 'and' is a keyword, so instead we use 'also'
        return optb

    def also_then(self, f: Callable[[T], O], /) -> O:
        return f(self._value)

    def expect(self, msg: str, /) -> T:
        return self._value

    def filter(self, predicate: Callable[[T], bool], /) -> Option[T]:
        return self if predicate(self._value) else Nil()

    def flatten(self: Some[O]) -> O:
        if isinstance(self._value, (Some, Nil)):
            return self._value
        else:
            raise TypeError(f"Cannot flatten type: Some({type(self._value).__name__})")

    def get_or_insert(self, value: T, /) -> T:
        return self._value

    def get_or_insert_with(self, f: Callable[[], T], /) -> T:
        return self._value

    def insert(self, value: T, /) -> T:
        self._value = value
        return value

    def is_none(self) -> Literal[False]:
        return False

    def is_some(self) -> Literal[True]:
        return True

    def iter(self) -> Iter[T]:
        from ._iter import Iter

        return Iter([self._value])

    def map(self, f: Callable[[T], U], /) -> Some[U]:
        return Some(f(self._value))

    def map_or(self, default: U, f: Callable[[T], U], /) -> U:
        return f(self._value)

    def map_or_else(self, default: Callable[[], U], f: Callable[[T], U], /) -> U:
        return f(self._value)

    # TODO: any reason to implement ok variants?, transpose as well

    def either(self, optb: Option[T], /) -> Some[T]:
        # 'or' is a keyword, so instead we use 'either'
        return self

    def either_else(self, f: Callable[[], Option[T]], /) -> Some[T]:
        return self

    def replace(self, value: T, /) -> Some[T]:
        old = self._value
        self._value = value
        return Some(old)

    def take(self) -> Some[T]:
        # TODO: this is a problem...
        return self

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: T, /) -> T:
        return self._value

    def unwrap_or_else(self, f: Callable[[], T], /) -> T:
        return self._value

    def unzip(self: Some[tuple[U, V]]) -> tuple[Some[U], Some[V]]:
        left, right = self._value
        return Some(left), Some(right)

    @overload
    def xor(self, optb: Some[T], /) -> Nil:
        ...

    @overload
    def xor(self, optb: Nil, /) -> Some[T]:
        ...

    def xor(self, optb: Option[T], /) -> Option[T]:
        # TODO: some things, like this can be overloaded to give a smarter type hint
        return self if isinstance(optb, Nil) else nil

    @overload
    def zip(self, other: Some[U], /) -> Some[tuple[T, U]]:
        ...

    @overload
    def zip(self, other: Nil, /) -> Nil:
        ...

    def zip(self, other: Option[U], /) -> Option[tuple[T, U]]:
        return nil if isinstance(other, Nil) else Some((self._value, other._value))


Option: TypeAlias = "Some[T] | Nil"