"""Instrument is an example module of an instrument setup.

The motion commands simply adjust a global variable and the
measurement commands just print some information.  It should never be
used in production, but allows us to perform unit tests of the
remaining code without needing a full instrument for the testing
environment.

"""
from __future__ import print_function
import os.path
import numpy as np
try:
    # pylint: disable=import-error
    from genie_python import genie as g
except ImportError:
    from .Mocks import g
try:
    import LSS.SANSroutines as lm  # pylint: disable=import-error
except ImportError:
    from .Mocks import lm
from .Defaults import Defaults
from .Detector import dae_periods
from .Monoid import Polarisation, Average, MonoidList
from .Util import make_scan


class Larmor(Defaults):
    """
    This class represents the default functions for the Larmor instrument.
    """

    @staticmethod
    @dae_periods(lm.setuplarmor_transmission)
    def detector(**kwargs):
        g.resume()
        g.waitfor(**kwargs)
        temp = sum(g.get_spectrum(4)["signal"])
        base = sum(g.get_spectrum(1)["signal"])
        g.pause()
        return Average(temp*100, count=base)

    @staticmethod
    def log_file():
        from datetime import datetime
        now = datetime.now()
        return "larmor_scan_{}_{}_{}_{}_{}_{}.dat".format(
            now.year, now.month, now.day, now.hour, now.minute, now.second)

    def __repr__(self):
        return "Larmor()"


def get_user_dir():
    """Move to the current user directory"""
    base = r"U:/Users/"
    dirs = [[os.path.join(base,x,d)
             for d in os.listdir(os.path.join(base,x))
             if os.path.isdir(os.path.join(base,x,d))]
            for x in os.listdir(base)
            if os.path.isdir(os.path.join(base,x))]
    dirs = [x for x in dirs if x]
    result = max([max(x, key=os.path.getmtime)
                  for x in dirs],
                 key=os.path.getmtime)
    print("Setting path to {}".format(result))
    os.chdir(result)


get_user_dir()


@dae_periods(lm.setuplarmor_echoscan, lambda x: 2*len(x))
def pol_measure(**kwargs):
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
    g.waitfor(frames=gfrm+kwargs["frames"])
    g.pause()

    lm.flipper1(0)
    g.change(period=i+2)
    gfrm = g.get_frames()
    g.resume()
    g.waitfor(frames=gfrm+kwargs["frames"])
    g.pause()

    pols = [Polarisation.zero() for _ in slices]
    for channel in [11, 12]:
        mon1 = g.get_spectrum(1, i+1)
        spec1 = g.get_spectrum(channel, i+1)
        mon2 = g.get_spectrum(1, i+2)
        spec2 = g.get_spectrum(channel, i+2)
        for idx, slc in enumerate(slices):
            ups = Average(
                np.sum(spec1["signal"][slc])*100.0,
                np.sum(mon1["signal"])*100.0)
            down = Average(
                np.sum(spec2["signal"][slc])*100.0,
                np.sum(mon2["signal"])*100.0)
            pols[idx] += Polarisation(ups, down)
    return MonoidList(pols)


@dae_periods()
def fast_pol_measure(**kwargs):
    """
    Get a single polarisation measurement
    """
    slices = [slice(222, 666), slice(222, 370), slice(370, 518),
              slice(518, 666)]

    i = g.get_period()

    g.change(period=i+1)
    g.waitfor_move()
    gfrm = g.get_frames()
    g.resume()
    g.waitfor(frames=gfrm+kwargs["frames"])
    g.pause()

    pols = [Average.zero() for _ in slices]
    for channel in [11, 12]:
        mon1 = g.get_spectrum(1, i+1)
        spec1 = g.get_spectrum(channel, i+1)
        for idx, slc in enumerate(slices):
            ups = Average(
                np.sum(spec1["signal"][slc])*100.0,
                np.sum(mon1["signal"])*100.0)
            pols[idx] += ups
    return MonoidList(pols)


scan = make_scan(Larmor())
