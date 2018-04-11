"""Instrument is an example module of an instrument setup.

The motion commands simply adjust a global variable and the
measurement commands just print some information.  It should never be
used in production, but allows us to perform unit tests of the
remaining code without needing a full instrument for the testing
environment.

"""
from __future__ import print_function
import mock
import numpy as np
try:
    # pylint: disable=import-error
    from genie_python import genie as g
except ImportError:
    from .Instrument import THETA
    from time import sleep
    g = mock.Mock()
    g._period = 0
    g._frames = 0
    g.get_period = lambda: g._period
    g.get_frames = lambda: g._frames

    def fake_spectrum(channel, period):
        if channel == 1:
            return {"signal": np.zeros(1000)+1}
        x = np.arange(1000)
        base = np.cos(0.01*(THETA()+1.05)*x)+1
        if period % 2 == 0:
            base = 2 - base
        base *= 100000
        base += np.sqrt(base) * (2 * np.random.rand(1000) - 1)
        base /= x
        sleep(0.1)
        return {"signal": base}

    g.get_spectrum = fake_spectrum
try:
    import LSS.SANSroutines as lm  # pylint: disable=import-error
except ImportError:
    lm = mock.Mock()
from .Util import make_scan, make_estimator
from .Defaults import Defaults
from .Monoid import Polarisation, ListOfMonoids, Average, MonoidList


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
        base = sum(g.get_spectrum(1)["signal"])
        g.abort()
        return Average(temp*100, count=base)

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


def pol_measure(frames, **kwargs):
    """
    Get a single polarisation measurement
    """
    slices = [slice(222, 666), slice(222, 370), slice(370, 518),
              slice(518, 666)]

    i = g.get_period()

    g.change(period=i+1)
    lm.flipper1(1)
    g.waitfor_move()
    gfrm = g.get_frames()
    g.resume()
    g.waitfor(frames=gfrm+frames)
    g.pause()

    lm.flipper1(0)
    g.change(period=i+2)
    gfrm = g.get_frames()
    g.resume()
    g.waitfor(frames=gfrm+frames)
    g.pause()

    pols = [Polarisation.zero() for x in slices]
    for channel in [11, 12]:
        mon1 = g.get_spectrum(1, i+1)
        a1 = g.get_spectrum(channel, i+1)
        mon2 = g.get_spectrum(1, i+2)
        a2 = g.get_spectrum(channel, i+2)
        for idx, slc in enumerate(slices):
            up = Average(
                np.sum(a1["signal"][slc])*100.0,
                np.sum(mon1["signal"][slc])*100.0)
            down = Average(
                np.sum(a2["signal"][slc])*100.0,
                np.sum(mon2["signal"][slc])*100.0)
            pols[idx] += Polarisation(up, down)
    return MonoidList(pols)

scan = make_scan(Larmor())
