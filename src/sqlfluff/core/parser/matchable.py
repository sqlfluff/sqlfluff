"""The definition of a matchable interface."""

import copy
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING


if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.context import ParseContext
    from sqlfluff.core.parser.match_result import MatchResult


class Matchable(ABC):
    """A base object defining the matching interface."""

    @abstractmethod
    def is_optional(self) -> bool:
        """Return whether this element is optional."""

    @abstractmethod
    def simple(self, parse_context: "ParseContext") -> Optional[List[str]]:
        """Try to obtain a simple response from the matcher."""

    @abstractmethod
    def match(self, segments: tuple, parse_context: "ParseContext") -> "MatchResult":
        """Match against this matcher."""

    def copy(self, **kwargs) -> "Matchable":  # pragma: no cover TODO?
        """Copy this Matchable."""
        return copy.copy(self)
