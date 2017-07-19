import unittest


class TestPlots(unittest.TestCase):
    def test_live_plot(self):
        from Scans.Instrument import scan, theta
        scan(theta, begin=0, end=2, stride=0.6).plot(frames=2)
        self.assertTrue(True)
