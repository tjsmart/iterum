from __future__ import annotations

from typing import assert_type

from iterum import InfSeq
from iterum import Seq
from iterum import seq


def seq_with_explicit_start_end_returns_seq():
    assert_type(seq(0, 10), Seq)
    assert_type(seq(0, 10, 5), Seq)
    assert_type(seq(0, 10, step=5), Seq)


def seq_with_explicit_end_returns_seq():
    assert_type(seq(10), Seq)
    assert_type(seq(10, step=5), Seq)


def seq_with_explicit_start_and_no_end_returns_seq():
    assert_type(seq(0, ...), InfSeq)
    assert_type(seq(0, ..., 5), InfSeq)
    assert_type(seq(0, ..., step=5), InfSeq)


def seq_with_no_end_returns_infseq():
    assert_type(seq(...), InfSeq)
    assert_type(seq(..., step=5), InfSeq)
