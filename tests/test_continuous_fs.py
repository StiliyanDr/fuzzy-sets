import pytest

from fuzzysets.sets.continuous import ContinuousDomain, ContinuousFuzzySet


class TestContinuousDomain:
    def test_init_with_invalid_range_raises_value_error(self):
        with pytest.raises(ValueError):
            ContinuousDomain("x", 1.5)

    def test_init_with_negative_step_raises_value_error(self):
        with pytest.raises(ValueError):
            ContinuousDomain(1.0, 1.5, -0.5)

    def test_init_with_valid_range_and_step_returns_domain(self):
        domain = ContinuousDomain(1.0, 1.5, 0.1)

        assert domain.start == 1.0
        assert domain.end == 1.5
        assert domain.step == 0.1

    def test_iter_returns_elements_in_range(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)

        assert list(domain) == [1.0, 1.5, 2.0, 2.5]

    def test_contains_returns_true_if_item_in_range(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)

        assert 1.5 in domain
        assert 2.5 in domain
        assert 3.0 not in domain
        assert "x" not in domain

    def test_eq_returns_true_if_same_class_domains_are_equal(self):
        assert not "not a continuous domain" == ContinuousDomain(1.0, 2.6, 0.5)
        assert not ContinuousDomain(1.0, 2.6, 0.5) == ContinuousDomain(1.0, 2.7, 0.5)
        assert ContinuousDomain(1.0, 2.6, 0.5) == ContinuousDomain(1.0, 2.6, 0.5)
        assert ContinuousDomain(1.0, 2.6, 0.5) == ContinuousDomain(1.0, 2.6, 0.6)

    def test_repr_returns_string_representation(self):
        assert repr(ContinuousDomain(1.0, 2.6, 0.5)) == "ContinuousDomain(start=1.0, end=2.6, step=0.5)"


