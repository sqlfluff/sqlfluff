"""Matching utility methods.

These are mostly extracted from the body of either BaseSegment
or BaseGrammar to un-bloat those classes.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import (
    DefaultDict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    cast,
)

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult2
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.bracketed import BracketedSegment
from sqlfluff.core.parser.types import MatchableType


@dataclass
class BracketInfo:
    """BracketInfo tuple for keeping track of brackets during matching."""

    bracket: BaseSegment
    segments: Tuple[BaseSegment, ...]

    def to_segment(self, end_bracket: Tuple[BaseSegment, ...]) -> BracketedSegment:
        """Turn the contained segments into a bracketed segment."""
        assert len(end_bracket) == 1
        return BracketedSegment(
            segments=self.segments,
            start_bracket=(self.bracket,),
            end_bracket=cast(Tuple[BaseSegment], end_bracket),
        )


def first_trimmed_raw(seg: BaseSegment) -> str:
    """Trim whitespace off a whole element raw.

    Used as a helper function in BaseGrammar._look_ahead_match.

    For existing compound segments, we should assume that within
    that segment, things are internally consistent, that means
    rather than enumerating all the individual segments of a longer
    one we just dump out the whole segment, but splitting off the
    first element separated by whitespace. This is a) faster and
    also b) prevents some really horrible bugs with bracket matching.
    See https://github.com/sqlfluff/sqlfluff/issues/433

    This fetches the _whole_ raw of a potentially compound segment
    to match against, trimming off any whitespace. This is the
    most efficient way to get at the first element of a potentially
    longer segment.
    """
    s = seg.raw_upper.split(maxsplit=1)
    return s[0] if s else ""


def first_non_whitespace(
    segments: Sequence[BaseSegment],
    start_idx=0,
) -> Optional[Tuple[str, Set[str]]]:
    """Return the upper first non-whitespace segment in the iterable."""
    for i in range(start_idx, len(segments)):
        _segment = segments[i]
        if _segment.first_non_whitespace_segment_raw_upper:
            return (
                _segment.first_non_whitespace_segment_raw_upper,
                _segment.class_types,
            )
    return None


def prune_options(
    options: List[MatchableType],
    segments: Sequence[BaseSegment],
    parse_context: ParseContext,
    start_idx=0,
) -> List[MatchableType]:
    """Use the simple matchers to prune which options to match on.

    Works in the context of a grammar making choices between options
    such as AnyOf or the content of Delimited.
    """
    available_options = []
    prune_buff = []

    # Find the first code element to match against.
    first = first_non_whitespace(segments, start_idx=start_idx)
    # If we don't have an appropriate option to match against,
    # then we should just return immediately. Nothing will match.
    if not first:
        return options
    first_raw, first_types = first

    for opt in options:
        simple = opt.simple(parse_context=parse_context)
        if simple is None:
            # This element is not simple, we have to do a
            # full match with it...
            available_options.append(opt)
            continue

        # Otherwise we have a simple option, so let's use
        # it for pruning.
        simple_raws, simple_types = simple
        matched = False

        # We want to know if the first meaningful element of the str_buff
        # matches the option, based on either simple _raw_ matching or
        # simple _type_ matching.

        # Match Raws
        if simple_raws and first_raw in simple_raws:
            # If we get here, it's matched the FIRST element of the string buffer.
            available_options.append(opt)
            matched = True

        # Match Types
        if simple_types and not matched and first_types.intersection(simple_types):
            # If we get here, it's matched the FIRST element of the string buffer.
            available_options.append(opt)
            matched = True

        if not matched:
            # Ditch this option, the simple match has failed
            prune_buff.append(opt)
            continue

    return available_options


def longest_match2(
    segments: Tuple[BaseSegment, ...],
    matchers: Sequence[MatchableType],
    idx: int,
    parse_context: ParseContext,
) -> Tuple[MatchResult2, Optional[MatchableType]]:
    """Return longest match from a selection of matchers.

    Priority is:
    1. The first total match, which means we've matched all available segments or
        that we've hit a valid terminator.
    2. The longest clean match.
    3. The longest unclean match.
    4. An empty match.

    If for #2 and #3, there's a tie for the longest match, priority is given to the
    first in the iterable.

    Returns:
        `tuple` of (match_object, matcher).

    NOTE: This matching method is the workhorse of the parser. It drives the
    functionality of the AnyOf & AnyNumberOf grammars, and therefore by extension
    the degree of branching within the parser. It's performance can be monitored
    using the `parse_stats` object on the context.

    The things which determine the performance of this method are:
    1. Pruning. This method uses `prune_options()` to filter down which matchable
        options proceed to the full matching step. Ideally only very few do and this
        can handle the majority of the filtering.
    2. Caching. This method uses the parse cache (`check_parse_cache` and
        `put_parse_cache`) on the ParseContext to speed up repetitive matching
        operations. As we make progress through a file there will often not be a
        cached value already available, and so this cache has the greatest impact
        within poorly optimised (or highly nested) expressions.
    3. Terminators. By default, _all_ the options are evaluated, and then the
        longest (the `best`) is returned. The exception to this is when the match
        is `complete` (i.e. it matches _all_ the remaining segments), or when a
        match is followed by a valid terminator (i.e. a segment which indicates
        that the match is _effectively_ complete). In these latter scenarios, the
        _first_ complete or terminated match is returned. In the ideal case, the
        only matcher which is evaluated should be the "correct" one, and then no
        others should be attempted.
    """
    max_idx = len(segments)  # What is the limit

    # No matchers or no segments? No match.
    if not matchers or idx == max_idx:
        return MatchResult2.empty_at(idx), None

    # Prune available options, based on their simple representation for efficiency.
    # TODO: Given we don't allow trimming here we should be able to remove
    # some complexity from this function so that we just take the first segment.
    # Maybe that's just small potatoes though.
    available_options = prune_options(
        matchers, segments, parse_context=parse_context, start_idx=idx
    )

    # If no available options, return no match.
    # NOTE: No partials at this stage, because we're pruning the *starts*.
    if not available_options:
        return MatchResult2.empty_at(idx), None

    terminators = parse_context.terminators or ()
    terminated = False

    # NOTE: No start and end trimming as before. Check that's not an issue,
    # but I don't think it should happen here regardless.
    # TODO: REMOVE THIS COMMENT ONCE CONFIRMED.

    _s = segments[idx]
    # At parse time we should be able to count on there being a position marker.
    assert _s.pos_marker

    # Characterise this location.
    # Initial segment raw, loc, type and length of segment series.
    loc_key = (
        _s.raw,
        _s.pos_marker.working_loc,
        _s.get_type(),
        # NOTE: I don't think this key makes sense in this context
        # but I continue to include it for consistency.
        # It's a negative number for now so we don't get collisions
        # with the existing cache.
        # We use our own cache on the context so there we can easily
        # change.
        # TODO: CHECK THIS.
        -(max_idx - idx),
    )

    best_match = MatchResult2.empty_at(idx)
    best_matcher: Optional[MatchableType] = None
    # iterate at this position across all the matchers
    for matcher_idx, matcher in enumerate(available_options):
        # Check parse cache.
        matcher_key = matcher.cache_key()
        res_match: Optional[MatchResult2] = parse_context.check_parse_cache2(
            loc_key, matcher_key
        )
        # If cache miss, match fresh and repopulate.
        # NOTE: By comparing with None, we'll also still get "failed" matches.
        if res_match is None:
            # Match fresh if no cache hit
            res_match = matcher.match2(segments, idx, parse_context)
            # Cache it for later to for performance.
            parse_context.put_parse_cache2(loc_key, matcher_key, res_match)

        # Have we matched all available segments?
        # TODO: Do we still want this clause in the new world? It seems unlikely
        # if we assume there are _always_ more segments.
        if res_match and res_match.matched_slice.stop == max_idx:
            # TODO: Assess the issue of not handling trailing whitespace here.
            return res_match, matcher

        # Is this the best match so far?
        # NOTE: Using the inbuilt comparison functions of MatchResult2.
        if res_match.is_better_than(best_match):
            best_match = res_match
            best_matcher = matcher

            # If it _is_ better AND it's clean, then see if we can finish
            # early with a terminator.
            if best_match.is_clean:
                # If we've got a terminator next, it's an opportunity to
                # end earlier, and claim an effectively "complete" match.
                # NOTE: This means that by specifying terminators, we can
                # significantly increase performance.
                if idx == len(available_options) - 1:
                    # If it's the last option - no need to check terminators.
                    # We're going to end anyway, so we can skip that step.
                    terminated = True
                    break
                elif terminators:
                    _next_code_idx = best_match.matched_slice.stop
                    while not segments[_next_code_idx].is_code:
                        _next_code_idx += 1
                    for terminator in terminators:
                        terminator_match: MatchResult2 = terminator.match2(
                            segments, _next_code_idx, parse_context
                        )
                        if terminator_match:
                            terminated = True
                            break

        if terminated:
            break

    # Return the best we found.
    return best_match, best_matcher


def next_match2(
    segments: Sequence[BaseSegment],
    idx: int,
    matchers: Sequence[MatchableType],
    parse_context: ParseContext,
) -> Tuple[MatchResult2, Optional[MatchableType]]:
    """Look ahead for matches beyond the first element of the segments list.

    NOTE: Returns *only clean* matches.

    This function also contains the performance improved hash-matching approach to
    searching for matches, which should significantly improve performance.

    Prioritise the first match, and if multiple match at the same point the longest.
    If two matches of the same length match at the same time, then it's the first in
    the iterable of matchers.

    Returns:
        `tuple` of (match_object, matcher).

    """
    max_idx = len(segments)

    # Have we got any segments to match on?
    if idx >= max_idx:  # No? Return empty.
        return MatchResult2.empty_at(idx), None

    # This next section populates a lookup of the simple matchers.
    # TODO: This should really be populated on instantiation of the
    # host grammar.
    # NOTE: We keep the index of the matcher so we can prioritise
    # later. Mathchers themselves are obtained through direct lookup.
    raw_simple_map: DefaultDict[str, List[int]] = defaultdict(list)
    type_simple_map: DefaultDict[str, List[int]] = defaultdict(list)
    for _idx, matcher in enumerate(matchers):
        simple = matcher.simple(parse_context=parse_context)
        if not simple:  # pragma: no cover
            # NOTE: For all bundled dialects, this clause is true, but until
            # the RegexMatcher is completely deprecated (and therefore that
            # `.simple()` must provide a result), it is still _possible_
            # to end up here.
            raise NotImplementedError(
                "All matchers passed to `._next_match2()` are "
                "assumed to have a functioning `.simple()` option. "
                "In a future release it will be compulsory for _all_ "
                "matchables to implement `.simple()`. Please report "
                "this as a bug on GitHub along with your current query "
                f"and dialect.\nProblematic matcher: {matcher}"
            )

        for simple_raw in simple[0]:
            raw_simple_map[simple_raw].append(_idx)
        for simple_type in simple[1]:
            type_simple_map[simple_type].append(_idx)

    # There's an optimisation we could do here where we don't iterate
    # through them one by one, but we use a lookup which we pre-calculate
    # at the start of the whole matching process.
    # TODO: That's only worthwhile once we've got a bit closer to a single
    # pass parsing process.
    for _idx in range(idx, max_idx):
        seg = segments[_idx]
        _matcher_idxs = []
        # Raw matches first.
        _matcher_idxs.extend(raw_simple_map[first_trimmed_raw(seg)])
        # Type matches second.
        _type_overlap = seg.class_types.intersection(type_simple_map.keys())
        for _type in _type_overlap:
            _matcher_idxs.extend(type_simple_map[_type])

        # If no matchers to work with, continue
        if not _matcher_idxs:
            continue

        # If we do have them, sort them and then do the full match.
        _matcher_idxs.sort()
        for _matcher_idx in _matcher_idxs:
            _matcher = matchers[_matcher_idx]
            _match = _matcher.match2(segments, _idx, parse_context)
            # NOTE: We're only going to consider clean matches from this method.
            if _match:
                # This will do. Return.
                return _match, _matcher

    # If we finish the loop, we didn't find a match. Return empty.
    return MatchResult2.empty_at(idx), None


def resolve_bracket2(
    segments: Sequence[BaseSegment],
    opening_match: MatchResult2,
    opening_matcher: MatchableType,
    start_brackets: List[MatchableType],
    end_brackets: List[MatchableType],
    parse_context: ParseContext,
) -> MatchResult2:
    """Recursive match to resolve an opened bracket.

    Returns when the opening bracket is resolved.
    """
    max_idx = len(segments)
    assert opening_match
    assert opening_matcher in start_brackets
    type_idx = start_brackets.index(opening_matcher)
    matched_idx = opening_match.matched_slice.stop
    child_matches = ()

    while True:
        # Look for the next relevant bracket.
        match, matcher = next_match2(
            segments,
            matched_idx,
            matchers=start_brackets + end_brackets,
            parse_context=parse_context,
        )

        # Was it a failed match?
        if not match:
            # If it was failed, then this is a problem, we started an
            # opening bracket but never found the end.
            raise SQLParseError(
                "Couldn't find closing bracket for opening bracket.",
                segment=segments[opening_match.matched_slice.start],
            )

        # Did we find a closing bracket?
        if matcher in end_brackets:
            closing_idx = end_brackets.index(matcher)
            if closing_idx == type_idx:
                # We're closing the opening type.
                # NOTE: This is how we exit the loop.
                return MatchResult2(
                    # Slice should span from the first to the second.
                    slice(opening_match.matched_slice.start, match.matched_slice.stop),
                    matched_class=BracketedSegment,
                    segment_kwargs={
                        # TODO: This feels a bit weird. Could we infer it on construction?
                        "start_bracket": (segments[opening_match.matched_slice.start],),
                        "end_bracket": (segments[match.matched_slice.stop - 1],),
                    },
                    child_matches=child_matches,
                )
            # Otherwise we're closing an unexpected type. This is less good.
            raise SQLParseError(
                f"Found unexpected end bracket!, "
                f"was expecting "
                f"{end_brackets[type_idx]}, "
                f"but got {matcher}",
                segment=segments[match.matched_slice.stop - 1],
            )

        # Otherwise we found a new opening bracket.
        assert matcher in start_brackets
        # Recurse into a new bracket matcher.
        inner_match = resolve_bracket2(
            segments,
            opening_match=match,
            opening_matcher=matcher,
            start_brackets=start_brackets,
            end_brackets=end_brackets,
            parse_context=parse_context,
        )
        # This will either error, or only return once we're back out of the
        # bracket which started it. The return value will be a match result for
        # the inner BracketedSegment. This becomes a child of our return.
        child_matches += (inner_match,)
        matched_idx = inner_match.matched_slice.stop

        # Head back around the loop again to see if we can find the end...


def next_ex_bracket_match2(
    segments: Sequence[BaseSegment],
    idx: int,
    matchers: List[MatchableType],
    parse_context: ParseContext,
    start_bracket: Optional[MatchableType] = None,
    end_bracket: Optional[MatchableType] = None,
    bracket_pairs_set: str = "bracket_pairs",
) -> Tuple[MatchResult2, Optional[MatchableType]]:
    """Same as `next_match2` but with bracket counting.

    NB: Given we depend on `next_match2` we can also utilise
    the same performance optimisations which are implemented there.

    bracket_pairs_set: Allows specific segments to override the available
        bracket pairs. See the definition of "angle_bracket_pairs" in the
        BigQuery dialect for additional context on why this exists.

    Returns:
        `tuple` of (match_object, matcher).

    """
    max_idx = len(segments)

    # Have we got any segments to match on?
    if idx >= max_idx:  # No? Return empty.
        return MatchResult2.empty_at(idx), None

    # Get hold of the bracket matchers from the dialect, and append them
    # to the list of matchers. We get them from the relevant set on the
    # dialect. We use zip twice to "unzip" them. We ignore the first
    # argument because that's just the name.
    _, start_bracket_refs, end_bracket_refs, persists = zip(
        *parse_context.dialect.bracket_sets(bracket_pairs_set)
    )
    # These are matchables, probably StringParsers.
    start_brackets = [
        parse_context.dialect.ref(seg_ref) for seg_ref in start_bracket_refs
    ]
    end_brackets = [parse_context.dialect.ref(seg_ref) for seg_ref in end_bracket_refs]
    # Add any bracket-like things passed as arguments
    if start_bracket:
        start_brackets += [start_bracket]
    if end_bracket:
        end_brackets += [end_bracket]
    bracket_matchers = start_brackets + end_brackets

    # Make some buffers
    bracket_stack: List[BracketInfo] = []
    matched_idx = idx
    child_matches = ()

    # Iterate
    while True:  ### TODO: Check whether it should be a for loop?
        # Look ahead for opening brackets or the thing(s)
        # that we're otherwise looking for.
        match, matcher = next_match2(
            segments,
            matched_idx,
            matchers + bracket_matchers,
            parse_context=parse_context,
        )
        # Did we match? If so, is it a target or a bracket?
        if not match or matcher in matchers:
            # If there's either no match, or we hit a target, just pass the result.
            # NOTE: This method returns the same as `next_match2` in a "no match"
            # scenario, which is why we can simplify like this.
            return match, matcher
        # If it's a _closing_ bracket, then we also return no match.
        if matcher in end_brackets:
            # Unexpected end bracket! Return no match.
            # TODO: Should we make an unclean match here to help with unparsables?
            return MatchResult2.empty_at(idx), None

        # Otherwise we found a opening bracket before finding a target.
        # We now call the recursive function because there might be more
        # brackets inside.
        # NOTE: This only returns on resolution of the opening bracket.
        # TODO: We go to quite a bit of work to construct the inner matches
        # here, but we're not really using them. Should we deal with that?
        bracket_match = resolve_bracket2(
            segments,
            opening_match=match,
            opening_matcher=matcher,
            start_brackets=start_brackets,
            end_brackets=end_brackets,
            parse_context=parse_context,
        )
        matched_idx = bracket_match.matched_slice.stop
        child_matches += (bracket_match,)
        # Head back around the loop and keep looking.