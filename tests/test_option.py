from __future__ import annotations

import pytest

from iterum import ExpectNilError
from iterum import Nil
from iterum import nil
from iterum import Option
from iterum import Some
from iterum import Swap
from iterum import UnwrapNilError


def test_eq():
    assert Some(3) == Some(3)
    assert Some(3) != Some(5)


def test_repr():
    assert repr(Some("test")) == f"{Some.__name__}({repr('test')})"


def test_and_basic_usage():
    assert Some(2).and_(nil) == nil
    assert nil.and_(Some("foo")) == nil
    assert Some(2).and_(Some("foo")) == Some("foo")
    assert nil.and_(nil) == nil


MAX_U32 = (1 << 32) - 1


def checked_sq_u32(x: int) -> Option[int]:
    sq = x * x
    if sq > MAX_U32:
        return nil
    return Some(sq)


def test_and_then_basic_usage():
    assert Some(2).and_then(checked_sq_u32) == Some(4)
    assert Some(1_000_000).and_then(checked_sq_u32) == nil
    assert nil.and_then(checked_sq_u32) == nil


def test_expect_basic_usage():
    x = Some("value")
    assert x.expect("fruits are healthy") == "value"

    x = nil
    with pytest.raises(ExpectNilError) as ex:
        x.expect("fruits are healthy")
    assert str(ex.value) == "fruits are healthy"


def is_even(n: int) -> bool:
    return n % 2 == 0


def test_filter_basic_usage():
    assert nil.filter(is_even) == nil
    assert Some(3).filter(is_even) == nil
    assert Some(4).filter(is_even) == Some(4)


def test_flatten_basic_usage():
    assert Some(Some(6)).flatten() == Some(6)
    assert Some(nil).flatten() == nil
    assert nil.flatten() == nil


def test_get_or_insert_basic_usage():
    x = nil
    x, y = x.get_or_insert(5)
    assert y == 5
    y = 7
    assert x == Some(5)


def test_get_or_insert_returned_value():
    assert Some(10).get_or_insert(5).returned == 10
    assert nil.get_or_insert(5).returned == 5


def test_get_or_insert_inserted_value():
    assert Some(10).get_or_insert(5).inserted == Some(10)
    assert nil.get_or_insert(5).inserted == Some(5)


def test_get_or_insert_with_basic_usage():
    x = nil
    x, y = x.get_or_insert_with(lambda: 5)
    assert y == 5
    y = 7
    assert x == Some(5)


def test_get_or_insert_with_returned_value():
    assert Some(10).get_or_insert_with(lambda: 5).returned == 10
    assert nil.get_or_insert_with(lambda: 5).returned == 5


def test_get_or_insert_with_inserted_value():
    assert Some(10).get_or_insert_with(lambda: 5).inserted == Some(10)
    assert nil.get_or_insert_with(lambda: 5).inserted == Some(5)


def test_insert_basic_usage():
    opt = nil
    opt, val = opt.insert(1)

    assert val == 1
    assert opt.unwrap() == 1


def test_insert_returned_value():
    assert Some(10).insert(5).returned == 5
    assert nil.insert(5).returned == 5


def test_insert_inserted_value():
    assert Some(10).insert(5).inserted == Some(5)
    assert nil.insert(5).inserted == Some(5)


def test_is_nil_basic_usage():
    assert Some(2).is_nil() is False
    assert nil.is_nil() is True


def test_is_some_basic_usage():
    assert Some(2).is_some() is True
    assert nil.is_some() is False


def test_is_some_and_basic_usage():
    assert Some(2).is_some_and(lambda x: x > 1) is True
    assert Some(0).is_some_and(lambda x: x > 1) is False
    assert nil.is_some_and(lambda x: x > 1) is False


def test_iter_basic_usage():
    assert Some(4).iter().next() == Some(4)
    assert nil.iter().next() == nil


def test_map_basic_usage():
    assert Some("Hello, World!").map(len) == Some(13)
    assert nil.map(len) == nil


def test_map_or_basic_usage():
    assert Some("foo").map_or(42, len) == 3
    assert nil.map_or(42, len) == 42


def test_map_or_else_basic_usage():
    k = 21
    assert Some("foo").map_or_else(lambda: 2 * k, len) == 3
    assert nil.map_or_else(lambda: 2 * k, len) == 42


def test_ok_or_basic_usage():
    assert Some("foo").ok_or(RuntimeError("oh no!")) == "foo"

    with pytest.raises(RuntimeError) as ex:
        assert nil.ok_or(RuntimeError("oh no!"))
    assert str(ex.value) == "oh no!"


def test_ok_or_else_basic_usage():
    assert Some("foo").ok_or_else(AssertionError) == "foo"

    with pytest.raises(AssertionError) as ex:
        assert nil.ok_or_else(AssertionError)
    assert str(ex.value) == ""


def test_or_basic_usage():
    assert Some(2).or_(nil) == Some(2)
    assert nil.or_(Some(100)) == Some(100)
    assert Some(2).or_(Some(100)) == Some(2)
    assert nil.or_(nil) == nil


def nobody() -> Option[str]:
    return nil


def vikings() -> Option[str]:
    return Some("vikings")


def test_or_else_basic_usage():
    assert Some("barbarians").or_else(vikings) == Some("barbarians")
    assert nil.or_else(vikings) == Some("vikings")
    assert nil.or_else(nobody) == nil


def test_replace_basic_usage():
    x = Some(2)
    x, old = x.replace(5)
    assert x == Some(5)
    assert old == Some(2)

    x = nil
    x, old = x.replace(5)
    assert x == Some(5)
    assert old == nil


def test_take_basic_usage():
    x = Some(2)
    x, y = x.take()
    assert x == nil
    assert y == Some(2)

    x = nil
    x, y = x.take()
    assert x == nil
    assert y == nil


def test_unwrap_basic_usage():
    assert Some("air").unwrap() == "air"
    with pytest.raises(UnwrapNilError):
        nil.unwrap()


def test_unwrap_or_basic_usage():
    assert Some("car").unwrap_or("bike") == "car"
    assert nil.unwrap_or("bike") == "bike"


def test_unwrap_or_else_basic_usage():
    k = 10
    assert Some(4).unwrap_or_else(lambda: 2 * k) == 4
    assert nil.unwrap_or_else(lambda: 2 * k) == 20


def test_unzip_basic_usage():
    assert Some((1, "hi")).unzip() == (Some(1), Some("hi"))
    assert nil.unzip() == (nil, nil)


def test_xor_basic_usage():
    assert Some(2).xor(nil) == Some(2)
    assert nil.xor(Some(100)) == Some(100)
    assert Some(2).xor(Some(100)) == nil
    assert nil.xor(nil) == nil


def test_zip_basic_usage():
    assert Some(1).zip(Some("hi")) == Some((1, "hi"))
    assert Some(1).zip(nil) == nil
    assert nil.zip(nil) == nil
