"""Definitions for Grammar."""
import logging

from .segments_base import (BaseSegment, check_still_complete, parse_match_logging)
from .match import MatchResult, join_segments_raw_curtailed
from ..errors import SQLParseError
from ..helpers import get_time


class BaseGrammar(object):
    """Grammars are a way of composing match statements.

    Any grammar must implment the `match` function. Segments can also be
    passed to most grammars. Segments implement `match` as a classmethod. Grammars
    implement it as an instance method.

    """
    v_level = 3

    def __init__(self, *args, **kwargs):
        """Deal with kwargs common to all grammars."""
        # We provide a common interface for any grammar that allows positional elements
        self._elements = args
        # Now we deal with the standard kwargs
        for var, default in [('code_only', True), ('optional', False)]:
            setattr(self, var, kwargs.pop(var, default))
        # optional, only really makes sense in the context of a sequence.
        # If a grammar is optional, then a sequence can continue without it.
        if kwargs:
            raise ValueError("Unconsumed kwargs is creation of grammar: {0}\nExcess: {1}".format(
                self.__class__.__name__,
                kwargs
            ))

    def is_optional(self):
        """Return whether this segment is optional.

        The optional attribute is set in the __init__ method.
        """
        return self.optional

    def match(self, segments, parse_context):
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        raise NotImplementedError("{0} has no match function implemented".format(self.__class__.__name__))

    def _match(self, segments, parse_context):
        """A wrapper on the match function to do some basic validation."""
        t0 = get_time()

        if isinstance(segments, BaseSegment):
            segments = segments,  # Make into a tuple for compatability
        if not isinstance(segments, tuple):
            logging.warning(
                "{0}.match, was passed {1} rather than tuple or segment".format(
                    self.__class__.__name__, type(segments)))
            if isinstance(segments, list):
                # Let's make it a tuple for compatibility
                segments = tuple(segments)

        if len(segments) == 0:
            logging.info("{0}.match, was passed zero length segments list. NB: {0} contains {1!r}".format(
                self.__class__.__name__, self._elements))

        # Work out the raw representation and curtail if long
        parse_match_logging(
            self.__class__.__name__, '_match', 'IN', parse_context=parse_context,
            v_level=self.v_level,
            le=len(self._elements), ls=len(segments),
            seg=join_segments_raw_curtailed(segments))

        m = self.match(segments, parse_context=parse_context)

        if not isinstance(m, MatchResult):
            logging.warning(
                "{0}.match, returned {1} rather than MatchResult".format(
                    self.__class__.__name__, type(m)))

        dt = get_time() - t0
        if m.is_complete():
            msg = 'OUT ++'
        elif m:
            msg = 'OUT -'
        else:
            msg = 'OUT'

        parse_match_logging(
            self.__class__.__name__, '_match', msg,
            parse_context=parse_context, v_level=self.v_level, dt=dt, m=m)

        # Basic Validation
        check_still_complete(segments, m.matched_segments, m.unmatched_segments)
        return m

    def expected_string(self, dialect=None, called_from=None):
        """Return a String which is helpful to understand what this grammar expects."""
        raise NotImplementedError(
            "{0} does not implement expected_string!".format(
                self.__class__.__name__))

    @classmethod
    def _code_only_sensitive_match(cls, segments, matcher, parse_context, code_only=True):
        """Match, but also deal with leading and trailing non-code."""
        if code_only:
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
            m = matcher._match(seg_buff, parse_context)
            if m.is_complete():
                # We need to do more to complete matches. It's complete so
                # we don't need to worry about the unmatched.
                return MatchResult.from_matched(tuple(pre_ws) + m.matched_segments + tuple(post_ws))
            elif m:
                # Incomplete matches, just get it added to the end of the unmatched
                return MatchResult(
                    matched_segments=tuple(pre_ws) + m.matched_segments,
                    unmatched_segments=m.unmatched_segments + tuple(post_ws))
            else:
                # No match, just return unmatched
                return MatchResult.from_unmatched(segments)
        else:
            # Code only not enabled, so just carry on
            return matcher._match(segments, parse_context)

    @classmethod
    def _longest_code_only_sensitive_match(cls, segments, matchers, parse_context, code_only=True):
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
                segments, m, parse_context=parse_context,
                code_only=code_only)
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
    def _look_ahead_match(cls, segments, matchers, parse_context, code_only=True):
        """Look ahead for matches beyond the first element of the segments list.

        Look ahead in a bracket sensitive way to find the next occurance of a particular
        matcher(s). When a match is found, it is returned, along with any preceeding
        (unmatched) segments, and a reference to the matcher which eventually matched it.

        The intent is that this will become part of the bracket matching routines.

        Prioritise the first match, and if multiple match at the same point the longest.
        If two matches of the same length match at the same time, then it's the first in
        the iterable of matchers.

        Returns:
            `tuple` of (unmatched_segments, match_object, matcher).

        """
        # Do some type munging
        matchers = list(matchers)
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # Have we been passed an empty list?
        if len(segments) == 0:
            return ((), MatchResult.from_empty(), None)

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

            mat, m = cls._longest_code_only_sensitive_match(
                seg_buff, matchers, parse_context=parse_context, code_only=code_only)

            if mat:
                return (pre_seg_buff, mat, m)
            else:
                # If there aren't any matches, then advance the buffer and try again.
                pre_seg_buff += seg_buff[0],
                seg_buff = seg_buff[1:]

    @classmethod
    def _bracket_sensitive_look_ahead_match(cls, segments, matchers, parse_context, code_only=True):
        """Same as `_look_ahead_match` but with bracket counting.

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
        start_bracket = parse_context.dialect.ref('StartBracketSegment')
        end_bracket = parse_context.dialect.ref('EndBracketSegment')
        bracket_matchers = [start_bracket, end_bracket]
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
                        seg_buff, bracket_matchers, parse_context=parse_context,
                        code_only=code_only)

                    if match:
                        if matcher is start_bracket:
                            # Same procedure as below in finding brackets.
                            bracket_stack.append(match.matched_segments[0])
                            pre_seg_buff += pre
                            pre_seg_buff += match.matched_segments
                            seg_buff = match.unmatched_segments
                            continue
                        elif matcher is end_bracket:
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
                            segment=bracket_stack.pop())
                else:
                    # No, we're open to more opening brackets or the thing(s)
                    # that we're otherwise looking for.
                    pre, match, matcher = cls._look_ahead_match(
                        seg_buff, matchers, parse_context=parse_context,
                        code_only=code_only)

                    if match:
                        if matcher is start_bracket:
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
                        elif matcher is end_bracket:
                            # We've found an unexpected end bracket!
                            raise SQLParseError(
                                "Found unexpected end bracket!",
                                segment=match.matched_segments[0])
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
                        segment=bracket_stack.pop())
                else:
                    # We at the end but without a bracket left open. This is a
                    # friendly unmatched return.
                    return ((), MatchResult.from_unmatched(segments), None)


class Ref(BaseGrammar):
    """A kind of meta-grammar that references other grammars by name at runtime."""
    # Log less for Ref
    v_level = 4

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
                    self._elements))

    def _get_elem(self, dialect):
        """Get the actual object we're referencing."""
        if dialect:
            # Use the dialect to retrieve the grammar it refers to.
            return dialect.ref(self._get_ref())
        else:
            raise ReferenceError("No Dialect has been provided to Ref grammar!")

    def match(self, segments, parse_context):
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        elem = self._get_elem(dialect=parse_context.dialect)

        if elem:
            # Match against that. NB We're not incrementing the match_depth here.
            # References shouldn't relly count as a depth of match.
            return elem._match(
                segments=segments,
                parse_context=parse_context.copy(match_segment=self._get_ref()))
        else:
            raise ValueError("Null Element returned! _elements: {0!r}".format(self._elements))

    def expected_string(self, dialect=None, called_from=None):
        """Get the expected string from the referenced element."""
        elem = self._get_elem(dialect=dialect)
        if called_from and self._get_ref() in called_from:
            # This means we're in recursion so we should stop here.
            # At the moment this means we'll just insert in the name
            # of the segment that we're looking for.
            # Otherwise we get an infinite recursion error
            # TODO: Make this more elegant
            return self._get_ref()
        else:
            # Either add to set or make set
            if called_from:
                called_from.add(self._get_ref())
            else:
                called_from = {self._get_ref()}
            return elem.expected_string(dialect=dialect, called_from=called_from)


