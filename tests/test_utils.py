import pytest

from fuzzysets import utils


def test_default_if_none():
    assert utils.default_if_none(None, 1) == 1
    assert utils.default_if_none(1, 2) == 1


def test_to_float_if_int():
    assert utils.to_float_if_int(1) == 1.0
    assert utils.to_float_if_int("s") == "s"


def test_is_membership_degree():
    assert utils.is_membership_degree(0.5)
    assert not utils.is_membership_degree(1.5)
    assert not utils.is_membership_degree(-0.5)
    assert not utils.is_membership_degree("s")


def test_validate_alpha():
    utils.validate_alpha(0.5)

    with pytest.raises(ValueError):
        utils.validate_alpha(1.5)


def test_verify_is_numeric():
    utils.verify_is_numeric(1.0)

    with pytest.raises(ValueError):
        utils.verify_is_numeric("s")


def test_complement():
    assert utils.complement(0.5) == 0.5
    assert utils.complement(1.0) == 0.0
