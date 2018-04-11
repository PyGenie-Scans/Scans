"""This module adds a helper class for detectors."""


class DetectorManager(object):
    def __init__(self, f):
        self._f = f

    def __call__(self, scan):
        self.scan = scan
        return self

    def __enter__(self):
        return self._f

    def __exit__(self, type, value, traceback):
        pass
