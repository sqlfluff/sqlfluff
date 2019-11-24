"""Base segment definitions.

Here we define:
- BaseSegment. This is the root class for all segments, and is
  designed to hold other subsegments.
- RawSegment. This is designed to be the root segment, without
  any children, and the output of the lexer.
- UnparsableSegment. A special wrapper to indicate that the parse
  function failed on this block of segments and to prevent further
  analysis.

These are the fundamental building blocks of the rest of the parser.
"""

import logging
from six import StringIO

from .match import MatchResult, curtail_string, join_segments_raw
from ..errors import SQLLintError


def verbosity_logger(msg, verbosity=0, level='info', v_level=3):
    """Log or print based on configuration."""
    if verbosity >= v_level:
        print(msg)
    else:
        # Should be mostly equivalent to logging.info(msg)
        getattr(logging, level)(msg)


def parse_match_logging(grammar, func, msg, parse_context, v_level, **kwargs):
    """Log in a particular consistent format for use while matching."""
    s = "[PD:{0} MD:{1}]\t{2:<50}\t{3:<20}".format(
        parse_context.parse_depth, parse_context.match_depth,
        ('.' * parse_context.match_depth) + str(parse_context.match_segment),
        "{0}.{1} {2}".format(grammar, func, msg)
    )
    if kwargs:
        s += "\t[{0}]".format(
            ', '.join(["{0}={1}".format(
                k, repr(v) if isinstance(v, str) else v) for k, v in kwargs.items()])
        )
    verbosity_logger(s, parse_context.verbosity, v_level=v_level)


def frame_msg(msg):
    """Frame a message with hashes so that it covers five lines."""
    return "###\n#\n# {0}\n#\n###".format(msg)


def check_still_complete(segments_in, matched_segments, unmatched_segments):
    """Check that the segments in are the same as the segments out."""
    initial_str = join_segments_raw(segments_in)
    current_str = join_segments_raw(
        matched_segments + unmatched_segments
    )
    if initial_str != current_str:
        raise RuntimeError(
            "Dropped elements in sequence matching! {0!r} != {1!r}".format(
                initial_str, current_str))


class ParseContext(object):
    """The context for parsing. It holds configuration and rough state.

    We expect that an object (or copy of this object) will be passed
    around rather than the individual variables for parse and match depth
    as before.
    """

    __slots__ = ['match_depth', 'parse_depth', 'verbosity', 'dialect', 'match_segment', 'recurse']

    def __init__(self, dialect=None, verbosity=0, match_depth=0, parse_depth=0, match_segment=None, recurse=True):
        # Write all the variables in a DRY way. Yes it's a bit convoluted. Sorry.
        for k in self.__slots__:
            setattr(self, k, locals()[k])

    def copy(self, incr=None, decr=None, **kwargs):
        """Make a copy of the parse context, optionally with some edited variables."""
        current_vals = {k: getattr(self, k) for k in self.__slots__}
        current_vals.update(kwargs or {})
        # Increment
        if isinstance(incr, str):
            current_vals[incr] += 1
        elif incr:
            for k in incr:
                current_vals[k] += 1
        # Decrement
        if isinstance(decr, str):
            current_vals[decr] -= 1
        elif decr:
            for k in decr:
                current_vals[k] -= 1
        # Return
        return self.__class__(**current_vals)

    @classmethod
    def from_config(cls, config):
        """Construct a `ParseContext` from a `FluffConfig`."""
        return cls(dialect=config.get('dialect_obj'), recurse=config.get('recurse'))


