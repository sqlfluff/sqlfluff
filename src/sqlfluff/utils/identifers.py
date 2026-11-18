"""Helper utilities for identifiers.

These are primarily common functions used by multiple rule
bundles. Defined here to avoid duplication, but also avoid
circular imports.
"""

from sqlfluff.core.parser import BaseSegment


def identifiers_policy_applicable(
    policy: str, parent_stack: tuple[BaseSegment, ...]
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
    # Walk outward from the identifier looking for the nearest of
    # "select_clause" or "from_clause". A column alias that belongs to a
    # derived table's own SELECT (e.g. `FROM (SELECT 1 AS x) sub`) is
    # nested inside that inner select_clause, which is itself nested
    # inside the *outer* from_clause - so scanning the whole parent_stack
    # for any from_clause wrongly classifies it as a table alias. Stopping
    # at the first select_clause encountered keeps such a column alias
    # scoped to the SELECT it actually belongs to.
    is_inside_from = False
    for p in reversed(parent_stack):
        if p.is_type("select_clause"):
            break
        if p.is_type("from_clause"):
            is_inside_from = True
            break
    if policy == "column_aliases" and is_alias and not is_inside_from:
        return True
    if policy == "table_aliases" and is_alias and is_inside_from:
        return True
    return False
