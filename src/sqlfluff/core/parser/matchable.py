"""The definition of a matchable interface."""

from abc import ABC


class Matchable(ABC):
    """A base object defining the matching interface."""

    def is_optional(self):
        """Return whether this element is optional."""
        pass

    def simple(self, parse_context):
        """Try to obtain a simple response from the matcher."""
        pass

    def match(self, segments, parse_context):
        """Match against this matcher."""
        pass
