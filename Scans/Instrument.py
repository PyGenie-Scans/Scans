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
from .Detector import dae_periods
from .Monoid import Polarisation, MonoidList
from .Motion import populate
from .Mocks import g


class MockInstrument(Defaults):
    """
    This class represents a fake instrument that can be
    used for testing purposes.
    """

    scan_count = 0

    @staticmethod
    @dae_periods()
    def detector(**kwargs):
        print("Taking a count at theta=%0.2f and two theta=%0.2f" %
              (g.cget("theta")["value"], g.cget("two_theta")["value"]))
        return (1+np.cos(g.cget("theta")["value"])) * \
            np.sqrt(g.cget("theta")["value"]) + \
            g.cget("two_theta")["value"] ** 2 + \
            0.05 * np.random.rand()

    def log_file(self):
        self.scan_count += 1
        return "mock_scan_{:02}.dat".format(self.scan_count)

    def __repr__(self):
        return "MockInstrument()"


populate()
scan = make_scan(MockInstrument())


def pol_measure(**_):
    """
    Get a single polarisation measurement
    """

    results = []
    for freq, width in zip([4, 6, 8, 4], [9, 9, 9, 3]):
        x = g.cget("theta")["value"]
        pol = np.exp(-((x - 1)/width)**2)*np.cos(freq * (x - 1))

        ups = (1 + pol)*50
        down = (1 - pol)*50
        ups += np.sqrt(ups)*(2*np.random.rand()-1)
        down += np.sqrt(down)*(2*np.random.rand()-1)
        results.append(Polarisation(ups, down))

    return MonoidList(results)
