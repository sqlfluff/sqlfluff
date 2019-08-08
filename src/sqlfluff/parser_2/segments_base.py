
import logging
from six import StringIO


class BaseSegment(object):
    type = 'base'
    parse_grammar = None
    grammar = None
    comment_seperate = False
    is_whitespace = False
    is_code = False

    @classmethod
    def _match_grammar(self):
        if self.grammar:
            return self.grammar
        else:
            return self.parse_grammar

    @classmethod
    def _parse_grammar(self):
        # return self.parse_grammar
        if self.parse_grammar:
            return self.parse_grammar
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

    def parse(self):
        logging.debug("{0}.parse A".format(self.__class__.__name__))
        if self.segments is None:
            raise ValueError("No Segments to parse!?")
        # First we need to allow any existing segments in this
        # statement to expand out. This could inlude code and comment
        # segments.
        # We now need to parse each of the sub elements. Expand does that.
        self.segments = self.expand(self.segments)
        logging.debug("{0}.parse B".format(self.__class__.__name__))
        # logging.debug("{0}".format(self.segments))
        # logging.debug("{0}: {1}".format(self.__class__.__name__, self.segments))
        # Here we then need to allow any number of comments and whitespace
        # (to lint later)
        # THEN it must match a type of sql statement

        # Mutate itself, and then return

        # If it can't match, then we should have an unparsable block
        # match = self.match(segments=self.segments)
        # if match is None:
        #    self.segments = [UnparsableSegment(segments=self.segments)]
        # else:
        #    self.segments = [match]

        # Similar to the match grammar, we use parse grammar here:
        if self._parse_grammar():
            m = self._parse_grammar().match(segments=self.segments)
            logging.debug("{0}.parse C".format(self.__class__.__name__))
            # logging.debug(m)
            # m will either be a segment, or a list.
            # if it's a list, it's a list of segments to construct THIS class
            # if it's a segment, then it's a replacement
            # if it's NONE then we haven't matched and we should return that
            if isinstance(m, BaseSegment):
                self.segments = [m]
            elif isinstance(m, list):
                self.segments = m
            elif m is None:
                self.segments = [UnparsableSegment(segments=self.segments)]
            else:
                raise ValueError("Unexpected response to self._parse_grammar.match: {0!r}".format(m))
            logging.debug("{0}.parse D".format(self.__class__.__name__))
            # logging.debug(self.segments)
            self.segments = self.expand(self.segments)
        # else:
        #    raise NotImplementedError("{0} has no parse grammar function implemented".format(self.__class__.__name__))
        logging.debug("{0}.parse E".format(self.__class__.__name__))
        # rint(self.segments)
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
        if code_only:
            return (self.type, tuple([seg.to_tuple(**kwargs) for seg in self.segments if seg.is_code]))
        else:
            return (self.type, tuple([seg.to_tuple(**kwargs) for seg in self.segments]))

    # Match for segments is done in the ABSTRACT.
    # When dealing with concrete then we're always in parse.
    # Parse is what happens during expand.
    @classmethod
    def match(cls, segments):
        """
            Matching can be done from either the raw or the segments.
            This raw function can be overridden, or a grammar defined
            on the underlying class.
        """
        logging.debug("MATCH: {0}".format(cls))
        if cls._match_grammar():
            m = cls._match_grammar().match(segments=segments)
            # m will either be a segment, or a list.
            # if it's a list, it's a list of segments to construct THIS class
            # if it's a segment, then it's a replacement
            # if it's NONE then we haven't matched and we should return that
            if isinstance(m, BaseSegment):
                return cls(segments=[m])
            elif isinstance(m, list):
                return cls(segments=m)
            elif m is None:
                return None
            else:
                raise ValueError("Unexpected response to cls._match_grammar.match: {0!r}".format(m))
        else:
            raise NotImplementedError("{0} has no match function implemented".format(cls.__name__))

    @staticmethod
    def expand(segments):
        segs = []
        for stmt in segments:
            res = stmt.parse()
            if isinstance(res, BaseSegment):
                segs.append(res)
            else:
                # We might get back an iterable of segments
                segs += stmt.parse()
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

    def parse(self):
        # TODO: Check this is right?
        return self

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
