from __future__ import annotations

from collections.abc import Callable
from typing import Any
from typing import Generic
from typing import Literal
from typing import NamedTuple
from typing import NoReturn
from typing import overload
from typing import TYPE_CHECKING
from typing import TypeAlias
from typing import TypeVar

from ._singleton import Singleton

if TYPE_CHECKING:
    from ._iterum import iterum


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

S = TypeVar("S", bound="Some")
O = TypeVar("O", bound="Option")  # noqa: E741


# TODO: Some issues in docs? and validate with doctest


class Swap(NamedTuple, Generic[T, U]):
    """
    Used for various 'swapping' operations on [Option][iterum.Option].
    """

    inserted: T
    """
    Value inserted into an option
    """

    returned: U
    """
    Value returned from an option
    """


class UnwrapNilError(RuntimeError):
    """
    Exception raised when [nil.unwrap][iterum.Nil.unwrap] is called.
    """

    def __init__(self, msg: str = "Attempted to unwrap nil") -> None:
        super().__init__(msg)


class ExpectNilError(RuntimeError):
    """
    Exception raised when [nil.expect][iterum.Nil.expect] is called.
    """

    def __init__(self, msg: str = "Expected some but option is nil") -> None:
        super().__init__(msg)


class Nil(Singleton):
    """
    [Nil][iterum.Nil] has no value.

    Examples:

        >>> x = Nil()  # Type of "x" is "Nil"
        >>> x
        nil
        >>> x.is_nil()
        True

    [Nil][iterum.Nil] always returns the same object so just use [nil][iterum.nil] instead.

        >>> nil is Nil()
        True

    Likely, the only practical use of the [Nil][iterum.Nil] class is for type annotations and calls to `isinstance`.
    """

    __slots__ = ()

    def __repr__(self) -> str:
        return "nil"

    def __bool__(self) -> Literal[False]:
        return False

    def and_(self, optb: Option[U], /) -> Nil:
        """
        Returns [nil][iterum.nil] if the option is [nil][iterum.nil], otherwise
        returns optb.

        Arguments passed to [and_][iterum.Nil.and_] are eagerly evaluated; if
        you are passing the result of a function call, it is recommended to use
        [and_then][iterum.Nil.and_then], which is lazily evaluated.

        Examples:

            >>> assert Some(2).and_(nil) == nil
            >>> assert nil.and_(Some("foo")) == nil
            >>> assert Some(2).and_(Some("foo")) == Some("foo")
            >>> assert nil.and_(nil) == nil

        Note: because `and` is a keyword, this method is called `and_` instead.
        """
        # 'and' is a keyword, so instead we use 'and_'
        return self

    def and_then(self, f: Callable[[Any], Option[U]], /) -> Nil:
        """
        Returns [nil][iterum.nil] if the option is [nil][iterum.nil], otherwise
        calls `f` with the wrapped value and returns the result.

        Examples:

            >>> MAX_U32 = (1 << 32) - 1
            >>> def checked_sq_u32(x: int) -> Option[int]:
            ...     sq = x * x
            ...     if sq > MAX_U32:
            ...         return nil
            ...     return Some(sq)
            ...
            >>> assert Some(2).and_then(checked_sq_u32) == Some(4)
            >>> assert Some(1_000_000).and_then(checked_sq_u32) == nil
            >>> assert nil.and_then(checked_sq_u32) == nil
        """
        return self

    def expect(self, msg: str, /) -> NoReturn:
        """
        Returns the contained [Some][iterum.Some] value, consuming the self value.

        Examples:

            >>> x = Some("value")
            >>> assert x.expect("fruits are healthy") == "value"

            >>> try:
            ...     nil.expect("fruits are healthy")
            ... except ExpectNilError as ex:
            ...     print(ex)
            ...
            fruits are healthy

        Raises:
            ExpectNilError: if the value is a [nil][iterum.nil] with a custom
                panic message provided by msg.
        """
        raise ExpectNilError(msg)

    def filter(self, predicate: Callable[[Any], object], /) -> Nil:
        """
        Returns [nil][iterum.nil] if the option is [nil][iterum.nil], otherwise
        calls `predicate` with the wrapped value and returns:

            - [Some(value)][iterum.Some] if the predicate returns `True`
            - [nil][iterum.nil] if the predicate returns `False`

        Examples:

            >>> assert nil.filter(lambda x: x % 2 == 0) == nil
            >>> assert Some(3).filter(lambda x: x % 2 == 0) == nil
            >>> assert Some(4).filter(lambda x: x % 2 == 0) == Some(4)
        """
        return self

    def flatten(self) -> Nil:
        """
        Converts from `Option[Option[T]]` to `Option[T]`.

        Examples:

            >>> assert Some(Some(6)).flatten() == Some(6)
            >>> assert Some(nil).flatten() == nil
            >>> assert nil.flatten() == nil
        """
        return self

    def get_or_insert(self, value: T, /) -> Swap[Some[T], T]:
        """
        Inserts value into the option if it is [nil][iterum.nil], then returns a
        tuple of the resulting option and the returned value.

        See also [insert][iterum.Nil.insert], which updates the value even if
        the option already contains a value.

        Examples:

            >>> opt = nil
            >>> opt, value = opt.get_or_insert(5)
            >>> assert value == 5
            >>> assert opt == Some(5)

            >>> opt = Some(3)
            >>> opt, value = opt.get_or_insert(5)
            >>> assert value == 3
            >>> assert opt == Some(3)

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> assert Some(10).get_or_insert(5).returned == 10
            >>> assert nil.get_or_insert(5).returned == 5

            >>> assert Some(10).get_or_insert(5).inserted == Some(10)
            >>> assert nil.get_or_insert(5).inserted == Some(5)
        """
        return Swap(Some(value), value)

    def get_or_insert_with(self, f: Callable[[], T], /) -> Swap[Some[T], T]:
        """
        Inserts a value computed from `f` into the option if it is
        [nil][iterum.nil], then returns a tuple of the resulting option and the
        returned value.

        Examples:

            >>> opt = nil
            >>> opt, value = opt.get_or_insert_with(lambda: 5)
            >>> assert value == 5
            >>> assert opt == Some(5)

            >>> opt = Some(3)
            >>> opt, value = opt.get_or_insert_with(lambda: 5)
            >>> assert value == 3
            >>> assert opt == Some(3)

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> swap = Some(10).get_or_insert_with(lambda: 5)
            >>> assert swap.inserted == Some(10)
            >>> assert swap.returned == 10

            >>> swap = nil.get_or_insert_with(lambda: 5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == 5
        """
        return Swap(Some(value := f()), value)

    def insert(self, value: T, /) -> Swap[Some[T], T]:
        """
        Inserts value into the option, then returns a tuple of the resulting
        option and the returned value.

        If the option already contains a value, the old value is dropped.

        See also [get_or_insert][iterum.Nil.get_or_insert], which doesn’t
        update the value if the option already contains a value.

        Examples:

            >>> opt = nil
            >>> opt, value = opt.insert(1)
            >>> assert value == 1
            >>> assert opt == Some(1)

            >>> opt = Some(3)
            >>> opt, value = opt.insert(1)
            >>> assert value == 1
            >>> assert opt == Some(1)

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> swap = Some(10).insert(5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == 5

            >>> swap = nil.insert(5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == 5
        """
        return Swap(Some(value), value)

    def is_nil(self) -> Literal[True]:
        """
        Returns `True` if the option is a [nil][iterum.nil] value.

        Examples:

            >>> assert Some(2).is_nil() is False
            >>> assert nil.is_nil() is True
        """
        return True

    def is_some(self) -> Literal[False]:
        """
        Returns `True` if the option is a Some value.

        Examples:

            >>> assert Some(2).is_some() is True
            >>> assert nil.is_some() is False
        """
        return False

    def is_some_and(self, f: Callable[[Any], object]) -> Literal[False]:
        """
        Returns `True` if the option is a [Some][iterum.Some] and the value
        inside of it matches a predicate.

        Examples:

            >>> assert Some(2).is_some_and(lambda x: x > 1) is True
            >>> assert Some(0).is_some_and(lambda x: x > 1) is False
            >>> assert nil.is_some_and(lambda x: x > 1) is False
        """
        return False

    def iter(self) -> iterum[Any]:
        """
        Returns an iterator over the possibly contained value.

        Examples:

            >>> assert Some(4).iter().next() == Some(4)
            >>> assert nil.iter().next() == nil
        """
        from ._iterum import iterum

        return iterum([])

    def map(self, f: Callable[[Any], Any], /) -> Nil:
        """
        Maps an [Option[T]][iterum.Option] to [Option[U]][iterum.Option] by
        applying a function to a contained value (if [Some][iterum.Some]) or
        returns [nil][iterum.nil] (if [Nil][iterum.Nil]).

        Examples:

            >>> assert Some("Hello, World!").map(len) == Some(13)
            >>> assert nil.map(len) == nil
        """
        return self

    def map_or(self, default: U, f: Callable[[Any], U], /) -> U:
        """
        Returns the provided default result (if [nil][iterum.nil]), or applies a
        function to the contained value (if any).

        Arguments passed to [map_or][iterum.Nil.map_or] are eagerly evaluated;
        if you are passing the result of a function call, it is recommended to
        use [map_or_else][iterum.Nil.map_or_else], which is lazily evaluated.

        Examples:

            >>> assert Some("foo").map_or(42, len) == 3
            >>> assert nil.map_or(42, len) == 42
        """
        return default

    def map_or_else(self, default: Callable[[], U], f: Callable[[Any], U], /) -> U:
        """
        Computes a default function result (if [nil][iterum.nil]), or applies a
        different function to the contained value (if any).

        Examples:

            >>> k = 21
            >>> assert Some("foo").map_or_else(lambda: 2 * k, len) == 3
            >>> assert nil.map_or_else(lambda: 2 * k, len) == 42
        """
        return default()

    def ok_or(self, err: Exception, /) -> NoReturn:
        """
        Unwraps the option returning the value if [Some][iterum.Some] or raises
        the provided exception if [nil][iterum.nil].

        Arguments passed to [ok_or][iterum.Nil.ok_or] are eagerly evaluated; if
        you are passing the result of a function call, it is recommended to use
        [ok_or_else][iterum.Nil.ok_or_else], which is lazily evaluated.

        Examples:

            >>> assert Some("foo").ok_or(RuntimeError("oh no!")) == "foo"

            >>> try:
            ...     nil.ok_or(RuntimeError("oh no!"))
            ... except RuntimeError as ex:
            ...     print(ex)
            ...
            oh no!
        """
        raise err

    def ok_or_else(self, err: Callable[[], Exception], /) -> NoReturn:
        """
        Unwraps the option returning the value if [Some][iterum.Some] or raises
        the exception returned by the provided callable if [nil][iterum.nil].

        Examples:

            >>> assert Some("foo").ok_or_else(AssertionError) == "foo"

            >>> try:
            ...     nil.ok_or_else(lambda: AssertionError("oopsy!"))
            ... except AssertionError as ex:
            ...     print(ex)
            ...
            oopsy!
        """
        raise err()

    def or_(self, optb: O, /) -> O:
        """
        Returns the option if it contains a value, otherwise returns optb.

        Arguments passed to [or_][iterum.Nil.or_] are eagerly evaluated; if you
        are passing the result of a function call, it is recommended to use
        [or_else][iterum.Nil.or_else], which is lazily evaluated.

        Examples:

            >>> assert Some(2).or_(nil) == Some(2)
            >>> assert nil.or_(Some(100)) == Some(100)
            >>> assert Some(2).or_(Some(100)) == Some(2)
            >>> assert nil.or_(nil) == nil

        Note: because `or` is a keyword, this method is called `or_` instead.
        """
        # 'or' is a keyword, so instead we use 'or_'
        return optb

    def or_else(self, f: Callable[[], O], /) -> O:
        """
        Returns the option if it contains a value, otherwise calls `f` and
        returns the result.

        Examples:

            >>> def nobody() -> Option[str]:
            ...     return nil
            ...
            >>> def vikings() -> Option[str]:
            ...     return Some("vikings")
            ...
            >>> assert Some("barbarians").or_else(vikings) == Some("barbarians")
            >>> assert nil.or_else(vikings) == Some("vikings")
            >>> assert nil.or_else(nobody) == nil
        """
        return f()

    def replace(self, value: T, /) -> Swap[Some[T], Nil]:
        """
        Replaces the actual value in the option by the value given in parameter,
        returning a tuple of the resulting option and the returned old value if
        present.

        Examples:

            >>> x = Some(2)
            >>> new, old = x.replace(5)
            >>> assert new == Some(5)
            >>> assert old == Some(2)

            >>> x = nil
            >>> new, old = x.replace(5)
            >>> assert new == Some(5)
            >>> assert old == nil

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> swap = Some(10).replace(5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == Some(10)

            >>> swap = nil.replace(5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == nil
        """
        return Swap(Some(value), nil)

    def take(self) -> Swap[Nil, Nil]:
        """
        Takes the value out of the option, returning a tuple of the resulting
        nil and the old option.

        Examples:

            >>> x = Some(2)
            >>> new, old = x.take()
            >>> assert new == nil
            >>> assert old == Some(2)

            >>> x = nil
            >>> new, old = x.take()
            >>> assert new == nil
            >>> assert old == nil

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> swap = Some(2).take()
            >>> assert swap.inserted == nil
            >>> assert swap.returned == Some(2)

            >>> swap = nil.take()
            >>> assert swap.inserted == nil
            >>> assert swap.returned == nil
        """
        return Swap(nil, self)

    # transpose ... without a Result concept there isn't any value

    def unwrap(self) -> NoReturn:
        """
        Returns the contained [Some][iterum.Some] value.

        Examples:

            >>> assert Some("air").unwrap() == "air"

            >>> try:
            ...     nil.unwrap()
            ... except UnwrapNilError as ex:
            ...     print("Attempted to unwrap a nil!")
            ...
            Attempted to unwrap a nil!

        Raises:
            UnwrapNilError: if the value is a [nil][iterum.nil].
        """
        raise UnwrapNilError()

    def unwrap_or(self, default: T, /) -> T:
        """
        Returns the contained [Some][iterum.Some] value or a provided default.

        Arguments passed to [unwrap_or][iterum.Nil.unwrap_or] are eagerly
        evaluated; if you are passing the result of a function call, it is
        recommended to use [unwrap_or_else][iterum.Nil.unwrap_or_else], which
        is lazily evaluated.

        Examples:

            >>> assert Some("car").unwrap_or("bike") == "car"
            >>> assert nil.unwrap_or("bike") == "bike"
        """
        return default

    # In order for unwrap_or_default to be implemented we would
    # need to know within nil what type we are supposed to have.
    #
    # If this was known we could come up with reasonable defaults, e.g. 0, {}, [], "", ...
    # note: these also happen to be what constructing the type with no params gives.
    #
    # If I wanted to get real fancy could provide user way to register defaults
    # for their custom types.

    def unwrap_or_else(self, f: Callable[[], T], /) -> T:
        """
        Returns the contained [Some][iterum.Some] value or computes it from a closure.

        Examples:

            >>> k = 10
            >>> assert Some(4).unwrap_or_else(lambda: 2 * k) == 4
            >>> assert nil.unwrap_or_else(lambda: 2 * k) == 20
        """
        return f()

    def unzip(self) -> tuple[Nil, Nil]:
        """
        Unzips an option containing a tuple of two options.

        If `self` is `Some((a, b))` this method returns `(Some(a), Some(b))`.
        Otherwise, `(nil, nil)` is returned.

        Examples:

            >>> assert Some((1, "hi")).unzip() == (Some(1), Some("hi"))
            >>> assert nil.unzip() == (nil, nil)
        """
        return (nil, nil)

    @overload
    def xor(self, optb: S, /) -> S:
        ...

    @overload
    def xor(self, optb: Nil, /) -> Nil:
        ...

    def xor(self, optb: O, /) -> O | Nil:
        """
        Returns [Some][iterum.Some] if exactly one of `self`, `optb` is
        [Some][iterum.Some], otherwise returns [nil][iterum.nil].

        Examples:

            >>> assert Some(2).xor(nil) == Some(2)
            >>> assert nil.xor(Some(100)) == Some(100)
            >>> assert Some(2).xor(Some(100)) == nil
            >>> assert nil.xor(nil) == nil
        """
        return nil if isinstance(optb, Nil) else optb

    def zip(self, other: Option[U], /) -> Nil:
        """
        Zips `self` with another option.

        If `self` is `Some(s)` and `other` is `Some(o)`,
        this method returns `Some((s, o))`.
        Otherwise, `nil` is returned.

        Examples:

            >>> assert Some(1).zip(Some("hi")) == Some((1, "hi"))
            >>> assert Some(1).zip(nil) == nil
            >>> assert nil.zip(nil) == nil
        """
        return self


