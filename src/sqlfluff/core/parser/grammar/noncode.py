"""A non-code matcher.

This is a stub of a grammar, intended for use entirely as a
terminator or similar alongside other matchers.
"""

from typing import Optional, List

from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.context import ParseContext


class NonCodeMatcher(Matchable):
    """An object which behaves like a matcher to match non-code."""

    def simple(self, parse_context: ParseContext) -> Optional[List[str]]:
        """This element doesn't work with simple."""
        return None

    @match_wrapper(v_level=4)
    def match(self, segments, parse_context):
        """Match any starting non-code segments."""
        if not isinstance(segments, tuple):
            raise TypeError("NonCodeMatcher expects a tuple.")
        idx = 0
        while idx < len(segments) and not segments[idx].is_code:
            idx += 1
        return MatchResult(segments[:idx], segments[idx:])
