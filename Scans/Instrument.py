import numpy as np
from .Scans import SimpleScan

instrument = {"theta": 0, "two_theta": 0}


def measure(title, info):
    """Dummy function to simulate making a measurement"""
    print(title.format(**info))


def count():
    """Dummy function to simulate taking a neutron count"""
    print("Taking a count at theta=%0.2f and two theta=%0.2f" %
          (instrument["theta"], instrument["two_theta"]))
    return np.sqrt(instrument["theta"])+instrument["two_theta"]**2


class Defaults():
    def __init__(self):
        self.measure = measure
        self.detector = count


def move_theta(x):
    """move_theta is a dummy functino to simulate moving the theta motor
in the examples

    """
    instrument["theta"] = x


def move_two_theta(x):
    """move_two_theta is a dummy functino to simulate moving the two_theta
motor in the examples

    """
    instrument["two_theta"] = x


def cset(**kwargs):
    """cset is a dummy substitution of the PyGenie cset code used here for
demonstration purposes"""
    if "theta" in kwargs:
        return move_theta(kwargs["theta"])
    if "two_theta" in kwargs:
        return move_two_theta(kwargs["two_theta"])


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


def scan(pv, **kwargs):
    """scan is the primary command that users will call to create scans.
The pv parameter should be a string containing the name of the motor
to be moved.  The keyword arguments decide the position spacing."""
    points = get_points(kwargs)

    def motion(x):
        """motion is a helper function to call the appropriate cset function
for the user's chosen motor"""
        d = {pv: x}
        cset(**d)
    return SimpleScan(motion, points, pv, Defaults())
