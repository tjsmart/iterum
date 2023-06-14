from __future__ import annotations

from functools import partial
from typing import Iterable
from typing import Iterator

import pytest

from iterum import iterum
from iterum import nil
from iterum import Option
from iterum import Ordering
from iterum import Some
from iterum import State


def count_forever():
    i = 0
    while True:
        yield i
        i += 1


def test_all_basic_usage():
    a = [1, 2, 3]

    assert iterum(a).all(lambda x: x > 0)
    assert not iterum(a).all(lambda x: x > 2)


def test_all_stops_at_first_false():
    a = [1, 2, 3]
    itr = iterum(a)

    assert not itr.all(lambda x: x != 2)

    # itr still has more elements.
    assert itr.next() == Some(3)


def test_any_basic_usage():
    a = [1, 2, 3]

    assert iterum(a).any(lambda x: x > 0)
    assert not iterum(a).any(lambda x: x > 5)


def test_any_stops_at_first_false():
    a = [1, 2, 3]
    itr = iterum(a)

    assert itr.any(lambda x: x != 2)

    # itr still has more elements.
    assert itr.next() == Some(2)


def test_chain_basic_usage():
    a1 = [1, 2, 3]
    a2 = [4, 5, 6]

    itr = iterum(a1).chain(a2)

    assert itr.next() == Some(1)
    assert itr.next() == Some(2)
    assert itr.next() == Some(3)
    assert itr.next() == Some(4)
    assert itr.next() == Some(5)
    assert itr.next() == Some(6)
    assert itr.next() == nil


def test_cmp_basic_usage():
    assert iterum([1]).cmp([1]) == Ordering.Equal
    assert iterum([1, 2]).cmp([1]) == Ordering.Greater
    assert iterum([1]).cmp([1, 2]) == Ordering.Less


def test_cmp_some_more():
    assert iterum([2]).cmp([1]) == Ordering.Greater
    assert iterum([1]).cmp([2]) == Ordering.Less

    assert iterum([2]).cmp([1, 3]) == Ordering.Greater
    assert iterum([1, 3]).cmp([2]) == Ordering.Less


def test_collect_basic_usage():
    doubled = iterum([1, 2, 3]).map(lambda x: x * 2).collect(list)
    assert doubled == [2, 4, 6]


def test_collect_string():
    assert iterum("test").map(str.upper).collect("".join) == "TEST"


def test_count_basic_usage():
    assert iterum([1, 2, 3]).count() == 3
    assert iterum([1, 2, 3, 4, 5]).count() == 5


def test_cycle_basic_usage():
    a = [1, 2, 3]
    it = iterum(a).cycle()

    assert it.next() == Some(1)
    assert it.next() == Some(2)
    assert it.next() == Some(3)
    assert it.next() == Some(1)
    assert it.next() == Some(2)
    assert it.next() == Some(3)
    assert it.next() == Some(1)


def test_enumerate_basic_usage():
    a = ["a", "b", "c"]

    it = iterum(a).enumerate()

    assert it.next() == Some((0, "a"))
    assert it.next() == Some((1, "b"))
    assert it.next() == Some((2, "c"))
    assert it.next() == nil


def test_eq_basic_usage():
    assert iterum([1]).eq([1])
    assert not iterum([1]).eq([1, 2])


def test_filter_basic_usage():
    a = [0, 1, 2]

    it = iterum(a).filter(lambda x: x > 0)

    assert it.next() == Some(1)
    assert it.next() == Some(2)
    assert it.next() == nil


def parse2int(x: str) -> Option[int]:
    try:
        value = int(x)
    except ValueError:
        return nil
    else:
        return Some(value)


def test_filter_map_basic_usage():
    a = ["1", "two", "NaN", "four", "5"]

    it = iterum(a).filter_map(parse2int)

    assert it.next() == Some(1)
    assert it.next() == Some(5)
    assert it.next() == nil


def test_find_basic_usage():
    a = [1, 2, 3]

    assert iterum(a).find(lambda x: x == 2) == Some(2)
    assert iterum(a).find(lambda x: x == 5) == nil


def test_find_stops_at_first_true():
    it = iterum([1, 2, 3])

    assert it.find(lambda x: x == 2) == Some(2)

    assert it.next() == Some(3)


def test_find_map_basic_usage():
    a = ["lol", "NaN", "2", "5"]

    first_number = iterum(a).find_map(parse2int)

    assert first_number == Some(2)


def test_flat_map_basic_usage():
    words = ["alpha", "beta", "gamma"]

    merged = iterum(words).flat_map(iterum).collect("".join)

    assert merged == "alphabetagamma"


