
import logging
from six import StringIO


class BaseSegment(object):
    type = 'base'
    parse_grammar = None
    match_grammar = None
    grammar = None
    comment_seperate = False
    is_whitespace = False
    is_code = False

    @classmethod
    def _match_grammar(self):
        if self.match_grammar:
            return self.match_grammar
        else:
            return self.grammar

    @classmethod
    def _parse_grammar(self):
        # return self.parse_grammar
        if self.parse_grammar:
            return self.parse_grammar
        elif self.match_grammar:
            return self.match_grammar
        else:
            return self.grammar

    def __init__(self, segments, pos_marker=None):
        self.segments = segments
        if pos_marker:
            self.pos_marker = pos_marker
        else:
            # If no pos given, it's the pos of the first segment
            self.pos_marker = segments[0].pos_marker

    @classmethod
    def from_raw(cls, raw):
        raise NotImplementedError("from_raw is not implemented for {0}".format(cls.__name__))

    def parse(self, recurse=True):
        """ Use the parse kwarg for testing, mostly to check how deep to go.
        True/False for yes or no, an integer allows a certain number of levels """

        # We should call the parse grammar on this segment, which calls
        # the match grammar on all it's children.

        # if the `parse` kwarg has the right value, we then call `parse`
        # on each of the children.
        logging.debug("{0}.parse: recurse={1!r}".format(self.__class__.__name__, recurse))
        if not self.segments:
            # This means we're a root segment, just return an unmutated self
            return self

        # Get the Parse Grammar
        g = self._parse_grammar()
        if g is None:
            logging.debug("{0}.parse: no grammar. returning".format(self.__class__.__name__))
            return self
        # Use the Parse Grammar (and the private method)
        m = g._match(segments=self.segments)  # NB No match depth kwarg, because we're starting here!
        if isinstance(m, BaseSegment):
            logging.error(self._parse_grammar())
            logging.error(m)
            raise ValueError("Grammar returned a segment rather than an iterable!!")
        elif isinstance(m, (list, tuple)):
            self.segments = m
        elif m is None:
            self.segments = [UnparsableSegment(segments=self.segments)]
        else:
            raise ValueError("Unexpected response to self._parse_grammar.match: {0!r}".format(m))

        # Recurse if allowed (using the expand method to deal with the expansion)
        logging.debug("{0}.parse: Done Parse. Plotting Recursion. Recurse={1!r}".format(self.__class__.__name__, recurse))
        logging.debug("{0}.parse: Pre-Recursion Structure: {1!r}".format(self.__class__.__name__, self.segments))
        if recurse is True:
            self.segments = self.expand(self.segments, recurse=True)
        if isinstance(recurse, int):
            if recurse > 1:
                self.segments = self.expand(self.segments, recurse=recurse - 1)

        return self

    def __repr__(self):
        # return "<{0}: ({1}) {2!s}>".format(
        #    self.__class__.__name__,
        #    self.pos_marker,
        #    self.segments)
        return "<{0}: ({1})>".format(
            self.__class__.__name__,
            self.pos_marker)

    def _reconstruct(self):
        return "".join([seg._reconstruct() for seg in self.segments])

    @property
    def raw(self):
        return self._reconstruct()

    def _preface(self, ident, tabsize, pos_idx):
        preface = (' ' * (ident * tabsize)) + self.__class__.__name__ + ":"
        preface = preface + (' ' * max(pos_idx - len(preface), 0)) + str(self.pos_marker)
        return preface

    @property
    def _comments(self):
        return [seg for seg in self.segments if seg.type == 'comment']

    @property
    def _non_comments(self):
        return [seg for seg in self.segments if seg.type != 'comment']

    def stringify(self, ident=0, tabsize=4, pos_idx=60, raw_idx=80):
        buff = StringIO()
        preface = self._preface(ident=ident, tabsize=tabsize, pos_idx=pos_idx)
        buff.write(preface + '\n')
        if self.comment_seperate and len(self._comments) > 0:
            if self._comments:
                buff.write((' ' * ((ident + 1) * tabsize)) + 'Comments:' + '\n')
                for seg in self._comments:
                    buff.write(seg.stringify(ident=ident + 2, tabsize=tabsize, pos_idx=pos_idx, raw_idx=raw_idx))
            if self._non_comments:
                buff.write((' ' * ((ident + 1) * tabsize)) + 'Code:' + '\n')
                for seg in self._non_comments:
                    buff.write(seg.stringify(ident=ident + 2, tabsize=tabsize, pos_idx=pos_idx, raw_idx=raw_idx))
        else:
            for seg in self.segments:
                buff.write(seg.stringify(ident=ident + 1, tabsize=tabsize, pos_idx=pos_idx, raw_idx=raw_idx))
        return buff.getvalue()

    def to_tuple(self, **kwargs):
        # works for both base and raw
        code_only = kwargs.get('code_only', False)
        show_raw = kwargs.get('show_raw', False)
        if show_raw and not self.segments:
            return (self.type, self.raw)
        elif code_only:
            return (self.type, tuple([seg.to_tuple(**kwargs) for seg in self.segments if seg.is_code]))
        else:
            return (self.type, tuple([seg.to_tuple(**kwargs) for seg in self.segments]))

    # Match for segments is done in the ABSTRACT.
    # When dealing with concrete then we're always in parse.
    # Parse is what happens during expand.
    @classmethod
    def match(cls, segments, match_depth=0):
        """
            Matching can be done from either the raw or the segments.
            This raw function can be overridden, or a grammar defined
            on the underlying class.
        """
        logging.debug("MATCH: {0}".format(cls))
        if cls._match_grammar():
            # Call the private method
            m = cls._match_grammar()._match(segments=segments, match_depth=match_depth + 1)
            # m will either be a segment, or a list.
            # if it's a list, it's a list of segments to construct THIS class
            # if it's a segment, then it's a replacement
            # if it's NONE then we haven't matched and we should return that
            if isinstance(m, BaseSegment):
                logging.info("MATCH SUCCESS: {0}: {1}".format(cls, [m]))
                logging.warning("Matcher {0} returned a list!".format(cls._match_grammar()))
                return cls(segments=(m,))
            elif isinstance(m, (list, tuple)):
                logging.info("MATCH SUCCESS: {0}: {1}".format(cls, m))
                return cls(segments=m),  # Return a tuple
            elif m is None:
                return None
            else:
                raise ValueError("Unexpected response to cls._match_grammar.match: {0!r}".format(m))
        else:
            raise NotImplementedError("{0} has no match function implemented".format(cls.__name__))

    @classmethod
    def _match(cls, segments, match_depth=0):
        """ A wrapper on the match function to do some basic validation """
        logging.info("[MD:{0}] {1}._match IN".format(match_depth, cls.__name__))
        if not isinstance(segments, (tuple, BaseSegment)):
            logging.warning(
                "{0}.match, was passed {1} rather than tuple or segment".format(
                    cls.__name__, type(segments)))
            if isinstance(segments, list):
                # Let's make it a tuple for compatibility
                segments = tuple(segments)
        m = cls.match(segments, match_depth=match_depth)
        if not isinstance(m, tuple) and m is not None:
            logging.warning(
                "{0}.match, returned {1} rather than tuple".format(
                    cls.__name__, type(m)))
        logging.info("[MD:{0}] {1}._match OUT [m={2}]".format(match_depth, cls.__name__, m))
        return m

    @staticmethod
    def expand(segments, recurse=True):
        segs = tuple()
        for stmt in segments:
            res = stmt.parse(recurse=recurse)
            if isinstance(res, BaseSegment):
                raise ValueError("We got ANOTHER segment back rather than an iterable!!?")
            else:
                # We might get back an iterable of segments
                segs += res
        return segs

    def raw_list(self):
        """ List of raw elements, mostly for testing """
        buff = []
        for s in self.segments:
            buff += s.raw_list()
        return buff

    def type_set(self):
        """ A set of the types contained, mostly for testing """
        typs = set([self.type])
        for s in self.segments:
            typs |= s.type_set()
        return typs

    def __eq__(self, other):
        # Equal if type, content and pos are the same
        # NB: this should also work for RawSegment
        return ((type(self) == type(other))
                and (self.raw == other.raw)
                and (self.pos_marker == other.pos_marker))


