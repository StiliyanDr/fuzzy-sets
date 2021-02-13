
def default_if_none(value, default):
    return (value
            if (value is not None)
            else default)


def to_float_if_int(value):
    return (float(value)
            if (isinstance(value, int))
            else value)


def verify_is_numeric(value):
    if (not isinstance(value, float)):
        raise ValueError(
            f"Expected a number but received: {value!r}"
        )


def sign_of(number):
    return ("+"
            if (number >= 0)
            else "-")
