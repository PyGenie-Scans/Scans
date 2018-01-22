Guide for Instrument Scientists
*******************************

Introduction
============

The instrument scientist is responsible for writing a single function,
``scan``, which will create the necessary scan objects for the user.
So as to minimize the work required of the instrument scientists, a
set of utility functions exist to remove most of the boilerplate from
this task.  The main point of entry will be the
:meth:`Scans.Util.make_scan` function.  Given a set of defaults
defined by the instrument scientist, the ``make_scan`` function will
create the necessary function. For example, on the Zoom instrument,
the scanning function is simply defined by:

>>> from .Util import make_scan
>>> scan = make_scan(Zoom())

Then, at the user's scripting prompt, all that is needed is a single import

>>> from Scans.Zoom import scan

All that remains for the instrument scientist is to create a subclass
of the :class:`Scans.Defaults.Defaults` to provide ``make_scan`` with
the information that it needs.

Defaults
========

The ``Defaults`` class requires the instrument scientist to implement
four class methods.  If any of the four methods are missing, the class
will immediately throw an error on the first attempt to instantiate
it.  This helps finding errors quickly, instead of in the middle of a
measurement when the missing function is first needed.

measure
-------

The :meth:`Scans.Defaults.Defaults.measure` function should start a
full measurement on the instrument.  It will take two positional
arguments:

:title: A string containing the title of the measurement
:position: The current position of the instrument in the scan

The function may also take additional keyword arguments that were
passed by the user.

This function is deprecated and may be removed in the future.

detector
--------

The :meth:`Scans.Defaults.Defaults.detector` function should return
the result of a single valued measurement.  This will most likely be
either a total number of counts on a detector or transmission monitor.
However, it is possible to provide more complicated measurements and
values, such as taking a flipping measurement and returning a
polarisation.

The value returned by the function should either be a raw count
represented by a number or an instance of the
:class:`Scans.Monoids.Monoid` class.  The Monoid_ class allows for
multiple measurements to be combined correctly.

time_estimator
--------------

The :meth:`Scans.Defaults.Defaults.time_estimator` function calculates
the expected number of seconds for a given measurement delay.  For
example

>>> Zoom.time_estimator(frames=50)
5.0
>>>

As there is a large amount of boilerplate involved in all of the
various parameter options available to ``time_estimator``,
:meth:`Scans.Util.make_estimator` exists to generate more
``time_estimator`` functions.  ``make_estimator`` takes a single
parameter, which is a floating point number representing the neutron
flux per second on the beam monitor.  It returns a function to
calculate the time from the user's parameters.  The monitor count rate
is necessary since that value is instrument dependent, unlike the
length of a minute or the frame frequency.

If no one is using the monitor count for specifying their scans, this
may be removed in a later version and the time_estimator function
could have a default value.  This would allow the ``Defaults`` class
to provide a baseline version of the function.

log_file
--------

The :meth:`Scans.Defaults.Defaults.log_file` returns the path to a
file where the results of the current scan should be stored.  This
function should return a unique value for each scan, to ensure that
previous results are not overwritten.  This can easily be achieved by
appending the current date and time onto the filename.

Monoid
======

Mathematically, a monoid is a collection with the following properties:

1) There exists an operator ⊙, such that, for any two elements, such as x and y, in the collection, then there is another element in the collection whose value would be x ⊙ y.
2) a ⊙ (b ⊙ c) = (a ⊙ b) ⊙ c
3) There exists a zero element Z such that, a ⊙ Z = Z ⊙ a = a

The more intuitive explanation is that a monoid promises use that we
can combine many elements together and get back a single element.  Many common structures form monoids.

Count
  0 is the zero element and addition is the operator
Lists
  The zero element is the empty list and concatenation is the operator
Boolean
  False is the zero element and ``or`` is the operator
Product
  1 is the zero element and multiplication is the operator
Sum
  0 is the zero element and addition is the operator
Unit Monoid
  The collection with only a single element is a monoid.  The zero
  value is that element and the operator just returns its first
  value.  For example, the set {🌲} is a monoid with zero element
  🌲 and a combining operator 🌲 ⊙ 🌲 = 🌲.

As a more complicated example, the collections of monoids is, in and
of itself, a monoid.  The zero element is the unit monoid and the
operator is the cartesian product (basically, just putting the two
values together).  For example, since the Sum and Count are both
monoids, then the combination (Sum, Count) is also a monoid.  We know
that dividing the sum by the count will give us the average.  What the
monoid convention provides, however, is a way to combine two averages
to correctly get the new average.  If I know that one set has an
average of 6 and the other has an average of 4, I don't know what the
average of the combined sets should be.  On the other hand, if I know
that one set has a sum and count of (60, 10) and the other has (160,
40), I know that the combined set has a sum and count of (220, 50) and
the total average is 4.4.

Uncertainties
-------------

Although monoids do not natively contain a notion of uncertainty [#]_,
the monoids used in this project could allow for the calculation of
uncertainty.  Additionally, the initial design decision was that
adding that uncertainty calculation into the monoid provided enough
utility and simplified the value enough to warrant its inclusion.

.. [#] Returning to the Unit monoid example, there is no obvious
       implementation of uncertainty for {🌲}.

Models
======

All models for fitting should deriving from the :class:`Scans.Fit.Fit`
class.  However, this class is likely too generic for common use, as
it expects the instrument scientist to implement their own fitting
procedures.  While this is useful for implementing classes like
:class:`Scans.Fit.PolyFit`, where we can take advantage of our
knowledge of the model to get an exact fitting procedure, most models
will not need this level of control.  For this reason, there is a
subclass :class:`Scans.Fit.CurveFit` which simplifies this work as
much as possible.  Implementing a new model for fitting requires
implementing three functions.

_model
  This function should take a list of x coordinates as its first
  parameter.  The remaining function parameters should be the
  parameters of the model.  This function should return the value of
  the model at those x-coordinates for the model with those parameters

guess
  This function takes two parameters - the lists of x and y
  coordinates for the data set.  The return value is a list of
  approximate values for the correct parameters to the _model
  function.  This rough approximation is used as the starting point
  for the fitting procedure.

readable
  This function operates on a list of parameters values like the kind
  returned by ``guess``.  It returns a dictionary with each parameter
  given a human readable name.  The purpose is to make it easier for
  users to understand the results of the fit.
