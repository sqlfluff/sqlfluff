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
    next_ex_bracket_match2,
    prune_options,
    resolve_bracket2,
)
from sqlfluff.core.parser.match_result import MatchResult, MatchResult2
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.segments import (
    BaseSegment,
    BracketedSegment,
    Dedent,
    Indent,
    UnparsableSegment,
)
from sqlfluff.core.parser.types import MatchableType, ParseMode, SimpleHintType
from sqlfluff.core.slice_helpers import slice_length


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
    with parse_context.deeper_match(
        name="Sequence-GreedyB-@0", track_progress=False
    ) as ctx:
        term_match = greedy_match(
            segments,
            parse_context=ctx,
            matchers=terminators,
        )

    # NOTE: If there's no match, i.e. no terminator, then we continue
    # to consider all the segments, and therefore take no different
    # action at this stage.
    if term_match:
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


def _flush_metas(pre_nc_idx, post_nc_idx, meta_buffer):
    # Flush any metas...
    if all(m.indent_val >= 0 for m in meta_buffer):
        meta_idx = pre_nc_idx
    else:
        meta_idx = post_nc_idx
    return tuple((meta_idx, meta) for meta in meta_buffer)


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
            parse_context.update_progress(matched_segments)

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
        # NOTE: This adds an overhead to do on _every_ sequence match so we
        # only do it here within the test environment.
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

    def match2(
        self,
        segments: SequenceType["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult2:
        """Match against this Sequence.

        In the match2 regime, the Sequence matcher behaves a little differently.
        Importantly when we make a *partial* sequence match, we *still return*,
        it's just that we set the `is_clean` flag to false. This indicates the
        furthest that we got.

        TODO: At some point in the future we might also want to extend this to
        include some kind of hint on what we _expected_ to find instead.
        """
        start_idx = idx  # Where did we start
        matched_idx = idx  # Where have we got to
        max_idx = len(segments)  # What is the limit
        insert_segments = ()
        child_matches = ()
        # Metas with a negative indent value come AFTER
        # the whitespace. Positive or neutral come BEFORE.
        # HOWEVER: If one is already there, we must preserve
        # the order. This forced ordering is fine if there's
        # a positive followed by a negative in the sequence,
        # but if by design a positive arrives *after* a
        # negative then we should insert it after the positive
        # instead.
        # https://github.com/sqlfluff/sqlfluff/issues/3836
        meta_buffer = []

        # Iterate elements
        for elem in self._elements:
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
                _match = elem.match2(segments, matched_idx, parse_context)
                # Rather than taking them as a match at this location, we
                # requeue them for addition later.
                for _, submatch in _match.insert_segments:
                    meta_buffer.append(submatch)
                continue
            # If it's a raw meta, just add it to our list.
            elif isinstance(elem, type) and issubclass(elem, Indent):
                meta_buffer.append(elem)
                continue

            # 2. Match Segments.
            # At this point we know there are segments left to match
            # on and that the current element isn't a meta or conditional.
            _idx = matched_idx
            # TODO: Need test cases to cover overmatching non code properly
            # especially around optional elements.
            if self.allow_gaps:
                # First, if we're allowing gaps, consume any non-code.
                # NOTE: This won't consume from the end of a sequence
                # because this happens only in the run up to matching
                # another element. This is as designed.
                for _idx in range(matched_idx, max_idx):
                    if segments[_idx].is_code:
                        break

            # Have we prematurely run out of segments?
            if _idx >= max_idx:
                # If the current element is optional, carry on.
                if elem.is_optional():
                    continue
                # Otherwise we have a problem. We've already consumed
                # any metas, optionals and conditionals.
                # This is a failed match because we couldn't complete
                # the sequence.
                # To facilitate later logging of unparsable sections
                # we still return a match object, but mark is as unclean
                # so that it isn't prioritised.
                # Flush any metas...
                insert_segments += tuple((matched_idx, meta) for meta in meta_buffer)
                return MatchResult2(
                    matched_slice=slice(start_idx, matched_idx),
                    insert_segments=insert_segments,
                    child_matches=child_matches,
                    is_clean=False,
                )

            # TODO: Check for terminators here, but my first pass didn't help.

            # Match the current element against the current position.
            with parse_context.deeper_match(name=f"Sequence-@{idx}") as ctx:
                elem_match = elem.match2(segments, _idx, ctx)

            # print(f"ELEM MATCH:\n{parse_context.stack()[1]}\n{elem_match}")
            # Did we fail to match? (totally or un-cleanly)
            if not elem_match:
                # If we can't match an element, we should ascertain whether it's
                # required. If so then fine, move on, but otherwise we should
                # crash out without a match. We have not matched the sequence.
                if elem.is_optional():
                    # Pass this one and move onto the next element.
                    continue

                # Otherwise we've failed to match the sequence. In this case
                # we return a _partial_ match (i.e. an unclean one). We'll also
                # use any unclean elements of the existing match to enrich that.

                # In the case that we don't have any existing matches, we can
                # just return the inner unclean match. This stops unnecessary
                # nesting.
                # NOTE: This is also the most likely return path, as it's where
                # we go when we fail to match the first element of a sequence.
                # In that case we just pass the match straight through.
                if (
                    not insert_segments
                    and not child_matches
                    and start_idx == elem_match.matched_slice.start
                ):
                    return elem_match

                # If the child match has a size (i.e. it matched *some* segments)
                # then add it as a child and update out position before returning.
                if slice_length(elem_match.matched_slice):
                    # We should be able to rely on it being an unclean match at
                    # this stage.
                    assert not elem_match.is_clean
                    child_matches += (elem_match,)
                    matched_idx = elem_match.matched_slice.stop
                return MatchResult2(
                    matched_slice=slice(start_idx, matched_idx),
                    insert_segments=insert_segments,
                    child_matches=child_matches,
                    is_clean=False,
                )

            # Flush any metas...
            insert_segments += _flush_metas(matched_idx, _idx, meta_buffer)
            meta_buffer = []

            # Otherwise we _do_ have a match. Update the position.
            matched_idx = elem_match.matched_slice.stop
            # How we deal with child segments depends on whether it had a matched
            # class or not.
            # If it did, then just add it as a child match and we're done. Move on.
            if elem_match.matched_class:
                child_matches += (elem_match,)
                continue
            # Otherwise, we un-nest the returned structure, adding any inserts and
            # children into the inserts and children of this sequence.
            child_matches += elem_match.child_matches
            insert_segments += elem_match.insert_segments

        # If we get to here, we've matched all of the elements (or skipped them).
        insert_segments += tuple((matched_idx, meta) for meta in meta_buffer)
        # Return successfully.
        return MatchResult2(
            matched_slice=slice(start_idx, matched_idx),
            insert_segments=insert_segments,
            child_matches=child_matches,
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
        parse_mode: ParseMode = ParseMode.STRICT,
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
            parse_mode=parse_mode,
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
        # If we've already got indents, don't add more (we only need to check
        # the initial non-code section).
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

    def match2(
        self,
        segments: SequenceType["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult2:
        """Match against this matcher."""
        # NOTE: THIS IS A GREAT PLACE FOR PARTIAL UNPARSABLES.
        # TODO: Deal with unparsables.
        # First deal with the negative case. No start, no match.

        # Rehydrate the bracket segments in question.
        # bracket_persists controls whether we make a BracketedSegment or not.
        start_bracket, end_bracket, _ = self.get_bracket_from_dialect(parse_context)
        # Allow optional override for special bracket-like things
        start_bracket = self.start_bracket or start_bracket
        end_bracket = self.end_bracket or end_bracket

        # Are we dealing with a pre-existing BracketSegment?
        if segments[idx].is_type("bracketed"):
            # This feels a little risky to assume that the content is necessarily
            # the same. TODO: Revisit whether this is too bullish.
            return MatchResult2(matched_slice=slice(idx, idx + 1))

        # Otherwise try and match the segments directly.
        # Look for the first bracket
        with parse_context.deeper_match(name="Bracketed-Start") as ctx:
            start_match = start_bracket.match2(segments, idx, ctx)

        if not start_match:
            # Can't find the opening bracket. No Match.
            return MatchResult2.empty_at(idx)

        # NOTE: Ideally we'd match on the _content_ next, providing we were sure
        # we wouldn't hit the end. But it appears the terminator logic isn't
        # robust enough for that yet. Until then, we _first_ look for the closing
        # bracket and _then_ match on the inner content.
        bracket_match = resolve_bracket2(
            segments,
            opening_match=start_match,
            opening_matcher=start_bracket,
            start_brackets=[start_bracket],
            end_brackets=[end_bracket],
            parse_context=parse_context,
        )

        if not bracket_match:
            raise NotImplementedError(
                f"BRACKETED. WE'RE GOING TO NEED THIS. CASE 5 {bracket_match}"
            )

        # Work forward through any gaps at the start and end.
        # NOTE: We assume that all brackets are single segment.
        _idx = start_match.matched_slice.stop
        _end_idx = bracket_match.matched_slice.stop - 1
        if self.allow_gaps:
            for _idx in range(_idx, len(segments)):
                if segments[_idx].is_code:
                    break
            for _end_idx in range(_end_idx, _idx, -1):
                if segments[_end_idx - 1].is_code:
                    break

        # Try and match content, clearing and adding the closing bracket
        # to the terminators.
        with parse_context.deeper_match(
            name="Bracketed", clear_terminators=True, push_terminators=[end_bracket]
        ) as ctx:
            # NOTE: This slice is a bit of a hack, but it's the only
            # reliable way so far to make sure we don't "over match" when
            # presented with a potential terminating bracket.
            # TODO: MAKE THIS BETTER. GET RID OF THE HACK.
            content_match = super().match2(segments[:_end_idx], _idx, ctx)

        # Wherever we got to, work forward to find the closing bracket.
        # NOTE: We do this even if we didn't find a content match.
        with parse_context.deeper_match(name="Bracketed-End") as ctx:
            final_match, _ = next_ex_bracket_match2(
                segments,
                idx=content_match.matched_slice.stop,
                matchers=[end_bracket],
                parse_context=ctx,
            )

        if not final_match:
            # NOTE: THIS IS A GREAT PLACE FOR PARTIAL UNPARSABLES??????
            raise NotImplementedError(
                "BRACKETED. WE'RE GOING TO NEED THIS? "
                f"CASE 4\n{content_match}\n{final_match}\n{segments}"
            )

        # Regardless of whether the inner match was successful, append it.
        # We're going to pick out the rest as unparsable shortly.
        # NOTE: If it's unparsable content, then wrap in an unparsable here.
        # TODO: YESYESYES MORE TESTS
        if len(content_match) and not content_match.is_clean:
            content_match = content_match.wrap(
                UnparsableSegment,
                segment_kwargs={"expected": f"Bracketed Sequence of: {self._elements}"},
            )
        working_match = start_match.append(content_match)

        # What's between the final match and the content. Hopefully just gap?
        intermediate_slice = slice(
            content_match.matched_slice.stop, final_match.matched_slice.start
        )
        if any(seg.is_code for seg in segments[intermediate_slice]):
            # Work out what to say for what we _were_ expecting.
            if len(content_match):
                expected = "Nothing else in bracketed expression."
            else:
                expected = str(self._elements)
            # Ok, there's something else in the gap. Add it as an UnparsableSegment.
            child_match = MatchResult2(
                intermediate_slice,
                UnparsableSegment,
                segment_kwargs={"expected": expected},
                is_clean=False,
            )
            working_match = working_match.append(child_match)

        # NOTE: For backward compatibility reasons (and not ones I'm sure
        # I agree with), we only wrap if the brackets are _round_. Otherwise
        # we just return flat.
        # HACK: We should probably remove this, I think it just perpetuates an
        # old existing inconsistency.
        if segments[start_match.matched_slice.start].raw != "(":
            return working_match.append(
                final_match,
                insert_segments=(
                    (start_match.matched_slice.stop, Indent),
                    (final_match.matched_slice.start, Dedent),
                ),
            )

        return working_match.append(final_match).wrap(
            BracketedSegment,
            insert_segments=(
                (start_match.matched_slice.stop, Indent),
                (final_match.matched_slice.start, Dedent),
            ),
            segment_kwargs={
                "start_bracket": (segments[start_match.matched_slice.start],),
                "end_bracket": (segments[final_match.matched_slice.stop - 1],),
            },
        )
