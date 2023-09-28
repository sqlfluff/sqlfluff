"""GreedyUntil Grammar."""

from typing import Sequence, Tuple, Union

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.base import BaseGrammar, BaseSegment
from sqlfluff.core.parser.match_algorithms import greedy_match
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.matchable import Matchable


class GreedyUntil(BaseGrammar):
    """Matching for GreedyUntil works just how you'd expect."""

    def __init__(
        self,
        *args: Union[Matchable, str],
        optional: bool = False,
        terminators: Sequence[Union[Matchable, str]] = (),
        reset_terminators: bool = False,
    ) -> None:
        # NOTE: This grammar does not support allow_gaps=False,
        # therefore that option is not provided here.
        super().__init__(
            *args,
            optional=optional,
            terminators=terminators,
            reset_terminators=reset_terminators,
        )

    @match_wrapper()
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> MatchResult:
        """Matching for GreedyUntil works just how you'd expect."""
        return greedy_match(
            segments,
            parse_context,
            matchers=self._elements,
            include_terminator=False,
        )
