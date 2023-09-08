"""Sequence and Bracketed Grammars."""

# NOTE: We rename the typing.Sequence here so it doesn't collide
# with the grammar class that we're defining.
from os import getenv
from typing import List, Optional
from typing import Sequence as SequenceType
from typing import Set, Tuple, Union, cast

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.base import (
    BaseGrammar,
    cached_method_for_parse_context,
)
from sqlfluff.core.parser.grammar.conditional import Conditional
from sqlfluff.core.parser.helpers import check_still_complete, trim_non_code_segments
from sqlfluff.core.parser.match_algorithms import (
    bracket_sensitive_look_ahead_match,
    greedy_match,
    prune_options,
)
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.segments import (
    BaseSegment,
    BracketedSegment,
    Dedent,
    Indent,
    MetaSegment,
    UnparsableSegment,
    allow_ephemeral,
)
from sqlfluff.core.parser.types import MatchableType, ParseMode, SimpleHintType


def _trim_to_terminator(
    segments: Tuple[BaseSegment, ...],
    tail: Tuple[BaseSegment, ...],
    terminators: SequenceType[MatchableType],
    parse_context: ParseContext,
) -> Tuple[Tuple[BaseSegment, ...], Tuple[BaseSegment, ...]]:
    """Trim forward segments based on terminators.

    Given a forward set of segments, trim elements from `segments` to
    `tail` by using a `greedy_match()` to identify terminators.

    If no terminators are found, no change is made.

    NOTE: This method is designed to be used to mutate `segments` and
    `tail` and used as such:

    .. code-block:: python

        segments, tail = _trim_to_terminator(segments, tail, ...)

    """
    # In the greedy mode, we first look ahead to find a terminator
    # before matching any code.

    # NOTE: If there is a terminator _immediately_, then greedy
    # match will appear to not match (because there's "nothing" before
    # the terminator). To resolve that case, we first match immediately
    # on the terminators and handle that case explicitly if it occurs.
    with parse_context.deeper_match(name="Sequence-GreedyA-@0") as ctx:
        pruned_terms = prune_options(terminators, segments, parse_context=ctx)
        for term in pruned_terms:
            if term.match(segments, ctx):
                # One matched immediately. Claim everything to the tail.
                return (), segments + tail

    # If the above case didn't match then we proceed as expected.
    with parse_context.deeper_match(name="Sequence-GreedyB-@0") as ctx:
        term_match = greedy_match(
            segments,
            parse_context=ctx,
            matchers=terminators,
        )

    # NOTE: If there's no match, i.e. no terminator, then we continue
    # to consider all the segments, and therefore take no different
    # action at this stage.
    if term_match:
        if segments and segments[0].raw == "COMMENT":
            print(f"YES: {term_match}")
        # If we _do_ find a terminator, we separate off everything
        # beyond that terminator (and any preceding non-code) so that
        # it's not available to match against for the rest of this.
        tail = term_match.unmatched_segments
        segments = term_match.matched_segments
        for _idx in range(len(segments), -1, -1):
            if segments[_idx - 1].is_code:
                return segments[:_idx], segments[_idx:] + tail

    return segments, tail


def _position_metas(
    metas: SequenceType[Indent], non_code: SequenceType[BaseSegment]
) -> Tuple[BaseSegment, ...]:
    # First flush any metas along with the gap.
    # Elements with a negative indent value come AFTER
    # the whitespace. Positive or neutral come BEFORE.
    # HOWEVER: If one is already there, we must preserve
    # the order. This forced ordering is fine if there's
    # a positive followed by a negative in the sequence,
    # but if by design a positive arrives *after* a
    # negative then we should insert it after the positive
    # instead.
    # https://github.com/sqlfluff/sqlfluff/issues/3836
    if all(m.indent_val >= 0 for m in metas):
        return tuple((*metas, *non_code))
    else:
        return tuple((*non_code, *metas))


