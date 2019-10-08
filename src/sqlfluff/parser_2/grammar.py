""" Definitions for Grammar """
import logging
import time

from .segments_base import BaseSegment, verbosity_logger
from .segments_common import KeywordSegment
from .match import MatchResult, join_segments_raw_curtailed


class BaseGrammar(object):
    """ Grammars are a way of composing match statements, any grammar
    must implment the `match` function. Segments can also be passed to
    most grammars. Segments implement `match` as a classmethod. Grammars
    implement it as an instance method """

    def __init__(self, *args, **kwargs):
        """ Deal with kwargs common to all grammars """
        # We provide a common interface for any grammar that allows positional elements
        self._elements = args
        # Now we deal with the standard kwargs
        for var, default in [('code_only', True), ('optional', False), ('terminal_hint', None)]:
            setattr(self, var, kwargs.pop(var, default))
        # optional, only really makes sense in the context of a sequence.
        # If a grammar is optional, then a sequence can continue without it.
        if kwargs:
            raise ValueError("Unconsumed kwargs is creation of grammar: {0}\nExcess: {1}".format(
                self.__class__.__name__,
                kwargs
            ))

    def is_optional(self):
        # The optional attribute is set in the __init__ method
        return self.optional

    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0):
        """
            Matching can be done from either the raw or the segments.
            This raw function can be overridden, or a grammar defined
            on the underlying class.
        """
        raise NotImplementedError("{0} has no match function implemented".format(self.__class__.__name__))

    def _match(self, segments, match_depth=0, parse_depth=0, verbosity=0):
        """ A wrapper on the match function to do some basic validation """
        t0 = time.monotonic()
        # Work out the raw representation and curtail if long
        verbosity_logger(
            "[PD:{0} MD:{1}] {2}._match IN [ls={3}, seg={4!r}]".format(
                parse_depth, match_depth, self.__class__.__name__, len(segments),
                join_segments_raw_curtailed(segments)),
            verbosity)
        if not isinstance(segments, (tuple, BaseSegment)):
            logging.warning(
                "{0}.match, was passed {1} rather than tuple or segment".format(
                    self.__class__.__name__, type(segments)))
            if isinstance(segments, list):
                # Let's make it a tuple for compatibility
                segments = tuple(segments)
        m = self.match(segments, match_depth=match_depth, parse_depth=parse_depth, verbosity=verbosity)
        if not isinstance(m, MatchResult):
            logging.warning(
                "{0}.match, returned {1} rather than MatchResult".format(
                    self.__class__.__name__, type(m)))
        dt = time.monotonic() - t0
        verbosity_logger(
            "[PD:{0} MD:{1}] {2}._match OUT [dt={3:.3f}, m={4}]".format(parse_depth, match_depth, self.__class__.__name__, dt, m),
            verbosity)
        return m

    def expected_string(self):
        """ Return a String which is helpful to understand what this grammar expects """
        raise NotImplementedError(
            "{0} does not implement expected_string!".format(
                self.__class__.__name__))


class OneOf(BaseGrammar):
    """ Match any of the elements given once, if it matches
    multiple, it returns the first """
    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0):
        logging.debug("MATCH: {0}".format(self))
        # Match on each of the options
        matches = []
        for opt in self._elements:
            m = opt._match(segments, match_depth=match_depth + 1, parse_depth=parse_depth, verbosity=verbosity)
            # Do Type Munging using unify
            m = MatchResult.unify(m)
            matches.append(m)

        if sum([1 if m.has_match() else 0 for m in matches]) > 1:
            logging.warning("WARNING! Ambiguous match!")
        else:
            logging.debug(matches)

        for m in matches:
            if m.has_match():
                return m
        else:
            return MatchResult.from_unmatched(segments)

    def expected_string(self):
        return " | ".join([opt.expected_string() for opt in self._elements])


