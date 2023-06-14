from __future__ import annotations

from typing import Literal
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

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


some = Some(0)


def some_also():
    assert_type(some.also(Some("test")), Some[str])
    assert_type(some.also(nil), Nil)


def some_also_then():
    assert_type(some.also_then(map_value_to_option), Option[str])
    assert_type(some.also_then(map_value_to_some), Some[str])
    assert_type(some.also_then(map_value_to_nil), Nil)


def some_expect():
    assert_type(some.expect("Uh Oh!"), int)


def some_filter():
    assert_type(some.filter(predicate), Option[int])


def some_flatten():
    assert_type(Some(create_option()).flatten(), Option[int])
    assert_type(Some(Some(1)).flatten(), Some[int])
    assert_type(Some(nil).flatten(), Nil)


def some_get_or_insert():
    assert_type(some.get_or_insert(2), int)


def some_get_or_insert_with():
    assert_type(some.get_or_insert_with(create_value), int)


def some_insert():
    assert_type(some.insert(2), int)


def some_is_none():
    assert_type(some.is_none(), Literal[False])


def some_is_some():
    assert_type(some.is_some(), Literal[True])


def some_iter():
    assert_type(some.iter(), iterum[int])


def some_map():
    assert_type(some.map(map_value_to_value), Some[str])


def some_map_or():
    assert_type(some.map_or("test", map_value_to_value), str)


def some_map_or_else():
    assert_type(some.map_or_else(map_to_value, map_value_to_value), str)


def some_either():
    assert_type(some.either(create_option()), Some[int])
    assert_type(some.either(Some(1)), Some[int])
    assert_type(some.either(nil), Some[int])


def some_either_else():
    assert_type(some.either_else(create_option), Some[int])
    assert_type(some.either_else(create_some), Some[int])
    assert_type(some.either_else(create_nil), Some[int])


def some_replace():
    assert_type(some.replace(1), Some[int])


def some_take():
    assert_type(some.take(), Some[int])


def some_unwrap_or():
    assert_type(some.unwrap_or(1), int)


def some_unwrap_or_else():
    assert_type(some.unwrap_or_else(create_value), int)


def some_unzip():
    assert_type(Some((1, "test")).unzip(), tuple[Some[int], Some[str]])


def some_xor():
    assert_type(some.xor(create_option()), Option[int])
    assert_type(some.xor(Some(1)), Nil)
    assert_type(some.xor(nil), Some[int])


def some_zip():
    assert_type(some.zip(Some("test")), Some[tuple[int, str]])
    assert_type(some.zip(nil), Nil)