class Anything(BaseGrammar):
    """Matches anything."""

    def match(self, segments, parse_context):
        """Matches... Anything.

        Most useful in match grammars, where a later parse grammmar
        will work out what's inside.
        """
        return MatchResult.from_matched(segments)

    def expected_string(self, dialect=None, called_from=None):
        """A hint to the user on what this grammar expects."""
        return " <anything> "


class OneOf(BaseGrammar):
    """Match any of the elements given once.

    If it matches multiple, it returns the longest, and if any are the same
    length it returns the first (unless we explicitly just match first).
    """

    def __init__(self, *args, **kwargs):
        self.mode = kwargs.pop('mode', 'longest')  # can be 'first' or 'longest'
        super(OneOf, self).__init__(*args, **kwargs)

    def match(self, segments, parse_context):
        """Match any of the elements given once.

        If it matches multiple, it returns the longest, and if any are the same
        length it returns the first (unless we explicitly just match first).
        """
        best_match = None
        # Match on each of the options
        for opt in self._elements:
            m = opt._match(
                segments,
                parse_context=parse_context.copy(incr='match_depth')
            )
            # If we get a complete match, just return it. If it's incomplete, then check to
            # see if it's all non-code if that allowed and match it
            if m.is_complete():
                # this will return on the *first* complete match
                return m
            elif m:
                if self.code_only:
                    # Attempt to consume whitespace if we can
                    matched_segments = m.matched_segments
                    unmatched_segments = m.unmatched_segments
                    while True:
                        if len(unmatched_segments) > 0:
                            if unmatched_segments[0].is_code:
                                break
                            else:
                                # Append as tuple
                                matched_segments += unmatched_segments[0],
                                unmatched_segments = unmatched_segments[1:]
                        else:
                            break
                    m = MatchResult(matched_segments, unmatched_segments)
                if best_match:
                    if len(m) > len(best_match):
                        best_match = m
                    else:
                        continue
                else:
                    best_match = m
                parse_match_logging(
                    self.__class__.__name__,
                    '_match', "Saving Match of Length {0}:  {1}".format(len(m), m),
                    parse_context=parse_context, v_level=self.v_level)
        else:
            # No full match from the first time round. If we've got a long partial match then return that.
            if best_match:
                return best_match
            # Ok so no match at all from the elements. Small getout if we can match any whitespace
            if self.code_only:
                matched_segs = tuple()
                unmatched_segs = segments
                # Look for non-code up front
                while True:
                    if len(unmatched_segs) == 0:
                        # We can't return a successful match on JUST whitespace
                        return MatchResult.from_unmatched(segments)
                    elif not unmatched_segs[0].is_code:
                        matched_segs += unmatched_segs[0],
                        unmatched_segs = unmatched_segs[1:]
                    else:
                        break
                # Now try and match
                for opt in self._elements:
                    m = opt._match(unmatched_segs, parse_context=parse_context.copy(incr='match_depth'))
                    # Once again, if it's complete - return, if not wait to see if we get a more complete one
                    new_match = MatchResult(matched_segs + m.matched_segments, m.unmatched_segments)
                    if m.is_complete():
                        return new_match
                    elif m:
                        if best_match:
                            if len(best_match) > len(m):
                                best_match = m
                            else:
                                continue
                        else:
                            best_match = m
                        parse_match_logging(
                            self.__class__.__name__,
                            '_match', "Last-Ditch: Saving Match of Length {0}:  {1}".format(len(m), m),
                            parse_context=parse_context, v_level=self.v_level)
                else:
                    if best_match:
                        return MatchResult(matched_segs + best_match.matched_segments, best_match.unmatched_segments)
                    else:
                        return MatchResult.from_unmatched(segments)

    def expected_string(self, dialect=None, called_from=None):
        """Get the expected string from the referenced element."""
        return " | ".join([opt.expected_string(dialect=dialect, called_from=called_from) for opt in self._elements])


