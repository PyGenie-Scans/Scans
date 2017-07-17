from __future__ import absolute_import
import numpy as np
import matplotlib.pyplot as plt


def merge_dicts(x, y):
    """Given two dices, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


class Scan(object):
    """The virtual class that represents all controlled scans.  This class
should never be instantiated directly, but rather by one of its
subclasses."""
    def __add__(self, b):
        return SumScan(self, b)

    def __mul__(self, b):
        return ProductScan(self, b)

    def __and__(self, b):
        return ParallelScan(self, b)

    def plot(self, detector=None, save=None, cont=None, **kwargs):
        """Run over the scan an perform a simple measurement at each position.
The measurement parameter can be used to set what type of measurement
is to be taken.  If the save parameter is set to a file name, then the
plot will be saved in that file."""
        if not detector:
            detector = self.defaults.detector

        # FIXME: Support multi-processing plots
        results = [(x, detector(**kwargs))
                   for x in self]

        if len(results[0][0].items()) == 1:
            xs = [next(iter(x[0].items()))[1] for x in results]
            ys = [x[1] for x in results]
            plt.xlabel(next(iter(results[0][0].items()))[0])
            plt.plot(xs, ys)
        else:
            # FIXME: Handle multidimensional plots
            return results
        if save:
            plt.savefig(save)
        elif cont:
            return results
        else:
            plt.show()

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
        if "save" in kwargs and kwargs["save"]:
            save = kwargs["save"]
            kwargs["save"] = None
        else:
            save = None
        results = self.plot(cont=True, **kwargs)
        if fit == "linear":
            x = [next(iter(i[0].items()))[1] for i in results]
            y = [i[1] for i in results]
            # print(x)
            # print(y)
            pfit = np.polyfit(x, y, 1)
            plt.plot(x, np.polyval(pfit, x), "m-", label="{} fit".format(fit))
            plt.legend()
            if save:
                plt.savefig(save)
            else:
                plt.show()
            return pfit

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
            dt = timedelta(0, total)
            print("The run would finish at {}".format(dt+datetime.now()))
        return total


class SimpleScan(Scan):
    """SimpleScan is a scan along a single axis for a fixed set of values"""
    def __init__(self, action, values, defaults):
        self.action = action
        self.values = values
        self.name = action.title
        self.defaults = defaults

    def map(self, f):
        """The map function returns a modified scan that performs the given
function on all of the original positions to return the new positions.

        """
        return SimpleScan(self.action,
                          map(f, self.values),
                          self.name)

    def reverse(self):
        """Create a new scan that runs in the opposite direction"""
        return SimpleScan(self.action, self.values[::-1], self.name)

    def __iter__(self):
        for v in self.values:
            self.action(v)
            yield {self.name: v}

    def __len__(self):
        return len(self.values)


class SumScan(Scan):
    """The SumScan performs two separate scans sequentially"""
    def __init__(self, first, second):
        self.a = first
        self.b = second
        self.defaults = self.a.defaults

    def __iter__(self):
        for x in self.a:
            yield x
        for y in self.b:
            yield y

    def __len__(self):
        return len(self.a) + len(self.b)

    def map(self, f):
        """The map function returns a modified scan that performs the given
function on all of the original positions to return the new positions.

        """
        return SumScan(self.a.map(f),
                       self.b.map(f))

    def reverse(self):
        """Creates a new scan that runs in the opposite direction"""
        return SumScan(self.b.reverse(),
                       self.a.reverse())


class ProductScan(Scan):
    """ProductScan performs every possible combination of the positions of
its two constituent scans."""
    def __init__(self, outer, inner):
        self.a = outer
        self.b = inner
        self.defaults = self.a.defaults

    def __iter__(self):
        for x in self.a:
            for y in self.b:
                yield merge_dicts(x, y)

    def __len__(self):
        return len(self.a)*len(self.b)

    def map(self, f):
        """The map function returns a modified scan that performs the given
function on all of the original positions to return the new positions.

        """
        return ProductScan(self.a.map(f),
                           self.b.map(f))

    def reverse(self):
        """Creates a new scan that runs in the opposite direction"""
        return ProductScan(self.a.reverse(),
                           self.b.reverse())


class ParallelScan(Scan):
    """ParallelScan runs two scans alongside each other, performing both
sets of position adjustments before each step of the scan."""
    def __init__(self, first, second):
        self.a = first
        self.b = second
        self.defaults = self.a.defaults

    def __iter__(self):
        for x, y in zip(self.a, self.b):
            yield merge_dicts(x, y)

    def __len__(self):
        return min(len(self.a), len(self.b))

    def map(self, f):
        """The map function returns a modified scan that performs the given
function on all of the original positions to return the new positions.

        """
        return ParallelScan(self.a.map(f),
                            self.b.map(f))

    def reverse(self):
        """Creates a new scan that runs in the opposite direction"""
        return ParallelScan(self.a.reverse(),
                            self.b.reverse())
