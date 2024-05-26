from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Mapping,
    Type,
    TypeVar,
)

import numpy as np

from fuzzysets.sets import base


T = TypeVar("T")


class FiniteDomain(base.Domain):
    """
    Represents the domain of a finite fuzzy set.
    """
    def __init__(self, items: Iterable[T]) -> None:
        """
        :param items: an iterable of hashable items.
        """
        self.__items = set(items)
        self.__sequenced_items = list(self.__items)

    def __iter__(self) -> Iterator[T]:
        return iter(self.__sequenced_items)

    def __contains__(self, item: Any) -> bool:
        return item in self.__items

    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, self.__class__) and
                self.__items == other.__items)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__items})"


class FiniteFuzzySet(base.FuzzySet):
    """
    Represents a fuzzy set with a finite domain.
    """
    @classmethod
    def _from_domain(cls: Type[base.FuzzySetT],
                     domain: FiniteDomain,
                     mu: Callable[[T], float]) -> base.FuzzySetT:
        return cls({
            x: mu(x)
            for x in domain
        })

    def __init__(self, elements: Mapping[T, float]) -> None:
        """
        :param elements: an instance of abc.Mapping (like dict) whose
        keys are the set's elements and whose values are their
        corresponding membership degrees (floats between 0 and 1).

        :raises ValueError: if the degrees are invalid.
        """
        domain = FiniteDomain(elements.keys())
        degrees = np.array([elements[x] for x in domain])
        super().__init__(domain, degrees)

        self.__indexes = {
            x: i
            for i, x in enumerate(domain)
        }

    def mu(self, x: T) -> float:
        """
        :param x: an element of the domain.
        :returns: the membership degree of `x`, if it is within the
        domain, otherwise 0.
        """
        index = self.__indexes.get(x)

        return (self._degree_at(index)
                if (index is not None)
                else 0.)
