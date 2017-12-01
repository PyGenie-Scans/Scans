"""Instrument is an example module of an instrument setup.

The motion commands simply adjust a global variable and the
measurement commands just print some information.  It should never be
used in production, but allows us to perform unit tests of the
remaining code without needing a full instrument for the testing
environment.

"""
from __future__ import print_function
from genie_python import genie as g
import numpy as np
from .Util import make_scan, make_estimator
from .Motion import Motion
from .Defaults import Defaults

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
        return np.sqrt(instrument["theta"])+instrument["two_theta"]**2

    @staticmethod
    def time_estimator(**kwargs):
        return make_estimator(1e6)(**kwargs)

    def __repr__(self):
        return "MockInstrument()"

class BlockMotion(Motion):
    """

    A helper class for creating motion objects from
    Ibex blocks

    Parameters
    ----------

    block
      A string containing the name of the ibex block to control
    """
    def __init__(self, block):
        Motion.__init__(self,
                        lambda: g.cget(block)["value"],
                        lambda x: g.cset(block, x),
                        block)

def populate():
	for i in g.get_blocks():
		__builtins__[i.upper()] = BlockMotion(i)

theta = BlockMotion("theta")
two_theta = BlockMotion("two_theta")

scan = make_scan(MockInstrument())
