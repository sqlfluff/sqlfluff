"""GreedyUntil and StartsWith Grammars."""

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
    """Matching for GreedyUntil works just how you'd expect.

    Args:
        enforce_whitespace_preceding (:obj:`bool`): Should the GreedyUntil
            match only match the content if it's preceded by whitespace?
            (defaults to False). This is useful for some keywords which may
            have false alarms on some array accessors.

    """

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


T = TypeVar("T", bound="StartsWith")


class StartsWith(GreedyUntil):
    """Match if this sequence starts with a match.

    This also has configurable whitespace and comment handling.
    """

    def __init__(
        self,
        target: Union[MatchableType, str],
        *args: Union[MatchableType, str],
        terminators: Sequence[Union[MatchableType, str]] = (),
        reset_terminators: bool = False,
        include_terminator: bool = False,
        optional: bool = False,
        ephemeral_name: Optional[str] = None,
    ) -> None:
        self.target = self._resolve_ref(target)
        self.include_terminator = include_terminator

        super().__init__(
            *args,
            optional=optional,
            ephemeral_name=ephemeral_name,
            terminators=terminators,
            reset_terminators=reset_terminators,
        )

        # StartsWith should only be used with a terminator
        assert self.terminators

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a uppercase hash matching route?

        `StartsWith` is simple, if the thing it starts with is also simple.
        """
        return self.target.simple(parse_context=parse_context, crumbs=crumbs)

    @match_wrapper()
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> MatchResult:
        """Match if this sequence starts with a match."""
        first_code_idx = None
        # Work through to find the first code segment...
        for idx, seg in enumerate(segments):
            if seg.is_code:
                first_code_idx = idx
                break
        else:
            # We've trying to match on a sequence of segments which contain no code.
            # That means this isn't a match.
            return MatchResult.from_unmatched(segments)  # pragma: no cover TODO?
        with parse_context.deeper_match(name="StartsWith") as ctx:
            match = self.target.match(segments[first_code_idx:], ctx)

        if not match:
            return MatchResult.from_unmatched(segments)

        # The match will probably have returned a mutated version rather
        # that the raw segment sent for matching. We need to reinsert it
        # back into the sequence in place of the raw one, but we can't
        # just assign at the index because it's a tuple and not a list.
        # to get around that we do this slightly more elaborate construction.

        # NB: This match may be partial or full, either is cool. In the case
        # of a partial match, given that we're only interested in what it STARTS
        # with, then we can still used the unmatched parts on the end.
        # We still need to deal with any non-code segments at the start.
        assert self.terminators
        greedy_matched = greedy_match(
            match.unmatched_segments,
            parse_context,
            # We match up to the terminators for this segment, but _also_
            # any existing terminators within the context.
            matchers=[*self.terminators, *parse_context.terminators],
            include_terminator=self.include_terminator,
        )

        # NB: If all we matched in the greedy match was non-code then we can't
        # claim it.
        if not any(seg.is_code for seg in greedy_matched.matched_segments):
            # So just return the original match.
            return match

        # Otherwise Combine the results.
        return MatchResult(
            match.matched_segments + greedy_matched.matched_segments,
            greedy_matched.unmatched_segments,
        )
