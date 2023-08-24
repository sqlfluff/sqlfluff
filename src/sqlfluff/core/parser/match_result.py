"""Source for the MatchResult class.

This should be the default response from any `match` method.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    DefaultDict,
    List,
    Optional,
    Tuple,
    Type,
    TYPE_CHECKING,
    cast,
)

from sqlfluff.core.parser.helpers import join_segments_raw, trim_non_code_segments
from sqlfluff.core.slice_helpers import slice_length

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.segments import BaseSegment, MetaSegment


@dataclass(frozen=True)
class MatchResult:
    """This should be the default response from any `match` method.

    Args:
        matched_segments (:obj:`tuple`): A tuple of the segments which have been
            matched in this matching operation.
        unmatched_segments (:obj:`tuple`): A tuple of the segments, which come after
            the `matched_segments` which could not be matched.

    """

    matched_segments: Tuple["BaseSegment", ...] = ()
    unmatched_segments: Tuple["BaseSegment", ...] = ()

    @property
    def trimmed_matched_length(self) -> int:
        """Return the length of the match in characters, trimming whitespace."""
        _, segs, _ = trim_non_code_segments(self.matched_segments)
        return sum(seg.matched_length for seg in segs)

    def all_segments(self) -> Tuple["BaseSegment", ...]:
        """Return a tuple of all the segments, matched or otherwise."""
        return self.matched_segments + self.unmatched_segments

    def __len__(self) -> int:
        return len(self.matched_segments)

    def is_complete(self) -> bool:
        """Return true if everything has matched.

        Note: An empty match is not a match so will return False.
        """
        return len(self.unmatched_segments) == 0 and len(self.matched_segments) > 0

    def has_match(self) -> bool:
        """Return true if *anything* has matched."""
        return len(self) > 0

    def __bool__(self) -> bool:
        return self.has_match()

    def raw_matched(self) -> str:
        """Make a string from the raw matched segments."""
        return join_segments_raw(self.matched_segments)

    def __str__(self) -> str:
        content = self.raw_matched()
        # Clip the content if it's long.
        # The ends are the important bits.
        if len(content) > 32:
            content = content[:15] + "..." + content[-15:]
        return "<MatchResult {}/{}: {!r}>".format(
            len(self.matched_segments),
            len(self.matched_segments) + len(self.unmatched_segments),
            content,
        )

    @classmethod
    def from_unmatched(cls, unmatched: Tuple["BaseSegment", ...]) -> "MatchResult":
        """Construct a `MatchResult` from just unmatched segments."""
        return cls(matched_segments=(), unmatched_segments=unmatched)

    @classmethod
    def from_matched(cls, matched: Tuple["BaseSegment", ...]) -> "MatchResult":
        """Construct a `MatchResult` from just matched segments."""
        return cls(unmatched_segments=(), matched_segments=matched)

    @classmethod
    def from_empty(cls) -> "MatchResult":
        """Construct an empty `MatchResult`."""
        return cls(unmatched_segments=(), matched_segments=())

    def __add__(self, other: Tuple["BaseSegment", ...]) -> "MatchResult":
        """Override add for concatenating tuples onto this match."""
        return self.__class__(
            matched_segments=self.matched_segments + other,
            unmatched_segments=self.unmatched_segments,
        )


@dataclass(frozen=True)
class MatchResult2:
    """This should be the NEW default response from any `match` method.

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
    child_matches: Tuple["MatchResult2", ...] = field(default_factory=tuple)
    # Is it clean? i.e. free of unparsable sections?
    is_clean: bool = True

    def __len__(self):
        return slice_length(self.matched_slice)

    def apply(self, segments: Tuple["BaseSegment", ...]) -> Tuple["BaseSegment", ...]:
        """Actually this match to segments to instantiate.

        This turns a theoretical match into a nested structure of segments.

        We handle child segments _first_ so that we can then include them when
        creating the parent. That means sequentially working through the children
        and any inserts. If there are overlaps, then we have a problem, and we
        should abort.
        """
        # Which are the locations we need to care about?
        trigger_locs: DefaultDict[
            int, List[MatchResult2, Type["MetaSegment"]]
        ] = defaultdict(list)
        # Add the inserts first...
        for insert in self.insert_segments:
            trigger_locs[insert[0]].append(insert[1])
        # ...and then the matches
        for match in self.child_matches:
            trigger_locs[match.matched_slice.start].append(match)

        # Then work through creating any subsegments.
        result_segments = ()
        max_idx = self.matched_slice.start
        for idx in sorted(trigger_locs.keys()):
            # Have we passed any untouched segments?
            if idx > max_idx:
                # If so, add them in unchanged.
                result_segments += segments[max_idx:idx]
            elif idx < max_idx:  # pragma: no cover
                raise ValueError("SKIP AHEAD ERROR")
            # Then work through each of the triggers.
            for trigger in trigger_locs[idx]:
                # If it's a segment, instantiate it.
                if isinstance(trigger, MatchResult2):
                    result_segments += trigger.apply(segments=segments)
                    # Update the end slice.
                    max_idx = trigger.matched_slice.stop
                    continue

                # Otherwise it's a segment.
                seg_type = cast("MetaSegment", trigger)
                result_segments += (seg_type(),)

        # If we finish working through the triggers and there's
        # still something left, then add that too.
        if max_idx < self.matched_slice.stop:
            result_segments += segments[max_idx : self.matched_slice.stop]

        if not self.matched_class:
            return result_segments

        # Otherwise construct the subsegment
        new_seg = self.matched_class(segments=result_segments, **self.segment_kwargs)
        return (new_seg,)

    def _to_old_match_result(self, segments):
        pass
