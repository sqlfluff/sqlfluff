"""Base segment definitions.

Here we define:
- BaseSegment. This is the root class for all segments, and is
  designed to hold other subsegments.
- UnparsableSegment. A special wrapper to indicate that the parse
  function failed on this block of segments and to prevent further
  analysis.
"""

from io import StringIO
from benchit import BenchIt
from typing import Optional

from ..match_result import MatchResult
from ..match_logging import parse_match_logging
from ..match_wrapper import match_wrapper
from ..helpers import frame_msg, check_still_complete, trim_non_code, curtail_string
from ..matchable import Matchable


class BaseSegment:
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

    # `type` should be the *category* of this kind of segment
    type = "base"
    parse_grammar: Optional[Matchable] = None
    match_grammar: Optional[Matchable] = None
    comment_seperate = False
    is_whitespace = False
    optional = False  # NB: See the sequence grammar for details
    is_segment = True
    _name = None
    is_meta = False
    # Are we able to have non-code at the start or end?
    can_start_end_non_code = False
    # Can we allow it to be empty? Usually used in combination
    # with the can_start_end_non_code.
    allow_empty = False
    # What should we trim off the ends to get to content
    trim_chars = None
    trim_start = None
    # A cache variable for expandable
    _is_expandable = None

    def __init__(self, segments, pos_marker=None, validate=True):
        if len(segments) == 0:
            raise RuntimeError(
                "Setting {0} with a zero length segment set. This shouldn't happen.".format(
                    self.__class__
                )
            )

        if hasattr(segments, "matched_segments"):
            # Safely extract segments from a match
            self.segments = segments.matched_segments
        elif isinstance(segments, tuple):
            self.segments = segments
        elif isinstance(segments, list):
            self.segments = tuple(segments)
        else:
            raise TypeError(
                "Unexpected type passed to BaseSegment: {0}".format(type(segments))
            )

        # Check elements of segments:
        self.validate_segments(validate=validate)

        if pos_marker:
            self.pos_marker = pos_marker
        else:
            # If no pos given, it's the pos of the first segment.
            if isinstance(segments, (tuple, list)):
                self.pos_marker = segments[0].pos_marker.combine(
                    *(seg.pos_marker for seg in segments)
                )
            else:
                raise TypeError(
                    "Unexpected type passed to BaseSegment: {0}".format(type(segments))
                )

    def __eq__(self, other):
        # Equal if type, content and pos are the same
        # NB: this should also work for RawSegment
        return (
            type(self) is type(other)
            and (self.raw == other.raw)
            and (self.pos_marker == other.pos_marker)
        )

    def __repr__(self):
        return "<{0}: ({1})>".format(self.__class__.__name__, self.pos_marker)

    # ################ PRIVATE PROPERTIES

    @property
    def _comments(self):
        """Returns only the comment elements of this segment."""
        return [seg for seg in self.segments if seg.type == "comment"]

    @property
    def _non_comments(self):
        """Returns only the non-comment elements of this segment."""
        return [seg for seg in self.segments if seg.type != "comment"]

    # ################ PUBLIC PROPERTIES

    @property
    def name(self):
        """The name of this segment.

        The reason for two routes for names is that some subclasses
        might want to overrise the name rather than just getting it
        the class name.

        Name should be specific to this kind of segment, while `type`
        should be a higher level descriptor of the kind of segment.
        For example, the name of `+` is 'plus' but the type might be
        'binary_operator'.
        """
        return self._name or self.__class__.__name__

    @property
    def is_expandable(self):
        """Return true if it is meaningful to call `expand` on this segment.

        We need to do this recursively because even if *this* segment doesn't
        need expanding, maybe one of it's children does.

        Once a segment is *not* expandable, it can never become so, which is
        why the variable is cached.
        """
        if self._is_expandable is False:
            return self._is_expandable
        elif self.parse_grammar:
            return True
        elif self.segments and any(s.is_expandable for s in self.segments):
            return True
        else:
            # Cache the variable
            self._is_expandable = False
            return False

    @property
    def is_code(self):
        """Return True if this segment contains any code."""
        return any(seg.is_code for seg in self.segments)

    @property
    def is_comment(self):
        """Return True if this is entirely made of comments."""
        return all(seg.is_comment for seg in self.segments)

    @property
    def raw(self):
        """Make a string from the segments of this segment."""
        return self._reconstruct()

    @property
    def raw_upper(self):
        """Make an uppercase string from the segments of this segment."""
        return self._reconstruct().upper()

    # ################ STATIC METHODS

    @staticmethod
    def segs_to_tuple(segs, **kwargs):
        """Return a tuple structure from an iterable of segments."""
        return tuple(seg.to_tuple(**kwargs) for seg in segs)

    @staticmethod
    def _suffix():
        """Return any extra output required at the end when logging.

        NB Override this for specific subclassesses if we want extra output.
        """
        return ""

    @staticmethod
    def expand(segments, parse_context):
        """Expand the list of child segments using their `parse` methods."""
        segs = ()
        for stmt in segments:
            try:
                if not stmt.is_expandable:
                    parse_context.logger.info(
                        "[PD:%s] Skipping expansion of %s...",
                        parse_context.parse_depth,
                        stmt,
                    )
                    segs += (stmt,)
                    continue
            except Exception as err:
                # raise ValueError("{0} has no attribute `is_expandable`. This segment appears poorly constructed.".format(stmt))
                parse_context.logger.error(
                    "%s has no attribute `is_expandable`. This segment appears poorly constructed.",
                    stmt,
                )
                raise err
            if not hasattr(stmt, "parse"):
                raise ValueError(
                    "{0} has no method `parse`. This segment appears poorly constructed.".format(
                        stmt
                    )
                )
            parse_depth_msg = "Parse Depth {0}. Expanding: {1}: {2!r}".format(
                parse_context.parse_depth,
                stmt.__class__.__name__,
                curtail_string(stmt.raw, length=40),
            )
            parse_context.logger.info(frame_msg(parse_depth_msg))
            res = stmt.parse(parse_context=parse_context)
            if isinstance(res, BaseSegment):
                segs += (res,)
            else:
                # We might get back an iterable of segments
                segs += tuple(res)
        # Basic Validation
        check_still_complete(segments, segs, ())
        return segs

    # ################ CLASS METHODS

    @classmethod
    def simple(cls, parse_context):
        """Does this matcher support an uppercase hash matching route?

        This should be true if the MATCH grammar is simple. Most more
        complicated segments will be assumed to overwrite this method
        if they wish to be considered simple.
        """
        if cls.match_grammar:
            return cls.match_grammar.simple(parse_context=parse_context)
        else:
            # Other segments will either override this method, or aren't
            # simple.
            return False

    @classmethod
    def is_optional(cls):
        """Return True if this segment is optional.

        This is used primarily in sequence matching, where optional
        segments can be skipped.
        """
        return cls.optional

    @classmethod
    def is_type(cls, *seg_type):
        """Is this segment (or it's parent) of the given type."""
        # Do we match on the type of _this_ class.
        if cls.type in seg_type:
            return True
        # Have we reached the bottom?
        elif cls.type == "base":
            return False
        # If not, check parent classes.
        else:
            return any(base_class.is_type(*seg_type) for base_class in cls.__bases__)

    @classmethod
    def structural_simplify(cls, elem):
        """Simplify the structure recursively so it serializes nicely in json/yaml."""
        if isinstance(elem, tuple):
            # Does this look like an element?
            if len(elem) == 2 and isinstance(elem[0], str):
                # This looks like a single element, make a dict
                elem = {elem[0]: cls.structural_simplify(elem[1])}
            elif isinstance(elem[0], tuple):
                # This looks like a list of elements.
                keys = [e[0] for e in elem]
                # Any duplicate elements?
                if len(set(keys)) == len(keys):
                    # No, we can use a mapping typle
                    elem = {e[0]: cls.structural_simplify(e[1]) for e in elem}
                else:
                    # Yes, this has to be a list :(
                    elem = [cls.structural_simplify(e) for e in elem]
        return elem

    @classmethod
    @match_wrapper(v_level=4)
    def match(cls, segments, parse_context):
        """Match a list of segments against this segment.

        Note: Match for segments is done in the ABSTRACT.
        When dealing with concrete then we're always in parse.
        Parse is what happens during expand.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        # Edge case, but it's possible that we have *already matched* on
        # a previous cycle. Do should first check whether this is a case
        # of that.
        if len(segments) == 1 and isinstance(segments[0], cls):
            # This has already matched. Winner.
            parse_match_logging(
                cls.__name__,
                "_match",
                "SELF",
                parse_context=parse_context,
                v_level=3,
                symbol="+++",
            )
            return MatchResult.from_matched(segments)
        elif len(segments) > 1 and isinstance(segments[0], cls):
            parse_match_logging(
                cls.__name__,
                "_match",
                "SELF",
                parse_context=parse_context,
                v_level=3,
                symbol="+++",
            )
            # This has already matched, but only partially.
            return MatchResult((segments[0],), segments[1:])

        if cls.match_grammar:
            # Call the private method
            with parse_context.deeper_match() as ctx:
                m = cls.match_grammar.match(segments=segments, parse_context=ctx)

            # Calling unify here, allows the MatchResult class to do all the type checking.
            if not isinstance(m, MatchResult):
                raise TypeError(
                    "[PD:{0} MD:{1}] {2}.match. Result is {3}, not a MatchResult!".format(
                        parse_context.parse_depth,
                        parse_context.match_depth,
                        cls.__name__,
                        type(m),
                    )
                )
            # Once unified we can deal with it just as a MatchResult
            if m.has_match():
                return MatchResult(
                    (cls(segments=m.matched_segments),), m.unmatched_segments
                )
            else:
                return MatchResult.from_unmatched(segments)
        else:
            raise NotImplementedError(
                "{0} has no match function implemented".format(cls.__name__)
            )

    # ################ PRIVATE INSTANCE METHODS

    def _reconstruct(self):
        """Make a string from the segments of this segment."""
        return "".join(seg.raw for seg in self.segments)

    def _preface(self, ident, tabsize):
        """Returns the preamble to any logging."""
        padded_type = "{padding}{modifier}{type}".format(
            padding=" " * (ident * tabsize),
            modifier="[META] " if self.is_meta else "",
            type=self.type + ":",
        )
        preface = "{pos:20}|{padded_type:60}  {suffix}".format(
            pos=str(self.pos_marker) if self.pos_marker else "-",
            padded_type=padded_type,
            suffix=self._suffix() or "",
        )
        # Trim unnecessary whitespace before returning
        return preface.rstrip()

    # ################ PUBLIC INSTANCE METHODS

    def validate_segments(self, text="constructing", validate=True):
        """Validate the current set of segments.

        Check the elements of the `segments` attribute are all
        themselves segments, and that the positions match up.

        `validate` confirms whether we should check contigiousness.
        """
        # Placeholder variables for positions
        start_pos = None
        end_pos = None
        prev_seg = None
        for elem in self.segments:
            if not isinstance(elem, BaseSegment):
                raise TypeError(
                    "In {0} {1}, found an element of the segments tuple which"
                    " isn't a segment. Instead found element of type {2}.\nFound: {3}\nFull segments:{4}".format(
                        text, type(self), type(elem), elem, self.segments
                    )
                )
            # While applying fixes, we shouldn't validate here, because it will fail.
            if validate:
                # If we have a comparison point, validate that
                if end_pos and elem.get_start_pos_marker() != end_pos:
                    raise TypeError(
                        "In {0} {1}, found an element of the segments tuple which"
                        " isn't contigious with previous: {2} > {3}. End pos: {4}."
                        " Prev String: {5!r}".format(
                            text, type(self), prev_seg, elem, end_pos, prev_seg.raw
                        )
                    )
                start_pos = elem.get_start_pos_marker()
                end_pos = elem.get_end_pos_marker()
                prev_seg = elem
                if start_pos.advance_by(elem.raw) != end_pos:
                    raise TypeError(
                        "In {0} {1}, found an element of the segments tuple which"
                        " isn't self consistent: {2}".format(text, type(self), elem)
                    )

    def get_end_pos_marker(self):
        """Return the pos marker at the end of this segment."""
        return self.segments[-1].get_end_pos_marker()

    def get_start_pos_marker(self):
        """Return the pos marker at the start of this segment."""
        return self.segments[0].get_start_pos_marker()

    def stringify(self, ident=0, tabsize=4, code_only=False):
        """Use indentation to render this segment and it's children as a string."""
        buff = StringIO()
        preface = self._preface(ident=ident, tabsize=tabsize)
        buff.write(preface + "\n")
        if not code_only and self.comment_seperate and len(self._comments) > 0:
            if self._comments:
                buff.write((" " * ((ident + 1) * tabsize)) + "Comments:" + "\n")
                for seg in self._comments:
                    buff.write(
                        seg.stringify(
                            ident=ident + 2,
                            tabsize=tabsize,
                            code_only=code_only,
                        )
                    )
            if self._non_comments:
                buff.write((" " * ((ident + 1) * tabsize)) + "Code:" + "\n")
                for seg in self._non_comments:
                    buff.write(
                        seg.stringify(
                            ident=ident + 2,
                            tabsize=tabsize,
                            code_only=code_only,
                        )
                    )
        else:
            for seg in self.segments:
                # If we're in code_only, only show the code segments, otherwise always true
                if not code_only or seg.is_code:
                    buff.write(
                        seg.stringify(
                            ident=ident + 1,
                            tabsize=tabsize,
                            code_only=code_only,
                        )
                    )
        return buff.getvalue()

    def to_tuple(self, **kwargs):
        """Return a tuple structure from this segment.

        NB: If he segment is a meta segment, i.e. it's an indent or dedent,
        then it will never be returned from here!
        """
        # works for both base and raw
        code_only = kwargs.get("code_only", False)
        show_raw = kwargs.get("show_raw", False)

        if show_raw and not self.segments:
            result = (self.type, self.raw)
        elif code_only:
            result = (
                self.type,
                tuple(
                    seg.to_tuple(**kwargs)
                    for seg in self.segments
                    if seg.is_code and not seg.is_meta
                ),
            )
        else:
            result = (
                self.type,
                tuple(
                    seg.to_tuple(**kwargs) for seg in self.segments if not seg.is_meta
                ),
            )
        return result

    def as_record(self, **kwargs):
        """Return the segment as a structurally simplified record.

        This is useful for serialization to yaml or json.
        kwargs passed to to_tuple
        """
        return self.structural_simplify(self.to_tuple(**kwargs))

    def raw_list(self):
        """Return a list of raw elements, mostly for testing or searching."""
        buff = []
        for s in self.segments:
            buff += s.raw_list()
        return buff

    def iter_raw_seg(self):
        """Iterate raw segments, mostly for searching."""
        for s in self.segments:
            yield from s.iter_raw_seg()

    def iter_unparsables(self):
        """Iterate through any unparsables this segment may contain."""
        for s in self.segments:
            yield from s.iter_unparsables()

    def type_set(self):
        """Return a set of the types contained, mostly for testing."""
        typs = {self.type}
        for s in self.segments:
            typs |= s.type_set()
        return typs

    def is_raw(self):
        """Return True if this segment has no children."""
        return len(self.segments) == 0

    def get_child(self, *seg_type):
        """Retrieve the first of the children of this segment with matching type."""
        for seg in self.segments:
            if seg.is_type(*seg_type):
                return seg
        return None

    def get_children(self, *seg_type):
        """Retrieve the all of the children of this segment with matching type."""
        buff = []
        for seg in self.segments:
            if seg.is_type(*seg_type):
                buff.append(seg)
        return buff

    def recursive_crawl(self, *seg_type):
        """Recursively crawl for segments of a given type.

        Args:
            seg_type: :obj:`str`: one or more type of segment
                to look for.
        """
        # Check this segment
        if self.is_type(*seg_type):
            yield self
        # Recurse
        for seg in self.segments:
            yield from seg.recursive_crawl(*seg_type)

    def path_to(self, other):
        """Given a segment which is assumed within self, get the intermediate segments.

        Returns:
            :obj:`list` of segments, including the segment we're looking for.
            None if not found.

        """
        # Return self if we've found the segment.
        if self is other:
            return [self]

        # Are we in the right ballpark?
        if (
            not self.get_start_pos_marker()
            <= other.get_start_pos_marker()
            <= self.get_end_pos_marker()
        ):
            return None

        # Do we have any child segments at all?
        if not self.segments:
            return None

        # Check through each of the child segments
        for seg in self.segments:
            res = seg.path_to(other)
            if res:
                return [self] + res
        return None

    def parse(self, parse_context=None):
        """Use the parse grammar to find subsegments within this segment.

        A large chunk of the logic around this can be found in the `expand` method.

        Use the parse setting in the context for testing, mostly to check how deep to go.
        True/False for yes or no, an integer allows a certain number of levels.
        """
        # Clear the blacklist cache so avoid missteps
        if parse_context:
            parse_context.blacklist.clear()

        # the parse_depth and recurse kwargs control how deep we will recurse for testing.
        if not self.segments:
            # This means we're a root segment, just return an unmutated self
            return self

        # Check the Parse Grammar
        if self.parse_grammar is None:
            # No parse grammar, go straight to expansion
            parse_context.logger.debug(
                "{0}.parse: no grammar. Going straight to expansion".format(
                    self.__class__.__name__
                )
            )
        else:
            # For debugging purposes. Ensure that we don't have non-code elements
            # at the start or end of the segments. They should always in the middle,
            # or in the parent expression.
            segments = self.segments
            if self.can_start_end_non_code:
                pre_nc, segments, post_nc = trim_non_code(segments)
            else:
                pre_nc = ()
                post_nc = ()
                if (not segments[0].is_code) and (not segments[0].is_meta):
                    raise ValueError(
                        "Segment {0} starts with non code segment: {1!r}.\n{2!r}".format(
                            self, segments[0].raw, segments
                        )
                    )
                if (not segments[-1].is_code) and (not segments[-1].is_meta):
                    raise ValueError(
                        "Segment {0} ends with non code segment: {1!r}.\n{2!r}".format(
                            self, segments[-1].raw, segments
                        )
                    )

            # NOTE: No match_depth kwarg, because this is the start of the matching.
            with parse_context.matching_segment(self.__class__.__name__) as ctx:
                m = self.parse_grammar.match(segments=segments, parse_context=ctx)

            if not isinstance(m, MatchResult):
                raise TypeError(
                    "[PD:{0}] {1}.match. Result is {2}, not a MatchResult!".format(
                        parse_context.parse_depth, self.__class__.__name__, type(m)
                    )
                )

            # Basic Validation, that we haven't dropped anything.
            check_still_complete(segments, m.matched_segments, m.unmatched_segments)

            if m.has_match():
                if m.is_complete():
                    # Complete match, happy days!
                    self.segments = pre_nc + m.matched_segments + post_nc
                else:
                    # Incomplete match.
                    # For now this means the parsing has failed. Lets add the unmatched bit at the
                    # end as something unparsable.
                    # TODO: Do something more intelligent here.
                    self.segments = (
                        pre_nc
                        + m.matched_segments
                        + (
                            UnparsableSegment(
                                segments=m.unmatched_segments + post_nc,
                                expected="Nothing...",
                            ),
                        )
                    )
            elif self.allow_empty and not segments:
                # Very edge case, but some segments are allowed to be empty other than non-code
                self.segments = pre_nc + post_nc
            else:
                # If there's no match at this stage, then it's unparsable. That's
                # a problem at this stage so wrap it in an unparable segment and carry on.
                self.segments = (
                    pre_nc
                    + (
                        UnparsableSegment(
                            segments=segments,
                            expected=self.type,
                        ),  # NB: tuple
                    )
                    + post_nc
                )

            # Validate new segments
            self.validate_segments(text="parsing")

        bencher = BenchIt()  # starts the timer
        bencher("Parse complete of {0!r}".format(self.__class__.__name__))

        # Recurse if allowed (using the expand method to deal with the expansion)
        parse_context.logger.debug(
            "{0}.parse: Done Parse. Plotting Recursion. Recurse={1!r}".format(
                self.__class__.__name__, parse_context.recurse
            )
        )
        parse_depth_msg = "###\n#\n# Beginning Parse Depth {0}: {1}\n#\n###\nInitial Structure:\n{2}".format(
            parse_context.parse_depth + 1, self.__class__.__name__, self.stringify()
        )
        if parse_context.may_recurse():
            parse_context.logger.debug(parse_depth_msg)
            with parse_context.deeper_parse() as ctx:
                self.segments = self.expand(self.segments, parse_context=ctx)
        # Validate new segments
        self.validate_segments(text="expanding")

        return self

    def apply_fixes(self, fixes):
        """Apply an iterable of fixes to this segment.

        Used in applying fixes if we're fixing linting errors.
        If anything changes, this should return a new version of the segment
        rather than mutating the original.

        Note: We need to have fixes to apply AND this must have children. In the case
        of raw segments, they will be replaced or removed by their parent and
        so this function should just return self.
        """
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
                    # We don't apply fixes to meta segments
                    if seg.is_meta:
                        seg_buffer.append(seg)
                        continue

                    fix_buff = fixes.copy()
                    unused_fixes = []
                    while fix_buff:
                        f = fix_buff.pop()
                        if f.anchor == seg:
                            if f.edit_type == "delete":
                                # We're just getting rid of this segment.
                                seg = None
                            elif f.edit_type in ("edit", "create"):
                                # We're doing a replacement (it could be a single segment or an iterable)
                                if isinstance(f.edit, BaseSegment):
                                    seg_buffer.append(f.edit)
                                else:
                                    for s in f.edit:
                                        seg_buffer.append(s)

                                if f.edit_type == "create":
                                    # in the case of a creation, also add this segment on the end
                                    seg_buffer.append(seg)
                            else:
                                raise ValueError(
                                    "Unexpected edit_type: {0!r} in {1!r}".format(
                                        f.edit_type, f
                                    )
                                )
                            # We've applied a fix here. Move on, this also consumes the fix
                            # TODO: Maybe deal with overlapping fixes later.
                            break
                        else:
                            # We've not used the fix so we should keep it in the list for later.
                            unused_fixes.append(f)
                    else:
                        seg_buffer.append(seg)
                # Switch over the the unused list
                fixes = unused_fixes + fix_buff

            # Then recurse (i.e. deal with the children) (Requeueing)
            seg_queue = seg_buffer
            seg_buffer = []
            for seg in seg_queue:
                s, fixes = seg.apply_fixes(fixes)
                seg_buffer.append(s)

            # Reform into a new segment
            r = r.__class__(
                segments=tuple(seg_buffer), pos_marker=r.pos_marker, validate=False
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
                new_pos = seg.pos_marker.shift_to(running_pos)
                if seg.is_meta:
                    # It's a meta segment, just update the position
                    seg = seg.__class__(pos_marker=new_pos)
                elif len(seg.segments) > 0:
                    # It's a compound segment, so keep track of it's children
                    child_segs = seg.segments
                    # Create a new segment of the same type with the new position
                    seg = seg.__class__(segments=child_segs, pos_marker=new_pos)
                    # Realign the children of that class
                    seg = seg.realign()
                else:
                    # It's a raw segment...
                    # Create a new segment of the same type with the new position
                    seg = seg.__class__(raw=seg.raw, pos_marker=new_pos)
                # Update the running position with the content of that segment
                running_pos = running_pos.advance_by(raw=seg.raw, idx=idx)
                # Add the buffer to my new segment
                seg_buffer.append(seg)

        # Create a new version of this class with the new details
        return self.__class__(segments=tuple(seg_buffer), pos_marker=self.pos_marker)


class UnparsableSegment(BaseSegment):
    """This is a segment which can't be parsed. It indicates a error during parsing."""

    type = "unparsable"
    # From here down, comments are printed seperately.
    comment_seperate = True
    _expected = ""

    def __init__(self, *args, expected="", **kwargs):
        self._expected = expected
        super().__init__(*args, **kwargs)

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
