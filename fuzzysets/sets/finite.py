from fuzzysets.sets import base


class FiniteDomain(base.Domain):
    """
    Represents the domain of a finite fuzzy set.
    """
    def __init__(self, items):
        """
        :param items: an iterable of hashable items.
        """
        self.__items = set(items)
        self.__sequenced_items = list(self.__items)

    def __iter__(self):
        return iter(self.__sequenced_items)

    def __contains__(self, item):
        return item in self.__items

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.__items == other.__items)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__items})"
