"""Scans provides a unified scanning layer for scattering instruments

A wildcard import from this module will provide all of the scanning
utilities a user could be expected to need at a beamline.

"""
from __future__ import absolute_import
# We are doing some trickery with the imports that pylint doesn't
# understand, so we need to turn off some warnings
# pylint: disable=wildcard-import, unused-import, unused-wildcard-import
from socket import gethostname
from .Fit import *  # noqa: F403,F401
from . import Fit

host = gethostname().upper()

_all = Fit.__all__[:]

if "LARMOR" in host:
    from .Motion import populate
    populate()
    from .Larmor import scan
    _all += ["populate", "scan"]
elif "ZOOM" in host:
    from .Motion import populate
    populate()
    from .Zoom import scan
    _all += ["populate", "scan"]
else:
    from .Instrument import scan, THETA, TWO_THETA, pol_measure  # noqa: F403,F401
    _all += ["scan", "THETA", "TWO_THETA", "pol_measure"]