class GreedyUntil(BaseGrammar):
    """ See the match method desription for the full details """
    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0):
        """
        Matching for GreedyUntil works just how you'd expect.
        """
        for idx, seg in enumerate(segments):
            for opt in self._elements:
                if opt._match(seg, match_depth=match_depth + 1, parse_depth=parse_depth, verbosity=verbosity):
                    # We've matched something. That means we should return everything up to this point
                    return MatchResult(segments[:idx], segments[idx:])
                else:
                    continue
        else:
            # We've got to the end without matching anything, so return.
            # We don't need to keep track of the match results, because
            # if any of them were usable, then we wouldn't be returning
            # anyway.
            return MatchResult.from_matched(segments)

    def expected_string(self):
        return "..., " + " !( " + " | ".join([opt.expected_string() for opt in self._elements]) + " ) "


class Sequence(BaseGrammar):
    """ Match a specific sequence of elements """

    @staticmethod
    def _terminal_hint(grammar, segments, matcher, code_only):
        """ A place to override for a whole class """
        return False

    def _get_terminal_hint_func(self):
        if self.terminal_hint:
            return self.terminal_hint
        else:
            return self._terminal_hint

    @staticmethod
    def _match_forward(segments, matcher, hint_func, grammar, code_only=True, match_depth=0, parse_depth=0, verbosity=0):
        """ sequentially match shorter and shorter forward segments
        looking for arbitrary length matches. this function deals with
        skipping non code segments.
        UPDATE: Now starts with the longest, and go shorter. That's the make things
        work for the Delimited grammar especially. Used to start short and go long.
        UPDATE: We now allow a `terminal_hint` method, which if it's present and true,
        stops any further iteration. If it returns true then we terminate, if it returns an integer
        then it skips to that index."""
        # logging.debug("_match_forward: {0!r}, {1!r}".format(matcher, segments))
        # Check if the start of this sequence is code_only
        if code_only and not segments[0].is_code:
            # skip this one for matching, but add it to the match
            return (segments[0],), 1, False
        # Try decreasing lengths to match the remainder
        match_len = len(segments)
        while True:
            print("[PD:{0} MD:{1}] Forward Match (l={2}): {3}".format(parse_depth, match_depth, match_len, ''.join([seg.raw for seg in segments[:match_len]])))
            # logging.debug("_match_forward [loop]: {0!r}, {1!r}".format(matcher, segments[:match_len]))
            # Check for terminal hint
            hint = hint_func(grammar, segments[:match_len], matcher, code_only)
            if isinstance(hint, bool) and hint:
                # print("Got TRUE hint")
                return None, 0, True
            elif isinstance(hint, bool) and not hint:
                pass
            elif isinstance(hint, int):
                print("Got hint of {0}".format(hint))
                if hint < match_len:
                    match_len = hint
                else:
                    logging.warning("Ignoring hint - it seems longer the current match length?!")
            m = matcher._match(segments[:match_len], match_depth=match_depth + 1,
                               parse_depth=parse_depth, verbosity=verbosity)
            if m:
                # deal with the matches
                # advance the counter
                if isinstance(m, BaseSegment):
                    logging.warning("{0} returned a segment not a tuple!".format(matcher))
                    return (m,), match_len, True
                else:
                    return m, match_len, True
            match_len -= 1
            if match_len <= 0:
                return None, 0, True

    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0):
        print(
            "PD:{0} MD:{1} Entering {2}.match. expected: {3!r}\t\traw: {4!r}\t\tsegments: {5!r}".format(
                parse_depth,
                match_depth,
                self.__class__.__name__,
                self.expected_string(),
                ''.join([seg.raw for seg in segments]),
                BaseSegment.segs_to_tuple(segments, show_raw=True)))
        if isinstance(segments, BaseSegment):
            segments = tuple(segments)
        seg_idx = 0
        matched_segments = MatchResult.from_empty()
        for elem in self._elements:
            while True:
                if seg_idx >= len(segments):
                    # We've run our of sequence without matching everyting:
                    # is it optional?
                    if elem.is_optional():
                        # then it's ok
                        break
                    else:
                        logging.debug("{0}.match, failed to see match full sequence? Looking for non-optional: {1!r}".format(self.__class__.__name__, elem))
                        return MatchResult.from_empty()
                # sequentially try longer segments to see if it works.
                # We do this because the matcher might also be looking for
                # a sequence rather than a singular.
                m, n, c = self._match_forward(
                    segments=segments[seg_idx:], matcher=elem, hint_func=self._get_terminal_hint_func(),
                    grammar=self,
                    code_only=self.code_only, match_depth=match_depth, parse_depth=parse_depth, verbosity=verbosity)
                if not m:
                    # We've failed to match at this index.
                    # Normally failing to match the next element in the
                    # sequence should return None directly, BUT if the element
                    # is optional then we may be able to move on.
                    if elem.is_optional():
                        logging.debug("{0}.match, skipping optional segment: {1!r}".format(self.__class__.__name__, elem))
                        break
                    else:
                        logging.debug("{0}.match, failed to find non-optional segment: {1!r}".format(self.__class__.__name__, elem))
                        return MatchResult.from_empty()
                else:
                    print("{0}.match, found: [n={1}] {2!r}".format(self.__class__.__name__, n, m))
                    matched_segments += m
                    # Advance the counter by the length of the match
                    if n <= 0:
                        raise ValueError("Advancing by zero: This means we'll loop infinitely!")
                    seg_idx += n
                    # If code only, then see if we've matched on code
                    if self.code_only:
                        if c:
                            # If code_only, and a code match, we should move on to the next element
                            break
                        else:
                            # If code_only, and not a code match, we should carry on with the same element
                            continue
                    else:
                        # If not code_only, then any match means we should advance the element
                        break
        else:
            # We've matched everything in the sequence, but we need to check FINALLY
            # if we've matched everything that was given.
            if seg_idx == len(segments):
                # If the segments get mutated we might need to do something different here
                return matched_segments
            elif self.code_only and all(not seg.is_code for seg in segments[seg_idx:]):
                # If we're only looking for code, and the only segments left are non-code
                # then be greedy
                return matched_segments + segments[seg_idx:]
            else:
                # We matched all the sequence, but the number of segments given was longer
                logging.debug("{0}.match, failed to match fully. Unmatched elements remain: {1!r}".format(self.__class__.__name__, segments[seg_idx:]))
                return MatchResult.from_empty()

    def expected_string(self):
        return ", ".join([opt.expected_string() for opt in self._elements])