def foo(_: iterum[Iterable[int]]) -> None:
    ...


def test_flatten_basic_usage():
    data = [[1, 2, 3, 4], [5, 6]]
    flattened = iterum(data).flatten().collect(list)
    assert flattened == [1, 2, 3, 4, 5, 6]


def test_flatten_mapping_and_then_flattening():
    words = ["alpha", "beta", "gamma"]

    merged = iterum(words).map(iterum).flatten().collect("".join)
    assert merged == "alphabetagamma"


def test_fold_basic_usage():
    a = [1, 2, 3]
    sum = iterum(a).fold(0, lambda acc, x: acc + x)
    assert sum == 6


def test_fold_string_build():
    numbers = [1, 2, 3, 4, 5]

    result = iterum(numbers).fold("0", lambda acc, x: f"({acc} + {x})")

    assert result == "(((((0 + 1) + 2) + 3) + 4) + 5)"


def test_for_each_basic_usage():
    v = []
    iterum(range(0, 5)).map(lambda x: x * 2 + 1).for_each(v.append)
    assert v == [1, 3, 5, 7, 9]


class Alternator(Iterator[int]):
    def __init__(self) -> None:
        self.i = 0

    def __next__(self) -> int:
        self.i += 1
        if self.i % 5:
            return self.i
        else:
            raise StopIteration()


def test_fuse_not_so_basic_usage():
    it = iterum(Alternator())

    assert list(it) == [1, 2, 3, 4]
    assert list(it) == [6, 7, 8, 9]
    assert list(it) == [11, 12, 13, 14]

    it = it.fuse()

    assert list(it) == [16, 17, 18, 19]
    assert list(it) == []
    assert list(it) == []


def test_ge_basic_usage():
    assert iterum([1]).ge([1])
    assert not iterum([1]).ge([1, 2])
    assert iterum([1, 2]).ge([1])
    assert iterum([1, 2]).ge([1, 2])


def test_gt_basic_usagt():
    assert not iterum([1]).gt([1])
    assert not iterum([1]).gt([1, 2])
    assert iterum([1, 2]).gt([1])
    assert not iterum([1, 2]).gt([1, 2])


def test_inspect_basic_usage():
    a = [1, 2, 3]
    b = []

    c = (
        iterum(a)
        .map(lambda x: x * 2)
        .inspect(b.append)
        .take_while(lambda x: x < 5)
        .collect(list)
    )

    assert b == [2, 4, 6]
    assert c == [2, 4]


def test_last_basic_usage():
    assert iterum([1, 2, 3]).last() == Some(3)
    assert iterum([1, 2, 3, 4, 5]).last() == Some(5)


def test_le_basic_usage():
    assert iterum([1]).le([1])
    assert iterum([1]).le([1, 2])
    assert not iterum([1, 2]).le([1])
    assert iterum([1, 2]).le([1, 2])


def test_lt_basic_usage():
    assert not iterum([1]).lt([1])
    assert iterum([1]).lt([1, 2])
    assert not iterum([1, 2]).lt([1])
    assert not iterum([1, 2]).lt([1, 2])


def test_map_basic_usage():
    a = [1, 2, 3]
    itr = iterum(a).map(lambda x: x * 2)

    assert itr.next() == Some(2)
    assert itr.next() == Some(4)
    assert itr.next() == Some(6)
    assert itr.next() == nil


