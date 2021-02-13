from fuzzysets import utils

from numpy.polynomial.polynomial import Polynomial


class TriangularFuzzyNumber:
    """
    Represents a triangular fuzzy number (TFN).

    Each TFN can be uniquely represented as a 3-tuple of real numbers
    (left, peak, right) (l, n and r below) where:
     - peak is the number whose membership degree is 1, that is, the
       number being modeled
     - left (< peak) and right (> peak) determine the fuzzy number's
       membership function:
        mu(x) = 0, x ∈ (-inf, l) U (r, +inf)
        mu(x) = (x - l) / (n - l), l <= x <= n
        mu(x) = (r - x) / (r - n), n <= x <= r
    """
    class AlphaCut:
        """
        Represents the alpha-cut of a TFN, parameterised by alpha:
        [left + alpha * (peak - left), right - alpha (right - peak)] =
        [a + alpha * b, c - alpha * d] = [p, q]
        """
        @classmethod
        def for_tfn(cls, tfn):
            """
            :param tfn: a TriangularFuzzyNumber instance.
            """
            p = Polynomial([tfn.left, tfn.peak - tfn.left])
            q = Polynomial([tfn.right, tfn.peak - tfn.right])

            return cls(p, q)

        def __init__(self, p, q):
            """
            Non-public constructor.
            """
            self.__p = p
            self.__q = q

        def _add(self, other):
            return self.__class__(
                self.__p + other.__p,
                self.__q + other.__q
            )

        def _sub(self, other):
            return self.__class__(
                self.__p - other.__q,
                self.__q - other.__p
            )

        def _mul(self, other):
            return self.__class__(
                self.__p * other.__p,
                self.__q * other.__q
            )

        def _div(self, other):
            return self.__class__(
                self.__p // other.__q,
                self.__q // other.__p
            )

        def for_alpha(self, alpha):
            """
            :param alpha: a float between 0 and 1.
            :returns: a two tuple representing the range
            [a + alpha * b, c - alpha * d]

            :raises ValueError: if `alpha` is not a float in the range
            [0, 1].
            """
            utils.verify_is_numeric(alpha)

            if (0. <= alpha <= 1.):
                return (
                    self.__p(alpha),
                    self.__q(alpha)
                )
            else:
                raise ValueError("Alpha must be between 0 and 1!")

        def __str__(self):
            return f"[{self.__as_str()}]"

        def __as_str(self):
            a, b = self.__p.coef[:2]
            c, d = self.__q.coef[:2]

            return (f"{a} + alpha * {b}, "
                    f"{c} + alpha * {d}")

        def __repr__(self):
            return (f"{self.__class__.__name__}("
                    f"{self.__as_str()})")

    __PEAK_OFFSET = 1.

    @classmethod
    def from_tuple(cls, t):
        """
        Creates a TFN from a 3-tuple in the format (left, peak, right).
        Equivalent to `TNF(t[1], t[0], t[2])`.

        :raises ValueError: if t is not a 3-tuple or the values are not
        numeric (float) or the following condition is not met:
        l < n < r.
        """
        if (isinstance(t, tuple) and len(t) == 3):
            l, n, r = t
            return cls(n, l, r)
        else:
            raise ValueError("Expected a 3-tuple!")

    def __init__(self, n=0., l=None, r=None):
        """
        :param n: a float or int - the peak of the FN. Defaults to 0.0.
        :param l: a float or int - the 'left' component of the FN. If
        omitted or `None`, defaults to `n - PEAK_OFFSET`.
        :param r: a float or int - the 'right' component of the FN. If
        omitted or `None`, defaults to `n + PEAK_OFFSET`.

        :raises ValueError: if the values are not numeric or the
        following condition is not met: l < n < r.
        """
        self.__set_peak(utils.to_float_if_int(n))
        self.__set_left(utils.to_float_if_int(l))
        self.__set_right(utils.to_float_if_int(r))
        self.__alpha_cut = self.__class__.AlphaCut.for_tfn(self)

    def __set_peak(self, n):
        utils.verify_is_numeric(n)
        self.__n = n

    def __set_left(self, left):
        left = utils.default_if_none(
            left,
            self.__n - self.__class__.__PEAK_OFFSET
        )
        utils.verify_is_numeric(left)

        if (left < self.__n):
            self.__l = left
        else:
            raise ValueError(
                f"l ({left}) >= n ({self.__n})!"
            )

    def __set_right(self, right):
        right = utils.default_if_none(
            right,
            self.__n + self.__class__.__PEAK_OFFSET
        )
        utils.verify_is_numeric(right)

        if (self.__n < right):
            self.__r = right
        else:
            raise ValueError(
                f"r ({right}) <= n ({self.__n})!"
            )

    def mu(self, x):
        """
        Computes the membership degree of a real number.

        :param x: a float.
        :returns: a float in the range [0, 1].

        :raises ValueError: if x is not a number.
        """
        x = utils.to_float_if_int(x)
        utils.verify_is_numeric(x)

        return (
            0
            if (x < self.__l or x > self.__r)
            else (x - self.__l) / (self.__n - self.__l)
            if (self.__l <= x <= self.__n)
            else (self.__r - x) / (self.__r - self.__n)
        )

    def __add__(self, other):
        return self.__operation(other, op_name="_add")

    def __operation(self, other, op_name):
        self.__class__.__verify_has_same_type(other)
        op = getattr(self.__alpha_cut, op_name)
        result_alpha_cut = op(other.alpha_cut)
        left, right = result_alpha_cut.for_alpha(0.)
        peak = result_alpha_cut.for_alpha(1.)[0]

        return self.__class__(peak, left, right)

    @classmethod
    def __verify_has_same_type(cls, other):
        if (not isinstance(other, cls)):
            raise TypeError(
               f"Expected an instance of {cls.__name__!r}!"
            )

    def __sub__(self, other):
        return self.__operation(other, op_name="_sub")

    def __mul__(self, other):
        return self.__operation(other, op_name="_mul")

    def __truediv__(self, other):
        return self.__operation(other, op_name="_div")

    def __neg__(self):
        return self.__class__(
            -self.__n,
            -self.__r,
            -self.__l
        )

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                tuple(self) == tuple(other))

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return (isinstance(other, self.__class__) and
                self.__n == other.__n and
                ((self.__l > other.__l and self.__r <= other.__r) or
                 (self.__l >= other.__l and self.__r < other.__r)))

    def __gt__(self, other):
        return (isinstance(other, self.__class__) and
                other < self)

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return (isinstance(other, self.__class__) and
                other <= self)

    def __iter__(self):
        """
        :returns: a generator which yields the `left`, `peak` and
        `right` properties of the TFN, in that order. This makes it
        possible to unpack the number like so:
        `tfn = TriangularFuzzyNumber()`
        `left, peak, right = tfn`
        or to convert it to a tuple:
        `t = tuple(tfn)`
        """
        return iter((self.__l, self.__n, self.__r))

    def __hash__(self):
        return hash(tuple(self))

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"n={self.__n}, "
                f"l={self.__l}, "
                f"r={self.__r})")

    @property
    def alpha_cut(self):
        """
        :returns: an instance of AlphaCut - the alpha cut of the TFN.
        """
        return self.__alpha_cut

    @property
    def peak(self):
        return self.__n

    @property
    def left(self):
        return self.__l

    @property
    def right(self):
        return self.__r
