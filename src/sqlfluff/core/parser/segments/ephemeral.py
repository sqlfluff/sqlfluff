"""Ephemeral segment definitions."""

import copy
import logging
from typing import TYPE_CHECKING, Optional, Tuple

from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import MatchFuncType
from sqlfluff.core.parser.segments.base import BaseSegment

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.context import ParseContext
    from sqlfluff.core.parser.grammar.base import BaseGrammar
    from sqlfluff.core.parser.markers import PositionMarker
    from sqlfluff.core.parser.matchable import Matchable


parser_logger = logging.getLogger("sqlfluff.parser")


class EphemeralSegment(BaseSegment):
    """A segment which acts like a normal segment, but is ephemeral.

    This segment allows grammars to behave like segments. It behaves like
    a normal segment except that during the `parse` step, it returns its
    contents rather than itself. This means in the final parsed structure
    it no longer exists.
    """

    type = "ephemeral"

    def __init__(
        self,
        segments: Tuple[BaseSegment, ...],
        pos_marker: Optional["PositionMarker"],
        parse_grammar: "Matchable",
        ephemeral_name: str,
    ):
        # Stash the parse grammar for now.
        self._parse_grammar = parse_grammar
        self.ephemeral_name = ephemeral_name
        super().__init__(segments, pos_marker=pos_marker)

    @property
    def expected_form(self) -> str:
        """What to return to the user when unparsable."""
        return self.ephemeral_name

    @property
    def is_expandable(self) -> bool:
        """Ephemeral segments are always expandable.

        They should dissolve after expansion. So if it exists, it's expandable.
        We need to redefine this here because the usual introspection doesn't
        handle the custom parse_grammar properly.
        """
        return True

    def parse(
        self, parse_context: "ParseContext", parse_grammar: Optional["Matchable"] = None
    ) -> Tuple[BaseSegment, ...]:
        """Use the parse grammar to find subsegments within this segment.

        Return the content of the result, rather than itself.
        """
        # Call the usual parse function, but overriding the parse grammar.
        parsed_segments = super().parse(
            parse_context, parse_grammar=self._parse_grammar
        )

        # Check we only got a result of length 1.
        assert len(parsed_segments) == 1
        # Return the content of that result rather than self
        return parsed_segments[0].segments


def allow_ephemeral(func: MatchFuncType) -> MatchFuncType:
    """Wraps a .match() method to the option of ephemeral matching for grammars.

    This is designed to be used as follows:

        class SomeMatchableObject(object):
            @match_wrapper()
            @allow_ephemeral
            def match(self, segments, parse_context):
                ...
                return m

    NOTE: This should come inside the match_wrapper.
    """

    def wrapped_match_method(
        self: "BaseGrammar",
        segments: Tuple[BaseSegment, ...],
        parse_context: "ParseContext",
    ) -> MatchResult:
        """A wrapper on the match function to do some basic validation."""
        # Use the ephemeral_segment if present. This should only
        # be the case for grammars where `ephemeral_name` is defined.
        if self.ephemeral_name:
            # We're going to return as though it's a full match, similar to Anything().
            new_grammar = copy.copy(self)
            # Reset the ephemeral name on the new version of the grammar otherwise
            # we get infinite recursion.
            new_grammar.ephemeral_name = None
            # We shouldn't allow nested ephemerals. If they're present, don't create
            # another. This can happen when grammars call super() on their match method.
            if len(segments) == 1 and segments[0].is_type("ephemeral"):
                parser_logger.debug(
                    "Developer Note: Nested ephemeral segments found. This "
                    "is an anti-pattern: Consider alternative implementation."
                )  # pragma: no cover
                return MatchResult.from_matched(segments)  # pragma: no cover
            else:
                return MatchResult.from_matched(
                    (
                        EphemeralSegment(
                            segments=segments,
                            pos_marker=None,
                            # Ephemeral segments get a copy of the parent grammar.
                            parse_grammar=new_grammar,
                            ephemeral_name=self.ephemeral_name,
                        ),
                    )
                )
        else:
            # Otherwise carry on through with wrapping the function.
            return func(self, segments, parse_context)

    return wrapped_match_method
