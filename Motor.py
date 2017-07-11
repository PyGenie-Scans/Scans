import numpy as np
import matplotlib.pyplot as plt
from Instrument import count, measure, cset

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
    def plot(self, measurement=count,
             save=None):
        """Run over the scan an perform a simple measurement at each position.
The measurement parameter can be used to set what type of measurement
is to be taken.  If the save parameter is set to a file name, then the
plot will be saved in that file."""
        #FIXME: Support multi-processing plots
        results = [(x, measurement())
                   for x in self]

        if len(results[0][0].items()) == 1:
            xs = [next(iter(x[0].items()))[1] for x in results]
            ys = [x[1] for x in results]
            plt.xlabel(next(iter(results[0][0].items()))[0])
            plt.plot(xs, ys)
        else:
            #FIXME: Handle multidimensional plots
            return
        if save:
            plt.savefig(save)
        else:
            plt.show()
    def measure(self, title):
        """Perform a full measurement at each position indicated by the scan.
        The title parameter gives the run's title and allows for
        values to be interpolated into it.  For instance, the string
        "{theta}" will include the current value of the theta motor if
        it is being iterated over.

        """
        for x in self:
            measure(title, x)

class SimpleScan(Scan):
    """The SimpleScan is a scan along a single axis for a fixed set of values"""
    def __init__(self, action, values, name):
        self.action = action
        self.values = values
        self.name = name
    def map(self, f):
        """The map function returns a modified scan that performs the given
function on all of the original positions to return the new positions.

        """
        return SimpleScan(self.action,
                          map(f, self.values),
                          self.name)
    def reverse(self):
        """Creates a new scan that runs in the opposite direction of this scan"""
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
        """Creates a new scan that runs in the opposite direction of this scan"""
        return SumScan(self.b.reverse(),
                       self.a.reverse())

class ProductScan(Scan):
    """ProductScan performs every possible combination of the positions of
its two constituent scans."""
    def __init__(self, outer, inner):
        self.a = outer
        self.b = inner
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
        """Creates a new scan that runs in the opposite direction of this scan"""
        return ProductScan(self.a.reverse(),
                           self.b.reverse())

class ParallelScan(Scan):
    """ParallelScan runs two scans alongside each other, performing both
sets of position adjustments before each step of the scan."""
    def __init__(self, first, second):
        self.a = first
        self.b = second
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
        """Creates a new scan that runs in the opposite direction of this scan"""
        return ParallelScan(self.a.reverse(),
                            self.b.reverse())

def get_points(d):
    """This function takes a dictionary of keyword arguments for
    a scan and returns the points at which the scan should be measured."""

    #FIXME:  Ask use for starting position if none is given
    begin = d["begin"]

    if "end" in d:
        end = d["end"]
        if "stride" in d:
            steps = np.ceil((end-begin)/float(d["stride"]))
            return np.linspace(begin, end, steps+1)
        elif "count" in d:
            return np.linspace(begin, end, d["count"])
        elif "gaps" in d:
            return np.linspace(begin, end, d["gaps"]+1)
        elif "step" in d:
            return np.arange(begin, end, d["step"])
    elif "count" in d and ("stride" in d or "step" in d):
        if "stride" in d:
            step = d["stride"]
        else:
            step = d["step"]
        return np.linspace(begin, begin+(d["count"]-1)*step, d["count"])
    elif "gaps" in d and ("stride" in d or "step" in d):
        if "stride" in d:
            step = d["stride"]
        else:
            step = d["step"]
        return np.linspace(begin, begin+(d["gaps"]+1)*step, d["gaps"]+1)


def scan(pv, **kwargs):
    """scan is the primary command that users will call to create scans.
The pv parameter should be a string containing the name of the motor
to be moved.  The keyword arguments decide the position spacing."""
    points = get_points(kwargs)
    def motion(x):
        """motion is a helper function to call the appropriate cset function
for the user's chosen motor"""
        d = {pv: x}
        cset(**d)
    return SimpleScan(motion, points, pv)
