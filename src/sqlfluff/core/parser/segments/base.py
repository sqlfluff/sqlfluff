"""Base segment definitions.

Here we define:
- BaseSegment. This is the root class for all segments, and is
  designed to hold other subsegments.
- UnparsableSegment. A special wrapper to indicate that the parse
  function failed on this block of segments and to prevent further
  analysis.
"""

from collections import defaultdict
from collections.abc import MutableSet
from copy import deepcopy, copy
from dataclasses import dataclass, field, replace
from io import StringIO
from itertools import takewhile, chain
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Optional,
    List,
    Tuple,
    Iterator,
    Set,
    TYPE_CHECKING,
)
import logging
from uuid import UUID, uuid4

from tqdm import tqdm

from sqlfluff.core.cached_property import cached_property
from sqlfluff.core.config import progress_bar_configuration
from sqlfluff.core.string_helpers import (
    frame_msg,
    curtail_string,
)

from sqlfluff.core.parser.context import RootParseContext
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
from sqlfluff.core.templaters.base import TemplatedFile

if TYPE_CHECKING:
    from sqlfluff.core.rules import LintFix  # pragma: no cover
    from sqlfluff.core.parser.segments import RawSegment  # pragma: no cover

# Instantiate the linter logger (only for use in methods involved with fixing.)
linter_logger = logging.getLogger("sqlfluff.linter")


@dataclass(frozen=True)
class SourceFix:
    """A stored reference to a fix in the non-templated file."""

    edit: str
    source_slice: slice
    # TODO: It might be possible to refactor this to not require
    # a templated_slice (because in theory it's unnecessary).
    # However much of the fix handling code assumes we need
    # a position in the templated file to interpret it.
    # More work required to achieve that if desired.
    templated_slice: slice

    def __hash__(self):
        # Only hash based on the source slice, not the
        # templated slice (which might change)
        return hash((self.edit, self.source_slice.start, self.source_slice.stop))


@dataclass(frozen=True)
class PathStep:
    """An element of the response to BaseSegment.path_to().

    Attributes:
        segment (:obj:`BaseSegment`): The segment in the chain.
        idx (int): The index of the target within its `segment`.
        len (int): The number of children `segment` has.
    """

    segment: "BaseSegment"
    idx: int
    len: int


@dataclass
class FixPatch:
    """An edit patch for a source file."""

    templated_slice: slice
    fixed_raw: str
    # The patch category, functions mostly for debugging and explanation
    # than for function. It allows traceability of *why* this patch was
    # generated. It has no significance for processing.
    patch_category: str
    source_slice: slice
    templated_str: str
    source_str: str

    def dedupe_tuple(self):
        """Generate a tuple of this fix for deduping."""
        return (self.source_slice, self.fixed_raw)

    @classmethod
    def infer_from_template(
        cls,
        templated_slice: slice,
        fixed_raw: str,
        patch_category: str,
        templated_file: TemplatedFile,
    ):
        """Infer source position from just templated position.

        In cases where we expect it to be uncontroversial it
        is sometimes more straightforward to just leverage
        the existing mapping functions to auto-generate the
        source position rather than calculating it explicitly.
        """
        # NOTE: There used to be error handling here to catch ValueErrors.
        # Removed in July 2022 because untestable.
        source_slice = templated_file.templated_slice_to_source_slice(
            templated_slice,
        )
        return cls(
            source_slice=source_slice,
            templated_slice=templated_slice,
            patch_category=patch_category,
            fixed_raw=fixed_raw,
            templated_str=templated_file.templated_str[templated_slice],
            source_str=templated_file.source_str[source_slice],
        )


