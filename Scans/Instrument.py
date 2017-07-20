"""Instrument is an example module of an instrument setup.

The motion commands simply adjust a global variable and the
measurement commands just print some information.  It should never be
used in production, but allows us to perform unit tests of the
remaining code without needing a full instrument for the testing
environment.

"""
from __future__ import print_function
import numpy as np
from .Util import make_scan, make_estimator
from .Motion import Motion

instrument = {"theta": 0, "two_theta": 0}

estimator = make_estimator(1e6)


def measure(title, info):
    """Dummy function to simulate making a measurement"""
    print(title.format(**info))


def count(**kwargs):
    """Dummy function to simulate taking a neutron count"""
    from time import sleep
    sleep(estimator(**kwargs))
    print("Taking a count at theta=%0.2f and two theta=%0.2f" %
          (instrument["theta"], instrument["two_theta"]))
    return np.sqrt(instrument["theta"])+instrument["two_theta"]**2


class Defaults(object):
    """A defaults object to store the correct functions for this instrument"""
    def __init__(self):
        self.measure = measure
        self.detector = count
        self.time_estimator = estimator


def move_theta(x):
    """move_theta is a dummy functino to simulate moving the theta motor
in the examples

    """
    instrument["theta"] = x


def move_two_theta(x):
    """move_two_theta is a dummy functino to simulate moving the two_theta
motor in the examples

    """
    instrument["two_theta"] = x


def cset(**kwargs):
    """cset is a dummy substitution of the PyGenie cset code used here for
demonstration purposes"""
    if "theta" in kwargs:
        return move_theta(kwargs["theta"])
    if "two_theta" in kwargs:
        return move_two_theta(kwargs["two_theta"])


def cget(x):
    """cget is a dummy substitution of the PyGenie cget code.
    This has only been encluded for demonstation purposes.
    """
    return instrument[x]


theta = Motion(lambda: cget("theta"),
               lambda x: cset(theta=x),
               "theta")

two_theta = Motion(lambda: cget("two_theta"),
                   lambda x: cset(two_theta=x),
                   "two_theta")

scan = make_scan(Defaults())
