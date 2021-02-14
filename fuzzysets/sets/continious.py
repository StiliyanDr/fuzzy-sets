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