class AnyNumberOf(BaseGrammar):
    """A more configurable version of OneOf."""

    def __init__(self, *args, **kwargs):
        self.max_times = kwargs.pop('max_times', None)
        self.min_times = kwargs.pop('min_times', 0)
        super(AnyNumberOf, self).__init__(*args, **kwargs)

    def is_optional(self):
        """Return whether this element is optional.

        This is mostly set in the init method, but also in this
        case, if min_times is zero then this is also optional.
        """
        return self.optional or self.min_times == 0

    def match(self, segments, parse_context):
        """Match against any of the elements any number of times."""
        # Match on each of the options
        matched_segments = MatchResult.from_empty()
        unmatched_segments = segments
        n_matches = 0
        while True:
            if self.max_times and n_matches >= self.max_times:
                # We've matched as many times as we can
                return MatchResult(matched_segments.matched_segments, unmatched_segments)

            # Is there anything left to match?
            if len(unmatched_segments) == 0:
                # No...
                if n_matches >= self.min_times:
                    return MatchResult(matched_segments.matched_segments, unmatched_segments)
                else:
                    # We didn't meet the hurdle
                    return MatchResult.from_unmatched(unmatched_segments)

            # Is the next segment code?
            if self.code_only and not unmatched_segments[0].is_code:
                # We should add this one to the match and carry on
                matched_segments += unmatched_segments[0],
                unmatched_segments = unmatched_segments[1:]
                check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)
                continue

            # Try the possibilities
            for opt in self._elements:
                m = opt._match(
                    unmatched_segments,
                    parse_context=parse_context.copy(incr='match_depth')
                )
                if m.has_match():
                    matched_segments += m.matched_segments
                    unmatched_segments = m.unmatched_segments
                    n_matches += 1
                    # Break out of the for loop which cycles us round
                    break
            else:
                # If we get here, then we've not managed to match. And the next
                # unmatched segments are meaningful, i.e. they're not what we're
                # looking for.
                if n_matches >= self.min_times:
                    return MatchResult(matched_segments.matched_segments, unmatched_segments)
                else:
                    # We didn't meet the hurdle
                    return MatchResult.from_unmatched(unmatched_segments)

    def expected_string(self, dialect=None, called_from=None):
        """Get the expected string from the referenced element."""
        # TODO: Make something nice here
        return " !!TODO!! "


