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
from matplotlib.pyplot import rcParams
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
        if self.count == 0:
            return float(np.nan)
        return float(self.total) / float(self.count)

    def __add__(self, y):
        if y == 0:
            y = self.zero()
        return Average(
            self.total + y.total,
            self.count + y.count)

    def __iadd__(self, y):
        if y == 0:
            y = self.zero()
        self.total += y.total
        self.count += y.count
        return self

    def __radd__(self, y):
        return self + y

    @staticmethod
    def zero():
        return Average(0, 0)

    def err(self):
        if self.count == 0:
            return np.nan
        return np.sqrt(self.total)/self.count

    def __str__(self):
        if self.count == 0:
            return str(np.nan)
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
        if y == 0:
            y = self.zero()
        self.total += y.total
        return self

    def __add__(self, y):
        if y == 0:
            y = self.zero()
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
        if float(self.ups) + float(self.downs) == 0:
            return 0.0
        return (float(self.ups) - float(self.downs)) / \
            (float(self.ups) + float(self.downs))

    def __iadd__(self, y):
        if y == 0 or y == 0.0:
            y = self.zero()
        self.ups += y.ups
        self.downs += y.downs
        return self

    def __add__(self, y):
        if y == 0:
            y = self.zero()
        return Polarisation(
            self.ups + y.ups,
            self.downs + y.downs)

    def err(self):
        if float(self.ups) + float(self.downs) == 0:
            return 0.0
        return float(self)*np.sqrt(self.downs.err()**2+self.ups.err()**2)*np.sqrt((float(self.ups)-float(self.downs))**-2+(float(self.ups)+float(self.downs))**-2)

    @staticmethod
    def zero():
        return Polarisation(0, 0)

    def __str__(self):
        return str(float(self))

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
        if y == 0:
            y = self.zero()
        return MonoidList([a + b for a, b in zip(self.values, y)])

    def __iadd__(self, y):
        if y == 0:
            y = self.zero()
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


class ListOfMonoids(list):
    """
    A modified list class with special helpers for handlings
    lists of Monoids
    """
    def __init__(self, *args):
        list.__init__(self, *args)
        try:
            self.color_cycle = rcParams["axes.prop_cycle"].by_key()["color"]
        except KeyError:
            self.color_cycle = ["k", "b", "g", "r"]

    def values(self):
        """
        Get the numerical values from the List
        """
        if isinstance(self[0], MonoidList):
            return np.array([[float(v) for v in y] for y in self]).T
        return [float(y) for y in self]

    def err(self):
        """
        Get the uncertainty values from the List
        """
        if isinstance(self[0], MonoidList):
            return np.array([[v for v in y.err()] for y in self]).T
        return [y.err() for y in self]

    def plot(self, axis, xs):
        """
        Make an errorbar plot of a monoid onto an axis
        at a given set of x coordinates
        """
        markers = "osp+xv^<>"
        if isinstance(self[0], MonoidList):
            for y, err, color, marker in zip(self.values(), self.err(),
                                             self.color_cycle, markers):
                axis.errorbar(xs, y, yerr=err, fmt="",
                              color=color, marker=marker,
                              linestyle="None")
        else:
            axis.errorbar(xs, self.values(), yerr=self.err(), fmt="d")

    def max(self):
        """
        Find the largest value in the list, including for uncertainty
        """
        return np.nanmax(np.array(self.values()) +
                         np.array(self.err()))

    def min(self):
        """
        Find the smallest value in the list, including for uncertainty
        """
        return np.nanmin(np.array(self.values()) -
                         np.array(self.err()))
