"""Base grammar, Ref, Anything and Nothing."""

import copy

from ...errors import SQLParseError

from ..segments import BaseSegment, EphemeralSegment
from ..helpers import curtail_string
from ..match_result import MatchResult
from ..match_logging import (
    parse_match_logging,
    LateBoundJoinSegmentsCurtailed,
)
from ..match_wrapper import match_wrapper


class BaseGrammar:
    """Grammars are a way of composing match statements.

    Any grammar must implment the `match` function. Segments can also be
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
            (False, BaseSegment, lambda x: x),
        ]
        # Getout clause for None
        if elem is None:
            return None

        for instance, init_type, init_func in initialisers:
            if (instance and isinstance(elem, init_type)) or (
                not instance and issubclass(elem, init_type)
            ):
                return init_func(elem)
        raise TypeError(
            "Grammar element [{0!r}] was found of unexpected type [{1}] was found.".format(
                elem, type(elem)
            )
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
                with the given name in it's place. The content of this grammar
                is passed to the segment, and will become the parse grammar
                for it. If used widely this is an excellent way of breaking
                up the parse process and also signposting the name of a given
                chunk of code that might be parsed seperately.
        """
        # We provide a common interface for any grammar that allows positional elements.
        # If *any* for the elements are a string and not a grammar, then this is a shortcut
        # to the Ref.keyword grammar by default.
        if self.allow_keyword_string_refs:
            self._elements = []
            for elem in args:
                self._elements.append(self._resolve_ref(elem))
        else:
            self._elements = args

        # Now we deal with the standard kwargs
        self.allow_gaps = allow_gaps
        self.optional = optional
        self.ephemeral_segment = None
        # Set up the ephemeral_segment if name is specified.
        if ephemeral_name:
            # Make the EphemeralSegment class. This is effectively syntactic sugar
            # to allow us to avoid specifying a EphemeralSegment directly in a dialect.

            # Copy self (*before* making the EphemeralSegment, but with everything else in place)
            parse_grammar = copy.copy(self)
            # Add the EphemeralSegment to self.
            self.ephemeral_segment = EphemeralSegment.make(
                match_grammar=None,
                # Pass in the copy without the EphemeralSegment
                parse_grammar=parse_grammar,
                name=ephemeral_name,
            )

    def is_optional(self):
        """Return whether this segment is optional.

        The optional attribute is set in the __init__ method.
        """
        return self.optional

    @match_wrapper()
    def match(self, segments, parse_context):
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        raise NotImplementedError(
            "{0} has no match function implemented".format(self.__class__.__name__)
        )

    def simple(self, parse_context):
        """Does this matcher support a lowercase hash matching route?"""
        return False

    @classmethod
    def _code_only_sensitive_match(
        cls, segments, matcher, parse_context, allow_gaps=True
    ):
        """Match, but also deal with leading and trailing non-code."""
        if allow_gaps:
            seg_buff = segments
            pre_ws = []
            post_ws = []
            # Trim whitespace at the start
            while True:
                if len(seg_buff) == 0:
                    return MatchResult.from_unmatched(segments)
                elif not seg_buff[0].is_code:
                    pre_ws += [seg_buff[0]]
                    seg_buff = seg_buff[1:]
                else:
                    break
            # Trim whitespace at the end
            while True:
                if len(seg_buff) == 0:
                    return MatchResult.from_unmatched(segments)
                elif not seg_buff[-1].is_code:
                    post_ws = [seg_buff[-1]] + post_ws
                    seg_buff = seg_buff[:-1]
                else:
                    break
            m = matcher.match(seg_buff, parse_context)
            if m.is_complete():
                # We need to do more to complete matches. It's complete so
                # we don't need to worry about the unmatched.
                return MatchResult.from_matched(
                    tuple(pre_ws) + m.matched_segments + tuple(post_ws)
                )
            elif m:
                # Incomplete matches, just get it added to the end of the unmatched.
                return MatchResult(
                    matched_segments=tuple(pre_ws) + m.matched_segments,
                    unmatched_segments=m.unmatched_segments + tuple(post_ws),
                )
            else:
                # No match, just return unmatched
                return MatchResult.from_unmatched(segments)
        else:
            # Code only not enabled, so just carry on
            return matcher.match(segments, parse_context)

    @classmethod
    def _longest_code_only_sensitive_match(
        cls, segments, matchers, parse_context, allow_gaps=True
    ):
        """Match like `_code_only_sensitive_match` but return longest match from a selection of matchers.

        Prioritise the first match, and if multiple match at the same point the longest.
        If two matches of the same length match at the same time, then it's the first in
        the iterable of matchers.

        Returns:
            `tuple` of (match_object, matcher).

        """
        # Do some type munging
        matchers = list(matchers)
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # Have we been passed an empty list?
        if len(segments) == 0:
            return MatchResult.from_empty(), None

        matches = []
        # iterate at this position across all the matchers
        for m in matchers:
            res_match = cls._code_only_sensitive_match(
                segments, m, parse_context=parse_context, allow_gaps=allow_gaps
            )
            if res_match.is_complete():
                # Just return it! (WITH THE RIGHT OTHER STUFF)
                return res_match, m
            elif res_match:
                # Add it to the buffer, make sure the buffer is processed
                # and return the longest afterward.
                matches.append((res_match, m))
            else:
                # Don't do much. Carry on.
                pass

        # If we get here, then there wasn't a complete match. Let's iterate
        # through any other matches and return the longest if there is one.
        if matches:
            longest = None
            for mat in matches:
                if longest:
                    # Compare the lengths of the matches
                    if len(mat[0]) > len(longest[0]):
                        longest = mat
                else:
                    longest = mat
            return longest
        else:
            return MatchResult.from_unmatched(segments), None

    @classmethod
    def _look_ahead_match(cls, segments, matchers, parse_context, allow_gaps=True):
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
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # Have we been passed an empty list?
        if len(segments) == 0:
            return ((), MatchResult.from_empty(), None)

        # Here we enable a performance optimisation. Most of the time in this cycle
        # happens in loops looking for simple matchers which we should
        # be able to find a shortcut for.
        # First: Assess the matchers passed in, if any are
        # "simple", then we effectively use a hash lookup across the
        # content of segments to quickly evaluate if the segment is present.
        # Matchers which aren't "simple" still take a slower route.
        simple_matchers = [m for m in matchers if m.simple(parse_context=parse_context)]
        non_simple_matchers = [
            m for m in matchers if not m.simple(parse_context=parse_context)
        ]
        best_simple_match = None
        if simple_matchers:
            # If they're all simple we can use a hash match to identify the first one.
            # Build a buffer of all the upper case raw segments ahead of us.
            str_buff = []
            # For existing compound segments, we should assume that within
            # that segment, things are internally consistent, that means
            # rather than enumerating all the individual segments of a longer
            # one we just dump out the whole segment. This is a) faster and
            # also b) prevents some really horrible bugs with bracket matching.
            # See https://github.com/sqlfluff/sqlfluff/issues/433
            str_buff = [seg.raw_upper for seg in segments]
            match_queue = []

            for m in simple_matchers:
                simple = m.simple(parse_context=parse_context)
                # Simple will be a tuple of options
                for simple_option in simple:
                    try:
                        buff_pos = str_buff.index(simple_option)
                        mat = (m, buff_pos, simple_option)
                        match_queue.append(mat)
                    except ValueError:
                        pass

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
                m_first = match_queue.pop()
                # We've managed to match. We can shortcut home.
                # NB: We may still need to deal with whitespace.
                segments_index = m_first[1]
                # Here we do the actual transform to the new segment.
                matcher = m_first[0]
                match = matcher.match(segments[segments_index:], parse_context)
                if not match:
                    # We've had something match in simple matching, but then later excluded.
                    # Log but then move on to the next item on the list.
                    parse_match_logging(
                        cls.__name__,
                        "_look_ahead_match",
                        "NM",
                        parse_context=parse_context,
                        v_level=4,
                        _so=m_first[2],
                    )
                    continue
                pre_segments = segments[:segments_index]
                if allow_gaps:
                    # Pick up any non-code segments as necessary
                    # ...from the start
                    while True:
                        if not pre_segments or pre_segments[-1].is_code:
                            break
                        else:
                            match = MatchResult(
                                (pre_segments[-1],) + match.matched_segments,
                                match.unmatched_segments,
                            )
                            pre_segments = pre_segments[:-1]
                    # ...from the end (but only if it's the whole of the rest,
                    # otherwise assume the next matcher will pick it up)
                    if all(not elem.is_code for elem in match.unmatched_segments):
                        match = MatchResult.from_matched(
                            match.matched_segments + match.unmatched_segments
                        )
                best_simple_match = (pre_segments, match, m_first[0])

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
            mat, m = cls._longest_code_only_sensitive_match(
                seg_buff,
                non_simple_matchers,
                parse_context=parse_context,
                allow_gaps=allow_gaps,
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

                if allow_gaps:
                    while seg_buff and not seg_buff[0].is_code:
                        pre_seg_buff += (seg_buff[0],)
                        seg_buff = seg_buff[1:]

    @classmethod
    def _bracket_sensitive_look_ahead_match(
        cls, segments, matchers, parse_context, allow_gaps=True
    ):
        """Same as `_look_ahead_match` but with bracket counting.

        NB: Given we depend on `_look_ahead_match` we can also utilise
        the same performance optimisations which are implemented there.

        Returns:
            `tuple` of (unmatched_segments, match_object, matcher).

        """
        # Type munging
        matchers = list(matchers)
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # Have we been passed an empty list?
        if len(segments) == 0:
            return ((), MatchResult.from_unmatched(segments), None)

        # Get hold of the bracket matchers from the dialect, and append them
        # to the list of matchers.
        # TODO: Potentially have error handling here for dialects without
        # square brackets.
        start_brackets = [
            parse_context.dialect.ref("StartBracketSegment"),
            parse_context.dialect.ref("StartSquareBracketSegment"),
        ]
        end_brackets = [
            parse_context.dialect.ref("EndBracketSegment"),
            parse_context.dialect.ref("EndSquareBracketSegment"),
        ]
        bracket_matchers = start_brackets + end_brackets
        matchers += bracket_matchers

        # Make some buffers
        seg_buff = segments
        pre_seg_buff = ()  # NB: Tuple
        bracket_stack = []

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
                        allow_gaps=allow_gaps,
                    )

                    if match:
                        if matcher in start_brackets:
                            # Same procedure as below in finding brackets.
                            bracket_stack.append(match.matched_segments[0])
                            pre_seg_buff += pre
                            pre_seg_buff += match.matched_segments
                            seg_buff = match.unmatched_segments
                            continue
                        elif matcher in end_brackets:
                            # We've found an end bracket, remove it from the
                            # stack and carry on.
                            bracket_stack.pop()
                            pre_seg_buff += pre
                            pre_seg_buff += match.matched_segments
                            seg_buff = match.unmatched_segments
                            continue
                        else:
                            raise RuntimeError("I don't know how we get here?!")
                    else:
                        # No match and we're in a bracket stack. Raise an error
                        raise SQLParseError(
                            "Couldn't find closing bracket for opening bracket.",
                            segment=bracket_stack.pop(),
                        )
                else:
                    # No, we're open to more opening brackets or the thing(s)
                    # that we're otherwise looking for.
                    pre, match, matcher = cls._look_ahead_match(
                        seg_buff,
                        matchers,
                        parse_context=parse_context,
                        allow_gaps=allow_gaps,
                    )

                    if match:
                        if matcher in start_brackets:
                            # We've found the start of a bracket segment.
                            # NB: It might not *Actually* be the bracket itself,
                            # but could be some non-code element preceeding it.
                            # That's actually ok.

                            # Add the bracket to the stack.
                            bracket_stack.append(match.matched_segments[0])
                            # Add the matched elements and anything before it to the
                            # pre segment buffer. Reset the working buffer.
                            pre_seg_buff += pre
                            pre_seg_buff += match.matched_segments
                            seg_buff = match.unmatched_segments
                            continue
                        elif matcher in end_brackets:
                            # We've found an unexpected end bracket!
                            raise SQLParseError(
                                "Found unexpected end bracket!",
                                segment=match.matched_segments[0],
                            )
                        else:
                            # It's one of the things we were looking for!
                            # Return.
                            return (pre_seg_buff + pre, match, matcher)
                    else:
                        # Not in a bracket stack, but no match. This is a happy
                        # unmatched exit.
                        return ((), MatchResult.from_unmatched(segments), None)
            else:
                # No we're at the end:
                # Now check have we closed all our brackets?
                if bracket_stack:
                    # No we haven't.
                    # TODO: Format this better
                    raise SQLParseError(
                        "Couldn't find closing bracket for opening bracket.",
                        segment=bracket_stack.pop(),
                    )

                # We at the end but without a bracket left open. This is a
                # friendly unmatched return.
                return ((), MatchResult.from_unmatched(segments), None)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "<{0}: [{1}]>".format(
            self.__class__.__name__,
            curtail_string(
                ", ".join(curtail_string(repr(elem), 40) for elem in self._elements),
                100,
            ),
        )


