from ._singleton import Singleton


# TODO: Replace with typing.sentinel once available
#       and better supported.
class NotSetType(Singleton):
    __slots__ = ()


NotSet = NotSetType()
