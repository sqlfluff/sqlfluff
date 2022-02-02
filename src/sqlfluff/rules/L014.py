"""Implementation of Rule L014."""

from typing import Tuple, List

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.rules.L010 import Rule_L010


def identifiers_policy_applicable(
    policy: str, parent_stack: Tuple[BaseSegment, ...]
) -> bool:
    """Does `(un)quoted_identifiers_policy` apply to this segment?"""
    if policy == "all":
        return True
    if policy == "none":
        return False
    is_alias = parent_stack and parent_stack[-1].is_type(
        "alias_expression", "column_definition", "with_compound_statement"
    )
    if policy == "aliases" and is_alias:
        return True
    is_inside_from = any(p.is_type("from_clause") for p in parent_stack)
    if policy == "column_aliases" and is_alias and not is_inside_from:
        return True
    return False


@document_configuration
@document_fix_compatible
class Rule_L014(Rule_L010):
    """Inconsistent capitalisation of unquoted identifiers.

    **Anti-pattern**

    In this example, unquoted identifier ``a`` is in lower-case but
    ``B`` is in upper-case.

    .. code-block:: sql

        select
            a,
            B
        from foo

    **Best practice**

    Ensure all unquoted identifiers are either in upper-case or in lower-case.

    .. code-block:: sql

        select
            a,
            b
        from foo

        -- Also good

        select
            A,
            B
        from foo

    """

    _target_elems: List[Tuple[str, str]] = [("name", "naked_identifier")]
    config_keywords = [
        "extended_capitalisation_policy",
        "unquoted_identifiers_policy",
        "ignore_words",
    ]
    _description_elem = "Unquoted identifiers"

    def _eval(self, context: RuleContext) -> LintResult:
        if identifiers_policy_applicable(
            self.unquoted_identifiers_policy, context.parent_stack  # type: ignore
        ):
            return super()._eval(context=context)
        else:
            return LintResult(memory=context.memory)
