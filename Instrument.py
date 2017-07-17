import numpy as np

instrument = {"theta": 0, "two_theta": 0}


def measure(title, info):
    """Dummy function to simulate making a measurement"""
    print(title.format(**info))


def count():
    """Dummy function to simulate taking a neutron count"""
    print("Taking a count at theta=%0.2f and two theta=%0.2f" %
          (instrument["theta"], instrument["two_theta"]))
    return np.sqrt(instrument["theta"])+instrument["two_theta"]**2


def move_theta(x):
    """move_theta is a dummy functino to simulate moving the theta motor
in the examples

    """
    instrument["theta"] = x


def move_two_theta(x):
    """move_two_theta is a dummy functino to simulate moving the two_theta
motor in the examples

    """
    instrument["two_theta"] = x


def cset(**kwargs):
    """cset is a dummy substitution of the PyGenie cset code used here for
demonstration purposes"""
    if "theta" in kwargs:
        return move_theta(kwargs["theta"])
    if "two_theta" in kwargs:
        return move_two_theta(kwargs["two_theta"])
