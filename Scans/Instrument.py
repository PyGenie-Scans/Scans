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
from .Defaults import Defaults
from .Monoid import Polarisation, MonoidList

instrument = {"theta": 0, "two_theta": 0}


class MockInstrument(Defaults):
    """
    This class represents a fake instrument that can be
    used for testing purposes.
    """

    @staticmethod
    def measure(title, position, **kwargs):
        print(title.format(**position))

    @staticmethod
    def detector(**kwargs):
        from time import sleep
        sleep(MockInstrument.time_estimator(**kwargs))
        print("Taking a count at theta=%0.2f and two theta=%0.2f" %
              (instrument["theta"], instrument["two_theta"]))
        return np.sqrt(instrument["theta"]) + instrument["two_theta"] ** 2 \
            + 0.05 * np.random.rand()

    @staticmethod
    def time_estimator(**kwargs):
        return make_estimator(1e7)(**kwargs)

    @staticmethod
    def log_file():
        return "mock_scan.dat"

    def __repr__(self):
        return "MockInstrument()"


def set_motion(name):
    """Create a function to update the dictionary of the mock instrument

    Python won't let you update a dict in a lambda."""
    def inner(x):
        """Actually update the dictionary"""
        instrument[name] = x
    return inner


def mock_motion(name):
    """Create a motion object for the mcok instrument"""
    return Motion(lambda: instrument[name], set_motion(name), name)


THETA = mock_motion("theta")
TWO_THETA = mock_motion("two_theta")

scan = make_scan(MockInstrument())


def pol_measure(**kwargs):
    """
    Get a single polarisation measurement
    """
    from time import sleep

    results = []
    for freq, width in zip([4, 6, 8, 4], [9, 9, 9, 3]):
        x = instrument["theta"]
        pol = np.exp(-((x - 1)/width)**2)*np.cos(freq * (x - 1))

        ups = (1 + pol)*50
        down = (1 - pol)*50
        ups += np.sqrt(ups)*(2*np.random.rand()-1)
        down += np.sqrt(down)*(2*np.random.rand()-1)
        results.append(Polarisation(ups, down))
    sleep(0.01*kwargs["frames"])

    return MonoidList(results)
