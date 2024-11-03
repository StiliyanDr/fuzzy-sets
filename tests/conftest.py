import pytest

from fuzzysets.tfn import AlphaCut, TriangularFuzzyNumber


@pytest.fixture
def tfn():
    return TriangularFuzzyNumber.from_tuple((1, 2, 3))


@pytest.fixture
def another_tfn():
    return TriangularFuzzyNumber.from_tuple((4, 5, 6))


@pytest.fixture
def alpha_cut(tfn):
    return AlphaCut.for_tfn(tfn)


@pytest.fixture
def another_alpha_cut():
    return AlphaCut.for_tfn(TriangularFuzzyNumber.from_tuple((4, 5, 6)))
