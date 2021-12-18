"""Base segment definitions.

Here we define:
- BaseSegment. This is the root class for all segments, and is
  designed to hold other subsegments.
- UnparsableSegment. A special wrapper to indicate that the parse
  function failed on this block of segments and to prevent further
  analysis.
"""

from io import StringIO
from cached_property import cached_property
from typing import Any, Callable, Optional, List, Tuple, NamedTuple, Iterator
import logging

from tqdm import tqdm

from sqlfluff.core.config import progress_bar_configuration
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
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.context import ParseContext

# Instantiate the linter logger (only for use in methods involved with fixing.)
linter_logger = logging.getLogger("sqlfluff.linter")


class FixPatch(NamedTuple):
    """An edit patch for a templated file."""

    templated_slice: slice
    fixed_raw: str
    # The patch category, functions mostly for debugging and explanation
    # than for function. It allows traceability of *why* this patch was
    # generated. It has no siginificance for processing.
    patch_category: str


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
    # We define the type here but no value. Subclasses must provide a value.
    match_grammar: Matchable
    comment_separate = False
    optional = False  # NB: See the sequence grammar for details
    _name: Optional[str] = None
    is_meta = False
    # Are we able to have non-code at the start or end?
    can_start_end_non_code = False
    # Can we allow it to be empty? Usually used in combination
    # with the can_start_end_non_code.
    allow_empty = False
    # What other kwargs need to be copied when applying fixes.
    additional_kwargs: List[str] = []

    def __init__(
        self,
        segments,
        pos_marker=None,
        name: Optional[str] = None,
    ):
        # A cache variable for expandable
        self._is_expandable = None
        # Surrogate name option.
        self._surrogate_name = name

        if len(segments) == 0:  # pragma: no cover
            raise RuntimeError(
                "Setting {} with a zero length segment set. This shouldn't happen.".format(
                    self.__class__
                )
            )

        if hasattr(segments, "matched_segments"):  # pragma: no cover TODO?
            # Safely extract segments from a match
            self.segments = segments.matched_segments
        elif isinstance(segments, tuple):
            self.segments = segments
        elif isinstance(segments, list):
            self.segments = tuple(segments)
        else:  # pragma: no cover
            raise TypeError(f"Unexpected type passed to BaseSegment: {type(segments)}")

        if not pos_marker:
            # If no pos given, it's the pos of the first segment.
            if isinstance(segments, (tuple, list)):
                pos_marker = PositionMarker.from_child_markers(
                    *(seg.pos_marker for seg in segments)
                )
            else:  # pragma: no cover
                raise TypeError(
                    f"Unexpected type passed to BaseSegment: {type(segments)}"
                )
        self.pos_marker: PositionMarker = pos_marker

        self._recalculate_caches()

    def __setattr__(self, key, value):

        try:
            if key == "segments":
                self._recalculate_caches()

        except (AttributeError, KeyError):  # pragma: no cover
            pass

        super().__setattr__(key, value)

    def __eq__(self, other):
        # NB: this should also work for RawSegment
        return (
            # Same class NAME. (could be constructed elsewhere)
            self.__class__.__name__ == other.__class__.__name__
            and (self.raw == other.raw)
            # Both must have a non-null position marker to compare.
            and self.pos_marker
            and other.pos_marker
            # We only match that the *start* is the same. This means we can
            # still effectively construct searches look for segments.
            # This is important for .apply_fixes().
            and (
                self.pos_marker.start_point_marker()
                == other.pos_marker.start_point_marker()
            )
        )

    def __hash__(self):
        return hash(
            (self.__class__.__name__, self.raw, self.pos_marker.source_position())
        )

    def __repr__(self):
        return f"<{self.__class__.__name__}: ({self.pos_marker})>"

    # ################ PRIVATE PROPERTIES

    @property
    def _comments(self):
        """Returns only the comment elements of this segment."""
        return [seg for seg in self.segments if seg.is_type("comment")]

    @property
    def _non_comments(self):  # pragma: no cover TODO?
        """Returns only the non-comment elements of this segment."""
        return [seg for seg in self.segments if not seg.is_type("comment")]

    # ################ PUBLIC PROPERTIES

    @property
    def name(self):
        """The name of this segment.

        The reason for three routes for names is that some subclasses
        might want to override the name rather than just getting
        the class name. Instances may also override this with the
        _surrogate_name.

        Name should be specific to this kind of segment, while `type`
        should be a higher level descriptor of the kind of segment.
        For example, the name of `+` is 'plus' but the type might be
        'binary_operator'.
        """
        return self._surrogate_name or self._name or self.__class__.__name__

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
    def is_comment(self):  # pragma: no cover TODO?
        """Return True if this is entirely made of comments."""
        return all(seg.is_comment for seg in self.segments)

    @cached_property
    def is_whitespace(self):
        """Return True if this segment is entirely whitespace."""
        return all(seg.is_whitespace for seg in self.segments)

    @cached_property
    def raw(self):
        """Make a string from the segments of this segment."""
        return "".join(seg.raw for seg in self.segments)

    @cached_property
    def raw_upper(self):
        """Make an uppercase string from the segments of this segment."""
        return self.raw.upper()

    @cached_property
    def matched_length(self):
        """Return the length of the segment in characters."""
        return sum(seg.matched_length for seg in self.segments)

    @cached_property
    def raw_segments(self):
        """Returns a list of raw segments in this segment."""
        return self.get_raw_segments()

    @cached_property
    def raw_segments_upper(self):
        """Returns the first non-whitespace subsegment of this segment."""
        for seg in self.raw_segments:
            if seg.raw_upper.strip():
                return seg.raw_upper
        return None
        # return [seg.raw_upper for seg in self.raw_segments]

    # ################ STATIC METHODS

    @staticmethod
    def segs_to_tuple(segs, **kwargs):  # pragma: no cover TODO?
        """Return a tuple structure from an iterable of segments."""
        return tuple(seg.to_tuple(**kwargs) for seg in segs)

    @staticmethod
    def _suffix():
        """Return any extra output required at the end when logging.

        NB Override this for specific subclasses if we want extra output.
        """
        return ""

    @classmethod
    def expand(cls, segments, parse_context):
        """Expand the list of child segments using their `parse` methods."""
        segs = ()

        # Renders progress bar only for `BaseFileSegments`.
        disable_progress_bar = (
            not issubclass(cls, BaseFileSegment)
            or progress_bar_configuration.disable_progress_bar
        )

        progressbar_segments = tqdm(
            segments,
            desc="parsing",
            miniters=30,
            leave=False,
            disable=disable_progress_bar,
        )

        for stmt in progressbar_segments:
            try:
                if not stmt.is_expandable:
                    parse_context.logger.info(
                        "[PD:%s] Skipping expansion of %s...",
                        parse_context.parse_depth,
                        stmt,
                    )
                    segs += (stmt,)
                    continue
            except Exception as err:  # pragma: no cover
                parse_context.logger.error(
                    "%s has no attribute `is_expandable`. This segment appears poorly constructed.",
                    stmt,
                )
                raise err
            if not hasattr(stmt, "parse"):  # pragma: no cover
                raise ValueError(
                    "{} has no method `parse`. This segment appears poorly constructed.".format(
                        stmt
                    )
                )
            parse_depth_msg = "Parse Depth {}. Expanding: {}: {!r}".format(
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

    @classmethod
    def _position_segments(cls, segments, parent_pos=None):
        """Refresh positions of segments within a span.

        This does two things:
        - Assign positions to any segments without them.
        - Updates the working line_no and line_pos for all
          segments during fixing.

        New segments are assumed to be metas or insertions
        and so therefore have a zero-length position in the
        source and templated file.
        """
        # If there are no segments, there's no need to reposition.
        if not segments:
            return segments

        # Work out our starting position for working through
        if parent_pos:
            line_no = parent_pos.working_line_no
            line_pos = parent_pos.working_line_pos
        # If we don't have it, infer it from the first position
        # in this segment that does have a position.
        else:
            for fwd_seg in segments:
                if fwd_seg.pos_marker:
                    line_no = fwd_seg.pos_marker.working_line_no
                    line_pos = fwd_seg.pos_marker.working_line_pos
                    break
            else:  # pragma: no cover
                linter_logger.warning("SEG: %r, POS: %r", segments, parent_pos)
                raise ValueError("Unable to find working position.")

        # Use the index so that we can look forward
        # and backward.
        for idx, segment in enumerate(segments):
            # Fill any that don't have a position.
            if not segment.pos_marker:
                # Can we get a position from the previous?
                if idx > 0:
                    segment.pos_marker = segments[idx - 1].pos_marker.end_point_marker()
                # Can we get it from the parent?
                elif parent_pos:
                    segment.pos_marker = parent_pos.start_point_marker()
                # Search forward for a following one, if we have to?
                else:
                    for fwd_seg in segments[idx + 1 :]:
                        if fwd_seg.pos_marker:
                            segments[
                                idx
                            ].pos_marker = fwd_seg.pos_marker.start_point_marker()
                            break
                    else:  # pragma: no cover
                        raise ValueError("Unable to position new segment")

            # Update the working position.
            segment.pos_marker = segment.pos_marker.with_working_position(
                line_no,
                line_pos,
            )
            line_no, line_pos = segment.pos_marker.infer_next_position(
                segment.raw, line_no, line_pos
            )

            # If this segment has children, recurse and reposition them too.
            if segment.segments:
                segment.segments = cls._position_segments(
                    segment.segments, parent_pos=segment.pos_marker
                )

        return segments

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
        else:  # pragma: no cover TODO?
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
    def class_is_type(cls, *seg_type):
        """Is this segment class (or its parent) of the given type."""
        # Do we match on the type of _this_ class.
        if cls.type in seg_type:
            return True
        # If not, check types of parents.
        for base_class in cls.__bases__:
            if base_class is object:
                break
            elif base_class.type in seg_type:
                return True
            elif base_class.type == "base":
                break
        return False

    @classmethod
    def structural_simplify(cls, elem):
        """Simplify the structure recursively so it serializes nicely in json/yaml."""
        if len(elem) == 0:
            return None
        elif isinstance(elem, tuple):
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
            if not isinstance(m, MatchResult):  # pragma: no cover
                raise TypeError(
                    "[PD:{} MD:{}] {}.match. Result is {}, not a MatchResult!".format(
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
        else:  # pragma: no cover
            raise NotImplementedError(
                f"{cls.__name__} has no match function implemented"
            )

    # ################ PRIVATE INSTANCE METHODS

    def _recalculate_caches(self):

        for key in [
            "is_code",
            "is_comment",
            "is_whitespace",
            "raw",
            "raw_upper",
            "matched_length",
            "raw_segments",
            "raw_segments_upper",
        ]:
            self.__dict__.pop(key, None)

    def _preface(self, ident, tabsize):
        """Returns the preamble to any logging."""
        padded_type = "{padding}{modifier}{type}".format(
            padding=" " * (ident * tabsize),
            modifier="[META] " if self.is_meta else "",
            type=self.get_type() + ":",
        )
        preface = "{pos:20}|{padded_type:60}  {suffix}".format(
            pos=str(self.pos_marker) if self.pos_marker else "-",
            padded_type=padded_type,
            suffix=self._suffix() or "",
        )
        # Trim unnecessary whitespace before returning
        return preface.rstrip()

    # ################ PUBLIC INSTANCE METHODS

    def get_type(self):
        """Returns the type of this segment as a string."""
        return self.type

    def is_type(self, *seg_type):
        """Is this segment (or its parent) of the given type."""
        return self.class_is_type(*seg_type)

    def invalidate_caches(self):
        """Invalidate the cached properties.

        This should be called whenever the segments within this
        segment is mutated.
        """
        for seg in self.segments:
            seg.invalidate_caches()

        self._recalculate_caches()

    def get_start_point_marker(self):
        """Get a point marker at the start of this segment."""
        return self.pos_marker.start_point_marker()

    def get_end_point_marker(self):
        """Get a point marker at the end of this segment."""
        return self.pos_marker.end_point_marker()

    def get_start_loc(self):
        """Get a location tuple at the start of this segment."""
        return self.pos_marker.working_loc

    def get_end_loc(self):
        """Get a location tuple at the end of this segment."""
        return self.pos_marker.working_loc_after(
            self.raw,
        )

    def stringify(self, ident=0, tabsize=4, code_only=False):
        """Use indentation to render this segment and its children as a string."""
        buff = StringIO()
        preface = self._preface(ident=ident, tabsize=tabsize)
        buff.write(preface + "\n")
        if not code_only and self.comment_separate and len(self._comments) > 0:
            if self._comments:  # pragma: no cover TODO?
                buff.write((" " * ((ident + 1) * tabsize)) + "Comments:" + "\n")
                for seg in self._comments:
                    buff.write(
                        seg.stringify(
                            ident=ident + 2,
                            tabsize=tabsize,
                            code_only=code_only,
                        )
                    )
            if self._non_comments:  # pragma: no cover TODO?
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

    def to_tuple(self, code_only=False, show_raw=False, include_meta=False):
        """Return a tuple structure from this segment."""
        # works for both base and raw

        if show_raw and not self.segments:
            result = (self.get_type(), self.raw)
        elif code_only:
            result = (
                self.get_type(),
                tuple(
                    seg.to_tuple(
                        code_only=code_only,
                        show_raw=show_raw,
                        include_meta=include_meta,
                    )
                    for seg in self.segments
                    if seg.is_code and not seg.is_meta
                ),
            )
        else:
            result = (
                self.get_type(),
                tuple(
                    seg.to_tuple(
                        code_only=code_only,
                        show_raw=show_raw,
                        include_meta=include_meta,
                    )
                    for seg in self.segments
                    if include_meta or not seg.is_meta
                ),
            )
        return result

    def as_record(self, **kwargs):
        """Return the segment as a structurally simplified record.

        This is useful for serialization to yaml or json.
        kwargs passed to to_tuple
        """
        return self.structural_simplify(self.to_tuple(**kwargs))

    def raw_list(self):  # pragma: no cover TODO?
        """Return a list of raw elements, mostly for testing or searching."""
        buff = []
        for s in self.segments:
            buff += s.raw_list()
        return buff

    def get_raw_segments(self):
        """Iterate raw segments, mostly for searching."""
        return [item for s in self.segments for item in s.raw_segments]

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

    def recursive_crawl(self, *seg_type, recurse_into=True):
        """Recursively crawl for segments of a given type.

        Args:
            seg_type: :obj:`str`: one or more type of segment
                to look for.
            recurse_into: :obj:`bool`: When an element of type "seg_type" is
                found, whether to recurse into it.
        """
        # Check this segment
        if self.is_type(*seg_type):
            match = True
            yield self
        else:
            match = False
        if recurse_into or not match:
            # Recurse
            for seg in self.segments:
                yield from seg.recursive_crawl(*seg_type, recurse_into=recurse_into)

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
        # NB: Comparisons have a higher precedence than `not`.
        if not self.get_start_loc() <= other.get_start_loc() <= self.get_end_loc():
            return None

        # Do we have any child segments at all?
        if not self.segments:
            return None

        # Check through each of the child segments
        for seg in self.segments:
            res = seg.path_to(other)
            if res:
                return [self] + res
        return None  # pragma: no cover

    def parse(
        self,
        parse_context: ParseContext,
        parse_grammar: Optional[Matchable] = None,
    ) -> "BaseSegment":
        """Use the parse grammar to find subsegments within this segment.

        A large chunk of the logic around this can be found in the `expand` method.

        Use the parse setting in the context for testing, mostly to check how deep to go.
        True/False for yes or no, an integer allows a certain number of levels.

        Optionally, this method allows a custom parse grammar to be
        provided which will override any existing parse grammar
        on the segment.
        """
        # Clear the denylist cache so avoid missteps
        if parse_context:
            parse_context.denylist.clear()

        # the parse_depth and recurse kwargs control how deep we will recurse for testing.
        if not self.segments:  # pragma: no cover TODO?
            # This means we're a root segment, just return an unmutated self
            return self

        # Check the Parse Grammar
        parse_grammar = parse_grammar or self.parse_grammar
        if parse_grammar is None:
            # No parse grammar, go straight to expansion
            parse_context.logger.debug(
                "{}.parse: no grammar. Going straight to expansion".format(
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
                if (not segments[0].is_code) and (
                    not segments[0].is_meta
                ):  # pragma: no cover
                    raise ValueError(
                        "Segment {} starts with non code segment: {!r}.\n{!r}".format(
                            self, segments[0].raw, segments
                        )
                    )
                if (not segments[-1].is_code) and (
                    not segments[-1].is_meta
                ):  # pragma: no cover
                    raise ValueError(
                        "Segment {} ends with non code segment: {!r}.\n{!r}".format(
                            self, segments[-1].raw, segments
                        )
                    )

            # NOTE: No match_depth kwarg, because this is the start of the matching.
            with parse_context.matching_segment(self.__class__.__name__) as ctx:
                m = parse_grammar.match(segments=segments, parse_context=ctx)

            if not isinstance(m, MatchResult):  # pragma: no cover
                raise TypeError(
                    "[PD:{}] {}.match. Result is {}, not a MatchResult!".format(
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
                            expected=self.name,
                        ),  # NB: tuple
                    )
                    + post_nc
                )
        # Recurse if allowed (using the expand method to deal with the expansion)
        parse_context.logger.debug(
            "{}.parse: Done Parse. Plotting Recursion. Recurse={!r}".format(
                self.__class__.__name__, parse_context.recurse
            )
        )
        parse_depth_msg = "###\n#\n# Beginning Parse Depth {}: {}\n#\n###\nInitial Structure:\n{}".format(
            parse_context.parse_depth + 1, self.__class__.__name__, self.stringify()
        )
        if parse_context.may_recurse():
            parse_context.logger.debug(parse_depth_msg)
            with parse_context.deeper_parse() as ctx:
                self.segments = self.expand(
                    self.segments,
                    parse_context=ctx,
                )

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
                        # Look for identity not just equality.
                        # This handles potential positioning ambiguity.
                        if f.anchor is seg:
                            linter_logger.debug(
                                "Matched fix against segment: %s -> %s", f, seg
                            )
                            if f.edit_type == "delete":
                                # We're just getting rid of this segment.
                                seg = None
                            elif f.edit_type in (
                                "replace",
                                "create_before",
                                "create_after",
                            ):
                                if f.edit_type == "create_after":
                                    # in the case of a creation after, also add this segment before the edit.
                                    seg_buffer.append(seg)

                                # We're doing a replacement (it could be a single segment or an iterable)
                                if isinstance(f.edit, BaseSegment):
                                    seg_buffer.append(f.edit)  # pragma: no cover TODO?
                                else:
                                    for s in f.edit:
                                        seg_buffer.append(s)

                                if f.edit_type == "create_before":
                                    # in the case of a creation before, also add this segment on the end
                                    seg_buffer.append(seg)

                            else:  # pragma: no cover
                                raise ValueError(
                                    "Unexpected edit_type: {!r} in {!r}".format(
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
                # Realign the segments within
                segments=self._position_segments(
                    tuple(seg_buffer), parent_pos=r.pos_marker
                ),
                pos_marker=r.pos_marker,
                # Pass through any additional kwargs
                **{k: getattr(self, k) for k in self.additional_kwargs},
            )
            # Return the new segment with any unused fixes.
            return r, fixes
        else:
            return self, fixes

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
        linter_logger.debug(
            "%s at %s: Original: [%r] Fixed: [%r]",
            type(self).__name__,
            self.pos_marker.templated_slice,
            templated_str[self.pos_marker.templated_slice],
            self.raw,
        )

        # If it's all literal, then we don't need to recurse.
        if self.pos_marker.is_literal():
            # Yield the position in the source file and the patch
            yield FixPatch(
                self.pos_marker.templated_slice, self.raw, patch_category="literal"
            )
        # Can we go deeper?
        elif not self.segments:
            # It's not literal, but it's also a raw segment. If we're going
            # to yield a change, we would have done it from the parent, so
            # we just abort from here.
            return  # pragma: no cover TODO?
        else:
            # This segment isn't a literal, but has changed, we need to go deeper.

            # Iterate through the child segments
            templated_idx = self.pos_marker.templated_slice.start
            insert_buff = ""
            for seg_idx, segment in enumerate(self.segments):

                # First check for insertions.
                # We know it's an insertion if it has length but not in the templated file.
                if segment.raw and segment.pos_marker.is_point():
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
                # Check for deletions at the point before this segment (vs the TEMPLATED).
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
                        patch_category="mid_point",
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
                    patch_category="end_point",
                )

    def edit(self, raw):
        """Stub."""
        raise NotImplementedError()


class BracketedSegment(BaseSegment):
    """A segment containing a bracketed expression."""

    type = "bracketed"
    additional_kwargs = ["start_bracket", "end_bracket"]

    def __init__(
        self,
        *args,
        # These are tuples of segments but we're expecting them to
        # be tuples of length 1. This is because we'll almost always
        # be doing tuple arithmetic with the results and constructing
        # 1-tuples on the fly is very easy to misread.
        start_bracket: Tuple[BaseSegment] = None,
        end_bracket: Tuple[BaseSegment] = None,
        **kwargs,
    ):
        """Stash the bracket segments for later."""
        if not start_bracket or not end_bracket:  # pragma: no cover
            raise ValueError(
                "Attempted to construct Bracketed segment without specifying brackets."
            )
        self.start_bracket = start_bracket
        self.end_bracket = end_bracket
        super().__init__(*args, **kwargs)

    @classmethod
    def simple(cls, parse_context: ParseContext) -> Optional[List[str]]:
        """Simple methods for bracketed and the persitent brackets."""
        start_brackets = [
            start_bracket
            for _, start_bracket, _, persistent in parse_context.dialect.sets(
                "bracket_pairs"
            )
            if persistent
        ]
        start_simple = []
        for ref in start_brackets:
            start_simple += parse_context.dialect.ref(ref).simple(parse_context)
        return start_simple

    @classmethod
    def match(
        cls, segments: Tuple["BaseSegment", ...], parse_context: ParseContext
    ) -> MatchResult:
        """Only useful as a terminator."""
        if segments and isinstance(segments[0], cls):
            return MatchResult((segments[0],), segments[1:])
        return MatchResult.from_unmatched(segments)


class UnparsableSegment(BaseSegment):
    """This is a segment which can't be parsed. It indicates a error during parsing."""

    type = "unparsable"
    # From here down, comments are printed separately.
    comment_separate = True
    _expected = ""

    def __init__(self, *args, expected="", **kwargs):
        self._expected = expected
        super().__init__(*args, **kwargs)

    def _suffix(self):
        """Return any extra output required at the end when logging.

        NB Override this for specific subclasses if we want extra output.
        """
        return f"!! Expected: {self._expected!r}"

    def iter_unparsables(self):
        """Iterate through any unparsables.

        As this is an unparsable, it should yield itself.
        """
        yield self


class BaseFileSegment(BaseSegment):
    """A segment representing a whole file or script.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    type = "file"
    # The file segment is the only one which can start or end with non-code
    can_start_end_non_code = True
    # A file can be empty!
    allow_empty = True

    def __init__(
        self,
        segments,
        pos_marker=None,
        name: Optional[str] = None,
        fname: Optional[str] = None,
    ):
        self._file_path = fname
        super().__init__(segments, pos_marker=pos_marker, name=name)

    @property
    def file_path(self):
        """File path of a parsed SQL file."""
        return self._file_path

    def get_table_references(self):
        """Use parsed tree to extract table references."""
        references = set()
        for stmt in self.get_children("statement"):
            references |= stmt.get_table_references()
        return references
