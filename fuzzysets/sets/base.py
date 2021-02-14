import abc
import operator

from fuzzysets import utils


class Domain(abc.ABC):
    """
    An abstract class for domain of a fuzzy set.
    """
    @abc.abstractmethod
    def __iter__(self):
        """
        :returns: a generator which yields the elements of the domain.
        The order of the elements is the same in each call.
        """
        pass

    @abc.abstractmethod
    def __contains__(self, item):
        pass

    @abc.abstractmethod
    def __eq__(self, other):
        pass

    def __ne__(self, other):
        return not self == other


class FuzzySet(abc.ABC):
    """
    An abstract class for fuzzy set.
    """
    def __init__(self, domain, degrees):
        """
        :param domain: an instance of type Domain.
        :param degrees: a NumPy array of floats in the range [0, 1] -
        the corresponding membership degrees.
        """
        self.__domain = domain
        self.__degrees = degrees
        self.__core = None
        self.__support = None
        self.__cross_over_points = None

    @abc.abstractmethod
    def mu(self, x):
        """
        :param x: an element of the domain.
        :returns: the membership degree of `x`, if it is within the
        domain, otherwise 0.
        """
        pass

    @property
    def domain(self):
        """
        :returns: an instance of type Domain - the set's domain.
        """
        return self.__domain

    @property
    def range(self):
        """
        :returns: a generator of floats in the range [0, 1] - the set's
        range.
        """
        return (i for i in self.__degrees)

    def __iter__(self):
        """
        :returns: an generator of pairs (x, d), where x is an element
        of the domain and d is its membership degree.
        """
        return zip(self.domain, self.range)

    @property
    def core(self):
        """
        :returns: an immutable set of all the elements whose membership
        degree is 1.
        """
        if (self.__core is None):
            self.__core = frozenset(x for x, d in self if (d == 1.))

        return self.__core

    @property
    def support(self):
        """
        :returns: an immutable set of all the elements whose membership
        degree is positive.
        """
        if (self.__support is None):
            self.__support = frozenset(x for x, d in self if (d > 0.))

        return self.__support

    @property
    def cross_over_points(self):
        """
        :returns: an immutable set of all the elements whose membership
        degree is 0.5.
        """
        if (self.__cross_over_points is None):
            self.__cross_over_points = frozenset(
                x for x, d in self if (d == 0.5)
            )

        return self.__cross_over_points

    def alpha_cut(self, alpha):
        """
        :param alpha: a float between 0 and 1.
        :returns: a set of the elements whose membership degree is
        greater or equal to `alpha`.
        """
        alpha = utils.to_float_if_int(alpha)
        utils.validate_alpha(alpha)

        return {x for x, d in self if (d >= alpha)}

    @property
    def height(self):
        """
        :returns: the highest membership degree in the set, 0.0 if it is
        empty.
        """
        return self.__degrees.max(initial=0.0)

    def __eq__(self, other):
        """
        :param other: a value.
        :returns: a boolean value indicating whether `other` is a fuzzy
        set of the same type which has the same domain and membership
        degrees.
        """
        return (isinstance(other, self.__class__) and
                self.__pointwise_comparison(other, operator.eq))

    def __pointwise_comparison(self, other, p, reduction=all):
        return (self.domain == other.domain and
                reduction(p(self.mu(x), other.mu(x))
                          for x in self._select_between_domains(other)))

    def _select_between_domains(self, other):
        """
        This method is invoked whenever two FS's have equal domains and
        one of them is needed, in case it matters which one it is.
        """
        return self.domain

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        """
        Checks whether the fuzzy set is a proper subset of `other`.

        :param other: an instance of the same FuzzySet subclass.
        :returns: a boolean value indicating whether `other` has the
        same domain and its membership degrees are greater or equal
        to the fuzzy set's membership degrees, with at least one of them
        being greater.

        :raises TypeError: if `other` is not an instance of the same
        class.
        """
        self.__class__.__verify_has_same_class(other)
        return (self.__pointwise_comparison(other, operator.le) and
                self.__pointwise_comparison(other, operator.lt, any))

    @classmethod
    def __verify_has_same_class(cls, other):
        if (not isinstance(other, cls)):
            raise TypeError(
                f"Expected an instance of {cls.__name__!r}!"
            )

    def __gt__(self, other):
        """
        Checks whether the fuzzy set is a proper superset of `other`.

        :raises TypeError: if `other` is not an instance of the same
        class.
        """
        self.__class__.__verify_has_same_class(other)
        return other < self

    def __le__(self, other):
        """
        Checks whether the fuzzy set is a subset of `other`.

        :raises TypeError: if `other` is not an instance of the same
        class.
        """
        self.__class__.__verify_has_same_class(other)
        return self.__pointwise_comparison(other, operator.le)

    def __ge__(self, other):
        """
        Checks whether the fuzzy set is a superset of `other`.

        :raises TypeError: if `other` is not an instance of the same
        class.
        """
        self.__class__.__verify_has_same_class(other)
        return other <= self

    def __norm(self, other, norm):
        self.__verify_has_same_class_and_domain(other)

        return self.__class__._from_domain(
            self._select_between_domains(other),
            mu=lambda x: norm(self.mu(x), other.mu(x))
        )

    def __verify_has_same_class_and_domain(self, other):
        self.__class__.__verify_has_same_class(other)

        if (self.domain != other.domain):
            raise ValueError(f"Domains differ: {self.domain} "
                             f"!= {other.domain}")

    @classmethod
    @abc.abstractmethod
    def _from_domain(cls, domain, mu):
        """
        :param domain: an instance of Domain.
        :param mu: a callable that takes elements of `domain` and
        returns floats in the range [0, 1] (not assumed).
        """
        pass

    def t_norm(self, other, norm=min):
        """
        Finds the t-norm of the fuzzy set and `other`.

        :param other: an instance of the same FuzzySet class.
        :param norm: a callable that takes two membership degrees
        (floats between 0 and 1) and returns a membership degree. This
        callable (denoted by I below) must also satisfy the following
        axioms:
         1) boundary condition:
            I(1, 1) = 1; I(0, 0) = 0; I(0, 1) = 0; I(1, 0) = 0
         2) commutativity:
            I(a, b) = I(b, a)
         3) I is monotonic:
            If a' <= a and b' <= b, then I(a', b') <= I(a, b)
        4) associativity
           I(a, I(b, c)) = I(I(a, b), c)
        Defaults to min.
        :returns: an instance of the same FuzzySet class.

        :raises TypeError: if `other` is not an instance of the same
        class.
        :raises ValueError: if the supplied callable does not return
        membership degrees.
        """
        return self.__norm(other, norm)

    def s_norm(self, other, norm=max):
        """
        Finds the s-norm of the fuzzy set and `other`.

        :param other: an instance of the same FuzzySet class.
        :param norm: a callable that takes two membership degrees
        (floats between 0 and 1) and returns a membership degree. This
        callable (denoted by U below) must also satisfy the following
        axioms:
         1) boundary condition:
            U(1, 1) = 1; U(0, 0) = 0; U(0, 1) = 1; U(1, 0) = 1
         2) commutativity:
            U(a, b) = U(b, a)
         3) U is monotonic:
            If a' <= a and b' <= b, then U(a', b') <= U(a, b)
        4) associativity
           U(a, U(b, c)) = U(U(a, b), c)
        Defaults to max.
        :returns: an instance of the same FuzzySet class.

        :raises TypeError: if `other` is not an instance of the same
        class.
        :raises ValueError: if the supplied callable does not return
        membership degrees.
        """
        return self.__norm(other, norm)

    def complement(self, comp=utils.complement):
        """
        Finds the complement of the fuzzy set.

        :param comp: a callable that takes a membership degree (float
        between 0 and 1) and returns a membership degree. This callable
        (denoted by C below) must also satisfy the following axioms:
         1) boundary condition:
            C(0) = 1; C(1) = 0
         2) if a <= b then C(a) >= C(b)
        Defaults to `1 - x`.
        :returns: an instance of the same FuzzySet class.

        :raises ValueError: if the supplied callable does not return
        membership degrees.
        """
        return self.__class__._from_domain(
            self.domain,
            mu=lambda x: comp(self.mu(x))
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self})"

    def __str__(self):
        """
        :returns: a str in the format:
        <x 0>/<d 0> + ... + <x n>/<d n>
        where <x i> and <d i> are the elements of the set and their
        membership degrees, respectively.
        """
        return "+".join(f"{x}/{d}" for x, d in self)


def t_norm(a, b, norm=min):
    """
    Equivalent to `a.t_norm(b, norm)`.
    """
    return a.t_norm(b, norm)


def s_norm(a, b, norm=max):
    """
    Equivalent to `a.s_norm(b, norm)`.
    """
    return a.s_norm(b, norm)


def complement(a, comp=utils.complement):
    """
    Equivalent to `a.complement(comp)`.
    """
    return a.complement(comp)


def alpha_cut(a, alpha):
    """
    Equivalent to `a.alpha_cut(alpha)`.
    """
    return a.alpha_cut(alpha)
