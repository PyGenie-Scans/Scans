import numpy as np
from .Scans import SimpleScan


def get_points(d):
    """This function takes a dictionary of keyword arguments for
    a scan and returns the points at which the scan should be measured."""

    # FIXME:  Ask use for starting position if none is given
    begin = d["begin"]

    if "end" in d:
        end = d["end"]
        if "stride" in d:
            steps = np.ceil((end-begin)/float(d["stride"]))
            return np.linspace(begin, end, steps+1)
        elif "count" in d:
            return np.linspace(begin, end, d["count"])
        elif "gaps" in d:
            return np.linspace(begin, end, d["gaps"]+1)
        elif "step" in d:
            return np.arange(begin, end, d["step"])
    elif "count" in d and ("stride" in d or "step" in d):
        if "stride" in d:
            step = d["stride"]
        else:
            step = d["step"]
        return np.linspace(begin, begin+(d["count"]-1)*step, d["count"])
    elif "gaps" in d and ("stride" in d or "step" in d):
        if "stride" in d:
            step = d["stride"]
        else:
            step = d["step"]
        return np.linspace(begin, begin+d["gaps"]*step, d["gaps"]+1)


def make_scan(defaults):
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
    def estimate(seconds=None, minutes=None, hours=None,
                 uamps=None, frames=None, monitor=None,
                 **kwargs):
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
