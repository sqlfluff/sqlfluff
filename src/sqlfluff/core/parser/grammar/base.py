"""Base grammar, Ref, Anything and Nothing."""

import copy
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    Union,
    Set,
    Type,
    Tuple,
    Any,
    cast,
)
from typing_extensions import Literal
from uuid import uuid4

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser.grammar.types import SimpleHintType
from sqlfluff.core.string_helpers import curtail_string

from sqlfluff.core.parser.segments import BaseSegment, BracketedSegment, allow_ephemeral
from sqlfluff.core.parser.helpers import trim_non_code_segments
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_logging import (
    parse_match_logging,
    LateBoundJoinSegmentsCurtailed,
)
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.parsers import BaseParser

# Either a Matchable (a grammar or parser) or a Segment CLASS

MatchableType = Union[Matchable, Type[BaseSegment]]

if TYPE_CHECKING:
    from sqlfluff.core.dialects.base import Dialect  # pragma: no cover


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

    def to_segment(self, end_bracket) -> BracketedSegment:
        """Turn the contained segments into a bracketed segment."""
        return BracketedSegment(
            segments=self.segments,
            start_bracket=(self.bracket,),
            end_bracket=end_bracket,
        )


def cached_method_for_parse_context(func):
    """A decorator to cache the output of this method for a given parse context.

    This cache automatically invalidates if the uuid
    of the parse context changes. The value is store
    in the __dict__ attribute of the class against a
    key unique to that function.
    """
    cache_key = "__cache_" + func.__name__

    def wrapped_method(self, parse_context: ParseContext, **kwargs):
        """Cache the output of the method against a given parse context.

        Note: kwargs are not taken into account in the caching, but
        for the current use case of dependency loop debugging that's
        ok.
        """
        cache_tuple: tuple = self.__dict__.get(cache_key, (None, None))
        # Do we currently have a cached value?
        if cache_tuple[0] == parse_context.uuid:
            return cache_tuple[1]
        # Generate a new value, cache it and return
        result = func(self, parse_context=parse_context, **kwargs)
        self.__dict__[cache_key] = (parse_context.uuid, result)
        return result

    return wrapped_method


