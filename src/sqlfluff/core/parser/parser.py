"""Defines the Parser class."""

from typing import Optional, Sequence, TYPE_CHECKING

from sqlfluff.core.parser.context import RootParseContext
from sqlfluff.core.config import FluffConfig
import sys

if TYPE_CHECKING:
    from sqlfluff.core.parser.segments import BaseSegment  # pragma: no cover


class Parser:
    """Instantiates parsed queries from a sequence of lexed raw segments."""

    def __init__(
        self, config: Optional[FluffConfig] = None, dialect: Optional[str] = None
    ):
        # Allow optional config and dialect
        self.config = FluffConfig.from_kwargs(config=config, dialect=dialect)
        self.RootSegment = self.config.get("dialect_obj").get_root_segment()

    def parse(
        self,
        segments: Sequence["BaseSegment"],
        recurse=True,
        fname: Optional[str] = None,
    ) -> Optional["BaseSegment"]:
        """Parse a series of lexed tokens using the current dialect."""
        if not segments:  # pragma: no cover
            # This should normally never happen because there will usually
            # be an end_of_file segment. It would probably only happen in
            # api use cases.
            return None
        # Instantiate the root segment
        root_segment = self.RootSegment(segments=segments, fname=fname)
        # Call .parse() on that segment

        # Temporarily increase the Python recursion limit to 10,000.  This helps
        # deal with recursion errors when parsing recursive segments like expressions.
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, 10000))
        try:
            with RootParseContext.from_config(
                config=self.config, recurse=recurse
            ) as ctx:
                parsed = root_segment.parse(parse_context=ctx)
        finally:
            sys.setrecursionlimit(old_limit)

        return parsed
