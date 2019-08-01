
import logging

from .segments_base import BaseSegment, KeywordSegment


class BaseGrammar(object):
    """ Grammars are a way of composing match statements, any grammar
    must implment the `match` function. Segments can also be passed to
    most grammars. Segments implement `match` as a classmethod. Grammars
    implement it as an instance method """

    def match(self, segments):
        """
            Matching can be done from either the raw or the segments.
            This raw function can be overridden, or a grammar defined
            on the underlying class.
        """
        logging.debug("MATCH: {0}".format(self))
        raise NotImplementedError("{0} has no match function implemented".format(self.__class__.__name__))


class OneOf(BaseGrammar):
    """ Match any of the elements given once, if it matches
    multiple, it returns the first """
    def __init__(self, *args, **kwargs):
        self._options = args

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        # Match on each of the options
        matches = [opt.match(segments) for opt in self._options]

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

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        seg_buffer = []
        for seg in segments:
            for opt in self._options:
                if opt.match(seg):
                    # it's a match! Return everything up to this point
                    if seg_buffer:
                        return seg
                    else:
                        # if the buffer is empty, then no match
                        return None
                else:
                    continue
            else:
                # Add this to the buffer
                seg_buffer.append(seg)
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

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        # we should assume that segments aren't mutated in a grammar
        # so that the number we get back from a match is the same as
        # the number we should skip.
        if isinstance(segments, BaseSegment):
            segments = [segments]
        seg_idx = 0
        for elem in self._elems:
            logging.debug(elem)
            logging.debug("Sequence Matching at index: {0}".format(seg_idx))
            # sequentially try longer segments to see if it works
            seg_len = 1
            while True:
                if seg_idx + seg_len > len(segments):
                    # We failed to match an element, fail out.
                    logging.debug("FAIL")
                    return None
                m = elem.match(segments[seg_idx:seg_idx + seg_len])
                logging.debug(m)
                if m:
                    # deal with the matches
                    # advance the counter
                    if isinstance(m, BaseSegment):
                        seg_idx = 1
                    else:
                        seg_idx += len(m)
                    logging.debug(seg_idx)
                    break
                seg_len += 1
        else:
            # If the segments get mutated we might need to do something different here
            return segments


class ContainsOnly(BaseGrammar):
    """ match a sequence of segments which are only of the types,
    or only match the grammars in the list """
    def __init__(self, *args, **kwargs):
        self._options = args

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        for seg in segments:
            matched = False
            for opt in self._options:
                if isinstance(opt, str) and seg.type == opt:
                    matched = True
                    break
                elif isinstance(opt, (BaseGrammar, BaseSegment)) and opt.match([seg]):
                    matched = True
                    break
            if not matched:
                logging.debug("Non Matching Segment! {0!r}".format(seg))
                # found a non matching segment:
                return None
        else:
            # Should we also be returning a raw here?
            return segments


class StartsWith(BaseGrammar):
    """ Match if the first element is the same, with configurable
    whitespace and comment handling """
    def __init__(self, target, code_only=True, **kwargs):
        self.target = target
        self.code_only = code_only
        # Implement config handling later...

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        if self.code_only:
            first_code = None
            first_code_idx = None
            for idx, seg in enumerate(segments):
                if seg.type == 'strippedcode':
                    first_code_idx = idx
                    first_code = seg
                    break
            else:
                return None

            match = self.target.match(segments=[first_code])
            if match:
                # Let's actually make it a keyword segment
                segments[first_code_idx] = match
                return segments
            else:
                return None
        else:
            raise NotImplementedError("Not expecting to match StartsWith and also not just code!?")


class Keyword(BaseGrammar):
    """ Match a keyword, optionally case sensitive """
    def __init__(self, word, case_sensitive=False, **kwargs):
        # NB We store the word as upper case unless case sensitive
        # For this one we won't accept whitespace or comments
        self.case_sensitive = case_sensitive
        if self.case_sensitive:
            self.word = word
        else:
            self.word = word.upper()

    def match(self, segments):
        # TODO: This shouldn't reference KeywordSegment, it's untidy. Ideally
        # a keyword should be able to match itself, without needing a grammar
        # to do if for itself.
        logging.debug("MATCH: {0}".format(self))
        # We can only match segments of length 1
        if isinstance(segments, BaseSegment):
            segments = [segments]
        logging.debug(len(segments))
        if len(segments) == 1:
            raw = segments[0].raw
            pos = segments[0].pos_marker
            logging.debug(raw)
            if ((self.case_sensitive and self.word == raw) or (not self.case_sensitive and self.word == raw.upper())):
                return KeywordSegment(raw=raw, pos_marker=pos)
        return None