def checked_div(num: int, dem: int) -> Option[int]:
    try:
        return Some(num // dem)
    except ZeroDivisionError:
        return nil


def test_map_while_basic_usage():
    a = [-1, 4, 0, 1]

    it = iterum(a).map_while(partial(checked_div, 16))

    assert it.next() == Some(-16)
    assert it.next() == Some(4)
    assert it.next() == nil


def test_map_while_stop_after_first_nil():
    a = [0, 1, 2, -3, 4, 5, -6]

    it = iterum(a).map_while(lambda x: Some(x) if x >= 0 else nil)
    vec = it.collect(list)

    assert vec == [0, 1, 2]


def test_max_basic_usage():
    a = [1, 2, 3]
    b = []

    assert iterum(a).max() == Some(3)
    assert iterum(b).max() == nil


def test_max_by_basic_usage():
    a = [-3, 0, 1, 5, -10]

    assert iterum(a).max_by(Ordering.cmp).unwrap() == 5


def test_max_by_key_basic_usage():
    a = [-3, 0, 1, 5, -10]

    assert iterum(a).max_by_key(abs).unwrap() == -10


def test_min_basic_usage():
    a = [1, 2, 3]
    b = []

    assert iterum(a).min() == Some(1)
    assert iterum(b).min() == nil


def test_min_by_basic_usage():
    a = [-3, 0, 1, 5, -10]

    assert iterum(a).min_by(Ordering.cmp).unwrap() == -10


def test_min_by_key_basic_usage():
    a = [-3, 0, 1, 5, -10]

    assert iterum(a).min_by_key(abs).unwrap() == 0


def test_min_by_key_ensure_map_is_not_returned():
    a = [-3, 0, 1, 5]

    assert iterum(a).min_by_key(lambda x: -x).unwrap() == 5


def test_ne_basic_usage():
    assert not iterum([1]).ne([1])
    assert iterum([1]).ne([1, 2])


def test_nth_basic_usage():
    a = [1, 2, 3]

    assert iterum(a).nth(1) == Some(2)


def test_nth_no_rewind():
    itr = iterum([1, 2, 3])

    assert itr.nth(1) == Some(2)
    assert itr.nth(1) == nil


def test_nth_nil_if_past():
    itr = iterum([1, 2, 3])

    assert itr.nth(3) == nil


def test_partial_cmp_basic_usage():
    assert iterum([1]).partial_cmp([1]) == Some(Ordering.Equal)
    assert iterum([1, 2]).partial_cmp([1]) == Some(Ordering.Greater)
    assert iterum([1]).partial_cmp([1, 2]) == Some(Ordering.Less)


def test_partial_cmp_results_determined_by_order():
    assert iterum([1, None]).partial_cmp([2, nil]) == Some(Ordering.Less)
    assert iterum([2, None]).partial_cmp([1, nil]) == Some(Ordering.Greater)
    assert iterum([None, 1]).partial_cmp([2, None]) == nil


def test_partition_basic_usage():
    a = [1, 2, 3]

    even, odd = iterum(a).partition(lambda n: n % 2 == 0)

    assert even == [2]
    assert odd == [1, 3]


def test_peekable_basic_usage():
    xs = [1, 2, 3]

    itr = iterum(xs).peekable()

    assert itr.peek == Some(1)
    assert itr.next() == Some(1)

    assert itr.next() == Some(2)

    assert itr.peek == Some(3)
    assert itr.peek == Some(3)

    assert itr.next() == Some(3)

    assert itr.peek == nil
    assert itr.next() == nil


def test_peekable_setter():
    xs = [1, 2, 3]

    itr = iterum(xs).peekable()

    assert itr.peek == Some(1)
    assert itr.peek == Some(1)
    assert itr.next() == Some(1)

    assert itr.peek == Some(2)
    itr.peek = 1000

    assert list(itr) == [1000, 3]


def test_peekable_setting_peek_before_checking_it_is_okay():
    itr = iterum([1, 2, 3]).peekable()
    itr.peek = 1000

    assert list(itr) == [1000, 2, 3]


def test_peekable_setting_peek_past_end_raises():
    itr = iterum([1, 2, 3]).peekable()
    list(itr)

    with pytest.raises(IndexError) as ex:
        itr.peek = 1000

    assert str(ex.value) == "Cannot set peek value past end of the iterator"


def test_peekable_peek_then_iter():
    xs = [1, 2, 3]

    itr = iterum(xs).peekable()

    assert itr.peek == Some(1)
    assert list(itr) == [1, 2, 3]


def test_position_basic_usage():
    a = [1, 2, 3]

    assert iterum(a).position(lambda x: x == 2) == Some(1)
    assert iterum(a).position(lambda x: x == 5) == nil


def test_position_stop_after_the_first_true():
    it = iterum([1, 2, 3, 4])

    assert it.position(lambda x: x >= 2) == Some(1)
    assert it.next() == Some(3)
    assert it.position(lambda x: x == 4) == Some(0)


def test_product_factorial():
    def factorial(n: int) -> int:
        return iterum(range(1, n + 1)).product().unwrap_or(1)

    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120


def test_reduce_basic_usage():
    reduced = iterum(range(1, 10)).reduce(lambda acc, e: acc + e).unwrap()
    assert reduced == 45


def test_scan_not_so_basic_usage():
    itr = iterum([1, 2, 3, 4])

    def scanner(state: State, x: int) -> Option[int]:
        state.value *= x
        if state.value > 6:
            return nil
        return Some(-state.value)

    scan = itr.scan(1, scanner)
    assert scan.next() == Some(-1)
    assert scan.next() == Some(-2)
    assert scan.next() == Some(-6)
    assert scan.next() == nil


def test_skip_basic_usage():
    itr = iterum([1, 2, 3]).skip(2)

    assert itr.next() == Some(3)
    assert itr.next() == nil


def test_skip_past_end():
    itr = iterum([1, 2, 3]).skip(10)

    assert itr.next() == nil
    assert itr.next() == nil


def test_skip_while_basic_usage():
    itr = iterum([-1, 0, 1]).skip_while(lambda x: x < 0)

    assert itr.next() == Some(0)
    assert itr.next() == Some(1)
    assert itr.next() == nil


def test_skip_while_blown_fuse_no_recover():
    itr = iterum([-1, 0, 1, -3]).skip_while(lambda x: x < 0)

    assert itr.next() == Some(0)
    assert itr.next() == Some(1)
    assert itr.next() == Some(-3)
    assert itr.next() == nil


def test_step_by_basic_usage():
    itr = iterum([0, 1, 2, 3, 4, 5]).step_by(2)

    assert itr.next() == Some(0)
    assert itr.next() == Some(2)
    assert itr.next() == Some(4)
    assert itr.next() == nil


def test_sum_basic_usage():
    a = [1, 2, 3]
    sum_ = iterum(a).sum().unwrap()

    assert sum_ == 6


def test_take_basic_usage():
    a = [1, 2, 3]
    itr = iterum(a).take(2)

    assert itr.next() == Some(1)
    assert itr.next() == Some(2)
    assert itr.next() == nil


def test_take_basic_usage2():
    a = [1, 2, 3]
    itr = iterum(a).take(2)

    assert list(itr) == [1, 2]
    assert itr.next() == nil


def test_take_truncates_infinite():
    itr = iterum(count_forever()).take(3)

    assert itr.next() == Some(0)
    assert itr.next() == Some(1)
    assert itr.next() == Some(2)
    assert itr.next() == nil


def test_take_more_than_you_have():
    itr = iterum([1, 2]).take(5)

    assert itr.next() == Some(1)
    assert itr.next() == Some(2)
    assert itr.next() == nil


def test_take_while_basic_usage():
    a = [-1, 0, 1]
    itr = iterum(a).take_while(lambda x: x < 0)

    assert itr.next() == Some(-1)
    assert itr.next() == nil


def test_take_while_stop_after_first_false():
    a = [-1, 0, 1, -2]
    itr = iterum(a).take_while(lambda x: x < 0)

    assert itr.next() == Some(-1)
    assert itr.next() == nil


def checked_add_i8(lhs: int, rhs: int) -> int:
    value = lhs + rhs
    if -128 <= value <= 127:
        return value
    else:
        raise ValueError("Overflow!")


def test_try_fold_basic_usage():
    a = [1, 2, 3]

    sum = iterum(a).try_fold(0, checked_add_i8)

    assert sum == Some(6)


def test_try_fold_short_circuiting():
    it = iterum([10, 20, 30, 100, 40, 50])

    sum = it.try_fold(0, checked_add_i8)

    assert sum == nil
    assert list(it) == [40, 50]


def test_unzip_basic_usage():
    a = [(1, 2), (3, 4), (5, 6)]

    left, right = iterum(a).unzip()

    assert left == [1, 3, 5]
    assert right == [2, 4, 6]


@pytest.mark.xfail(reason="Just not cool enough...")
def test_unzip_multiple():
    a = [(1, (2, 3)), (4, (5, 6))]

    (x, (y, z)) = iterum(a).unzip()
    assert x == [1, 4]
    assert y == [2, 5]
    assert z == [3, 6]


def test_zip_basic_usage():
    a1 = [1, 2, 3]
    a2 = [4, 5, 6]
    itr = iterum(a1).zip(a2)

    assert itr.next() == Some((1, 4))
    assert itr.next() == Some((2, 5))
    assert itr.next() == Some((3, 6))
    assert itr.next() == nil


def test_zip_against_larger():
    cf_itr = iterum(count_forever())
    foo_itr = iterum("foo")
    zip_itr = foo_itr.zip(cf_itr)

    assert zip_itr.next() == Some(("f", 0))
    assert zip_itr.next() == Some(("o", 1))
    assert zip_itr.next() == Some(("o", 2))
    assert zip_itr.next() == nil

    assert foo_itr.next() == nil
    # Presumably here we zip_itr next
    assert cf_itr.next() == Some(3)


def test_zip_against_smaller():
    cf_itr = iterum(count_forever())
    foo_itr = iterum("foo")
    zip_itr = cf_itr.zip(foo_itr)

    assert zip_itr.next() == Some((0, "f"))
    assert zip_itr.next() == Some((1, "o"))
    assert zip_itr.next() == Some((2, "o"))
    assert zip_itr.next() == nil

    assert foo_itr.next() == nil
    assert cf_itr.next() == Some(4)