class Delimited(BaseGrammar):
    """ Match an arbitrary number of elements seperated by a delimiter """
    def __init__(self, *args, **kwargs):
        if 'delimiter' not in kwargs:
            raise ValueError("Delimited grammars require a `delimiter`")
        self.delimiter = kwargs.pop('delimiter')
        self.allow_trailing = kwargs.pop('allow_trailing', False)
        super(Delimited, self).__init__(*args, **kwargs)

    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0):
        if isinstance(segments, BaseSegment):
            segments = [segments]
        seg_idx = 0
        # delimiters is a list of tuples (idx, len), which keeps track of where
        # we found delimiters up to this point.
        delimiters = []
        matched_segments = MatchResult.from_empty()

        # First iterate through all the segments, looking for the delimiter.
        # Second, split the list on each of the delimiters, and ensure that
        # each sublist in turn matches one of the elements.

        # In more detail, match against delimiter, if we match, put a slice
        # up to that point onto a list of slices. Carry on.
        while True:
            # Are we at the end of the sequence?
            if seg_idx >= len(segments):
                # Yes we're at the end

                # We now need to check whether everything from either the start
                # or from the last delimiter up to here matches. We CAN allow
                # a partial match at this stage.

                # Do we already have any delimiters?
                if delimiters:
                    # Yes, get the last delimiter
                    dm1 = delimiters[-1]
                    # get everything after the last delimiter
                    pre_segment = segments[dm1[0] + dm1[1]:]
                else:
                    # No, no delimiters at all so far.
                    # TODO: Allow this to be configured.
                    # Just get everything up to this point
                    pre_segment = segments

                # See if any of the elements match
                for elem in self._elements:
                    elem_match = elem._match(
                        pre_segment, match_depth=match_depth + 1,
                        parse_depth=parse_depth, verbosity=verbosity)

                    if elem_match.has_match():
                        # Successfully matched one of the elements in this spot

                        # Add this match onto any already matched segments and return.
                        # We do this in a slightly odd way here to allow partial matches.
                        return MatchResult(
                            matched_segments + elem_match.matched_segments,
                            elem_match.unmatched_segments)
                    else:
                        # Not matched this element, move on.
                        # NB, a partial match here isn't helpful. We're matching
                        # BETWEEN two delimiters and so it must be a complete match.
                        # Incomplete matches are only possible at the end
                        continue
                else:
                    # If we're here we haven't matched any of the elements on this last element.
                    # BUT, if we allow trailing, and we have matched something, we can end on the last
                    # delimiter
                    if self.allow_trailing and len(matched_segments) > 0:
                        return MatchResult(matched_segments.matched_segments, pre_segment)
                    else:
                        return MatchResult.from_unmatched(segments)

            else:
                # We've got some sequence left
                # Do we have a delimiter at the current index?

                # NB: New matching format, pass it all to the matcher and allow
                # it to match the rest.
                del_match = self.delimiter._match(
                    segments[seg_idx:], match_depth=match_depth + 1,
                    parse_depth=parse_depth, verbosity=verbosity)

                # Doesn't have to match fully, just has to give us a delimiter.
                if del_match.has_match():
                    # We've got at least a partial match
                    # Record the location of this delimiter
                    d = (seg_idx, len(del_match))
                    # Do we already have any delimiters?
                    if delimiters:
                        # Yes
                        dm1 = delimiters[-1]
                        # slice the segments between this delimiter and the previous
                        pre_segment = segments[dm1[0] + dm1[1]:d[0]]
                    else:
                        # No
                        # Just get everything up to this point
                        pre_segment = segments[:d[0]]
                    # Append the delimiter that we have found.
                    delimiters.append(d)

                    # We now check that this chunk matches whatever we're delimiting.
                    # In this case it MUST be a full match, not just a partial match
                    for elem in self._elements:
                        elem_match = elem._match(
                            pre_segment, match_depth=match_depth + 1,
                            parse_depth=parse_depth, verbosity=verbosity)

                        if elem_match.is_complete():
                            # Successfully matched one of the elements in this spot

                            # First add the segment up to the delimiter to the matched segments
                            matched_segments += elem_match
                            # Then add the delimiter to the matched segments
                            matched_segments += del_match
                            # Break this for loop and move on, looking for the next delimiter
                            seg_idx += 1
                            break
                        else:
                            # Not matched this element, move on.
                            # NB, a partial match here isn't helpful. We're matching
                            # BETWEEN two delimiters and so it must be a complete match.
                            # Incomplete matches are only possible at the end
                            continue
                    else:
                        # If we're here we haven't matched any of the elements, then we have a problem
                        return MatchResult.from_unmatched(segments)
                # This index doesn't have a delimiter, carry on.
                else:
                    seg_idx += 1

    def expected_string(self):
        return " {0} ".format(self.delimiter.expected_string()).join([opt.expected_string() for opt in self._elements])


