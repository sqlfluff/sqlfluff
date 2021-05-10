"""Conditional Grammar."""

from sqlfluff.core.parser.segments import Indent
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper

from sqlfluff.core.parser.grammar.base import (
    BaseGrammar,
)


class Conditional(BaseGrammar):
    """A grammar which is conditional on the parse context.

    Args:
        enforce_whitespace_preceeding (:obj:`bool`): Should the GreedyUntil
            match only match the content if it's preceded by whitespace?
            (defaults to False). This is useful for some keywords which may
            have false alarms on some array accessors.

    """

    def __init__(self, *args, config_type: str = "", **kwargs):
        if not all(issubclass(arg, Indent) for arg in args):
            raise ValueError(
                "Conditional is only designed to work with Indent segments."
            )
        if len(args) != 1:
            raise ValueError(
                "Conditional is only designed to work with a single element."
            )
        if not config_type:
            raise ValueError("Conditional config_type must be set.")
        if not kwargs:
            raise ValueError("Conditional requires rules to be set.")
        self._config_type = config_type
        self._config_rules = kwargs
        super().__init__(*args)

    def is_enabled(self, parse_context):
        """Evaluate conditionals and return whether enabled."""
        # If no config rules are set then it's always enabled.
        try:
            config = {"indent": parse_context.indentation_config}[self._config_type]
        except KeyError:
            raise ValueError(
                "Conditional: unknown config_type: {0}".format(self._config_type)
            )

        # If any rules fail, return no match.
        for rule, val in self._config_rules.items():
            # Assume False if not set.
            conf_val = config.get(rule, False)
            # Coerce to boolean.
            if val != bool(conf_val):
                return False
        return True

    @match_wrapper()
    def match(self, segments, parse_context):
        """Evaluate conditionals and return content."""
        if not self.is_enabled(parse_context):
            return MatchResult.from_unmatched(segments)

        # Instantiate the new element and return
        new_seg = self._elements[0]()
        return MatchResult((new_seg,), segments)
