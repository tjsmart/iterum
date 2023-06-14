from __future__ import annotations

from typing import Any
from typing import TypeVar

from typing_extensions import assert_type

from .option_helpers import create_nil
from .option_helpers import create_option
from .option_helpers import create_some
from .option_helpers import create_value
from .option_helpers import map_to_value
from .option_helpers import map_value_to_nil
from .option_helpers import map_value_to_option
from .option_helpers import map_value_to_some
from .option_helpers import map_value_to_value
from .option_helpers import predicate
from iterum import iterum
from iterum import Nil
from iterum import nil
from iterum import Option
from iterum import Some
from iterum import Swap


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


option = create_option()


def isinstance_nil_implies_nil_else_some():
    x = create_option()
    if isinstance(x, Nil):
        assert_type(x, Nil)
    else:
        assert_type(x, Some[int])


def isinstance_some_implies_some_else_nil():
    x = create_option()
    if isinstance(x, Some):
        assert_type(x, Some[int])
    else:
        assert_type(x, Nil)


def option_also():
    assert_type(option.also(Some("test")), Option[str])
    assert_type(option.also(nil), Nil)


def option_also_then():
    assert_type(option.also_then(map_value_to_option), Option[str])
    assert_type(option.also_then(map_value_to_some), Option[str])
    assert_type(option.also_then(map_value_to_nil), Nil)


def option_expect():
    assert_type(option.expect("Uh Oh!"), int)


def option_filter():
    assert_type(option.filter(predicate), Option[int])


def option_flatten():
    assert_type(Some(create_option()).flatten(), Option[int])
    assert_type(Some(Some(1)).flatten(), Some[int])
    assert_type(Some(nil).flatten(), Nil)


def option_get_or_insert():
    assert_type(option.get_or_insert(2), Swap[Some[int], int])


def option_get_or_insert_with():
    assert_type(option.get_or_insert_with(create_value), Swap[Some[int], int])


def option_insert():
    assert_type(option.insert(2), Swap[Some[int], int])


def option_is_none():
    assert_type(option.is_none(), bool)


def option_is_some():
    assert_type(option.is_some(), bool)


def option_iter():
    assert_type(option.iter(), iterum[int] | iterum[Any])


def option_map():
    assert_type(option.map(map_value_to_value), Option[str])


def option_map_or():
    assert_type(option.map_or("test", map_value_to_value), str)


def option_map_or_else():
    assert_type(option.map_or_else(map_to_value, map_value_to_value), str)


def option_either():
    assert_type(option.either(create_option()), Option[int])
    assert_type(option.either(Some(1)), Some[int])
    assert_type(option.either(nil), Option[int])


def option_either_else():
    assert_type(option.either_else(create_option), Option[int])
    assert_type(option.either_else(create_some), Some[int])
    assert_type(option.either_else(create_nil), Option[int])


def option_replace():
    # assert_type(option.replace(1), Swap[Some[int], Option[int]])  # sad this doesn't work...
    assert_type(option.replace(1), Swap[Some[int], Some[int]] | Swap[Some[int], Nil])


def option_take():
    # assert_type(option.take(), Swap[Nil, Option[int]])  # sad this doesn't work...
    assert_type(option.take(), Swap[Nil, Some[int]] | Swap[Nil, Nil])


def option_unwrap_or():
    assert_type(option.unwrap_or(1), int)


def option_unwrap_or_else():
    assert_type(option.unwrap_or_else(create_value), int)


def create_option_tuple() -> Option[tuple[int, str]]:
    ...


def option_unzip():
    assert_type(
        create_option_tuple().unzip(), tuple[Some[int], Some[str]] | tuple[Nil, Nil]
    )


def option_xor():
    assert_type(option.xor(create_option()), Option[int])
    assert_type(option.xor(Some(1)), Option[int])
    assert_type(option.xor(nil), Option[int])


def option_zip():
    assert_type(option.zip(Some("test")), Option[tuple[int, str]])
    assert_type(option.zip(nil), Nil)
