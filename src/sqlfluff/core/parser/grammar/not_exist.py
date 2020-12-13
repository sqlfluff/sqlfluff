"""NotExist grammar."""

from .base import BaseGrammar
from sqlfluff.core.parser.match_result import MatchResult


class NotExist(BaseGrammar):
    """Lookahead/lookbehind which matches when the target does not match and vice-versa.

    The Not grammar always returns segments as they were before the match() function ran.
    In other words, it does not "consume" segments.
    """

    def __init__(self, target, *args, **kwargs):
        self.target = self._resolve_ref(target)
        super(NotExist, self).__init__(*args, **kwargs)

    def match(self, segments, parse_context):
        """Uses the target matcher and negates the result while leaving segments untouched."""
        match_result = self.target.match(segments, parse_context)

        if match_result.matched_segments:
            return MatchResult.from_unmatched(segments)
        else:
            return MatchResult.from_matched(segments)