class GreedyUntil(BaseGrammar):
    """Matching for GreedyUntil works just how you'd expect."""
    def match(self, segments, parse_context):
        """Matching for GreedyUntil works just how you'd expect."""
        pre, mat, _ = self._bracket_sensitive_look_ahead_match(
            segments, self._elements, parse_context=parse_context.copy(incr='match_depth'),
            code_only=self.code_only)

        # Do we have a match?
        if mat:
            # Return everything up to the match
            return MatchResult(pre, mat.all_segments())
        else:
            # Return everything
            return MatchResult.from_matched(segments)

    def expected_string(self, dialect=None, called_from=None):
        """Get the expected string from the referenced element."""
        return "..., " + " !( " + " | ".join(
            [opt.expected_string(dialect=dialect, called_from=called_from) for opt in self._elements]
        ) + " ) "


class Sequence(BaseGrammar):
    """Match a specific sequence of elements."""

    def match(self, segments, parse_context):
        """Match a specific sequence of elements."""
        if isinstance(segments, BaseSegment):
            segments = tuple(segments)

        matched_segments = MatchResult.from_empty()
        unmatched_segments = segments

        for idx, elem in enumerate(self._elements):
            while True:
                if len(unmatched_segments) == 0:
                    # We've run our of sequence without matching everyting.
                    # Do only optional elements remain.
                    if all([e.is_optional() for e in self._elements[idx:]]):
                        # then it's ok, and we can return what we've got so far.
                        # No need to deal with anything left over because we're at the end.
                        return matched_segments
                    else:
                        # we've got to the end of the sequence without matching all
                        # required elements.
                        return MatchResult.from_unmatched(segments)
                else:
                    # We're not at the end, first detect whitespace and then try to match.
                    if self.code_only and not unmatched_segments[0].is_code:
                        # We should add this one to the match and carry on
                        matched_segments += unmatched_segments[0],
                        unmatched_segments = unmatched_segments[1:]
                        check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)
                        continue

                    # It's not whitespace, so carry on to matching
                    elem_match = elem._match(
                        unmatched_segments, parse_context=parse_context.copy(incr='match_depth'))

                    if elem_match.has_match():
                        # We're expecting mostly partial matches here, but complete
                        # matches are possible.
                        matched_segments += elem_match.matched_segments
                        unmatched_segments = elem_match.unmatched_segments
                        # Each time we do this, we do a sense check to make sure we haven't
                        # dropped anything. (Because it's happened before!).
                        check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)

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
        else:
            # If we get to here, we've matched all of the elements (or skipped them)
            # but still have some segments left (or perhaps have precisely zero left).
            # In either case, we're golden. Return successfully, with any leftovers as
            # the unmatched elements. UNLESS they're whitespace and we should be greedy.
            if self.code_only:
                while True:
                    if len(unmatched_segments) == 0:
                        break
                    elif not unmatched_segments[0].is_code:
                        # We should add this one to the match and carry on
                        matched_segments += unmatched_segments[0],
                        unmatched_segments = unmatched_segments[1:]
                        check_still_complete(segments, matched_segments.matched_segments, unmatched_segments)
                        continue
                    else:
                        break

            return MatchResult(matched_segments.matched_segments, unmatched_segments)

    def expected_string(self, dialect=None, called_from=None):
        """Get the expected string from the referenced element."""
        return ", ".join([opt.expected_string(dialect=dialect, called_from=called_from) for opt in self._elements])


