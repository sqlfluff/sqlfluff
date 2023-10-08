"""Defines the Parser class."""

from typing import TYPE_CHECKING, Optional, Sequence, Type

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.helpers import check_still_complete

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.segments import BaseFileSegment, BaseSegment


class Parser:
    """Instantiates parsed queries from a sequence of lexed raw segments."""

    def __init__(
        self, config: Optional[FluffConfig] = None, dialect: Optional[str] = None
    ):
        # Allow optional config and dialect
        self.config = FluffConfig.from_kwargs(config=config, dialect=dialect)
        self.RootSegment: Type[BaseFileSegment] = self.config.get(
            "dialect_obj"
        ).get_root_segment()

    def parse(
        self,
        segments: Sequence["BaseSegment"],
        fname: Optional[str] = None,
        parse_statistics: bool = False,
    ) -> Optional["BaseSegment"]:
        """Parse a series of lexed tokens using the current dialect."""
        if not segments:  # pragma: no cover
            # This should normally never happen because there will usually
            # be an end_of_file segment. It would probably only happen in
            # api use cases.
            return None

        # NOTE: This is the only time we use the parse context not in the
        # context of a context manager. That's because it's the initial
        # instantiation.
        ctx = ParseContext.from_config(config=self.config)
        # Kick off parsing with the root segment. The BaseFileSegment has
        # a unique entry point to facilitate exaclty this. All other segments
        # will use the standard .match() route.
        root = self.RootSegment.root_parse(
            tuple(segments), fname=fname, parse_context=ctx
        )

        # Basic Validation, that we haven't dropped anything.
        check_still_complete(tuple(segments), (root,), ())

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

        return root
