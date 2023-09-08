"""Base segment definitions.

Here we define:
- BaseSegment. This is the root class for all segments, and is
  designed to hold other subsegments.
- UnparsableSegment. A special wrapper to indicate that the parse
  function failed on this block of segments and to prevent further
  analysis.
"""
# Import annotations for py 3.7 to allow `weakref.ReferenceType["BaseSegment"]`
from __future__ import annotations

import logging
import weakref
from collections import defaultdict
from copy import copy
from dataclasses import dataclass
from io import StringIO
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)
from uuid import UUID, uuid4

from tqdm import tqdm

from sqlfluff.core.cached_property import cached_property
from sqlfluff.core.config import progress_bar_configuration
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.helpers import check_still_complete, trim_non_code_segments
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.match_logging import parse_match_logging
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments.fix import AnchorEditInfo, FixPatch, SourceFix
from sqlfluff.core.parser.types import SimpleHintType
from sqlfluff.core.string_helpers import curtail_string, frame_msg
from sqlfluff.core.templaters.base import TemplatedFile

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.dialects import Dialect
    from sqlfluff.core.parser.segments.raw import RawSegment
    from sqlfluff.core.rules import LintFix

# Instantiate the linter logger (only for use in methods involved with fixing.)
linter_logger = logging.getLogger("sqlfluff.linter")

TupleSerialisedSegment = Tuple[str, Union[str, Tuple["TupleSerialisedSegment", ...]]]
RecordSerialisedSegment = Dict[
    str, Union[None, str, "RecordSerialisedSegment", List["RecordSerialisedSegment"]]
]


@dataclass(frozen=True)
class PathStep:
    """An element of the response to BaseSegment.path_to().

    Attributes:
        segment (:obj:`BaseSegment`): The segment in the chain.
        idx (int): The index of the target within its `segment`.
        len (int): The number of children `segment` has.
        code_idxs (:obj:`tuple` of int): The indices which contain code.
    """

    segment: "BaseSegment"
    idx: int
    len: int
    code_idxs: Tuple[int, ...]


