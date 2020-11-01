"""Classes to help with match logging."""

from .helpers import join_segments_raw_curtailed


class ParseMatchLogObject:
    """A late binding log object for parse_match_logging.

    This allows us to defer the string manipulation involved
    until actually required by the logger.
    """

    __slots__ = [
        "parse_depth",
        "match_depth",
        "match_segment",
        "grammar",
        "func",
        "msg",
        "kwargs",
    ]

    def __init__(
        self, parse_depth, match_depth, match_segment, grammar, func, msg, **kwargs
    ):
        self.parse_depth = parse_depth
        self.match_depth = match_depth
        self.match_segment = match_segment
        self.grammar = grammar
        self.func = func
        self.msg = msg
        self.kwargs = kwargs

    @classmethod
    def from_context(cls, parse_context, grammar, func, msg, **kwargs):
        """Create a ParseMatchLogObject given a parse_context."""
        return cls(
            parse_context.parse_depth,
            parse_context.match_depth,
            parse_context.match_segment,
            grammar,
            func,
            msg,
            **kwargs
        )

    def __str__(self):
        """Actually materialise the string."""
        symbol = self.kwargs.pop("symbol", "")
        s = "[PD:{0:<2} MD:{1:<2}]\t{2:<50}\t{3:<20}\t{4:<4}".format(
            self.parse_depth,
            self.match_depth,
            ("." * self.match_depth) + str(self.match_segment),
            "{0:.5}.{1} {2}".format(self.grammar, self.func, self.msg),
            symbol,
        )
        if self.kwargs:
            s += "\t[{0}]".format(
                ", ".join(
                    "{0}={1}".format(k, repr(v) if isinstance(v, str) else str(v))
                    for k, v in self.kwargs.items()
                )
            )
        return s


def parse_match_logging(grammar, func, msg, parse_context, v_level, **kwargs):
    """Log in a particular consistent format for use while matching."""
    # Make a late bound log object so we only do the string manipulation when we need to.
    log_obj = ParseMatchLogObject.from_context(
        parse_context, grammar, func, msg, **kwargs
    )
    # Otherwise carry on...
    if v_level == 3:
        parse_context.logger.info(log_obj)
    elif v_level == 4:
        parse_context.logger.debug(log_obj)


class LateBoundJoinSegmentsCurtailed:
    """Object to delay `join_segments_raw_curtailed` until later.

    This allows us to defer the string manipulation involved
    until actually required by the logger.
    """

    def __init__(self, segments):
        self.segments = segments

    def __str__(self):
        return repr(join_segments_raw_curtailed(self.segments))