class RawSegment(BaseSegment):
    """ This is a segment without any subsegments,
    it could be postprocessed later, but then it would be
    a different class. """
    type = 'raw'
    is_code = False
    _template = '<unset>'
    _case_sensitive = False

    def __init__(self, raw, pos_marker):
        self._raw = raw
        # pos marker is required here
        self.pos_marker = pos_marker

    @property
    def segments(self):
        """ in case we need to iterate """
        return []
        # A Raw segments, has no segments, it's empty
        # raise RuntimeError("Trying to iterate on a RawSegment!")
        # return [self]

    def raw_list(self):
        return [self.raw]

    @property
    def raw(self):
        return self._raw

    def _reconstruct(self):
        return self.raw

    def __repr__(self):
        return "<{0}: ({1}) {2!r}>".format(
            self.__class__.__name__,
            self.pos_marker,
            self.raw)

    def stringify(self, ident=0, tabsize=4, pos_idx=60, raw_idx=80):
        preface = self._preface(ident=ident, tabsize=tabsize, pos_idx=pos_idx)
        return preface + (' ' * max(raw_idx - len(preface), 0)) + "{0!r}\n".format(self.raw)

    @classmethod
    def make(cls, template, case_sensitive=False, name=None,
             # type=None, is_code=None. USE KWARGS FOR THESE
             **kwargs):
        # Let's deal with the template first
        if case_sensitive:
            _template = template
        else:
            _template = template.upper()
        # Use the name if provided otherwise default to the template
        name = name or _template
        # Now lets make the classname (it indicates the mother class for clarity)
        classname = "{0}_{1}".format(name, cls.__name__)
        # This is the magic, we generate a new class! SORCERY
        newclass = type(classname, (cls, ),
                        dict(_template=_template, _case_sensitive=case_sensitive,
                             **kwargs))
        # Now we return that class in the abstract. NOT INSTANTIATED
        return newclass


class UnparsableSegment(BaseSegment):
    type = 'unparsable'
    # From here down, comments are printed seperately.
    comment_seperate = True