class ContainsOnly(BaseGrammar):
    """ match a sequence of segments which are only of the types,
    or only match the grammars in the list """
    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0):
        seg_buffer = tuple()
        for seg in segments:
            matched = False
            if self.code_only and not seg.is_code:
                # Don't worry about non-code segments if we're configured
                # to do so.
                matched = True
                seg_buffer += (seg,)
            else:
                for opt in self._elements:
                    if isinstance(opt, str):
                        if seg.type == opt:
                            matched = True
                            seg_buffer += (seg,)
                            break
                    else:
                        try:
                            m = opt._match(seg, match_depth=match_depth + 1, parse_depth=parse_depth, verbosity=verbosity)
                        except AttributeError:
                            # This is unlikely, but if the element doesn't have a
                            # match method, then don't sweat. Just carry on.
                            continue
                        if m:
                            matched = True
                            seg_buffer += m
                            break
            if not matched:
                # Found a segment which doesn't match, this means
                # we fail the whole grammar because it doesn't just
                # contain only the given elements.
                return MatchResult.from_empty()
        else:
            return seg_buffer

    def expected_string(self):
        buff = []
        for opt in self._elements:
            if isinstance(opt, str):
                buff.append(opt)
            else:
                buff.append(opt.expected_string())
        return " ( " + " | ".join(buff) + " | + )"


