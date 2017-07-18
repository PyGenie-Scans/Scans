"""The Util module contains functions which are useful for the
instrument scientist in defining their beamline.  Nothing in this
module should ever need to be called by the end user.

"""
import numpy as np
from .Scans import SimpleScan


def get_points(x):
    """This function takes a dictionary of keyword arguments for
    a scan and returns the points at which the scan should be measured."""

    # FIXME:  Ask use for starting position if none is given
    begin = x["begin"]

    if "end" in x:
        end = x["end"]
        if "stride" in x:
            steps = np.ceil((end-begin)/float(x["stride"]))
            return np.linspace(begin, end, steps+1)
        elif "count" in x:
            return np.linspace(begin, end, x["count"])
        elif "gaps" in x:
            return np.linspace(begin, end, x["gaps"]+1)
        elif "step" in x:
            return np.arange(begin, end, x["step"])
    elif "count" in x and ("stride" in x or "step" in x):
        if "stride" in x:
            step = x["stride"]
        else:
            step = x["step"]
        return np.linspace(begin, begin+(x["count"]-1)*step, x["count"])
    elif "gaps" in x and ("stride" in x or "step" in x):
        if "stride" in x:
            step = x["stride"]
        else:
            step = x["step"]
        return np.linspace(begin, begin+x["gaps"]*step, x["gaps"]+1)


def make_scan(defaults):
    """This is a helper function to be used by the instrument scientist.
    Given a defaults class that holds the default values needed for
    scans, it creates a scan function that uses those default values.

    The basic usage is that the instrument science will have some
    module for setting up their instrument, which will include

    >>> scan = make_scan(my_defaults)

    The main python environment will then import scan from that module

    """
    def scan(motion, **kwargs):
        """scan is the primary command that users will call to create scans.
        The pv parameter should be a string containing the name of the
        motor to be moved.  The keyword arguments decide the position
        spacing.

        """
        points = get_points(kwargs)

        return SimpleScan(motion, points, defaults)
    return scan


def make_estimator(flux):
    """One of the values in the Defaults class is an estimator that turns
    measurement time requests into seconds.  This can be handled
    automatically for most requests, but the relationship between
    monitor count and time will be different for each instrument.
    This function takes the expected neutron flux per second on the
    monitor and returns a full estimator function.

    """
    def estimate(seconds=None, minutes=None, hours=None,
                 uamps=None, frames=None, monitor=None,
                 **_):
        """Estimate takes a measurement specification and predicts how long
        the measurement will take in seconds.

        """
        if seconds or minutes or hours:
            if not seconds:
                seconds = 0
            if not minutes:
                minutes = 0
            if not hours:
                hours = 0
            return seconds + 60 * minutes + 3600 * hours
        elif frames:
            return frames/10.0
        elif uamps:
            return 90*uamps
        elif monitor:
            return monitor/flux
    return estimate