class Delimited(BaseGrammar):
    """Match an arbitrary number of elements seperated by a delimiter.

    Note that if there are multiple elements passed in that they will be treated
    as different options of what can be delimited, rather than a sequence.
    """

    def __init__(self, *args, **kwargs):
        if 'delimiter' not in kwargs:
            raise ValueError("Delimited grammars require a `delimiter`")
        self.delimiter = kwargs.pop('delimiter')
        self.allow_trailing = kwargs.pop('allow_trailing', False)
        self.terminator = kwargs.pop('terminator', None)
        # Setting min delimiters means we have to match at least this number
        self.min_delimiters = kwargs.pop('min_delimiters', None)
        super(Delimited, self).__init__(*args, **kwargs)

    def match(self, segments, parse_context):
        """Match an arbitrary number of elements seperated by a delimiter.

        Note that if there are multiple elements passed in that they will be treated
        as different options of what can be delimited, rather than a sequence.
        """
        # Type munging
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # Have we been passed an empty list?
        if len(segments) == 0:
            return MatchResult.from_empty()

        # Make some buffers
        seg_buff = segments
        matched_segments = MatchResult.from_empty()
        # delimiters is a list of tuples containing delimiter segments as we find them.
        delimiters = []

        # First iterate through all the segments, looking for the delimiter.
        # Second, split the list on each of the delimiters, and ensure that
        # each sublist in turn matches one of the elements.

        # In more detail, match against delimiter, if we match, put a slice
        # up to that point onto a list of slices. Carry on.
        while True:
            # Check to see whether we've exhausted the buffer (or it's all non-code)
            if len(seg_buff) == 0 or (self.code_only and all([not s.is_code for s in seg_buff])):
                # Append the remaining buffer in case we're in the not is_code case.
                matched_segments += seg_buff
                # Nothing left, this is potentially a trailling case?
                if self.allow_trailing and (self.min_delimiters is None or len(delimiters) >= self.min_delimiters):
                    # It is! (nothing left so no unmatched segments to append)
                    return matched_segments
                else:
                    MatchResult.from_unmatched(segments)

            # We rely on _bracket_sensitive_look_ahead_match to do the bracket counting
            # element of this now. We look ahead to find a delimiter or terminator.
            matchers = [self.delimiter]
            if self.terminator:
                matchers.append(self.terminator)
            pre, mat, m = self._bracket_sensitive_look_ahead_match(
                seg_buff, matchers, parse_context=parse_context.copy(incr='match_depth'),
                # NB: We don't want whitespace at this stage, that should default to
                # being passed to the elements in between.
                code_only=False)

            # Have we found a delimiter or terminator looking forward?
            if mat:
                if m is self.delimiter:
                    # Yes. Store it and then match the contents up to now.
                    delimiters.append(mat.matched_segments)
                # We now test the intervening section as to whether it matches one
                # of the things we're looking for. NB: If it's of zero length then
                # we return without trying it.
                if len(pre) > 0:
                    for elem in self._elements:
                        # We use the whitespace padded match to hoover up whitespace if enabled.
                        elem_match = self._code_only_sensitive_match(
                            pre, elem, parse_context=parse_context.copy(incr='match_depth'),
                            # This is where the configured code_only behaviour kicks in.
                            code_only=self.code_only)

                        if elem_match.is_complete():
                            # First add the segment up to the delimiter to the matched segments
                            matched_segments += elem_match
                            # Then it depends what we matched.
                            # Delimiter
                            if m is self.delimiter:
                                # Then add the delimiter to the matched segments
                                matched_segments += mat.matched_segments
                                # Break this for loop and move on, looking for the next delimiter
                                seg_buff = mat.unmatched_segments
                                # Still got some buffer left. Carry on.
                                break
                            # Terminator
                            elif m is self.terminator:
                                # We just return straight away here. We don't add the terminator to
                                # this match, it should go with the unmatched parts.

                                # First check we've had enough delimiters
                                if self.min_delimiters and len(delimiters) < self.min_delimiters:
                                    return MatchResult.from_unmatched(segments)
                                else:
                                    return MatchResult(
                                        matched_segments.matched_segments,
                                        mat.all_segments())
                            else:
                                raise RuntimeError(
                                    ("I don't know how I got here. Matched instead on {0}, which "
                                     "doesn't appear to be delimiter or terminator").format(m))
                        else:
                            # We REQUIRE a complete match here between delimiters or up to a
                            # terminator. If it's only partial then we don't want it.
                            # NB: using the sensitive match above deals with whitespace
                            # appropriately.
                            continue
                    else:
                        # None of them matched, return unmatched.
                        return MatchResult.from_unmatched(segments)
                else:
                    # Zero length section between delimiters. Return unmatched.
                    return MatchResult.from_unmatched(segments)
            else:
                # No match for a delimiter looking forward, this means we're
                # at the end. In this case we look for a potential partial match
                # looking forward. We know it's a non-zero length section because
                # we checked that up front.

                # First check we're had enough delimiters, because if we haven't then
                # there's no sense to try matching
                if self.min_delimiters and len(delimiters) < self.min_delimiters:
                    return MatchResult.from_unmatched(segments)

                # We use the whitespace padded match to hoover up whitespace if enabled,
                # and default to the longest matcher. We don't care which one matches.
                mat, _ = self._longest_code_only_sensitive_match(
                    seg_buff, self._elements, parse_context=parse_context.copy(incr='match_depth'),
                    code_only=self.code_only)
                if mat:
                    # We've got something at the end. Return!
                    return MatchResult(
                        matched_segments.matched_segments + mat.matched_segments,
                        mat.unmatched_segments
                    )
                else:
                    # No match at the end, are we allowed to trail? If we are then return,
                    # otherwise we fail because we can't match the last element.
                    if self.allow_trailing:
                        return MatchResult(matched_segments.matched_segments, seg_buff)
                    else:
                        return MatchResult.from_unmatched(segments)

    def expected_string(self, dialect=None, called_from=None):
        """Get the expected string from the referenced element."""
        return " {0} ".format(
            self.delimiter.expected_string(dialect=dialect, called_from=called_from)).join(
                [opt.expected_string(dialect=dialect, called_from=called_from) for opt in self._elements])


