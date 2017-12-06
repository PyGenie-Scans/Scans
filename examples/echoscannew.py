if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# import genie_python.genie as gen
# import LSS.SANSroutines as lm
# from ..Scans.Larmor import pol_measure
# from ..Scans.Fit import DampedOscillator
from Scans import Larmor, Fit
from Scans.Instrument import scan, THETA, pol_measure
from Scans.Fit import DampedOscillator


def echoscan_axis(scan, rtitle, frames=100, save=False):
    """
    Perform an echo scan on a given instrument parameter

    Parameters
    ==========
    scan
      The scan object over which to search for echo
    rtitle
      The title of the run.  This is important when the run is saved
    frames
      How many frames to measure for in each spin state at each point.  The
      default is 100.
    save:
      If True, save the scan in the log.
    """
    # gen.abort()
    # gen.change(title=rtitle)
    # lm.setuplarmor_echoscan()
    result = scan.fit(DampedOscillator, frames=frames,
                      detector=pol_measure)
    print("The center is {center}".format(**result))
    return result["center"]

th = scan(THETA, start=-8, stop=5, stride=0.1)
result = echoscan_axis(th.forever() , "Test")
THETA(result["center"])
