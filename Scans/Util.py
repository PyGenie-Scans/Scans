"""The Util module contains functions which are useful for the
instrument scientist in defining their beamline.  Nothing in this
module should ever need to be called by the end user.

"""
import numpy as np
from .Scans import SimpleScan


def get_points(
        current,
        start=None, stop=None,
        step=None, stride=None,
        count=None, gaps=None,
        before=None, after=None,
        exact=None,
        **_):
    """This function takes a dictionary of keyword arguments for
    a scan and returns the points at which the scan should be measured.


    This function provides many ways to define a scan

    - start point, stop point, and number of points
    - start point, stop point, and spacing
    - start point, spacing, and number of points

    Parameters
    ----------
    current : float
      The present position of the motor.  This is needed to relative scans.
    start : float
      The absolute first position in the scan.  This is a valid start point.
    stop : float
      The absolute final position in the scan.  This is a valid stop point.
    before : float
      The relative first position in the scan.  If the motor is currently
      at 3 and ``before`` is set to -5, then the first scan point will be -2.
      This is a valid start point.
    after : float
      The relative final position in the scan.  If the motor is currently
      at 3 and ``before`` is set to 5, then the last scan point will be 8.
      This is a valid stop point.
    step : float
      The fixed distance between points.  If the distance between the
      beginning and end aren't an exact multiple of this step size,
      then the end point will not be included.  This is a valid spacing.
    stride : float
      The approximate distance between points.  In order to ensure that
      the ``start`` and ``stop`` points are included in the scan, a finer
      resolution scan will be called for if the stride is not an exact
      multiple of the distance. This is a valid spacing.
    count : float
      The number of measurements to perform.  A scan with a ``count`` of 2
      would measure at only the beginning and the end.  This is a valid
      number of points.
    gaps : float
      The number of steps that the motor will take.  A scan with a ``gaps``
      of 1 would measure at only the beginning and the end.  This is a
      valid number of points.
    exact : list of float
      An array of the exact values to visit.  This allows taking scans
      at any arbitrary set of points.  This is also necessary for
      scans that don't use numerical values, such as the sample changer.

    Returns
    -------
    Array of Floats
      The positions for the scan.

    Raises
    ------
    RuntimeError
      If the supplied parameters cannot be combined into a coherent scan.


    """

    if exact is not None:
        return np.array(exact)
    if gaps:
        count = gaps + 1
    if before is not None:
        start = current + before
    if after is not None:
        stop = current + after

    if start is not None and stop is not None:
        if stride:
            steps = np.ceil((stop - start) / float(stride))
            return np.linspace(start, stop, steps + 1)
        elif count:
            return np.linspace(start, stop, count)
        elif step:
            return np.arange(start, stop, step)
    elif start is not None and count and (stride or step):
        if stride:
            step = stride
        return np.linspace(start, start + (count - 1) * step, count)
    raise RuntimeError("Unable to build a scan with that set of options.")


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
        points = get_points(motion(), **kwargs)

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
            return frames / 10.0
        elif uamps:
            return 90 * uamps
        elif monitor:
            return monitor / flux
        return 0
    return estimate
