"""
Base segment definitions

Here we define:
- BaseSegment. This is the root class for all segments, and is
  designed to hold other subsegments.
- RawSegment. This is designed to be the root segment, without
  any children, and the output of the lexer.
- UnparsableSegment. A special wrapper to indicate that the parse
  function failed on this block of segments and to prevent further
  analysis.

These are the fundamental building blocks.
"""

import logging
from six import StringIO

from .match import MatchResult, curtail_string, join_segments_raw


def verbosity_logger(msg, verbosity=0, level='info', v_level=3):
    if verbosity >= v_level:
        print(msg)
    else:
        # Should be mostly equivalent to logging.info(msg)
        getattr(logging, level)(msg)


def frame_msg(msg):
    return "###\n#\n# {0}\n#\n###".format(msg)


def check_still_complete(segments_in, matched_segments, unmatched_segments):
    initial_str = join_segments_raw(segments_in)
    current_str = join_segments_raw(
        matched_segments + unmatched_segments
    )
    if initial_str != current_str:
        raise RuntimeError(
            "Dropped elements in sequence matching! {0!r} != {1!r}".format(
                initial_str, current_str))


class BaseSegment(object):
    type = 'base'
    parse_grammar = None
    match_grammar = None
    grammar = None
    comment_seperate = False
    is_whitespace = False
    optional = False  # NB: See the seguence grammar for details
    is_segment = True
    _name = None

    @property
    def name(self):
        return self._name or self.__class__.__name__

    @property
    def is_expandable(self):
        if self._parse_grammar():
            return True
        else:
            return False

    @property
    def is_code(self):
        return any([seg.is_code for seg in self.segments])

    @classmethod
    def is_optional(cls):
        return cls.optional

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
        else:
            return self.grammar

    def validate_segments(self, text="constructing"):
        # Check elements of segments:
        for elem in self.segments:
            if not isinstance(elem, BaseSegment):
                raise TypeError(
                    "In {0} {1}, found an element of the segments tuple which"
                    " isn't a segment. Instead found element of type {2}.\nFound: {3}\nFull segments:{4}".format(
                        text,
                        type(self),
                        type(elem),
                        elem,
                        self.segments
                    ))

    def __init__(self, segments, pos_marker=None):
        if hasattr(segments, 'matched_segments'):
            # Safely extract segments from a match
            self.segments = segments.matched_segments
        elif isinstance(segments, tuple):
            self.segments = segments
        elif isinstance(segments, list):
            self.segments = tuple(segments)
        else:
            raise TypeError(
                "Unexpected type passed to BaseSegment: {0}".format(
                    type(segments)))

        # Check elements of segments:
        self.validate_segments()

        if pos_marker:
            self.pos_marker = pos_marker
        else:
            # If no pos given, it's the pos of the first segment
            # Work out if we're dealing with a match result...
            if hasattr(segments, 'initial_match_pos_marker'):
                self.pos_marker = segments.initial_match_pos_marker()
            elif isinstance(segments, (tuple, list)):
                self.pos_marker = segments[0].pos_marker
            else:
                raise TypeError(
                    "Unexpected type passed to BaseSegment: {0}".format(
                        type(segments)))

    @classmethod
    def from_raw(cls, raw):
        raise NotImplementedError("from_raw is not implemented for {0}".format(cls.__name__))

    def parse(self, recurse=True, parse_depth=0, verbosity=0):
        """ Use the parse kwarg for testing, mostly to check how deep to go.
        True/False for yes or no, an integer allows a certain number of levels """

        # We should call the parse grammar on this segment, which calls
        # the match grammar on all it's children.

        # the parse_depth and recurse kwargs control how deep we will recurse for testing.
        if not self.segments:
            # This means we're a root segment, just return an unmutated self
            return self

        # Get the Parse Grammar
        g = self._parse_grammar()
        if g is None:
            logging.debug("{0}.parse: no grammar. returning".format(self.__class__.__name__))
            return self
        # Use the Parse Grammar (and the private method)
        # NOTE: No match_depth kwarg, because this is the start of the matching.
        m = g._match(segments=self.segments, parse_depth=parse_depth, verbosity=verbosity)

        # Calling unify here, allows the MatchResult class to do all the type checking.
        try:
            m = MatchResult.unify(m)
        except TypeError as err:
            logging.error(
                "[PD:{0}] {1}.parse. Error on unifying result of match grammar!".format(
                    parse_depth, self.__class__.__name__))
            raise err

        # Basic Validation, that we haven't dropped anything.
        check_still_complete(self.segments, m.matched_segments, m.unmatched_segments)

        if m.has_match():
            if m.is_complete():
                # Complete match, happy days!
                self.segments = m.matched_segments
            else:
                # Incomplete match.
                # For now this means the parsing has failed. Lets add the unmatched bit at the
                # end as something unparsable.
                # TODO: Do something more intelligent here.
                self.segments = m.matched_segments + (UnparsableSegment(
                    segments=m.unmatched_segments, expected="Nothing..."),)
        else:
            # If there's no match at this stage, then it's unparsable. That's
            # a problem at this stage so wrap it in an unparable segment and carry on.
            self.segments = UnparsableSegment(segments=self.segments, expected=g.expected_string()),  # NB: tuple

        # Validate new segments
        self.validate_segments(text="parsing")

        # Recurse if allowed (using the expand method to deal with the expansion)
        logging.debug(
            "{0}.parse: Done Parse. Plotting Recursion. Recurse={1!r}".format(
                self.__class__.__name__, recurse))
        parse_depth_msg = "###\n#\n# Beginning Parse Depth {0}: {1}\n#\n###\nInitial Structure:\n{2}".format(
            parse_depth + 1, self.__class__.__name__, self.stringify())
        if recurse is True:
            logging.debug(parse_depth_msg)
            self.segments = self.expand(self.segments, recurse=True, parse_depth=parse_depth + 1, verbosity=verbosity)
        elif isinstance(recurse, int):
            if recurse > 1:
                logging.debug(parse_depth_msg)
                self.segments = self.expand(self.segments, recurse=recurse - 1, parse_depth=parse_depth + 1, verbosity=verbosity)

        # Validate new segments
        self.validate_segments(text="expanding")

        return self

    def __repr__(self):
        return "<{0}: ({1})>".format(
            self.__class__.__name__,
            self.pos_marker)

    def _reconstruct(self):
        return "".join([seg._reconstruct() for seg in self.segments])

    @property
    def raw(self):
        return self._reconstruct()

    def _suffix(self):
        """ NB Override this for specific subclassesses if we want extra output """
        return ""

    def _preface(self, ident, tabsize, pos_idx, raw_idx):
        preface = (' ' * (ident * tabsize)) + self.__class__.__name__ + ":"
        preface = preface + (' ' * max(pos_idx - len(preface), 0)) + str(self.pos_marker)
        sfx = self._suffix()
        if sfx:
            return preface + (' ' * max(raw_idx - len(preface), 0)) + sfx
        else:
            return preface

    @property
    def _comments(self):
        return [seg for seg in self.segments if seg.type == 'comment']

    @property
    def _non_comments(self):
        return [seg for seg in self.segments if seg.type != 'comment']

    def stringify(self, ident=0, tabsize=4, pos_idx=60, raw_idx=80):
        buff = StringIO()
        preface = self._preface(ident=ident, tabsize=tabsize, pos_idx=pos_idx, raw_idx=raw_idx)
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

    @staticmethod
    def segs_to_tuple(segs, **kwargs):
        return tuple([seg.to_tuple(**kwargs) for seg in segs])

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
    def match(cls, segments, match_depth=0, parse_depth=0, verbosity=0):
        """
            Matching can be done from either the raw or the segments.
            This raw function can be overridden, or a grammar defined
            on the underlying class.
        """
        if cls._match_grammar():
            # Call the private method
            m = cls._match_grammar()._match(segments=segments, match_depth=match_depth + 1, parse_depth=parse_depth, verbosity=verbosity)

            # Calling unify here, allows the MatchResult class to do all the type checking.
            try:
                m = MatchResult.unify(m)
            except TypeError as err:
                logging.error(
                    "[PD:{0} MD:{1}] {2}.match. Error on unifying result of match grammar!".format(
                        parse_depth, match_depth, cls.__name__))
                raise err

            # Once unified we can deal with it just as a MatchResult
            if m.has_match():
                return MatchResult((cls(segments=m.matched_segments),), m.unmatched_segments)
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError("{0} has no match function implemented".format(cls.__name__))

    @classmethod
    def _match(cls, segments, match_depth=0, parse_depth=0, verbosity=0):
        """ A wrapper on the match function to do some basic validation and logging """
        verbosity_logger(
            "[PD:{0} MD:{1}] {2}._match IN [ls={3}]".format(parse_depth, match_depth, cls.__name__, len(segments)),
            verbosity=verbosity,
            v_level=4)
        if isinstance(segments, BaseSegment):
            segments = segments,  # Make into a tuple for compatability
        if not isinstance(segments, tuple):
            logging.warning(
                "{0}.match, was passed {1} rather than tuple or segment".format(
                    cls.__name__, type(segments)))
            if isinstance(segments, list):
                # Let's make it a tuple for compatibility
                segments = tuple(segments)
        m = cls.match(segments, match_depth=match_depth, parse_depth=parse_depth, verbosity=verbosity)
        if not isinstance(m, tuple) and m is not None:
            logging.warning(
                "{0}.match, returned {1} rather than tuple".format(
                    cls.__name__, type(m)))
        verbosity_logger(
            "[PD:{0} MD:{1}] {2}._match OUT [m={3}]".format(parse_depth, match_depth, cls.__name__, m),
            verbosity=verbosity,
            v_level=4)
        # Basic Validation
        check_still_complete(segments, m.matched_segments, m.unmatched_segments)
        return m

    @staticmethod
    def expand(segments, recurse=True, parse_depth=0, verbosity=0):
        segs = tuple()
        for stmt in segments:
            try:
                if not stmt.is_expandable:
                    logging.info("[PD:{0}] Skipping expansion of {1}...".format(parse_depth, stmt))
                    segs += stmt,
                    continue
            except Exception as err:
                # raise ValueError("{0} has no attribute `is_expandable`. This segment appears poorly constructed.".format(stmt))
                logging.error("{0} has no attribute `is_expandable`. This segment appears poorly constructed.".format(stmt))
                raise err
            if not hasattr(stmt, 'parse'):
                raise ValueError("{0} has no method `parse`. This segment appears poorly constructed.".format(stmt))
            parse_depth_msg = "Parse Depth {0}. Expanding: {1}: {2!r}".format(
                parse_depth, stmt.__class__.__name__,
                curtail_string(stmt.raw))
            verbosity_logger(frame_msg(parse_depth_msg), verbosity=verbosity)
            res = stmt.parse(recurse=recurse, parse_depth=parse_depth, verbosity=verbosity)
            if isinstance(res, BaseSegment):
                segs += (res,)
            else:
                # We might get back an iterable of segments
                segs += tuple(res)
        # Basic Validation
        check_still_complete(segments, segs, tuple())
        return segs

    def raw_list(self):
        """ List of raw elements, mostly for testing or searching """
        buff = []
        for s in self.segments:
            buff += s.raw_list()
        return buff

    def iter_raw_seg(self):
        """ Iterate raw segments, mostly for searching """
        for s in self.segments:
            for seg in s.iter_raw_seg():
                yield seg

    def iter_unparsables(self):
        """ Iterate through any unparsables this segment may contain """
        for s in self.segments:
            for u in s.iter_unparsables():
                yield u

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

    def __len__(self):
        """ implement a len method to make everyone's lives easier """
        return 1

    @classmethod
    def expected_string(cls):
        """ This is never going to be called on an _instance_
        but rather on the class, as part of a grammar, and therefore
        as part of the matching phase. So we use the match grammar."""
        return cls._match_grammar().expected_string()

    @classmethod
    def as_optional(cls):
        """ Used in constructing grammars, will make an identical class
        but with the optional argument set to true. Used in constructing
        sequences """
        # Now lets make the classname (it indicates the mother class for clarity)
        classname = "Optional_{0}".format(cls.__name__)
        # This is the magic, we generate a new class! SORCERY
        newclass = type(classname, (cls, ),
                        dict(optional=True))
        # Now we return that class in the abstract. NOT INSTANTIATED
        return newclass


