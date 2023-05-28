from __future__ import annotations

from rust_iterator import Nil
from rust_iterator import Option
from rust_iterator import Some


def create_option() -> Option[int]:
    ...


def create_some() -> Some[int]:
    ...


def create_nil() -> Nil:
    ...


def create_value() -> int:
    ...


def map_value_to_option(x: int) -> Option[str]:
    ...


def map_value_to_some(x: int) -> Some[str]:
    ...


def map_value_to_nil(x: int) -> Nil:
    ...


def map_value_to_value(x: int) -> str:
    ...


def map_to_value() -> str:
    ...


def predicate(x: int) -> bool:
    ...
