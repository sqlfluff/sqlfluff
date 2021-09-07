"""Implementation of Rule L014."""

from typing import Tuple, List

from sqlfluff.core.rules.base import LintResult
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.rules.L010 import Rule_L010


def unquoted_ids_policy_applicable(policy, parent_stack):
    """Does `unquoted_identifiers_policy` apply to this segment?"""
    if policy == "all":
        return True
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

    The functionality for this rule is inherited from :obj:`Rule_L010`.

    | **Anti-pattern**
    | In this example, unquoted identifier 'a' is in lower-case but
    | 'B' is in upper-case.

    .. code-block:: sql

        select
            a,
            B
        from foo

    | **Best practice**
    | Ensure all unquoted identifiers are either in upper-case or in lower-case

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
    config_keywords = ["extended_capitalisation_policy", "unquoted_identifiers_policy"]
    _description_elem = "Unquoted identifiers"

    def _eval(self, segment, memory, parent_stack, **kwargs):
        if unquoted_ids_policy_applicable(
            self.unquoted_identifiers_policy, parent_stack
        ):
            return super()._eval(segment, memory, parent_stack, **kwargs)
        else:
            return LintResult(memory=memory)
