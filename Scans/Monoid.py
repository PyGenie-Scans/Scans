"""
The module defines a series of Monoid classes for handlings
measurements.  For the unfamiliar, a monoid is just a type that A) has
a zero value and B) can be combined with other values of the same type
to produce new monoids.  For example, Sum is a monoid because Sum(a) +
Sum(b) = Sum(a+b) and Sum(a) + Sum(0) = Sum(a).

Putting the incoming data into amonoid makes it easier to get the
information out of a combined measuremnts.
"""

from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class Monoid(object):
    """
    The Monoid base class enforces the two laws: There must be a zero
    operation and a combining function (add).
    """
    @staticmethod
    @abstractmethod
    def zero():
        """
        The zero element of the monoid.  This element obeys the law that

        x + x.zero() == x
        """
        pass

    @abstractmethod
    def __add__(self, x):
        pass

    @abstractmethod
    def __iadd__(self, x):
        pass


class Average(Monoid):
    """
    This monoid calculates the average of its values.
    """
    def __init__(self, x, count=1):
        self.total = x
        self.count = count

    def __float__(self):
        return float(self.total) / float(self.count)

    def __add__(self, y):
        return Average(
            self.total + y.total,
            self.count + y.count)

    def __iadd__(self, y):
        self.total += y.total
        self.count += y.count
        return self

    @staticmethod
    def zero():
        Average(0, 0)


class Sum(Monoid):
    """
    This monoid calculates the sum total of the values presented
    """
    def __init__(self, x):
        self.total = x

    def __float__(self):
        return float(self.total)

    def __iadd__(self, y):
        self.total += y.total
        return self

    def __add__(self, y):
        return Sum(self.total + y.total)

    @staticmethod
    def zero():
        return Sum(0)


class Polarisation(Monoid):
    """
    This monoid calculates the polarisation from the total of all of
    the up and down counts.
    """
    def __init__(self, ups, downs):
        self.ups = ups
        self.downs = downs

    def __float__(self):
        return float(self.ups - self.downs) / float(self.ups + self.downs)

    def __iadd__(self, y):
        self.ups += y.ups
        self.downs += y.downs
        return self

    def __add__(self, y):
        return Polarisation(
            self.ups + y.ups,
            self.downs + y.downs)

    @staticmethod
    def zero():
        Polarisation(0, 0)
