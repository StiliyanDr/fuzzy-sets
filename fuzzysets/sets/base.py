import abc
import operator
from typing import (
    Any,
    Callable,
    FrozenSet,
    Iterable,
    Iterator,
    Set,
    Tuple,
    Type,
    TypeVar,
)

import numpy as np

from fuzzysets import utils


T = TypeVar("T")

FuzzySetT = TypeVar("FuzzySetT", bound="FuzzySet")

NormFunction = Callable[[float, float], float]


class Domain(abc.ABC):
    """
    An abstract class for domain of a fuzzy set.
    """
    @abc.abstractmethod
    def __iter__(self) -> Iterator[T]:
        """
        :returns: a generator which yields the elements of the domain.
        The order of the elements is the same in each call.
        """
        pass

    @abc.abstractmethod
    def __contains__(self, item: Any) -> bool:
        pass

    @abc.abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    def __ne__(self, other: Any) -> bool:
        return not self == other


class FuzzySet(abc.ABC):
    """
    An abstract class for fuzzy set.
    """
    def __init__(self, domain: Domain, degrees: np.ndarray) -> None:
        """
        :param domain: an instance of type Domain.
        :param degrees: a NumPy array of floats in the range [0, 1] -
        the corresponding membership degrees.

        :raises ValueError: if the degrees are invalid.
        """
        self.__set_degrees(degrees)
        self.__domain = domain
        self.__core = None
        self.__support = None
        self.__cross_over_points = None

    def __set_degrees(self, degrees: np.ndarray) -> None:
        if (utils.is_membership_degree_v(degrees).all()):
            self.__degrees = degrees
        else:
            raise ValueError("Membership degrees must be "
                             "floats between 0 and 1!")

    def _degree_at(self, i: int) -> float:
        return self.__degrees[i]

    @abc.abstractmethod
    def mu(self, x: Any) -> float:
        """
        :param x: an element of the domain.
        :returns: the membership degree of `x`, if it is within the
        domain, otherwise 0.
        """
        pass

    @property
    def domain(self) -> Domain:
        """
        :returns: an instance of type Domain - the set's domain.
        """
        return self.__domain

    @property
    def range(self) -> Iterator[float]:
        """
        :returns: a generator of floats in the range [0, 1] - the set's
        range.
        """
        return (i for i in self.__degrees)

    def __iter__(self) -> Iterator[Tuple[T, float]]:
        """
        :returns: a generator of pairs (x, d), where x is an element
        of the domain and d is its membership degree.
        """
        return zip(self.domain, self.range)

    @property
    def core(self) -> FrozenSet[T]:
        """
        :returns: an immutable set of all the elements whose membership
        degree is 1.
        """
        if (self.__core is None):
            self.__core = frozenset(x for x, d in self if (d == 1.))

        return self.__core

    @property
    def support(self) -> FrozenSet[T]:
        """
        :returns: an immutable set of all the elements whose membership
        degree is positive.
        """
        if (self.__support is None):
            self.__support = frozenset(x for x, d in self if (d > 0.))

        return self.__support

    @property
    def cross_over_points(self) -> FrozenSet[T]:
        """
        :returns: an immutable set of all the elements whose membership
        degree is 0.5.
        """
        if (self.__cross_over_points is None):
            self.__cross_over_points = frozenset(
                x for x, d in self if (d == 0.5)
            )

        return self.__cross_over_points

    def alpha_cut(self, alpha: float) -> Set[T]:
        """
        :param alpha: a float between 0 and 1.
        :returns: a set of the elements whose membership degree is
        greater or equal to `alpha`.
        """
        alpha = utils.to_float_if_int(alpha)
        utils.validate_alpha(alpha)

        return {x for x, d in self if (d >= alpha)}

    @property
    def height(self) -> float:
        """
        :returns: the highest membership degree in the set, 0.0 if it is
        empty.
        """
        return self.__degrees.max(initial=0.0)

    def __eq__(self, other: Any) -> bool:
        """
        :param other: a value.
        :returns: a boolean value indicating whether `other` is a fuzzy
        set of the same type which has the same domain and membership
        degrees.
        """
        return (isinstance(other, self.__class__) and
                self.__pointwise_comparison(other, operator.eq))

    def __pointwise_comparison(
        self: FuzzySetT,
        other: FuzzySetT,
        p: Callable[[float, float], bool],
        reduction: Callable[[Iterable[bool]], bool] = all
    ) -> bool:
        return (self.domain == other.domain and
                reduction(p(self.mu(x), other.mu(x))
                          for x in self._select_between_domains(other)))

    def _select_between_domains(self: FuzzySetT,
                                other: FuzzySetT) -> Domain:
        """
        This method is invoked whenever two FS's have equal domains and
        one of them is needed, in case it matters which one it is.
        """
        return self.domain

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __lt__(self: FuzzySetT, other: FuzzySetT) -> bool:
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
    def __verify_has_same_class(cls, other: Any) -> None:
        if (not isinstance(other, cls)):
            raise TypeError(
                f"Expected an instance of {cls.__name__!r}!"
            )

    def __gt__(self: FuzzySetT, other: FuzzySetT) -> bool:
        """
        Checks whether the fuzzy set is a proper superset of `other`.

        :raises TypeError: if `other` is not an instance of the same
        class.
        """
        self.__class__.__verify_has_same_class(other)
        return other < self

    def __le__(self: FuzzySetT, other: FuzzySetT) -> bool:
        """
        Checks whether the fuzzy set is a subset of `other`.

        :raises TypeError: if `other` is not an instance of the same
        class.
        """
        self.__class__.__verify_has_same_class(other)
        return self.__pointwise_comparison(other, operator.le)

    def __ge__(self: FuzzySetT, other: FuzzySetT) -> bool:
        """
        Checks whether the fuzzy set is a superset of `other`.

        :raises TypeError: if `other` is not an instance of the same
        class.
        """
        self.__class__.__verify_has_same_class(other)
        return other <= self

    def __norm(self: FuzzySetT,
               other: FuzzySetT,
               norm: NormFunction) -> FuzzySetT:
        self.__verify_has_same_class_and_domain(other)

        return self.__class__._from_domain(
            self._select_between_domains(other),
            mu=lambda x: norm(self.mu(x), other.mu(x))
        )

    def __verify_has_same_class_and_domain(
        self: FuzzySetT,
        other: FuzzySetT
    ) -> None:
        self.__class__.__verify_has_same_class(other)

        if (self.domain != other.domain):
            raise ValueError(f"Domains differ: {self.domain} "
                             f"!= {other.domain}")

    @classmethod
    @abc.abstractmethod
    def _from_domain(cls: Type[FuzzySetT],
                     domain: Domain,
                     mu: Callable[[T], float]) -> FuzzySetT:
        """
        :param domain: an instance of Domain.
        :param mu: a callable that takes elements of `domain` and
        returns floats in the range [0, 1] (not assumed).
        """
        pass

    def t_norm(self: FuzzySetT,
               other: FuzzySetT,
               norm: NormFunction = min) -> FuzzySetT:
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

    def s_norm(self: FuzzySetT,
               other: FuzzySetT,
               norm: NormFunction = max) -> FuzzySetT:
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

    def complement(
        self: FuzzySetT,
        comp: Callable[[float], float] = utils.complement
    ) -> FuzzySetT:
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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.domain})"

    def __str__(self) -> str:
        """
        :returns: a str in the format:
        <x 0>/<d 0> + ... + <x n>/<d n>
        where <x i> and <d i> are the elements of the set and their
        membership degrees, respectively.
        """
        return " + ".join(f"{x}/{d:.2f}" for x, d in self)


def t_norm(a: FuzzySetT,
           b: FuzzySetT,
           norm: NormFunction = min) -> FuzzySetT:
    """
    Equivalent to `a.t_norm(b, norm)`.
    """
    return a.t_norm(b, norm)


def s_norm(a: FuzzySetT,
           b: FuzzySetT,
           norm: NormFunction = max) -> FuzzySetT:
    """
    Equivalent to `a.s_norm(b, norm)`.
    """
    return a.s_norm(b, norm)


def complement(
    a: FuzzySetT,
    comp: Callable[[float], float] = utils.complement
) -> FuzzySetT:
    """
    Equivalent to `a.complement(comp)`.
    """
    return a.complement(comp)


def alpha_cut(a: FuzzySet, alpha: float) -> Set[T]:
    """
    Equivalent to `a.alpha_cut(alpha)`.
    """
    return a.alpha_cut(alpha)
