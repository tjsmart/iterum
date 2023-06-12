from __future__ import annotations

from typing import Any
from typing import Generic
from typing import Iterable
from typing import TypeVar

from typing_extensions import assert_type

from iterum import Iter
from iterum import Nil
from iterum import nil
from iterum import Option
from iterum import Ordering
from iterum import Peekable
from iterum import Scannable
from iterum import Some

T = TypeVar("T")
# U = TypeVar("U")
# V = TypeVar("V")


class MyCollection(Generic[T]):
    def __init__(self, _: Iterable[T]) -> None:
        ...


def create_int() -> int:
    ...


def create_tuple_int() -> tuple[int, ...]:
    ...


def create_tuple_str_int() -> tuple[str, int]:
    ...


itr = Iter([1, 2, 3])


def iter_init():
    assert_type(Iter([1, 2, 3]), Iter[int])
    assert_type(Iter("test"), Iter[str])


def iter_dunder_iter():
    for x in itr:
        assert_type(x, int)


def iter_dunder_next():
    assert_type(next(itr), int)


def iter_next():
    assert_type(itr.next(), Option[int])


def iter_all():
    assert_type(itr.all(bool), bool)


def iter_any():
    assert_type(itr.any(bool), bool)


def iter_chain():
    assert_type(itr.chain({3, 4, 5}), Iter[int])


def iter_cmp():
    assert_type(Iter([1, 2, 3]).cmp((object(),)), Ordering)
    assert_type(Iter([object()]).cmp((1, 2)), Ordering)


def iter_collect():
    assert_type(itr.collect(), list[int])
    assert_type(itr.collect(list), list[int])
    assert_type(itr.collect(set), set[int])
    assert_type(itr.collect(tuple), tuple[int, ...])
    assert_type(Iter([create_tuple_str_int()]).collect(dict), dict[str, int])
    assert_type(Iter("test").collect("".join), str)
    assert_type(itr.collect(MyCollection), MyCollection)


def iter_count():
    assert_type(itr.count(), int)


def iter_cycle():
    assert_type(itr.cycle(), Iter[int])


def iter_enumerate():
    assert_type(itr.enumerate(), Iter[tuple[int, int]])


def iter_eq():
    assert_type(Iter([1, 2, 3]).eq((object(),)), bool)
    assert_type(Iter([object()]).eq((1, 2)), bool)


def iter_filter():
    assert_type(itr.filter(lambda _: False), Iter[int])


def iter_filter_map():
    assert_type(itr.filter_map(lambda _: Some("test")), Iter[str])


def iter_find():
    assert_type(itr.find(lambda _: False), Option[int])


def iter_find_map():
    assert_type(itr.find_map(lambda _: Some("test")), Option[str])


def iter_flat_map():
    assert_type(itr.flat_map(lambda _: "test"), Iter[str])


def iter_flatten():
    assert_type(Iter(["test", "this"]).flatten(), Iter[str])
    assert_type(Iter([create_tuple_int(), create_tuple_int()]).flatten(), Iter[int])


def iter_fold():
    assert_type(itr.fold("test", lambda _x, _y: "this"), str)


def iter_for_each():
    assert_type(itr.for_each(lambda _: "whatever"), None)


def iter_fuse():
    assert_type(itr.fuse(), Iter[int])


def iter_ge():
    assert_type(Iter([1, 2, 3]).ge((object(),)), bool)
    assert_type(Iter([object()]).ge((1, 2)), bool)


def iter_gt():
    assert_type(Iter([1, 2, 3]).gt((object(),)), bool)
    assert_type(Iter([object()]).gt((1, 2)), bool)


def iter_inspect():
    assert_type(itr.inspect(lambda _: "whatever"), Iter[int])


def iter_last():
    assert_type(itr.last(), Option[int])


def iter_le():
    assert_type(Iter([1, 2, 3]).le((object(),)), bool)
    assert_type(Iter([object()]).le((1, 2)), bool)


def iter_lt():
    assert_type(Iter([1, 2, 3]).lt((object(),)), bool)
    assert_type(Iter([object()]).lt((1, 2)), bool)


def iter_map():
    assert_type(itr.map(lambda _: "test"), Iter[str])


def iter_map_while():
    assert_type(itr.map_while(lambda _: Some("test")), Iter[str])


def iter_max():
    assert_type(itr.max(), Option[int])


def iter_max_by():
    assert_type(itr.max_by(lambda _x, _y: Ordering.Less), Option[int])


def iter_max_by_key():
    assert_type(itr.max_by_key(lambda _: "test"), Option[int])


def iter_min():
    assert_type(itr.min(), Option[int])


def iter_min_by():
    assert_type(itr.min_by(lambda _x, _y: Ordering.Less), Option[int])


def iter_min_by_key():
    assert_type(itr.min_by_key(lambda _: "test"), Option[int])


def iter_ne():
    assert_type(Iter([1, 2, 3]).ne((object(),)), bool)
    assert_type(Iter([object()]).ne((1, 2)), bool)


def iter_nth():
    assert_type(itr.nth(10), Option[int])


def iter_partial_cmp():
    assert_type(Iter([1, 2, 3]).partial_cmp((object(),)), Some[Ordering])
    assert_type(Iter([object()]).partial_cmp((1, 2)), Some[Ordering])
    assert_type(Iter([object()]).partial_cmp((object(),)), Nil)


def iter_partition():
    assert_type(itr.partition(lambda _: False), tuple[list[int], list[int]])
    assert_type(itr.partition(lambda _: False, list), tuple[list[int], list[int]])
    assert_type(itr.partition(lambda _: False, set), tuple[set[int], set[int]])
    assert_type(
        itr.partition(lambda _: False, tuple), tuple[tuple[int, ...], tuple[int, ...]]
    )
    assert_type(
        Iter([create_tuple_str_int()]).partition(lambda _: False, dict),
        tuple[dict[str, int], dict[str, int]],
    )
    assert_type(
        itr.partition(lambda _: False, MyCollection), tuple[MyCollection, MyCollection]
    )


def iter_peekable():
    assert_type(itr.peekable(), Peekable[int])


def iter_position():
    assert_type(itr.position(lambda _: False), Option[int])


def iter_product():
    assert_type(itr.product(), Option[int])


def iter_reduce():
    assert_type(itr.reduce(lambda _x, _y: 3), Option[int])


def iter_scannable():
    assert_type(itr.scannable("test"), Scannable[int, str])


def iter_skip():
    assert_type(itr.skip(10), Iter[int])


def iter_skip_while():
    assert_type(itr.skip_while(lambda _: False), Iter[int])


def iter_step_by():
    assert_type(itr.step_by(2), Iter[int])


def iter_sum():
    assert_type(itr.sum(), Option[int])


def iter_take():
    assert_type(itr.take(10), Iter[int])


def iter_take_while():
    assert_type(itr.take_while(lambda _: False), Iter[int])


def iter_try_fold():
    assert_type(itr.try_fold("test", lambda x, y: f"{x}{y}"), Option[str])


def iter_unzip():
    itr = Iter([create_tuple_str_int()])
    assert_type(itr.unzip(), tuple[list[str], list[int]])
    assert_type(itr.unzip(list), tuple[list[str], list[int]])
    assert_type(itr.unzip(set), tuple[set[str], set[int]])
    assert_type(itr.unzip(tuple), tuple[tuple[str, ...], tuple[int, ...]])


def iter_zip():
    assert_type(itr.zip(["test", "this"]), Iter[tuple[int, str]])