@dataclass
class AnchorEditInfo:
    """For a given fix anchor, count of the fix edit types and fixes for it."""

    delete: int = field(default=0)
    replace: int = field(default=0)
    create_before: int = field(default=0)
    create_after: int = field(default=0)
    fixes: List = field(default_factory=list)
    source_fixes: List = field(default_factory=list)
    # First fix of edit_type "replace" in "fixes"
    _first_replace: Optional["LintFix"] = field(default=None)

    def add(self, fix: "LintFix"):
        """Adds the fix and updates stats.

        We also allow potentially multiple source fixes on the same
        anchor by condensing them together here.
        """
        if fix.is_just_source_edit():
            assert fix.edit
            # is_just_source_edit confirms there will be a list
            # so we can hint that to mypy.
            self.source_fixes += fix.edit[0].source_fixes
            # is there already a replace?
            if self._first_replace:
                assert self._first_replace.edit
                # is_just_source_edit confirms there will be a list
                # and that's the only way to get into _first_replace
                # if it's populated so we can hint that to mypy.
                linter_logger.info(
                    "Multiple edits detected, condensing %s onto %s",
                    fix,
                    self._first_replace,
                )
                self._first_replace.edit[0] = self._first_replace.edit[0].edit(
                    source_fixes=self.source_fixes
                )
                linter_logger.info("Condensed fix: %s", self._first_replace)
                # Return without otherwise adding in this fix.
                return

        self.fixes.append(fix)
        if fix.edit_type == "replace" and not self._first_replace:
            self._first_replace = fix
        setattr(self, fix.edit_type, getattr(self, fix.edit_type) + 1)

    @property
    def total(self):
        """Returns total count of fixes."""
        return len(self.fixes)

    @property
    def is_valid(self):
        """Returns True if valid combination of fixes for anchor.

        Cases:
        * 0-1 fixes of any type: Valid
        * 2 fixes: Valid if and only if types are create_before and create_after
        """
        if self.total <= 1:
            # Definitely valid (i.e. no conflict) if 0 or 1. In practice, this
            # function probably won't be called if there are 0 fixes, but 0 is
            # valid; it simply means "no fixes to apply".
            return True
        if self.total == 2:
            # This is only OK for this special case. We allow this because
            # the intent is clear (i.e. no conflict): Insert something *before*
            # the segment and something else *after* the segment.
            return self.create_before == 1 and self.create_after == 1
        # Definitely bad if > 2.
        return False  # pragma: no cover


class SegmentMetaclass(type):
    """The metaclass for segments.

    This metaclass provides pre-computed class attributes
    based on the defined attributes of specific classes.
    """

    def __new__(mcs, name, bases, class_dict):
        """Generate a new class.

        We use the `type` class attribute for the class
        and it's parent base classes to build up a `set`
        of types on construction to use in type checking
        later in the process. Doing it on construction
        here saves calculating it at runtime for each
        instance of the class.
        """
        class_obj = super().__new__(mcs, name, bases, class_dict)
        added_type = class_dict.get("type", None)
        class_types = {added_type} if added_type else set()
        for base in bases:
            class_types.update(base._class_types)
        # NB: We're setting the private value so that some dependent
        # classes can make their own public property.
        class_obj._class_types = class_types
        return class_obj


