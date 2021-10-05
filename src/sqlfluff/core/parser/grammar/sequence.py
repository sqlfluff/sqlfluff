"""Sequence and Bracketed Grammars."""

from typing import Optional, List, Tuple, cast

from sqlfluff.core.errors import SQLParseError

from sqlfluff.core.parser.segments import (
    BaseSegment,
    Indent,
    Dedent,
    allow_ephemeral,
    BracketedSegment,
    MetaSegment,
)
from sqlfluff.core.parser.helpers import trim_non_code_segments, check_still_complete
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.base import (
    BaseGrammar,
    cached_method_for_parse_context,
)
from sqlfluff.core.parser.grammar.conditional import Conditional


class Sequence(BaseGrammar):
    """Match a specific sequence of elements."""

    @cached_method_for_parse_context
    def simple(self, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        Sequence does provide this, as long as the *first* non-optional
        element does, *AND* and optional elements which preceded it also do.
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
    @allow_ephemeral
    def match(self, segments, parse_context):
        """Match a specific sequence of elements."""
        if isinstance(segments, BaseSegment):
            segments = tuple(segments)  # pragma: no cover TODO?

        matched_segments = MatchResult.from_empty()
        unmatched_segments = segments

        # Buffers of uninstantiated meta segments.
        meta_pre_nc = ()
        meta_post_nc = ()
        early_break = False

        for idx, elem in enumerate(self._elements):
            # Check for an early break.
            if early_break:
                break

            while True:
                # Consume non-code if appropriate
                if self.allow_gaps:
                    pre_nc, mid_seg, post_nc = trim_non_code_segments(
                        unmatched_segments
                    )
                else:
                    pre_nc = ()
                    mid_seg = unmatched_segments
                    post_nc = ()

                # Is it an indent or dedent?
                if elem.is_meta:
                    # Elements with a negative indent value come AFTER
                    # the whitespace. Positive or neutral come BEFORE.
                    if elem.indent_val < 0:
                        meta_post_nc += (elem(),)
                    else:
                        meta_pre_nc += (elem(),)
                    break

                # Is it a conditional? If so is it active
                if isinstance(elem, Conditional) and not elem.is_enabled(parse_context):
                    # If it's not active, skip it.
                    break

                if len(pre_nc + mid_seg + post_nc) == 0:
                    # We've run our of sequence without matching everything.
                    # Do only optional or meta elements remain?
                    if all(
                        e.is_optional() or e.is_meta or isinstance(e, Conditional)
                        for e in self._elements[idx:]
                    ):
                        # then it's ok, and we can return what we've got so far.
                        # No need to deal with anything left over because we're at the end,
                        # unless it's a meta segment.

                        # We'll add those meta segments after any existing ones. So
                        # the go on the meta_post_nc stack.
                        for e in self._elements[idx:]:
                            # If it's meta, instantiate it.
                            if e.is_meta:
                                meta_post_nc += (e(),)  # pragma: no cover TODO?
                            # If it's conditional and it's enabled, match it.
                            if isinstance(e, Conditional) and e.is_enabled(
                                parse_context
                            ):
                                meta_match = e.match(tuple(), parse_context)
                                if meta_match:
                                    meta_post_nc += meta_match.matched_segments

                        # Early break to exit via the happy match path.
                        early_break = True
                        break
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
                        matched_segments += (
                            meta_pre_nc
                            + pre_nc
                            + meta_post_nc
                            + elem_match.matched_segments
                        )
                        meta_pre_nc = ()
                        meta_post_nc = ()
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
        # the unmatched elements. Meta all go at the end regardless of wny trailing
        # whitespace.
        return MatchResult(
            BaseSegment._position_segments(
                matched_segments.matched_segments + meta_pre_nc + meta_post_nc,
            ),
            unmatched_segments,
        )


class Bracketed(Sequence):
    """Match if this is a bracketed sequence, with content that matches one of the elements.

    Note that the contents of the Bracketed Expression are treated as an expected sequence.

    Changelog:
    - Post 0.3.2: Bracketed inherits from Sequence and anything within
      the the `Bracketed()` expression is treated as a sequence. For the
      content of the Brackets, we call the `match()` method of the sequence
      grammar.
    - Post 0.1.0: Bracketed was separate from sequence, and the content
      of the expression were treated as options (like OneOf).
    - Pre 0.1.0: Bracketed inherited from Sequence and simply added
      brackets to that sequence,

    """

    def __init__(self, *args, **kwargs):
        # Store the bracket type. NB: This is only
        # hydrated into segments at runtime.
        self.bracket_type = kwargs.pop("bracket_type", "round")
        self.bracket_pairs_set = kwargs.pop("bracket_pairs_set", "bracket_pairs")
        # Allow optional override for special bracket-like things
        self.start_bracket = kwargs.pop("start_bracket", None)
        self.end_bracket = kwargs.pop("end_bracket", None)
        super().__init__(*args, **kwargs)

    @cached_method_for_parse_context
    def simple(self, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        Bracketed does this easily, we just look for the bracket.
        """
        start_bracket, _, _ = self.get_bracket_from_dialect(parse_context)
        return start_bracket.simple(parse_context=parse_context)

    def get_bracket_from_dialect(self, parse_context):
        """Rehydrate the bracket segments in question."""
        for bracket_type, start_ref, end_ref, persists in parse_context.dialect.sets(
            self.bracket_pairs_set
        ):
            if bracket_type == self.bracket_type:
                start_bracket = parse_context.dialect.ref(start_ref)
                end_bracket = parse_context.dialect.ref(end_ref)
                break
        else:  # pragma: no cover
            raise ValueError(
                "bracket_type {!r} not found in bracket_pairs of {!r} dialect.".format(
                    self.bracket_type, parse_context.dialect.name
                )
            )
        return start_bracket, end_bracket, persists

    @match_wrapper()
    @allow_ephemeral
    def match(
        self, segments: Tuple["BaseSegment", ...], parse_context: ParseContext
    ) -> MatchResult:
        """Match if this is a bracketed sequence, with content that matches one of the elements.

        1. work forwards to find the first bracket.
           If we find something other that whitespace, then fail out.
        2. Once we have the first bracket, we need to bracket count forward to find its partner.
        3. Assuming we find its partner then we try and match what goes between them
           using the match method of Sequence.
           If we match, great. If not, then we return an empty match.
           If we never find its partner then we return an empty match but should probably
           log a parsing warning, or error?

        """
        # Trim ends if allowed.
        if self.allow_gaps:
            pre_nc, seg_buff, post_nc = trim_non_code_segments(segments)
        else:
            seg_buff = segments  # pragma: no cover TODO?

        # Rehydrate the bracket segments in question.
        # bracket_persits controls whether we make a BracketedSegment or not.
        start_bracket, end_bracket, bracket_persists = self.get_bracket_from_dialect(
            parse_context
        )
        # Allow optional override for special bracket-like things
        start_bracket = self.start_bracket or start_bracket
        end_bracket = self.end_bracket or end_bracket

        # Are we dealing with a pre-existing BracketSegment?
        if seg_buff[0].is_type("bracketed"):
            seg: BracketedSegment = cast(BracketedSegment, seg_buff[0])
            content_segs = seg.segments[len(seg.start_bracket) : -len(seg.end_bracket)]
            bracket_segment = seg
            trailing_segments = seg_buff[1:]
        # Otherwise try and match the segments directly.
        else:
            # Look for the first bracket
            with parse_context.deeper_match() as ctx:
                start_match = start_bracket.match(seg_buff, parse_context=ctx)
            if start_match:
                seg_buff = start_match.unmatched_segments
            else:
                # Can't find the opening bracket. No Match.
                return MatchResult.from_unmatched(segments)

            # Look for the closing bracket
            content_segs, end_match, _ = self._bracket_sensitive_look_ahead_match(
                segments=seg_buff,
                matchers=[end_bracket],
                parse_context=parse_context,
                start_bracket=start_bracket,
                end_bracket=end_bracket,
                bracket_pairs_set=self.bracket_pairs_set,
            )
            if not end_match:  # pragma: no cover
                raise SQLParseError(
                    "Couldn't find closing bracket for opening bracket.",
                    segment=start_match.matched_segments[0],
                )

            # Construct a bracket segment
            bracket_segment = BracketedSegment(
                segments=(
                    start_match.matched_segments
                    + content_segs
                    + end_match.matched_segments
                ),
                start_bracket=start_match.matched_segments,
                end_bracket=end_match.matched_segments,
            )
            trailing_segments = end_match.unmatched_segments

        # Then trim whitespace and deal with the case of non-code content e.g. "(   )"
        if self.allow_gaps:
            pre_segs, content_segs, post_segs = trim_non_code_segments(content_segs)
        else:  # pragma: no cover TODO?
            pre_segs = ()
            post_segs = ()

        # If we've got a case of empty brackets check whether that is allowed.
        if not content_segs:
            if not self._elements or (
                all(e.is_optional() for e in self._elements)
                and (self.allow_gaps or (not pre_segs and not post_segs))
            ):
                return MatchResult(
                    (bracket_segment,)
                    if bracket_persists
                    else bracket_segment.segments,
                    trailing_segments,
                )
            else:
                return MatchResult.from_unmatched(segments)

        # Match the content using super. Sequence will interpret the content of the elements.
        with parse_context.deeper_match() as ctx:
            content_match = super().match(content_segs, parse_context=ctx)

        # We require a complete match for the content (hopefully for obvious reasons)
        if content_match.is_complete():
            # Reconstruct the bracket segment post match.
            # We need to realign the meta segments so the pos markers are correct.
            # Have we already got indents?
            meta_idx = None
            for idx, seg in enumerate(bracket_segment.segments):
                if seg.is_meta and cast(MetaSegment, seg).indent_val > 0:
                    meta_idx = idx
                    break
            # If we've already got indents, don't add more.
            if meta_idx:
                bracket_segment.segments = BaseSegment._position_segments(
                    bracket_segment.start_bracket
                    + pre_segs
                    + content_match.all_segments()
                    + post_segs
                    + bracket_segment.end_bracket
                )
            # Append some indent and dedent tokens at the start and the end.
            else:
                bracket_segment.segments = BaseSegment._position_segments(
                    # NB: The nc segments go *outside* the indents.
                    bracket_segment.start_bracket
                    + (Indent(),)  # Add a meta indent here
                    + pre_segs
                    + content_match.all_segments()
                    + post_segs
                    + (Dedent(),)  # Add a meta indent here
                    + bracket_segment.end_bracket
                )
            return MatchResult(
                (bracket_segment,) if bracket_persists else bracket_segment.segments,
                trailing_segments,
            )
        # No complete match. Fail.
        else:
            return MatchResult.from_unmatched(segments)
