"""Implementation of Rule L029."""
from typing import Optional, List

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_configuration
from sqlfluff.rules.L014 import identifiers_policy_applicable


@document_configuration
class Rule_L029(BaseRule):
    """Keywords should not be used as identifiers.

    | **Anti-pattern**
    | In this example, ``SUM`` (built-in function) is used as an alias.

    .. code-block:: sql

        SELECT
            sum.a
        FROM foo AS sum

    | **Best practice**
    |  Avoid keywords as the name of an alias.

    .. code-block:: sql

        SELECT
            vee.a
        FROM foo AS vee

    """

    config_keywords = [
        "unquoted_identifiers_policy",
        "quoted_identifiers_policy",
        "ignore_words",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Keywords should not be used as identifiers."""
        # Get the Quoted policy configuration.
        try:
            ignore_words_list = self.ignore_words_list
        except AttributeError:
            # First-time only, read the settings from configuration. This is
            # very slow.
            ignore_words_list = self._init_ignore_string()

        # Skip if not an element of the specified type/name
        if ignore_words_list and context.segment.raw.lower() in ignore_words_list:
            return LintResult(memory=context.memory)

        if (
            (
                context.segment.name == "naked_identifier"
                and identifiers_policy_applicable(
                    self.unquoted_identifiers_policy,  # type: ignore
                    context.parent_stack,
                )
                and (
                    context.segment.raw.upper()
                    in context.dialect.sets("unreserved_keywords")
                )
            )
        ) or (
            (
                context.segment.name == "quoted_identifier"
                and identifiers_policy_applicable(
                    self.quoted_identifiers_policy, context.parent_stack  # type: ignore
                )
                and (
                    context.segment.raw.upper()[1:-1]
                    in context.dialect.sets("unreserved_keywords")
                    or context.segment.raw.upper()[1:-1]
                    in context.dialect.sets("reserved_keywords")
                )
            )
        ):
            return LintResult(anchor=context.segment)
        else:
            return None

    @staticmethod
    def _split_comma_separated_string(raw_str: str) -> List[str]:
        return [s.strip() for s in raw_str.split(",") if s.strip()]

    def _init_ignore_string(self):
        """Called first time rule is evaluated to fetch & cache the ignore_words."""
        # Use str() in case bools are passed which might otherwise be read as bool
        ignore_words_config = str(getattr(self, "ignore_words"))
        if ignore_words_config and ignore_words_config != "None":
            self.ignore_words_list = self._split_comma_separated_string(
                ignore_words_config.lower()
            )
        else:
            self.ignore_words_list = []

        ignore_words_list = self.ignore_words_list
        return ignore_words_list