class Ref(BaseGrammar):
    """A kind of meta-grammar that references other grammars by name at runtime."""

    # We can't allow keyword refs here, because it doesn't make sense
    # and it also causes infinite recursion.
    allow_keyword_string_refs = False

    def simple(self, parse_context):
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
        else:
            raise ValueError(
                "Ref grammar can only deal with precisely one element for now. Instead found {0!r}".format(
                    self._elements
                )
            )

    def _get_elem(self, dialect):
        """Get the actual object we're referencing."""
        if dialect:
            # Use the dialect to retrieve the grammar it refers to.
            return dialect.ref(self._get_ref())
        else:
            raise ReferenceError("No Dialect has been provided to Ref grammar!")

    def __repr__(self):
        return "<Ref: {0}{1}>".format(
            ", ".join(self._elements), " [opt]" if self.is_optional() else ""
        )

    @match_wrapper(v_level=4)  # Log less for Ref
    def match(self, segments, parse_context):
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.

        The match element of Ref, also implements the caching
        using the parse_context `blacklist` methods.
        """
        elem = self._get_elem(dialect=parse_context.dialect)

        if not elem:
            raise ValueError(
                "Null Element returned! _elements: {0!r}".format(self._elements)
            )

        # First check against the efficiency Cache.
        # We used to use seg_to_tuple here, but it was too slow,
        # so instead we rely on segments not being mutated within a given
        # match cycle and so the ids should continue to refer to unchanged
        # objects.
        seg_tuple = (id(seg) for seg in segments)
        self_name = self._get_ref()
        if parse_context.blacklist.check(self_name, seg_tuple):
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
        # References shouldn't relly count as a depth of match.
        with parse_context.matching_segment(self._get_ref()) as ctx:
            resp = elem.match(segments=segments, parse_context=ctx)
        if not resp:
            parse_context.blacklist.mark(self_name, seg_tuple)
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

        Most useful in match grammars, where a later parse grammmar
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
