# iterum

<div align="center">
<img src="https://raw.githubusercontent.com/tjsmart/iterum/main/docs/assets/logo.png" alt="Iterum logo" width="500" role="img">
</div>


[![PyPI - Version](https://img.shields.io/pypi/v/iterum.svg)](https://pypi.org/project/iterum)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/iterum.svg)](https://pypi.org/project/iterum)
[![project - uv](https://img.shields.io/badge/%F0%9F%A5%9A-uv-4051b5.svg)](https://github.com/astral-sh/uv)


[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![types - ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

-----

Rusty iterators in Python.

## Installation

```console
pip install iterum
```

## Documentation

The [documentation](https://tjsmart.github.io/iterum) is made with [Material for MkDocs](https://github.com/squidfunk/mkdocs-material) and is hosted by [GitHub Pages](https://docs.github.com/en/pages).


## Example

```python
from iterum import iterum, Some, nil, seq

itr = iterum([1, 2])
assert itr.next() == Some(1)
assert itr.next() == Some(2)
assert itr.next() == nil

itr = iterum([1, 2, 3, 4])
assert itr.fold(0, lambda acc, x: acc + x) == 10

lst = (
    seq(5)
    .map(lambda x: x**2 + 1)
    .filter(lambda x: x % 2)
    .collect()
)
assert lst == [1, 5, 17]
```

## License

`iterum` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
