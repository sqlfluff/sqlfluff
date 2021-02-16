"""Classes to help with match logging."""

from sqlfluff.core.parser.helpers import join_segments_raw_curtailed


class LateLoggingObject(object):
    """A basic late binding log object for parse_match_logging.

    This allows us to defer the string manipulation involved
    until actually required by the logger.
    """

    __slots__ = "v_level", "logger", "msg"

    def __init__(self, logger, msg, v_level=3):
        self.v_level = v_level
        self.logger = logger
        self.msg = msg

    def __str__(self):
        """Actually materialise the string."""
        return self.msg

    def log(self):
        """Actually log this object."""
        # Otherwise carry on...
        if self.v_level == 3:
            self.logger.info(self)
        elif self.v_level == 4:
            self.logger.debug(self)


class ParseMatchLogObject(LateLoggingObject):
    """A late binding log object for parse_match_logging.

    This allows us to defer the string manipulation involved
    until actually required by the logger.
    """

    __slots__ = [
        "context",
        "grammar",
        "func",
        "kwargs",
    ]

    def __init__(self, parse_context, grammar, func, msg, v_level=3, **kwargs):
        super().__init__(v_level=v_level, logger=parse_context.logger, msg=msg)
        self.context = parse_context
        self.grammar = grammar
        self.func = func
        self.kwargs = kwargs

    def __str__(self):
        """Actually materialise the string."""
        symbol = self.kwargs.pop("symbol", "")
        s = "[PD:{0:<2} MD:{1:<2}]\t{2:<50}\t{3:<20}\t{4:<4}".format(
            self.context.parse_depth,
            self.context.match_depth,
            ("." * self.context.match_depth) + str(self.context.match_segment),
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


def parse_match_logging(grammar, func, msg, parse_context, v_level=3, **kwargs):
    """Log in a particular consistent format for use while matching."""
    # Make a late bound log object so we only do the string manipulation when we need to.
    ParseMatchLogObject(
        parse_context, grammar, func, msg, v_level=v_level, **kwargs
    ).log()


class LateBoundJoinSegmentsCurtailed:
    """Object to delay `join_segments_raw_curtailed` until later.

    This allows us to defer the string manipulation involved
    until actually required by the logger.
    """

    def __init__(self, segments):
        self.segments = segments

    def __str__(self):
        return repr(join_segments_raw_curtailed(self.segments))
