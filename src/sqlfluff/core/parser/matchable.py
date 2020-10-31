"""The definition of a matchable interface."""

from abc import ABC
from typing import Tuple, TYPE_CHECKING


if TYPE_CHECKING:
    from .context import ParseContext


class Matchable(ABC):
    """A base object defining the matching interface."""

    def is_optional(self):
        """Return whether this element is optional."""
        pass

    def simple(self, parse_context: "ParseContext"):
        """Try to obtain a simple response from the matcher."""
        pass

    def match(self, segments: Tuple, parse_context: "ParseContext"):
        """Match against this matcher."""
        pass