class BaseSegment(object):
    """The base segment element.

    This defines the base element which drives both Lexing, Parsing and Linting.
    A large chunk of the logic which defines those three operations are centered
    here. Much of what is defined in the BaseSegment is also used by it's many
    subclasses rather than directly here.

    For clarity, the `BaseSement` is mostly centered around a segment which contains
    other subsegments. For segments which don't have *children*, refer to the `RawSegment`
    class (which still inherits from this one).

    Segments are used both as instances to hold chunks of text, but also as classes
    themselves where they function a lot like grammars, and return instances of themselves
    when they match. The many classmethods in this class are usually to serve their
    purpose as a matcher.
    """

    type = 'base'
    parse_grammar = None
    match_grammar = None
    grammar = None
    comment_seperate = False
    is_whitespace = False
    optional = False  # NB: See the seguence grammar for details
    is_segment = True
    _name = None
    _func = None  # Available for use by subclasses (e.g. the LambdaSegment)

    @property
    def name(self):
        """The name of this segment.

        The reason for two routes for names is that some subclasses
        might want to overrise the name rather than just getting it
        the class name.
        """
        return self._name or self.__class__.__name__

    @property
    def is_expandable(self):
        """Return true if it is meaningful to call `expand` on this segment."""
        if self._parse_grammar():
            return True
        else:
            return False

    @property
    def is_code(self):
        """Return True if this segment contains any code."""
        return any([seg.is_code for seg in self.segments])

    @property
    def is_comment(self):
        """Return True if this is entirely made of comments."""
        return all([seg.is_comment for seg in self.segments])

    @classmethod
    def is_optional(cls):
        """Return True if this segment is optional.

        This is used primarily in sequence matching, where optional
        segments can be skipped.
        """
        return cls.optional

    @classmethod
    def _match_grammar(self):
        """Return the `match_grammar` attribute if present, or the `grammar` attribute if not."""
        if self.match_grammar:
            return self.match_grammar
        else:
            return self.grammar

    @classmethod
    def _parse_grammar(self):
        """Return the `parse_grammar` attribute if present, or the `grammar` attribute if not."""
        if self.parse_grammar:
            return self.parse_grammar
        else:
            return self.grammar

    def validate_segments(self, text="constructing"):
        """Check the elements of the `segments` attribute are all themselves segments."""
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
        if len(segments) == 0:
            raise RuntimeError(
                "Setting {0} with a zero length segment set. This shouldn't happen.".format(
                    self.__class__))

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
        """Instantiate a segment from a string. This is only implemented for the `FileSegment`."""
        raise NotImplementedError("from_raw is not implemented for {0}".format(cls.__name__))

    def parse(self, parse_context=None):
        """Use the parse grammar to find subsegments within this segment.

        A large chunk of the logic around this can be found in the `expand` method.

        Use the parse setting in the context for testing, mostly to check how deep to go.
        True/False for yes or no, an integer allows a certain number of levels.
        """
        if not parse_context.dialect:
            raise RuntimeError("No dialect provided to {0!r}!".format(self))

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
        m = g._match(
            segments=self.segments,
            parse_context=parse_context.copy(
                match_segment=self.__class__.__name__
            )
        )

        # Calling unify here, allows the MatchResult class to do all the type checking.
        try:
            m = MatchResult.unify(m)
        except TypeError as err:
            logging.error(
                "[PD:{0}] {1}.parse. Error on unifying result of match grammar!".format(
                    parse_context.parse_depth, self.__class__.__name__))
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
            self.segments = UnparsableSegment(
                segments=self.segments,
                expected=g.expected_string(dialect=parse_context.dialect)),  # NB: tuple

        # Validate new segments
        self.validate_segments(text="parsing")

        # Recurse if allowed (using the expand method to deal with the expansion)
        logging.debug(
            "{0}.parse: Done Parse. Plotting Recursion. Recurse={1!r}".format(
                self.__class__.__name__, parse_context.recurse))
        parse_depth_msg = "###\n#\n# Beginning Parse Depth {0}: {1}\n#\n###\nInitial Structure:\n{2}".format(
            parse_context.parse_depth + 1, self.__class__.__name__, self.stringify())
        if parse_context.recurse is True:
            logging.debug(parse_depth_msg)
            self.segments = self.expand(
                self.segments,
                parse_context=parse_context.copy(
                    incr='parse_depth', match_depth=0, recurse=True
                )
            )
        elif isinstance(parse_context.recurse, int):
            if parse_context.recurse > 1:
                logging.debug(parse_depth_msg)
                self.segments = self.expand(
                    self.segments,
                    parse_context=parse_context.copy(decr='recurse', incr='parse_depth')
                )
        # Validate new segments
        self.validate_segments(text="expanding")

        return self

    def __repr__(self):
        return "<{0}: ({1})>".format(
            self.__class__.__name__,
            self.pos_marker)

    def _reconstruct(self):
        """Make a string from the segments of this segment."""
        return "".join([seg._reconstruct() for seg in self.segments])

    @property
    def raw(self):
        """Make a string from the segments of this segment."""
        return self._reconstruct()

    def _suffix(self):
        """Return any extra output required at the end when logging.

        NB Override this for specific subclassesses if we want extra output.
        """
        return ""

    def _preface(self, ident, tabsize, pos_idx, raw_idx):
        """Returns the preamble to any logging."""
        preface = (' ' * (ident * tabsize)) + self.__class__.__name__ + ":"
        preface = preface + (' ' * max(pos_idx - len(preface), 0)) + str(self.pos_marker)
        sfx = self._suffix()
        if sfx:
            return preface + (' ' * max(raw_idx - len(preface), 0)) + sfx
        else:
            return preface

    @property
    def _comments(self):
        """Returns only the comment elements of this segment."""
        return [seg for seg in self.segments if seg.type == 'comment']

    @property
    def _non_comments(self):
        """Returns only the non-comment elements of this segment."""
        return [seg for seg in self.segments if seg.type != 'comment']

    def stringify(self, ident=0, tabsize=4, pos_idx=60, raw_idx=80):
        """Use indentation to render this segment and it's children as a string."""
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
        """Return a tuple structure from an iterable of segments."""
        return tuple([seg.to_tuple(**kwargs) for seg in segs])

    def to_tuple(self, **kwargs):
        """Return a tuple structure from this segment."""
        # works for both base and raw
        code_only = kwargs.get('code_only', False)
        show_raw = kwargs.get('show_raw', False)
        if show_raw and not self.segments:
            return (self.type, self.raw)
        elif code_only:
            return (self.type, tuple([seg.to_tuple(**kwargs) for seg in self.segments if seg.is_code]))
        else:
            return (self.type, tuple([seg.to_tuple(**kwargs) for seg in self.segments]))

    @classmethod
    def match(cls, segments, parse_context):
        """Match a list of segments against this segment.

        Note: Match for segments is done in the ABSTRACT.
        When dealing with concrete then we're always in parse.
        Parse is what happens during expand.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        if cls._match_grammar():
            # Call the private method
            m = cls._match_grammar()._match(segments=segments, parse_context=parse_context.copy(incr='match_depth'))

            # Calling unify here, allows the MatchResult class to do all the type checking.
            try:
                m = MatchResult.unify(m)
            except TypeError as err:
                logging.error(
                    "[PD:{0} MD:{1}] {2}.match. Error on unifying result of match grammar!".format(
                        parse_context.parse_depth, parse_context.match_depth, cls.__name__))
                raise err

            # Once unified we can deal with it just as a MatchResult
            if m.has_match():
                return MatchResult((cls(segments=m.matched_segments),), m.unmatched_segments)
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError("{0} has no match function implemented".format(cls.__name__))

    @classmethod
    def _match(cls, segments, parse_context):
        """A wrapper on the match function to do some basic validation and logging."""
        parse_match_logging(
            cls.__name__, '_match', 'IN', parse_context=parse_context,
            v_level=4, ls=len(segments))

        if isinstance(segments, BaseSegment):
            segments = segments,  # Make into a tuple for compatability

        if not isinstance(segments, tuple):
            logging.warning(
                "{0}.match, was passed {1} rather than tuple or segment".format(
                    cls.__name__, type(segments)))
            if isinstance(segments, list):
                # Let's make it a tuple for compatibility
                segments = tuple(segments)

        if len(segments) == 0:
            logging.info("{0}._match, was passed zero length segments list".format(cls.__name__))

        m = cls.match(segments, parse_context=parse_context)

        if not isinstance(m, tuple) and m is not None:
            logging.warning(
                "{0}.match, returned {1} rather than tuple".format(
                    cls.__name__, type(m)))

        parse_match_logging(
            cls.__name__, '_match', 'OUT',
            parse_context=parse_context, v_level=4, m=m)
        # Basic Validation
        check_still_complete(segments, m.matched_segments, m.unmatched_segments)
        return m

    @staticmethod
    def expand(segments, parse_context):
        """Expand the list of child segments using their `parse` methods."""
        segs = tuple()
        for stmt in segments:
            try:
                if not stmt.is_expandable:
                    logging.info("[PD:{0}] Skipping expansion of {1}...".format(parse_context.parse_depth, stmt))
                    segs += stmt,
                    continue
            except Exception as err:
                # raise ValueError("{0} has no attribute `is_expandable`. This segment appears poorly constructed.".format(stmt))
                logging.error("{0} has no attribute `is_expandable`. This segment appears poorly constructed.".format(stmt))
                raise err
            if not hasattr(stmt, 'parse'):
                raise ValueError("{0} has no method `parse`. This segment appears poorly constructed.".format(stmt))
            parse_depth_msg = "Parse Depth {0}. Expanding: {1}: {2!r}".format(
                parse_context.parse_depth, stmt.__class__.__name__,
                curtail_string(stmt.raw, length=40))
            verbosity_logger(frame_msg(parse_depth_msg), verbosity=parse_context.verbosity)
            res = stmt.parse(parse_context=parse_context)
            if isinstance(res, BaseSegment):
                segs += (res,)
            else:
                # We might get back an iterable of segments
                segs += tuple(res)
        # Basic Validation
        check_still_complete(segments, segs, tuple())
        return segs

    def raw_list(self):
        """Return a list of raw elements, mostly for testing or searching."""
        buff = []
        for s in self.segments:
            buff += s.raw_list()
        return buff

    def iter_raw_seg(self):
        """Iterate raw segments, mostly for searching."""
        for s in self.segments:
            for seg in s.iter_raw_seg():
                yield seg

    def iter_unparsables(self):
        """Iterate through any unparsables this segment may contain."""
        for s in self.segments:
            for u in s.iter_unparsables():
                yield u

    def type_set(self):
        """Return a set of the types contained, mostly for testing."""
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
        """Implement a len method to make everyone's lives easier."""
        return 1

    def is_raw(self):
        """Return True if this segment has no children."""
        return len(self.segments) == 0

    @classmethod
    def expected_string(cls, dialect=None, called_from=None):
        """Return the expected string for this segment.

        This is never going to be called on an _instance_
        but rather on the class, as part of a grammar, and therefore
        as part of the matching phase. So we use the match grammar.
        """
        return cls._match_grammar().expected_string(dialect=dialect, called_from=called_from)

    @classmethod
    def as_optional(cls):
        """Construct a copy of this class, but with the optional flag set true.

        Used in constructing grammars, will make an identical class
        but with the optional argument set to true. Used in constructing
        sequences.
        """
        # Now lets make the classname (it indicates the mother class for clarity)
        classname = "Optional_{0}".format(cls.__name__)
        # This is the magic, we generate a new class! SORCERY
        newclass = type(classname, (cls, ),
                        dict(optional=True))
        # Now we return that class in the abstract. NOT INSTANTIATED
        return newclass

    def apply_fixes(self, fixes):
        """Apply an iterable of fixes to this segment.

        Used in applying fixes if we're fixing linting errors.
        If anything changes, this should return a new version of the segment
        rather than mutating the original.

        Note: We need to have fixes to apply AND this must have children. In the case
        of raw segments, they will be replaced or removed by their parent and
        so this function should just return self.
        """
        # Let's check what we've been given.
        if fixes and isinstance(fixes[0], SQLLintError):
            logging.error("Transforming `fixes` from errors into a list of fixes")
            # We've got linting errors, let's aggregate them into a list of fixes
            buff = []
            for err in fixes:
                buff += err.fixes
            # Overwrite fixes
            fixes = buff

        if fixes and not self.is_raw():
            # Get a reference to self to start with, but this will rapidly
            # become a working copy.
            r = self

            # Make a working copy
            seg_buffer = []
            todo_buffer = list(self.segments)
            while True:
                if len(todo_buffer) == 0:
                    break
                else:
                    seg = todo_buffer.pop(0)
                    unused_fixes = []
                    for f in fixes:
                        if f.anchor == seg:
                            if f.edit_type == 'delete':
                                # We're just getting rid of this segment.
                                seg = None
                            elif f.edit_type in ('edit', 'create'):
                                # We're doing a replacement (it could be a single segment or an iterable)
                                if isinstance(f.edit, BaseSegment):
                                    seg_buffer.append(f.edit)
                                else:
                                    for s in f.edit:
                                        seg_buffer.append(s)

                                if f.edit_type == 'create':
                                    # in the case of a creation, also add this segment on the end
                                    seg_buffer.append(seg)
                            else:
                                raise ValueError(
                                    "Unexpected edit_type: {0!r} in {1!r}".format(
                                        f.edit_type, f))
                            # We've applied a fix here. Move on, this also consumes the fix
                            # TODO: Maybe deal with overlapping fixes later.
                            break
                        else:
                            # We've not used the fix so we should keep it in the list for later.
                            unused_fixes.append(f)
                    else:
                        seg_buffer.append(seg)
                # Switch over the the unused list
                fixes = unused_fixes

            # Then recurse (i.e. deal with the children) (Requeueing)
            seg_queue = seg_buffer
            seg_buffer = []
            for seg in seg_queue:
                s, fixes = seg.apply_fixes(fixes)
                seg_buffer.append(s)

            # Reform into a new segment
            r = r.__class__(
                segments=tuple(seg_buffer),
                pos_marker=r.pos_marker
            )

            # Lastly, before returning, we should realign positions.
            # Note: Realign also returns a copy
            return r.realign(), fixes
        else:
            return self, fixes

    def realign(self):
        """Realign the positions in this segment.

        Returns:
            a copy of this class with the pos_markers realigned.

        Note: this is used mostly during fixes.

        Realign is recursive. We will assume that the pos_marker of THIS segment is
        truthful, and that during recursion it will have been set by the parent.

        This function will align the pos marker if it's direct children, we then
        recurse to realign their children.

        """
        seg_buffer = []
        todo_buffer = list(self.segments)
        running_pos = self.pos_marker

        while True:
            if len(todo_buffer) == 0:
                # We're done.
                break
            else:
                # Get the first off the buffer
                seg = todo_buffer.pop(0)
                # We'll preserve statement indexes so we should keep track of that.
                # When recreating, we use the DELTA of the index so that's what matter...
                idx = seg.pos_marker.statement_index - running_pos.statement_index
                if len(seg.segments) > 0:
                    # It's a compound segment, so keep track of it's children
                    child_segs = seg.segments
                    # Create a new segment of the same type with the new position
                    seg = seg.__class__(
                        segments=child_segs,
                        pos_marker=running_pos
                    )
                    # Realign the children of that class
                    seg = seg.realign()
                else:
                    # It's a raw segment...
                    # Create a new segment of the same type with the new position
                    seg = seg.__class__(
                        raw=seg.raw,
                        pos_marker=running_pos
                    )
                # Update the running position with the content of that segment
                running_pos = running_pos.advance_by(
                    raw=seg.raw, idx=idx
                )
                # Add the buffer to my new segment
                seg_buffer.append(seg)

        # Create a new version of this class with the new details
        return self.__class__(
            segments=tuple(seg_buffer),
            pos_marker=self.pos_marker
        )


