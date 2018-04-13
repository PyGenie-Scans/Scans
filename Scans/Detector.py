"""This module adds a helper class for detectors."""
try:
    # pylint: disable=import-error
    from genie_python import genie as g
except ImportError:
    from .Mocks import g

class DetectorManager(object):
    def __init__(self, f):
        self._f = f

    def __call__(self, scan, **kwargs):
        self.scan = scan
        return self

    def __enter__(self):
        return self._f

    def __exit__(self, type, value, traceback):
        pass


class DaePeriods(DetectorManager):
    """This helper class aids in making detector managers that perform all
    of their measurements in a single DAE run, instead of constantly
    starting and stoping the DAE."""

    def __init__(self, f, pre_init, period_function=len):
        """Create a new detector manager that runs in a single Dae run

        Parameters
        ----------
        f: Function
          The actual detector command.  Should return a Monoid with the
          measured value.
        pre_init: Function
          Any additional setup that's needed by the detector (e.g. starting
          wiring tables)
        period_function: Function
          A function that takes a scan and calculates the number of periods
          that need to be created.  The default value is to just take the
          length of the scan.
        """
        self._pre_init = pre_init
        self.save = True  # Default value should never be reachable
        DetectorManager.__init__(self, f)

    def __call__(self, scan, save, **kwargs):
        self._pre_init()
        self._save = save
        if "title" in kwargs:
            title = kwargs["title"]
        else:
            title = "Scan"
        g.change_title(title)
        g.change(nperiods=self.period_function(scan))
        g.begin(paused=1)
        return self._f

    def __exit__(self):
        if self._save:
            g.end()
        else:
            g.abort()


def dae_periods(pre_init=lambda: None, period_function=len):
    def inner(f):
        return DaePeriods(f, pre_init, period_function=period_function)