class TestContinuousFuzzySet:
    def test_init_with_invalid_domain_raises_value_error(self):
        with pytest.raises(ValueError):
            ContinuousFuzzySet("x", lambda x: 0.0)
    
    def test_init_with_invalid_membership_function_raises_value_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)

        with pytest.raises(ValueError):
            ContinuousFuzzySet(domain, lambda x: -1.0)

    def test_init_with_singleton_domain(self):
        domain = ContinuousDomain(1.0, 1.0, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: x)

        assert fs.domain == domain
        assert fs.mu(1.0) == 1.0
        assert fs.mu(1.5) == 0.0

    def test_init_with_domain_and_membership_function(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 1.0 - 1/(1 + x))

        assert fs.domain == domain
        assert fs.mu(1.0) == 0.5
        assert fs.mu(1.5) == 0.6
        assert fs.mu(2.7) == 0.0
        assert fs.mu(3.0) == 0.0

    def test_range_returns_membership_degrees_with_set_in_range(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: float(x == 1.5))

        assert list(fs.range) == [0.0, 1.0, 0.0, 0.0]

    def test_iter_returns_pairs_of_elements_and_membership_degrees(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: float(x == 1.5))

        assert list(fs) == [(1.0, 0.0), (1.5, 1.0), (2.0, 0.0), (2.5, 0.0)]

    def test_core_returns_elements_with_membership_degree_1(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: float(x == 1.5))

        assert fs.core == {1.5}

    def test_support_returns_elements_with_positive_membership_degree(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: float(x == 1.5))

        assert fs.support == {1.5}

    def test_cross_over_points_returns_elements_with_membership_degree_0_5(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.5 if x == 1.5 else 0.0)

        assert fs.cross_over_points == {1.5}

    def test_alpha_cut_returns_elements_with_membership_degree_greater_or_equal_to_alpha(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.5 if x == 1.5 else 0.0)

        assert fs.alpha_cut(0.4) == {1.5}
        assert fs.alpha_cut(0.5) == {1.5}
        assert fs.alpha_cut(0.6) == set()

    def test_height_returns_highest_membership_degree(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.5 if x == 1.5 else 0.1)

        assert fs.height == 0.5

    def test_eq_if_other_is_not_a_continuous_fuzzy_set_returns_false(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        assert not fs == "not a continuous fuzzy set"

    def test_eq_if_domains_are_not_equal_returns_false(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.7, 0.5), lambda x: 0.0)

        assert not fs1 == fs2

    def test_eq_if_domains_are_equal_does_pointwise_comparison_with_smaller_step(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.2)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.6), lambda x: 0.2)

        assert fs1 == fs2
    
    def test_select_between_domains_returns_domain_with_smaller_step(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.2)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.4), lambda x: 0.2)

        assert fs1._select_between_domains(fs2) == fs2.domain

    def test_eq_if_membership_degrees_are_not_equal_returns_false(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.4), lambda x: 1.0)

        assert not fs1 == fs2

    def test_ne_if_other_is_not_a_continuous_fuzzy_set_returns_true(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        assert fs != "not a continuous fuzzy set"

    def test_ne_if_domains_are_not_equal_returns_true(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.7, 0.5), lambda x: 0.0)

        assert fs1 != fs2

    def test_ne_if_domains_are_equal_does_pointwise_comparison_with_smaller_step(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.2)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.6), lambda x: 0.2)

        assert not fs1 != fs2

    def test_ne_if_membership_degrees_are_not_equal_returns_true(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.4), lambda x: 1.0)

        assert fs1 != fs2

    def test_lt_when_other_is_not_a_continuous_fuzzy_set_raises_type_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        with pytest.raises(TypeError):
            fs < "not a continuous fuzzy set"

    def test_lt_if_domains_are_not_equal_returns_false(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.7, 0.5), lambda x: 0.0)

        assert not fs1 < fs2

    def test_lt_if_domains_are_equal_does_pointwise_comparison_with_smaller_step(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.2)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.6), lambda x: 0.2)

        assert not fs1 < fs2

    def test_lt_when_lhs_is_a_proper_subset_of_rhs_returns_true(self):
        lhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.1)
        rhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.4), lambda x: 0.2)

        assert lhs < rhs

    def test_gt_when_other_is_not_a_continuous_fuzzy_set_raises_type_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        with pytest.raises(TypeError):
            fs > "not a continuous fuzzy set"

    def test_gt_if_domains_are_not_equal_returns_false(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.7, 0.5), lambda x: 0.0)

        assert not fs1 > fs2

    def test_gt_if_domains_are_equal_does_pointwise_comparison_with_smaller_step(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.2)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.6), lambda x: 0.2)

        assert not fs1 > fs2

    def test_gt_when_lhs_is_a_proper_superset_of_rhs_returns_true(self):
        lhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.2)
        rhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.4), lambda x: 0.1)

        assert lhs > rhs

    def test_le_when_other_is_not_a_continuous_fuzzy_set_raises_type_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        with pytest.raises(TypeError):
            fs <= "not a continuous fuzzy set"

    def test_le_if_domains_are_not_equal_returns_false(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.7, 0.5), lambda x: 0.0)

        assert not fs1 <= fs2

    def test_le_if_domains_are_equal_does_pointwise_comparison_with_smaller_step(self):
        lhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.2)
        rhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.6), lambda x: 0.2)

        assert lhs <= rhs

    def test_le_when_lhs_is_a_subset_of_rhs_returns_true(self):
        lhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.1)
        rhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.4), lambda x: 0.2)

        assert lhs <= rhs

    def test_ge_when_other_is_not_a_continuous_fuzzy_set_raises_type_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        with pytest.raises(TypeError):
            fs >= "not a continuous fuzzy set"

    def test_ge_if_domains_are_not_equal_returns_false(self):
        fs1 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        fs2 = ContinuousFuzzySet(ContinuousDomain(1.0, 2.7, 0.5), lambda x: 0.0)

        assert not fs1 >= fs2

    def test_ge_if_domains_are_equal_does_pointwise_comparison_with_smaller_step(self):
        lhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.2)
        rhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.6), lambda x: 0.2)

        assert lhs >= rhs

    def test_ge_when_lhs_is_a_superset_of_rhs_returns_true(self):
        lhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.5), lambda x: 0.2)
        rhs = ContinuousFuzzySet(ContinuousDomain(1.0, 3.0, 0.4), lambda x: 0.1)

        assert lhs >= rhs

    def test_t_norm_if_other_is_not_a_continuous_fuzzy_set_raises_type_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        with pytest.raises(TypeError):
            fs.t_norm("not a continuous fuzzy set")

    def test_t_norm_if_norm_doesnt_return_membership_degrees_raises_value_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        with pytest.raises(ValueError):
            fs.t_norm(fs, lambda x, y: "not a membership degree")
    
    def test_t_norm_when_domains_are_different_raises_value_error(self):
        lhs = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        rhs = ContinuousFuzzySet(ContinuousDomain(1.0, 2.7, 0.5), lambda x: 0.0)

        with pytest.raises(ValueError):
            lhs.t_norm(rhs)

    def test_t_norm_uses_min_by_default(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        lhs = ContinuousFuzzySet(domain, lambda x: 0.1)
        rhs = ContinuousFuzzySet(domain, lambda x: 0.4)

        assert lhs.t_norm(rhs) == ContinuousFuzzySet(domain, lambda x: 0.1)

    def test_t_norm_with_custom_norm(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        lhs = ContinuousFuzzySet(domain, lambda x: 0.5)
        rhs = ContinuousFuzzySet(domain, lambda x: 0.4)

        assert lhs.t_norm(rhs, lambda x, y: x * y) == ContinuousFuzzySet(domain, lambda x: 0.2)

    def test_s_norm_if_other_is_not_a_continuous_fuzzy_set_raises_type_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        with pytest.raises(TypeError):
            fs.s_norm("not a continuous fuzzy set")

    def test_s_norm_if_norm_doesnt_return_membership_degrees_raises_value_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        with pytest.raises(ValueError):
            fs.s_norm(fs, lambda x, y: "not a membership degree")

    def test_s_norm_when_domains_are_different_raises_value_error(self):
        lhs = ContinuousFuzzySet(ContinuousDomain(1.0, 2.6, 0.5), lambda x: 0.0)
        rhs = ContinuousFuzzySet(ContinuousDomain(1.0, 2.7, 0.5), lambda x: 0.0)

        with pytest.raises(ValueError):
            lhs.s_norm(rhs)

    def test_s_norm_uses_max_by_default(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        lhs = ContinuousFuzzySet(domain, lambda x: 0.2)
        rhs = ContinuousFuzzySet(domain, lambda x: 0.4)

        assert lhs.s_norm(rhs) == ContinuousFuzzySet(domain, lambda x: 0.4)

    def test_s_norm_with_custom_norm(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        lhs = ContinuousFuzzySet(domain, lambda x: 0.5)
        rhs = ContinuousFuzzySet(domain, lambda x: 0.4)

        assert lhs.s_norm(rhs, lambda x, y: min(x + y, 1)) == ContinuousFuzzySet(domain, lambda x: 0.9)

    def test_complement_with_invalid_complement_function_raises_value_error(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.0)

        with pytest.raises(ValueError):
            fs.complement(lambda x: "not a membership degree")

    def test_complement_uses_1_minus_mu_by_default(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.4)

        assert fs.complement() == ContinuousFuzzySet(domain, lambda x: 0.6)

    def test_repr_returns_string_representation_of_the_fuzzy_set(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.4)

        assert repr(fs) == "ContinuousFuzzySet(ContinuousDomain(start=1.0, end=2.6, step=0.5))"

    def test_str_returns_string_representation_of_the_fuzzy_set(self):
        domain = ContinuousDomain(1.0, 2.6, 0.5)
        fs = ContinuousFuzzySet(domain, lambda x: 0.4)

        assert str(fs) == "1.0/0.40 + 1.5/0.40 + 2.0/0.40 + 2.5/0.40"
