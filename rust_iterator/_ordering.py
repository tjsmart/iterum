from __future__ import annotations

from enum import Enum
from enum import unique

from ._singleton import create_singleton


@unique
class Ordering(Enum):
    Less = create_singleton("Less")
    Equal = create_singleton("Equal")
    Greater = create_singleton("Greater")
