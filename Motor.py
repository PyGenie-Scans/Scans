import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def measure(title, info):
    print(title.format(**info))

def count():
    print("Taking a count at theta=%0.2f and two theta=%0.2f" %
        (instrument["theta"], instrument["two_theta"]))
    return np.sqrt(instrument["theta"])+instrument["two_theta"]**2

def merge_dicts(x, y):
    """Given two dices, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

class Scan(object):
    def __add__(self, b):
        return SumScan(self, b)
    def __mul__(self, b):
        return ProductScan(self, b)
    def __and__(self, b):
        return ParallelScan(self, b)
    def plot(self, measurement=count,
             save=None):
        #FIXME: Support multi-processing plots
        results = [(x,measurement())
                   for x in self]

        if len(results[0][0].items()) == 1:
            xs = [next(iter(x[0].items()))[1] for x in results]
            ys = [x[1] for x in results]
            plt.plot(xs, ys)
        else:
            #FIXME: Handle multidimensional plots
            return
        if save:
            plt.savefig(save)
        else:
            plt.show()
    def measure(self, title):
        for x in self:
            measure(title.format(**instrument), x)

class SimpleScan(Scan):
    def __init__(self, action, values, name):
        self.action = action
        self.values = values
        self.name = name
    def map(self, f):
        return SimpleScan(self.action,
                          map(f, self.values))
    def reverse(self):
        return SimpleScan(self.action, self.values[::-1])
    def __iter__(self):
        for v in self.values:
            self.action(v)
            yield {self.name: v}
    def __len__(self):
        return len(self.values)

class SumScan(Scan):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __iter__(self):
        for x in self.a:
            yield x
        for y in self.b:
            yield y
    def __len__(self):
        return len(self.a) + len(self.b)
    def map(self, f):
        return SumScan(self.a.map(f),
                       self.b.map(f))
    def reverse(self):
        return SumScan(self.b.reverse(),
                       self.a.reverse())

class ProductScan(Scan):
    def __init__(self, a, b, mutate=lambda x, y: y):
        self.a = a
        self.b = b
        self.mutate = mutate
    def __iter__(self):
        for x in self.a:
            curry = lambda y: self.mutate(x, y)
            for y in self.b.map(curry):
                yield merge_dicts(x, y)
    def __len__(self):
        return len(self.a)*len(self.b)
    def map(self, f):
        return ProductScan(self.a.map(f),
                           self.b.map(f),
                           self.mutate)
    def reverse(self):
        return ProductScan(self.a.reverse(),
                           self.b.reverse(),
                           self.mutate)

class ParallelScan(Scan):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __iter__(self):
        for x, y in zip(self.a, self.b):
            yield merge_dicts(x, y)
    def __len__(self):
        return min(len(self.a), len(self.b))
    def map(self, f):
        return ParallelScan(self.a.map(f),
                            self.b.map(f))
    def reverse(self):
        return ParallelScan(self.a.reverse(),
                            self.b.reverse())

instrument = {"theta":0, "two_theta":0}

def cset(**kwargs):
    if "theta" in kwargs:
        return move_theta(kwargs["theta"])
    if "two_theta" in kwargs:
        return move_two_theta(kwargs["two_theta"])

def move_theta(x):
    instrument["theta"] = x

def move_two_theta(x):
    instrument["two_theta"] = x

from math import sin, cos

def get_value():
    return sin(instrument["theta"])*cos(instrument["two_theta"])
#

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
    points = get_points(kwargs)
    def motion(x):
        d = {pv: x}
        cset(**d)
    return SimpleScan(motion, points, pv)
