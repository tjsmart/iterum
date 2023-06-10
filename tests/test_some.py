from rust_iterator import Some


def test_eq():
    assert Some(3) == Some(3)
    assert Some(3) != Some(5)


def test_repr():
    assert repr(Some("test")) == f"{Some.__name__}({repr('test')})"
