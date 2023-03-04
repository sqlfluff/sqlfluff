"""Helper utilities for identifiers.

These are primarily common functions used by multiple rule
bundles. Defined here to avoid duplication, but also avoid
circular imports.
"""

from typing import Tuple

from sqlfluff.core.parser import BaseSegment


def identifiers_policy_applicable(
    policy: str, parent_stack: Tuple[BaseSegment, ...]
) -> bool:
    """Does `(un)quoted_identifiers_policy` apply to this segment?

    This method is used in CP02, RF04 and RF05.
    """
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
