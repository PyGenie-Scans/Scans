if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from Scans import *


currents = scan(THETA, start=-3, stop=2, stride=0.2).and_back.forever
result = currents.fit(PeakFit(0.3), frames=100,
                      detector=pol_measure)
print(result)
THETA(result["peak"])
print(THETA)
