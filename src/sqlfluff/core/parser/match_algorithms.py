"""Matching algorithms.

These are mostly extracted from the body of either BaseSegment
or BaseGrammar to un-bloat those classes.
"""

from collections import defaultdict
from typing import DefaultDict, FrozenSet, List, Optional, Sequence, Tuple, cast

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments import BaseSegment, BracketedSegment, Dedent, Indent


def skip_start_index_forward_to_code(
    segments: Sequence[BaseSegment], start_idx: int, max_idx: Optional[int] = None
) -> int:
    """Move an index forward through segments until segments[index] is code."""
    if max_idx is None:
        max_idx = len(segments)
    for _idx in range(start_idx, max_idx):
        if segments[_idx].is_code:
            break
    else:
        _idx = max_idx
    return _idx


def skip_stop_index_backward_to_code(
    segments: Sequence[BaseSegment], stop_idx: int, min_idx: int = 0
) -> int:
    """Move an index backward through segments until segments[index - 1] is code."""
    for _idx in range(stop_idx, min_idx, -1):
        if segments[_idx - 1].is_code:
            break
    else:
        _idx = min_idx
    return _idx


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
    start_idx: int = 0,
) -> Optional[Tuple[str, FrozenSet[str]]]:
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
    options: Sequence[Matchable],
    segments: Sequence[BaseSegment],
    parse_context: ParseContext,
    start_idx: int = 0,
) -> List[Matchable]:
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
        return list(options)
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


def longest_match(
    segments: Sequence[BaseSegment],
    matchers: Sequence[Matchable],
    idx: int,
    parse_context: ParseContext,
) -> Tuple[MatchResult, Optional[Matchable]]:
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
        return MatchResult.empty_at(idx), None

    # Prune available options, based on their simple representation for efficiency.
    # TODO: Given we don't allow trimming here we should be able to remove
    # some complexity from this function so that we just take the first segment.
    # Maybe that's just small potatoes though.
    available_options = prune_options(
        matchers, segments, parse_context=parse_context, start_idx=idx
    )

    # If no available options, return no match.
    if not available_options:
        return MatchResult.empty_at(idx), None

    terminators = parse_context.terminators or ()
    terminated = False
    # At parse time we should be able to count on there being a position marker.
    _cache_position = segments[idx].pos_marker
    assert _cache_position

    # Characterise this location.
    # Initial segment raw, loc, type and length of segment series.
    loc_key = (
        segments[idx].raw,
        _cache_position.working_loc,
        segments[idx].get_type(),
        # The reason that the max_idx is part of the cache key is to
        # account for scenarios where the end of the segment sequence
        # has been trimmed and we don't want to assume we can match
        # things which have now been trimmed off.
        max_idx,
    )

    best_match = MatchResult.empty_at(idx)
    best_matcher: Optional[Matchable] = None
    # iterate at this position across all the matchers
    for matcher_idx, matcher in enumerate(available_options):
        # Check parse cache.
        matcher_key = matcher.cache_key()
        res_match: Optional[MatchResult] = parse_context.check_parse_cache(
            loc_key, matcher_key
        )
        # If cache miss, match fresh and repopulate.
        # NOTE: By comparing with None, "failed" matches can still be used
        # from cache. They a falsy, but not None.
        if res_match is None:
            # Match fresh if no cache hit
            res_match = matcher.match(segments, idx, parse_context)
            # Cache it for later to for performance.
            parse_context.put_parse_cache(loc_key, matcher_key, res_match)

        # Have we matched all available segments?
        if res_match and res_match.matched_slice.stop == max_idx:
            return res_match, matcher

        # Is this the best match so far?
        if res_match.is_better_than(best_match):
            best_match = res_match
            best_matcher = matcher

            # If we've got a terminator next, it's an opportunity to
            # end earlier, and claim an effectively "complete" match.
            # NOTE: This means that by specifying terminators, we can
            # significantly increase performance.
            if matcher_idx == len(available_options) - 1:
                # If it's the last option - no need to check terminators.
                # We're going to end anyway, so we can skip that step.
                terminated = True
                break
            elif terminators:
                _next_code_idx = skip_start_index_forward_to_code(
                    segments, best_match.matched_slice.stop
                )
                if _next_code_idx == len(segments):
                    # We're run out of segments, we're effectively terminated.
                    terminated = True
                    break
                for terminator in terminators:
                    terminator_match: MatchResult = terminator.match(
                        segments, _next_code_idx, parse_context
                    )
                    if terminator_match:
                        terminated = True
                        break

        if terminated:
            break

    # Return the best we found.
    return best_match, best_matcher


