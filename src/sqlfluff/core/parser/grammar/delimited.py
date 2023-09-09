"""Definitions for Grammar."""

from typing import Optional, Sequence, Tuple, Union

from tqdm import tqdm

from sqlfluff.core.config import progress_bar_configuration
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import Ref
from sqlfluff.core.parser.grammar.anyof import OneOf
from sqlfluff.core.parser.grammar.noncode import NonCodeMatcher
from sqlfluff.core.parser.helpers import trim_non_code_segments
from sqlfluff.core.parser.match_result import MatchResult
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
        terminators: Sequence[Union[MatchableType, str]] = (),
        reset_terminators: bool = False,
        min_delimiters: Optional[int] = None,
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
        # Setting min delimiters means we have to match at least this number
        self.min_delimiters = min_delimiters
        super().__init__(
            *args,
            terminators=terminators,
            reset_terminators=reset_terminators,
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
        new_line_segments = [s for s in segments if s.is_type("newline")]
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
        # NOTE: If the configured delimiter is in parse_context.terminators then
        # treat is _only_ as a delimiter and not as a terminator. This happens
        # frequently during nested comma expressions.
        terminator_matchers = [
            *self.terminators,
            *(t for t in parse_context.terminators if t not in delimiter_matchers),
        ]

        # If gaps aren't allowed, a gap (or non-code segment), acts like a terminator.
        if not self.allow_gaps:
            terminator_matchers.append(NonCodeMatcher())

        while True:
            progressbar_matching.update(n=1)

            if len(seg_buff) == 0:  # pragma: no cover
                break

            pre_non_code, seg_content, post_non_code = trim_non_code_segments(seg_buff)

            if not self.allow_gaps and any(seg.is_whitespace for seg in pre_non_code):
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

            with parse_context.deeper_match(
                name="Delimited",
                push_terminators=[] if seeking_delimiter else delimiter_matchers,
                clear_terminators=self.reset_terminators,
            ) as ctx:
                match, _ = self._longest_trimmed_match(
                    segments=seg_content,
                    matchers=delimiter_matchers
                    if seeking_delimiter
                    else self._elements,
                    parse_context=ctx,
                    # We've already trimmed
                    trim_noncode=False,
                )

            if not match:
                matched_segments += pre_non_code
                unmatched_segments = match.unmatched_segments + post_non_code
                break

            if seeking_delimiter:
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
