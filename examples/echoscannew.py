import genie_python.genie as gen
import LSS.SANSroutines as lm
from .Larmor import pol_measure

def echoscan_axis(scan, frames=100, rtitle, save=False):
    lm.setuplarmor_echoscan()
    result = scan.fit(DampedOscillator, frames=100, detector=pol_measure)
    print("The center is {:center}".format(result))
    return result["center"]
