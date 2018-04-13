"""The Spec module implements a couple of commond commands from SPEC."""

from . import scan


def ascan(motor, start, end, intervals, time):
    """A reimplementations of ascan from spec

    Parameters
    ----------
    motor
      The axis to scan
    start
      The initial position
    stop
      The final position
    intervals
      How many steps to take between the initial and final position
    time
      If positive, the measurement time at each point in seconds.  If
      negative, the measurement time at each point in microamp hours.

    """
    if time > 0:
        return scan(motor, start=start, stop=end,
                    gaps=intervals).plot(seconds=time)
    return scan(motor, start=start, stop=end,
                gaps=intervals).plot(uamps=-time)


def dscan(motor, start, end, intervals, time):
    """A reimplementations of dscan from spec

    Parameters
    ----------
    motor
      The axis to scan
    start
      The initial position as an offset from the current position
    stop
      The final position as an offset from the current position
    intervals
      How many steps to take between the initial and final position
    time
      If positive, the measurement time at each point in seconds.  If
      negative, the measurement time at each point in microamp hours.

    """
    init = motor()
    try:
        if time > 0:
            return scan(motor, before=start, after=end,
                        gaps=intervals).plot(seconds=time)
        return scan(motor, before=start, after=end,
                    gaps=intervals).plot(uamps=-time)
    finally:
        motor(init)
