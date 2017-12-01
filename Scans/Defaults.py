"""

This module holds the base class for the instrument defaults.
This is an abstract class which will need to be overwritten
for each beamline.  This design was chosen because the
subclass cannot be instantiated unless all of the abstract methods
have been implemented.  This means that we detect mistakes in the
subclass the moment that the Defaults object is created, instead of
in the middle of a user run when a missing method is called.

"""

from abc import ABCMeta, abstractmethod


class Defaults(object):
    """A defaults object to store the correct functions for this instrument"""

    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def measure(title, position, **kwargs):
        """Perform a full measurement.

        Parameters
        ----------
        title
          The title for the run.
        position
          The current position in the scan

        """
        pass

    @staticmethod
    @abstractmethod
    def detector(**kwargs):
        """
        The default function for pulling a count off the detector.
        Takes the standard time settings (e.g. seconds, frames, uamps)
        as keyword arguments.

        """
        pass

    @staticmethod
    @abstractmethod
    def time_estimator(**kwargs):
        """
        The default function for estimating the number of seconds
        needed by a time settings (e.g. seconds, frames, uamps) as
        keyword arguments.
        """
        pass
