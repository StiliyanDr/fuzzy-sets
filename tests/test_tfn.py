import pytest

from numpy.polynomial.polynomial import Polynomial

from fuzzysets.tfn import (
    _PolynomialPair,
    AlphaCut,
    TriangularFuzzyNumber,
)


class TestPolynomialPair:
    def test_when_polynomials_are_passed_then_a_pair_of_their_values_is_returned(self):
        p = Polynomial([1, 2, 3])
        q = Polynomial([4, 5, 6])
        pair = _PolynomialPair(p, q)

        assert pair(0.5) == (p(0.5), q(0.5))

    def test_when_pairs_of_polynomials_are_passed_then_a_pair_of_division_results_is_returned(self):
        p = Polynomial([1, 2, 3])
        q = Polynomial([4, 5, 6])
        r = Polynomial([7, 8, 9])
        s = Polynomial([10, 11, 12])
        pair = _PolynomialPair((p, q), (r, s))

        assert pair(0.5) == (p(0.5) / q(0.5), r(0.5) / s(0.5))


class TestAlphaCut:
    def test_for_alpha(self, alpha_cut):
        assert alpha_cut.for_alpha(0.5) == (1.5, 2.5)

    def test_str(self, alpha_cut):
        assert str(alpha_cut) == "[1.0 + alpha * 1.0, 3.0 + alpha * -1.0]"

    def test_repr(self, alpha_cut):
        assert repr(alpha_cut) == "AlphaCut(1.0 + alpha * 1.0, 3.0 + alpha * -1.0)"


