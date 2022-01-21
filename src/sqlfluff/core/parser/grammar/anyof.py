"""AnyNumberOf and OneOf."""

from typing import List, Optional, Tuple

from sqlfluff.core.parser.helpers import trim_non_code_segments
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.match_logging import parse_match_logging
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.segments import BaseSegment, allow_ephemeral
from sqlfluff.core.parser.grammar.base import (
    BaseGrammar,
    MatchableType,
    cached_method_for_parse_context,
)
from sqlfluff.core.parser.grammar.sequence import Sequence, Bracketed


class AnyNumberOf(BaseGrammar):
    """A more configurable version of OneOf."""

    def __init__(self, *args, **kwargs):
        self.max_times = kwargs.pop("max_times", None)
        self.min_times = kwargs.pop("min_times", 0)
        self.max_times_per_element = kwargs.pop("max_times_per_element", None)
        # Any patterns to _prevent_ a match.
        self.exclude = kwargs.pop("exclude", None)
        super().__init__(*args, **kwargs)

    @cached_method_for_parse_context
    def simple(self, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        AnyNumberOf does provide this, as long as *all* the elements *also* do.
        """
        simple_buff = [
            opt.simple(parse_context=parse_context) for opt in self._elements
        ]
        if any(elem is None for elem in simple_buff):
            return None
        # Flatten the list
        return [inner for outer in simple_buff for inner in outer]

    def is_optional(self) -> bool:
        """Return whether this element is optional.

        This is mostly set in the init method, but also in this
        case, if min_times is zero then this is also optional.
        """
        return self.optional or self.min_times == 0

    @staticmethod
    def _first_non_whitespace(segments) -> Optional[str]:
        """Return the upper first non-whitespace segment in the iterable."""
        for segment in segments:
            if segment.raw_segments_upper:
                return segment.raw_segments_upper
        return None

    def _prune_options(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> Tuple[List[MatchableType], List[str]]:
        """Use the simple matchers to prune which options to match on."""
        available_options = []
        simple_opts = []
        prune_buff = []
        non_simple = 0
        pruned_simple = 0
        matched_simple = 0

        # Find the first code element to match against.
        first_elem = self._first_non_whitespace(segments)

        for opt in self._elements:
            simple = opt.simple(parse_context=parse_context)
            if simple is None:
                # This element is not simple, we have to do a
                # full match with it...
                available_options.append(opt)
                non_simple += 1
                continue
            # Otherwise we have a simple option, so let's use
            # it for pruning.
            for simple_opt in simple:
                # Check it's not a whitespace option
                if not simple_opt.strip():  # pragma: no cover
                    raise NotImplementedError(
                        "_prune_options not supported for whitespace matching."
                    )
                # We want to know if the first meaningful element of the str_buff
                # matches the option.

                # match the FIRST non-whitespace element of the list.
                if first_elem != simple_opt:
                    # No match, carry on.
                    continue
                # If we get here, it's matched the FIRST element of the string buffer.
                available_options.append(opt)
                simple_opts.append(simple_opt)
                matched_simple += 1
                break
            else:
                # Ditch this option, the simple match has failed
                prune_buff.append(opt)
                pruned_simple += 1
                continue

        parse_match_logging(
            self.__class__.__name__,
            "match",
            "PRN",
            parse_context=parse_context,
            v_level=3,
            ns=non_simple,
            ps=pruned_simple,
            ms=matched_simple,
            pruned=prune_buff,
            opts=available_options or "ALL",
        )

        return available_options, simple_opts

    def _match_once(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> Tuple[MatchResult, Optional["MatchableType"]]:
        """Match the forward segments against the available elements once.

        This serves as the main body of OneOf, but also a building block
        for AnyNumberOf.
        """
        # For efficiency, we'll be pruning options if we can
        # based on their simpleness. this provides a short cut
        # to return earlier if we can.
        # `segments` may already be nested so we need to break out
        # the raw segments within it.
        available_options, _ = self._prune_options(
            segments, parse_context=parse_context
        )

        # If we've pruned all the options, return unmatched (with some logging).
        if not available_options:
            return MatchResult.from_unmatched(segments)

        with parse_context.deeper_match() as ctx:
            match, matched_option = self._longest_trimmed_match(
                segments,
                available_options,
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
            with parse_context.deeper_match() as ctx:
                if self.exclude.match(segments, parse_context=ctx):
                    return MatchResult.from_unmatched(segments)

        # Match on each of the options
        matched_segments: MatchResult = MatchResult.from_empty()
        unmatched_segments: Tuple[BaseSegment, ...] = segments
        n_matches = 0

        # Keep track of the number of times each option has been matched.
        available_options, _ = self._prune_options(
            segments, parse_context=parse_context
        )
        available_option_counter = {str(o): 0 for o in available_options}

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
            if matched_option and (str(matched_option) in available_option_counter):
                available_option_counter[str(matched_option)] += 1
                # Check if we have matched an option too many times.
                if (
                    self.max_times_per_element
                    and available_option_counter[str(matched_option)]
                    > self.max_times_per_element
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_times=1, min_times=1, **kwargs)


class OptionallyBracketed(OneOf):
    """Hybrid of Bracketed and Sequence: allows brackets but they aren't required.

    NOTE: This class is greedy on brackets so if they *can* be claimed, then
    they will be.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            Bracketed(*args),
            # In the case that there is only one argument, no sequence is required.
            args[0] if len(args) == 1 else Sequence(*args),
            **kwargs,
        )


class AnySetOf(AnyNumberOf):
    """Match any number of the elements but each element can only be matched once."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_times_per_element=1, **kwargs)
