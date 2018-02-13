from .Fit import *
import .Fit as Fit
from socket import gethostname

host = gethostname().upper()

all = Fit.__all__[:]

if "LARMOR" in host:
    from .Motion import populate
    populate()
    from .Larmor import scan
    all += ["populate", "scan"]
elif "ZOOM" in host:
    from .Motion import populate
    populate()
    from .Zoom import scan
    all += ["populate", "scan"]
else:
    from .Instrument import scan, THETA, TWO_THETA
    all += ["scan", "THETA", "TWO_THETA"]

del gethostname
del host

__all__ = all
