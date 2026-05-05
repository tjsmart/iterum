from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import TYPE_CHECKING
from typing import TypeVar


if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison
    from _typeshed import SupportsRAdd
    from _typeshed import SupportsAdd


T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


if TYPE_CHECKING:
    SupportsRichComparisonT = TypeVar(
        "SupportsRichComparisonT", bound=SupportsRichComparison
    )

    class SupportsMul(Protocol[T_contra, T_co]):
        def __mul__(self, __x: T_contra) -> T_co:
            ...

    SupportsMulT = TypeVar("SupportsMulT", bound=SupportsMul)

    class SupportsSumWithNoDefaultGiven(
        SupportsAdd[Any, Any], SupportsRAdd[int, Any], Protocol
    ):
        ...

    SupportsSumNoDefaultT = TypeVar(
        "SupportsSumNoDefaultT", bound=SupportsSumWithNoDefaultGiven
    )
