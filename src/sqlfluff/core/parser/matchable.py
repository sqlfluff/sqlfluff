"""The definition of a matchable interface."""

from abc import ABC
from typing import List, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from sqlfluff.core.parser.context import ParseContext
    from sqlfluff.core.parser.match_result import MatchResult


class Matchable(ABC):
    """A base object defining the matching interface."""

    def is_optional(self) -> bool:
        """Return whether this element is optional."""

    def simple(self, parse_context: "ParseContext") -> Optional[List[str]]:
        """Try to obtain a simple response from the matcher."""

    def match(self, segments: tuple, parse_context: "ParseContext") -> "MatchResult":
        """Match against this matcher."""
