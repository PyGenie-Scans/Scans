"""This module provides a way to access genie that can be mocked out
for test functions."""

from socket import gethostname

# pylint: disable=import-error
if gethostname().upper().startswith("NDX"):
    from genie_python import genie as g
else:
    from .Mocks import g

# pylint: disable=pointless-statement
g