class Sequence(BaseGrammar):
    """Match a specific sequence of elements."""

    supported_parse_modes = {
        ParseMode.STRICT,
        ParseMode.GREEDY,
        ParseMode.GREEDY_ONCE_STARTED,
    }
    test_env = getenv("SQLFLUFF_TESTENV", "")

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a uppercase hash matching route?

        Sequence does provide this, as long as the *first* non-optional
        element does, *AND* and optional elements which preceded it also do.
        """
        simple_raws: Set[str] = set()
        simple_types: Set[str] = set()
        for opt in self._elements:
            simple = opt.simple(parse_context=parse_context, crumbs=crumbs)
            if not simple:
                return None
            simple_raws.update(simple[0])
            simple_types.update(simple[1])

            if not opt.is_optional():
                # We found our first non-optional element!
                return frozenset(simple_raws), frozenset(simple_types)
        # If *all* elements are optional AND simple, I guess it's also simple.
        return frozenset(simple_raws), frozenset(simple_types)

    @match_wrapper()
    @allow_ephemeral
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> MatchResult:
        """Match a specific sequence of elements.

        When returning incomplete matches in one of the greedy parse
        modes, we don't return any new meta segments (whether from conditionals
        or otherwise). This is because we meta segments (typically indents)
        may only make sense in the context of a full sequence, as their
        corresponding pair may be later (and yet unrendered).

        Partial matches should however still return the matched (mutated)
        versions of any segments which _have_ been processed to provide
        better feedback to the user.
        """
        matched_segments: Tuple[BaseSegment, ...] = ()
        unmatched_segments = segments
        tail: Tuple[BaseSegment, ...] = ()
        first_match = True

        if self.parse_mode == ParseMode.GREEDY:
            # In the greedy mode, we first look ahead to find a terminator
            # before matching any code.
            unmatched_segments, tail = _trim_to_terminator(
                unmatched_segments,
                tail,
                terminators=[*self.terminators, *parse_context.terminators],
                parse_context=parse_context,
            )

        # Buffers of segments, not yet added.
        meta_buffer: List[Indent] = []
        non_code_buffer: List[BaseSegment] = []

        for idx, elem in enumerate(self._elements):
            # 1. Handle any metas or conditionals.
            # We do this first so that it's the same whether we've run
            # out of segments or not.
            # If it's a conditional, evaluate it.
            # In both cases, we don't actually add them as inserts yet
            # because their position will depend on what types we accrue.
            if isinstance(elem, Conditional):
                # A conditional grammar will only ever return insertions.
                # If it's not enabled it returns an empty match.
                # NOTE: No deeper match here, it seemed unnecessary.
                _match = elem.match(unmatched_segments, parse_context)
                # We don't add them directly to the result, we buffer them
                # for later.
                # NOTE: If it's not enabled, it will be an empty tuple
                # so this code is safe regardless of whether it matches or
                # not.
                meta_buffer.extend(cast(Tuple[Indent], _match.matched_segments))
                continue
            # If it's a raw meta, just add it to our list.
            elif isinstance(elem, type) and issubclass(elem, Indent):
                meta_buffer.append(elem())
                continue

            # 2. Handle any gaps in the sequence.
            # At this point we know the next element isn't a meta or conditional
            # so if we're going to look for it we need to work up to the next
            # code element (if allowed)
            if self.allow_gaps and matched_segments:
                # First, if we're allowing gaps, consume any non-code.
                # NOTE: This won't consume from the end of a sequence
                # because this happens only in the run up to matching
                # another element. This is as designed. It also won't
                # happen at the *start* of a sequence either.
                for _idx in range(len(unmatched_segments)):
                    if unmatched_segments[_idx].is_code:
                        non_code_buffer.extend(unmatched_segments[:_idx])
                        unmatched_segments = unmatched_segments[_idx:]
                        break
                else:
                    # If _all_ of it is non code then consume all of it.
                    non_code_buffer.extend(unmatched_segments)
                    unmatched_segments = ()

            # 3. Check we still have segments left to work on.
            # Have we prematurely run out of segments?
            if not unmatched_segments:
                # If the current element is optional, carry on.
                if elem.is_optional():
                    continue
                # Otherwise we have a problem. We've already consumed
                # any metas, optionals and conditionals.
                # This is a failed match because we couldn't complete
                # the sequence.

                if self.parse_mode == ParseMode.STRICT:
                    # In a strict mode, running out a segments to match
                    # on means that we don't match anything.
                    return MatchResult.from_unmatched(segments)

                if not matched_segments:
                    # If nothing has been matched _anyway_ then just bail out.
                    return MatchResult.from_unmatched(segments)

                # On any of the other modes (GREEDY or GREEDY_ONCE_STARTED)
                # we've effectively already claimed the segments, we've
                # just failed to match. In which case it's unparsable.
                return MatchResult(
                    (
                        UnparsableSegment(
                            # NOTE: We use the already matched segments in the
                            # return value so that if any have already been
                            # matched, the user can see that.
                            matched_segments,
                            expected=(
                                f"{elem} after {matched_segments[-1]}. "
                                "Found nothing."
                            ),
                        ),
                    ),
                    # Any trailing non code isn't claimed.
                    tuple(non_code_buffer) + tail,
                )

            # 4. Match the current element against the current position.
            with parse_context.deeper_match(name=f"Sequence-@{idx}") as ctx:
                elem_match = elem.match(unmatched_segments, ctx)

            # Did we fail to match? (totally or un-cleanly)
            if not elem_match:
                # If we can't match an element, we should ascertain whether it's
                # required. If so then fine, move on, but otherwise we should
                # crash out without a match. We have not matched the sequence.
                if elem.is_optional():
                    # Pass this one and move onto the next element.
                    continue

                if self.parse_mode == ParseMode.STRICT:
                    # In a strict mode, failing to match an element means that
                    # we don't match anything.
                    return MatchResult.from_unmatched(segments)

                if (
                    self.parse_mode == ParseMode.GREEDY_ONCE_STARTED
                    and not matched_segments
                ):
                    # If it's only greedy once started, and we haven't matched
                    # anything yet, then we also don't match anything.
                    return MatchResult.from_unmatched(segments)

                # On any of the other modes (GREEDY or GREEDY_ONCE_STARTED)
                # we've effectively already claimed the segments, we've
                # just failed to match. In which case it's unparsable.
                if matched_segments:
                    _expected = (
                        f"{elem} after {matched_segments[-1]}. "
                        f"Found {elem_match.unmatched_segments[0]}"
                    )
                else:
                    _expected = (
                        f"{elem} to start sequence. "
                        f"Found {elem_match.unmatched_segments[0]}"
                    )

                return MatchResult(
                    # NOTE: We use the already matched segments in the
                    # return value so that if any have already been
                    # matched, the user can see that. Those are not
                    # part of the unparsable section.
                    matched_segments
                    + tuple(non_code_buffer)
                    + (
                        # The unparsable section is just the remaining
                        # segments we were unable to match from the
                        # sequence.
                        UnparsableSegment(
                            unmatched_segments,
                            expected=_expected,
                        ),
                    ),
                    tail,
                )

            # 5. Successful match: Update the buffers.
            # First flush any metas along with the gap.
            matched_segments += _position_metas(meta_buffer, non_code_buffer)
            non_code_buffer = []
            meta_buffer = []

            # Add on the match itself
            matched_segments += elem_match.matched_segments
            unmatched_segments = elem_match.unmatched_segments

            if first_match and self.parse_mode == ParseMode.GREEDY_ONCE_STARTED:
                # In the GREEDY_ONCE_STARTED mode, we first look ahead to find a
                # terminator after the first match (and only the first match).
                unmatched_segments, tail = _trim_to_terminator(
                    unmatched_segments,
                    tail,
                    terminators=[*self.terminators, *parse_context.terminators],
                    parse_context=parse_context,
                )
                first_match = False

        # TODO: After the main loop is when we would loop for terminators if
        # we are going to be greedy but only _after_ matching content.

        # Finally if we're in one of the greedy modes, and there's anything
        # left as unclaimed, mark it as unparsable.
        if self.parse_mode in (ParseMode.GREEDY, ParseMode.GREEDY_ONCE_STARTED):
            pre, unmatched_mid, post = trim_non_code_segments(unmatched_segments)
            if unmatched_mid:
                unparsable_seg = UnparsableSegment(
                    segments=unmatched_mid,
                    # TODO: We should come up with a better "expected" string
                    # than this
                    expected="Nothing here.",
                )
                matched_segments += _position_metas(
                    meta_buffer, tuple(non_code_buffer) + pre
                ) + (unparsable_seg,)
                unmatched_segments = ()
                meta_buffer = []
                non_code_buffer = []
                # Add the trailing non code to the tail (if it exists)
                tail = post + tail

        # If we finished on an optional, and so still have some unflushed metas,
        # we should do that first, then add any unmatched noncode back onto the
        # unmatched sequence.
        if meta_buffer:
            matched_segments += tuple(meta_buffer)
        if non_code_buffer:
            unmatched_segments = tuple(non_code_buffer) + unmatched_segments

        # If we're in a test environment, we do a sense check to make sure we
        # haven't dropped anything. (Because it's happened before!).
        if self.test_env:
            check_still_complete(
                segments,
                matched_segments,
                unmatched_segments + tail,
            )

        # If we get to here, we've matched all of the elements (or skipped them).
        # Return successfully.
        return MatchResult(
            BaseSegment._position_segments(
                matched_segments,
                # Repositioning only meta segments at this stage does increase the
                # risk of leakage a little (by not fully copying everything on
                # return), but it does drastically improve performance. Future
                # work may involve more immutable segments or a smarter way
                # of isolating them.
                metas_only=True,
            ),
            unmatched_segments + tail,
        )


class Bracketed(Sequence):
    """Match if a bracketed sequence, with content that matches one of the elements.

    Note that the contents of the Bracketed Expression are treated as an expected
    sequence.

    Changelog:
    - Post 0.3.2: Bracketed inherits from Sequence and anything within
      the the `Bracketed()` expression is treated as a sequence. For the
      content of the Brackets, we call the `match()` method of the sequence
      grammar.
    - Post 0.1.0: Bracketed was separate from sequence, and the content
      of the expression were treated as options (like OneOf).
    - Pre 0.1.0: Bracketed inherited from Sequence and simply added
      brackets to that sequence.
    """

    def __init__(
        self,
        *args: Union[MatchableType, str],
        bracket_type: str = "round",
        bracket_pairs_set: str = "bracket_pairs",
        start_bracket: Optional[MatchableType] = None,
        end_bracket: Optional[MatchableType] = None,
        allow_gaps: bool = True,
        optional: bool = False,
        ephemeral_name: Optional[str] = None,
    ) -> None:
        # Store the bracket type. NB: This is only
        # hydrated into segments at runtime.
        self.bracket_type = bracket_type
        self.bracket_pairs_set = bracket_pairs_set
        # Allow optional override for special bracket-like things
        self.start_bracket = start_bracket
        self.end_bracket = end_bracket
        super().__init__(
            *args,
            allow_gaps=allow_gaps,
            optional=optional,
            ephemeral_name=ephemeral_name,
        )

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a uppercase hash matching route?

        Bracketed does this easily, we just look for the bracket.
        """
        start_bracket, _, _ = self.get_bracket_from_dialect(parse_context)
        return start_bracket.simple(parse_context=parse_context, crumbs=crumbs)

    def get_bracket_from_dialect(
        self, parse_context: ParseContext
    ) -> Tuple[MatchableType, MatchableType, bool]:
        """Rehydrate the bracket segments in question."""
        bracket_pairs = parse_context.dialect.bracket_sets(self.bracket_pairs_set)
        for bracket_type, start_ref, end_ref, persists in bracket_pairs:
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
        """Match if a bracketed sequence, with content that matches one of the elements.

        1. work forwards to find the first bracket.
           If we find something other that whitespace, then fail out.
        2. Once we have the first bracket, we need to bracket count forward to find its
           partner.
        3. Assuming we find its partner then we try and match what goes between them
           using the match method of Sequence.
           If we match, great. If not, then we return an empty match.
           If we never find its partner then we return an empty match but should
           probably log a parsing warning, or error?

        """
        # Trim ends if allowed.
        if self.allow_gaps:
            _, seg_buff, _ = trim_non_code_segments(segments)
        else:
            seg_buff = segments  # pragma: no cover TODO?

        # Rehydrate the bracket segments in question.
        # bracket_persists controls whether we make a BracketedSegment or not.
        start_bracket, end_bracket, bracket_persists = self.get_bracket_from_dialect(
            parse_context
        )
        # Allow optional override for special bracket-like things
        start_bracket = self.start_bracket or start_bracket
        end_bracket = self.end_bracket or end_bracket

        # Are we dealing with a pre-existing BracketSegment?
        if seg_buff[0].is_type("bracketed"):
            # NOTE: We copy the original segment here because otherwise we will begin to
            # edit a _reference_ and not a copy - and that may lead to unused matches
            # leaking out. https://github.com/sqlfluff/sqlfluff/issues/3277
            seg: BracketedSegment = cast(BracketedSegment, seg_buff[0].copy())
            # Check it's of the right kind of bracket
            if not start_bracket.match(seg.start_bracket, parse_context):
                # Doesn't match - return no match
                return MatchResult.from_unmatched(segments)

            content_segs = seg.segments[len(seg.start_bracket) : -len(seg.end_bracket)]
            bracket_segment = seg
            trailing_segments = seg_buff[1:]
        # Otherwise try and match the segments directly.
        else:
            # Look for the first bracket
            with parse_context.deeper_match(name="Bracketed-First") as ctx:
                start_match = start_bracket.match(seg_buff, ctx)
            if start_match:
                seg_buff = start_match.unmatched_segments
            else:
                # Can't find the opening bracket. No Match.
                return MatchResult.from_unmatched(segments)

            # Look for the closing bracket.
            # Within the brackets, clear any inherited terminators.
            with parse_context.deeper_match(
                name="Bracketed-End", clear_terminators=True
            ) as ctx:
                content_segs, end_match, _ = bracket_sensitive_look_ahead_match(
                    segments=seg_buff,
                    matchers=[end_bracket],
                    parse_context=ctx,
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
                start_bracket=cast(Tuple[BaseSegment], start_match.matched_segments),
                end_bracket=cast(Tuple[BaseSegment], end_match.matched_segments),
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

        # Match the content using super. Sequence will interpret the content of the
        # elements. Within the brackets, clear any inherited terminators.
        with parse_context.deeper_match(
            name="Bracketed", clear_terminators=True
        ) as ctx:
            content_match = super().match(content_segs, ctx)

        # We require a complete match for the content (hopefully for obvious reasons)
        if not content_match.is_complete():
            # No complete match. Fail.
            return MatchResult.from_unmatched(segments)

        # Reconstruct the bracket segment post match.
        # We need to realign the meta segments so the pos markers are correct.
        # Have we already got indents?
        meta_idx = None
        for idx, _seg in enumerate(bracket_segment.segments):
            if _seg.is_meta:
                _meta_seg = cast(MetaSegment, _seg)
                if _meta_seg.indent_val > 0 and not _meta_seg.is_template:
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
