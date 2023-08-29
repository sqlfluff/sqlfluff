"""Definitions for Grammar."""

from typing import Optional, Tuple, Union, Sequence

from tqdm import tqdm

from sqlfluff.core.config import progress_bar_configuration
from sqlfluff.core.parser import NewlineSegment
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import Ref
from sqlfluff.core.parser.grammar.anyof import OneOf
from sqlfluff.core.parser.grammar.noncode import NonCodeMatcher
from sqlfluff.core.parser.helpers import trim_non_code_segments
from sqlfluff.core.parser.match_result import MatchResult, MatchResult2
from sqlfluff.core.parser.match_utils import longest_match2
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.segments import BaseSegment, allow_ephemeral
from sqlfluff.core.parser.types import MatchableType


class Delimited(OneOf):
    """Match an arbitrary number of elements separated by a delimiter.

    Note that if there are multiple elements passed in that they will be treated
    as different options of what can be delimited, rather than a sequence.
    """

    equality_kwargs = (
        "_elements",
        "optional",
        "allow_gaps",
        "delimiter",
        "allow_trailing",
        "terminator",
        "min_delimiters",
    )

    def __init__(
        self,
        *args: Union[MatchableType, str],
        delimiter: Union[MatchableType, str] = Ref("CommaSegment"),
        allow_trailing: bool = False,
        # NOTE: Other grammars support terminators (plural)
        # TODO: Align these to be the same eventually.
        terminator: Optional[Union[MatchableType, str]] = None,
        min_delimiters: int = 1,
        bracket_pairs_set: str = "bracket_pairs",
        allow_gaps: bool = True,
        optional: bool = False,
        ephemeral_name: Optional[str] = None,
    ) -> None:
        if delimiter is None:  # pragma: no cover
            raise ValueError("Delimited grammars require a `delimiter`")
        self.bracket_pairs_set = bracket_pairs_set
        self.delimiter = self._resolve_ref(delimiter)
        self.allow_trailing = allow_trailing
        self.terminator = self._resolve_ref(terminator)
        # Setting min delimiters means we have to match at least this number
        self.min_delimiters = min_delimiters
        super().__init__(
            *args,
            allow_gaps=allow_gaps,
            optional=optional,
            ephemeral_name=ephemeral_name,
        )

    @match_wrapper()
    @allow_ephemeral
    def match(
        self,
        segments: Tuple[BaseSegment, ...],
        parse_context: ParseContext,
    ) -> MatchResult:
        """Match an arbitrary number of elements separated by a delimiter.

        Note that if there are multiple elements passed in that they will be treated
        as different options of what can be delimited, rather than a sequence.
        """
        # Have we been passed an empty list?
        if len(segments) == 0:
            return MatchResult.from_empty()

        # Make some buffers
        seg_buff = segments
        matched_segments: Tuple[BaseSegment, ...] = ()
        unmatched_segments: Tuple[BaseSegment, ...] = ()
        cached_matched_segments: Tuple[BaseSegment, ...] = ()
        cached_unmatched_segments: Tuple[BaseSegment, ...] = ()

        delimiters = 0
        matched_delimiter = False

        # We want to render progress bar only for the main matching loop,
        # so disable it when in deeper parsing.
        disable_progress_bar = (
            parse_context.parse_depth > 0
            or progress_bar_configuration.disable_progress_bar
        )

        # We use amount of `NewLineSegment` to estimate how many steps could be in
        # a big file. It's not perfect, but should do a job in most cases.
        new_line_segments = [s for s in segments if isinstance(s, NewlineSegment)]
        progressbar_matching = tqdm(
            total=len(new_line_segments),
            desc="matching",
            miniters=30,
            disable=disable_progress_bar,
            leave=False,
        )

        seeking_delimiter = False
        has_matched_segs = False
        terminated = False

        delimiter_matchers = [self.delimiter]
        terminator_matchers = []

        if self.terminator:
            terminator_matchers.append(self.terminator)
        # If gaps aren't allowed, a gap (or non-code segment), acts like a terminator.
        if not self.allow_gaps:
            terminator_matchers.append(NonCodeMatcher())

        while True:
            progressbar_matching.update(n=1)

            if seeking_delimiter:
                elements = delimiter_matchers

            else:
                elements = self._elements

            if len(seg_buff) > 0:
                pre_non_code, seg_content, post_non_code = trim_non_code_segments(
                    seg_buff
                )

                if not self.allow_gaps and any(
                    seg.is_whitespace for seg in pre_non_code
                ):
                    unmatched_segments = seg_buff
                    break

                if not seg_content:  # pragma: no cover
                    matched_segments += pre_non_code
                    break

                # Check whether there is a terminator before checking for content
                with parse_context.deeper_match(name="Delimited-Term") as ctx:
                    match, _ = self._longest_trimmed_match(
                        segments=seg_content,
                        matchers=terminator_matchers,
                        parse_context=ctx,
                        # We've already trimmed
                        trim_noncode=False,
                    )

                    if match:
                        terminated = True
                        unmatched_segments = (
                            pre_non_code + match.all_segments() + post_non_code
                        )
                        break

                _push_terminators = []
                if delimiter_matchers and elements != delimiter_matchers:
                    _push_terminators = delimiter_matchers
                with parse_context.deeper_match(
                    name="Delimited", push_terminators=_push_terminators
                ) as ctx:
                    match, _ = self._longest_trimmed_match(
                        segments=seg_content,
                        matchers=elements,
                        parse_context=ctx,
                        # We've already trimmed
                        trim_noncode=False,
                    )

                if match:
                    if elements == delimiter_matchers:
                        delimiters += 1
                        matched_delimiter = True
                        cached_matched_segments = matched_segments
                        cached_unmatched_segments = seg_buff

                    else:
                        matched_delimiter = False

                    has_matched_segs = True
                    seg_buff = match.unmatched_segments + post_non_code
                    unmatched_segments = match.unmatched_segments

                    if match.is_complete():
                        matched_segments += (
                            pre_non_code + match.matched_segments + post_non_code
                        )

                        unmatched_segments = match.unmatched_segments
                        break

                    matched_segments += pre_non_code + match.matched_segments
                    seeking_delimiter = not seeking_delimiter

                else:
                    matched_segments += pre_non_code
                    unmatched_segments = match.unmatched_segments + post_non_code
                    break

            else:
                break  # pragma: no cover

        if self.min_delimiters:
            if delimiters < self.min_delimiters:
                return MatchResult.from_unmatched(matched_segments + unmatched_segments)

        if terminated:
            if has_matched_segs:
                return MatchResult(matched_segments, unmatched_segments)
            else:
                return MatchResult.from_unmatched(matched_segments + unmatched_segments)

        if matched_delimiter and not self.allow_trailing:
            if not unmatched_segments:
                return MatchResult.from_unmatched(matched_segments + unmatched_segments)
            else:
                return MatchResult(cached_matched_segments, cached_unmatched_segments)

        if not has_matched_segs:
            return MatchResult.from_unmatched(matched_segments + unmatched_segments)

        if not unmatched_segments:
            return MatchResult.from_matched(matched_segments)

        return MatchResult(matched_segments, unmatched_segments)

    def match2(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult2:
        """Match against this matcher."""
        # NOTE: THIS IS A GREAT PLACE FOR PARTIAL UNPARSABLES.
        # TODO: WE SHOULD PORT THE PROGRESSBAR LOGIC (NOT DONE YET).
        # In theory it should be even better because in a "single match"
        # regime, we can literally count the matched segments so far.
        # SUPER GRANULAR.

        delimiters = 0
        seeking_delimiter = False
        max_idx = len(segments)
        working_idx = idx
        working_match = MatchResult2.empty_at(idx)
        delimiter_match: Optional[MatchResult2] = None

        delimiter_matchers = [self.delimiter]
        terminator_matchers = []

        if self.terminator:
            terminator_matchers.append(self.terminator)
        # If gaps aren't allowed, a gap (or non-code segment), acts like a terminator.
        if not self.allow_gaps:
            terminator_matchers.append(NonCodeMatcher())

        while True:
            _idx = working_idx
            # If we're past the start and allowed gaps, work forward
            # through any gaps.
            if self.allow_gaps and working_idx > idx:
                for _idx in range(working_idx, max_idx):
                    if segments[_idx].is_code:
                        break

            # Do we have anything left to match on?
            if _idx >= max_idx:  # TODO: Revisit this.
                break

            # Check whether there is a terminator before checking for content
            with parse_context.deeper_match(name="Delimited-Term") as ctx:
                match, _ = longest_match2(
                    segments=segments,
                    matchers=terminator_matchers,
                    idx=_idx,
                    parse_context=ctx,
                )
            if match:
                break

            # Then match for content/delimiter as appropriate.
            _push_terminators = []
            if delimiter_matchers and not seeking_delimiter:
                _push_terminators = delimiter_matchers
            with parse_context.deeper_match(
                name="Delimited", push_terminators=_push_terminators
            ) as ctx:
                match, _ = longest_match2(
                    segments=segments,
                    matchers=delimiter_matchers
                    if seeking_delimiter
                    else self._elements,
                    idx=_idx,
                    parse_context=ctx,
                )

            if not match:
                # Failed the find the next item in the sequence.
                # TODO: Should we handle the partial better?
                # Looking for the next delimiter or terminator if we can and then
                # claiming an unparsable.
                break

            # Otherwise we _did_ match. Handle it.
            if seeking_delimiter:
                # It's a delimiter
                delimiter_match = match
            else:
                # It's content. Add both the last delimiter and the content to the
                # working match.
                if delimiter_match:
                    # NOTE: This should happen on every loop _except_ the first.
                    delimiters += 1
                    working_match.append(delimiter_match)
                working_match = working_match.append(match)

            # Prep for going back around the loop...
            working_idx = match.matched_slice.stop
            seeking_delimiter = not seeking_delimiter

        if self.allow_trailing and not seeking_delimiter:
            delimiters += 1
            working_match = working_match.append(delimiter_match)

        if delimiters < self.min_delimiters:
            return MatchResult2.empty_at(idx)

        return working_match
