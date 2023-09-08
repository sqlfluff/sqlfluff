"""GreedyUntil Grammar."""

from typing import Optional, Sequence, Tuple, TypeVar, Union

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.base import (
    BaseGrammar,
    BaseSegment,
    cached_method_for_parse_context,
)
from sqlfluff.core.parser.match_algorithms import greedy_match
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.segments import allow_ephemeral
from sqlfluff.core.parser.types import MatchableType, SimpleHintType


class GreedyUntil(BaseGrammar):
    """Matching for GreedyUntil works just how you'd expect."""

    def __init__(
        self,
        *args: Union[MatchableType, str],
        optional: bool = False,
        ephemeral_name: Optional[str] = None,
        terminators: Sequence[Union[MatchableType, str]] = (),
        reset_terminators: bool = False,
    ) -> None:
        # NOTE: This grammar does not support allow_gaps=False,
        # therefore that option is not provided here.
        super().__init__(
            *args,
            optional=optional,
            ephemeral_name=ephemeral_name,
            terminators=terminators,
            reset_terminators=reset_terminators,
        )

    @match_wrapper()
    @allow_ephemeral
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
