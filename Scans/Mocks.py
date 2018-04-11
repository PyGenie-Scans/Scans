"""This module exists to make mock version of the beamline

This module creates mocks to handle classes that may not be available
on development or testing machines.
"""

from mock import Mock
import numpy as np
from time import sleep
from .Instrument import THETA

g = Mock()
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

lm = Mock()
