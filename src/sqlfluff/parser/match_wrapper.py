"""Defined the `match_wrapper` which adds validation and logging to match methods."""

from .match_logging import LateBoundJoinSegmentsCurtailed, parse_match_logging
from .match_result import MatchResult, is_segment


def match_wrapper(v_level=3):
    """Wraps a .match() method to add validation and logging.

    This is designed to be used as follows:

        class SomeMatchableObject(object):
            @match_wrapper()
            def match(self, segments, parse_context):
                ...
                return m

    This applies a common logging framework to both Grammar and
    Segment based match routines.
    """

    def inner_match_wrapper(func):
        """Decorate a match function."""

        def wrapped_match_method(self_cls, segments, parse_context):
            """A wrapper on the match function to do some basic validation."""
            # Type unification
            if is_segment(segments):
                segments = (segments,)
            elif isinstance(segments, list):
                segments = tuple(segments)
            elif not isinstance(segments, tuple):
                raise TypeError(
                    "{0} passed unacceptable segments of type {1}: {2}".format(
                        func.__qualname__, type(segments), segments
                    )
                )

            # Use the ephemeral_segment if present. This should only
            # be the case for grammars where `ephemeral_name` is defined.
            ephemeral_segment = getattr(self_cls, "ephemeral_segment", None)
            if ephemeral_segment:
                parse_match_logging(
                    func.__qualname__,
                    "_match",
                    "EPH",
                    parse_context=parse_context,
                    v_level=v_level,
                )
                # We're going to return as though it's a full match, similar to Anything().
                m = MatchResult.from_matched(ephemeral_segment(segments=segments))
            else:
                # Otherwise carry on through with wrapping the function.
                parse_match_logging(
                    func.__qualname__,
                    "_match",
                    "IN",
                    parse_context=parse_context,
                    v_level=v_level,
                    ls=len(segments),
                    # Log what we're matching.
                    # Work out the raw representation and curtail if long.
                    seg=LateBoundJoinSegmentsCurtailed(segments),
                )

                # Perform the inner matching operation.
                m = func(self_cls, segments, parse_context=parse_context)

            # Validate result
            if not isinstance(m, MatchResult):
                parse_context.logger.warning(
                    "{0}.match, returned {1} rather than MatchResult".format(
                        func.__qualname__, type(m)
                    )
                )

            # Log the result.
            if m.is_complete():
                msg = "OUT"
                symbol = "++"
            elif m:
                msg = "OUT"
                symbol = "+"
            else:
                msg = "OUT"
                symbol = ""
            parse_match_logging(
                func.__qualname__,
                "_match",
                msg,
                parse_context=parse_context,
                v_level=v_level,
                m=m,
                symbol=symbol,
            )
            # Basic Validation, skipped here because it still happens in the parse commands.
            return m

        return wrapped_match_method

    return inner_match_wrapper
