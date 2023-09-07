"""Matching algorithms.

These are mostly extracted from the body of either BaseSegment
or BaseGrammar to un-bloat those classes.
"""

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, cast

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.helpers import trim_non_code_segments
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.segments import BaseSegment, BracketedSegment
from sqlfluff.core.parser.types import MatchableType


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


@dataclass
class BracketInfo:
    """BracketInfo tuple for keeping track of brackets during matching.

    This is used in BaseGrammar._bracket_sensitive_look_ahead_match but
    defined here for type checking.
    """

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


def look_ahead_match(
    segments: Tuple[BaseSegment, ...],
    matchers: List[MatchableType],
    parse_context: ParseContext,
) -> Tuple[Tuple[BaseSegment, ...], MatchResult, Optional[MatchableType]]:
    """Look ahead for matches beyond the first element of the segments list.

    This function also contains the performance improved hash-matching approach to
    searching for matches, which should significantly improve performance.

    Prioritise the first match, and if multiple match at the same point the longest.
    If two matches of the same length match at the same time, then it's the first in
    the iterable of matchers.

    Returns:
        `tuple` of (unmatched_segments, match_object, matcher).

    """
    # Have we been passed an empty tuple?
    if not segments:  # pragma: no cover TODO?
        return ((), MatchResult.from_empty(), None)

    # Here we enable a performance optimisation. Most of the time in this cycle
    # happens in loops looking for simple matchers which we should
    # be able to find a shortcut for.
    best_simple_match = None
    simple_match = None
    for idx, seg in enumerate(segments):
        trimmed_seg = first_trimmed_raw(seg)
        for matcher in matchers:
            simple_match = None
            simple = matcher.simple(parse_context=parse_context)
            if not simple:  # pragma: no cover
                # NOTE: For all bundled dialects, this clause is true, but until
                # the RegexMatcher is completely deprecated (and therefore that
                # `.simple()` must provide a result), it is still _possible_
                # to end up here.
                raise NotImplementedError(
                    "All matchers passed to `.look_ahead_match()` are "
                    "assumed to have a functioning `.simple()` option. "
                    "In a future release it will be compulsory for _all_ "
                    "matchables to implement `.simple()`. Please report "
                    "this as a bug on GitHub along with your current query "
                    f"and dialect.\nProblematic matcher: {matcher}"
                )
            simple_raws, simple_types = simple

            assert simple_raws or simple_types
            if simple_raws:
                if trimmed_seg in simple_raws:
                    simple_match = matcher

            if simple_types and not simple_match:
                intersection = simple_types.intersection(seg.class_types)
                if intersection:
                    simple_match = matcher

            # If we couldn't achieve a simple match, move on to the next option.
            if not simple_match:
                continue

            # If there is, check the full version matches. If it doesn't
            # then discount it and move on.
            match = simple_match.match(segments[idx:], parse_context)
            if not match:
                continue

            best_simple_match = (
                segments[:idx],
                match,
                simple_match,
            )
            # Stop looking through matchers
            break

        # If we have a valid match, stop looking through segments
        if best_simple_match:
            break

    if best_simple_match:
        return best_simple_match
    else:
        return ((), MatchResult.from_unmatched(segments), None)


