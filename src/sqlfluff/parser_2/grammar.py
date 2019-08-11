
import logging

from .segments_base import BaseSegment


class BaseGrammar(object):
    """ Grammars are a way of composing match statements, any grammar
    must implment the `match` function. Segments can also be passed to
    most grammars. Segments implement `match` as a classmethod. Grammars
    implement it as an instance method """

    def match(self, segments, match_depth=0):
        """
            Matching can be done from either the raw or the segments.
            This raw function can be overridden, or a grammar defined
            on the underlying class.
        """
        logging.debug("MATCH: {0}".format(self))
        raise NotImplementedError("{0} has no match function implemented".format(self.__class__.__name__))

    def _match(self, segments, match_depth=0):
        """ A wrapper on the match function to do some basic validation """
        logging.info("[MD:{0}] {1}._match IN".format(match_depth, self.__class__.__name__))
        if not isinstance(segments, (tuple, BaseSegment)):
            logging.warning(
                "{0}.match, was passed {1} rather than tuple or segment".format(
                    self.__class__.__name__, type(segments)))
            if isinstance(segments, list):
                # Let's make it a tuple for compatibility
                segments = tuple(segments)
        m = self.match(segments, match_depth=match_depth)
        if not isinstance(m, tuple) and m is not None:
            logging.warning(
                "{0}.match, returned {1} rather than tuple".format(
                    self.__class__.__name__, type(m)))
        logging.info("[MD:{0}] {1}._match OUT [m={2}]".format(match_depth, self.__class__.__name__, m))
        return m


class OneOf(BaseGrammar):
    """ Match any of the elements given once, if it matches
    multiple, it returns the first """
    def __init__(self, *args, **kwargs):
        self._options = args
        self.code_only = kwargs.get('code_only', True)

    def match(self, segments, match_depth=0):
        logging.debug("MATCH: {0}".format(self))
        # Match on each of the options
        matches = []
        for opt in self._options:
            m = opt._match(segments, match_depth=match_depth + 1)
            matches.append(m)

        # matches = [opt.match(segments) for opt in self._options]

        if sum([1 if m is not None else 0 for m in matches]) > 1:
            logging.warning("WARNING! Ambiguous match!")

        for m in matches:
            if m:
                logging.debug("MATCH: {0}: Returning: {1}".format(self, m))
                return m
        else:
            return None


class GreedyUntil(BaseGrammar):
    """ Match anything, up to but not including the given options """
    def __init__(self, *args, **kwargs):
        self._options = args
        # `strict`, means the segment will not be matched WITHOUT
        # the ending clause. Normally, if we run out of segments,
        # then this will still match
        self.strict = kwargs.get('strict', False)
        # NB: Right now, code_only has no effect here, because we're already
        # greedy regardless of type
        self.code_only = kwargs.get('code_only', True)

    def match(self, segments, match_depth=0):
        seg_buffer = tuple()
        for seg in segments:
            for opt in self._options:
                if opt._match(seg, match_depth=match_depth + 1):
                    # it's a match! Return everything up to this point
                    if seg_buffer:
                        return seg_buffer
                    else:
                        # if the buffer is empty, then no match
                        return None
                else:
                    continue
            else:
                # Add this to the buffer
                seg_buffer += (seg,)
        else:
            # We've gone through all the segments, and not found the end
            if self.strict:
                # Strict mode means this is NOT at match because we didn't find the end
                return None
            else:
                return seg_buffer


class Sequence(BaseGrammar):
    """ Match a specific sequence of elements """
    def __init__(self, *args, **kwargs):
        self._elems = args
        self.code_only = kwargs.get('code_only', True)

    @staticmethod
    def _match_forward(segments, matcher, code_only=True, match_depth=0):
        """ sequentially match shorter and shorter forward segments
        looking for arbitrary length matches. this function deals with
        skipping non code segments.
        UPDATE: Now starts with the longest, and go shorter. That's the make things
        work for the Delimited grammar especially. Used to start short and go long."""
        logging.debug("_match_forward: {0!r}, {1!r}".format(matcher, segments))
        # Check if the start of this sequence is code_only
        if code_only and not segments[0].is_code:
            # skip this one for matching, but add it to the match
            return (segments[0],), 1, False
        # Try decreasing lengths to match the remainder
        match_len = len(segments)
        while True:
            logging.debug("_match_forward [loop]: {0!r}, {1!r}".format(matcher, segments[:match_len]))
            m = matcher._match(segments[:match_len], match_depth=match_depth + 1)
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

    def match(self, segments, match_depth=0):
        if isinstance(segments, BaseSegment):
            segments = tuple(segments)
        logging.debug("{0}.match, inbound segments: {1!r}".format(self.__class__.__name__, segments))
        seg_idx = 0
        matched_segments = tuple()
        for elem in self._elems:
            logging.debug("{0}.match, already matched: {1!r}".format(self.__class__.__name__, matched_segments))
            logging.debug("{0}.match, considering: {1!r}".format(self.__class__.__name__, elem))
            logging.debug("{0}.match, seg_idx: {1!r}".format(self.__class__.__name__, seg_idx))
            while True:
                if seg_idx >= len(segments):
                    # We've run our of sequence without matching everyting:
                    return None
                # sequentially try longer segments to see if it works.
                # We do this because the matcher might also be looking for
                # a sequence rather than a singular.
                m, n, c = self._match_forward(
                    segments=segments[seg_idx:], matcher=elem, code_only=self.code_only,
                    match_depth=match_depth)
                if m is None:
                    # We've failed to match at this index
                    return None
                else:
                    logging.debug("{0}.match, found: [n={1}] {2!r}".format(self.__class__.__name__, n, m))
                    matched_segments += m
                    # Advance the counter by the length of the match
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
                return None


