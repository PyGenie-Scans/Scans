"""The Scans module holds the base classes for scan objects.  These
objects reify the steps an instrument takes in a scan and allow us to
have single place where all of the various scanning methods can be
condensed.

The only export of this module that should ever need to be directly
accessed by other modules is SimpleScan.  Everything else should be
treated as private.

"""
from __future__ import absolute_import, print_function
from abc import ABCMeta, abstractmethod
from collections import Iterable
import numpy as np
from six import add_metaclass
from .Monoid import MonoidList

try:
    # pylint: disable=import-error
    from genie_python import genie as g
except ImportError:
    # We must be in a test environment
    g = None
from .multiplot import NBPlot
from .Monoid import Average


def merge_dicts(x, y):
    """Given two dices, merge them into a new dict as a shallow copy."""
    final = x.copy()
    final.update(y)
    return final


def _plot_range(array):
    if not array:
        return (-0.05, 0.05)
    # array = [float(x) for x in array]
    if isinstance(array[0], MonoidList):
        low = float(array[0].min())
        high = float(array[0].max())
        for x in array[1:]:
            if float(x.min()) < low:
                low = float(x.min())
            if float(x.max()) > high:
                high = float(x.max())
        diff = high-low
    else:
        low = min(array)
        high = max(array)
        diff = max(array) - min(array)
    return (low - 0.05 * diff,
            high + 0.05 * diff)


@add_metaclass(ABCMeta)
class Scan(object):
    """The virtual class that represents all controlled scans.  This class
    should never be instantiated directly, but rather by one of its
    subclasses."""

    defaults = None

    @abstractmethod
    def map(self, func):
        """The map function returns a modified scan that performs the given
        function on all of the original positions to return the new positions.
        """
        pass

    @abstractmethod
    def reverse(self):
        """Create a new scan that runs in the opposite direction"""
        pass

    def __iter__(self):
        pass

    def __add__(self, x):
        return SumScan(self, x)

    def __mul__(self, x):
        return ProductScan(self, x)

    def __and__(self, x):
        return ParallelScan(self, x)

    def forever(self):
        """
        Create a scan that will cycle until stopped by the user.
        """
        return ForeverScan(self)

    def plot(self, detector=None, save=None,
             action=None, **kwargs):
        """Run over the scan an perform a simple measurement at each position.
        The measurement parameter can be used to set what type of measurement
        is to be taken.  If the save parameter is set to a file name, then the
        plot will be saved in that file."""
        import warnings
        warnings.simplefilter("ignore", UserWarning)

        if g and g.get_runstate() != "SETUP":
            raise RuntimeError("Cannot start scan while already in a run!")

        if not detector:
            detector = self.defaults.detector
        axis = NBPlot()

        xs = []
        ys = []
        xlabelled = False

        action_remainder = None
        try:
            with open(self.defaults.log_file(), "w") as logfile:
                for x in self:
                    # FIXME: Handle multidimensional plots
                    (label, position) = next(iter(x.items()))
                    if not xlabelled:
                        axis.set_xlabel(label)
                        xlabelled = True
                    value = detector(**kwargs)
                    if isinstance(value, float):
                        value = Average(value)
                    if position in xs:
                        ys[xs.index(position)] += value
                    else:
                        xs.append(position)
                        ys.append(value)
                    logfile.write("{}\t{}\n".format(xs[-1], str(ys[-1])))
                    axis.clear()
                    rng = _plot_range(xs)
                    axis.set_xlim(rng[0], rng[1])
                    rng = _plot_range(ys)
                    axis.set_ylim(rng[0], rng[1])
                    if isinstance(ys[0], MonoidList):
                        values = np.array([[v for v in y] for y in ys]).T
                        for v in values:
                            axis.plot(xs, v, "d")
                    else:
                        axis.plot(xs, [float(y) for y in ys], "d")
                    if action:
                        action_remainder = action(xs, ys,
                                                  axis)
        except KeyboardInterrupt:
            pass
        if save:
            axis.savefig(save)

        if action_remainder is not None:
            return action_remainder
        return

    def measure(self, title, measure=None, **kwargs):
        """Perform a full measurement at each position indicated by the scan.
        The title parameter gives the run's title and allows for
        values to be interpolated into it.  For instance, the string
        "{theta}" will include the current value of the theta motor if
        it is being iterated over.

        """
        if not measure:
            measure = self.defaults.measure
        for x in self:
            measure(title, x, **kwargs)

    def fit(self, fit, **kwargs):
        """The fit method performs the scan, plotting the points as they are
        taken.  Once the scan is completed, a fit is then plotted over
        the scan and the fitting parameters are returned.

        """

        result = self.plot(return_values=True,
                           action=fit.fit_plot_action(),
                           return_figure=True, **kwargs)

        if isinstance(result[0], Iterable):
            result = np.array(result)
            result = np.mean(result, axis=0)

        return fit.readable(result)

    def calculate(self, time=False, pad=0, **kwargs):
        """Calculate the expected time needed to perform a scan.
        Additionally, print the expected time of completion.

        Beyond accepting the default arguments for setting a
        measurement time (e.g uamps, minutes, frames), this method
        accept two other keywords.  The pad argument is an extra time,
        in seconds, to add to each measurement to account for motor
        movements, file saving, and other such effects.  The quiet
        keyword, if set to true, prevents the printing of the expected
        time of completion.

        """
        from datetime import timedelta, datetime
        est = self.defaults.time_estimator
        total = len(self) * (pad + est(**kwargs))
        if time:
            delta = timedelta(0, total)
            print("The run would finish at {}".format(delta + datetime.now()))
        return total


