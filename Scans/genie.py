"""This module provides a way to access genie that can be mocked out for test functions."""

from socket import gethostname

if gethostname().upper().startswith("NDX"):
    from genie_python import genie as g
else:
    from .Mocks import g
