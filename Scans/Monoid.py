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
import numpy as np
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
    def err(self):
        """
        Return the uncertainty of the current value
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

    def err(self):
        return np.sqrt(self.total)/self.count

    def __str__(self):
        return str(self.total/self.count)

    def __repr__(self):
        return "Average({}, count={})".format(self.total, self.count)


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

    def err(self):
        return np.sqrt(self.total)

    def __str__(self):
        return str(self.total)

    def __repr__(self):
        return "Sum({})".format(self.total)


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

    def err(self):
        return np.sqrt(4*self.ups*self.downs/(self.ups+self.downs)**3)

    @staticmethod
    def zero():
        Polarisation(0, 0)

    def __str__(self):
        return str(float(self.ups - self.downs) / float(self.ups + self.downs))

    def __repr__(self):
        return "Polarisation({}, {})".format(self.ups, self.downs)


class MonoidList(Monoid):
    """
    This class turns a collection of Monoids into its own Monoid.
    """
    def __init__(self, values):
        self.values = values

    def __float__(self):
        return [float(x) for x in self.values]

    def zero(self):
        return [x.zero() for x in self.values]

    def __add__(self, y):
        return MonoidList([a + b for a, b in zip(self.values, y)])

    def __iadd__(self, y):
        for value, update in zip(self.values, y):
            value += update
        return self

    def __str__(self):
        return str([str(x) for x in self.values])

    def __repr__(self):
        return "MonoidList({})".format([repr(x) for x in self.values])

    def __iter__(self):
        for x in self.values:
            yield x

    def err(self):
        return [x.err() for x in self.values]

    def min(self):
        """Return the smallest value"""
        lowest = self.values[0]
        for x in self.values[1:]:
            if float(lowest) > float(x):
                lowest = x
        return lowest

    def max(self):
        """Return the largest value"""
        best = self.values[0]
        for x in self.values[1:]:
            if float(best) < float(x):
                best = x
        return best