class BaseSegment(metaclass=SegmentMetaclass):
    """The base segment element.

    This defines the base element which drives both Lexing, Parsing and Linting.
    A large chunk of the logic which defines those three operations are centered
    here. Much of what is defined in the BaseSegment is also used by its many
    subclasses rather than directly here.

    For clarity, the `BaseSegment` is mostly centered around a segment which contains
    other subsegments. For segments which don't have *children*, refer to the
    `RawSegment` class (which still inherits from this one).

    Segments are used both as instances to hold chunks of text, but also as classes
    themselves where they function a lot like grammars, and return instances of
    themselves when they match. The many classmethods in this class are usually to serve
    their purpose as a matcher.
    """

    # `type` should be the *category* of this kind of segment
    type: ClassVar[str] = "base"
    _class_types: ClassVar[Set[str]]  # NOTE: Set by SegmentMetaclass
    parse_grammar: Optional[Matchable] = None
    # We define the type here but no value. Subclasses must provide a value.
    match_grammar: Matchable
    comment_separate = False
    optional = False  # NB: See the sequence grammar for details
    is_meta = False
    # Are we able to have non-code at the start or end?
    can_start_end_non_code = False
    # Can we allow it to be empty? Usually used in combination
    # with the can_start_end_non_code.
    allow_empty = False
    # What other kwargs need to be copied when applying fixes.
    additional_kwargs: List[str] = []
    pos_marker: Optional[PositionMarker]

    def __init__(
        self,
        segments,
        pos_marker: Optional[PositionMarker] = None,
        uuid: Optional[UUID] = None,
    ):
        # A cache variable for expandable
        self._is_expandable: Optional[bool] = None

        if len(segments) == 0:  # pragma: no cover
            raise RuntimeError(
                "Setting {} with a zero length segment set. This shouldn't "
                "happen.".format(self.__class__)
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
                if all(seg.pos_marker for seg in segments):
                    pos_marker = PositionMarker.from_child_markers(
                        *(seg.pos_marker for seg in segments)
                    )
            else:  # pragma: no cover
                raise TypeError(
                    f"Unexpected type passed to BaseSegment: {type(segments)}"
                )

        self.pos_marker = pos_marker
        # Tracker for matching when things start moving.
        self.uuid = uuid or uuid4()

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
            (
                self.__class__.__name__,
                self.raw,
                self.pos_marker.source_position() if self.pos_marker else None,
            )
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
    def is_expandable(self) -> bool:
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
    def is_code(self) -> bool:
        """Return True if this segment contains any code."""
        return any(seg.is_code for seg in self.segments)

    @cached_property
    def is_comment(self) -> bool:  # pragma: no cover TODO?
        """Return True if this is entirely made of comments."""
        return all(seg.is_comment for seg in self.segments)

    @cached_property
    def is_whitespace(self) -> bool:
        """Return True if this segment is entirely whitespace."""
        return all(seg.is_whitespace for seg in self.segments)

    @cached_property
    def raw(self) -> str:
        """Make a string from the segments of this segment."""
        return "".join(seg.raw for seg in self.segments)

    @property
    def class_types(self) -> Set[str]:
        """The set of types for this segment."""
        # NOTE: This version is simple, but some dependent classes
        # (notably RawSegment) override this with something more
        # custom.
        return self._class_types

    @property
    def expected_form(self) -> str:
        """What to return to the user when unparsable."""
        return self.get_type()

    @cached_property
    def descendant_type_set(self) -> Set[str]:
        """The set of all contained types.

        This is used for rule crawling.

        NOTE: Does not include the types of the parent segment itself.
        """
        return set(
            chain.from_iterable(
                seg.descendant_type_set | seg.class_types for seg in self.segments
            )
        )

    @cached_property
    def direct_descendant_type_set(self) -> Set[str]:
        """The set of all directly child types.

        This is used for rule crawling.

        NOTE: Does not include the types of the parent segment itself.
        """
        return set(chain.from_iterable(seg.class_types for seg in self.segments))

    @cached_property
    def raw_upper(self) -> str:
        """Make an uppercase string from the segments of this segment."""
        return self.raw.upper()

    @cached_property
    def matched_length(self) -> int:
        """Return the length of the segment in characters."""
        return sum(seg.matched_length for seg in self.segments)

    @cached_property
    def raw_segments(self) -> List["RawSegment"]:
        """Returns a list of raw segments in this segment."""
        return self.get_raw_segments()

    @cached_property
    def raw_segments_with_ancestors(
        self,
    ) -> List[Tuple["RawSegment", List[PathStep]]]:
        """Returns a list of raw segments in this segment with the ancestors."""
        buffer = []
        for idx, seg in enumerate(self.segments):
            # If it's a raw, yield it with this segment as the parent
            new_step = [PathStep(self, idx, len(self.segments))]
            if seg.is_type("raw"):
                buffer.append((seg, new_step))
            # If it's not, recurse - prepending self to the ancestor stack
            else:
                buffer.extend(
                    [
                        (raw_seg, new_step + stack)
                        for raw_seg, stack in seg.raw_segments_with_ancestors
                    ]
                )
        return buffer

    @cached_property
    def source_fixes(self) -> List[SourceFix]:
        """Return any source fixes as list."""
        return list(chain.from_iterable(s.source_fixes for s in self.segments))

    @cached_property
    def first_non_whitespace_segment_raw_upper(self) -> Optional[str]:
        """Returns the first non-whitespace subsegment of this segment."""
        for seg in self.raw_segments:
            if seg.raw_upper.strip():
                return seg.raw_upper
        return None
        # return [seg.raw_upper for seg in self.raw_segments]

    @cached_property
    def is_templated(self) -> bool:
        """Returns True if the segment includes any templated code.

        This is a simple, very efficient check that doesn't require looking up
        the RawFileSlices for the segment.

        NOTE: A segment returning a True result may still have some literal
        code as well (i.e. a mixture of literal and templated).
        """
        # We check two things:
        # * Source slice not empty: If it's empty, this means it doesn't appear
        #   in the source, e.g. because it is new code generated by a lint fix.
        #   Return False for these.
        # * Source string doesn't match raw segment contents. This can only
        #   happen if templating is involved.
        assert self.pos_marker
        return (
            self.pos_marker.source_slice.start != self.pos_marker.source_slice.stop
            and self.raw != self.pos_marker.source_str()
        )

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
                    "%s has no attribute `is_expandable`. This segment appears poorly "
                    "constructed.",
                    stmt,
                )
                raise err
            if not hasattr(stmt, "parse"):  # pragma: no cover
                raise ValueError(
                    "{} has no method `parse`. This segment appears poorly "
                    "constructed.".format(stmt)
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
    def _position_segments(
        cls,
        segments: Tuple["BaseSegment", ...],
        parent_pos: Optional[PositionMarker] = None,
    ) -> Tuple["BaseSegment", ...]:
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
        segment_buffer: Tuple["BaseSegment", ...] = ()
        for idx, segment in enumerate(segments):
            repositioned_seg = copy(segment)
            # Fill any that don't have a position.
            if not repositioned_seg.pos_marker:
                # Can we get a position from the previous?
                if idx > 0:
                    prev_seg = segment_buffer[idx - 1]
                    # Given we're going back in the buffer we should
                    # have set the position marker for everything already
                    # in there. This is mostly a hint to mypy.
                    assert prev_seg.pos_marker
                    repositioned_seg.pos_marker = prev_seg.pos_marker.end_point_marker()
                # Can we get it from the parent?
                elif parent_pos:
                    repositioned_seg.pos_marker = parent_pos.start_point_marker()
                # Search forward for a following one, if we have to?
                else:
                    for fwd_seg in segments[idx + 1 :]:
                        if fwd_seg.pos_marker:
                            repositioned_seg.pos_marker = (
                                fwd_seg.pos_marker.start_point_marker()
                            )
                            break
                    else:  # pragma: no cover
                        raise ValueError("Unable to position new segment")

            assert repositioned_seg.pos_marker  # hint for mypy
            # Update the working position.
            repositioned_seg.pos_marker = (
                repositioned_seg.pos_marker.with_working_position(
                    line_no,
                    line_pos,
                )
            )
            line_no, line_pos = repositioned_seg.pos_marker.infer_next_position(
                repositioned_seg.raw, line_no, line_pos
            )

            # If this segment has children, recurse and reposition them too.
            if repositioned_seg.segments:
                repositioned_seg.segments = cls._position_segments(
                    repositioned_seg.segments, parent_pos=repositioned_seg.pos_marker
                )

            segment_buffer += (repositioned_seg,)

        return segment_buffer

    # ################ CLASS METHODS

    @classmethod
    def simple(cls, parse_context: ParseContext, crumbs=None) -> Optional[List[str]]:
        """Does this matcher support an uppercase hash matching route?

        This should be true if the MATCH grammar is simple. Most more
        complicated segments will be assumed to overwrite this method
        if they wish to be considered simple.
        """
        if cls.match_grammar:
            return cls.match_grammar.simple(parse_context=parse_context, crumbs=crumbs)
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
        # Use set intersection
        if cls._class_types.intersection(seg_type):
            return True
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

            # Calling unify here, allows the MatchResult class to do all the type
            # checking.
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
                try:
                    return MatchResult(
                        (cls(segments=m.matched_segments),), m.unmatched_segments
                    )
                except TypeError as err:  # pragma: no cover
                    # This is an error to assist with debugging dialect design.
                    # It's most likely that the match_grammar has been set on
                    # a raw segment which shouldn't happen.
                    raise TypeError(
                        f"Error in instantiating {cls.__module__}.{cls.__name__}. Have "
                        f"you defined a match_grammar on a RawSegment? : {str(err)}"
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
            "raw_segments_with_ancestors",
            "first_non_whitespace_segment_raw_upper",
            "source_fixes",
            "full_type_set",
            "descendant_type_set ",
            "direct_descendant_type_set ",
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

    def count_segments(self, raw_only=False):
        """Returns the number of segments in this segment."""
        if self.segments:
            self_count = 0 if raw_only else 1
            return self_count + sum(
                seg.count_segments(raw_only=raw_only) for seg in self.segments
            )
        else:
            return 1

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
                # If we're in code_only, only show the code segments, otherwise always
                # true
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

    def copy(self):
        """Copy the segment recursively, with appropriate copying of references."""
        new_seg = copy(self)
        if self.segments:
            new_seg.segments = tuple(seg.copy() for seg in self.segments)
        return new_seg

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
        """Iterate raw segments, optionally expanding some children."""
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

    def recursive_crawl_all(self, reverse: bool = False):
        """Recursively crawl all descendant segments."""
        if reverse:
            for seg in reversed(self.segments):
                yield from seg.recursive_crawl_all(reverse=reverse)
        yield self
        if not reverse:
            for seg in self.segments:
                yield from seg.recursive_crawl_all(reverse=reverse)

    def recursive_crawl(
        self,
        *seg_type: str,
        recurse_into: bool = True,
        no_recursive_seg_type: str = None,
    ):
        """Recursively crawl for segments of a given type.

        Args:
            seg_type: :obj:`str`: one or more type of segment
                to look for.
            recurse_into: :obj:`bool`: When an element of type "seg_type" is
                found, whether to recurse into it.
            no_recursive_seg_type: obj: `str`: a type of segment
                not to recurse further into.
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
                if not seg.is_type(no_recursive_seg_type):
                    yield from seg.recursive_crawl(
                        *seg_type,
                        recurse_into=recurse_into,
                        no_recursive_seg_type=no_recursive_seg_type,
                    )

    def path_to(self, other) -> List[PathStep]:
        """Given a segment which is assumed within self, get the intermediate segments.

        Returns:
            :obj:`list` of :obj:`PathStep`, not including the segment we're looking
                for. If `other` is not found, then empty list. This includes if
                called on self.

        The result of this should be interpreted as *the path from `self` to `other`*.
        If the return value is `[]` (an empty list), that implies there is no path
        from `self` to `other`. This would include the case where the two are the same
        segment, as there is no path from a segment to itself.

        Technically this could be seen as a "half open interval" of the path between
        two segments: in that it includes the root segment, but not the leaf.
        """
        # Return empty if they are the same segment.
        if self is other:
            return []  # pragma: no cover

        # Are we in the right ballpark?
        # NB: Comparisons have a higher precedence than `not`.
        if not self.get_start_loc() <= other.get_start_loc() <= self.get_end_loc():
            return []

        # Do we have any child segments at all?
        if not self.segments:
            return []

        # Check through each of the child segments
        for idx, seg in enumerate(self.segments):
            step = PathStep(self, idx, len(self.segments))
            # Have we found the target?
            if seg is other:
                return [step]
            # Is there a path to the target?
            res = seg.path_to(other)
            if res:
                return [step] + res

        # Not found.
        return []  # pragma: no cover

    def parse(
        self,
        parse_context: ParseContext,
        parse_grammar: Optional[Matchable] = None,
    ) -> "BaseSegment":
        """Use the parse grammar to find subsegments within this segment.

        A large chunk of the logic around this can be found in the `expand` method.

        Use the parse setting in the context for testing, mostly to check how deep to
        go. True/False for yes or no, an integer allows a certain number of levels.

        Optionally, this method allows a custom parse grammar to be
        provided which will override any existing parse grammar
        on the segment.
        """
        # Clear the denylist cache so avoid missteps
        if parse_context:
            parse_context.denylist.clear()

        # the parse_depth and recurse kwargs control how deep we will recurse for
        # testing.
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
                idx_non_code = self._find_start_or_end_non_code(segments)
                if idx_non_code is not None:  # pragma: no cover
                    raise ValueError(
                        f"Segment {self} {'starts' if idx_non_code == 0 else 'ends'} "
                        f"with non code segment: "
                        f"{segments[idx_non_code].raw!r}.\n{segments!r}"
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
                    # For now this means the parsing has failed. Lets add the unmatched
                    # bit at the end as something unparsable.
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
                # Very edge case, but some segments are allowed to be empty other than
                # non-code
                self.segments = pre_nc + post_nc
            else:
                # If there's no match at this stage, then it's unparsable. That's
                # a problem at this stage so wrap it in an unparsable segment and carry
                # on.
                self.segments = (
                    pre_nc
                    + (
                        UnparsableSegment(
                            segments=segments,
                            expected=self.expected_form,
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
        parse_depth_msg = (
            "###\n#\n# Beginning Parse Depth {}: {}\n#\n###\nInitial Structure:\n"
            "{}".format(
                parse_context.parse_depth + 1, self.__class__.__name__, self.stringify()
            )
        )
        if parse_context.may_recurse():
            parse_context.logger.debug(parse_depth_msg)
            with parse_context.deeper_parse() as ctx:
                self.segments = self.expand(
                    self.segments,
                    parse_context=ctx,
                )

        return self

    @staticmethod
    def _is_code_or_meta(segment: "BaseSegment") -> bool:
        return segment.is_code or segment.is_meta

    @classmethod
    def _find_start_or_end_non_code(cls, segments) -> Optional[int]:
        """If segment's first/last child is non-code, return index."""
        if segments:
            for idx in [0, -1]:
                if not cls._is_code_or_meta(segments[idx]):
                    return idx
        return None

    def apply_fixes(
        self, dialect, rule_code: str, fixes: Dict
    ) -> Tuple["BaseSegment", List["BaseSegment"], List["BaseSegment"]]:
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
            fixes_applied = []
            todo_buffer = list(self.segments)
            while True:
                if len(todo_buffer) == 0:
                    break
                else:
                    seg = todo_buffer.pop(0)

                    # Look for uuid match.
                    # This handles potential positioning ambiguity.
                    anchor_info: Optional[AnchorEditInfo] = fixes.pop(seg.uuid, None)
                    if anchor_info is not None:
                        seg_fixes = anchor_info.fixes
                        if (
                            len(seg_fixes) == 2
                            and seg_fixes[0].edit_type == "create_after"
                        ):  # pragma: no cover
                            # Must be create_before & create_after. Swap so the
                            # "before" comes first.
                            seg_fixes.reverse()

                        for f in anchor_info.fixes:
                            assert f.anchor.uuid == seg.uuid
                            fixes_applied.append(f)
                            linter_logger.debug(
                                "Matched fix for %s against segment: %s -> %s",
                                rule_code,
                                f,
                                seg,
                            )
                            if f.edit_type == "delete":
                                # We're just getting rid of this segment.
                                seg = None
                            elif f.edit_type in (
                                "replace",
                                "create_before",
                                "create_after",
                            ):
                                if (
                                    f.edit_type == "create_after"
                                    and len(anchor_info.fixes) == 1
                                ):
                                    # in the case of a creation after that is not part
                                    # of a create_before/create_after pair, also add
                                    # this segment before the edit.
                                    seg_buffer.append(seg)

                                # We're doing a replacement (it could be a single
                                # segment or an iterable)
                                if isinstance(f.edit, BaseSegment):
                                    seg_buffer.append(f.edit)  # pragma: no cover TODO?
                                else:
                                    for s in f.edit:
                                        seg_buffer.append(s)

                                if f.edit_type == "create_before":
                                    # in the case of a creation before, also add this
                                    # segment on the end
                                    seg_buffer.append(seg)

                            else:  # pragma: no cover
                                raise ValueError(
                                    "Unexpected edit_type: {!r} in {!r}".format(
                                        f.edit_type, f
                                    )
                                )
                    else:
                        seg_buffer.append(seg)
                # Invalidate any caches
                self.invalidate_caches()

            # If any fixes applied, do an intermediate reposition. When applying
            # fixes to children and then trying to reposition them, that recursion
            # may rely on the parent having already populated positions for any
            # of the fixes applied there first. This ensures those segments have
            # working positions to work with.
            if fixes_applied:
                seg_buffer = list(
                    self._position_segments(tuple(seg_buffer), parent_pos=r.pos_marker)
                )

            # Then recurse (i.e. deal with the children) (Requeueing)
            seg_queue = seg_buffer
            seg_buffer = []
            for seg in seg_queue:
                s, before, after = seg.apply_fixes(dialect, rule_code, fixes)
                # 'before' and 'after' will usually be empty. Only used when
                # lower-level fixes left 'seg' with non-code (usually
                # whitespace) segments as the first or last children. This is
                # generally not allowed (see the can_start_end_non_code field),
                # and these segments need to be "bubbled up" the tree.
                seg_buffer.extend(before)
                seg_buffer.append(s)
                seg_buffer.extend(after)

            before = []
            after = []
            # If there's a parse grammar and this segment is not allowed to
            # start or end with non-code, check for (and fix) misplaced
            # segments. The reason for the parse grammar check is autofix if and
            # only if parse() would've complained, and it has the same parse
            # grammar check prior to checking can_start_end_non_code.
            if r.parse_grammar and not r.can_start_end_non_code:
                idx_non_code = self._find_start_or_end_non_code(seg_buffer)
                # Are there misplaced segments from a fix?
                if idx_non_code is not None:
                    # Yes. Fix the misplaced segments: Do not include them
                    # in the new segment's children. Instead, return them to the
                    # caller, which will place them *adjacent to* the new
                    # segment, in effect, bubbling them up to the tree to a
                    # valid location.
                    save_seg_buffer = list(seg_buffer)
                    before.extend(
                        takewhile(
                            lambda seg: not self._is_code_or_meta(seg), seg_buffer
                        )
                    )
                    seg_buffer = seg_buffer[len(before) :]
                    after.extend(
                        takewhile(
                            lambda seg: not self._is_code_or_meta(seg),
                            reversed(seg_buffer),
                        )
                    )
                    after.reverse()
                    seg_buffer = seg_buffer[: len(seg_buffer) - len(after)]
                    assert before + seg_buffer + after == save_seg_buffer
                    linter_logger.debug(
                        "After applying fixes, segment %s violated "
                        "'can_start_end_non_code=False' constraint. Autofixing, "
                        "before=%s, after=%s",
                        self,
                        before,
                        after,
                    )
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
            if fixes_applied:
                self._validate_segment_after_fixes(rule_code, dialect, fixes_applied, r)
            # Return the new segment and any non-code that needs to bubble up
            # the tree.
            return r, before, after
        else:
            return self, [], []

    @classmethod
    def compute_anchor_edit_info(
        cls, fixes: List["LintFix"]
    ) -> Dict[int, AnchorEditInfo]:
        """Group and count fixes by anchor, return dictionary."""
        anchor_info = defaultdict(AnchorEditInfo)  # type: ignore
        for fix in fixes:
            # :TRICKY: Use segment uuid as the dictionary key since
            # different segments may compare as equal.
            anchor_id = fix.anchor.uuid
            anchor_info[anchor_id].add(fix)
        return dict(anchor_info)

    def _validate_segment_after_fixes(self, rule_code, dialect, fixes_applied, segment):
        """Checks correctness of new segment against match or parse grammar."""
        root_parse_context = RootParseContext(dialect=dialect)
        with root_parse_context as parse_context:
            try:
                # :HACK: Calling parse() corrupts the segment 'r'
                # in some cases, e.g. adding additional Dedent child
                # segments. Here, we work around this by calling
                # parse() on a "backup copy" of the segment.
                r_copy = deepcopy(segment)
                for seg in r_copy.segments:
                    seg.pos_marker = replace(
                        seg.pos_marker,
                        templated_file=self.pos_marker.templated_file,
                    )
                r_copy.parse(parse_context)
            except ValueError:  # pragma: no cover
                self._log_apply_fixes_check_issue(
                    "After %s fixes were applied, segment %r failed the "
                    "parse() check. Fixes: %r",
                    rule_code,
                    r_copy,
                    fixes_applied,
                )

    @staticmethod
    def _log_apply_fixes_check_issue(message, *args):  # pragma: no cover
        linter_logger.critical(message, exc_info=True, *args)

    def _iter_source_fix_patches(
        self, templated_file: TemplatedFile
    ) -> Iterator[FixPatch]:
        """Yield any source patches as fixes now.

        NOTE: This yields source fixes for the segment and any of its
        children, so it's important to call it at the right point in
        the recursion to avoid yielding duplicates.
        """
        for source_fix in self.source_fixes:
            yield FixPatch(
                source_fix.templated_slice,
                source_fix.edit,
                patch_category="source",
                source_slice=source_fix.source_slice,
                templated_str=templated_file.templated_str[source_fix.templated_slice],
                source_str=templated_file.source_str[source_fix.source_slice],
            )

    def iter_patches(self, templated_file: TemplatedFile) -> Iterator[FixPatch]:
        """Iterate through the segments generating fix patches.

        The patches are generated in TEMPLATED space. This is important
        so that we defer dealing with any loops until later. At this stage
        everything *should* happen in templated order.

        Occasionally we have an insertion around a placeholder, so we also
        return a hint to deal with that.
        """
        # Does it match? If so we can ignore it.
        assert self.pos_marker
        templated_raw = templated_file.templated_str[self.pos_marker.templated_slice]
        matches = self.raw == templated_raw
        if matches:
            # First yield any source fixes
            yield from self._iter_source_fix_patches(templated_file)
            # Then return.
            return

        # If we're here, the segment doesn't match the original.
        linter_logger.debug(
            "# Changed Segment Found: %s at %s: Original: [%r] Fixed: [%r]",
            type(self).__name__,
            self.pos_marker.templated_slice,
            templated_raw,
            self.raw,
        )

        # If it's all literal, then we don't need to recurse.
        if self.pos_marker.is_literal():
            # First yield any source fixes
            yield from self._iter_source_fix_patches(templated_file)
            # Then yield the position in the source file and the patch
            yield FixPatch.infer_from_template(
                self.pos_marker.templated_slice,
                self.raw,
                patch_category="literal",
                templated_file=templated_file,
            )
        # Can we go deeper?
        elif not self.segments:
            # It's not literal, but it's also a raw segment. If we're going
            # to yield a change, we would have done it from the parent, so
            # we just abort from here.
            return  # pragma: no cover TODO?
        else:
            # This segment isn't a literal, but has changed, we need to go deeper.

            # If there's an end of file segment or indent, ignore them just for the
            # purposes of patch iteration.
            # NOTE: This doesn't mutate the underlying `self.segments`.
            segments = self.segments
            while segments and segments[-1].is_type("end_of_file", "indent"):
                segments = segments[:-1]

            # Iterate through the child segments
            source_idx = self.pos_marker.source_slice.start
            templated_idx = self.pos_marker.templated_slice.start
            insert_buff = ""
            for seg_idx, segment in enumerate(segments):

                # First check for insertions.
                # We know it's an insertion if it has length but not in the templated
                # file.
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

                # If we get here, then we know it's an original. Check for deletions at
                # the point before this segment (vs the TEMPLATED).
                start_diff = segment.pos_marker.templated_slice.start - templated_idx

                # Check to see whether there's a discontinuity before the current
                # segment
                if start_diff > 0 or insert_buff:
                    # If we have an insert buffer, then it's an edit, otherwise a
                    # deletion.
                    yield FixPatch.infer_from_template(
                        slice(
                            segment.pos_marker.templated_slice.start
                            - max(start_diff, 0),
                            segment.pos_marker.templated_slice.start,
                        ),
                        insert_buff,
                        patch_category="mid_point",
                        templated_file=templated_file,
                    )

                    insert_buff = ""

                # Now we deal with any changes *within* the segment itself.
                yield from segment.iter_patches(templated_file=templated_file)

                # Once we've dealt with any patches from the segment, update
                # our position markers.
                source_idx = segment.pos_marker.source_slice.stop
                templated_idx = segment.pos_marker.templated_slice.stop

            # After the loop, we check whether there's a trailing deletion
            # or insert. Also valid if we still have an insertion buffer here.
            end_diff = self.pos_marker.templated_slice.stop - templated_idx
            if end_diff or insert_buff:
                source_slice = slice(
                    source_idx,
                    self.pos_marker.source_slice.stop,
                )
                templated_slice = slice(
                    templated_idx,
                    self.pos_marker.templated_slice.stop,
                )
                # We determine the source_slice directly rather than
                # inferring it so that we can be very specific that
                # we ensure that fixes adjacent to source-only slices
                # (e.g. {% endif %}) are placed appropriately relative
                # to source-only slices.
                yield FixPatch(
                    source_slice=source_slice,
                    templated_slice=templated_slice,
                    patch_category="end_point",
                    fixed_raw=insert_buff,
                    templated_str=templated_file.templated_str[templated_slice],
                    source_str=templated_file.source_str[source_slice],
                )

    def edit(
        self, raw: Optional[str] = None, source_fixes: Optional[List[SourceFix]] = None
    ):
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
    def simple(cls, parse_context: ParseContext, crumbs=None) -> Optional[List[str]]:
        """Simple methods for bracketed and the persistent brackets."""
        start_brackets = [
            start_bracket
            for _, start_bracket, _, persistent in parse_context.dialect.sets(
                "bracket_pairs"
            )
            if persistent
        ]
        start_simple = []
        for ref in start_brackets:
            start_simple += parse_context.dialect.ref(ref).simple(
                parse_context, crumbs=crumbs
            )
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
        fname: Optional[str] = None,
    ):
        self._file_path = fname
        super().__init__(segments, pos_marker=pos_marker)

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


class IdentitySet(MutableSet):
    """Similar to built-in set(), but based on object IDENTITY.

    This is often important when working with BaseSegment and other types,
    where different object instances may compare as equal.

    Copied from: https://stackoverflow.com/questions/16994307/identityset-in-python
    """

    key = id  # should return a hashable object

    def __init__(self, iterable=()):
        self.map = {}  # id -> object
        self |= iterable  # add elements from iterable to the set (union)

    def __len__(self):  # Sized
        return len(self.map)

    def __iter__(self):  # Iterable
        return self.map.values().__iter__()  # pragma: no cover

    def __contains__(self, x):  # Container
        return self.key(x) in self.map

    def add(self, value):  # MutableSet
        """Add an element."""
        self.map[self.key(value)] = value

    def update(self, value):
        """Add elements in 'value'."""
        for v in value:
            self.add(v)

    def discard(self, value):  # MutableSet
        """Remove an element.  Do not raise an exception if absent."""
        self.map.pop(self.key(value), None)  # pragma: no cover

    def __repr__(self):  # pragma: no cover
        if not self:
            return "%s()" % (self.__class__.__name__,)
        return "%s(%r)" % (self.__class__.__name__, list(self))
