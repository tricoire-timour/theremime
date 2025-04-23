class Option:
    """
    A simple option class for a nicer experience dealing with values that can be None.
    """
    def __init__(self, inner=None):
        self.inner = inner

    def map(self, f):
        if self.inner is None:
            return Option(None)
        else:
            return Option(f(self.inner))
        
def todo():
    """
    A simple function to mark a function as TODO.
    """
    raise NotImplementedError("This function is not yet implemented.")