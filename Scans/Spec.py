"""The Spec module implements a couple of commond commands from SPEC."""

from . import scan


def ascan(motor, start, end, intervals, time):
    """A reimplementations of ascan from spec

    Example
    -------
    >>> ascan(COARSEZ, -20, 20, 40, -50)

    Scan the CoarseZ motor from position -20 to position 20
    (inclusive) in 1 mm steps.  At each point, take measure for
    50 frames (about five seconds). After the plot, the CoarseZ
    motor will be at position 20.

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
      negative, the measurement frames at each point.

    """
    if time > 0:
        return scan(motor, start=start, stop=end,
                    gaps=intervals).plot(seconds=time)
    return scan(motor, start=start, stop=end,
                gaps=intervals).plot(frames=-time)


def dscan(motor, start, end, intervals, time):
    """A reimplementations of dscan from spec

    Example
    -------
    >>> dscan(COARSEZ, -20, 20, 40, -50)

    Scan the CoarseZ motor from 20 mm below the current position
    to position 20 mm above the current position (inclusive) in 1 mm steps.
    At each point, take measure for 50 frames (about five seconds).
    After the plot, the CoarseZ motor will move back to its original position.

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
      negative, the measurement frames at each point.

    """
    init = motor()
    try:
        if time > 0:
            return scan(motor, before=start, after=end,
                        gaps=intervals).plot(seconds=time)
        return scan(motor, before=start, after=end,
                    gaps=intervals).plot(frames=-time)
    finally:
        motor(init)
