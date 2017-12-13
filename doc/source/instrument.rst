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
