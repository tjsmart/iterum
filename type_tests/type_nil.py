from __future__ import annotations

from typing import Literal
from typing import NoReturn
from typing import TypeVar

from typing_extensions import assert_type

from .option_helpers import create_nil
from .option_helpers import create_option
from .option_helpers import create_some
from .option_helpers import create_value
from .option_helpers import map_to_value
from .option_helpers import map_value_to_option
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


def nil_also():
    assert_type(nil.also(Some(1)), Nil)
    assert_type(nil.also(nil), Nil)


def nil_also_then():
    assert_type(nil.also_then(map_value_to_option), Nil)


def nil_expect():
    assert_type(nil.expect("Uh Oh!"), NoReturn)


def nil_filter():
    assert_type(nil.filter(predicate), Nil)


def nil_flatten():
    assert_type(nil.flatten(), Nil)


def nil_get_or_insert():
    assert_type(nil.get_or_insert(2), Swap[Some[int], int])


def nil_get_or_insert_with():
    assert_type(nil.get_or_insert_with(create_value), Swap[Some[int], int])


def nil_insert():
    assert_type(nil.insert(2), Swap[Some[int], int])


def nil_is_none():
    assert_type(nil.is_none(), Literal[True])


def nil_is_some():
    assert_type(nil.is_some(), Literal[False])


def nil_iter():
    assert_type(nil.iter(), iterum)


def nil_map():
    assert_type(nil.map(map_value_to_value), Nil)


def nil_map_or():
    assert_type(nil.map_or("test", map_value_to_value), str)


def nil_map_or_else():
    assert_type(nil.map_or_else(map_to_value, map_value_to_value), str)


def nil_either():
    assert_type(nil.either(create_option()), Option[int])
    assert_type(nil.either(Some(1)), Some[int])
    assert_type(nil.either(nil), Nil)


def nil_either_else():
    assert_type(nil.either_else(create_option), Option[int])
    assert_type(nil.either_else(create_some), Some[int])
    assert_type(nil.either_else(create_nil), Nil)


def nil_replace():
    assert_type(nil.replace(1), Swap[Some[int], Nil])


def nil_take():
    assert_type(nil.take(), Swap[Nil, Nil])


def nil_unwrap_or():
    assert_type(nil.unwrap_or(1), int)


def nil_unwrap_or_else():
    assert_type(nil.unwrap_or_else(create_value), int)


def nil_unzip():
    assert_type(nil.unzip(), tuple[Nil, Nil])


def nil_xor():
    assert_type(nil.xor(create_option()), Option[int])
    assert_type(nil.xor(Some(1)), Some[int])
    assert_type(nil.xor(nil), Nil)


def nil_zip():
    assert_type(nil.zip(Some(1)), Nil)
