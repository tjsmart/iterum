from __future__ import annotations

from typing_extensions import Self


class Singleton:
    __slots__ = ()
    __instance = None

    def __new__(cls) -> Self:
        if cls.__instance is None:
            return cls()
        return cls.__instance


def create_singleton(name: str) -> object:
    return type(name, (Singleton,), {})()