def bracket_sensitive_look_ahead_match(
    segments: Tuple[BaseSegment, ...],
    matchers: List[MatchableType],
    parse_context: ParseContext,
    start_bracket: Optional[MatchableType] = None,
    end_bracket: Optional[MatchableType] = None,
    bracket_pairs_set: str = "bracket_pairs",
) -> Tuple[Tuple[BaseSegment, ...], MatchResult, Optional[MatchableType]]:
    """Same as `look_ahead_match` but with bracket counting.

    NB: Given we depend on `look_ahead_match` we can also utilise
    the same performance optimisations which are implemented there.

    bracket_pairs_set: Allows specific segments to override the available
        bracket pairs. See the definition of "angle_bracket_pairs" in the
        BigQuery dialect for additional context on why this exists.

    Returns:
        `tuple` of (unmatched_segments, match_object, matcher).

    """
    # Have we been passed an empty tuple?
    if not segments:
        return ((), MatchResult.from_unmatched(segments), None)

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
    seg_buff: Tuple[BaseSegment, ...] = segments
    pre_seg_buff: Tuple[BaseSegment, ...] = ()
    bracket_stack: List[BracketInfo] = []

    # Iterate
    while True:
        # Do we have anything left to match on?
        if seg_buff:
            # Yes we have buffer left to work with.
            # Are we already in a bracket stack?
            if bracket_stack:
                # Yes, we're just looking for the closing bracket, or
                # another opening bracket.
                pre, match, matcher = look_ahead_match(
                    seg_buff,
                    bracket_matchers,
                    parse_context=parse_context,
                )

                if match:
                    # NB: We can only consider this as a nested bracket if the start
                    # and end tokens are not the same. If a matcher is both a start
                    # and end token we cannot deepen the bracket stack. In general,
                    # quoted strings are a typical example where the start and end
                    # tokens are the same. Currently, though, quoted strings are
                    # handled elsewhere in the parser, and there are no cases where
                    # *this* code has to handle identical start and end brackets.
                    # For now, consider this a small, speculative investment in a
                    # possible future requirement.
                    if matcher in start_brackets and matcher not in end_brackets:
                        # Add any segments leading up to this to the previous
                        # bracket.
                        bracket_stack[-1].segments += pre
                        # Add a bracket to the stack and add the matches from the
                        # segment.
                        bracket_stack.append(
                            BracketInfo(
                                bracket=match.matched_segments[0],
                                segments=match.matched_segments,
                            )
                        )
                        seg_buff = match.unmatched_segments
                        continue
                    elif matcher in end_brackets:
                        # Found an end bracket. Does its type match that of
                        # the innermost start bracket? E.g. ")" matches "(",
                        # "]" matches "[".
                        # For the start bracket we don't have the matcher
                        # but we can work out the type, so we use that for
                        # the lookup.
                        start_index = [
                            bracket.type for bracket in start_brackets
                        ].index(bracket_stack[-1].bracket.get_type())
                        # For the end index, we can just look for the matcher
                        end_index = end_brackets.index(matcher)
                        bracket_types_match = start_index == end_index
                        if bracket_types_match:
                            # Yes, the types match. So we've found a
                            # matching end bracket. Pop the stack, construct
                            # a bracketed segment and carry
                            # on.

                            # Complete the bracketed info
                            bracket_stack[-1].segments += pre + match.matched_segments
                            # Construct a bracketed segment (as a tuple) if allowed.
                            persist_bracket = persists[end_brackets.index(matcher)]
                            if persist_bracket:
                                new_segments: Tuple[BaseSegment, ...] = (
                                    bracket_stack[-1].to_segment(
                                        end_bracket=match.matched_segments
                                    ),
                                )
                            else:
                                new_segments = bracket_stack[-1].segments
                            # Remove the bracket set from the stack
                            bracket_stack.pop()
                            # If we're still in a bracket, add the new segments to
                            # that bracket, otherwise add them to the buffer
                            if bracket_stack:
                                bracket_stack[-1].segments += new_segments
                            else:
                                pre_seg_buff += new_segments
                            seg_buff = match.unmatched_segments
                            continue
                        else:
                            # The types don't match. Error.
                            raise SQLParseError(
                                f"Found unexpected end bracket!, "
                                f"was expecting "
                                f"{end_brackets[start_index]}, "
                                f"but got {matcher}",
                                segment=match.matched_segments[0],
                            )

                    else:  # pragma: no cover
                        raise RuntimeError("I don't know how we get here?!")
                else:  # pragma: no cover
                    # No match, we're in a bracket stack. Error.
                    raise SQLParseError(
                        "Couldn't find closing bracket for opening bracket.",
                        segment=bracket_stack[-1].bracket,
                    )
            else:
                # No, we're open to more opening brackets or the thing(s)
                # that we're otherwise looking for.
                pre, match, matcher = look_ahead_match(
                    seg_buff,
                    matchers + bracket_matchers,
                    parse_context=parse_context,
                )

                if match:
                    if matcher in matchers:
                        # It's one of the things we were looking for!
                        # Return.
                        return (pre_seg_buff + pre, match, matcher)
                    elif matcher in start_brackets:
                        # We've found the start of a bracket segment.
                        # NB: It might not *actually* be the bracket itself,
                        # but could be some non-code element preceding it.
                        # That's actually ok.

                        # Add the bracket to the stack.
                        bracket_stack.append(
                            BracketInfo(
                                bracket=match.matched_segments[0],
                                segments=match.matched_segments,
                            )
                        )
                        # The matched element has already been added to the bracket.
                        # Add anything before it to the pre segment buffer.
                        # Reset the working buffer.
                        pre_seg_buff += pre
                        seg_buff = match.unmatched_segments
                        continue
                    elif matcher in end_brackets:
                        # We've found an unexpected end bracket! This is likely
                        # because we're matching a section which should have ended.
                        # If we had a match, it would have matched by now, so this
                        # means no match.
                        pass
                        # From here we'll drop out to the happy unmatched exit.
                    else:  # pragma: no cover
                        # This shouldn't happen!?
                        raise NotImplementedError(
                            "This shouldn't happen. Panic in "
                            "_bracket_sensitive_look_ahead_match."
                        )
                # Not in a bracket stack, but no match.
                # From here we'll drop out to the happy unmatched exit.
        else:
            # No we're at the end:
            # Now check have we closed all our brackets?
            if bracket_stack:  # pragma: no cover
                # No we haven't.
                raise SQLParseError(
                    "Couldn't find closing bracket for opened brackets: "
                    f"`{bracket_stack}`.",
                    segment=bracket_stack[-1].bracket,
                )

        # This is the happy unmatched path. This occurs when:
        # - We reached the end with no open brackets.
        # - No match while outside a bracket stack.
        # - We found an unexpected end bracket before matching something
        # interesting. We return with the mutated segments so we can reuse any
        # bracket matching.
        return ((), MatchResult.from_unmatched(pre_seg_buff + seg_buff), None)