nil = Nil()
"""
Instance of type [Nil][iterum.Nil]. See [Nil][iterum.Nil] for more details.
"""


class Some(Generic[T]):
    """
    [Some][iterum.Some] value of type T.

    Examples:
        >>> x = Some(1)  # Type of "x" is "Some[int]"
        >>> x
        Some(1)
        >>> x.is_some()
        True
        >>> x.unwrap()
        1
    """

    __match_args__ = ("_value",)

    def __init__(self, value: T, /) -> None:
        self._value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Some):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"{Some.__name__}({self._value!r})"

    def __bool__(self) -> Literal[True]:
        return True

    def and_(self, optb: O, /) -> O:
        """Returns [nil][iterum.nil] if the option is [nil][iterum.nil], otherwise
        returns optb.

        Arguments passed to [and_][iterum.Some.and_] are eagerly evaluated; if
        you are passing the result of a function call, it is recommended to use
        [and_then][iterum.Some.and_then], which is lazily evaluated.

        Examples:

            >>> assert Some(2).and_(nil) == nil
            >>> assert nil.and_(Some("foo")) == nil
            >>> assert Some(2).and_(Some("foo")) == Some("foo")
            >>> assert nil.and_(nil) == nil

        Note: because `and` is a keyword, this method is called `and_` instead.
        """
        return optb

    def and_then(self, f: Callable[[T], O], /) -> O:
        """Returns [nil][iterum.nil] if the option is [nil][iterum.nil], otherwise
        calls `f` with the wrapped value and returns the result.

        Examples:


            >>> MAX_U32 = (1 << 32) - 1
            >>> def checked_sq_u32(x: int) -> Option[int]:
            ...     sq = x * x
            ...     if sq > MAX_U32:
            ...         return nil
            ...     return Some(sq)
            ...
            >>> assert Some(2).and_then(checked_sq_u32) == Some(4)
            >>> assert Some(1_000_000).and_then(checked_sq_u32) == nil
            >>> assert nil.and_then(checked_sq_u32) == nil
        """
        return f(self._value)

    def expect(self, msg: str, /) -> T:
        """Returns the contained [Some][iterum.Some] value, consuming the self value.

        Examples:

            >>> x = Some("value")
            >>> assert x.expect("fruits are healthy") == "value"

            >>> try:
            ...     nil.expect("fruits are healthy")
            ... except ExpectNilError as ex:
            ...     print(ex)
            ...
            fruits are healthy

        Raises:
            ExpectNilError: if the value is a [nil][iterum.nil] with a custom
                message provided by msg.
        """
        return self._value

    def filter(self, predicate: Callable[[T], object], /) -> Option[T]:
        """Returns [nil][iterum.nil] if the option is [nil][iterum.nil], otherwise
        calls `predicate` with the wrapped value and returns:

            - [Some(value)][iterum.Some] if the predicate returns `True`
            - [nil][iterum.nil] if the predicate returns `False`

        Examples:

            >>> assert nil.filter(lambda x: x % 2 == 0) == nil
            >>> assert Some(3).filter(lambda x: x % 2 == 0) == nil
            >>> assert Some(4).filter(lambda x: x % 2 == 0) == Some(4)
        """
        return self if predicate(self._value) else Nil()

    def flatten(self: Some[O]) -> O:
        """Converts from `Option[Option[T]]` to `Option[T]`.

        Examples:

            >>> assert Some(Some(6)).flatten() == Some(6)
            >>> assert Some(nil).flatten() == nil
            >>> assert nil.flatten() == nil
        """
        if isinstance(self._value, (Some, Nil)):
            return self._value
        else:
            raise TypeError(f"Cannot flatten type: Some({type(self._value).__name__})")

    def get_or_insert(self, value: T, /) -> Swap[Some[T], T]:
        """Inserts value into the option if it is [nil][iterum.nil], then returns a
        tuple of the resulting option and the returned value.

        See also [insert][iterum.Some.insert], which updates the value even if
        the option already contains a value.

        Examples:

            >>> opt = nil
            >>> opt, value = opt.get_or_insert(5)
            >>> assert value == 5
            >>> assert opt == Some(5)

            >>> opt = Some(3)
            >>> opt, value = opt.get_or_insert(5)
            >>> assert value == 3
            >>> assert opt == Some(3)

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> assert Some(10).get_or_insert(5).returned == 10
            >>> assert nil.get_or_insert(5).returned == 5

            >>> assert Some(10).get_or_insert(5).inserted == Some(10)
            >>> assert nil.get_or_insert(5).inserted == Some(5)
        """
        return Swap(Some(self._value), self._value)

    def get_or_insert_with(self, f: Callable[[], T], /) -> Swap[Some[T], T]:
        """Inserts a value computed from `f` into the option if it is
        [nil][iterum.nil], then returns a tuple of the resulting option and the
        returned value.

        Examples:

            >>> opt = nil
            >>> opt, value = opt.get_or_insert_with(lambda: 5)
            >>> assert value == 5
            >>> assert opt == Some(5)

            >>> opt = Some(3)
            >>> opt, value = opt.get_or_insert_with(lambda: 5)
            >>> assert value == 3
            >>> assert opt == Some(3)

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> swap = Some(10).get_or_insert_with(lambda: 5)
            >>> assert swap.inserted == Some(10)
            >>> assert swap.returned == 10

            >>> swap = nil.get_or_insert_with(lambda: 5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == 5
        """
        return Swap(Some(self._value), self._value)

    def insert(self, value: T, /) -> Swap[Some[T], T]:
        """Inserts value into the option, then returns a tuple of the resulting
        option and the returned value.

        If the option already contains a value, the old value is dropped.

        See also [get_or_insert][iterum.Some.get_or_insert], which doesn’t
        update the value if the option already contains a value.

        Examples:

            >>> opt = nil
            >>> opt, value = opt.insert(1)
            >>> assert value == 1
            >>> assert opt == Some(1)

            >>> opt = Some(3)
            >>> opt, value = opt.insert(1)
            >>> assert value == 1
            >>> assert opt == Some(1)

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> swap = Some(10).insert(5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == 5

            >>> swap = nil.insert(5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == 5
        """
        self._value = value
        return Swap(Some(self._value), self._value)

    def is_nil(self) -> Literal[False]:
        """Returns `True` if the option is a [nil][iterum.nil] value.

        Examples:

            >>> assert Some(2).is_nil() is False
            >>> assert nil.is_nil() is True
        """
        return False

    def is_some(self) -> Literal[True]:
        """Returns `True` if the option is a Some value.

        Examples:

            >>> assert Some(2).is_some() is True
            >>> assert nil.is_some() is False
        """
        return True

    def is_some_and(self, f: Callable[[T], object]) -> bool:
        """Returns `True` if the option is a [Some][iterum.Some] and the value
        inside of it matches a predicate.

        Examples:

            >>> assert Some(2).is_some_and(lambda x: x > 1) is True
            >>> assert Some(0).is_some_and(lambda x: x > 1) is False
            >>> assert nil.is_some_and(lambda x: x > 1) is False
        """
        return bool(f(self.unwrap()))

    def iter(self) -> iterum[T]:
        """Returns an iterator over the possibly contained value.

        Examples:

            >>> assert Some(4).iter().next() == Some(4)
            >>> assert nil.iter().next() == nil
        """
        from ._iterum import iterum

        return iterum([self._value])

    def map(self, f: Callable[[T], U], /) -> Some[U]:
        """Maps an [Option[T]][iterum.Option] to [Option[U]][iterum.Option] by
        applying a function to a contained value (if [Some][iterum.Some]) or
        returns [nil][iterum.nil] (if [Nil][iterum.Nil]).

        Examples:

            >>> assert Some("Hello, World!").map(len) == Some(13)
            >>> assert nil.map(len) == nil
        """
        return Some(f(self._value))

    def map_or(self, default: U, f: Callable[[T], U], /) -> U:
        """
        Returns the provided default result (if [nil][iterum.nil]), or applies a
        function to the contained value (if any).

        Arguments passed to [map_or][iterum.Some.map_or] are eagerly evaluated;
        if you are passing the result of a function call, it is recommended to
        use [map_or_else][iterum.Some.map_or_else], which is lazily evaluated.

        Examples:

            >>> assert Some("foo").map_or(42, len) == 3
            >>> assert nil.map_or(42, len) == 42
        """
        return f(self._value)

    def map_or_else(self, default: Callable[[], U], f: Callable[[T], U], /) -> U:
        """
        Computes a default function result (if [nil][iterum.nil]), or applies a
        different function to the contained value (if any).

        Examples:

            >>> k = 21
            >>> assert Some("foo").map_or_else(lambda: 2 * k, len) == 3
            >>> assert nil.map_or_else(lambda: 2 * k, len) == 42
        """
        return f(self._value)

    def ok_or(self, err: Exception, /) -> T:
        """Unwraps the option returning the value if [Some][iterum.Some] or raises
        the provided exception if [nil][iterum.nil].

        Arguments passed to [ok_or][iterum.Some.ok_or] are eagerly evaluated; if
        you are passing the result of a function call, it is recommended to use
        [ok_or_else][iterum.Some.ok_or_else], which is lazily evaluated.

        Examples:

            >>> assert Some("foo").ok_or(RuntimeError("oh no!")) == "foo"

            >>> try:
            ...     nil.ok_or(RuntimeError("oh no!"))
            ... except RuntimeError as ex:
            ...     print(ex)
            ...
            oh no!
        """
        return self._value

    def ok_or_else(self, err: Callable[[], Exception], /) -> T:
        """Unwraps the option returning the value if [Some][iterum.Some] or raises
        the exception returned by the provided callable if [nil][iterum.nil].

        Examples:

            >>> assert Some("foo").ok_or_else(AssertionError) == "foo"

            >>> try:
            ...     nil.ok_or_else(lambda: AssertionError("oopsy!"))
            ... except AssertionError as ex:
            ...     print(ex)
            ...
            oopsy!
        """
        return self._value

    def or_(self, optb: Option[T], /) -> Some[T]:
        """Returns the option if it contains a value, otherwise returns optb.

        Arguments passed to [or_][iterum.Some.or_] are eagerly evaluated; if you
        are passing the result of a function call, it is recommended to use
        [or_else][iterum.Some.or_else], which is lazily evaluated.

        Examples:

            >>> assert Some(2).or_(nil) == Some(2)
            >>> assert nil.or_(Some(100)) == Some(100)
            >>> assert Some(2).or_(Some(100)) == Some(2)
            >>> assert nil.or_(nil) == nil

        Note: because `or` is a keyword, this method is called `or_` instead.
        """
        # 'or' is a keyword, so instead we use 'or_'
        return self

    def or_else(self, f: Callable[[], Option[T]], /) -> Some[T]:
        """Returns the option if it contains a value, otherwise calls `f` and
        returns the result.

        Examples:

            >>> def nobody() -> Option[str]:
            ...     return nil
            ...
            >>> def vikings() -> Option[str]:
            ...     return Some("vikings")
            ...
            >>> assert Some("barbarians").or_else(vikings) == Some("barbarians")
            >>> assert nil.or_else(vikings) == Some("vikings")
            >>> assert nil.or_else(nobody) == nil
        """
        return self

    def replace(self, value: T, /) -> Swap[Some[T], Some[T]]:
        """Replaces the actual value in the option by the value given in parameter,
        returning a tuple of the resulting option and the returned old value if
        present.

        Examples:

            >>> x = Some(2)
            >>> new, old = x.replace(5)
            >>> assert new == Some(5)
            >>> assert old == Some(2)

            >>> x = nil
            >>> new, old = x.replace(5)
            >>> assert new == Some(5)
            >>> assert old == nil

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> swap = Some(10).replace(5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == Some(10)

            >>> swap = nil.replace(5)
            >>> assert swap.inserted == Some(5)
            >>> assert swap.returned == nil
        """
        old = self._value
        self._value = value
        return Swap(Some(self._value), Some(old))

    def take(self) -> Swap[Nil, Some[T]]:
        """Takes the value out of the option, returning a tuple of the resulting
        nil and the old option.

        Examples:

            >>> x = Some(2)
            >>> new, old = x.take()
            >>> assert new == nil
            >>> assert old == Some(2)

            >>> x = nil
            >>> new, old = x.take()
            >>> assert new == nil
            >>> assert old == nil

        Alternatively, access the named attributes of [Swap][iterum.Swap],
        [inserted][iterum.Swap.inserted] and [returned][iterum.Swap.returned]:

            >>> swap = Some(2).take()
            >>> assert swap.inserted == nil
            >>> assert swap.returned == Some(2)

            >>> swap = nil.take()
            >>> assert swap.inserted == nil
            >>> assert swap.returned == nil
        """
        return Swap(nil, self)

    # transpose ... without a Result concept there isn't any value

    def unwrap(self) -> T:
        """Returns the contained [Some][iterum.Some] value.

        Examples:

            >>> assert Some("air").unwrap() == "air"

            >>> try:
            ...     nil.unwrap()
            ... except UnwrapNilError as ex:
            ...     print("Attempted to unwrap a nil!")
            ...
            Attempted to unwrap a nil!

        Raises:
            UnwrapNilError: if the value is a [nil][iterum.nil].
        """
        return self._value

    def unwrap_or(self, default: T, /) -> T:
        """
        Returns the contained [Some][iterum.Some] value or a provided default.

        Arguments passed to [unwrap_or][iterum.Some.unwrap_or] are eagerly
        evaluated; if you are passing the result of a function call, it is
        recommended to use [unwrap_or_else][iterum.Some.unwrap_or_else], which
        is lazily evaluated.

        Examples:

            >>> assert Some("car").unwrap_or("bike") == "car"
            >>> assert nil.unwrap_or("bike") == "bike"
        """
        return self._value

    def unwrap_or_else(self, f: Callable[[], T], /) -> T:
        """Returns the contained [Some][iterum.Some] value or computes it from a closure.

        Examples:

            >>> k = 10
            >>> assert Some(4).unwrap_or_else(lambda: 2 * k) == 4
            >>> assert nil.unwrap_or_else(lambda: 2 * k) == 20
        """
        return self._value

    def unzip(self: Some[tuple[U, V]]) -> tuple[Some[U], Some[V]]:
        """Unzips an option containing a tuple of two options.

        If `self` is `Some((a, b))` this method returns `(Some(a), Some(b))`.
        Otherwise, `(nil, nil)` is returned.

        Examples:

            >>> assert Some((1, "hi")).unzip() == (Some(1), Some("hi"))
            >>> assert nil.unzip() == (nil, nil)
        """
        left, right = self._value
        return Some(left), Some(right)

    @overload
    def xor(self, optb: Some[T], /) -> Nil:
        ...

    @overload
    def xor(self, optb: Nil, /) -> Some[T]:
        ...

    def xor(self, optb: Option[T], /) -> Option[T]:
        """
        Returns [Some][iterum.Some] if exactly one of `self`, `optb` is
        [Some][iterum.Some], otherwise returns [nil][iterum.nil].

        Examples:

            >>> assert Some(2).xor(nil) == Some(2)
            >>> assert nil.xor(Some(100)) == Some(100)
            >>> assert Some(2).xor(Some(100)) == nil
            >>> assert nil.xor(nil) == nil
        """
        return self if isinstance(optb, Nil) else nil

    @overload
    def zip(self, other: Some[U], /) -> Some[tuple[T, U]]:
        ...

    @overload
    def zip(self, other: Nil, /) -> Nil:
        ...

    def zip(self, other: Option[U], /) -> Option[tuple[T, U]]:
        """
        Zips `self` with another option.

        If `self` is `Some(s)` and `other` is `Some(o)`,
        this method returns `Some((s, o))`.
        Otherwise, `nil` is returned.

        Examples:

            >>> assert Some(1).zip(Some("hi")) == Some((1, "hi"))
            >>> assert Some(1).zip(nil) == nil
            >>> assert nil.zip(nil) == nil
        """
        return nil if isinstance(other, Nil) else Some((self._value, other._value))


Option: TypeAlias = "Some[T] | Nil"
"""
Type alias representing something which is either of type
[Some][iterum.Some] or [Nil][iterum.Nil].

Examples:

    >>> # Type annotate a function which returns `Some[int]` or `nil`:
    >>> def checked_div(num: int, dem: int) -> Option[int]:
    ...     try:
    ...         return Some(num // dem)
    ...     except ZeroDivisionError:
    ...         return nil
    ...

    >>> # Use isinstance to narrow the type:
    >>> x = checked_div(10, 3)
    >>> reveal_type(x)  # Type of "x" is "Some[int] | Nil"
    >>> if isinstance(x, Some):
    ...     reveal_type(x)  # Type of "x" is "Some[int]"
    ... else:
    ...     reveal_type(x)  # Type of "x" is "Nil"
    ...

    >>> # Alternatively use pattern matching:
    >>> match x:
    ...     case Some(value):
    ...         print(f"Result: {value=}")
    ...     case Nil:
    ...         print("Cannot divide by 0")
    ...
}
"""
