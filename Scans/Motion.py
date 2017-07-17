class Motion(object):
    def __init__(self, getter, setter, title):
        self.getter = getter
        self.setter = setter
        self.title = title

    def __call__(self, x=None):
        if x is None:
            return self.getter()
        return self.setter(x)