class ContainsOnly(BaseGrammar):
    """Match if the sequence contains only matches.

    In this grammar we allow not just elements with a `match` method,
    but also to match by name if a string is one of the elements. This
    exists mostly as legacy functionality.
    """
    def match(self, segments, parse_context):
        """Match if the sequence contains segments that match an element."""
        matched_buffer = tuple()
        forward_buffer = segments
        while True:
            if len(forward_buffer) == 0:
                # We're all good
                return MatchResult.from_matched(matched_buffer)
            elif self.code_only and not forward_buffer[0].is_code:
                matched_buffer += forward_buffer[0],
                forward_buffer = forward_buffer[1:]
            else:
                # Try and match it
                for opt in self._elements:
                    if isinstance(opt, str):
                        if forward_buffer[0].type == opt:
                            matched_buffer += forward_buffer[0],
                            forward_buffer = forward_buffer[1:]
                            break
                    else:
                        m = opt._match(
                            forward_buffer, parse_context=parse_context.copy(incr='match_depth'))
                        if m:
                            matched_buffer += m.matched_segments
                            forward_buffer = m.unmatched_segments
                            break
                else:
                    # Unable to match the forward buffer. We must have found something
                    # which isn't on our element list. Crash out.
                    return MatchResult.from_unmatched(segments)

    def expected_string(self, dialect=None, called_from=None):
        """Get the expected string from the referenced element."""
        buff = []
        for opt in self._elements:
            if isinstance(opt, str):
                buff.append(opt)
            else:
                buff.append(opt.expected_string(dialect=dialect, called_from=called_from))
        return " ( " + " | ".join(buff) + " | + )"


