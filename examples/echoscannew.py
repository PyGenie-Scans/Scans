if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np

from Scans import *
from Scans.Monoid import Average, MonoidList, Polarisation
from mock import Mock

abort = Mock()
end = Mock()
pause = Mock()
resume = Mock()
flipper1 = Mock()
lm = Mock()
gen = Mock()
gen._period = 0
gen._frames = 0
gen.get_period = lambda: gen._period
gen.get_frames = lambda: gen._frames

def fake_spectrum(channel, period):
    if channel == 1:
        return {"signal": np.zeros(1000)+1}
    x = np.arange(1000)
    base = np.cos(0.01*(THETA()-1.05)*x)+1
    if period % 2 == 0:
        base = 2 - base
    base *= 100000
    base += np.sqrt(base) * (2 * np.random.rand(1000) - 1)
    base /= x
    pol_measure(frames=20)
    return {"signal": base}

gen.get_spectrum = fake_spectrum

def pol_measure2(frames, **kwargs):
    """
    Get a single polarisation measurement
    """
    slices = [slice(222,666), slice(222, 370), slice(370, 518), slice(518, 666)]

    i = gen.get_period()

    gen.change(period=i+1)
    flipper1(1)
    gen.waitfor_move()
    gfrm = gen.get_frames()
    resume()
    gen.waitfor(frames=gfrm+frames)
    pause()

    flipper1(0)
    gen.change(period=i+2)
    gfrm = gen.get_frames()
    resume()
    gen.waitfor(frames=gfrm+frames)
    pause()

    pols = [Polarisation.zero() for x in slices]
    for channel in [11, 12]:
        mon1 = gen.get_spectrum(1, i+1)
        a1 = gen.get_spectrum(channel, i+1)
        mon2 = gen.get_spectrum(1, i+2)
        a2 = gen.get_spectrum(channel, i+2)
        for idx, slc in enumerate(slices):
            up = Average(
                np.sum(a1["signal"][slc])*100.0,
                np.sum(mon1["signal"][slc])*100.0)
            down = Average(
                np.sum(a2["signal"][slc])*100.0,
                np.sum(mon2["signal"][slc])*100.0)
            pols[idx] += Polarisation(up, down)
    return MonoidList(pols)


def echoscan_axis(axis, startval, endval, npoints, frms, rtitle, save=False):
    """
    Perform an echo scan on a given instrument parameter

    Parameters
    ==========
    axis
      The motor axis to scan, as a string.  You likely was "Echo_Coil_SP"
    startval
      The first value of the scan
    endval
      The last value of the scan
    npoints
      The number of points for the scan. This is one more than the number of steps
    frms
      The number of frames per spin state.  There are ten frames per second
    rtitle
      The title of the run.  This is important when the run is saved
    save
      If True, save the scan in the log.

    Returns
    =======
    The best fit for the center of the echo value.
    """
    abort()

    currents = scan(axis, start=startval, stop=endval, count=npoints).and_back

    flipper1(1)
    lm.setuplarmor_echoscan()
    gen.change(title=rtitle)
    gen.change(nperiods=len(currents)*2)
    gen.begin(paused=1)
    result = currents.fit(PeakFit(0.3), frames=100,
                          detector=pol_measure2)
    if save:
        end()
    else:
        abort()

    return (result["peak"], 0)



print(echoscan_axis(THETA, -3, 2, 26, 1, "Echo Scan"))
