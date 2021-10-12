"""Implementation of Rule L029."""
from typing import Optional, Tuple

from sqlfluff.core.dialects import Dialect
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.doc_decorators import document_configuration
from sqlfluff.rules.L014 import unquoted_ids_policy_applicable


@document_configuration
class Rule_L029(BaseRule):
    """Keywords should not be used as identifiers.

    | **Anti-pattern**
    | In this example, SUM function is used as an alias.

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

    config_keywords = ["unquoted_identifiers_policy"]

    def _eval(  # type: ignore
        self,
        segment: BaseSegment,
        dialect: Dialect,
        parent_stack: Tuple[BaseSegment, ...],
        **kwargs
    ) -> Optional[LintResult]:
        """Keywords should not be used as identifiers."""
        if (
            segment.name == "naked_identifier"
            and unquoted_ids_policy_applicable(
                self.unquoted_identifiers_policy, parent_stack  # type: ignore
            )
            and (segment.raw.upper() in dialect.sets("unreserved_keywords"))
        ):
            return LintResult(anchor=segment)
        else:
            return None
