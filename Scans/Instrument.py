"""Instrument is an example module of an instrument setup.

The motion commands simply adjust a global variable and the
measurement commands just print some information.  It should never be
used in production, but allows us to perform unit tests of the
remaining code without needing a full instrument for the testing
environment.

"""
from __future__ import print_function
import numpy as np
from .Util import make_scan
from .Defaults import Defaults
from .Monoid import Polarisation, MonoidList
from .Scans import estimate
from .Mocks import THETA, TWO_THETA


class MockInstrument(Defaults):
    """
    This class represents a fake instrument that can be
    used for testing purposes.
    """

    @staticmethod
    def detector(**kwargs):
        from time import sleep
        sleep(estimate(**kwargs))
        print("Taking a count at theta=%0.2f and two theta=%0.2f" %
              (THETA(), TWO_THETA()))
        return (1+np.cos(THETA())) * \
            np.sqrt(THETA()) + TWO_THETA() ** 2 + 0.05 * np.random.rand()

    @staticmethod
    def log_file():
        return "mock_scan.dat"

    def __repr__(self):
        return "MockInstrument()"


scan = make_scan(MockInstrument())


def pol_measure(**kwargs):
    """
    Get a single polarisation measurement
    """
    from time import sleep

    results = []
    for freq, width in zip([4, 6, 8, 4], [9, 9, 9, 3]):
        x = THETA()
        pol = np.exp(-((x - 1)/width)**2)*np.cos(freq * (x - 1))

        ups = (1 + pol)*50
        down = (1 - pol)*50
        ups += np.sqrt(ups)*(2*np.random.rand()-1)
        down += np.sqrt(down)*(2*np.random.rand()-1)
        results.append(Polarisation(ups, down))
    sleep(0.01*kwargs["frames"])

    return MonoidList(results)
