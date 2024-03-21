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
from dataclasses import dataclass
from functools import cached_property
from io import StringIO
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    FrozenSet,
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
from uuid import uuid4

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.helpers import trim_non_code_segments
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.types import SimpleHintType

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.dialects import Dialect
    from sqlfluff.core.parser.segments.raw import RawSegment

# Instantiate the linter logger (only for use in methods involved with fixing.)
linter_logger = logging.getLogger("sqlfluff.linter")

TupleSerialisedSegment = Tuple[str, Union[str, Tuple["TupleSerialisedSegment", ...]]]
RecordSerialisedSegment = Dict[
    str, Union[None, str, "RecordSerialisedSegment", List["RecordSerialisedSegment"]]
]


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

    def __hash__(self) -> int:
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
        code_idxs (:obj:`tuple` of int): The indices which contain code.
    """

    segment: "BaseSegment"
    idx: int
    len: int
    code_idxs: Tuple[int, ...]


def _iter_base_types(
    new_type: Optional[str], bases: Tuple[Type["BaseSegment"]]
) -> Iterator[str]:
    """Iterate types for a new segment class.

    This is a helper method used within in the construction of
    SegmentMetaclass so that we can construct a frozenset directly
    off the results.
    """
    if new_type is not None:
        yield new_type
    for base in bases:
        yield from base._class_types


class SegmentMetaclass(type, Matchable):
    """The metaclass for segments.

    This metaclass provides pre-computed class attributes
    based on the defined attributes of specific classes.

    Segments as a *type* should also implement the Matchable
    interface too. Once instantiated they no longer need to
    but we should be able to treat the BaseSegment class
    as a Matchable interface.
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
        class_dict["_class_types"] = frozenset(_iter_base_types(added_type, bases))
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
    _class_types: ClassVar[FrozenSet[str]]  # NOTE: Set by SegmentMetaclass
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
    _parent_idx: Optional[int] = None

    def __init__(
        self,
        segments: Tuple["BaseSegment", ...],
        pos_marker: Optional[PositionMarker] = None,
        uuid: Optional[int] = None,
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

        assert not hasattr(self, "parse_grammar"), "parse_grammar is deprecated."

        self.pos_marker = pos_marker
        self.segments: Tuple["BaseSegment", ...] = segments
        # Tracker for matching when things start moving.
        # NOTE: We're storing the .int attribute so that it's swifter
        # for comparisons.
        self.uuid = uuid or uuid4().int

        self.set_as_parent(recurse=False)
        self.validate_non_code_ends()
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
            # NOTE: `.working_loc` is much more performant than creating
            # a new start point marker for comparison.
            and (self.pos_marker.working_loc == other.pos_marker.working_loc)
        )

    @cached_property
    def _hash(self) -> int:
        """Cache the hash property to avoid recalculating it often."""
        return hash(
            (
                self.__class__.__name__,
                self.raw,
                # NOTE: We use the start of the source slice because it's
                # the lowest cost way of getting a reliable location in the source
                # file for deduplication.
                self.pos_marker.source_slice.start if self.pos_marker else None,
            )
        )

    def __hash__(self) -> int:
        return self._hash

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
    def class_types(self) -> FrozenSet[str]:
        """The set of types for this segment."""
        # NOTE: This version is simple, but some dependent classes
        # (notably RawSegment) override this with something more
        # custom.
        return self._class_types

    @cached_property
    def descendant_type_set(self) -> FrozenSet[str]:
        """The set of all contained types.

        This is used for rule crawling.

        NOTE: Does not include the types of the parent segment itself.
        """
        return frozenset(
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
            new_step = [PathStep(self, idx, len(self.segments), self._code_indices)]
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
    def _position_segments(
        cls,
        segments: Tuple["BaseSegment", ...],
        parent_pos: PositionMarker,
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
        assert segments, "_position_segments called on empty sequence."
        line_no = parent_pos.working_line_no
        line_pos = parent_pos.working_line_pos

        # Use the index so that we can look forward
        # and backward.
        segment_buffer: Tuple["BaseSegment", ...] = ()
        for idx, segment in enumerate(segments):
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
                elif end_point:  # pragma: no cover
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
                assert new_position
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
    def match(
        cls, segments: Sequence["BaseSegment"], idx: int, parse_context: ParseContext
    ) -> MatchResult:
        """Match a list of segments against this segment.

        Note: Match for segments is done in the ABSTRACT.
        When dealing with concrete then we're always in parse.
        Parse is what happens during expand.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        if idx >= len(segments):  # pragma: no cover
            return MatchResult.empty_at(idx)

        # Is this already the right kind of segment?
        if isinstance(segments[idx], cls):
            # Very simple "consume one" result.
            return MatchResult(slice(idx, idx + 1))

        assert cls.match_grammar, f"{cls.__name__} has no match grammar."

        with parse_context.deeper_match(name=cls.__name__) as ctx:
            match = cls.match_grammar.match(segments, idx, ctx)

        # Wrap are return regardless of success.
        return match.wrap(cls)

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
            "_hash",
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
        for idx, seg in enumerate(self.segments):
            seg.set_parent(self, idx)
            # Recurse if not disabled
            if recurse:
                seg.set_as_parent(recurse=recurse)

    def set_parent(self, parent: "BaseSegment", idx: int) -> None:
        """Set the weak reference to the parent.

        We keep a reference to the index within the parent too as that
        is often used at the same point in the operation.

        NOTE: Don't validate on set, because we might not have fully
        initialised the parent yet (because we call this method during
        the instantiation of the parent).
        """
        self._parent = weakref.ref(parent)
        self._parent_idx = idx

    def get_parent(self) -> Optional[Tuple["BaseSegment", int]]:
        """Get the parent segment, with some validation.

        This is provided as a performance optimisation when searching
        through the syntax tree. Any methods which depend on this should
        have an alternative way of assessing position, and ideally also
        set the parent of any segments found without them. As a performance
        optimisation, we also store the index of the segment within the
        parent to avoid needing to recalculate that.

        NOTE: We only store a weak reference to the parent so it might
        not be present. We also validate here that it's _still_ the parent
        and potentially also return None if those checks fail.
        """
        if not self._parent:
            return None
        _parent = self._parent()
        if not _parent or self not in _parent.segments:
            return None
        assert self._parent_idx is not None
        return _parent, self._parent_idx

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
        assert self.pos_marker, f"{self} has no PositionMarker"
        return self.pos_marker.start_point_marker()

    def get_end_point_marker(self) -> PositionMarker:
        """Get a point marker at the end of this segment."""
        assert self.pos_marker, f"{self} has no PositionMarker"
        return self.pos_marker.end_point_marker()

    def get_start_loc(self) -> Tuple[int, int]:
        """Get a location tuple at the start of this segment."""
        assert self.pos_marker, f"{self} has no PositionMarker"
        return self.pos_marker.working_loc

    def get_end_loc(self) -> Tuple[int, int]:
        """Get a location tuple at the end of this segment."""
        assert self.pos_marker, f"{self} has no PositionMarker"
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
        self,
        segments: Optional[Tuple["BaseSegment", ...]] = None,
        parent: Optional["BaseSegment"] = None,
        parent_idx: Optional[int] = None,
    ) -> "BaseSegment":
        """Copy the segment recursively, with appropriate copying of references.

        Optionally provide child segments which have already been dealt
        with to avoid another copy operation.

        NOTE: In the copy operation it's really important that we get
        a clean segregation so that we can't go backward and mutate the
        source object, but at the same time we should be mindful of what
        _needs_ to be copied to avoid a deep copy where one isn't required.
        """
        cls = self.__class__
        new_segment = cls.__new__(cls)
        # Position markers are immutable, and it's important that we keep
        # a reference to the same TemplatedFile, so keep the same position
        # marker. By updating from the source dict, we achieve that.
        # By using the __dict__ object we also transfer the _cache_ too
        # which is stored there by @cached_property.
        new_segment.__dict__.update(self.__dict__)

        # Reset the parent if provided.
        if parent:
            assert parent_idx is not None, "parent_idx must be provided it parent is."
            new_segment.set_parent(parent, parent_idx)

        # If the segment doesn't have a segments property, we're done.
        # NOTE: This is a proxy way of understanding whether it's a RawSegment
        # of not. Typically will _have_ a `segments` attribute, but it's an
        # empty tuple.
        if not self.__dict__.get("segments", None):
            assert (
                not segments
            ), f"Cannot provide `segments` argument to {cls.__name__} `.copy()`\n"
        # If segments were provided, use them.
        elif segments:
            new_segment.segments = segments
        # Otherwise we should handle recursive segment coping.
        # We use the native .copy() method (this method!) appropriately
        # so that the same logic is applied in recursion.
        # We set the parent for children directly on the copy method
        # to ensure those line up properly.
        else:
            new_segment.segments = tuple(
                seg.copy(parent=new_segment, parent_idx=idx)
                for idx, seg in enumerate(self.segments)
            )

        return new_segment

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
            _seg, _idx = _higher
            # If the higher doesn't have a position we'll run into problems.
            # Check that in advance.
            assert _seg.pos_marker, (
                f"`path_to()` found segment {_seg} without position. "
                "This shouldn't happen post-parse."
            )
            lower_path.append(
                PathStep(
                    _seg,
                    _idx,
                    len(_seg.segments),
                    _seg._code_indices,
                )
            )
            midpoint = _seg
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
            seg.set_parent(self, idx)
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

    @staticmethod
    def _is_code_or_meta(segment: "BaseSegment") -> bool:
        return segment.is_code or segment.is_meta

    def validate_non_code_ends(self) -> None:
        """Validates the start and end of the sequence based on it's config.

        Most normal segments may *not* start or end with whitespace. Any
        surrounding whitespace should be within the outer segment containing
        this one.

        The exception is for segments which configure `can_start_end_non_code`
        for which not check is conducted.

        TODO: Check whether it's only `can_start_end_non_code` is only set for
        FileSegment, in which case - take away the config and just override
        this method for that segment.
        """
        if self.can_start_end_non_code:
            return None
        if not self.segments:  # pragma: no cover
            return None
        assert self._is_code_or_meta(self.segments[0]), (
            f"Segment {self} starts with whitespace segment: "
            f"{self.segments[0].raw!r}.\n{self.segments!r}"
        )
        assert self._is_code_or_meta(self.segments[-1]), (
            f"Segment {self} ends with whitespace segment: "
            f"{self.segments[-1].raw!r}.\n{self.segments!r}"
        )

    def validate_segment_with_reparse(
        self,
        dialect: "Dialect",
    ) -> bool:
        """Checks correctness of new segment by re-parsing it."""
        ctx = ParseContext(dialect=dialect)
        # We're going to check the rematch without any metas because the
        # matching routines will assume they haven't already been added.
        # We also strip any non-code from the ends which might have moved.
        raw_content = tuple(s for s in self.raw_segments if not s.is_meta)
        _, trimmed_content, _ = trim_non_code_segments(raw_content)
        if not trimmed_content and self.can_start_end_non_code:
            # Edge case for empty segments which are allowed to be empty.
            return True
        rematch = self.match(trimmed_content, 0, ctx)
        if not rematch.matched_slice == slice(0, len(trimmed_content)):
            linter_logger.debug(
                f"Validation Check Fail for {self}.Incomplete Match. "
                f"\nMatched: {rematch.apply(trimmed_content)}. "
                f"\nUnmatched: {trimmed_content[rematch.matched_slice.stop:]}."
            )
            return False
        opening_unparsables = set(self.recursive_crawl("unparsable"))
        closing_unparsables: Set[BaseSegment] = set()
        new_segments = rematch.apply(trimmed_content)
        for seg in new_segments:
            closing_unparsables.update(seg.recursive_crawl("unparsable"))
        # Check we don't introduce any _additional_ unparsables.
        # Pre-existing unparsables are ok, and for some rules that's as
        # designed. The idea is that we shouldn't make the situation _worse_.
        if opening_unparsables >= closing_unparsables:
            return True

        linter_logger.debug(
            f"Validation Check Fail for {self}.\nFound additional Unparsables: "
            f"{closing_unparsables - opening_unparsables}"
        )
        for unparsable in closing_unparsables - opening_unparsables:
            linter_logger.debug(f"Unparsable:\n{unparsable.stringify()}\n")
        return False

    @staticmethod
    def _log_apply_fixes_check_issue(
        message: str, *args: Any
    ) -> None:  # pragma: no cover
        linter_logger.critical(message, exc_info=True, *args)

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
    # Unparsable segments could contain anything.
    can_start_end_non_code = True
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
