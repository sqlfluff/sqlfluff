"""Sequence and Bracketed Grammars."""

from typing import Optional, List, Tuple

from ...errors import SQLParseError

from ..segments import BaseSegment, Indent, Dedent
from ..helpers import trim_non_code_segments, check_still_complete
from ..match_result import MatchResult
from ..match_wrapper import match_wrapper
from ..context import ParseContext

from .base import BaseGrammar, Ref, cached_method_for_parse_context


class Sequence(BaseGrammar):
    """Match a specific sequence of elements."""

    @cached_method_for_parse_context
    def simple(self, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        Sequence does provide this, as long as the *first* non-optional
        element does, *AND* and optional elements which preceed it also do.
        """
        simple_buff = []
        for opt in self._elements:
            simple = opt.simple(parse_context=parse_context)
            if not simple:
                return None
            simple_buff += simple

            if not opt.is_optional():
                # We found our first non-optional element!
                return simple_buff
        # If *all* elements are optional AND simple, I guess it's also simple.
        return simple_buff

    @match_wrapper()
    def match(self, segments, parse_context):
        """Match a specific sequence of elements."""
        if isinstance(segments, BaseSegment):
            segments = tuple(segments)

        matched_segments = MatchResult.from_empty()
        unmatched_segments = segments

        for idx, elem in enumerate(self._elements):
            while True:
                # Is it an indent or dedent?
                if elem.is_meta:
                    # Is it actually enabled?
                    if not elem.is_enabled(parse_context=parse_context):
                        break
                    # Work out how to find an appropriate pos_marker for
                    # the meta segment.
                    if matched_segments:
                        # Get from end of last
                        last_matched = matched_segments.matched_segments[-1]
                        meta_pos_marker = last_matched.get_end_pos_marker()
                    else:
                        # Get from start of next
                        meta_pos_marker = unmatched_segments[0].pos_marker
                    matched_segments += elem(pos_marker=meta_pos_marker)
                    break

                # Consume non-code if appropriate
                if self.allow_gaps:
                    pre_nc, mid_seg, post_nc = trim_non_code_segments(
                        unmatched_segments
                    )
                else:
                    pre_nc = ()
                    mid_seg = unmatched_segments
                    post_nc = ()

                if len(pre_nc + mid_seg + post_nc) == 0:
                    # We've run our of sequence without matching everyting.
                    # Do only optional or meta elements remain?
                    if all(e.is_optional() or e.is_meta for e in self._elements[idx:]):
                        # then it's ok, and we can return what we've got so far.
                        # No need to deal with anything left over because we're at the end,
                        # unless it's a meta segment.

                        # Get hold of the last thing to be matched, so we've got an anchor.
                        last_matched = matched_segments.matched_segments[-1]
                        meta_pos_marker = last_matched.get_end_pos_marker()
                        # NB: This complicated expression just adds indents as appropriate.
                        return matched_segments + tuple(
                            e(pos_marker=meta_pos_marker)
                            for e in self._elements[idx:]
                            if e.is_meta and e.is_enabled(parse_context=parse_context)
                        )
                    else:
                        # we've got to the end of the sequence without matching all
                        # required elements.
                        return MatchResult.from_unmatched(segments)
                else:
                    # We've already dealt with potential whitespace above, so carry on to matching
                    with parse_context.deeper_match() as ctx:
                        elem_match = elem.match(mid_seg, parse_context=ctx)

                    if elem_match.has_match():
                        # We're expecting mostly partial matches here, but complete
                        # matches are possible. Don't be greedy with whitespace!
                        matched_segments += pre_nc + elem_match.matched_segments
                        unmatched_segments = elem_match.unmatched_segments + post_nc
                        # Each time we do this, we do a sense check to make sure we haven't
                        # dropped anything. (Because it's happened before!).
                        check_still_complete(
                            segments,
                            matched_segments.matched_segments,
                            unmatched_segments,
                        )

                        # Break out of the while loop and move to the next element.
                        break
                    else:
                        # If we can't match an element, we should ascertain whether it's
                        # required. If so then fine, move on, but otherwise we should crash
                        # out without a match. We have not matched the sequence.
                        if elem.is_optional():
                            # This will crash us out of the while loop and move us
                            # onto the next matching element
                            break
                        else:
                            return MatchResult.from_unmatched(segments)

        # If we get to here, we've matched all of the elements (or skipped them)
        # but still have some segments left (or perhaps have precisely zero left).
        # In either case, we're golden. Return successfully, with any leftovers as
        # the unmatched elements.
        return MatchResult(matched_segments.matched_segments, unmatched_segments)


class Bracketed(Sequence):
    """Match if this is a bracketed sequence, with content that matches one of the elements.

    Note that the contents of the Bracketed Expression are treated as an expected sequence.

    Changelog:
    - Post 0.3.2: Bracketed inherits from Sequence and anything within
      the the `Bracketed()` expression is treated as a sequence. For the
      content of the Brackets, we call the `match()` method of the sequence
      grammar.
    - Post 0.1.0: Bracketed was seperate from sequence, and the content
      of the expression were treated as options (like OneOf).
    - Pre 0.1.0: Bracketed inherited from Sequence and simply added
      brackets to that sequence,

    """

    def __init__(self, *args, **kwargs):
        self.square = kwargs.pop("square", False)
        # Start and end tokens
        # The details on how to match a bracket are stored in the dialect
        if self.square:
            self.start_bracket = Ref("StartSquareBracketSegment")
            self.end_bracket = Ref("EndSquareBracketSegment")
        else:
            self.start_bracket = Ref("StartBracketSegment")
            self.end_bracket = Ref("EndBracketSegment")
        super(Bracketed, self).__init__(*args, **kwargs)

    @cached_method_for_parse_context
    def simple(self, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        Bracketed does this easily, we just look for the bracket.
        """
        return self.start_bracket.simple(parse_context=parse_context)

    @match_wrapper()
    def match(
        self, segments: Tuple["BaseSegment", ...], parse_context: ParseContext
    ) -> MatchResult:
        """Match if this is a bracketed sequence, with content that matches one of the elements.

        1. work forwards to find the first bracket.
           If we find something other that whitespace, then fail out.
        2. Once we have the first bracket, we need to bracket count forward to find it's partner.
        3. Assuming we find it's partner then we try and match what goes between them
           using the match method of Sequence.
           If we match, great. If not, then we return an empty match.
           If we never find it's partner then we return an empty match but should probably
           log a parsing warning, or error?

        """
        # Trim ends if allowed.
        if self.allow_gaps:
            pre_nc, seg_buff, post_nc = trim_non_code_segments(segments)
        else:
            seg_buff = segments

        # Look for the first bracket
        with parse_context.deeper_match() as ctx:
            start_match = self.start_bracket.match(seg_buff, parse_context=ctx)
        if start_match:
            seg_buff = start_match.unmatched_segments
        else:
            # Can't find the opening bracket. No Match.
            return MatchResult.from_unmatched(segments)

        # Look for the closing bracket
        content_segs, end_match, _ = self._bracket_sensitive_look_ahead_match(
            segments=seg_buff,
            matchers=[self.end_bracket],
            parse_context=parse_context,
        )
        if not end_match:
            raise SQLParseError(
                "Couldn't find closing bracket for opening bracket.",
                segment=start_match.matched_segments[0],
            )

        # Match the content now we've confirmed the brackets.

        # First deal with the case of TOTALLY EMPTY BRACKETS e.g. "()"
        if not content_segs:
            # If it's allowed, return a match.
            if not self._elements or all(e.is_optional() for e in self._elements):
                return MatchResult(
                    start_match.matched_segments + end_match.matched_segments,
                    end_match.unmatched_segments,
                )
            # If not, don't.
            else:
                return MatchResult.from_unmatched(segments)

        # Then trim whitespace and deal with the case of no code content e.g. "(   )"
        if self.allow_gaps:
            pre_nc, content_segs, post_nc = trim_non_code_segments(content_segs)
        else:
            pre_nc = ()
            post_nc = ()

        # If we don't have anything left after trimming, act accordingly.
        if not content_segs:
            if not self._elements or (
                all(e.is_optional() for e in self._elements) and self.allow_gaps
            ):
                return MatchResult(
                    start_match.matched_segments
                    + pre_nc
                    + post_nc
                    + end_match.matched_segments,
                    end_match.unmatched_segments,
                )
            else:
                return MatchResult.from_unmatched(segments)

        # Match using super. Sequence will interpret the content of the elements.
        with parse_context.deeper_match() as ctx:
            content_match = super().match(content_segs, parse_context=ctx)

        # We require a complete match for the content (hopefully for obvious reasons)
        if content_match.is_complete():
            # Append some indent and dedent tokens at the start and the end.
            pre_meta = (
                Indent(
                    pos_marker=content_match.matched_segments[0].get_start_pos_marker()
                ),
            )
            post_meta = (
                Dedent(
                    pos_marker=content_match.matched_segments[-1].get_end_pos_marker()
                ),
            )
            return MatchResult(
                # NB: The nc segments go *outside* the indents.
                start_match.matched_segments
                + pre_nc
                + pre_meta  # Add a meta indent here
                + content_match.matched_segments
                + post_meta  # Add a meta indent here
                + post_nc
                + end_match.matched_segments,
                end_match.unmatched_segments,
            )
        # No complete match. Fail.
        else:
            return MatchResult.from_unmatched(segments)
