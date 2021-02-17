"""Base segment definitions.

Here we define:
- BaseSegment. This is the root class for all segments, and is
  designed to hold other subsegments.
- UnparsableSegment. A special wrapper to indicate that the parse
  function failed on this block of segments and to prevent further
  analysis.
"""

from io import StringIO
import copy
from benchit import BenchIt
from cached_property import cached_property
from typing import Any, Callable, Optional, List, Tuple, NamedTuple, Iterator
import logging

from sqlfluff.core.string_helpers import (
    frame_msg,
    curtail_string,
)

from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_logging import parse_match_logging
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.helpers import (
    check_still_complete,
    trim_non_code_segments,
)
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.markers import EnrichedFilePositionMarker
from sqlfluff.core.parser.context import ParseContext

# Instantiate the linter logger (only for use in methods involved with fixing.)
linter_logger = logging.getLogger("sqlfluff.linter")


class FixPatch(NamedTuple):
    """An edit patch for a templated file."""

    templated_slice: slice
    fixed_raw: str
    # The patch type, functions mostly for debugging and explanation
    # than for function. It allows traceability of *why* this patch was
    # generated.
    patch_type: str


class BaseSegment:
    """The base segment element.

    This defines the base element which drives both Lexing, Parsing and Linting.
    A large chunk of the logic which defines those three operations are centered
    here. Much of what is defined in the BaseSegment is also used by its many
    subclasses rather than directly here.

    For clarity, the `BaseSegment` is mostly centered around a segment which contains
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
                # Find the first segment with an enriched position marker
                first_enriched = next(
                    (
                        seg.pos_marker
                        for seg in segments
                        if isinstance(seg.pos_marker, EnrichedFilePositionMarker)
                    ),
                    # Default to the first un-enriched segment
                    segments[0].pos_marker,
                )
                self.pos_marker = first_enriched.combine(
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
            # Same class NAME. (could be constructed elsewhere)
            self.__class__.__name__ == other.__class__.__name__
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
        might want to override the name rather than just getting it
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
        need expanding, maybe one of its children does.

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

    @cached_property
    def is_code(self):
        """Return True if this segment contains any code."""
        return any(seg.is_code for seg in self.segments)

    @cached_property
    def is_comment(self):
        """Return True if this is entirely made of comments."""
        return all(seg.is_comment for seg in self.segments)

    @cached_property
    def raw(self):
        """Make a string from the segments of this segment."""
        return self._reconstruct()

    @cached_property
    def raw_upper(self):
        """Make an uppercase string from the segments of this segment."""
        return self._reconstruct().upper()

    @cached_property
    def matched_length(self):
        """Return the length of the segment in characters."""
        return sum(seg.matched_length for seg in self.segments)

    # ################ STATIC METHODS

    @staticmethod
    def segs_to_tuple(segs, **kwargs):
        """Return a tuple structure from an iterable of segments."""
        return tuple(seg.to_tuple(**kwargs) for seg in segs)

    @staticmethod
    def _suffix():
        """Return any extra output required at the end when logging.

        NB Override this for specific subclasses if we want extra output.
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

    @staticmethod
    def _realign_segments(segments, starting_pos=None, meta_only=False):
        """Realign the positions in the provided segments."""
        seg_buffer = []
        todo_buffer = list(segments)
        if not todo_buffer:
            return ()
        # If starting pos not provided, take it from the first of the buffer.
        running_pos = starting_pos
        if not running_pos:
            for seg in todo_buffer:
                if not seg.is_meta:
                    running_pos = seg.pos_marker
                    break
            else:
                raise ValueError("No starting pos provided and unable to infer.")

        # Strip the starting position regardless. This means
        # we don't accidentally contaminate any inserted initial
        # segments.
        running_pos = running_pos.strip()

        while len(todo_buffer) > 0:
            # Get the first off the buffer
            seg = todo_buffer.pop(0)

            # We'll preserve statement indexes so we should keep track of that.
            # When recreating, we use the DELTA of the index so that's what matter...
            idx = seg.pos_marker.statement_index - running_pos.statement_index
            new_pos = seg.pos_marker.shift_to(running_pos)

            if not meta_only or seg.is_meta:
                # Copy the segment
                seg_copy = copy.copy(seg)
                # Update the position
                seg_copy.pos_marker = new_pos
                # Realign the children of that class if required.
                if len(seg_copy.segments) > 0:
                    seg_copy = seg_copy.realign()
                seg = seg_copy

            # Update the running position with the content of that segment.
            running_pos = running_pos.advance_by(raw=seg.raw, idx=idx)
            # Add the buffer to my new segment
            seg_buffer.append(seg)
        return tuple(seg_buffer)

    # ################ CLASS METHODS

    @classmethod
    def simple(cls, parse_context: ParseContext) -> Optional[List[str]]:
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
            return None

    @classmethod
    def is_optional(cls):
        """Return True if this segment is optional.

        This is used primarily in sequence matching, where optional
        segments can be skipped.
        """
        return cls.optional

    @classmethod
    def is_type(cls, *seg_type):
        """Is this segment (or its parent) of the given type."""
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
                    # No, we can use a mapping tuple
                    elem = {e[0]: cls.structural_simplify(e[1]) for e in elem}
                else:
                    # Yes, this has to be a list :(
                    elem = [cls.structural_simplify(e) for e in elem]
        return elem

    @classmethod
    @match_wrapper(v_level=4)
    def match(
        cls, segments: Tuple["BaseSegment", ...], parse_context: ParseContext
    ) -> MatchResult:
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

    def invalidate_caches(self):
        """Invalidate the cached properties.

        This should be called whenever the segments within this
        segment is mutated.
        """
        for key in ["is_code", "is_comment", "raw", "raw_upper", "matched_length"]:
            self.__dict__.pop(key, None)

    def validate_segments(self, text="constructing", validate=True):
        """Validate the current set of segments.

        Check the elements of the `segments` attribute are all
        themselves segments, and that the positions match up.

        `validate` confirms whether we should check contiguousness.
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
                        " isn't contiguous with previous: {2} > {3}. End pos: {4}."
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
        """Use indentation to render this segment and its children as a string."""
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

    def iter_segments(self, expanding=None, pass_through=False):
        """Iterate raw segments, optionally expanding some chldren."""
        for s in self.segments:
            if expanding and s.is_type(*expanding):
                yield from s.iter_segments(
                    expanding=expanding if pass_through else None
                )
            else:
                yield s

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

    def select_children(
        self,
        start_seg: Optional["BaseSegment"] = None,
        stop_seg: Optional["BaseSegment"] = None,
        select_if: Optional[Callable[["BaseSegment"], Any]] = None,
        loop_while: Optional[Callable[["BaseSegment"], Any]] = None,
    ):
        """Retrieve subset of children based on range and filters.

        Often useful by linter rules when generating fixes, e.g. to find
        whitespace segments between two already known segments.
        """
        start_index = self.segments.index(start_seg) if start_seg else -1
        stop_index = self.segments.index(stop_seg) if stop_seg else len(self.segments)
        buff = []
        for seg in self.segments[start_index + 1 : stop_index]:
            if loop_while and not loop_while(seg):
                break
            if not select_if or select_if(seg):
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
                pre_nc, segments, post_nc = trim_non_code_segments(segments)
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
                # a problem at this stage so wrap it in an unparsable segment and carry on.
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

                    fix_buff = fixes.copy()
                    unused_fixes = []
                    while fix_buff:
                        f = fix_buff.pop()
                        if f.anchor == seg:
                            linter_logger.debug(
                                "Matched fix against segment: %s -> %s", f, seg
                            )
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
                # Invalidate any caches
                self.invalidate_caches()

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

        This function will align the pos marker if its direct children, we then
        recurse to realign their children.

        """
        # Create a new version of this class with the new details
        return self.__class__(
            segments=self._realign_segments(self.segments, self.pos_marker),
            pos_marker=self.pos_marker,
        )

    def iter_patches(self, templated_str: str) -> Iterator[FixPatch]:
        """Iterate through the segments generating fix patches.

        The patches are generated in TEMPLATED space. This is important
        so that we defer dealing with any loops until later. At this stage
        everything *should* happen in templated order.

        Occasionally we have an insertion around a placeholder, so we also
        return a hint to deal with that.
        """
        # Does it match? If so we can ignore it.
        matches = self.raw == templated_str[self.pos_marker.templated_slice]
        if matches:
            return

        # If we're here, the segment doesn't match the original.

        # If it's all literal, then we don't need to recurse.
        if self.pos_marker.is_literal:
            # Yield the position in the source file and the patch
            yield FixPatch(
                self.pos_marker.templated_slice, self.raw, patch_type="literal"
            )
        # Can we go deeper?
        elif not self.segments:
            # It's not literal, but it's also a raw segment. If were going
            # to yield a change, we would have done it from the parent, so
            # we just abort from here.
            return
        else:
            # This segment isn't a literal, but has changed, we need to go deeper.

            # Iterate through the child segments
            templated_idx = self.pos_marker.templated_slice.start
            insert_buff = ""
            for seg_idx, segment in enumerate(self.segments):

                # First check for insertions.
                # We know it is new if the position marker is NOT ENRICHED.
                if not isinstance(segment.pos_marker, EnrichedFilePositionMarker):
                    # Add it to the insertion buffer if it has length:
                    if segment.raw:
                        insert_buff += segment.raw
                        linter_logger.debug(
                            "Appending insertion buffer. %r @idx: %s",
                            insert_buff,
                            templated_idx,
                        )
                    continue

                # If we get here, then we know it's an original.
                # Check for deletions at the before this segment (vs the TEMPLATED).
                start_diff = segment.pos_marker.templated_slice.start - templated_idx

                # Check to see whether there's a discontinuity before the current segment
                if start_diff > 0 or insert_buff:
                    # If we have an insert buffer, then it's an edit, otherwise a deletion.
                    yield FixPatch(
                        slice(
                            segment.pos_marker.templated_slice.start
                            - max(start_diff, 0),
                            segment.pos_marker.templated_slice.start,
                        ),
                        insert_buff,
                        patch_type="mid_point",
                    )
                    insert_buff = ""

                # Now we deal with any changes *within* the segment itself.
                yield from segment.iter_patches(templated_str=templated_str)

                # Once we've dealt with any patches from the segment, update
                # our position markers.
                templated_idx = segment.pos_marker.templated_slice.stop

            # After the loop, we check whether there's a trailing deletion
            # or insert. Also valid if we still have an insertion buffer here.
            end_diff = self.pos_marker.templated_slice.stop - templated_idx
            if end_diff or insert_buff:
                yield FixPatch(
                    slice(
                        self.pos_marker.templated_slice.stop - end_diff,
                        self.pos_marker.templated_slice.stop,
                    ),
                    insert_buff,
                    patch_type="end_point",
                )


class UnparsableSegment(BaseSegment):
    """This is a segment which can't be parsed. It indicates a error during parsing."""

    type = "unparsable"
    # From here down, comments are printed separately.
    comment_seperate = True
    _expected = ""

    def __init__(self, *args, expected="", **kwargs):
        self._expected = expected
        super().__init__(*args, **kwargs)

    def _suffix(self):
        """Return any extra output required at the end when logging.

        NB Override this for specific subclasses if we want extra output.
        """
        return "!! Expected: {0!r}".format(self._expected)

    def iter_unparsables(self):
        """Iterate through any unparsables.

        As this is an unparsable, it should yield itself.
        """
        yield self
