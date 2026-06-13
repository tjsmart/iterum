from typing import TypeGuard

from ._singleton import Singleton


class NotSetType(Singleton):
    __slots__ = ()

    # def __instancecheck__(self, value: object | NotSetType) -> TypeGuard[Self]:
    def __instancecheck__(self, value):
        return value is self

    @classmethod
    def is_set[T](cls, value: T | NotSetType) -> TypeGuard[T]:
        return value is not cls()


NotSet = NotSetType()