class RawSegment(BaseSegment):
    """ This is a segment without any subsegments,
    it could be postprocessed later, but then it would be
    a different class. """
    type = 'raw'
    _is_code = False
    _template = '<unset>'
    _case_sensitive = False

    @property
    def is_expandable(self):
        return False

    @property
    def is_code(self):
        return self._is_code

    def __init__(self, raw, pos_marker):
        self._raw = raw
        # pos marker is required here
        self.pos_marker = pos_marker

    def iter_raw_seg(self):
        """ Iterate raw segments, mostly for searching """
        yield self

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
        preface = self._preface(ident=ident, tabsize=tabsize, pos_idx=pos_idx, raw_idx=raw_idx)
        return preface + '\n'

    def _suffix(self):
        return "{0!r}".format(self.raw)

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
                             _name=name, **kwargs))
        # Now we return that class in the abstract. NOT INSTANTIATED
        return newclass


class UnparsableSegment(BaseSegment):
    type = 'unparsable'
    # From here down, comments are printed seperately.
    comment_seperate = True
    _expected = ""

    def __init__(self, *args, **kwargs):
        self._expected = kwargs.pop('expected', "")
        super(UnparsableSegment, self).__init__(*args, **kwargs)

    def _suffix(self):
        return "!! Expected: {0!r}".format(self._expected)

    def iter_unparsables(self):
        """ As this is an unparsable, it should yield itself """
        yield self
