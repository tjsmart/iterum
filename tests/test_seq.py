import pytest

from iterum import nil
from iterum import seq
from iterum import Some
from iterum._seq import _compute_back


def test_seq_simple_next():
    itr = seq(0, 3)

    assert itr.next() == Some(0)
    assert itr.next() == Some(1)
    assert itr.next() == Some(2)
    assert itr.next() == nil


def test_seq_simple_next_back():
    itr = seq(0, 3)

    assert itr.next_back() == Some(2)
    assert itr.next_back() == Some(1)
    assert itr.next_back() == Some(0)
    assert itr.next_back() == nil


def test_seq_simple_back_and_forth_len():
    itr = seq(0, 3)

    assert itr.len() == 3
    assert itr.next_back() == Some(2)
    assert itr.len() == 2
    assert itr.next() == Some(0)
    assert itr.len() == 1
    assert itr.next_back() == Some(1)
    assert itr.len() == 0

    assert itr.next() == nil
    assert itr.len() == 0
    assert itr.next_back() == nil
    assert itr.len() == 0


def test_seq_with_step_next():
    itr = seq(1, 15, 5)

    assert itr.next() == Some(1)
    assert itr.next() == Some(6)
    assert itr.next() == Some(11)
    assert itr.next() == nil


def test_seq_with_step_next_back():
    itr = seq(1, 15, 5)

    assert itr.next_back() == Some(11)
    assert itr.next_back() == Some(6)
    assert itr.next_back() == Some(1)
    assert itr.next_back() == nil


def test_seq_with_step_back_and_forth_len():
    itr = seq(1, 15, 5)

    assert itr.len() == 3
    assert itr.next_back() == Some(11)
    assert itr.len() == 2
    assert itr.next() == Some(1)
    assert itr.len() == 1
    assert itr.next_back() == Some(6)
    assert itr.len() == 0

    assert itr.next() == nil
    assert itr.len() == 0
    assert itr.next_back() == nil
    assert itr.len() == 0


def test_seq_backwards_next():
    itr = seq(0, -3, -1)

    assert itr.next() == Some(0)
    assert itr.next() == Some(-1)
    assert itr.next() == Some(-2)
    assert itr.next() == nil


def test_seq_backwards_next_back():
    itr = seq(0, -3, -1)

    assert itr.next_back() == Some(-2)
    assert itr.next_back() == Some(-1)
    assert itr.next_back() == Some(0)
    assert itr.next_back() == nil


def test_seq_backwards_back_and_forth_len():
    itr = seq(0, -3, -1)

    assert itr.len() == 3
    assert itr.next_back() == Some(-2)
    assert itr.len() == 2
    assert itr.next() == Some(0)
    assert itr.len() == 1
    assert itr.next_back() == Some(-1)
    assert itr.len() == 0

    assert itr.next() == nil
    assert itr.len() == 0
    assert itr.next_back() == nil
    assert itr.len() == 0


def test_seq_eq():
    assert seq(1, 10, 5) == seq(1, 10, 5)
    assert seq(1, 10, 5) == seq(1, 11, 5)  # will still end with same value
    assert seq(1, 10, 5) != seq(0, 10, 5)
    assert seq(1, 10, 5) != seq(1, 3, 5)
    assert seq(1, 10, 5) != seq(1, 10, -1)


def test_seq_repr():
    itr = seq(1, 10, 5)

    assert repr(itr) == "Seq(start=1, end=11, step=5)"


def test_seq_bool():
    itr = seq(3)
    assert itr
    assert itr.next() == Some(0)
    assert itr
    assert itr.next() == Some(1)
    assert itr
    assert itr.next() == Some(2)

    assert not itr
    assert itr.next() == nil
    assert not itr


def test_infseq_simple_next():
    itr = seq(...)

    for i in range(10_000):
        assert itr.next() == Some(i)


def test_infseq_with_step_next():
    itr = seq(1, ..., 5)

    for i in range(1, 10_000, 5):
        assert itr.next() == Some(i)


def test_infseq_backwards_next():
    itr = seq(-1, ..., -1)

    for i in range(-1, -10_000, -1):
        assert itr.next() == Some(i)


def test_infseq_eq():
    assert seq(1, ..., 5) == seq(1, ..., 5)
    assert seq(1, ..., 5) != seq(0, ..., 5)
    assert seq(1, ..., 5) != seq(1, ..., -1)


def test_infseq_repr():
    itr = seq(1, ..., 5)

    assert repr(itr) == "InfSeq(start=1, step=5)"


@pytest.mark.parametrize(
    ("start", "end", "step", "expected"),
    [
        (1, 10, 2, 9),
        (1, 10, 4, 9),
        (1, 10, 5, 6),
        (1, 10, 3, 7),
    ],
)
def test_compute_back(start, end, step, expected):
    assert _compute_back(start, end, step) == expected
