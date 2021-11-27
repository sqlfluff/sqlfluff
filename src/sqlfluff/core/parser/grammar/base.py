"""Base grammar, Ref, Anything and Nothing."""

import copy
from dataclasses import dataclass
from typing import List, Optional, Union, Type, Tuple, Any

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.string_helpers import curtail_string

from sqlfluff.core.parser.segments import BaseSegment, BracketedSegment, allow_ephemeral
from sqlfluff.core.parser.helpers import trim_non_code_segments, iter_indices
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_logging import (
    parse_match_logging,
    LateBoundJoinSegmentsCurtailed,
)
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.parsers import StringParser

# Either a Grammar or a Segment CLASS
MatchableType = Union[Matchable, Type[BaseSegment]]


@dataclass
class BracketInfo:
    """BracketInfo tuple for keeping track of brackets during matching.

    This is used in BaseGrammar._bracket_sensitive_look_ahead_match but
    defined here for type checking.
    """

    bracket: BaseSegment
    segments: Tuple[BaseSegment, ...]

    def to_segment(self, end_bracket):
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

    def wrapped_method(self, parse_context: ParseContext):
        """Cache the output of the method against a given parse context."""
        cache_tuple: Tuple = self.__dict__.get(cache_key, (None, None))
        # Do we currently have a cached value?
        if cache_tuple[0] == parse_context.uuid:
            return cache_tuple[1]
        # Generate a new value, cache it and return
        result = func(self, parse_context=parse_context)
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

    @staticmethod
    def _resolve_ref(elem):
        """Resolve potential string references to things we can match against."""
        initialisers = [
            # t: instance / f: class, ref, func
            (True, str, Ref.keyword),
            (True, BaseGrammar, lambda x: x),
            (True, StringParser, lambda x: x),
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
            "Grammar element [{!r}] was found of unexpected type [{}] was found.".format(
                elem, type(elem)
            )  # pragma: no cover
        )

    def __init__(
        self,
        *args,
        allow_gaps=True,
        optional=False,
        ephemeral_name=None,
    ):
        """Deal with kwargs common to all grammars.

        Args:
            *args: Any number of elements which because the subjects
                of this grammar.
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
        # If *any* for the elements are a string and not a grammar, then this is a shortcut
        # to the Ref.keyword grammar by default.
        if self.allow_keyword_string_refs:
            self._elements = []
            for elem in args:
                self._elements.append(self._resolve_ref(elem))
        else:
            self._elements = list(args)

        # Now we deal with the standard kwargs
        self.allow_gaps = allow_gaps
        self.optional = optional
        # ephemeral_name is a flag to indicate whether we need to make an
        # EphemeralSegment class. This is effectively syntactic sugar
        # to allow us to avoid specifying a EphemeralSegment directly in a dialect.
        # If this is the case, the actual segment construction happens in the
        # match_wrapper.
        self.ephemeral_name = ephemeral_name

    def is_optional(self):
        """Return whether this segment is optional.

        The optional attribute is set in the __init__ method.
        """
        return self.optional

    @match_wrapper()
    @allow_ephemeral
    def match(self, segments: Tuple["BaseSegment", ...], parse_context: ParseContext):
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} has no match function implemented"
        )  # pragma: no cover

    @cached_method_for_parse_context
    def simple(self, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a lowercase hash matching route?"""
        return None

    @classmethod
    def _longest_trimmed_match(
        cls,
        segments: Tuple["BaseSegment", ...],
        matchers: List["MatchableType"],
        parse_context: ParseContext,
        trim_noncode=True,
    ) -> Tuple[MatchResult, Optional["MatchableType"]]:
        """Return longest match from a selection of matchers.

        Prioritise the first match, and if multiple match at the same point the longest.
        If two matches of the same length match at the same time, then it's the first in
        the iterable of matchers.

        Returns:
            `tuple` of (match_object, matcher).

        """
        # Have we been passed an empty list?
        if len(segments) == 0:
            return MatchResult.from_empty(), None

        # If gaps are allowed, trim the ends.
        if trim_noncode:
            pre_nc, segments, post_nc = trim_non_code_segments(segments)

        best_match_length = 0
        # iterate at this position across all the matchers
        for matcher in matchers:
            # MyPy seems to require a type hint here. Not quite sure why.
            res_match: MatchResult = matcher.match(
                segments, parse_context=parse_context
            )
            if res_match.is_complete():
                # Just return it! (WITH THE RIGHT OTHER STUFF)
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
                if res_match.matched_length > best_match_length:
                    best_match = res_match, matcher
                    best_match_length = res_match.matched_length
            # We could stash segments here, but given we might have some successful
            # matches here, we shouldn't, because they'll be mutated in the wrong way.
            # Eventually there might be a performance gain from doing that sensibly here.

        # If we get here, then there wasn't a complete match. If we
        # has a best_match, return that.
        if best_match_length > 0:
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
    def _look_ahead_match(cls, segments, matchers, parse_context):
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

        # Do some type munging
        matchers = list(matchers)
        if isinstance(segments, BaseSegment):  # pragma: no cover TODO?
            segments = [segments]

        # Have we been passed an empty list?
        if len(segments) == 0:  # pragma: no cover TODO?
            return ((), MatchResult.from_empty(), None)

        # Here we enable a performance optimisation. Most of the time in this cycle
        # happens in loops looking for simple matchers which we should
        # be able to find a shortcut for.
        # First: Assess the matchers passed in, if any are
        # "simple", then we effectively use a hash lookup across the
        # content of segments to quickly evaluate if the segment is present.
        # Matchers which aren't "simple" still take a slower route.
        _matchers = [
            (matcher, matcher.simple(parse_context=parse_context))
            for matcher in matchers
        ]
        simple_matchers = [matcher for matcher in _matchers if matcher[1]]
        non_simple_matchers = [matcher[0] for matcher in _matchers if not matcher[1]]
        best_simple_match = None
        if simple_matchers:
            # If they're all simple we can use a hash match to identify the first one.
            # Build a buffer of all the upper case raw segments ahead of us.
            str_buff = []
            # For existing compound segments, we should assume that within
            # that segment, things are internally consistent, that means
            # rather than enumerating all the individual segments of a longer
            # one we just dump out the whole segment, but splitting off the
            # first element seperated by whitespace. This is a) faster and
            # also b) prevents some really horrible bugs with bracket matching.
            # See https://github.com/sqlfluff/sqlfluff/issues/433

            def _trim_elem(seg):
                s = seg.raw_upper.split(maxsplit=1)
                return s[0] if s else ""

            str_buff = [_trim_elem(seg) for seg in segments]
            match_queue = []

            for matcher, simple in simple_matchers:
                # Simple will be a tuple of options
                for simple_option in simple:
                    # NOTE: We use iter_indices to make sure we capture
                    # all instances of potential matches if there are many.
                    # This is important for bracket counting.
                    for buff_pos in iter_indices(str_buff, simple_option):
                        match_queue.append((matcher, buff_pos, simple_option))

            # Sort the match queue. First to process AT THE END.
            # That means we pop from the end.
            match_queue = sorted(match_queue, key=lambda x: x[1])

            parse_match_logging(
                cls.__name__,
                "_look_ahead_match",
                "SI",
                parse_context=parse_context,
                v_level=4,
                mq=match_queue,
                sb=str_buff,
            )

            while match_queue:
                # We've managed to match. We can shortcut home.
                # NB: We may still need to deal with whitespace.
                queued_matcher, queued_buff_pos, queued_option = match_queue.pop()
                # Here we do the actual transform to the new segment.
                match = queued_matcher.match(segments[queued_buff_pos:], parse_context)
                if not match:
                    # We've had something match in simple matching, but then later excluded.
                    # Log but then move on to the next item on the list.
                    parse_match_logging(
                        cls.__name__,
                        "_look_ahead_match",
                        "NM",
                        parse_context=parse_context,
                        v_level=4,
                        _so=queued_option,
                    )
                    continue
                # Ok we have a match. Because we sorted the list, we'll take it!
                best_simple_match = (segments[:queued_buff_pos], match, queued_matcher)

        if not non_simple_matchers:
            # There are no other matchers, we can just shortcut now.

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

        # Make some buffers
        seg_buff = segments
        pre_seg_buff = ()  # NB: Tuple

        # Loop
        while True:
            # Do we have anything left to match on?
            if seg_buff:
                # Great, carry on.
                pass
            else:
                # We've got to the end without a match, return empty
                return ((), MatchResult.from_unmatched(segments), None)

            # We only check the NON-simple ones here for brevity.
            mat, m = cls._longest_trimmed_match(
                seg_buff,
                non_simple_matchers,
                parse_context=parse_context,
                trim_noncode=False,
            )

            if mat and not best_simple_match:
                return (pre_seg_buff, mat, m)
            elif mat:
                # It will be earlier than the simple one if we've even checked,
                # but there's a chance that this might be *longer*, or just FIRST.
                pre_lengths = (len(pre_seg_buff), len(best_simple_match[0]))
                mat_lengths = (len(mat), len(best_simple_match[1]))
                mat_indexes = (matchers.index(m), matchers.index(best_simple_match[2]))
                if (
                    (pre_lengths[0] < pre_lengths[1])
                    or (
                        pre_lengths[0] == pre_lengths[1]
                        and mat_lengths[0] > mat_lengths[1]
                    )
                    or (
                        pre_lengths[0] == pre_lengths[1]
                        and mat_lengths[0] == mat_lengths[1]
                        and mat_indexes[0] < mat_indexes[1]
                    )
                ):
                    return (pre_seg_buff, mat, m)
                else:
                    return best_simple_match
            else:
                # If there aren't any matches, then advance the buffer and try again.
                # Two improvements:
                # 1) if we get as far as the first simple match, then return that.
                # 2) be eager in consuming non-code segments if allowed
                if best_simple_match and len(pre_seg_buff) >= len(best_simple_match[0]):
                    return best_simple_match

                pre_seg_buff += (seg_buff[0],)
                seg_buff = seg_buff[1:]

    @classmethod
    def _bracket_sensitive_look_ahead_match(
        cls,
        segments,
        matchers,
        parse_context,
        start_bracket=None,
        end_bracket=None,
        bracket_pairs_set="bracket_pairs",
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
        # Type munging
        matchers = list(matchers)
        if isinstance(segments, BaseSegment):  # pragma: no cover TODO?
            segments = [segments]

        # Have we been passed an empty list?
        if len(segments) == 0:
            return ((), MatchResult.from_unmatched(segments), None)

        # Get hold of the bracket matchers from the dialect, and append them
        # to the list of matchers. We get them from the relevant set on the
        # dialect. We use zip twice to "unzip" them. We ignore the first
        # argument because that's just the name.
        _, start_bracket_refs, end_bracket_refs, persists = zip(
            *parse_context.dialect.sets(bracket_pairs_set)
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
                        # and end tokens are not the same. If a matcher is both a start and
                        # end token we cannot deepen the bracket stack. In general, quoted
                        # strings are a typical example where the start and end tokens are
                        # the same. Currently, though, quoted strings are handled elsewhere
                        # in the parser, and there are no cases where *this* code has to
                        # handle identical start and end brackets. For now, consider this
                        # a small, speculative investment in a possible future requirement.
                        if matcher in start_brackets and matcher not in end_brackets:
                            # Add any segments leading up to this to the previous bracket.
                            bracket_stack[-1].segments += pre
                            # Add a bracket to the stack and add the matches from the segment.
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
                            # but we can work out the name, so we use that for
                            # the lookup.
                            start_index = [
                                bracket.name for bracket in start_brackets
                            ].index(bracket_stack[-1].bracket.name)
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
                                # If we're still in a bracket, add the new segments to that bracket
                                # Otherwise add them to the buffer
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
                                "This shouldn't happen. Panic in _bracket_sensitive_look_ahead_match."
                            )
                    # Not in a bracket stack, but no match.
                    # From here we'll drop out to the happy unmatched exit.
            else:
                # No we're at the end:
                # Now check have we closed all our brackets?
                if bracket_stack:  # pragma: no cover
                    # No we haven't.
                    raise SQLParseError(
                        f"Couldn't find closing bracket for opened brackets: `{bracket_stack}`.",
                        segment=bracket_stack[-1].bracket,
                    )

            # This is the happy unmatched path. This occurs when:
            # - We reached the end with no open brackets.
            # - No match while outside a bracket stack.
            # - We found an unexpected end bracket before matching something interesting.
            # We return with the mutated segments so we can
            # reuse any bracket matching.
            return ((), MatchResult.from_unmatched(pre_seg_buff + seg_buff), None)

    def __str__(self):  # pragma: no cover TODO?
        return repr(self)

    def __repr__(self):
        return "<{}: [{}]>".format(
            self.__class__.__name__,
            curtail_string(
                ", ".join(curtail_string(repr(elem), 40) for elem in self._elements),
                100,
            ),
        )

    def __eq__(self, other):
        """Two grammars are equal if their elements and types are equal.

        NOTE: This could potentially mean that two grammars with
        the same elements but _different configuration_ will be
        classed as the same. If this matters for your use case,
        consider extending this function.

        e.g. `OneOf(foo) == OneOf(foo, optional=True)`
        """
        return type(self) is type(other) and self._elements == other._elements

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

    @cached_method_for_parse_context
    def simple(self, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        A ref is simple, if the thing it references is simple.
        """
        return self._get_elem(dialect=parse_context.dialect).simple(
            parse_context=parse_context
        )

    def _get_ref(self):
        """Get the name of the thing we're referencing."""
        # Unusually for a grammar we expect _elements to be a list of strings.
        # Notable ONE string for now.
        if len(self._elements) == 1:
            # We're good on length. Get the name of the reference
            return self._elements[0]
        else:  # pragma: no cover
            raise ValueError(
                "Ref grammar can only deal with precisely one element for now. Instead found {!r}".format(
                    self._elements
                )
            )

    def _get_elem(self, dialect):
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
    def match(self, segments, parse_context):
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.

        The match element of Ref, also implements the caching
        using the parse_context `denylist` methods.
        """
        elem = self._get_elem(dialect=parse_context.dialect)

        if not elem:  # pragma: no cover
            raise ValueError(f"Null Element returned! _elements: {self._elements!r}")

        # First check against the efficiency Cache.
        # We rely on segments not being mutated within a given
        # match cycle and so the ids should continue to refer to unchanged
        # objects.
        seg_tuple = (id(seg) for seg in segments)
        self_name = self._get_ref()
        if parse_context.denylist.check(self_name, seg_tuple):  # pragma: no cover TODO?
            # This has been tried before.
            parse_match_logging(
                self.__class__.__name__,
                "match",
                "SKIP",
                parse_context=parse_context,
                v_level=3,
                self_name=self_name,
            )
            return MatchResult.from_unmatched(segments)

        # Match against that. NB We're not incrementing the match_depth here.
        # References shouldn't really count as a depth of match.
        with parse_context.matching_segment(self._get_ref()) as ctx:
            resp = elem.match(segments=segments, parse_context=ctx)
        if not resp:
            parse_context.denylist.mark(self_name, seg_tuple)
        return resp

    @classmethod
    def keyword(cls, keyword, **kwargs):
        """Generate a reference to a keyword by name.

        This function is entirely syntactic sugar, and designed
        for more readable dialects.

        Ref.keyword('select') == Ref('SelectKeywordSegment')

        """
        name = keyword.capitalize() + "KeywordSegment"
        return cls(name, **kwargs)


class Anything(BaseGrammar):
    """Matches anything."""

    def match(self, segments, parse_context):
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

    def match(self, segments, parse_context):
        """Matches... nothing.

        Useful for placeholders which might be overwritten by other
        dialects.
        """
        return MatchResult.from_unmatched(segments)