class StartsWith(BaseGrammar):
    """Match if this sequence starts with a match.

    This also has configurable whitespace and comment handling.
    """
    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.terminator = kwargs.pop('terminator', None)
        self.include_terminator = kwargs.pop('include_terminator', False)
        super(StartsWith, self).__init__(*args, **kwargs)

    def match(self, segments, parse_context):
        """Match if this sequence starts with a match."""
        if self.code_only:
            first_code_idx = None
            # Work through to find the first code segment...
            for idx, seg in enumerate(segments):
                if seg.is_code:
                    first_code_idx = idx
                    break
            else:
                # We've trying to match on a sequence of segments which contain no code.
                # That means this isn't a match.
                return MatchResult.from_unmatched(segments)

            match = self.target._match(
                segments=segments[first_code_idx:],
                parse_context=parse_context.copy(incr='match_depth'))
            if match:
                # The match will probably have returned a mutated version rather
                # that the raw segment sent for matching. We need to reinsert it
                # back into the sequence in place of the raw one, but we can't
                # just assign at the index because it's a tuple and not a list.
                # to get around that we do this slightly more elaborate construction.

                # NB: This match may be partial or full, either is cool. In the case
                # of a partial match, given that we're only interested in what it STARTS
                # with, then we can still used the unmatched parts on the end.
                # We still need to deal with any non-code segments at the start.
                if self.terminator:
                    # We have an optional terminator. We should only match up to when
                    # this matches. This should also respect bracket counting.
                    match_segments = match.matched_segments
                    trailing_segments = match.unmatched_segments

                    # Given a set of segments, iterate through looking for
                    # a terminator.
                    res = self._bracket_sensitive_look_ahead_match(
                        segments=trailing_segments, matchers=[self.terminator],
                        parse_context=parse_context
                    )

                    # Depending on whether we found a terminator or not we treat
                    # the result slightly differently. If no terminator was found,
                    # we just use the whole unmatched segment. If we did find one,
                    # we match up until (but not including [unless self.include_terminator
                    # is true]) that terminator.
                    term_match = res[1]
                    if term_match:
                        if self.include_terminator:
                            m_tail = res[0] + term_match.matched_segments
                            u_tail = term_match.unmatched_segments
                        else:
                            m_tail = res[0]
                            u_tail = term_match.all_segments()
                    else:
                        m_tail = term_match.unmatched_segments
                        u_tail = ()

                    return MatchResult(
                        segments[:first_code_idx]
                        + match_segments
                        + m_tail,
                        u_tail,
                    )
                else:
                    return MatchResult.from_matched(
                        segments[:first_code_idx]
                        + match.all_segments())
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError("Not expecting to match StartsWith and also not just code!?")

    def expected_string(self, dialect=None, called_from=None):
        """Get the expected string from the referenced element."""
        return self.target.expected_string(dialect=dialect, called_from=called_from) + ", ..."


