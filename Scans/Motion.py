"""This module holds a single class: Motion.  The Motion class is used
to reify the getters and setters of the various parts of the
instrument.  The theory is that the instrument scientist will create
motion objects for each degree of freedom that the instrument
possesses and that the user can then run scans over these objects.

This module may eventually hold a set of motion objects that are
common to all beamlines.

"""


class Motion(object):
    """A Motion object largely acts like a function to control and
    interrogate a single axis of motion.  When called without a
    parameter, it returns the current position.  Being called with a
    parameter causes the position to update.

    Example:
    Assume that we have some motion object Foo

    >>> Foo()
    7
    >>> Foo(5)
    >>> Foo()
    5

    """
    def __init__(self, getter, setter, title):
        self.getter = getter
        self.setter = setter
        self.title = title

    def __call__(self, x=None):
        if x is None:
            return self.getter()
        return self.setter(x)

    def __iadd__(self, x):
        return self(self()+x)

    def __isub__(self, x):
        return self(self()-x)

    def __imul__(self, x):
        return self(self()*x)
