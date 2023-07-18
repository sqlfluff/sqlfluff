"""Defines the Parser class."""

from typing import Optional, Sequence, TYPE_CHECKING

from sqlfluff.core.parser.context import RootParseContext
from sqlfluff.core.config import FluffConfig

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
        parse_statistics: bool = False,
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

        with RootParseContext.from_config(config=self.config, recurse=recurse) as ctx:
            parsed = root_segment.parse(parse_context=ctx)

            if parse_statistics:  # pragma: no cover
                # NOTE: We use ctx.logger.warning here to output the statistics.
                # It's not particularly beautiful, but for the users who do utilise
                # this functionality, I don't think they mind. ¯\_(ツ)_/¯
                # In the future, this clause might become unnecessary.
                ctx.logger.warning("==== Parse Statistics ====")
                for key in ctx.parse_stats:
                    if key == "next_counts":
                        continue
                    ctx.logger.warning(f"{key}: {ctx.parse_stats[key]}")
                ctx.logger.warning("## Tokens following un-terminated matches")
                ctx.logger.warning(
                    "Adding terminator clauses to catch these may improve performance."
                )
                for key, val in sorted(
                    ctx.parse_stats["next_counts"].items(),
                    reverse=True,
                    key=lambda item: item[1],
                ):
                    ctx.logger.warning(f"{val}: {key!r}")
                ctx.logger.warning("==== End Parse Statistics ====")

        return parsed
