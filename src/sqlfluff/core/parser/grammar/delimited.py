"""Definitions for Grammar."""

from typing import Tuple, List

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
        matched_segments = MatchResult.from_empty()
        # delimiters is a list of tuples containing delimiter segments as we find them.
        delimiters: List[BaseSegment] = []

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

        # First iterate through all the segments, looking for the delimiter.
        # Second, split the list on each of the delimiters, and ensure that
        # each sublist in turn matches one of the elements.

        # In more detail, match against delimiter, if we match, put a slice
        # up to that point onto a list of slices. Carry on.
        while True:
            progressbar_matching.update(n=1)

            # Check to see whether we've exhausted the buffer, either by iterating
            # through it, or by consuming all the non-code segments already.
            # NB: If we're here then we've already tried matching the remaining segments
            # against the content, so we must be in a trailing case.
            if len(seg_buff) == 0:
                # Append the remaining buffer in case we're in the not is_code case.
                matched_segments += seg_buff
                # Nothing left, this is potentially a trailing case?
                if self.allow_trailing and (
                    self.min_delimiters is None
                    or len(delimiters) >= self.min_delimiters
                ):  # pragma: no cover TODO?
                    # It is! (nothing left so no unmatched segments to append)
                    return MatchResult.from_matched(matched_segments.matched_segments)
                else:  # pragma: no cover TODO?
                    return MatchResult.from_unmatched(segments)

            # We rely on _bracket_sensitive_look_ahead_match to do the bracket counting
            # element of this now. We look ahead to find a delimiter or terminator.
            matchers = [self.delimiter]
            if self.terminator:
                matchers.append(self.terminator)
            # If gaps aren't allowed, a gap (or non-code segment), acts like a
            # terminator.
            if not self.allow_gaps:
                matchers.append(NonCodeMatcher())

            with parse_context.deeper_match() as ctx:
                (
                    pre_content,
                    delimiter_match,
                    delimiter_matcher,
                ) = self._bracket_sensitive_look_ahead_match(
                    seg_buff,
                    matchers,
                    parse_context=ctx,
                    bracket_pairs_set=self.bracket_pairs_set,
                )

            # Store the mutated segments to reuse.
            mutated_segments = pre_content + delimiter_match.all_segments()

            # Have we found a delimiter or terminator looking forward?
            if delimiter_match:
                if delimiter_matcher is self.delimiter:
                    # Yes. Store it and then match the contents up to now.
                    delimiters.append(delimiter_match.matched_segments)

                # We now test the intervening section as to whether it matches one
                # of the things we're looking for. NB: If it's of zero length then
                # we return without trying it.
                if len(pre_content) > 0:
                    pre_non_code, pre_content, post_non_code = trim_non_code_segments(
                        pre_content
                    )
                    # Check for whitespace gaps.
                    # We do this explicitly here rather than relying on an
                    # untrimmed match so we can handle _whitespace_ explicitly
                    # compared to other non code segments like placeholders.
                    if not self.allow_gaps and any(
                        seg.is_whitespace for seg in pre_non_code + post_non_code
                    ):
                        return MatchResult.from_unmatched(
                            mutated_segments
                        )  # pragma: no cover TODO?

                    with parse_context.deeper_match() as ctx:
                        match, _ = self._longest_trimmed_match(
                            segments=pre_content,
                            matchers=self._elements,
                            parse_context=ctx,
                            # We've already trimmed
                            trim_noncode=False,
                        )
                    # No match - Not allowed
                    if not match:
                        if self.allow_trailing:
                            # If we reach this point, the lookahead match has hit a
                            # delimiter beyond the scope of this Delimited section.
                            # Trailing delimiters are allowed, so return matched up to
                            # this section.
                            return MatchResult(
                                matched_segments.matched_segments,
                                pre_non_code
                                + match.unmatched_segments
                                + post_non_code
                                + delimiter_match.all_segments(),
                            )
                        else:
                            return MatchResult.from_unmatched(mutated_segments)

                    if not match.is_complete():
                        # If we reach this point, the lookahead match has hit a
                        # delimiter beyond the scope of this Delimited section. We
                        # should return a partial match, and the delimiter as unmatched.
                        return MatchResult(
                            matched_segments.matched_segments
                            + pre_non_code
                            + match.matched_segments,
                            match.unmatched_segments
                            + post_non_code
                            + delimiter_match.all_segments(),
                        )

                    # We have a complete match!

                    # First add the segment up to the delimiter to the matched segments
                    matched_segments += (
                        pre_non_code + match.matched_segments + post_non_code
                    )
                    # Then it depends what we matched.
                    # Delimiter
                    if delimiter_matcher is self.delimiter:
                        # Then add the delimiter to the matched segments
                        matched_segments += delimiter_match.matched_segments
                        # Break this for loop and move on, looking for the next
                        # delimiter
                        seg_buff = delimiter_match.unmatched_segments
                        # Still got some buffer left. Carry on.
                        continue
                    # Terminator (or the gap terminator).
                    elif delimiter_matcher is self.terminator or isinstance(
                        delimiter_matcher, NonCodeMatcher
                    ):
                        # We just return straight away here. We don't add the terminator
                        # to this match, it should go with the unmatched parts.

                        # First check we've had enough delimiters
                        if (
                            self.min_delimiters
                            and len(delimiters) < self.min_delimiters
                        ):
                            return MatchResult.from_unmatched(mutated_segments)
                        else:
                            return MatchResult(
                                matched_segments.matched_segments,
                                delimiter_match.all_segments(),
                            )
                    else:  # pragma: no cover
                        raise RuntimeError(
                            (
                                "I don't know how I got here. Matched instead on {}, "
                                "which doesn't appear to be delimiter or terminator"
                            ).format(delimiter_matcher)
                        )
                else:
                    # Zero length section between delimiters, or zero code
                    # elements if appropriate. Return unmatched.
                    return MatchResult.from_unmatched(mutated_segments)
            else:
                # No match for a delimiter looking forward, this means we're
                # at the end. In this case we look for a potential partial match
                # looking forward. We know it's a non-zero length section because
                # we checked that up front.

                # First check we're had enough delimiters, because if we haven't then
                # there's no sense to try matching
                if self.min_delimiters and len(delimiters) < self.min_delimiters:
                    return MatchResult.from_unmatched(mutated_segments)
                # We use the whitespace padded match to hoover up whitespace if enabled,
                # and default to the longest matcher. We don't care which one matches.
                pre_non_code, trimmed_segments, post_non_code = trim_non_code_segments(
                    mutated_segments
                )
                # Check for whitespace gaps.
                # We do this explicitly here rather than relying on an
                # untrimmed match so we can handle _whitespace_ explicitly
                # compared to other non code segments like placeholders.
                if not self.allow_gaps and any(
                    seg.is_whitespace for seg in pre_non_code + post_non_code
                ):
                    return MatchResult.from_unmatched(
                        mutated_segments
                    )  # pragma: no cover TODO?

                with parse_context.deeper_match() as ctx:
                    mat, _ = self._longest_trimmed_match(
                        trimmed_segments,
                        self._elements,
                        parse_context=ctx,
                        # We've already trimmed
                        trim_noncode=False,
                    )

                if mat:
                    # We've got something at the end. Return!
                    if mat.unmatched_segments:
                        # We have something unmatched and so we should let it also have
                        # the trailing elements
                        return MatchResult(
                            matched_segments.matched_segments
                            + pre_non_code
                            + mat.matched_segments,
                            mat.unmatched_segments + post_non_code,
                        )
                    else:
                        # If there's nothing unmatched in the most recent match, then we
                        # can consume the trailing non code segments
                        return MatchResult.from_matched(
                            matched_segments.matched_segments
                            + pre_non_code
                            + mat.matched_segments
                            + post_non_code,
                        )
                else:
                    # No match at the end, are we allowed to trail? If we are then
                    # return, otherwise we fail because we can't match the last element.
                    if self.allow_trailing:
                        return MatchResult(matched_segments.matched_segments, seg_buff)
                    else:
                        return MatchResult.from_unmatched(mutated_segments)
