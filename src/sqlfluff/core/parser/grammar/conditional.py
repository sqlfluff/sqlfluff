"""Conditional Grammar."""

from typing import Sequence, Type, Union

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.base import BaseGrammar
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.segments import BaseSegment, Indent


class Conditional(BaseGrammar):
    """A grammar which is conditional on the parse context.

    | NOTE: The Conditional grammar is assumed to be operating
    | within a Sequence grammar, and some of the functionality
    | may not function within a different context.

    Args:
        *args: A meta segment which is instantiated
            conditionally upon the rules set.
        config_type: The area of the config that is used
            when evaluating the status of the given rules.
        rules: A set of `rule=boolean` pairs, which are
            evaluated when understanding whether conditions
            are met for this grammar to be enabled.

    Example:
        .. code-block:: python

            Conditional(Dedent, config_type="indent", indented_joins=False)

        This effectively says that if `indented_joins` in the "indent" section
        of the current config is set to `True`, then this grammar will allow
        a `Dedent` segment to be matched here. If `indented_joins` is set to
        `False`, it will be as though there was no `Dedent` in this sequence.

    | NOTE: While the Conditional grammar is set up to allow different
    | sources of configuration, it relies on configuration keys being
    | available within the ParseContext. Practically speaking only the
    | "indentation" keys are currently set up.
    """

    def __init__(
        self,
        meta: Type[Indent],
        config_type: str = "indentation",
        **rules: Union[str, bool],
    ):
        """Initialize a new instance of the class.

        This method initializes an instance of the class with the provided
        arguments.

        Args:
            meta (Type[Indent]): The meta argument.
            config_type (str, optional): The config_type argument. Defaults to
                "indentation".
            **rules (Union[str, bool]): The rules argument.
        """
        assert issubclass(
            meta, Indent
        ), "Conditional is only designed to work with Indent/Dedent segments."
        self._meta = meta
        if not config_type:  # pragma: no cover
            raise ValueError("Conditional config_type must be set.")
        elif config_type not in ("indentation"):  # pragma: no cover
            raise ValueError(
                "Only 'indentation' is supported as a Conditional config_type."
            )
        if not rules:  # pragma: no cover
            raise ValueError("Conditional requires rules to be set.")
        self._config_type = config_type
        self._config_rules = rules
        super().__init__()

    def is_enabled(self, parse_context: ParseContext) -> bool:
        """Evaluate conditionals and return whether enabled."""
        # NOTE: Because only "indentation" is the only current config_type
        # supported, this code is much simpler that would be required in
        # future if multiple options are available.
        if self._config_type != "indentation":  # pragma: no cover
            raise ValueError(
                "Only 'indentation' is supported as a Conditional config_type."
            )
        config_section = parse_context.indentation_config
        # If any rules fail, return no match.
        for rule, val in self._config_rules.items():
            # Assume False if not set.
            conf_val = config_section.get(rule, False)
            # Coerce to boolean.
            if val != bool(conf_val):
                return False
        return True

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """If enabled, return a single insert of the new segment."""
        if not self.is_enabled(parse_context):
            return MatchResult.empty_at(idx)

        return MatchResult(
            matched_slice=slice(idx, idx), insert_segments=((idx, self._meta),)
        )