class BaseGrammar(Matchable):
    """Grammars are a way of composing match statements.

    Any grammar must implement the `match` function. Segments can also be
    passed to most grammars. Segments implement `match` as a classmethod. Grammars
    implement it as an instance method.

    """

    is_meta = False
    # Are we allowed to refer to keywords as strings instead of only passing
    # grammars or segments?
    allow_keyword_string_refs = True
    equality_kwargs: Tuple[str, ...] = ("optional", "allow_gaps")

    @staticmethod
    def _resolve_ref(elem):
        """Resolve potential string references to things we can match against."""
        initialisers = [
            # t: instance / f: class, ref, func
            (True, str, Ref.keyword),
            (True, BaseGrammar, lambda x: x),
            (True, BaseParser, lambda x: x),
            (False, BaseSegment, lambda x: x),
        ]
        # Get-out clause for None
        if elem is None:
            return None

        for instance, init_type, init_func in initialisers:
            if (instance and isinstance(elem, init_type)) or (
                not instance and issubclass(elem, init_type)
            ):
                return init_func(elem)
        raise TypeError(
            "Grammar element [{!r}] was found of unexpected type [{}] was "
            "found.".format(elem, type(elem))  # pragma: no cover
        )

    def __init__(
        self,
        *args: Union[MatchableType, str],
        allow_gaps=True,
        optional=False,
        ephemeral_name=None,
    ) -> None:
        """Deal with kwargs common to all grammars.

        Args:
            *args: Any number of elements which because the subjects
                of this grammar. Optionally these elements may also be
                string references to elements rather than the Matchable
                elements themselves.
            allow_gaps (:obj:`bool`, optional): Does this instance of the
                grammar allow gaps between the elements it matches? This
                may be exhibited slightly differently in each grammar. See
                that grammar for details. Defaults `True`.
            optional (:obj:`bool`, optional): In the context of a sequence,
                is this grammar *optional*, i.e. can it be skipped if no
                match is found. Outside of a Sequence, this option does nothing.
                Defaults `False`.
            ephemeral_name (:obj:`str`, optional): If specified this allows
                the grammar to match anything, and create an EphemeralSegment
                with the given name in its place. The content of this grammar
                is passed to the segment, and will become the parse grammar
                for it. If used widely this is an excellent way of breaking
                up the parse process and also signposting the name of a given
                chunk of code that might be parsed separately.
        """
        # We provide a common interface for any grammar that allows positional elements.
        # If *any* for the elements are a string and not a grammar, then this is a
        # shortcut to the Ref.keyword grammar by default.
        if self.allow_keyword_string_refs:
            self._elements = []
            for elem in args:
                self._elements.append(self._resolve_ref(elem))
        else:
            self._elements = list(args)

        # Now we deal with the standard kwargs
        self.allow_gaps = allow_gaps
        self.optional: bool = optional
        # ephemeral_name is a flag to indicate whether we need to make an
        # EphemeralSegment class. This is effectively syntactic sugar
        # to allow us to avoid specifying a EphemeralSegment directly in a dialect.
        # If this is the case, the actual segment construction happens in the
        # match_wrapper.
        self.ephemeral_name = ephemeral_name
        # Generate a cache key
        self._cache_key = uuid4().hex

    def cache_key(self) -> str:
        """Get the cache key for this grammar.

        For grammars these are unique per-instance.
        """
        return self._cache_key

    def is_optional(self) -> bool:
        """Return whether this segment is optional.

        The optional attribute is set in the __init__ method.
        """
        return self.optional

    @match_wrapper()
    @allow_ephemeral
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> MatchResult:
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} has no match function implemented"
        )  # pragma: no cover

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[List[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a lowercase hash matching route?"""
        return None

    @staticmethod
    def _first_non_whitespace(segments) -> Optional[Tuple[str, Set[str]]]:
        """Return the upper first non-whitespace segment in the iterable."""
        for segment in segments:
            if segment.first_non_whitespace_segment_raw_upper:
                return (
                    segment.first_non_whitespace_segment_raw_upper,
                    segment.class_types,
                )
        return None

    @classmethod
    def _prune_options(
        cls,
        options: List[MatchableType],
        segments: Tuple[BaseSegment, ...],
        parse_context: ParseContext,
    ) -> List[MatchableType]:
        """Use the simple matchers to prune which options to match on.

        Works in the context of a grammar making choices between options
        such as AnyOf or the content of Delimited.
        """
        available_options = []
        prune_buff = []

        # Find the first code element to match against.
        first_segment = cls._first_non_whitespace(segments)
        # If we don't have an appropriate option to match against,
        # then we should just return immediately. Nothing will match.
        if not first_segment:
            return options
        first_raw, first_types = first_segment

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

    @classmethod
    def _longest_trimmed_match(
        cls,
        segments: Tuple[BaseSegment, ...],
        matchers: List[MatchableType],
        parse_context: ParseContext,
        trim_noncode: bool = True,
    ) -> Tuple[MatchResult, Optional[MatchableType]]:
        """Return longest match from a selection of matchers.

        Prioritise the first match, and if multiple match at the same point the longest.
        If two matches of the same length match at the same time, then it's the first in
        the iterable of matchers.

        Returns:
            `tuple` of (match_object, matcher).

        NOTE: This matching method is the workhorse of the parser. It drives the
        functionality of the AnyOf & AnyNumberOf grammars, and therefore by extension
        the degree of branching within the parser. It's performance can be monitored
        using the `parse_stats` object on the context.

        The things which determine the performance of this method are:
        1. Pruning. This method uses `_prune_options()` to filter down which matchable
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
        # Have we been passed an empty list?
        if len(segments) == 0:  # pragma: no cover
            return MatchResult.from_empty(), None
        # If presented with no options, return no match
        elif not matchers:
            return MatchResult.from_unmatched(segments), None

        # Prune available options, based on their simple representation for efficiency.
        available_options = cls._prune_options(
            matchers, segments, parse_context=parse_context
        )

        # If we've pruned all the options, return no match
        if not available_options:
            return MatchResult.from_unmatched(segments), None

        terminated = False

        parse_context.increment("ltm_calls")
        # NOTE: The use of terminators is only available via the context.
        # They are set in that way to allow appropriate inheritance rather
        # than only being used in a per-grammar basis.
        if parse_context.terminators:
            parse_context.increment("ltm_calls_w_ctx_terms")
            terminators = parse_context.terminators
        else:
            terminators = ()

        # If gaps are allowed, trim the ends.
        if trim_noncode:
            pre_nc, segments, post_nc = trim_non_code_segments(segments)

        # At parse time we should be able to count on there being a location.
        assert segments[0].pos_marker

        # Characterise this location.
        # Initial segment raw, loc, type and length of segment series.
        loc_key = (
            segments[0].raw,
            segments[0].pos_marker.working_loc,
            segments[0].get_type(),
            len(segments),
        )

        best_match_length = 0
        best_match: Optional[Tuple[MatchResult, MatchableType]] = None
        # iterate at this position across all the matchers
        for idx, matcher in enumerate(available_options):
            # Check parse cache.
            matcher_key = matcher.cache_key()
            res_match: Optional[MatchResult] = parse_context.check_parse_cache(
                loc_key, matcher_key
            )
            if res_match:
                parse_match_logging(
                    cls.__name__,
                    "_look_ahead_match",
                    "HIT",
                    parse_context=parse_context,
                    cache_hit=matcher.__class__.__name__,
                    cache_key=matcher_key,
                )
            else:
                # Match fresh if no cache hit
                res_match = matcher.match(segments, parse_context)
                # Cache it for later to for performance.
                parse_context.put_parse_cache(loc_key, matcher_key, res_match)

            # By here we know that it's a MatchResult
            res_match = cast(MatchResult, res_match)

            if res_match.is_complete():
                # Just return it! (WITH THE RIGHT OTHER STUFF)
                parse_context.increment("complete_match")
                if trim_noncode:
                    return (
                        MatchResult.from_matched(
                            pre_nc + res_match.matched_segments + post_nc
                        ),
                        matcher,
                    )
                else:
                    return res_match, matcher
            elif res_match:
                # We've got an incomplete match, if it's the best so far keep it.
                if res_match.trimmed_matched_length > best_match_length:
                    best_match = res_match, matcher
                    best_match_length = res_match.trimmed_matched_length

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
                        _, segs, _ = trim_non_code_segments(
                            best_match[0].unmatched_segments
                        )
                        for terminator in terminators:
                            terminator_match: MatchResult = terminator.match(
                                segs, parse_context
                            )

                            if terminator_match.matched_segments:
                                terminated = True
                                break

            if terminated:
                break

            # We could stash segments here, but given we might have some successful
            # matches here, we shouldn't, because they'll be mutated in the wrong way.
            # Eventually there might be a performance gain from doing that sensibly
            # here.

        if terminated:
            parse_context.increment("terminated_match")
        else:
            parse_context.increment("unterminated_match")

        # If we get here, then there wasn't a complete match. If we
        # has a best_match, return that.
        if best_match_length > 0:
            assert best_match
            # If not terminated, keep track of what the next token would
            # have been if we had been able to terminate using it.
            if not terminated:
                if best_match[0].unmatched_segments:
                    for seg in best_match[0].unmatched_segments:
                        if seg.is_code:
                            break
                    next_seg = seg.raw_segments[0].raw_upper
                else:  # pragma: no cover
                    # NOTE: I don't think this clause should ever
                    # occur, but it's included so that if it does happen
                    # we don't get an exception and can better debug.
                    next_seg = "<NONE>"
                parse_context.parse_stats["next_counts"][next_seg] += 1

            if trim_noncode:
                return (
                    MatchResult(
                        pre_nc + best_match[0].matched_segments,
                        best_match[0].unmatched_segments + post_nc,
                    ),
                    best_match[1],
                )
            else:
                return best_match
        # If no match at all, return nothing
        return MatchResult.from_unmatched(segments), None

    @classmethod
    def _look_ahead_match(
        cls,
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
        parse_match_logging(
            cls.__name__,
            "_look_ahead_match",
            "IN",
            parse_context=parse_context,
            v_level=4,
            ls=len(segments),
            seg=LateBoundJoinSegmentsCurtailed(segments),
        )

        # Have we been passed an empty tuple?
        if not segments:  # pragma: no cover TODO?
            return ((), MatchResult.from_empty(), None)

        # Here we enable a performance optimisation. Most of the time in this cycle
        # happens in loops looking for simple matchers which we should
        # be able to find a shortcut for.

        parse_match_logging(
            cls.__name__,
            "_look_ahead_match",
            "SI",
            parse_context=parse_context,
            v_level=4,
        )

        best_simple_match = None
        simple_match = None
        for idx, seg in enumerate(segments):
            for matcher in matchers:
                simple = matcher.simple(parse_context=parse_context)
                if not simple:  # pragma: no cover
                    # NOTE: For all bundled dialects, this clause is true, but until
                    # the RegexMatcher is completely deprecated (and therefore that
                    # `.simple()` must provide a result), it is still _possible_
                    # to end up here.
                    raise NotImplementedError(
                        "All matchers passed to `._look_ahead_match()` are "
                        "assumed to have a functioning `.simple()` option. "
                        "In a future release it will be compulsory for _all_ "
                        "matchables to implement `.simple()`. Please report "
                        "this as a bug on GitHub along with your current query "
                        f"and dialect.\nProblematic matcher: {matcher}"
                    )
                simple_raws, simple_types = simple

                assert simple_raws or simple_types
                if simple_raws:
                    trimmed_seg = first_trimmed_raw(seg)
                    if trimmed_seg in simple_raws:
                        simple_match = matcher
                        break
                if simple_types and not simple_match:
                    intersection = simple_types.intersection(seg.class_types)
                    if intersection:
                        simple_match = matcher
                        break

            # We've managed to match. We can shortcut home.
            # NB: We may still need to deal with whitespace.
            if simple_match:
                # If we have a _simple_ match, now we should call the
                # full match method to actually produce the result.
                match = simple_match.match(segments[idx:], parse_context)
                if match:
                    best_simple_match = (
                        segments[:idx],
                        match,
                        simple_match,
                    )
                    break
                else:
                    simple_match = None

        # There are no other matchers, we can just shortcut now. Either with
        # no match, or the best one we found (if we found one).
        parse_match_logging(
            cls.__name__,
            "_look_ahead_match",
            "SC",
            parse_context=parse_context,
            v_level=4,
            bsm=None
            if not best_simple_match
            else (
                len(best_simple_match[0]),
                len(best_simple_match[1]),
                best_simple_match[2],
            ),
        )

        if best_simple_match:
            return best_simple_match
        else:
            return ((), MatchResult.from_unmatched(segments), None)

    @classmethod
    def _bracket_sensitive_look_ahead_match(
        cls,
        segments: Tuple[BaseSegment, ...],
        matchers: List[MatchableType],
        parse_context: ParseContext,
        start_bracket: Optional[Matchable] = None,
        end_bracket: Optional[Matchable] = None,
        bracket_pairs_set: Literal[
            "bracket_pairs", "angle_bracket_pairs"
        ] = "bracket_pairs",
    ) -> Tuple[Tuple[BaseSegment, ...], MatchResult, Optional[MatchableType]]:
        """Same as `_look_ahead_match` but with bracket counting.

        NB: Given we depend on `_look_ahead_match` we can also utilise
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
        end_brackets = [
            parse_context.dialect.ref(seg_ref) for seg_ref in end_bracket_refs
        ]
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
                    pre, match, matcher = cls._look_ahead_match(
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
                                bracket_stack[-1].segments += (
                                    pre + match.matched_segments
                                )
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
                    pre, match, matcher = cls._look_ahead_match(
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
                            parse_match_logging(
                                cls.__name__,
                                "_bracket_sensitive_look_ahead_match",
                                "UEXB",
                                parse_context=parse_context,
                                v_level=3,
                                got=matcher,
                            )
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

    def __str__(self) -> str:  # pragma: no cover TODO?
        return repr(self)

    def __repr__(self) -> str:
        return "<{}: [{}]>".format(
            self.__class__.__name__,
            curtail_string(
                ", ".join(curtail_string(repr(elem), 40) for elem in self._elements),
                100,
            ),
        )

    def __eq__(self, other) -> bool:
        """Two grammars are equal if their elements and types are equal.

        NOTE: We use the equality_kwargs tuple on the class to define
        other kwargs which should also be checked so that things like
        "optional" is also taken into account in considering equality.
        """
        return (
            type(self) is type(other)
            and self._elements == other._elements
            and all(
                getattr(self, k, None) == getattr(other, k, None)
                for k in self.equality_kwargs
            )
        )

    def copy(
        self,
        insert: Optional[list] = None,
        at: Optional[int] = None,
        before: Optional[Any] = None,
        remove: Optional[list] = None,
        **kwargs,
    ):
        """Create a copy of this grammar, optionally with differences.

        This is mainly used in dialect inheritance.


        Args:
            insert (:obj:`list`, optional): Matchable elements to
                insert. This is inserted pre-expansion so can include
                unexpanded elements as normal.
            at (:obj:`int`, optional): The position in the elements
                to insert the item. Defaults to `None` which means
                insert at the end of the elements.
            before (optional): An alternative to _at_ to determine the
                position of an insertion. Using this inserts the elements
                immediately before the position of this element.
                Note that this is not an _index_ but an element to look
                for (i.e. a Segment or Grammar which will be compared
                with other elements for equality).
            remove (:obj:`list`, optional): A list of individual
                elements to remove from a grammar. Removal is done
                *after* insertion so that order is preserved.
                Elements are searched for individually.

        """
        # Copy only the *grammar* elements. The rest comes through
        # as is because they should just be classes rather than
        # instances.
        new_elems = [
            elem.copy() if isinstance(elem, BaseGrammar) else elem
            for elem in self._elements
        ]
        if insert:
            if at is not None and before is not None:  # pragma: no cover
                raise ValueError(
                    "Cannot specify `at` and `before` in BaseGrammar.copy()."
                )
            if before is not None:
                try:
                    idx = new_elems.index(before)
                except ValueError:  # pragma: no cover
                    raise ValueError(
                        "Could not insert {} in copy of {}. {} not Found.".format(
                            insert, self, before
                        )
                    )
                new_elems = new_elems[:idx] + insert + new_elems[idx:]
            elif at is None:
                new_elems = new_elems + insert
            else:
                new_elems = new_elems[:at] + insert + new_elems[at:]
        if remove:
            for elem in remove:
                try:
                    new_elems.remove(elem)
                except ValueError:  # pragma: no cover
                    raise ValueError(
                        "Could not remove {} from copy of {}. Not Found.".format(
                            elem, self
                        )
                    )
        new_seg = copy.copy(self)
        new_seg._elements = new_elems
        return new_seg


class Ref(BaseGrammar):
    """A kind of meta-grammar that references other grammars by name at runtime."""

    # We can't allow keyword refs here, because it doesn't make sense
    # and it also causes infinite recursion.
    allow_keyword_string_refs = False

    def __init__(self, *args: str, **kwargs) -> None:
        # Any patterns to _prevent_ a match.
        self.exclude = kwargs.pop("exclude", None)
        # The intent here is that if we match something, and then the _next_
        # item is one of these, we can safely conclude it's a "total" match.
        # In those cases, we return early without considering more options.
        # Terminators don't take effect directly within this grammar, but
        # the Ref grammar is an effective place to manage the terminators
        # inherited via the context.
        self.terminators = kwargs.pop("terminators", None)
        self.reset_terminators = kwargs.pop("reset_terminators", False)
        super().__init__(*args, **kwargs)

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a uppercase hash matching route?

        A ref is simple, if the thing it references is simple.
        """
        ref = self._get_ref()
        if crumbs and ref in crumbs:  # pragma: no cover
            loop = " -> ".join(crumbs)
            raise RecursionError(f"Self referential grammar detected: {loop}")
        return self._get_elem(dialect=parse_context.dialect).simple(
            parse_context=parse_context,
            crumbs=(crumbs or ()) + (ref,),
        )

    def _get_ref(self) -> str:
        """Get the name of the thing we're referencing."""
        # Unusually for a grammar we expect _elements to be a list of strings.
        # Notable ONE string for now.
        if len(self._elements) == 1:
            # We're good on length. Get the name of the reference
            ref = self._elements[0]
            if not isinstance(ref, str):  # pragma: no cover
                raise ValueError(
                    "Ref Grammar expects elements to be strings. "
                    f"Found {ref!r} instead."
                )
            return self._elements[0]
        else:  # pragma: no cover
            raise ValueError(
                "Ref grammar can only deal with precisely one element for now. Instead "
                "found {!r}".format(self._elements)
            )

    def _get_elem(self, dialect: "Dialect") -> Union[Type[BaseSegment], Matchable]:
        """Get the actual object we're referencing."""
        if dialect:
            # Use the dialect to retrieve the grammar it refers to.
            return dialect.ref(self._get_ref())
        else:  # pragma: no cover
            raise ReferenceError("No Dialect has been provided to Ref grammar!")

    def __repr__(self):
        return "<Ref: {}{}>".format(
            ", ".join(self._elements), " [opt]" if self.is_optional() else ""
        )

    @match_wrapper(v_level=4)  # Log less for Ref
    @allow_ephemeral
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> "MatchResult":
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        elem = self._get_elem(dialect=parse_context.dialect)

        # First if we have an *exclude* option, we should check that
        # which would prevent the rest of this grammar from matching.
        if self.exclude:
            with parse_context.deeper_match(
                name=self._get_ref() + "-Exclude",
                clear_terminators=self.reset_terminators,
                push_terminators=self.terminators,
            ) as ctx:
                if self.exclude.match(segments, parse_context=ctx):
                    return MatchResult.from_unmatched(segments)

        # Match against that. NB We're not incrementing the match_depth here.
        # References shouldn't really count as a depth of match.
        with parse_context.deeper_match(
            name=self._get_ref(),
            clear_terminators=self.reset_terminators,
            push_terminators=self.terminators,
        ) as ctx:
            resp = elem.match(segments, ctx)

        return resp

    @classmethod
    def keyword(cls, keyword: str, **kwargs) -> BaseGrammar:
        """Generate a reference to a keyword by name.

        This function is entirely syntactic sugar, and designed
        for more readable dialects.

        Ref.keyword('select') == Ref('SelectKeywordSegment')

        """
        name = keyword.capitalize() + "KeywordSegment"
        return cls(name, **kwargs)


class Anything(BaseGrammar):
    """Matches anything."""

    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> "MatchResult":
        """Matches... Anything.

        Most useful in match grammars, where a later parse grammar
        will work out what's inside.
        """
        return MatchResult.from_matched(segments)


class Nothing(BaseGrammar):
    """Matches nothing.

    Useful for placeholders which might be overwritten by other
    dialects.
    """

    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> "MatchResult":
        """Matches... nothing.

        Useful for placeholders which might be overwritten by other
        dialects.
        """
        return MatchResult.from_unmatched(segments)
