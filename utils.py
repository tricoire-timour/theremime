class Option:
    def __init__(self, inner=None):
        self.inner = inner

    def map(self, f):
        if self.inner is None:
            return Option(None)
        else:
            return Option(f(self.inner))