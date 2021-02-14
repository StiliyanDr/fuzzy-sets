import abc


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
