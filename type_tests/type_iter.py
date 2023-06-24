from __future__ import annotations

from typing import assert_type
from typing import Generic
from typing import Iterable
from typing import TypeVar

from iterum import Chain
from iterum import Cycle
from iterum import Enumerate
from iterum import Filter
from iterum import FilterMap
from iterum import FlatMap
from iterum import Flatten
from iterum import Fuse
from iterum import Inspect
from iterum import iterum
from iterum import Map
from iterum import MapWhile
from iterum import Nil
from iterum import nil
from iterum import Option
from iterum import Ordering
from iterum import Peekable
from iterum import Scan
from iterum import Skip
from iterum import SkipWhile
from iterum import Some
from iterum import State
from iterum import StepBy
from iterum import Take
from iterum import TakeWhile
from iterum import Zip

T = TypeVar("T")


class MyCollection(Generic[T]):
    def __init__(self, _: Iterable[T]) -> None:
        ...


def create_int() -> int:
    ...


def create_tuple_int() -> tuple[int, ...]:
    ...


def create_tuple_str_int() -> tuple[str, int]:
    ...


itr = iterum([1, 2, 3])


def iter_init():
    assert_type(iterum([1, 2, 3]), iterum[int])
    assert_type(iterum("test"), iterum[str])


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
    assert_type(itr.chain({3, 4, 5}), Chain[int])


def iter_cmp():
    assert_type(iterum([1, 2, 3]).cmp((object(),)), Ordering)
    assert_type(iterum([object()]).cmp((1, 2)), Ordering)


def iter_collect():
    assert_type(itr.collect(), list[int])
    assert_type(itr.collect(list), list[int])
    assert_type(itr.collect(set), set[int])
    assert_type(itr.collect(tuple), tuple[int, ...])
    assert_type(iterum([create_tuple_str_int()]).collect(dict), dict[str, int])
    assert_type(iterum("test").collect("".join), str)
    # Coulde be MyCollection[int] or MyCollection[Unkown]
    # assert_type(itr.collect(MyCollection), MyCollection[int])


def iter_count():
    assert_type(itr.count(), int)


def iter_cycle():
    assert_type(itr.cycle(), Cycle[int])


def iter_enumerate():
    assert_type(itr.enumerate(), Enumerate[int])


def iter_eq():
    assert_type(iterum([1, 2, 3]).eq((object(),)), bool)
    assert_type(iterum([object()]).eq((1, 2)), bool)


def iter_filter():
    assert_type(itr.filter(lambda _: False), Filter[int])


def iter_filter_map():
    assert_type(itr.filter_map(lambda _: Some("test")), FilterMap[str])


def iter_find():
    assert_type(itr.find(lambda _: False), Option[int])


def iter_find_map():
    assert_type(itr.find_map(lambda _: Some("test")), Option[str])


def iter_flat_map():
    assert_type(itr.flat_map(lambda _: "test"), FlatMap[str])


def iter_flatten():
    assert_type(iterum(["test", "this"]).flatten(), Flatten[str])
    assert_type(
        iterum([create_tuple_int(), create_tuple_int()]).flatten(), Flatten[int]
    )


def iter_fold():
    assert_type(itr.fold("test", lambda _x, _y: "this"), str)


def iter_for_each():
    assert_type(itr.for_each(lambda _: "whatever"), None)


def iter_fuse():
    assert_type(itr.fuse(), Fuse[int])


def iter_ge():
    assert_type(iterum([1, 2, 3]).ge((object(),)), bool)
    assert_type(iterum([object()]).ge((1, 2)), bool)


def iter_gt():
    assert_type(iterum([1, 2, 3]).gt((object(),)), bool)
    assert_type(iterum([object()]).gt((1, 2)), bool)


def iter_inspect():
    assert_type(itr.inspect(lambda _: "whatever"), Inspect[int])


def iter_last():
    assert_type(itr.last(), Option[int])


def iter_le():
    assert_type(iterum([1, 2, 3]).le((object(),)), bool)
    assert_type(iterum([object()]).le((1, 2)), bool)


def iter_lt():
    assert_type(iterum([1, 2, 3]).lt((object(),)), bool)
    assert_type(iterum([object()]).lt((1, 2)), bool)


def iter_map():
    assert_type(itr.map(lambda _: "test"), Map[str])


def iter_map_while():
    assert_type(itr.map_while(lambda _: Some("test")), MapWhile[str])


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
    assert_type(iterum([1, 2, 3]).ne((object(),)), bool)
    assert_type(iterum([object()]).ne((1, 2)), bool)


def iter_nth():
    assert_type(itr.nth(10), Option[int])


def iter_partial_cmp():
    assert_type(iterum([1, 2, 3]).partial_cmp((object(),)), Some[Ordering])
    assert_type(iterum([object()]).partial_cmp((1, 2)), Some[Ordering])
    assert_type(iterum([object()]).partial_cmp((object(),)), Nil)


def iter_partition():
    assert_type(itr.partition(lambda _: False), tuple[list[int], list[int]])
    assert_type(itr.partition(lambda _: False, list), tuple[list[int], list[int]])
    assert_type(itr.partition(lambda _: False, set), tuple[set[int], set[int]])
    assert_type(
        itr.partition(lambda _: False, tuple), tuple[tuple[int, ...], tuple[int, ...]]
    )
    assert_type(
        iterum([create_tuple_str_int()]).partition(lambda _: False, dict),
        tuple[dict[str, int], dict[str, int]],
    )
    # Coulde be MyCollection[int] or MyCollection[Unkown]
    # assert_type(
    #     itr.partition(lambda _: False, MyCollection), tuple[MyCollection, MyCollection]
    # )


def iter_peekable():
    assert_type(itr.peekable(), Peekable[int])


def iter_position():
    assert_type(itr.position(lambda _: False), Option[int])


def iter_product():
    assert_type(itr.product(), Option[int])


def iter_reduce():
    assert_type(itr.reduce(lambda _x, _y: 3), Option[int])


def iter_scan():
    def scanner(state: State, x: int) -> Option[int]:
        state.value *= x
        if state.value > 6:
            return nil
        return Some(-state.value)

    assert_type(itr.scan(1, scanner), Scan[int])


def iter_skip():
    assert_type(itr.skip(10), Skip[int])


def iter_skip_while():
    assert_type(itr.skip_while(lambda _: False), SkipWhile[int])


def iter_step_by():
    assert_type(itr.step_by(2), StepBy[int])


def iter_sum():
    assert_type(itr.sum(), Option[int])


def iter_take():
    assert_type(itr.take(10), Take[int])


def iter_take_while():
    assert_type(itr.take_while(lambda _: False), TakeWhile[int])


def iter_try_fold():
    assert_type(itr.try_fold("test", lambda x, y: f"{x}{y}"), Option[str])


def iter_unzip():
    itr = iterum([create_tuple_str_int()])
    assert_type(itr.unzip(), tuple[list[str], list[int]])
    assert_type(itr.unzip(list), tuple[list[str], list[int]])
    assert_type(itr.unzip(set), tuple[set[str], set[int]])
    assert_type(itr.unzip(tuple), tuple[tuple[str, ...], tuple[int, ...]])


def iter_zip():
    assert_type(itr.zip(["test", "this"]), Zip[int, str])
