"""The Fit module holds the Fit class, which defines common parameters
for fitting routines.  It also contains implementations of some common
fits (i.e. Linear and Gaussian).

"""
import numpy as np
from scipy.optimize import curve_fit


class Fit(object):
    """The Fit class combines the common requirements needed for fitting.
    We need to be able to turn a set of data points into a set of
    parameters, get the simulated curve from a set of parameters, and
    extract usable information from those parameters.
    """

    def __init__(self, action, run, fmt, degrees, title):
        self.action = action
        self.run = run
        self.fmt = fmt
        self.degrees = degrees
        self.title = title

    def fit(self, x, y):
        """The fit function takes arrays of independent and depedentend
        variables.  It returns a set of parameters in a format that is
        convenient for this specific object.

        """
        return self.action(x, y)

    def get_y(self, x, fit):
        """get_y takes an array of independent variables and a set of model
        parameters and returns the expected dependent variables for
        those parameters

        """
        return self.run(fit, x)

    def readable(self, fit):
        """Readable turns the implementation specific set of fit parameters
        into a human readable dictionary.

        """
        return self.fmt(fit)


def _gaussian_model(xs, center, sigma, amplitude, background):
    """This is the model for a gaussian with the mean at center, a
       standard deviation of sigma, and a peak of amplitude over a
       base of background.

    """
    return background + amplitude * np.exp(-((xs-center)/sigma/np.sqrt(2))**2)


#: A linear regression
Linear = Fit(lambda x, y: np.polyfit(x, y, 1),
             np.polyval,
             lambda x: {"slope": x[0], "intercept": x[1]},
             2, title="Linear")

#: A gaussian fit
Gaussian = Fit(lambda x, y: curve_fit(_gaussian_model, x, y,
                                      [np.mean(x), np.max(x)-np.min(x),
                                       np.max(y)-np.min(y), np.min(y)])[0],
               lambda cfit, x: _gaussian_model(x, *cfit),
               lambda x: {"center": x[0], "sigma": x[1],
                          "amplitude": x[2], "background": x[3]},
               5, title="Gaussian")
