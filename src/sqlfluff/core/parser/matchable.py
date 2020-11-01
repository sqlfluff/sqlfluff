"""The definition of a matchable interface."""

from abc import ABC
from typing import Tuple, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from .context import ParseContext
    from .match_result import MatchResult


class Matchable(ABC):
    """A base object defining the matching interface."""

    def is_optional(self) -> bool:
        """Return whether this element is optional."""

    def simple(self, parse_context: "ParseContext") -> Optional[str]:
        """Try to obtain a simple response from the matcher."""

    def match(self, segments: Tuple, parse_context: "ParseContext") -> MatchResult:
        """Match against this matcher."""
