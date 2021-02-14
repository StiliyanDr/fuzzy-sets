import numpy as np

from fuzzysets import utils
from fuzzysets.sets import base


_STEP = 0.1


class ContinuousDomain(base.Domain):
    """
    Represents the domain of a continuous fuzzy set - a range of real
    numbers: [start, end].
    """
    def __init__(self, start, end, step=_STEP):
        """
        :param start: a float - the range start.
        :param end: a float - the range end.
        :param step: a float - the step to use when iterating the range,
        for example when the domain object is being iterated. Defaults
        to `STEP`.

        Note that the following conditions must be satisfied:
         - start <= end
         - step > 0

        :raises ValueError: if the above condition is not satisfied.
        """
        values = [start, end, step]

        if (all(isinstance(v, float) for v in values) and
            start <= end and
            step > 0.):
            self.__start = start
            self.__end = end
            self.__step = step
        else:
            raise ValueError("Invalid range!")

    def __iter__(self):
        current = self.__start

        while current <= self.__end:
            yield current
            current += self.__step

    def __contains__(self, item):
        item = utils.to_float_if_int(item)

        return (isinstance(item, float) and
                self.__start <= item <= self.__end)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.__start == other.__start and
                self.__end == other.__end)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"start={self.__start}, "
                f"end={self.__end}, "
                f"step={self.__step})")

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def step(self):
        return self.__step


class ContinuousFuzzySet(base.FuzzySet):
    """
    Represents a fuzzy set whose domain is an interval of real numbers.
    """
    @classmethod
    def _from_domain(cls, domain, mu):
        return cls(domain, mu)

    def __init__(self, domain, mu):
        """
        :param domain: an instance of ContinuousDomain.
        :param mu: a callable that takes elements of `domain` and
        returns floats in the range [0, 1] - the membership function
        of the set.

        :raises ValueError: if the degrees returned by `mu` are invalid.
        """
        self.__class__.__validate_domain(domain)
        index = np.array(domain)
        degrees = mu(index)
        super().__init__(domain, degrees)
        self.__index = index

    @staticmethod
    def __validate_domain(d):
        if (not isinstance(d, ContinuousDomain)):
            raise ValueError("Invalid domain!")

    def mu(self, x):
        """
        :param x: a float - an element of the domain.
        :returns: the membership degree of `x`, if it is within the
        domain, otherwise 0.
        """
        x = utils.to_float_if_int(x)

        return (
            self.__mu_for(x)
            if (isinstance(x, float) and
                self.__index[0] <= x <= self.__index[-1])
            else 0.
        )

    def __mu_for(self, x):
        i = self.__index_for(x)

        return (self._degree_at(i)
                if (self.__index[i] == x)
                else (self._degree_at(i - 1) + self._degree_at(i)) / 2.)

    def __index_for(self, x):
        assert self.__index[0] <= x <= self.__index[-1]
        return np.searchsorted(self.__index, x, side="left")

    def _select_between_domains(self, other):
        """
        This method is invoked whenever two FS's have equal domains and
        one of them is needed, in case it matters which one it is.
        """
        return (self.domain
                if (self.domain.step < other.domain.step)
                else other.domain)