def next_match(
    segments: Sequence[BaseSegment],
    idx: int,
    matchers: Sequence[Matchable],
    parse_context: ParseContext,
) -> Tuple[MatchResult, Optional[Matchable]]:
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
        return MatchResult.empty_at(idx), None

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
                "All matchers passed to `._next_match()` are "
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

    # TODO: There's an optimisation we could do here where we don't iterate
    # through them one by one, but we use a lookup which we pre-calculate
    # at the start of the whole matching process.
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
            _match = _matcher.match(segments, _idx, parse_context)
            # NOTE: We're only going to consider clean matches from this method.
            if _match:
                # This will do. Return.
                return _match, _matcher

    # If we finish the loop, we didn't find a match. Return empty.
    return MatchResult.empty_at(idx), None


def resolve_bracket(
    segments: Sequence[BaseSegment],
    opening_match: MatchResult,
    opening_matcher: Matchable,
    start_brackets: List[Matchable],
    end_brackets: List[Matchable],
    bracket_persists: List[bool],
    parse_context: ParseContext,
    nested_match: bool = False,
) -> MatchResult:
    """Recursive match to resolve an opened bracket.

    If `nested_match` is True, then inner bracket matches are
    also returned as child matches. Otherwise only the outer
    match is returned.

    Returns when the opening bracket is resolved.
    """
    assert opening_match
    assert opening_matcher in start_brackets
    type_idx = start_brackets.index(opening_matcher)
    matched_idx = opening_match.matched_slice.stop
    child_matches: Tuple[MatchResult, ...] = (opening_match,)

    while True:
        # Look for the next relevant bracket.
        match, matcher = next_match(
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
                _persists = bracket_persists[type_idx]
                # We're closing the opening type.
                # Add the closing bracket match to the result as a child.
                child_matches += (match,)
                _match = MatchResult(
                    # Slice should span from the first to the second.
                    slice(opening_match.matched_slice.start, match.matched_slice.stop),
                    child_matches=child_matches,
                    insert_segments=(
                        (opening_match.matched_slice.stop, Indent),
                        (match.matched_slice.start, Dedent),
                    ),
                )
                # NOTE: This is how we exit the loop.
                if not _persists:
                    return _match
                return _match.wrap(
                    BracketedSegment,
                    segment_kwargs={
                        # TODO: This feels a bit weird.
                        # Could we infer it on construction?
                        "start_bracket": (segments[opening_match.matched_slice.start],),
                        "end_bracket": (segments[match.matched_slice.start],),
                    },
                )
            # Otherwise we're closing an unexpected type. This is less good.
            raise SQLParseError(
                f"Found unexpected end bracket!, "
                f"was expecting {end_brackets[type_idx]}, "
                f"but got {matcher}",
                segment=segments[match.matched_slice.stop - 1],
            )

        # Otherwise we found a new opening bracket.
        assert matcher in start_brackets
        # Recurse into a new bracket matcher.
        inner_match = resolve_bracket(
            segments,
            opening_match=match,
            opening_matcher=matcher,
            start_brackets=start_brackets,
            end_brackets=end_brackets,
            bracket_persists=bracket_persists,
            parse_context=parse_context,
        )
        # This will either error, or only return once we're back out of the
        # bracket which started it. The return value will be a match result for
        # the inner BracketedSegment. We ignore the inner and don't return it
        # as we only want to mutate the outer brackets.
        matched_idx = inner_match.matched_slice.stop
        if nested_match:
            child_matches += (inner_match,)

        # Head back around the loop again to see if we can find the end...


def next_ex_bracket_match(
    segments: Sequence[BaseSegment],
    idx: int,
    matchers: Sequence[Matchable],
    parse_context: ParseContext,
    bracket_pairs_set: str = "bracket_pairs",
) -> Tuple[MatchResult, Optional[Matchable], Tuple[MatchResult, ...]]:
    """Same as `next_match` but with bracket counting.

    NB: Given we depend on `next_match` we can also utilise
    the same performance optimisations which are implemented there.

    bracket_pairs_set: Allows specific segments to override the available
        bracket pairs. See the definition of "angle_bracket_pairs" in the
        BigQuery dialect for additional context on why this exists.

    Returns:
        `tuple` of (match_object, matcher, `tuple` of inner bracketed matches).

    """
    max_idx = len(segments)

    # Have we got any segments to match on?
    if idx >= max_idx:  # No? Return empty.
        return MatchResult.empty_at(idx), None, ()

    # Get hold of the bracket matchers from the dialect, and append them
    # to the list of matchers. We get them from the relevant set on the
    # dialect.
    _, start_bracket_refs, end_bracket_refs, bracket_persists = zip(
        *parse_context.dialect.bracket_sets(bracket_pairs_set)
    )
    # These are matchables, probably StringParsers.
    start_brackets = [
        parse_context.dialect.ref(seg_ref) for seg_ref in start_bracket_refs
    ]
    end_brackets = [parse_context.dialect.ref(seg_ref) for seg_ref in end_bracket_refs]
    bracket_matchers = start_brackets + end_brackets
    _matchers = list(matchers) + bracket_matchers

    # Make some buffers
    matched_idx = idx
    child_matches: Tuple[MatchResult, ...] = ()

    while True:
        match, matcher = next_match(
            segments,
            matched_idx,
            _matchers,
            parse_context=parse_context,
        )
        # Did we match? If so, is it a target or a bracket?
        if not match or matcher in matchers:
            # If there's either no match, or we hit a target, just pass the result.
            # NOTE: This method returns the same as `next_match` in a "no match"
            # scenario, which is why we can simplify like this.
            return match, matcher, child_matches
        # If it's a _closing_ bracket, then we also return no match.
        if matcher in end_brackets:
            # Unexpected end bracket! Return no match.
            return MatchResult.empty_at(idx), None, ()

        # Otherwise we found a opening bracket before finding a target.
        # We now call the recursive function because there might be more
        # brackets inside.
        assert matcher, "If there's a match, there should be a matcher."
        # NOTE: This only returns on resolution of the opening bracket.
        bracket_match = resolve_bracket(
            segments,
            opening_match=match,
            opening_matcher=matcher,
            start_brackets=start_brackets,
            end_brackets=end_brackets,
            bracket_persists=cast(List[bool], bracket_persists),
            parse_context=parse_context,
            # Do keep the nested brackets in case the calling method
            # wants to use them.
            nested_match=True,
        )
        matched_idx = bracket_match.matched_slice.stop
        child_matches += (bracket_match,)
        # Head back around the loop and keep looking.


def greedy_match(
    segments: Sequence[BaseSegment],
    idx: int,
    parse_context: ParseContext,
    matchers: Sequence[Matchable],
    include_terminator: bool = False,
    nested_match: bool = False,
) -> MatchResult:
    """Match anything up to some defined terminator."""
    working_idx = idx
    # NOTE: _stop_idx is always reset below after matching before reference
    # but mypy is unhappy unless we set a default value here.
    _stop_idx = idx
    # NOTE: child_matches is always tracked, but it will only ever have
    # _content_ if `nested_match` is True. It otherwise remains an empty tuple.
    child_matches: Tuple[MatchResult, ...] = ()

    while True:
        with parse_context.deeper_match(name="GreedyUntil") as ctx:
            match, matcher, inner_matches = next_ex_bracket_match(
                segments,
                idx=working_idx,
                matchers=matchers,
                parse_context=ctx,
            )

        if nested_match:
            child_matches += inner_matches

        # No match? That means we've not found any terminators.
        if not match:
            # Claim everything left.
            return MatchResult(slice(idx, len(segments)), child_matches=child_matches)

        _start_idx = match.matched_slice.start
        _stop_idx = match.matched_slice.stop
        # NOTE: For some terminators we only count them if they're preceded
        # by whitespace, and others we don't. In principle, we aim that for
        # _keywords_ we require whitespace, and for symbols we don't.
        # We do this by looking at the `simple` method of the returned
        # matcher, and if it's entirely alphabetical (as defined by
        # str.isalpha()) then we infer that it's a keyword, and therefore
        # _does_ require whitespace before it.
        assert matcher, f"Match without matcher: {match}"
        _simple = matcher.simple(parse_context)
        assert _simple, f"Terminators require a simple method: {matcher}"
        _strings, _types = _simple
        # NOTE: Typed matchers aren't common here, but we assume that they
        # _don't_ require preceding whitespace.
        # Do we need to enforce whitespace preceding?
        if all(_s.isalpha() for _s in _strings) and not _types:
            allowable_match = False
            # NOTE: Edge case - if we're matching the _first_ element (i.e. that
            # there are no `pre` segments) then we _do_ allow it.
            # TODO: Review whether this is as designed, but it is consistent
            # with past behaviour.
            if _start_idx == working_idx:
                allowable_match = True
            # Work backward through previous segments looking for whitespace.
            for _idx in range(_start_idx, working_idx, -1):
                if segments[_idx - 1].is_meta:
                    continue
                elif segments[_idx - 1].is_type("whitespace", "newline"):
                    allowable_match = True
                    break
                else:
                    # Found something other than metas and whitespace.
                    break

            # If this match isn't preceded by whitespace and that is
            # a requirement, then we can't use it. Carry on...
            if not allowable_match:
                working_idx = _stop_idx
                # Loop around, don't return yet
                continue

        # Otherwise, it's allowable!
        break

    # Return without any child matches or inserts. Greedy Matching
    # shouldn't be used for mutation.
    if include_terminator:
        return MatchResult(slice(idx, _stop_idx), child_matches=child_matches)

    # If we're _not_ including the terminator, we need to work back a little.
    # If it's preceded by any non-code, we can't claim that.
    # Work backwards so we don't include it.
    _stop_idx = skip_stop_index_backward_to_code(
        segments, match.matched_slice.start, idx
    )

    # If we went all the way back to `idx`, then ignore the _stop_idx.
    # There isn't any code in the gap _anyway_ - so there's no point trimming.
    if idx == _stop_idx:
        # TODO: I don't really like this rule, it feels like a hack.
        # Review whether it should be here.
        return MatchResult(
            slice(idx, match.matched_slice.start), child_matches=child_matches
        )

    # Otherwise return the trimmed version.
    return MatchResult(slice(idx, _stop_idx), child_matches=child_matches)


def trim_to_terminator(
    segments: Sequence[BaseSegment],
    idx: int,
    terminators: Sequence[Matchable],
    parse_context: ParseContext,
) -> int:
    """Trim forward segments based on terminators.

    Given a forward set of segments, trim elements from `segments` to
    `tail` by using a `greedy_match()` to identify terminators.

    If no terminators are found, no change is made.

    NOTE: This method is designed replace a `max_idx`:

    .. code-block:: python

        max_idx = _trim_to_terminator(segments[:max_idx], idx, ...)

    """
    # Is there anything left to match on.
    if idx >= len(segments):
        # Nope. No need to trim.
        return len(segments)

    # NOTE: If there is a terminator _immediately_, then greedy
    # match will appear to not match (because there's "nothing" before
    # the terminator). To resolve that case, we first match immediately
    # on the terminators and handle that case explicitly if it occurs.
    with parse_context.deeper_match(name="Trim-GreedyA-@0") as ctx:
        pruned_terms = prune_options(
            terminators, segments, start_idx=idx, parse_context=ctx
        )
        for term in pruned_terms:
            if term.match(segments, idx, ctx):
                # One matched immediately. Claim everything to the tail.
                return idx

    # If the above case didn't match then we proceed as expected.
    with parse_context.deeper_match(
        name="Trim-GreedyB-@0", track_progress=False
    ) as ctx:
        term_match = greedy_match(
            segments,
            idx,
            parse_context=ctx,
            matchers=terminators,
        )

    # Greedy match always returns.
    # Skip backward from wherever it got to (either a terminator, or
    # the end of the sequence).
    return skip_stop_index_backward_to_code(
        segments, term_match.matched_slice.stop, idx
    )
