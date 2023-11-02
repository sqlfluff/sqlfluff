"""Source for the MatchResult class.

This should be the default response from any `match` method.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    DefaultDict,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
)

from sqlfluff.core.helpers.slice import slice_length
from sqlfluff.core.parser.markers import PositionMarker

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.segments import BaseSegment, MetaSegment, RawSegment


def _get_point_pos_at_idx(
    segments: Sequence["BaseSegment"], idx: int
) -> PositionMarker:
    if idx < len(segments):
        _next_pos = segments[idx].pos_marker
        assert _next_pos, "Segments passed to .apply() should all have position."
        return _next_pos.start_point_marker()
    else:
        _prev_pos = segments[idx - 1].pos_marker
        assert _prev_pos, "Segments passed to .apply() should all have position."
        return _prev_pos.end_point_marker()


@dataclass(frozen=True)
class MatchResult:
    """This should be the default response from any `match` method.

    All references and indices are in reference to a single root tuple
    of segments. This result contains enough information to actually
    create the nested tree structure, but shouldn't actually contain
    any new segments itself. That means keeping information about:
    1. Ranges of segments which should be included segments to be
       created.
    2. References to the segment classes which we would create.
    3. Information about any _new_ segments to add in the process,
       such as MetaSegment classes.

    Given the segments aren't yet "nested", the structure of this
    result *will* need to be nested, ideally self nested.

    In the case of finding unparsable locations, we should return the
    "best" result, referencing the furthest that we got. That allows
    us to identify those parsing issues and create UnparsableSegment
    classes later.
    """

    # Slice in the reference tuple
    matched_slice: slice
    # Reference to the kind of segment to create.
    # NOTE: If this is null, it means we've matched a sequence of segments
    # but not yet created a container to put them in.
    matched_class: Optional[Type["BaseSegment"]] = None
    # kwargs to pass to the segment on creation.
    segment_kwargs: Dict[str, Any] = field(default_factory=dict)
    # Types and indices to add in new segments (they'll be meta segments)
    insert_segments: Tuple[Tuple[int, Type["MetaSegment"]], ...] = field(
        default_factory=tuple
    )
    # Child segment matches (this is the recursive bit)
    child_matches: Tuple["MatchResult", ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Do some lightweight validation post instantiation."""
        if not slice_length(self.matched_slice):
            # Zero length matches with inserts are allowed, but not with
            # matched_class or child_matches.
            assert not self.matched_class, (
                "Tried to create zero length MatchResult with "
                "`matched_class`. This MatchResult is invalid. "
                f"{self.matched_class} @{self.matched_slice}"
            )
            assert not self.child_matches, (
                "Tried to create zero length MatchResult with "
                "`child_matches`. Is this allowed?! "
                f"Result: {self}"
            )

    def __len__(self) -> int:
        return slice_length(self.matched_slice)

    def __bool__(self) -> bool:
        """A MatchResult is truthy if it has length or inserts."""
        return len(self) > 0 or bool(self.insert_segments)

    def stringify(self, indent: str = "") -> str:
        """Pretty print a match for debugging."""
        prefix = f"Match ({self.matched_class}): {self.matched_slice}"
        buffer = prefix
        for key, value in self.segment_kwargs.items():
            buffer += f"\n  {indent}-{key}: {value!r}"
        if self.insert_segments:
            for idx, insert in self.insert_segments:
                buffer += f"\n  {indent}+{idx}: {insert}"
        if self.child_matches:
            for child in self.child_matches:
                buffer += f"\n  {indent}+{child.stringify(indent + '  ')}"
        return buffer

    @classmethod
    def empty_at(cls, idx: int) -> "MatchResult":
        """Create an empty match at a particular index."""
        return cls(slice(idx, idx))

    def is_better_than(self, other: "MatchResult") -> bool:
        """A match is better compared on length."""
        return len(self) > len(other)

    def append(
        self,
        other: "MatchResult",
        insert_segments: Tuple[Tuple[int, Type["MetaSegment"]], ...] = (),
    ) -> "MatchResult":
        """Combine another subsequent match onto this one.

        NOTE: Because MatchResult is frozen, this returns a new
        match.
        """
        # If the current match is empty, just return the other.
        if not len(self) and not self.insert_segments:
            return other
        # If the same is true of the other, just return self.
        if not len(other) and not other.insert_segments:
            return self  # pragma: no cover

        # Otherwise the two must follow each other.
        # NOTE: A gap is allowed, but is assumed to be included in the
        # match.
        assert self.matched_slice.stop <= other.matched_slice.start
        new_slice = slice(self.matched_slice.start, other.matched_slice.stop)
        child_matches: Tuple[MatchResult, ...] = ()
        for match in (self, other):
            # If it's got a matched class, add it as a child.
            if match.matched_class:
                child_matches += (match,)
            # Otherwise incorporate
            else:
                # Note: We're appending to the optional insert segments
                # provided in the kwargs.
                insert_segments += match.insert_segments
                child_matches += match.child_matches
        return MatchResult(
            new_slice,
            insert_segments=insert_segments,
            child_matches=child_matches,
        )

    def wrap(
        self,
        outer_class: Type["BaseSegment"],
        insert_segments: Tuple[Tuple[int, Type["MetaSegment"]], ...] = (),
        segment_kwargs: Dict[str, Any] = {},
    ) -> "MatchResult":
        """Wrap this result with an outer class.

        NOTE: Because MatchResult is frozen, this returns a new
        match.
        """
        # If it's a failed (empty) match, then just pass straight
        # through. It's not valid to add a matched class to an empty
        # result.
        if not slice_length(self.matched_slice) and not self.insert_segments:
            assert not insert_segments, "Cannot wrap inserts onto an empty match."
            return self

        child_matches: Tuple[MatchResult, ...]
        if self.matched_class:
            # If the match already has a class, then make
            # the current one and child match and clear the
            # other buffers.
            child_matches = (self,)
        else:
            # Otherwise flatten the existing match into
            # the new one.
            insert_segments = self.insert_segments + insert_segments
            child_matches = self.child_matches

        # Otherwise flatten the content
        return MatchResult(
            self.matched_slice,
            matched_class=outer_class,
            segment_kwargs=segment_kwargs,
            insert_segments=insert_segments,
            child_matches=child_matches,
        )

    def apply(self, segments: Tuple["BaseSegment", ...]) -> Tuple["BaseSegment", ...]:
        """Actually this match to segments to instantiate.

        This turns a theoretical match into a nested structure of segments.

        We handle child segments _first_ so that we can then include them when
        creating the parent. That means sequentially working through the children
        and any inserts. If there are overlaps, then we have a problem, and we
        should abort.
        """
        result_segments: Tuple["BaseSegment", ...] = ()
        if not slice_length(self.matched_slice):
            assert not self.matched_class, (
                "Tried to apply zero length MatchResult with "
                "`matched_class`. This MatchResult is invalid. "
                f"{self.matched_class} @{self.matched_slice}"
            )
            assert not self.child_matches, (
                "Tried to apply zero length MatchResult with "
                "`child_matches`. This MatchResult is invalid. "
                f"Result: {self}"
            )
            if self.insert_segments:
                assert segments, "Cannot insert segments without reference position."
                for idx, seg in self.insert_segments:
                    assert idx == self.matched_slice.start, (
                        f"Tried to insert @{idx} outside of matched "
                        f"slice {self.matched_slice}"
                    )
                    _pos = _get_point_pos_at_idx(segments, idx)
                    result_segments += (seg(pos_marker=_pos),)
            return result_segments

        assert len(segments) >= self.matched_slice.stop, (
            f"Matched slice ({self.matched_slice}) sits outside segment "
            f"bounds: {len(segments)}"
        )

        # Which are the locations we need to care about?
        trigger_locs: DefaultDict[
            int, List[Union[MatchResult, Type["MetaSegment"]]]
        ] = defaultdict(list)
        # Add the inserts first...
        for insert in self.insert_segments:
            trigger_locs[insert[0]].append(insert[1])
        # ...and then the matches
        for match in self.child_matches:
            trigger_locs[match.matched_slice.start].append(match)

        # Then work through creating any subsegments.
        max_idx = self.matched_slice.start
        for idx in sorted(trigger_locs.keys()):
            # Have we passed any untouched segments?
            if idx > max_idx:
                # If so, add them in unchanged.
                result_segments += segments[max_idx:idx]
                max_idx = idx
            elif idx < max_idx:  # pragma: no cover
                raise ValueError(
                    "Segment skip ahead error. An outer match contains "
                    "overlapping child matches. This MatchResult was "
                    "wrongly constructed."
                )
            # Then work through each of the triggers.
            for trigger in trigger_locs[idx]:
                # If it's a match, apply it.
                if isinstance(trigger, MatchResult):
                    result_segments += trigger.apply(segments=segments)
                    # Update the end slice.
                    max_idx = trigger.matched_slice.stop
                    continue

                # Otherwise it's a segment.
                # Get the location from the next segment unless there isn't one.
                _pos = _get_point_pos_at_idx(segments, idx)
                result_segments += (trigger(pos_marker=_pos),)

        # If we finish working through the triggers and there's
        # still something left, then add that too.
        if max_idx < self.matched_slice.stop:
            result_segments += segments[max_idx : self.matched_slice.stop]

        if not self.matched_class:
            return result_segments

        # Otherwise construct the subsegment
        new_seg: "BaseSegment"
        if self.matched_class.class_is_type("raw"):
            _raw_type = cast(Type["RawSegment"], self.matched_class)
            assert len(result_segments) == 1
            # TODO: Should this be a generic method on BaseSegment and RawSegment?
            # It feels a little strange to be this specific here.
            new_seg = _raw_type(
                raw=result_segments[0].raw,
                pos_marker=result_segments[0].pos_marker,
                **self.segment_kwargs,
            )
        else:
            new_seg = self.matched_class(
                segments=result_segments, **self.segment_kwargs
            )
        return (new_seg,)