def greedy_match(
    segments: Tuple[BaseSegment, ...],
    parse_context: ParseContext,
    matchers: Sequence[MatchableType],
    include_terminator: bool = False,
) -> MatchResult:
    """Looks ahead to claim everything up to some future terminators."""
    seg_buff = segments
    seg_bank: Tuple[BaseSegment, ...] = ()  # Empty tuple

    while True:
        with parse_context.deeper_match(name="GreedyUntil") as ctx:
            pre, mat, matcher = bracket_sensitive_look_ahead_match(
                seg_buff, list(matchers), parse_context=ctx
            )

        if not mat:
            # No terminator match? Return everything
            return MatchResult.from_matched(segments)

        # NOTE: For some terminators we only count them if they're preceded
        # by whitespace, and others we don't. In principle, we aim that for
        # _keywords_ we require whitespace, and for symbols we don't.
        # We do this by looking at the `simple` method of the returned
        # matcher, and if it's entirely alphabetical (as defined by
        # str.isalpha()) then we infer that it's a keyword, and therefore
        # _does_ require whitespace before it.
        assert matcher, f"Match without matcher: {mat}"
        _simple = matcher.simple(parse_context)
        assert _simple, f"Terminators require a simple method: {matcher}"
        _strings, _types = _simple
        # NOTE: Typed matchers aren't common here, but we assume that they
        # _don't_ require preceding whitespace.
        # Do we need to enforce whitespace preceding?
        if all(_s.isalpha() for _s in _strings) and not _types:
            # Does the match include some whitespace already?
            # Work forward
            idx = 0
            while True:
                elem = mat.matched_segments[idx]
                if elem.is_meta:  # pragma: no cover TODO?
                    idx += 1
                    continue
                elif elem.is_type("whitespace", "newline"):  # pragma: no cover TODO?
                    allowable_match = True
                    break
                else:
                    # No whitespace before. Not allowed.
                    allowable_match = False
                    break

            # If we're not ok yet, work backward to the preceding sections.
            if not allowable_match:
                idx = -1
                while True:
                    if len(pre) < abs(idx):  # pragma: no cover TODO?
                        # If we're at the start, it's ok
                        allowable_match = True
                        break
                    if pre[idx].is_meta:  # pragma: no cover TODO?
                        idx -= 1
                        continue
                    elif pre[idx].is_type("whitespace", "newline"):
                        allowable_match = True
                        break
                    else:
                        # No whitespace before. Not allowed.
                        allowable_match = False
                        break

            # If this match isn't preceded by whitespace and that is
            # a requirement, then we can't use it. Carry on...
            if not allowable_match:
                # Update our buffers and continue onward
                seg_bank = seg_bank + pre + mat.matched_segments
                seg_buff = mat.unmatched_segments
                # Loop around, don't return yet
                continue

        # Return everything up to the match unless it's a gap matcher.
        if include_terminator:
            return MatchResult(
                seg_bank + pre + mat.matched_segments,
                mat.unmatched_segments,
            )

        # We can't claim any non-code segments, so we trim them off the end.
        leading_nc, pre_seg_mid, trailing_nc = trim_non_code_segments(seg_bank + pre)
        return MatchResult(
            leading_nc + pre_seg_mid,
            trailing_nc + mat.all_segments(),
        )