class SimpleScan(Scan):
    """SimpleScan is a scan along a single axis for a fixed set of values"""
    def __init__(self, action, values, defaults):
        self.action = action
        self.values = values
        self.name = action.title
        self.defaults = defaults

    def map(self, func):
        """The map function returns a modified scan that performs the given
        function on all of the original positions to return the new positions.

        """
        return SimpleScan(self.action,
                          map(func, self.values),
                          self.name)

    def reverse(self):
        """Create a new scan that runs in the opposite direction"""
        return SimpleScan(self.action, self.values[::-1], self.name)

    def __iter__(self):
        for i in self.values:
            self.action(i)
            yield {self.name: i}

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return "SimpleScan({}, {}, {})".format(self.action.title.upper(),
                                               repr(self.values),
                                               repr(self.defaults))


class SumScan(Scan):
    """The SumScan performs two separate scans sequentially"""
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.defaults = self.first.defaults

    def __iter__(self):
        for i in self.first:
            yield i
        for i in self.second:
            yield i

    def __len__(self):
        return len(self.first) + len(self.second)

    def __repr__(self):
        return "{} + {}".format(self.first, self.second)

    def map(self, func):
        """The map function returns a modified scan that performs the given
        function on all of the original positions to return the new positions.

        """
        return SumScan(self.first.map(func),
                       self.second.map(func))

    def reverse(self):
        """Creates a new scan that runs in the opposite direction"""
        return SumScan(self.second.reverse(),
                       self.first.reverse())


class ProductScan(Scan):
    """ProductScan performs every possible combination of the positions of
    its two constituent scans."""
    def __init__(self, outer, inner):
        self.outer = outer
        self.inner = inner
        self.defaults = self.outer.defaults

    def __iter__(self):
        for i in self.outer:
            for j in self.inner:
                yield merge_dicts(i, j)

    def __len__(self):
        return len(self.outer) * len(self.inner)

    def __repr__(self):
        return "{} * {}".format(self.outer, self.inner)

    def map(self, func):
        """The map function returns a modified scan that performs the given
        function on all of the original positions to return the new positions.

        """
        return ProductScan(self.outer.map(func),
                           self.inner.map(func))

    def reverse(self):
        """Creates a new scan that runs in the opposite direction"""
        return ProductScan(self.outer.reverse(),
                           self.inner.reverse())


class ParallelScan(Scan):
    """ParallelScan runs two scans alongside each other, performing both
    sets of position adjustments before each step of the scan."""
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.defaults = self.first.defaults

    def __iter__(self):
        for x, y in zip(self.first, self.second):
            yield merge_dicts(x, y)

    def __repr__(self):
        return "{} & {}".format(self.first, self.second)

    def __len__(self):
        return min(len(self.first), len(self.second))

    def map(self, func):
        """The map function returns a modified scan that performs the given
        function on all of the original positions to return the new positions.

        """
        return ParallelScan(self.first.map(func),
                            self.second.map(func))

    def reverse(self):
        """Creates a new scan that runs in the opposite direction"""
        return ParallelScan(self.first.reverse(),
                            self.second.reverse())


class ForeverScan(Scan):
    """
    ForeverScan repeats the same scan over and over again to improve
    the statistics until the user manually halts the scan.
    """
    def __init__(self, scan):
        self.scan = scan
        self.defaults = scan.defaults

    def __iter__(self):
        while True:
            for x in self.scan:
                yield x

    def __repr__(self):
        return "ForeverScan(" + repr(self.scan) + ")"

    def __len__(self):
        raise RuntimeError("Attempted to get the length of an infinite list")

    def map(self, func):
        return ForeverScan(self.scan.map(func))

    def reverse(self):
        return ForeverScan(self.scan.reverse())
