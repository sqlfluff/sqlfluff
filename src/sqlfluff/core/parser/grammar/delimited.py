"""Definitions for Grammar."""

from typing import Tuple

from tqdm import tqdm

from sqlfluff.core.config import progress_bar_configuration
from sqlfluff.core.parser import NewlineSegment
from sqlfluff.core.parser.grammar import Ref
from sqlfluff.core.parser.segments import BaseSegment, allow_ephemeral
from sqlfluff.core.parser.helpers import trim_non_code_segments
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.context import ParseContext

from sqlfluff.core.parser.grammar.noncode import NonCodeMatcher
from sqlfluff.core.parser.grammar.anyof import OneOf


class Delimited(OneOf):
    """Match an arbitrary number of elements separated by a delimiter.

    Note that if there are multiple elements passed in that they will be treated
    as different options of what can be delimited, rather than a sequence.
    """

    equality_kwargs = (
        "optional",
        "allow_gaps",
        "delimiter",
        "allow_trailing",
        "terminator",
        "min_delimiters",
    )

    def __init__(
        self,
        *args,
        delimiter=Ref("CommaSegment"),
        allow_trailing=False,
        terminator=None,
        min_delimiters=None,
        **kwargs,
    ):
        if delimiter is None:  # pragma: no cover
            raise ValueError("Delimited grammars require a `delimiter`")
        self.bracket_pairs_set = kwargs.pop("bracket_pairs_set", "bracket_pairs")
        self.delimiter = self._resolve_ref(delimiter)
        self.allow_trailing = allow_trailing
        self.terminator = self._resolve_ref(terminator)
        # Setting min delimiters means we have to match at least this number
        self.min_delimiters = min_delimiters
        super().__init__(*args, **kwargs)

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
                with parse_context.deeper_match() as ctx:
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

                with parse_context.deeper_match() as ctx:
                    match, _ = self._longest_trimmed_match(
                        segments=seg_content,
                        matchers=elements,
                        parse_context=ctx,
                        # We've already trimmed
                        trim_noncode=False,
                        terminators=delimiter_matchers
                        if elements != delimiter_matchers
                        else None,
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
