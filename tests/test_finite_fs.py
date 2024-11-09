import pytest

from fuzzysets.sets.finite import FiniteDomain, FiniteFuzzySet


class TestFiniteDomain:
    def test_ctor(self):
        domain = FiniteDomain([1, 2, 3])

        assert repr(domain) == "FiniteDomain({1, 2, 3})"

    def test_iter(self):
        domain = FiniteDomain([1, 2, 3])

        assert list(domain) == [1, 2, 3]

    def test_contains(self):
        items = [1, 2, 3]
        domain = FiniteDomain(items)

        assert all(item in domain for item in items)
        assert 4 not in domain

    def test_eq(self):
        items = [1, 2, 3]
        domain1 = FiniteDomain(items)
        domain2 = FiniteDomain(items)
        domain3 = FiniteDomain([1, 2, 3, 4])

        assert not (domain1 == items)
        assert domain1 == domain2
        assert domain1 != domain3


class TestFiniteFuzzySet:
    def test_ctor(self):
        items = [1, 2, 3]
        degrees = [0.5, 0.7, 0.9]

        fs = FiniteFuzzySet({
            item: degree
            for item, degree in zip(items, degrees)
        })

        assert fs.domain == FiniteDomain(items)
        assert list(fs.range) == degrees

    def test_ctor_with_invalid_degrees_raises_value_error(self):
        items = [1, 2, 3]
        degrees = [0.5, 1.2, -0.1]

        with pytest.raises(ValueError):
            FiniteFuzzySet({
                item: degree
                for item, degree in zip(items, degrees)
            })

    def test_mu(self):
        items = [1, 2, 3]
        degrees = [0.5, 0.7, 0.9]

        fs = FiniteFuzzySet({
            item: degree
            for item, degree in zip(items, degrees)
        })

        for item, degree in zip(items, degrees):
            assert fs.mu(item) == degree

        assert fs.mu(4) == 0.0

    def test_iter(self):
        items = [1, 2, 3]
        degrees = [0.5, 0.7, 0.9]

        fs = FiniteFuzzySet({
            item: degree
            for item, degree in zip(items, degrees)
        })

        assert list(fs) == list(zip(items, degrees))

    def test_core_when_empty_returns_empty_set(self):
        fs = FiniteFuzzySet({})

        assert fs.core == set()

    def test_core_when_not_empty_returns_items_with_degree_one(self):
        fs = FiniteFuzzySet({1: 0.5, 2: 1.0, 3: 0.0})

        assert fs.core == {2}

    def test_support_when_empty_returns_empty_set(self):
        fs = FiniteFuzzySet({})

        assert fs.support == set()

    def test_support_when_not_empty_returns_items_with_positive_degree(self):
        fs = FiniteFuzzySet({1: 0.5, 2: 0.0, 3: 0.9})

        assert fs.support == {1, 3}

    def test_cross_over_points_when_empty_returns_empty_set(self):
        fs = FiniteFuzzySet({})

        assert fs.cross_over_points == set()

    def test_cross_over_points_when_not_empty_returns_items_with_degree_point_5(self):
        fs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.3})

        assert fs.cross_over_points == {2}

    def test_alpha_cut_with_invalid_alpha_raises_value_error(self):
        fs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.3})

        with pytest.raises(ValueError):
            fs.alpha_cut(1.1)

    def test_alpha_cut_with_of_empty_set_returns_empty_set(self):
        fs = FiniteFuzzySet({})

        assert fs.alpha_cut(0.5) == set()

    def test_alpha_cut(self):
        fs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.3})

        assert fs.alpha_cut(0.5) == {1, 2}
        assert fs.alpha_cut(0.6) == {1}
        assert fs.alpha_cut(0.7) == set()

    def test_height_of_empty_set_is_0(self):
        fs = FiniteFuzzySet({})

        assert fs.height == 0.0

    def test_height_when_not_empty_returns_max_degree(self):
        fs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})

        assert fs.height == 0.9

    def test_eq_when_domains_are_different_returns_false(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9, 4: 0.3})

        assert lhs != rhs

    def test_eq_when_domains_and_degrees_are_the_same_returns_true(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})

        assert lhs == rhs

    def test_eq_when_degrees_are_different_returns_false(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.8})

        assert not lhs == rhs

    def test_ne_when_domains_are_different_returns_true(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9, 4: 0.3})

        assert lhs != rhs

    def test_ne_when_degrees_are_different_returns_true(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.8})

        assert lhs != rhs

    def test_ne_when_domains_and_degrees_are_the_same_returns_false(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})

        assert not lhs != rhs

    def test_lt_when_other_is_not_an_instance_of_the_same_class_raises_type_error(self):
        fs = FiniteFuzzySet({})

        with pytest.raises(TypeError):
            fs < "not a fuzzy set"

    def test_lt_when_other_has_same_domain_and_degrees_returns_false(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})

        assert not lhs < rhs

    def test_lt_when_other_has_greater_degree_for_some_item_returns_true(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.7, 3: 0.9})

        assert lhs < rhs

    def test_gt_when_other_is_not_an_instance_of_the_same_class_raises_type_error(self):
        fs = FiniteFuzzySet({})

        with pytest.raises(TypeError):
            fs > "not a fuzzy set"

    def test_gt_when_other_has_same_domain_and_degrees_returns_false(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})

        assert not lhs > rhs

    def test_gt_when_other_has_smaller_degree_for_some_item_returns_true(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.3, 3: 0.9})

        assert lhs > rhs

    def test_le_when_other_is_not_an_instance_of_the_same_class_raises_type_error(self):
        fs = FiniteFuzzySet({})

        with pytest.raises(TypeError):
            fs <= "not a fuzzy set"

    def test_le_when_other_has_same_domain_and_degrees_returns_true(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})

        assert lhs <= rhs

    def test_le_when_other_has_greater_degree_for_some_item_returns_true(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.7, 3: 0.9})

        assert lhs <= rhs

    def test_ge_when_other_is_not_an_instance_of_the_same_class_raises_type_error(self):
        fs = FiniteFuzzySet({})

        with pytest.raises(TypeError):
            fs >= "not a fuzzy set"

    def test_ge_when_other_has_same_domain_and_degrees_returns_true(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})

        assert lhs >= rhs

    def test_ge_when_other_has_smaller_degree_for_some_item_returns_true(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.3, 3: 0.9})

        assert lhs >= rhs

    def test_t_norm_with_invalid_other_raises_type_error(self):
        fs = FiniteFuzzySet({})

        with pytest.raises(TypeError):
            fs.t_norm("not a fuzzy set")

    def test_t_norm_with_invalid_norm_raises_value_error(self):
        fs = FiniteFuzzySet({"a": 0.5, "b": 0.7})

        with pytest.raises(ValueError):
            fs.t_norm(fs, lambda x, y: "not a membership degree")

    def test_t_norm_with_set_with_different_domain_raises_value_error(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 4: 0.9})

        with pytest.raises(ValueError):
            lhs.t_norm(rhs)

    def test_t_norm_with_empty_set_returns_empty_set(self):
        fs = FiniteFuzzySet({})

        assert fs.t_norm(fs) == FiniteFuzzySet({})

    def test_t_norm_with_non_empty_set_returns_non_empty_set(self):
        lhs = FiniteFuzzySet({1: 0.5, 2: 0.5, 3: 0.8})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.4, 3: 0.9})

        assert lhs.t_norm(rhs) == FiniteFuzzySet({1: 0.5, 2: 0.4, 3: 0.8})

    def test_t_norm_with_custom_norm(self):
        lhs = FiniteFuzzySet({1: 0.5, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.4, 3: 0.5})

        assert lhs.t_norm(rhs, lambda x, y: x * y) == FiniteFuzzySet({1: 0.3, 2: 0.2, 3: 0.45})

    def test_s_norm_with_invalid_other_raises_type_error(self):
        fs = FiniteFuzzySet({})

        with pytest.raises(TypeError):
            fs.s_norm("not a fuzzy set")

    def test_s_norm_with_invalid_norm_raises_value_error(self):
        fs = FiniteFuzzySet({"a": 0.5, "b": 0.7})

        with pytest.raises(ValueError):
            fs.s_norm(fs, lambda x, y: "not a membership degree")

    def test_s_norm_with_set_with_different_domain_raises_value_error(self):
        lhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.5, 4: 0.9})

        with pytest.raises(ValueError):
            lhs.s_norm(rhs)

    def test_s_norm_with_empty_set_returns_empty_set(self):
        fs = FiniteFuzzySet({})

        assert fs.s_norm(fs) == FiniteFuzzySet({})

    def test_s_norm_with_non_empty_set_returns_non_empty_set(self):
        lhs = FiniteFuzzySet({1: 0.5, 2: 0.5, 3: 0.8})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.4, 3: 0.9})

        assert lhs.s_norm(rhs) == FiniteFuzzySet({1: 0.6, 2: 0.5, 3: 0.9})

    def test_s_norm_with_custom_norm(self):
        lhs = FiniteFuzzySet({1: 0.5, 2: 0.5, 3: 0.9})
        rhs = FiniteFuzzySet({1: 0.6, 2: 0.4, 3: 0.5})

        assert lhs.s_norm(rhs, lambda x, y: min(x + y, 1)) == FiniteFuzzySet({1: 1.0, 2: 0.9, 3: 1.0})

    def test_complement_with_invalid_complement_function_raises_value_error(self):
        fs = FiniteFuzzySet({1: 0.5, 2: 0.7})

        with pytest.raises(ValueError):
            fs.complement(lambda x: "not a membership degree")

    def test_complement_with_empty_set_returns_empty_set(self):
        fs = FiniteFuzzySet({})

        assert fs.complement() == FiniteFuzzySet({})

    def test_complement_with_non_empty_set_returns_non_empty_set(self):
        fs = FiniteFuzzySet({1: 0.5, 2: 1.0})

        assert fs.complement() == FiniteFuzzySet({1: 0.5, 2: 0.0})

    def test_repr(self):
        fs = FiniteFuzzySet({1: 0.5, 2: 1.0})

        assert repr(fs) == "FiniteFuzzySet(FiniteDomain({1, 2}))"

    def test_str_formats_degrees_with_two_decimal_places(self):
        fs = FiniteFuzzySet({1: 0.564, 2: 1.0})

        assert str(fs) == "1/0.56 + 2/1.00"
