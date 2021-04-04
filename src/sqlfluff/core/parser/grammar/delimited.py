"""Definitions for Grammar."""

from typing import Tuple, List

from sqlfluff.core.parser.grammar import Ref
from sqlfluff.core.parser.segments import BaseSegment
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
        if delimiter is None:
            raise ValueError("Delimited grammars require a `delimiter`")
        self.delimiter = self._resolve_ref(delimiter)
        self.allow_trailing = allow_trailing
        self.terminator = self._resolve_ref(terminator)
        # Setting min delimiters means we have to match at least this number
        self.min_delimiters = min_delimiters
        super().__init__(*args, **kwargs)

    @match_wrapper()
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
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

        # First iterate through all the segments, looking for the delimiter.
        # Second, split the list on each of the delimiters, and ensure that
        # each sublist in turn matches one of the elements.

        # In more detail, match against delimiter, if we match, put a slice
        # up to that point onto a list of slices. Carry on.
        while True:
            # Check to see whether we've exhausted the buffer, either by iterating through it,
            # or by consuming all the non-code segments already.
            # NB: If we're here then we've already tried matching the remaining segments against
            # the content, so we must be in a trailing case.
            if len(seg_buff) == 0:
                # Append the remaining buffer in case we're in the not is_code case.
                matched_segments += seg_buff
                # Nothing left, this is potentially a trailing case?
                if self.allow_trailing and (
                    self.min_delimiters is None
                    or len(delimiters) >= self.min_delimiters
                ):
                    # It is! (nothing left so no unmatched segments to append)
                    return MatchResult.from_matched(matched_segments.matched_segments)
                else:
                    return MatchResult.from_unmatched(segments)

            # We rely on _bracket_sensitive_look_ahead_match to do the bracket counting
            # element of this now. We look ahead to find a delimiter or terminator.
            matchers = [self.delimiter]
            if self.terminator:
                matchers.append(self.terminator)
            # If gaps aren't allowed, a gap (or non-code segment), acts like a terminator.
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
                )
            # Keep track of the *length* of this pre-content section before we start
            # to change it later. We need this for dealing with terminators.
            pre_content_len = len(pre_content)

            # Have we found a delimiter or terminator looking forward?
            if delimiter_match:
                if delimiter_matcher is self.delimiter:
                    # Yes. Store it and then match the contents up to now.
                    delimiters.append(delimiter_match.matched_segments)

                # We now test the intervening section as to whether it matches one
                # of the things we're looking for. NB: If it's of zero length then
                # we return without trying it.
                if len(pre_content) > 0:
                    with parse_context.deeper_match() as ctx:
                        match, matcher = self._longest_trimmed_match(
                            segments=pre_content,
                            matchers=self._elements,
                            parse_context=ctx,
                            trim_noncode=self.allow_gaps,
                        )

                    # No match, or an incomplete match: Not allowed
                    if not match or not match.is_complete():
                        return MatchResult.from_unmatched(segments)

                    # We have a complete match!

                    # First add the segment up to the delimiter to the matched segments
                    matched_segments += match.matched_segments
                    # Then it depends what we matched.
                    # Delimiter
                    if delimiter_matcher is self.delimiter:
                        # Then add the delimiter to the matched segments
                        matched_segments += delimiter_match.matched_segments
                        # Break this for loop and move on, looking for the next delimiter
                        seg_buff = delimiter_match.unmatched_segments
                        # Still got some buffer left. Carry on.
                        continue
                    # Terminator (or the gap terminator).
                    elif delimiter_matcher is self.terminator or isinstance(
                        delimiter_matcher, NonCodeMatcher
                    ):
                        # We just return straight away here. We don't add the terminator to
                        # this match, it should go with the unmatched parts. The terminator
                        # may also have mutated the returned segments so we also DON'T want
                        # the mutated version, it can do that itself (so we return `seg_buff`
                        # and not `delimiter_match.all_segments()``)

                        # First check we've had enough delimiters
                        if (
                            self.min_delimiters
                            and len(delimiters) < self.min_delimiters
                        ):
                            return MatchResult.from_unmatched(segments)
                        else:
                            return MatchResult(
                                matched_segments.matched_segments,
                                # Return the part of the seg_buff which isn't in the
                                # pre-content.
                                seg_buff[pre_content_len:],
                            )
                    else:
                        raise RuntimeError(
                            (
                                "I don't know how I got here. Matched instead on {0}, which "
                                "doesn't appear to be delimiter or terminator"
                            ).format(delimiter_matcher)
                        )
                else:
                    # Zero length section between delimiters, or zero code
                    # elements if appropriate. Return unmatched.
                    return MatchResult.from_unmatched(segments)
            else:
                # No match for a delimiter looking forward, this means we're
                # at the end. In this case we look for a potential partial match
                # looking forward. We know it's a non-zero length section because
                # we checked that up front.

                # First check we're had enough delimiters, because if we haven't then
                # there's no sense to try matching
                if self.min_delimiters and len(delimiters) < self.min_delimiters:
                    return MatchResult.from_unmatched(segments)

                # We use the whitespace padded match to hoover up whitespace if enabled,
                # and default to the longest matcher. We don't care which one matches.
                with parse_context.deeper_match() as ctx:
                    mat, _ = self._longest_trimmed_match(
                        seg_buff,
                        self._elements,
                        parse_context=ctx,
                        trim_noncode=self.allow_gaps,
                    )
                if mat:
                    # We've got something at the end. Return!
                    if mat.unmatched_segments:
                        # We have something unmatched and so we should let it also have the trailing elements
                        return MatchResult(
                            matched_segments.matched_segments + mat.matched_segments,
                            mat.unmatched_segments,
                        )
                    else:
                        # If there's nothing unmatched in the most recent match, then we can consume the trailing
                        # non code segments
                        return MatchResult.from_matched(
                            matched_segments.matched_segments + mat.matched_segments,
                        )
                else:
                    # No match at the end, are we allowed to trail? If we are then return,
                    # otherwise we fail because we can't match the last element.
                    if self.allow_trailing:
                        return MatchResult(matched_segments.matched_segments, seg_buff)
                    else:
                        return MatchResult.from_unmatched(segments)
