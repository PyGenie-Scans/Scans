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

    def __repr__(self):
        return "Larmor()"

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

#theta = BlockMotion("theta")
#two_theta = BlockMotion("two_theta")

scan = make_scan(Larmor())
