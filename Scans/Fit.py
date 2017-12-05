"""The Fit module holds the Fit class, which defines common parameters
for fitting routines.  It also contains implementations of some common
fits (i.e. Linear and Gaussian).

"""
from abc import ABCMeta, abstractmethod
import numpy as np


class Fit(object):
    """The Fit class combines the common requirements needed for fitting.
    We need to be able to turn a set of data points into a set of
    parameters, get the simulated curve from a set of parameters, and
    extract usable information from those parameters.
    """

    __metaclass__ = ABCMeta

    def __init__(self, degree, title):
        self.degree = degree
        self._title = title

    @abstractmethod
    def fit(self, x, y):
        """The fit function takes arrays of independent and depedentend
        variables.  It returns a set of parameters in a format that is
        convenient for this specific object.

        """
        return lambda i, j: None

    @abstractmethod
    def get_y(self, x, fit):
        """get_y takes an array of independent variables and a set of model
        parameters and returns the expected dependent variables for
        those parameters

        """
        return lambda i, j: None

    @abstractmethod
    def readable(self, fit):
        """Readable turns the implementation specific set of fit parameters
        into a human readable dictionary.

        """
        return lambda i: {}

    def title(self, *args):
        """
        Give the title of the fit.
        """
        # pylint: disable=unused-argument
        return self._title

    def fit_plot_action(self):
        """
        Create a function to be called in a plotting loop
        to live fit the data

        Returns
        -------
        A function to call in the plotting loop
        """
        def action(x, y, fig):
            """Fit and plot the data within the plotting loop

            Parameters
            ----------
            x : Array of Float
              The x positions measured thus far
            y : Array of Float
              The y positions measured thus far
            fig : matplotlib.figure.Figure
              The figure on which to plot

            Returns
            -------
            line : None or dict
                Either None if the fit is not possible or a dict of the fit
                parameters if the fit was performed

            """
            if len(x) < self.degree:
                return None
            try:
                params = self.fit(x, y)
            except RuntimeError:
                return None
            fity = self.get_y(x, params)
            fig.plot(x, fity, "-",
                     label="{} fit".format(self.title(x, y)))
            fig.legend()
            return params
        return action


class PolyFit(Fit):
    """
    A fitting class for polynomials
    """
    def __init__(self, degree,
                 title=None):
        if title is None:
            title = "Polynomial fit of degree {}".format(degree)
        Fit.__init__(self, degree+1, title)

    def fit(self, x, y):
        return np.polyfit(x, y, self.degree-1)

    def get_y(self, x, fit):
        return np.polyval(fit, x)

    def readable(self, fit):
        if self.degree == 2:
            return {"slope": fit[0], "intercept": fit[1]}
        orders = np.arange(self.degree, 0, -1)
        results = {}
        for key, value in zip(orders, fit):
            results["^{}".format(key)] = value
        return results

    def title(self, x, y):
        # pylint: disable=arguments-differ
        if len(y) < self.degree:
            return self._title
        result = self.fit(x, y)
        xs = ["x^{}".format(i) for i in range(1, len(result))]
        xs = ([""] + xs)[::-1]
        terms = ["{:0.3g}".format(t)+i for i, t in zip(xs, result)]
        return self._title + ": $y = " + " + ".join(terms) + "$"


class GaussianFit(Fit):
    """
    A fitting class for handling gaussian peaks
    """
    def __init__(self):
        Fit.__init__(self, 4, "Gaussian Fit")

    @staticmethod
    def _gaussian_model(xs, cen, sigma, amplitude, background):
        """
        This is the model for a gaussian with the mean at center, a
        standard deviation of sigma, and a peak of amplitude over a base of
        background.

        """
        return background + amplitude * np.exp(-((xs-cen)/sigma/np.sqrt(2))**2)

    def fit(self, x, y):
        from scipy.optimize import curve_fit
        return curve_fit(self._gaussian_model, x, y,
                         [np.mean(x), np.max(x)-np.min(x),
                          np.max(y)-np.min(y), np.min(y)])[0]

    def get_y(self, x, fit):
        return self._gaussian_model(x, *fit)

    def readable(self, fit):
        return {"center": fit[0], "sigma": fit[1],
                "amplitude": fit[2], "background": fit[3]}

    def title(self, x, y):
        # pylint: disable=arguments-differ
        result = self.readable(self.fit(x, y))
        return (self._title + ": " +
                "y={amplitude:.3g}*exp((x-{center:.3g})$^2$" +
                "/{sigma:.3g})+{background:.1g}").format(**result)


#: A linear regression
Linear = PolyFit(1, title="Linear")

#: A gaussian fit
Gaussian = GaussianFit()