class StartsWith(BaseGrammar):
    """ Match if the first element is the same, with configurable
    whitespace and comment handling """
    def __init__(self, target, *args, **kwargs):
        self.target = target
        super(StartsWith, self).__init__(*args, **kwargs)

    def match(self, segments, match_depth=0, parse_depth=0, verbosity=0):
        if self.code_only:
            first_code_idx = None
            # Work through to find the first code segment...
            for idx, seg in enumerate(segments):
                if seg.is_code:
                    first_code_idx = idx
                    break
            else:
                # We've not found something that isn't code, that means this
                # isn't a match.
                return MatchResult.from_unmatched(segments)

            match = self.target._match(
                segments=segments[first_code_idx:], match_depth=match_depth + 1,
                parse_depth=parse_depth, verbosity=verbosity)
            if match:
                # The match will probably have returned a mutated version rather
                # that the raw segment sent for matching. We need to reinsert it
                # back into the sequence in place of the raw one, but we can't
                # just assign at the index because it's a tuple and not a list.
                # to get around that we do this slightly more elaborate construction.

                # NB: This match may be partial or full, either is cool. In the case
                # of a partial match, given that we're only interested in what it STARTS
                # with, then we can still used the unmatched parts on the end.
                # We still need to deal with ano non-code segments at the start.
                return MatchResult.from_matched(
                    segments[:first_code_idx]
                    + match.matched_segments
                    + match.unmatched_segments)
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError("Not expecting to match StartsWith and also not just code!?")

    def expected_string(self):
        return self.target.expected_string() + ", ..."


class Bracketed(Sequence):
    """ Bracketed is just a wrapper around Sequence """
    def __init__(self, *args, **kwargs):
        # Start and end tokens
        self.start_bracket = kwargs.pop(
            'start_bracket',
            KeywordSegment.make('(', name='start_bracket', type='start_bracket')
        )
        self.end_bracket = kwargs.pop(
            'end_bracket',
            KeywordSegment.make(')', name='end_bracket', type='end_bracket')
        )
        # Construct the sequence with brackets (as tuples)
        newargs = (self.start_bracket,) + args + (self.end_bracket,)
        # Call the sequence
        super(Bracketed, self).__init__(*newargs, **kwargs)

    @staticmethod
    def _terminal_hint(grammar, segments, matcher, code_only):
        """ A place to override for a whole class """
        # does it start with a bracket,
        for seg in segments:
            if grammar.start_bracket.match(seg):
                # ok we've got a start bracket
                break
            elif not seg.is_code and code_only:
                # this isn't code, move on
                continue
            else:
                # This starts with a segment which isn't a bracket
                return True
        else:
            # Don't know how we get here but it's bad
            return True

        bracket_stack = []
        for idx, seg in enumerate(segments):
            for raw in seg.iter_raw_seg():
                if grammar.start_bracket.match(raw):
                    bracket_stack.append(idx)
                elif grammar.end_bracket.match(raw):
                    if len(bracket_stack) == 1:
                        # We're on our last bracket, this should be the index to search for.
                        return idx
                    elif len(bracket_stack) <= 0:
                        # We should never get here
                        logging.warning("We should never get here: ID: A487AWHOL87AW3J")
                        return False
                    else:
                        bracket_stack.pop()

        # If we get to here, we never found the end bracket for the first opening one.
        # We should abort
        return False
