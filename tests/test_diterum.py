from iterum import diterum
from iterum import nil
from iterum import Some


def test_next_back_basic_usage():
    di = diterum([1, 2, 3, 4, 5, 6])

    assert di.next() == Some(1)
    assert di.next_back() == Some(6)
    assert di.next_back() == Some(5)
    assert di.next() == Some(2)
    assert di.next() == Some(3)
    assert di.next() == Some(4)
    assert di.next() == nil
    assert di.next_back() == nil


def test_nth_back_basic_usage():
    di = diterum([1, 2, 3])

    assert di.nth_back(2) == Some(1)


def test_nth_back_does_not_rewind():
    di = diterum([1, 2, 3])

    assert di.nth_back(1) == Some(2)
    assert di.nth_back(1) == nil


def test_nth_back_return_nil_if_not_enough_elements():
    di = diterum([1, 2, 3])

    assert di.nth_back(10) == nil


def test_rfind_basic_usage():
    di = diterum([1, 2, 3])

    assert di.rfind(lambda x: x == 2) == Some(2)
    assert di.rfind(lambda x: x == 5) == nil


def test_rfind_stop_after_first_true():
    di = diterum([1, 2, 3])

    assert di.rfind(lambda x: x == 2) == Some(2)
    assert di.next_back() == Some(1)


def test_rfold_basic_usage():
    di = diterum([1, 2, 3])

    sum = di.rfold(0, lambda acc, x: acc + x)
    assert sum == 6


def test_rfold_right_associative():
    numbers = [1, 2, 3, 4, 5]
    zero = "0"

    result = diterum(numbers).rfold(zero, lambda acc, x: f"({x} + {acc})")

    assert result == "(1 + (2 + (3 + (4 + (5 + 0)))))"


def test_try_rfold_basic_usage():
    di = diterum(["1", "2", "3"])

    sum = di.try_rfold(0, lambda acc, x: acc + int(x), exception=TypeError)

    assert sum == Some(6)


def test_rev_basic_usage():
    di = diterum([1, 2, 3]).rev()

    assert di.next() == Some(3)
    assert di.next() == Some(2)
    assert di.next() == Some(1)
    assert di.next() == nil


def test_rposition_basic_usage():
    di = diterum([1, 2, 3])

    assert di.rposition(lambda x: x == 3) == Some(2)
    assert di.rposition(lambda x: x == 5) == nil


def test_rposition_stop_after_first_true():
    di = diterum([-1, 2, 3, 4])

    assert di.rposition(lambda x: x >= 2) == Some(3)
    assert di.next() == Some(-1)


def test_len_basic_usage():
    di = diterum([1, 2, 3, 4])

    assert di.len() == 4

    assert di.next() == Some(1)
    assert di.len() == 3

    assert di.next_back() == Some(4)
    assert di.len() == 2

    assert di.collect() == [2, 3]
    assert di.len() == 0

    assert di.next() == nil
    assert di.len() == 0
