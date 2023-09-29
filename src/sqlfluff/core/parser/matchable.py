"""The definition of a matchable interface."""

import copy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, FrozenSet, Optional, Sequence, Tuple, TypeVar

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.context import ParseContext
    from sqlfluff.core.parser.match_result import MatchResult
    from sqlfluff.core.parser.segments import BaseSegment


T = TypeVar("T", bound="Matchable")


class Matchable(ABC):
    """A base object defining the matching interface."""

    # Matchables are also not meta unless otherwise defined
    is_meta = False

    @abstractmethod
    def is_optional(self) -> bool:
        """Return whether this element is optional."""

    @abstractmethod
    def simple(
        self, parse_context: "ParseContext", crumbs: Optional[Tuple[str, ...]] = None
    ) -> Optional[Tuple[FrozenSet[str], FrozenSet[str]]]:
        """Try to obtain a simple response from the matcher.

        Returns:
            None - if not simple.
            Tuple of two sets of strings if simple. The first is a set of
                uppercase raw strings which would match. The second is a set
                of segment types that would match.

        NOTE: the crumbs kwarg is designed to be used by Ref to
        detect recursion.
        """

    @abstractmethod
    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> "MatchResult":
        """Match against this matcher."""

    def copy(self: T, **kwargs: Any) -> T:  # pragma: no cover
        """Copy this Matchable.

        Matchable objects are usually copied during dialect inheritance.
        One dialect might make a copy (usually with some modifications)
        to a dialect element of a parent dialect which it can then use
        itself. This provides a little more modularity in dialect definition.

        NOTE: This method on the base class is not usually used, as the
        base matchable doesn't have any options for customisation. It is
        more frequently used by grammar objects such as Sequence, which
        provide more options for customisation. Those grammar objects should
        redefine this method accordingly.
        """
        return copy.copy(self)

    @abstractmethod
    def cache_key(self) -> str:
        """A string to use for cache keying.

        This string should be unique at the parsing stage such that
        if there has already been a match against this key for a set
        of segments, that we can reuse that match.
        """
