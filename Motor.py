import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def measure():
    print("Taking a measurement at theta=%0.2f and two theta=%0.2f" %
        (instrument["theta"], instrument["two_theta"]))
    return np.sqrt(instrument["theta"])+instrument["two_theta"]**2

class Scan(object):
    def __add__(self, b):
        return SumScan(self, b)
    def __mul__(self, b):
        return ProductScan(self, b)
    def __and__(self, b):
        return ParallelScan(self, b)
    def plot(self, measurement=measure):
        results = [(x,measurement())
                   for x in self]
        xs = [x[0] for x in results]
        ys = [x[1] for x in results]
        plt.plot(xs, ys)
        plt.savefig("plotter.png")
        # plt.show()

class SimpleScan(Scan):
    def __init__(self, action, values):
        self.action = action
        self.values = values
    def map(self, f):
        return SimpleScan(self.action,
                          map(f, self.values))
    def reverse(self):
        return SimpleScan(self.action, self.values[::-1])
    def __iter__(self):
        for v in self.values:
            self.action(v)
            yield v
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
                yield (x, y)
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
            yield (x, y)
    def __len__(self):
        return min(len(self.a), len(self.b))
    def map(self, f):
        return ParallelScan(self.a.map(f),
                            self.b.map(f))
    def reverse(self):
        return ParallelScan(self.a.reverse(),
                            self.b.reverse())

instrument = {"theta":0, "two_theta":0}

def move_theta(x):
    instrument["theta"] = x

def move_two_theta(x):
    print("Performing extra work for two theta motor")
    instrument["two_theta"] = x

from math import sin, cos

def get_value():
    return sin(instrument["theta"])*cos(instrument["two_theta"])
#

def get_points(d):
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
    return SimpleScan(move_theta, points)
