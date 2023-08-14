"""AnyNumberOf, OneOf, OptionallyBracketed & AnySetOf."""

from typing import List, Optional, Tuple

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.base import (
    BaseGrammar,
    cached_method_for_parse_context,
    MatchableType,
)
from sqlfluff.core.parser.grammar.types import SimpleHintType
from sqlfluff.core.parser.grammar.sequence import Sequence, Bracketed
from sqlfluff.core.parser.helpers import trim_non_code_segments
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.segments import BaseSegment, allow_ephemeral


class AnyNumberOf(BaseGrammar):
    """A more configurable version of OneOf."""

    def __init__(self, *args, **kwargs) -> None:
        self.max_times = kwargs.pop("max_times", None)
        self.min_times = kwargs.pop("min_times", 0)
        self.max_times_per_element = kwargs.pop("max_times_per_element", None)
        # Any patterns to _prevent_ a match.
        self.exclude = kwargs.pop("exclude", None)
        # The intent here is that if we match something, and then the _next_
        # item is one of these, we can safely conclude it's a "total" match.
        # In those cases, we return early without considering more options.
        self.terminators = kwargs.pop("terminators", None)
        self.reset_terminators = kwargs.pop("reset_terminators", False)
        super().__init__(*args, **kwargs)

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[List[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a uppercase hash matching route?

        AnyNumberOf does provide this, as long as *all* the elements *also* do.
        """
        simple_buff = [
            opt.simple(parse_context=parse_context, crumbs=crumbs)
            for opt in self._elements
        ]
        if any(elem is None for elem in simple_buff):
            return None
        # Combine the lists
        simple_raws = [simple[0] for simple in simple_buff if simple[0]]
        simple_types = [simple[1] for simple in simple_buff if simple[1]]
        return (
            frozenset.union(*simple_raws) if simple_raws else frozenset(),
            frozenset.union(*simple_types) if simple_types else frozenset(),
        )

    def is_optional(self) -> bool:
        """Return whether this element is optional.

        This is mostly set in the init method, but also in this
        case, if min_times is zero then this is also optional.
        """
        return self.optional or self.min_times == 0

    def _match_once(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> Tuple[MatchResult, Optional["MatchableType"]]:
        """Match the forward segments against the available elements once.

        This serves as the main body of OneOf, but also a building block
        for AnyNumberOf.
        """
        with parse_context.deeper_match(
            name=self.__class__.__name__,
            clear_terminators=self.reset_terminators,
            push_terminators=self.terminators,
        ) as ctx:
            match, matched_option = self._longest_trimmed_match(
                segments,
                self._elements,
                parse_context=ctx,
                trim_noncode=False,
            )

        return match, matched_option

    @match_wrapper()
    @allow_ephemeral
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> MatchResult:
        """Match against any of the elements a relevant number of times.

        If it matches multiple, it returns the longest, and if any are the same
        length it returns the first (unless we explicitly just match first).
        """
        # First if we have an *exclude* option, we should check that
        # which would prevent the rest of this grammar from matching.
        if self.exclude:
            with parse_context.deeper_match(
                name=self.__class__.__name__ + "-Exclude"
            ) as ctx:
                if self.exclude.match(segments, parse_context=ctx):
                    return MatchResult.from_unmatched(segments)

        # Match on each of the options
        matched_segments: MatchResult = MatchResult.from_empty()
        unmatched_segments: Tuple[BaseSegment, ...] = segments
        n_matches = 0

        # Keep track of the number of times each option has been matched.
        option_counter = {elem.cache_key(): 0 for elem in self._elements}

        while True:
            if self.max_times and n_matches >= self.max_times:
                # We've matched as many times as we can
                return MatchResult(
                    matched_segments.matched_segments, unmatched_segments
                )

            # Is there anything left to match?
            if len(unmatched_segments) == 0:
                # No...
                if n_matches >= self.min_times:
                    return MatchResult(
                        matched_segments.matched_segments, unmatched_segments
                    )
                else:  # pragma: no cover TODO?
                    # We didn't meet the hurdle
                    return MatchResult.from_unmatched(unmatched_segments)

            # If we've already matched once...
            if n_matches > 0 and self.allow_gaps:
                # Consume any non-code if there is any
                pre_seg, mid_seg, post_seg = trim_non_code_segments(unmatched_segments)
                unmatched_segments = mid_seg + post_seg
            else:
                pre_seg = ()  # empty tuple

            match, matched_option = self._match_once(
                unmatched_segments, parse_context=parse_context
            )

            # Increment counter for matched option.
            if matched_option:
                matched_key = matched_option.cache_key()
                if matched_option.cache_key() in option_counter:
                    option_counter[matched_key] += 1
                    # Check if we have matched an option too many times.
                    if (
                        self.max_times_per_element
                        and option_counter[matched_key] > self.max_times_per_element
                    ):
                        return MatchResult(
                            matched_segments.matched_segments, unmatched_segments
                        )

            if match:
                matched_segments += pre_seg + match.matched_segments
                unmatched_segments = match.unmatched_segments
                n_matches += 1
            else:
                # If we get here, then we've not managed to match. And the next
                # unmatched segments are meaningful, i.e. they're not what we're
                # looking for.
                if n_matches >= self.min_times:
                    return MatchResult(
                        matched_segments.matched_segments, pre_seg + unmatched_segments
                    )
                else:
                    # We didn't meet the hurdle
                    return MatchResult.from_unmatched(unmatched_segments)


class OneOf(AnyNumberOf):
    """Match any of the elements given once.

    If it matches multiple, it returns the longest, and if any are the same
    length it returns the first (unless we explicitly just match first).
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, max_times=1, min_times=1, **kwargs)


class OptionallyBracketed(OneOf):
    """Hybrid of Bracketed and Sequence: allows brackets but they aren't required.

    NOTE: This class is greedy on brackets so if they *can* be claimed, then
    they will be.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            Bracketed(*args),
            # In the case that there is only one argument, no sequence is required.
            args[0] if len(args) == 1 else Sequence(*args),
            **kwargs,
        )


class AnySetOf(AnyNumberOf):
    """Match any number of the elements but each element can only be matched once."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, max_times_per_element=1, **kwargs)
