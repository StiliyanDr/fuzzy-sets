
def default_if_none(value, default):
    return (value
            if (value is not None)
            else default)


def to_float_if_int(value):
    return (float(value)
            if (isinstance(value, int))
            else value)


def validate_alpha(a):
    verify_is_numeric(a)

    if (not (0. <= a <= 1.)):
        raise ValueError("Alpha must be between 0 and 1!")


def verify_is_numeric(value):
    if (not isinstance(value, float)):
        raise ValueError(
            f"Expected a number but received: {value!r}"
        )


def complement(x):
    return 1. - x
