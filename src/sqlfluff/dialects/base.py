"""Defines the base dialect class."""


class Dialect(object):
    """Serves as the basis for runtime resolution of Grammar.

    Args:
        name (:obj:`str`): The name of the dialect, used for lookup.

    """
    def __init__(self, name):
        self._library = {}
        self.name = name

    def segment(self):
        """This is the decorator for elements, it should be called as a method.

        e.g.
        @dialect.segment()
        class SomeSegment(BaseSegment):
            blah blah blah

        """
        def segment_wrap(cls):
            """Wrap a segment and register it against the dialect."""
            n = cls.__name__
            if n in self._library:
                raise ValueError("{0!r} is already registered in {1!r}".format(n, self))
            else:
                self._library[n] = cls
            # Pass it back after registering it
            return cls
        # return the wrapping function
        return segment_wrap

    def add(self, **kwargs):
        """Add a segment to the dialect directly.

        This is the alternative to the decorator route, most useful for segments
        defined using `make`. Segments are passed in as kwargs.

        e.g.
        dialect.add(SomeSegment=KeyworkSegment.make(blah, blah, blah))

        Note that mutiple segments can be added in the same call as this method
        will iterate through the kwargs
        """
        for n in kwargs:
            if n in self._library:
                raise ValueError("{0!r} is already registered in {1!r}".format(n, self))
            else:
                self._library[n] = kwargs[n]

    def ref(self, name):
        """Return an object which acts as a late binding reference to the element named."""
        if name in self._library:
            res = self._library[name]
            if res:
                return res
            else:
                raise ValueError(
                    "Unexpected Null response while fetching {0!r} from {1}".format(
                        name, self.name))
        else:
            raise RuntimeError(
                "Grammar refers to {0!r} which was not found in the {1} dialect".format(
                    name, self.name))
