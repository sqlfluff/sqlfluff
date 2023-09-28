"""The KeywordSegment class."""

from typing import List, Optional, Tuple

from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments.base import SourceFix
from sqlfluff.core.parser.segments.common import WordSegment


class KeywordSegment(WordSegment):
    """A segment used for matching single words.

    We rename the segment class here so that descendants of
    _ProtoKeywordSegment can use the same functionality
    but don't end up being labelled as a `keyword` later.
    """

    type = "keyword"

    def __init__(
        self,
        raw: Optional[str] = None,
        pos_marker: Optional[PositionMarker] = None,
        instance_types: Tuple[str, ...] = (),
        source_fixes: Optional[List[SourceFix]] = None,
        trim_chars: Optional[Tuple[str, ...]] = None,
    ):
        """If no other name is provided we extrapolate it from the raw."""
        super().__init__(
            raw=raw,
            pos_marker=pos_marker,
            instance_types=instance_types,
            source_fixes=source_fixes,
        )

    def edit(
        self, raw: Optional[str] = None, source_fixes: Optional[List[SourceFix]] = None
    ) -> "KeywordSegment":
        """Create a new segment, with exactly the same position but different content.

        Returns:
            A copy of this object with new contents.

        Used mostly by fixes.

        NOTE: This *doesn't* copy the uuid. The edited segment is a new segment.

        """
        return self.__class__(
            raw=raw or self.raw,
            pos_marker=self.pos_marker,
            instance_types=self.instance_types,
            source_fixes=source_fixes or self.source_fixes,
        )


class LiteralKeywordSegment(KeywordSegment):
    """A keyword style literal segment.

    This should be used for things like NULL, NAN, TRUE & FALSE.

    Defined here for type inheritance.
    """

    type = "literal"
