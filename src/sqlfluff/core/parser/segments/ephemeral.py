"""Ephemeral segment definitions."""

import copy
from typing import Optional

from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.segments.base import BaseSegment


class EphemeralSegment(BaseSegment):
    """A segment which acts like a normal segment, but is ephemeral.

    This segment allows grammars to behave like segments. It behaves like
    a normal segment except that during the `parse` step, it returns its
    contents rather than itself. This means in the final parsed structure
    it no longer exists.
    """

    type = "ephemeral"

    def __init__(self, segments, pos_marker, parse_grammar, name: Optional[str] = None):
        # Stash the parse grammar for now.
        self._parse_grammar = parse_grammar
        super().__init__(segments, pos_marker=pos_marker, name=name)

    @property
    def is_expandable(self):
        """Ephemeral segments are always expandable.

        They should dissolve after expansion. So if it exists, it's expandable.
        We need to redefine this here because the usual introspection doesn't
        handle the custom parse_grammar properly.
        """
        return True

    def parse(self, parse_context):
        """Use the parse grammar to find subsegments within this segment.

        Return the content of the result, rather than itself.
        """
        # Call the usual parse function, but overriding the parse grammar.
        new_self = super().parse(parse_context, parse_grammar=self._parse_grammar)
        # Return the content of that result rather than self
        return new_self.segments


def allow_ephemeral(func):
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

    def wrapped_match_method(self, segments: tuple, parse_context):
        """A wrapper on the match function to do some basic validation."""
        # Use the ephemeral_segment if present. This should only
        # be the case for grammars where `ephemeral_name` is defined.
        if self.ephemeral_name:
            # We're going to return as though it's a full match, similar to Anything().
            new_grammar = copy.copy(self)
            # Reset the ephemeral name on the new version of the grammar otherwise
            # we get infinite recursion.
            new_grammar.ephemeral_name = None
            # We shouldn't allow nested ephemerals. If they're present, don't create another.
            # This can happen when grammars call super() on their match method.
            if len(segments) == 1 and segments[0].is_type("ephemeral"):
                return MatchResult.from_matched(segments)
            else:
                return MatchResult.from_matched(
                    (
                        EphemeralSegment(
                            segments=segments,
                            pos_marker=None,
                            # Ephemeral segments get a copy of the parent grammar.
                            parse_grammar=new_grammar,
                            name=self.ephemeral_name,
                        ),
                    )
                )
        else:
            # Otherwise carry on through with wrapping the function.
            return func(self, segments, parse_context=parse_context)

    return wrapped_match_method
