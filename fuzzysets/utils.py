import numpy as np


def default_if_none(value, default):
    return (value
            if (value is not None)
            else default)


def to_float_if_int(value):
    return (float(value)
            if (isinstance(value, int))
            else value)


def validate_alpha(a):
    if (not is_membership_degree(a)):
        raise ValueError("Alpha must be a float between 0 and 1!")


def is_membership_degree(d):
    return isinstance(d, float) and 0. <= d <= 1.


is_membership_degree_v = np.vectorize(
    is_membership_degree
)


def verify_is_numeric(value):
    if (not isinstance(value, float)):
        raise ValueError(
            f"Expected a number but received: {value!r}"
        )


def complement(x):
    return 1. - x
