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
from .Util import make_scan, make_estimator
from .Defaults import Defaults

instrument = {"theta": 0, "two_theta": 0}


class Larmor(Defaults):
    """
    This class represents a fake instrument that can be
    used for testing purposes.
    """

    @staticmethod
    def measure(title, position, **kwargs):
        g.change_title(title.format(**position))
        g.begin()
        g.waitfor(**kwargs)
        temp = sum(g.get_spectrum(11)["signal"])
        g.abort()
        return temp

    @staticmethod
    def detector(**kwargs):
        g.begin()
        g.waitfor(**kwargs)
        temp = sum(g.get_spectrum(11)["signal"])
        g.abort()
        return temp

    @staticmethod
    def time_estimator(**kwargs):
        return make_estimator(1e6)(**kwargs)

    @staticmethod
    def log_file():
        from datetime import datetime
        now = datetime.now()
        return "/tmp/larmor_scan_{}_{}_{}_{}_{}_{}.dat".format(
            now.year, now.month, now.day, now.hour, now.minute, now.second)

    def __repr__(self):
        return "Larmor()"


scan = make_scan(Larmor())