class Bracketed(BaseGrammar):
    """Match if this is a bracketed sequence, with content that matches one of the elements.

    Bracketed works differently to sequence, although it used to work
    the same. Note that if multiple arguments are passed then the options
    will be considered as options for what can be in the brackets rather
    than a sequence. The elements used for matching the brackets themselves
    are taken directly from the dialect.
    """
    def __init__(self, *args, **kwargs):
        # Start and end tokens
        # The details on how to match a bracket are stored in the dialect
        self.start_bracket = Ref('StartBracketSegment')
        self.end_bracket = Ref('EndBracketSegment')
        super(Bracketed, self).__init__(*args, **kwargs)

    def match(self, segments, parse_context):
        """Match if this is a bracketed sequence, with content that matches one of the elements.

        1. work forwards to find the first bracket.
           If we find something other that whitespace, then fail out.
        2. Once we have the first bracket, we need to bracket count forward to find it's partner.
        3. Assuming we find it's partner then we try and match what goes between them.
           If we match, great. If not, then we return an empty match.
           If we never find it's partner then we return an empty match but should probably
           log a parsing warning, or error?

        """
        seg_buff = segments
        matched_segs = ()

        # Look for the first bracket
        start_match = self._code_only_sensitive_match(
            seg_buff, self.start_bracket,
            parse_context=parse_context.copy(incr='match_depth'),
            code_only=self.code_only)
        if start_match:
            seg_buff = start_match.unmatched_segments
        else:
            # Can't find the opening bracket. No Match.
            return MatchResult.from_unmatched(segments)

        # Look for the closing bracket
        pre, end_match, _ = self._bracket_sensitive_look_ahead_match(
            segments=seg_buff, matchers=[self.end_bracket],
            parse_context=parse_context, code_only=self.code_only
        )
        if not end_match:
            raise SQLParseError(
                "Couldn't find closing bracket for opening bracket.",
                segment=matched_segs)

        # Match the content now we've confirmed the brackets. We use the
        # _longest helper function mostly just because it deals with multiple
        # matchers.
        content_match, _ = self._longest_code_only_sensitive_match(
            pre, self._elements,
            parse_context=parse_context.copy(incr='match_depth'),
            code_only=self.code_only)

        # We require a complete match for the content (hopefully for obvious reasons)
        if content_match.is_complete():
            return MatchResult(
                start_match.matched_segments
                + content_match.matched_segments
                + end_match.matched_segments,
                end_match.unmatched_segments)
        else:
            # Now if we've not matched there's a final option. If the content is optional
            # and we allow non-code, then if the content is all non-code then it could be
            # empty brackets and still match.
            if (
                all([e.is_optional() for e in self._elements])
                and self.code_only
                and all([not e.is_code for e in pre])
            ):
                # It worked!
                return MatchResult(
                    start_match.matched_segments
                    + pre
                    + end_match.matched_segments,
                    end_match.unmatched_segments)
            else:
                return MatchResult.from_unmatched(segments)

    def expected_string(self, dialect=None, called_from=None):
        """Get the expected string from the referenced element."""
        return " ( {0} ) ".format(' | '.join([opt.expected_string(dialect=dialect, called_from=called_from) for opt in self._elements]))
