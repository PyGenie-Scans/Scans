"""This module contains helper classes for controlling motions on the beamline

There's three levels of depth to this module.  At the simplest level, merely
import and call populate().  This create motion object for every block
currently registered on the instrument.

The next level down is the BlockMotion class, which allows for creating
single objects that correspond to single IBEX blocks.

Finally, at the bottom, BlockMotion derives from the Motion object,
which gives a simple framework for all physical parameters that
can be controlled by an instrument.  Although it is called Motion,
it will also handle temperatures, currents, and other physical properties.
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
        self(self() + x)
        return self

    def __isub__(self, x):
        self(self() - x)
        return self

    def __imul__(self, x):
        self(self() * x)
        return self

    def __repr__(self):
        return "{} is at {}".format(self.title, self())


class BlockMotion(Motion):
    """

    A helper class for creating motion objects from
    Ibex blocks

    Parameters
    ----------

    block
      A string containing the name of the ibex block to control
    """
    def __init__(self, block):
        # pylint: disable=import-error
        from genie_python import genie as g
        Motion.__init__(self,
                        lambda: g.cget(block)["value"],
                        lambda x: g.cset(block, x),
                        block)


def populate():
    """Create Motion objects in the GLOBAL namespace for each
    block registered with IBEX."""
    # pylint: disable=import-error
    from genie_python import genie as g
    for i in g.get_blocks():
        __builtins__[i.upper()] = BlockMotion(i)