class SegmentMetaclass(type):
    """The metaclass for segments.

    This metaclass provides pre-computed class attributes
    based on the defined attributes of specific classes.
    """

    def __new__(
        mcs: Type[type],
        name: str,
        bases: Tuple[Type["BaseSegment"]],
        class_dict: Dict[str, Any],
    ) -> SegmentMetaclass:
        """Generate a new class.

        We use the `type` class attribute for the class
        and it's parent base classes to build up a `set`
        of types on construction to use in type checking
        later in the process. Doing it on construction
        here saves calculating it at runtime for each
        instance of the class.
        """
        # Create a cache uuid on definition.
        # We do it here so every _definition_ of a segment
        # gets a unique UUID regardless of dialect.
        class_dict["_cache_key"] = uuid4().hex

        # Populate the `_class_types` property on creation.
        added_type = class_dict.get("type", None)
        class_types = {added_type} if added_type else set()
        for base in bases:
            class_types.update(base._class_types)
        class_dict["_class_types"] = class_types

        return cast(Type["BaseSegment"], type.__new__(mcs, name, bases, class_dict))


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
    is_meta = False
    # Are we able to have non-code at the start or end?
    can_start_end_non_code = False
    # Can we allow it to be empty? Usually used in combination
    # with the can_start_end_non_code.
    allow_empty = False
    # What other kwargs need to be copied when applying fixes.
    additional_kwargs: List[str] = []
    pos_marker: Optional[PositionMarker]
    # NOTE: Cache key is generated by the SegmentMetaclass
    _cache_key: str
    # _preface_modifier used in ._preface()
    _preface_modifier: str = ""
    # Optional reference to the parent. Stored as a weakref.
    _parent: Optional[weakref.ReferenceType["BaseSegment"]] = None

    def __init__(
        self,
        segments: Tuple["BaseSegment", ...],
        pos_marker: Optional[PositionMarker] = None,
        uuid: Optional[UUID] = None,
    ) -> None:
        if len(segments) == 0:  # pragma: no cover
            raise RuntimeError(
                "Setting {} with a zero length segment set. This shouldn't "
                "happen.".format(self.__class__)
            )

        if not pos_marker:
            # If no pos given, work it out from the children.
            if all(seg.pos_marker for seg in segments):
                pos_marker = PositionMarker.from_child_markers(
                    *(seg.pos_marker for seg in segments)
                )

        self.pos_marker = pos_marker
        self.segments: Tuple["BaseSegment", ...] = segments
        # A cache variable for expandable
        self._is_expandable: Optional[bool] = None
        # Tracker for matching when things start moving.
        self.uuid = uuid or uuid4()

        self._recalculate_caches()

    def __setattr__(self, key: str, value: Any) -> None:
        try:
            if key == "segments":
                self._recalculate_caches()

        except (AttributeError, KeyError):  # pragma: no cover
            pass

        super().__setattr__(key, value)

    def __eq__(self, other: Any) -> bool:
        # NB: this should also work for RawSegment
        if not isinstance(other, BaseSegment):
            return False  # pragma: no cover
        # If the uuids match, then we can easily return early.
        if self.uuid == other.uuid:
            return True
        return (
            # Same class NAME. (could be constructed elsewhere)
            self.__class__.__name__ == other.__class__.__name__
            and (self.raw == other.raw)
            # Both must have a non-null position marker to compare.
            and self.pos_marker is not None
            and other.pos_marker is not None
            # We only match that the *start* is the same. This means we can
            # still effectively construct searches look for segments.
            # This is important for .apply_fixes().
            and (
                self.pos_marker.start_point_marker()
                == other.pos_marker.start_point_marker()
            )
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.__class__.__name__,
                self.raw,
                self.pos_marker.source_position() if self.pos_marker else None,
            )
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ({self.pos_marker})>"

    def __getstate__(self) -> Dict[str, Any]:
        """Get the current state to allow pickling."""
        s = self.__dict__.copy()
        # Kill the parent ref. It won't pickle well.
        s["_parent"] = None
        return s

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """Set state during process of unpickling."""
        self.__dict__ = state.copy()
        # Once state is ingested - repopulate, NOT recursing.
        # Child segments will do it for themselves on unpickling.
        self.set_as_parent(recurse=False)

    # ################ PRIVATE PROPERTIES

    @property
    def _comments(self) -> List["BaseSegment"]:
        """Returns only the comment elements of this segment."""
        return [seg for seg in self.segments if seg.is_type("comment")]

    @property
    def _non_comments(self) -> List["BaseSegment"]:  # pragma: no cover TODO?
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
    def _code_indices(self) -> Tuple[int, ...]:
        """The indices of code elements.

        This is used in the path_to algorithm for tree traversal.
        """
        return tuple(idx for idx, seg in enumerate(self.segments) if seg.is_code)

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
        code_idxs = tuple(idx for idx, seg in enumerate(self.segments) if seg.is_code)
        for idx, seg in enumerate(self.segments):
            # If it's a raw, yield it with this segment as the parent
            new_step = [PathStep(self, idx, len(self.segments), code_idxs)]
            if seg.is_type("raw"):
                buffer.append((cast("RawSegment", seg), new_step))
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
        # * It's not a literal slice. If it's a literal and has size then it's
        #   not templated.
        assert self.pos_marker
        return (
            self.pos_marker.source_slice.start != self.pos_marker.source_slice.stop
            and not self.pos_marker.is_literal()
        )

    # ################ STATIC METHODS

    def _suffix(self) -> str:
        """Return any extra output required at the end when logging.

        NB Override this for specific subclasses if we want extra output.
        """
        return ""

    @classmethod
    def expand(
        cls, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> Tuple[BaseSegment, ...]:
        """Expand the list of child segments using their `parse` methods."""
        expanded_segments: Tuple[BaseSegment, ...] = ()

        # Renders progress bar only for `BaseFileSegments`.
        disable_progress_bar = (
            not cls.class_is_type("file")
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
            if not stmt.is_expandable:
                parse_context.logger.info(
                    "[PD:%s] Skipping expansion of %s...",
                    parse_context.parse_depth,
                    stmt,
                )
                expanded_segments += (stmt,)
                continue

            parse_depth_msg = "Parse Depth {}. Expanding: {}: {!r}".format(
                parse_context.parse_depth,
                stmt.__class__.__name__,
                curtail_string(stmt.raw, length=40),
            )
            parse_context.logger.info(frame_msg(parse_depth_msg))
            expanded_segments += stmt.parse(parse_context=parse_context)

        # Basic Validation
        check_still_complete(segments, expanded_segments, ())
        return expanded_segments

    @classmethod
    def _position_segments(
        cls,
        segments: Tuple["BaseSegment", ...],
        parent_pos: Optional[PositionMarker] = None,
        metas_only: bool = False,
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
            # NOTE: Repositioning can be very compute intensive to do
            # completely (especially because of the copying required
            # to do it safely), but during the parsing phase we may
            # only need to reposition meta segments. Because they have
            # no size in the templated file and also no children - they
            # can be done safely without affecting the rest of the file.
            if metas_only and not segment.is_meta:
                # Assert that the segment already has position. Unless a
                # fix has occured this should already be true.
                assert segment.pos_marker, (
                    "Non-meta segment found without position. Inappropriate "
                    "use of `metas_only`."
                )
                # Add the original segment to the buffer.
                segment_buffer += (segment,)
                # Update working position
                line_no, line_pos = segment.pos_marker.infer_next_position(
                    segment.raw, line_no, line_pos
                )
                continue

            # Get hold of the current position.
            old_position = segment.pos_marker
            new_position = segment.pos_marker
            # Fill any that don't have a position.
            if not old_position:
                # Can we get a position from the previous?
                start_point = None
                if idx > 0:
                    prev_seg = segment_buffer[idx - 1]
                    # Given we're going back in the buffer we should
                    # have set the position marker for everything already
                    # in there. This is mostly a hint to mypy.
                    assert prev_seg.pos_marker
                    start_point = prev_seg.pos_marker.end_point_marker()
                # Can we get it from the parent?
                elif parent_pos:
                    start_point = parent_pos.start_point_marker()

                # Search forward for the end point.
                end_point = None
                for fwd_seg in segments[idx + 1 :]:
                    if fwd_seg.pos_marker:
                        # NOTE: Use raw segments because it's more reliable.
                        end_point = fwd_seg.raw_segments[
                            0
                        ].pos_marker.start_point_marker()
                        break

                if start_point and end_point and start_point != end_point:
                    # We should construct a wider position marker.
                    new_position = PositionMarker.from_points(
                        start_point,
                        end_point,
                    )
                # If we have start point (or if they were equal above),
                # just apply start point.
                elif start_point:
                    new_position = start_point
                # Do we have an end?
                elif end_point:
                    new_position = end_point
                else:  # pragma: no cover
                    raise ValueError("Unable to position new segment")

            assert new_position

            # Regardless of whether we change the position, we still need to
            # update the working location and keep track of it.
            new_position = new_position.with_working_position(line_no, line_pos)
            line_no, line_pos = new_position.infer_next_position(
                segment.raw, line_no, line_pos
            )

            # NOTE: If the position is already correct, we still
            # need to copy, but we don't need to reposition any further.
            if segment.segments and old_position != new_position:
                # Recurse to work out the child segments FIRST, before
                # copying the parent so we don't double the work.
                child_segments = cls._position_segments(
                    segment.segments, parent_pos=new_position
                )
                new_seg = segment.copy(segments=child_segments)
                new_seg.pos_marker = new_position
            else:
                new_seg = segment.copy()
                new_seg.pos_marker = new_position

            new_seg.pos_marker = new_position
            segment_buffer += (new_seg,)
            continue

        return segment_buffer

    # ################ CLASS METHODS

    @classmethod
    def simple(
        cls, parse_context: ParseContext, crumbs: Optional[Tuple[str, ...]] = None
    ) -> Optional["SimpleHintType"]:
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
    def cache_key(cls) -> str:
        """Return the cache key for this segment definition.

        NOTE: The key itself is generated on _definition_ by the metaclass.
        """
        return cls._cache_key

    @classmethod
    def is_optional(cls) -> bool:  # pragma: no cover
        """Returns False because Segments are never optional.

        This is used _only_ in the `Sequence` & `Bracketed` grammars
        to indicate optional elements in a sequence which may not be
        present while still returning a valid match.

        Typically in dialect definition, Segments are rarely referred to
        directly, but normally are referenced via a `Ref()` grammar.
        The `Ref()` grammar supports optional referencing and so we
        recommend wrapping a segment in an optional `Ref()` to take
        advantage of optional sequence elements as this is not
        supported directly on the Segment itself.
        """
        return False

    @classmethod
    def class_is_type(cls, *seg_type: str) -> bool:
        """Is this segment class (or its parent) of the given type."""
        # Use set intersection
        if cls._class_types.intersection(seg_type):
            return True
        return False

    @classmethod
    def structural_simplify(
        cls, elem: TupleSerialisedSegment
    ) -> RecordSerialisedSegment:
        """Simplify the structure recursively so it serializes nicely in json/yaml.

        This is used in the .as_record() method.
        """
        assert len(elem) == 2
        key, value = elem
        assert isinstance(key, str)
        if isinstance(value, str):
            return {key: value}
        assert isinstance(value, tuple)
        # If it's an empty tuple return a dict with None.
        if not value:
            return {key: None}
        # Otherwise value is a tuple with length.
        # Simplify all the child elements
        contents = [cls.structural_simplify(e) for e in value]

        # Any duplicate elements?
        subkeys: List[str] = []
        for _d in contents:
            subkeys.extend(_d.keys())
        if len(set(subkeys)) != len(subkeys):
            # Yes: use a list of single dicts.
            # Recurse directly.
            return {key: contents}

        # Otherwise there aren't duplicates, un-nest the list into a dict:
        content_dict = {}
        for record in contents:
            for k, v in record.items():
                content_dict[k] = v
        return {key: content_dict}

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
            with parse_context.deeper_match(name=cls.__name__) as ctx:
                m = cls.match_grammar.match(segments=segments, parse_context=ctx)

            if m.has_match():
                return MatchResult(
                    # Return result of the match_grammar match, wrapped in a new
                    # instance of this segment. The matched portion of the
                    # MatchResult from the match_grammar, becomes the children
                    # (i.e. the `segments`) of that new segment.
                    (cls(segments=m.matched_segments),),
                    m.unmatched_segments,
                )
            else:
                return MatchResult.from_unmatched(segments)
        else:  # pragma: no cover
            raise NotImplementedError(
                f"{cls.__name__} has no match function implemented"
            )

    # ################ PRIVATE INSTANCE METHODS

    def _recalculate_caches(self) -> None:
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
            "descendant_type_set",
            "direct_descendant_type_set",
            "_code_indices",
        ]:
            self.__dict__.pop(key, None)

    def _preface(self, ident: int, tabsize: int) -> str:
        """Returns the preamble to any logging."""
        padded_type = "{padding}{modifier}{type}".format(
            padding=" " * (ident * tabsize),
            modifier=self._preface_modifier,
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

    def set_as_parent(self, recurse: bool = True) -> None:
        """Set this segment as parent for child all segments."""
        for seg in self.segments:
            seg.set_parent(self)
            # Recurse if not disabled
            if recurse:
                seg.set_as_parent(recurse=recurse)

    def set_parent(self, parent: "BaseSegment") -> None:
        """Set the weak reference to the parent.

        NOTE: Don't validate on set, because we might not have fully
        initialised the parent yet (because we call this method during
        the instantiation of the parent).
        """
        self._parent = weakref.ref(parent)

    def get_parent(self) -> Optional["BaseSegment"]:
        """Get the parent segment, with some validation.

        This is provided as a performance optimisation when searching
        through the syntax tree. Any methods which depend on this should
        have an alternative way of assessing position, and ideally also
        set the parent of any segments found without them.

        NOTE: We only store a weak reference to the parent so it might
        not be present. We also validate here that it's _still_ the parent
        and potentially also return None if those checks fail.
        """
        if not self._parent:
            return None
        _parent = self._parent()
        if not _parent or self not in _parent.segments:
            return None
        return _parent

    def get_type(self) -> str:
        """Returns the type of this segment as a string."""
        return self.type

    def count_segments(self, raw_only: bool = False) -> int:
        """Returns the number of segments in this segment."""
        if self.segments:
            self_count = 0 if raw_only else 1
            return self_count + sum(
                seg.count_segments(raw_only=raw_only) for seg in self.segments
            )
        else:
            return 1

    def is_type(self, *seg_type: str) -> bool:
        """Is this segment (or its parent) of the given type."""
        return self.class_is_type(*seg_type)

    def invalidate_caches(self) -> None:
        """Invalidate the cached properties.

        This should be called whenever the segments within this
        segment is mutated.
        """
        for seg in self.segments:
            seg.invalidate_caches()

        self._recalculate_caches()

    def get_start_point_marker(self) -> PositionMarker:  # pragma: no cover
        """Get a point marker at the start of this segment."""
        assert self.pos_marker
        return self.pos_marker.start_point_marker()

    def get_end_point_marker(self) -> PositionMarker:
        """Get a point marker at the end of this segment."""
        assert self.pos_marker
        return self.pos_marker.end_point_marker()

    def get_start_loc(self) -> Tuple[int, int]:
        """Get a location tuple at the start of this segment."""
        assert self.pos_marker
        return self.pos_marker.working_loc

    def get_end_loc(self) -> Tuple[int, int]:
        """Get a location tuple at the end of this segment."""
        assert self.pos_marker
        return self.pos_marker.working_loc_after(
            self.raw,
        )

    def stringify(
        self, ident: int = 0, tabsize: int = 4, code_only: bool = False
    ) -> str:
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

    def to_tuple(
        self,
        code_only: bool = False,
        show_raw: bool = False,
        include_meta: bool = False,
    ) -> TupleSerialisedSegment:
        """Return a tuple structure from this segment."""
        # works for both base and raw

        if show_raw and not self.segments:
            return (self.get_type(), self.raw)
        elif code_only:
            return (
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
            return (
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

    def copy(
        self, segments: Optional[Tuple["BaseSegment", ...]] = None
    ) -> "BaseSegment":
        """Copy the segment recursively, with appropriate copying of references.

        Optionally provide child segments which have already been dealt
        with to avoid another copy operation.
        """
        new_seg = copy(self)
        # Position markers are immutable, and it's important that we keep
        # a reference to the same TemplatedFile, so keep the same position
        # marker.
        new_seg.pos_marker = self.pos_marker
        # If segments were provided, use them.
        if segments:
            new_seg.segments = segments
        # Otherwise copy them.
        elif self.segments:
            new_seg.segments = tuple(seg.copy() for seg in self.segments)
        return new_seg

    def as_record(self, **kwargs: bool) -> Optional[RecordSerialisedSegment]:
        """Return the segment as a structurally simplified record.

        This is useful for serialization to yaml or json.
        kwargs passed to to_tuple
        """
        return self.structural_simplify(self.to_tuple(**kwargs))

    def get_raw_segments(self) -> List["RawSegment"]:
        """Iterate raw segments, mostly for searching."""
        return [item for s in self.segments for item in s.raw_segments]

    def iter_segments(
        self, expanding: Optional[Sequence[str]] = None, pass_through: bool = False
    ) -> Iterator["BaseSegment"]:
        """Iterate segments, optionally expanding some children."""
        for s in self.segments:
            if expanding and s.is_type(*expanding):
                yield from s.iter_segments(
                    expanding=expanding if pass_through else None
                )
            else:
                yield s

    def iter_unparsables(self) -> Iterator["UnparsableSegment"]:
        """Iterate through any unparsables this segment may contain."""
        for s in self.segments:
            yield from s.iter_unparsables()

    def type_set(self) -> Set[str]:
        """Return a set of the types contained, mostly for testing."""
        typs = {self.type}
        for s in self.segments:
            typs |= s.type_set()
        return typs

    def is_raw(self) -> bool:
        """Return True if this segment has no children."""
        return len(self.segments) == 0

    def get_child(self, *seg_type: str) -> Optional[BaseSegment]:
        """Retrieve the first of the children of this segment with matching type."""
        for seg in self.segments:
            if seg.is_type(*seg_type):
                return seg
        return None

    def get_children(self, *seg_type: str) -> List[BaseSegment]:
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
    ) -> List["BaseSegment"]:
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

    def recursive_crawl_all(self, reverse: bool = False) -> Iterator[BaseSegment]:
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
        no_recursive_seg_type: Optional[str] = None,
        allow_self: bool = True,
    ) -> Iterator[BaseSegment]:
        """Recursively crawl for segments of a given type.

        Args:
            seg_type: :obj:`str`: one or more type of segment
                to look for.
            recurse_into: :obj:`bool`: When an element of type "seg_type" is
                found, whether to recurse into it.
            no_recursive_seg_type: :obj:`str`: a type of segment
                not to recurse further into. It is highly recommended
                to set this argument where possible, as it can significantly
                narrow the search pattern.
            allow_self: :obj:`bool`: Whether to allow the initial segment this
                is called on to be one of the results.
        """
        # Assuming there is a segment to be found, first check self (if allowed):
        if allow_self and self.is_type(*seg_type):
            match = True
            yield self
        else:
            match = False

        # Check whether the types we're looking for are in this segment
        # at all. If not, exit early.
        if not self.descendant_type_set.intersection(seg_type):
            # Terminate iteration.
            return None

        # Then handle any recursion.
        if recurse_into or not match:
            for seg in self.segments:
                # Don't recurse if the segment is of a type we shouldn't
                # recurse into.
                # NOTE: Setting no_recursive_seg_type can significantly
                # improve performance in many cases.
                if not no_recursive_seg_type or not seg.is_type(no_recursive_seg_type):
                    yield from seg.recursive_crawl(
                        *seg_type,
                        recurse_into=recurse_into,
                        no_recursive_seg_type=no_recursive_seg_type,
                    )

    def path_to(self, other: "BaseSegment") -> List[PathStep]:
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

        We first use any existing parent references to work upward, and then if that
        doesn't take us far enough we fill in from the top (setting any missing
        references as we go). This tries to be as efficient in that process as
        possible.
        """
        # Return empty if they are the same segment.
        if self is other:
            return []  # pragma: no cover

        # Do we have any child segments at all?
        if not self.segments:
            return []

        # Identifying the highest parent we can using any preset parent values.
        midpoint = other
        lower_path = []
        while True:
            _higher = midpoint.get_parent()
            # If we've run out of parents, stop for now.
            if not _higher:
                break
            lower_path.append(
                PathStep(
                    _higher,
                    _higher.segments.index(midpoint),
                    len(_higher.segments),
                    _higher._code_indices,
                )
            )
            midpoint = _higher
            # If we're found the target segment we can also stop.
            if midpoint == self:
                break

        # Reverse the path so far
        lower_path.reverse()

        # Have we already found the parent?
        if midpoint == self:
            return lower_path
        # Have we gone all the way up to the file segment?
        elif midpoint.class_is_type("file"):
            return []  # pragma: no cover
        # Are we in the right ballpark?
        # NOTE: Comparisons have a higher precedence than `not`.
        elif not self.get_start_loc() <= midpoint.get_start_loc() <= self.get_end_loc():
            return []

        # From here, we've worked "up" as far as we can, we now work "down".
        # When working down, we only need to go as far as the `midpoint`.

        # Check through each of the child segments
        for idx, seg in enumerate(self.segments):
            # Set the parent if it's not already set.
            seg.set_parent(self)
            # Build the step.
            step = PathStep(self, idx, len(self.segments), self._code_indices)
            # Have we found the target?
            # NOTE: Check for _equality_ not _identity_ here as that's most reliable.
            if seg == midpoint:
                return [step] + lower_path
            # Is there a path to the target?
            res = seg.path_to(midpoint)
            if res:
                return [step] + res + lower_path

        # Not found.
        return []  # pragma: no cover

    def parse(
        self,
        parse_context: ParseContext,
        parse_grammar: Optional[Matchable] = None,
    ) -> Tuple["BaseSegment", ...]:
        """Use the parse grammar to find subsegments within this segment.

        A large chunk of the logic around this can be found in the `expand` method.

        Use the parse setting in the context for testing, mostly to check how deep to
        go. True/False for yes or no, an integer allows a certain number of levels.

        Optionally, this method allows a custom parse grammar to be
        provided which will override any existing parse grammar
        on the segment.
        """
        # the parse_depth and recurse kwargs control how deep we will recurse for
        # testing.
        if not self.segments:  # pragma: no cover
            # This means we're a leaf segment, just return an unchanged self.
            # NOTE: This is uncovered in tests, because typically, the `expand()`
            # method of the parent will filter out any segments which aren't
            # expandable.
            return (self,)

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
            with parse_context.deeper_match(name=self.__class__.__name__) as ctx:
                m = parse_grammar.match(segments=segments, parse_context=ctx)

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

        parse_depth_msg = (
            "###\n#\n# Beginning Parse Depth {}: {}\n#\n###\nInitial Structure:\n"
            "{}".format(
                parse_context.parse_depth + 1, self.__class__.__name__, self.stringify()
            )
        )
        parse_context.logger.debug(parse_depth_msg)
        with parse_context.deeper_parse(name=self.__class__.__name__) as ctx:
            self.segments = self.expand(
                self.segments,
                parse_context=ctx,
            )
        # Once parsed, populate any parent relationships.
        for _seg in self.segments:
            _seg.set_as_parent()

        return (self,)

    @staticmethod
    def _is_code_or_meta(segment: "BaseSegment") -> bool:
        return segment.is_code or segment.is_meta

    @classmethod
    def _find_start_or_end_non_code(
        cls, segments: Sequence[BaseSegment]
    ) -> Optional[int]:
        """If segment's first/last child is non-code, return index."""
        if segments:
            for idx in [0, -1]:
                if not cls._is_code_or_meta(segments[idx]):
                    return idx
        return None

    def apply_fixes(
        self, dialect: "Dialect", rule_code: str, fixes: Dict[UUID, AnchorEditInfo]
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
            fixes_applied: List[LintFix] = []
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
                                pass
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
                                    seg.set_parent(self)

                                # We're doing a replacement (it could be a single
                                # segment or an iterable)
                                assert f.edit, f"Edit {f.edit_type!r} requires `edit`."
                                consumed_pos = False
                                for s in f.edit:
                                    seg_buffer.append(s)
                                    s.set_parent(self)
                                    # If one of them has the same raw representation
                                    # then the first that matches gets to take the
                                    # original position marker.
                                    if (
                                        f.edit_type == "replace"
                                        and s.raw == seg.raw
                                        and not consumed_pos
                                    ):
                                        seg_buffer[-1].pos_marker = seg.pos_marker
                                        consumed_pos = True

                                if f.edit_type == "create_before":
                                    # in the case of a creation before, also add this
                                    # segment on the end
                                    seg_buffer.append(seg)
                                    seg.set_parent(self)

                            else:  # pragma: no cover
                                raise ValueError(
                                    "Unexpected edit_type: {!r} in {!r}".format(
                                        f.edit_type, f
                                    )
                                )
                    else:
                        seg_buffer.append(seg)
                        seg.set_parent(self)
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

            # After fixing we should be able to rely on whitespace being
            # inserted in appropriate places. That logic now lives in
            # `BaseRule._choose_anchor_segment()`, rather than here.

            # Rather than fix that here, we simply assert that it has been
            # done. This will raise issues in testing, but shouldn't in use.
            if r.parse_grammar and not r.can_start_end_non_code and seg_buffer:
                assert not self._find_start_or_end_non_code(seg_buffer), (
                    "Found inappropriate fix application: inappropriate "
                    "whitespace positioning. Post `_choose_anchor_segment`. "
                    "Please report this issue on GitHub with your SQL query. "
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
    ) -> Dict[UUID, AnchorEditInfo]:
        """Group and count fixes by anchor, return dictionary."""
        anchor_info = defaultdict(AnchorEditInfo)  # type: ignore
        for fix in fixes:
            # :TRICKY: Use segment uuid as the dictionary key since
            # different segments may compare as equal.
            anchor_id = fix.anchor.uuid
            anchor_info[anchor_id].add(fix)
        return dict(anchor_info)

    def _validate_segment_after_fixes(
        self,
        rule_code: str,
        dialect: "Dialect",
        fixes_applied: List[LintFix],
        segment: BaseSegment,
    ) -> None:
        """Checks correctness of new segment against match or parse grammar."""
        ctx = ParseContext(dialect=dialect)
        try:
            # :HACK: Calling parse() corrupts the segment 'r'
            # in some cases, e.g. adding additional Dedent child
            # segments. Here, we work around this by calling
            # parse() on a "backup copy" of the segment.
            segment_copy = segment.copy()
            segment_copy.parse(ctx)
        except ValueError:  # pragma: no cover
            self._log_apply_fixes_check_issue(
                "After %s fixes were applied, segment %r failed the "
                "parse() check. Fixes: %r",
                rule_code,
                segment_copy,
                fixes_applied,
            )

    @staticmethod
    def _log_apply_fixes_check_issue(
        message: str, *args: Any
    ) -> None:  # pragma: no cover
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
            yield FixPatch(
                source_slice=self.pos_marker.source_slice,
                templated_slice=self.pos_marker.templated_slice,
                patch_category="literal",
                fixed_raw=self.raw,
                templated_str=templated_file.templated_str[
                    self.pos_marker.templated_slice
                ],
                source_str=templated_file.source_str[self.pos_marker.source_slice],
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
            for segment in segments:
                # First check for insertions.
                # At this stage, everything should have a position.
                assert segment.pos_marker
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
                # Deletions in this sense could also mean source consumption.
                start_diff = segment.pos_marker.templated_slice.start - templated_idx

                # Check to see whether there's a discontinuity before the current
                # segment
                if start_diff > 0 or insert_buff:
                    # If we have an insert buffer, then it's an edit, otherwise a
                    # deletion.

                    # For the start of the next segment, we need the position of the
                    # first raw, not the pos marker of the whole thing. That accounts
                    # better for loops.
                    first_segment_pos = segment.raw_segments[0].pos_marker
                    yield FixPatch(
                        # Whether the source slice is zero depends on the start_diff.
                        # A non-zero start diff implies a deletion, or more likely
                        # a consumed element of the source. We can use the tracking
                        # markers from the last segment to recreate where this element
                        # should be inserted in both source and template.
                        source_slice=slice(
                            source_idx,
                            first_segment_pos.source_slice.start,
                        ),
                        templated_slice=slice(
                            templated_idx,
                            first_segment_pos.templated_slice.start,
                        ),
                        patch_category="mid_point",
                        fixed_raw=insert_buff,
                        templated_str="",
                        source_str="",
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
    ) -> BaseSegment:
        """Stub."""
        raise NotImplementedError()


class UnparsableSegment(BaseSegment):
    """This is a segment which can't be parsed. It indicates a error during parsing."""

    type = "unparsable"
    # From here down, comments are printed separately.
    comment_separate = True
    _expected = ""

    def __init__(
        self,
        segments: Tuple[BaseSegment, ...],
        pos_marker: Optional[PositionMarker] = None,
        expected: str = "",
    ) -> None:
        self._expected = expected
        super().__init__(segments=segments, pos_marker=pos_marker)

    def _suffix(self) -> str:
        """Return any extra output required at the end when logging.

        NB Override this for specific subclasses if we want extra output.
        """
        return f"!! Expected: {self._expected!r}"

    def iter_unparsables(self) -> Iterator["UnparsableSegment"]:
        """Iterate through any unparsables.

        As this is an unparsable, it should yield itself.
        """
        yield self
