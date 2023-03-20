"""The definition of a matchable interface."""

import copy
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, TYPE_CHECKING


if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.context import ParseContext
    from sqlfluff.core.parser.match_result import MatchResult


class Matchable(ABC):
    """A base object defining the matching interface."""

    @abstractmethod
    def is_optional(self) -> bool:
        """Return whether this element is optional."""

    @abstractmethod
    def simple(
        self, parse_context: "ParseContext", crumbs: Optional[Tuple[str, ...]] = None
    ) -> Optional[List[str]]:
        """Try to obtain a simple response from the matcher.

        NOTE: the crumbs kwarg is designed to be used by Ref to
        detect recursion.
        """

    @abstractmethod
    def match(self, segments: tuple, parse_context: "ParseContext") -> "MatchResult":
        """Match against this matcher."""

    def copy(self, **kwargs) -> "Matchable":  # pragma: no cover TODO?
        """Copy this Matchable."""
        return copy.copy(self)

    @abstractmethod
    def cache_key(self) -> str:
        """A string to use for cache keying.

        This string should be unique at the parsing stage such that
        if there has already been a match against this key for a set
        of segments, that we can reuse that match.
        """