class RawSegment(BaseSegment):
    """This is a segment without any subsegments."""

    type = 'raw'
    _is_code = False
    _is_comment = False
    _template = '<unset>'
    _case_sensitive = False

    @property
    def is_expandable(self):
        """Return true if it is meaningful to call `expand` on this segment."""
        return False

    @property
    def is_code(self):
        """Return True if this segment is code."""
        return self._is_code

    @property
    def is_comment(self):
        """Return True if this segment is a comment."""
        return self._is_comment

    def __init__(self, raw, pos_marker):
        self._raw = raw
        # pos marker is required here
        self.pos_marker = pos_marker

    def iter_raw_seg(self):
        """Iterate raw segments, mostly for searching."""
        yield self

    @property
    def segments(self):
        """Return an empty list of child segments.

        This is in case something tries to iterate on this segment.
        """
        return []

    def raw_list(self):
        """Return a list of the raw content of this segment."""
        return [self.raw]

    @property
    def raw(self):
        """Return a strong of the raw content of this segment."""
        return self._raw

    def _reconstruct(self):
        """Return a strong of the raw content of this segment."""
        return self.raw

    def __repr__(self):
        return "<{0}: ({1}) {2!r}>".format(
            self.__class__.__name__,
            self.pos_marker,
            self.raw)

    def stringify(self, ident=0, tabsize=4, pos_idx=60, raw_idx=80):
        """Use indentation to render this segment and it's children as a string."""
        preface = self._preface(ident=ident, tabsize=tabsize, pos_idx=pos_idx, raw_idx=raw_idx)
        return preface + '\n'

    def _suffix(self):
        """Return any extra output required at the end when logging.

        NB Override this for specific subclassesses if we want extra output.
        """
        return "{0!r}".format(self.raw)

    @classmethod
    def make(cls, template, case_sensitive=False, name=None, **kwargs):
        """Make a subclass of the segment using a method."""
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

    def edit(self, raw):
        """Create a new segment, with exactly the same position but different content.

        Returns:
            A copy of this object with new contents.

        Used mostly by fixes.

        """
        return self.__class__(
            raw=raw,
            pos_marker=self.pos_marker
        )


class UnparsableSegment(BaseSegment):
    """This is a segment which can't be parsed. It indicates a error during parsing."""

    type = 'unparsable'
    # From here down, comments are printed seperately.
    comment_seperate = True
    _expected = ""

    def __init__(self, *args, **kwargs):
        self._expected = kwargs.pop('expected', "")
        super(UnparsableSegment, self).__init__(*args, **kwargs)

    def _suffix(self):
        """Return any extra output required at the end when logging.

        NB Override this for specific subclassesses if we want extra output.
        """
        return "!! Expected: {0!r}".format(self._expected)

    def iter_unparsables(self):
        """Iterate through any unparsables.

        As this is an unparsable, it should yield itself.
        """
        yield self