class TestTriangularFuzzyNumber:
    def test_from_tuple_with_valid_tuple_returns_a_tfn(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert tfn.left == 1
        assert tfn.peak == 2
        assert tfn.right == 3

    def test_from_tuple_with_invalid_numeric_values_raises_a_value_error(self):
        with pytest.raises(ValueError):
            TriangularFuzzyNumber.from_tuple((1, 2, 1))

    def test_from_tuple_with_invalid_tuple_length_raises_a_value_error(self):
        with pytest.raises(ValueError):
            TriangularFuzzyNumber.from_tuple((1, 2))

    def test_from_tuple_with_invalid_tuple_elements_raises_a_value_error(self):
        with pytest.raises(ValueError):
            TriangularFuzzyNumber.from_tuple((1, 2, "three"))

    def test_from_tuple_with_a_list_raises_a_value_error(self):
        with pytest.raises(ValueError):
            TriangularFuzzyNumber.from_tuple([1, 2, 3])

    def test_ctor_with_default_values(self):
        tfn = TriangularFuzzyNumber()

        assert tfn.left == -1.0
        assert tfn.peak == 0.0
        assert tfn.right == 1.0

    def test_ctor_with_peak_only_offsets_left_and_right(self):
        tfn = TriangularFuzzyNumber(2)

        assert tfn.left == 1.0
        assert tfn.peak == 2.0
        assert tfn.right == 3.0

    def test_ctor_with_peak_and_left_offsets_right(self):
        tfn = TriangularFuzzyNumber(2, 1)

        assert tfn.left == 1.0
        assert tfn.peak == 2.0
        assert tfn.right == 3.0

    def test_ctor_with_peak_and_right_offsets_left(self):
        tfn = TriangularFuzzyNumber(2, r=3)

        assert tfn.left == 1.0
        assert tfn.peak == 2.0
        assert tfn.right == 3.0

    def test_ctor_with_all_values(self):
        tfn = TriangularFuzzyNumber(2, 1, 3)

        assert tfn.left == 1.0
        assert tfn.peak == 2.0
        assert tfn.right == 3.0

    def test_mu_with_a_value_less_than_left_returns_0(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert tfn.mu(0.5) == 0.0

    def test_mu_with_a_value_greater_than_right_returns_0(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert tfn.mu(4.0) == 0.0

    def test_mu_with_a_value_between_left_and_peak(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert tfn.mu(1.5) == 0.5

    def test_mu_with_a_value_between_peak_and_right(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert tfn.mu(2.5) == 0.5

    def test_mu_with_a_value_equal_to_left_returns_0(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert tfn.mu(1.0) == 0.0

    def test_mu_with_a_value_equal_to_right_returns_0(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert tfn.mu(3.0) == 0.0

    def test_mu_with_a_value_equal_to_peak_returns_1(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert tfn.mu(2.0) == 1.0

    def test_addition_with_different_types_raises_a_type_error(self, tfn):
        with pytest.raises(TypeError):
            tfn + 1
    
    def test_addition_with_a_tfn_returns_a_tfn(self):
        lhs = TriangularFuzzyNumber.from_tuple((1, 2, 3))
        rhs = TriangularFuzzyNumber.from_tuple((4, 5, 6))

        result = lhs + rhs

        assert isinstance(result, TriangularFuzzyNumber)
        assert result.left == 5.0
        assert result.peak == 7.0
        assert result.right == 9.0

    def test_negation_returns_a_tfn(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        result = -tfn

        assert isinstance(result, TriangularFuzzyNumber)
        assert result.left == -3.0
        assert result.peak == -2.0
        assert result.right == -1.0

    def test_subtraction_with_different_types_raises_a_type_error(self, tfn):
        with pytest.raises(TypeError):
            tfn - 1

    def test_subtraction_with_a_tfn_returns_a_tfn(self):
        lhs = TriangularFuzzyNumber.from_tuple((1, 2, 3))
        rhs = TriangularFuzzyNumber.from_tuple((4, 5, 6))

        result = lhs - rhs

        assert isinstance(result, TriangularFuzzyNumber)
        assert result.left == -5.0
        assert result.peak == -3.0
        assert result.right == -1.0

    def test_multiplication_with_different_types_raises_a_type_error(self, tfn):
        with pytest.raises(TypeError):
            tfn * 1

    def test_multiplication_with_a_tfn_returns_a_tfn(self):
        lhs = TriangularFuzzyNumber.from_tuple((1, 2, 3))
        rhs = TriangularFuzzyNumber.from_tuple((4, 5, 6))

        result = lhs * rhs

        assert isinstance(result, TriangularFuzzyNumber)
        assert result.left == 4.0
        assert result.peak == 10.0
        assert result.right == 18.0

    def test_division_with_different_types_raises_a_type_error(self, tfn):
        with pytest.raises(TypeError):
            tfn / 1

    def test_division_with_a_tfn_returns_a_tfn(self):
        lhs = TriangularFuzzyNumber.from_tuple((1, 2, 3))
        rhs = TriangularFuzzyNumber.from_tuple((3, 4, 5))

        result = lhs / rhs

        assert isinstance(result, TriangularFuzzyNumber)
        assert result.left == 0.2
        assert result.peak == 0.5
        assert result.right == 1.0

    def test_eq_with_a_different_type_returns_false(self, tfn):
        assert not tfn == 1

    def test_eq_with_a_tfn_with_the_same_values_returns_true(self, tfn):
        assert tfn == TriangularFuzzyNumber.from_tuple(tuple(tfn))

    def test_eq_with_a_tfn_with_different_values_returns_false(self, tfn, another_tfn):
        assert not tfn == another_tfn

    def test_ne_with_a_different_type_returns_true(self, tfn):
        assert tfn != 1

    def test_ne_with_a_tfn_with_the_same_values_returns_false(self, tfn):
        assert not tfn != TriangularFuzzyNumber.from_tuple(tuple(tfn))

    def test_ne_with_a_tfn_with_different_values_returns_true(self, tfn, another_tfn):
        assert tfn != another_tfn

    def test_lt_with_a_different_type_raises_a_type_error(self, tfn):
        with pytest.raises(TypeError):
            tfn < 1

    def test_lt_with_a_tfn_with_the_same_values_returns_false(self, tfn):
        assert not tfn < TriangularFuzzyNumber.from_tuple(tuple(tfn))

    def test_lt_with_a_tfn_with_different_peak_value_returns_false(self):
        lhs = TriangularFuzzyNumber.from_tuple((1, 2, 3))
        rhs = TriangularFuzzyNumber.from_tuple((1, 3, 4))

        assert not lhs < rhs

    def test_lt_with_a_tfn_containing_it_returns_true(self):
        lhs = TriangularFuzzyNumber.from_tuple((1, 2, 3))
        rhs = TriangularFuzzyNumber.from_tuple((1, 2, 4))

        assert lhs < rhs

    def test_gt_with_a_different_type_raises_a_type_error(self, tfn):
        with pytest.raises(TypeError):
            tfn > 1

    def test_gt_with_a_tfn_with_the_same_values_returns_false(self, tfn):
        assert not tfn > TriangularFuzzyNumber.from_tuple(tuple(tfn))

    def test_gt_with_a_tfn_within_it_returns_true(self):
        lhs = TriangularFuzzyNumber.from_tuple((1, 2, 3))
        rhs = TriangularFuzzyNumber.from_tuple((1.5, 2, 2.5))

        assert lhs > rhs

    def test_le_with_a_different_type_raises_a_type_error(self, tfn):
        with pytest.raises(TypeError):
            tfn <= 1

    def test_le_with_equal_tfn_returns_true(self, tfn):
        assert tfn <= TriangularFuzzyNumber.from_tuple(tuple(tfn))

    def test_le_with_a_larger_tfn_returns_true(self):
        lhs = TriangularFuzzyNumber.from_tuple((1, 2, 3))
        rhs = TriangularFuzzyNumber.from_tuple((1, 2, 4))

        assert lhs <= rhs

    def test_ge_with_a_different_type_raises_a_type_error(self, tfn):
        with pytest.raises(TypeError):
            tfn >= 1

    def test_ge_with_equal_tfn_returns_true(self, tfn):
        assert tfn >= TriangularFuzzyNumber.from_tuple(tuple(tfn))

    def test_ge_with_a_smaller_tfn_returns_true(self):
        lhs = TriangularFuzzyNumber.from_tuple((1, 2, 3))
        rhs = TriangularFuzzyNumber.from_tuple((1, 2, 2.5))

        assert lhs >= rhs

    def test_iter_returns_left_peak_and_right_values(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert tuple(tfn) == (1, 2, 3)

    def test_hash_returns_a_hash_of_the_tuple_representation(self):
        t = (1, 2, 3)
        tfn = TriangularFuzzyNumber.from_tuple(t)

        assert hash(tfn) == hash(t)

    def test_repr_returns_a_string_representation_of_the_tfn(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert repr(tfn) == "TriangularFuzzyNumber(l=1.0, n=2.0, r=3.0)"

    def test_str_returns_repr(self, tfn):
        assert str(tfn) == repr(tfn)

    def test_alpha_cut_returns_an_alpha_cut_instance(self):
        tfn = TriangularFuzzyNumber.from_tuple((1, 2, 3))

        assert isinstance(tfn.alpha_cut, AlphaCut)
        assert str(tfn.alpha_cut) == "[1.0 + alpha * 1.0, 3.0 + alpha * -1.0]"
