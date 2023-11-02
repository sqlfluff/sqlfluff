"""AnyNumberOf, OneOf, OptionallyBracketed & AnySetOf."""

from typing import FrozenSet, List, Optional, Tuple, Union, cast
from typing import Sequence as SequenceType

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.base import (
    BaseGrammar,
    cached_method_for_parse_context,
)
from sqlfluff.core.parser.grammar.sequence import Bracketed, Sequence
from sqlfluff.core.parser.match_algorithms import (
    longest_match,
    skip_start_index_forward_to_code,
    trim_to_terminator,
)
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments import BaseSegment, UnparsableSegment
from sqlfluff.core.parser.types import ParseMode, SimpleHintType


def _parse_mode_match_result(
    segments: SequenceType[BaseSegment],
    current_match: MatchResult,
    max_idx: int,
    parse_mode: ParseMode,
) -> MatchResult:
    """A helper function for the return values of AnyNumberOf.

    This method creates UnparsableSegments as appropriate
    depending on the parse mode and return values.
    """
    # If we're being strict, just return.
    if parse_mode == ParseMode.STRICT:
        return current_match

    # Nothing in unmatched anyway?
    _stop_idx = current_match.matched_slice.stop
    if _stop_idx == max_idx or all(not s.is_code for s in segments[_stop_idx:max_idx]):
        return current_match

    _trim_idx = skip_start_index_forward_to_code(segments, _stop_idx)

    # Create an unmatched segment
    _expected = "Nothing else"
    if len(segments) > max_idx:
        _expected += f" before {segments[max_idx].raw!r}"

    unmatched_match = MatchResult(
        matched_slice=slice(_trim_idx, max_idx),
        matched_class=UnparsableSegment,
        segment_kwargs={"expected": _expected},
    )

    return current_match.append(unmatched_match)


class AnyNumberOf(BaseGrammar):
    """A more configurable version of OneOf."""

    supported_parse_modes = {
        ParseMode.STRICT,
        ParseMode.GREEDY,
    }

    def __init__(
        self,
        *args: Union[Matchable, str],
        max_times: Optional[int] = None,
        min_times: int = 0,
        max_times_per_element: Optional[int] = None,
        exclude: Optional[Matchable] = None,
        terminators: SequenceType[Union[Matchable, str]] = (),
        reset_terminators: bool = False,
        allow_gaps: bool = True,
        optional: bool = False,
        parse_mode: ParseMode = ParseMode.STRICT,
    ) -> None:
        self.max_times = max_times
        self.min_times = min_times
        self.max_times_per_element = max_times_per_element
        # Any patterns to _prevent_ a match.
        self.exclude = exclude
        super().__init__(
            *args,
            allow_gaps=allow_gaps,
            optional=optional,
            terminators=terminators,
            reset_terminators=reset_terminators,
            parse_mode=parse_mode,
        )

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a uppercase hash matching route?

        AnyNumberOf does provide this, as long as *all* the elements *also* do.
        """
        option_simples: List[SimpleHintType] = [
            opt.simple(parse_context=parse_context, crumbs=crumbs)
            for opt in self._elements
        ]
        if any(elem is None for elem in option_simples):
            return None
        # We now know that there are no Nones.
        simple_buff = cast(List[Tuple[FrozenSet[str], FrozenSet[str]]], option_simples)
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

    def match(
        self,
        segments: SequenceType["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match against any of the elements a relevant number of times.

        If it matches multiple, it returns the longest, and if any are the same
        length it returns the first (unless we explicitly just match first).
        """
        if self.exclude:
            with parse_context.deeper_match(
                name=self.__class__.__name__ + "-Exclude"
            ) as ctx:
                if self.exclude.match(segments, idx, ctx):
                    return MatchResult.empty_at(idx)

        n_matches = 0
        # Keep track of the number of times each option has been matched.
        option_counter = {elem.cache_key(): 0 for elem in self._elements}
        # Keep track of how far we've got.
        matched_idx = idx
        # The working index is to cover non-code elements which aren't
        # claimed yet, but we should conditionally claim if the next
        # match is succesful.
        working_idx = idx
        matched = MatchResult.empty_at(idx)
        max_idx = len(segments)  # What is the limit

        if self.parse_mode == ParseMode.GREEDY:
            max_idx = trim_to_terminator(
                segments,
                idx,
                terminators=[*self.terminators, *parse_context.terminators],
                parse_context=parse_context,
            )

        while True:
            if n_matches >= self.min_times:
                if (
                    # Either nothing left to match...
                    matched_idx >= max_idx
                    # ...Or we've matched as many times as allowed.
                    or (self.max_times and n_matches >= self.max_times)
                ):
                    # NOTE: For OneOf, this is the matched return path.
                    return _parse_mode_match_result(
                        segments,
                        matched,
                        max_idx,
                        self.parse_mode,
                    )

            # Is there nothing left to match?
            if matched_idx >= max_idx:
                # Return unsuccessful as we didn't meet the hurdle.
                # The positive exhausted return is above.
                return MatchResult.empty_at(idx)

            with parse_context.deeper_match(
                name=self.__class__.__name__,
                clear_terminators=self.reset_terminators,
                push_terminators=self.terminators,
            ) as ctx:
                match, matched_option = longest_match(
                    # TODO: Resolve re-slice limit hack
                    segments[:max_idx],
                    self._elements,
                    working_idx,
                    ctx,
                )

            # Did we fail to match?
            if not match:
                # If we haven't already met the hurdle rate, act as though
                # not match at all.
                if n_matches < self.min_times:
                    matched = MatchResult.empty_at(idx)

                return _parse_mode_match_result(
                    segments,
                    matched,
                    max_idx,
                    self.parse_mode,
                )

            # Otherwise we have a new clean match.
            assert match
            assert matched_option

            # Update counts of each option in case we've hit limits.
            matched_key = matched_option.cache_key()
            if matched_option.cache_key() in option_counter:
                option_counter[matched_key] += 1
                # Check if we have matched an option too many times.
                if (
                    self.max_times_per_element
                    and option_counter[matched_key] > self.max_times_per_element
                ):
                    # Return the match so far, without the most recent match.
                    return _parse_mode_match_result(
                        segments,
                        matched,
                        max_idx,
                        self.parse_mode,
                    )

            # If we haven't hit limits then consume and move on.
            matched = matched.append(match)
            matched_idx = matched.matched_slice.stop
            working_idx = matched_idx
            if self.allow_gaps:
                working_idx = skip_start_index_forward_to_code(segments, matched_idx)
            parse_context.update_progress(matched_idx)
            n_matches += 1
            # Continue around the loop...


