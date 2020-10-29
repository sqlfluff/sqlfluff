"""Defines the Parser class."""

from .context import RootParseContext


class Parser:
    """Instantiates parsed queries from a sequence of lexed raw segments."""

    def __init__(self, config):
        # config is required - we use it to get the dialect
        self.config = config
        self.RootSegment = config.get("dialect_obj").get_root_segment()

    def parse(self, segments, recurse=True):
        """Parse a series of lexed tokens using the current dialect."""
        # Instantiate the root segment
        root_segment = self.RootSegment(segments=segments)
        # Call .parse() on that segment
        with RootParseContext.from_config(config=self.config, recurse=recurse) as ctx:
            parsed = root_segment.parse(parse_context=ctx)
        return parsed
