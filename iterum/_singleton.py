from __future__ import annotations

from typing import TypeVar


Self = TypeVar("Self", bound="Singleton")


class Singleton:
    __slots__ = ()
    __instance = None

    def __new__(cls: type[Self]) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance


def create_singleton(name: str) -> object:
    return type(name, (Singleton,), {})()
