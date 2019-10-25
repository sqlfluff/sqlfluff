""" Defines the base dialect class """


class Dialect(object):
    """ Serves as the basis for runtime resolution of Grammar """
    def __init__(self, name):
        self._library = {}
        self.name = name

    def segment(self):
        """ This is the decorator for elements, it should be called as a method """
        def segment_wrap(cls):
            """ This inner function is applied to classes to register them """
            n = cls.__name__
            if n in self._library:
                raise ValueError("{0!r} is already registered in {1!r}".format(n, self))
            else:
                self._library[n] = cls
            # Pass it back after registering it
            return cls
        # return the wrapping function
        return segment_wrap

    def ref(self, name):
        """ Return an object which acts as a late binding reference to
        the element named """
        if name in self._library:
            return self._library[name]
        else:
            RuntimeError(
                "Grammar refers to {0!r} which was not found in the {1} dialect".format(
                    name, self.name))