class OneOf(AnyNumberOf):
    """Match any of the elements given once.

    If it matches multiple, it returns the longest, and if any are the same
    length it returns the first (unless we explicitly just match first).
    """

    def __init__(
        self,
        *args: Union[Matchable, str],
        exclude: Optional[Matchable] = None,
        terminators: SequenceType[Union[Matchable, str]] = (),
        reset_terminators: bool = False,
        allow_gaps: bool = True,
        optional: bool = False,
        parse_mode: ParseMode = ParseMode.STRICT,
    ) -> None:
        super().__init__(
            *args,
            max_times=1,
            min_times=1,
            exclude=exclude,
            terminators=terminators,
            reset_terminators=reset_terminators,
            allow_gaps=allow_gaps,
            optional=optional,
            parse_mode=parse_mode,
        )


class OptionallyBracketed(OneOf):
    """Hybrid of Bracketed and Sequence: allows brackets but they aren't required.

    NOTE: This class is greedy on brackets so if they *can* be claimed, then
    they will be.
    """

    def __init__(
        self,
        *args: Union[Matchable, str],
        exclude: Optional[Matchable] = None,
        terminators: SequenceType[Union[Matchable, str]] = (),
        reset_terminators: bool = False,
        optional: bool = False,
        parse_mode: ParseMode = ParseMode.STRICT,
    ) -> None:
        super().__init__(
            Bracketed(*args),
            # In the case that there is only one argument, no sequence is required.
            args[0] if len(args) == 1 else Sequence(*args),
            exclude=exclude,
            terminators=terminators,
            reset_terminators=reset_terminators,
            optional=optional,
            parse_mode=parse_mode,
        )


class AnySetOf(AnyNumberOf):
    """Match any number of the elements but each element can only be matched once."""

    def __init__(
        self,
        *args: Union[Matchable, str],
        max_times: Optional[int] = None,
        min_times: int = 0,
        exclude: Optional[Matchable] = None,
        terminators: SequenceType[Union[Matchable, str]] = (),
        reset_terminators: bool = False,
        allow_gaps: bool = True,
        optional: bool = False,
        parse_mode: ParseMode = ParseMode.STRICT,
    ) -> None:
        super().__init__(
            *args,
            max_times_per_element=1,
            max_times=max_times,
            min_times=min_times,
            exclude=exclude,
            terminators=terminators,
            reset_terminators=reset_terminators,
            allow_gaps=allow_gaps,
            optional=optional,
            parse_mode=parse_mode,
        )
