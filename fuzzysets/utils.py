from typing import (
    Any,
    TypeVar,
    Union,
)

import numpy as np


T = TypeVar("T")
U = TypeVar("U")


def default_if_none(value: T, default: U) -> Union[T, U]:
    return (value
            if (value is not None)
            else default)


def to_float_if_int(value: T) -> Union[float, T]:
    return (float(value)
            if (isinstance(value, int))
            else value)


def validate_alpha(a: Any) -> None:
    if (not is_membership_degree(a)):
        raise ValueError("Alpha must be a float between 0 and 1!")


def is_membership_degree(d: Any) -> bool:
    return isinstance(d, float) and 0. <= d <= 1.


is_membership_degree_v = np.vectorize(
    is_membership_degree
)


def verify_is_numeric(value: Any) -> None:
    if (not isinstance(value, float)):
        raise ValueError(
            f"Expected a number but received: {value!r}"
        )


def complement(x: float) -> float:
    return 1. - x