class Delimited(Sequence):
    """ Match an arbitrary number of elements seperated by a delimiter """
    def __init__(self, *args, **kwargs):
        self._elems = args
        self.code_only = kwargs.pop('code_only', True)
        if 'delimiter' not in kwargs:
            raise ValueError("Delimited grammars require a `delimiter`")
        self.delimiter = kwargs.pop('delimiter')
        self.allow_trailing = kwargs.pop('allow_trailing', False)
        if kwargs:
            raise ValueError("Unconsumed kwargs for {0}: {1}".format(
                self.__class__.__name__,
                kwargs
            ))

    def match(self, segments, match_depth=0):
        if isinstance(segments, BaseSegment):
            segments = [segments]
        seg_idx = 0
        matched_segments = tuple()
        looking_for = 'element'  # This will be `delimiter` when we find an element
        while True:
            logging.debug("{0}.match, already matched: {1!r}".format(self.__class__.__name__, matched_segments))
            logging.debug("{0}.match, looking for: {1!r}".format(self.__class__.__name__, looking_for))
            logging.debug("{0}.match, seg_idx: {1!r}".format(self.__class__.__name__, seg_idx))

            if seg_idx >= len(segments):
                # We've got to the end of the segments, we can't end on a delimiter
                # unless allow_trailing is set
                if looking_for == 'element':
                    if self.allow_trailing:
                        return matched_segments
                    else:
                        return None
                elif looking_for == 'delimiter':
                    return matched_segments
                else:
                    raise ValueError("Unexpected looking for!")

            if looking_for == 'element':
                for elem in self._elems:
                    logging.debug("{0}.match, considering: {1!r}".format(self.__class__.__name__, elem))
                    m, n, c = self._match_forward(
                        segments=segments[seg_idx:], matcher=elem,
                        code_only=self.code_only,
                        match_depth=match_depth)
                    if m is None:
                        # We've failed to match at this index
                        continue
                    else:
                        logging.debug("{0}.match, found: [n={1}] {2!r}".format(self.__class__.__name__, n, m))
                        matched_segments += m
                        # Advance the counter by the length of the match
                        seg_idx += n
                        # If we matched on code, then switch
                        if c:
                            looking_for = 'delimiter'
                        break
                else:
                    # Completed a loop without a match
                    logging.debug("{0}.match, no match [elem]".format(self.__class__.__name__))
                    return None
            elif looking_for == 'delimiter':
                logging.debug("{0}.match, considering: {1!r}".format(self.__class__.__name__, self.delimiter))
                m, n, c = self._match_forward(
                    segments=segments[seg_idx:], matcher=self.delimiter,
                    code_only=self.code_only,
                    match_depth=match_depth)
                if m is None:
                    # We've failed to match at this index
                    logging.debug("{0}.match, no match [delim]".format(self.__class__.__name__))
                    return None
                else:
                    logging.debug("{0}.match, found: [n={1}] {2!r}".format(self.__class__.__name__, n, m))
                    matched_segments += m
                    # Advance the counter by the length of the match
                    seg_idx += n
                    # If we matched on code, then switch
                    if c:
                        looking_for = 'element'
                    # NB: No break here, because we're not looping through options
            else:
                raise ValueError("Unexpected looking for: {0!r}".format(looking_for))


class ContainsOnly(BaseGrammar):
    """ match a sequence of segments which are only of the types,
    or only match the grammars in the list """
    def __init__(self, *args, **kwargs):
        self._options = args
        self.code_only = kwargs.get('code_only', True)

    def match(self, segments, match_depth=0):
        seg_buffer = tuple()
        for seg in segments:
            matched = False
            if self.code_only and not seg.is_code:
                # Don't worry about non-code segments
                matched = True
                seg_buffer += (seg,)
            else:
                for opt in self._options:
                    if isinstance(opt, str):
                        if seg.type == opt:
                            matched = True
                            seg_buffer += (seg,)
                            break
                    else:
                        try:
                            m = opt._match(seg, match_depth=match_depth + 1)
                        except AttributeError:
                            # it doesn't have a match method
                            continue
                        if m:
                            matched = True
                            seg_buffer += m
                            break
            if not matched:
                logging.debug("Non Matching Segment! {0!r}".format(seg))
                # found a non matching segment:
                return None
        else:
            # Should we also be returning a raw here?
            return seg_buffer


class StartsWith(BaseGrammar):
    """ Match if the first element is the same, with configurable
    whitespace and comment handling """
    def __init__(self, target, code_only=True, **kwargs):
        self.target = target
        self.code_only = code_only
        # Implement config handling later...

    def match(self, segments, match_depth=0):
        if self.code_only:
            first_code = None
            first_code_idx = None
            for idx, seg in enumerate(segments):
                if seg.is_code:
                    first_code_idx = idx
                    first_code = seg
                    break
            else:
                return None

            match = self.target._match(segments=[first_code], match_depth=match_depth + 1)
            if match:
                # Let's actually make it a keyword segment
                # segments[first_code_idx] = match  <- can't do this on a tuple
                segments = segments[:first_code_idx] + tuple(match) + segments[first_code_idx + 1:]
                return segments
            else:
                return None
        else:
            raise NotImplementedError("Not expecting to match StartsWith and also not just code!?")
