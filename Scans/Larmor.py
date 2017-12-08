"""Instrument is an example module of an instrument setup.

The motion commands simply adjust a global variable and the
measurement commands just print some information.  It should never be
used in production, but allows us to perform unit tests of the
remaining code without needing a full instrument for the testing
environment.

"""
from __future__ import print_function
try:
    # pylint: disable=import-error
    from genie_python import genie as g
except ImportError:
    g = None
import LSS.SANSroutines as lm  # pylint: disable=import-error
from .Util import make_scan, make_estimator
from .Defaults import Defaults
from .Monoid import Polarisation, ListOfMonoids


class Larmor(Defaults):
    """
    This class represents the default functions for the Larmor instrument.
    """

    @staticmethod
    def measure(title, position, **kwargs):
        g.change_title(title.format(**position))
        g.begin()
        g.waitfor(**kwargs)
        g.end()

    @staticmethod
    def detector(**kwargs):
        g.begin()
        g.waitfor(**kwargs)
        temp = sum(g.get_spectrum(4)["signal"])
        g.abort()
        return temp

    @staticmethod
    def time_estimator(**kwargs):
        return make_estimator(1e6)(**kwargs)

    @staticmethod
    def log_file():
        from datetime import datetime
        now = datetime.now()
        return "U:/larmor_scan_{}_{}_{}_{}_{}_{}.dat".format(
            now.year, now.month, now.day, now.hour, now.minute, now.second)

    def __repr__(self):
        return "Larmor()"


def full_pol(**kwargs):
    """
    Get the up and down counts as a function of the
    time of flight channel
    """
    lm.flipper1(1)
    g.waitfor_move()
    g.begin()
    g.waitfor(**kwargs)
    ups = sum(g.get_spectrum(11, 1)["signal"])
    ups += sum(g.get_spectrum(12, 1)["signal"])
    g.abort()
    lm.flipper1(0)
    g.waitfor_move()
    g.begin()
    g.waitfor(**kwargs)
    down = sum(g.get_spectrum(11, 2)["signal"])
    down += sum(g.get_spectrum(12, 2)["signal"])
    g.abort()
    return (ups, down)


def pol_measure(**kwargs):
    """
    Get the polarisation curves used in locating the spin echos
    """
    ups, downs = full_pol(**kwargs)
    slices = [slice(222, 666), slice(222, 370),
              slice(370, 518), slice(518, 666)]
    ups = [sum(ups[slc]) for slc in slices]
    downs = [sum(downs[slc]) for slc in slices]
    pols = [Polarisation(up, down)
            for up, down in zip(ups, downs)]
    return ListOfMonoids(pols)


scan = make_scan(Larmor())
