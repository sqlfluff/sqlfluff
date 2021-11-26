"""Basic code analysis tools for SELECT statements."""
from typing import List, NamedTuple, Optional

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.parser.segments.base import BaseSegment


class SelectStatementColumnsAndTables(NamedTuple):
    """Structure returned by get_select_statement_info()."""

    select_statement: BaseSegment
    table_aliases: List[AliasInfo]
    standalone_aliases: List[str]
    reference_buffer: List[BaseSegment]
    select_targets: List[BaseSegment]
    col_aliases: List[str]
    using_cols: List[str]


def get_select_statement_info(
    segment: BaseSegment, dialect: Optional[Dialect], early_exit: bool = True
) -> Optional[SelectStatementColumnsAndTables]:
    """Analyze a select statement: targets, aliases, etc. Return info."""
    assert segment.is_type("select_statement")
    table_aliases, standalone_aliases = get_aliases_from_select(segment, dialect)
    if early_exit and not table_aliases and not standalone_aliases:
        return None

    # Iterate through all the references, both in the select clause, but also
    # potential others.
    sc = segment.get_child("select_clause")
    reference_buffer = list(sc.recursive_crawl("object_reference"))
    for potential_clause in (
        "where_clause",
        "groupby_clause",
        "having_clause",
        "orderby_clause",
    ):
        clause = segment.get_child(potential_clause)
        if clause:
            reference_buffer += list(clause.recursive_crawl("object_reference"))

    # Get all select targets.
    select_targets = segment.get_child("select_clause").get_children(
        "select_clause_element"
    )

    # Get all column aliases
    col_aliases = []
    for col_seg in list(sc.recursive_crawl("alias_expression")):
        for seg in col_seg.segments:
            if seg.is_type("identifier"):
                col_aliases.append(seg.raw)

    # Get any columns referred to in a using clause, and extract anything
    # from ON clauses.
    using_cols = []
    fc = segment.get_child("from_clause")
    if fc:
        for join_clause in fc.recursive_crawl("join_clause"):
            seen_using = False
            for seg in join_clause.iter_segments():
                if seg.is_type("keyword") and seg.name == "using":
                    seen_using = True
                elif seg.is_type("join_on_condition"):
                    for on_seg in seg.segments:
                        if on_seg.is_type("expression"):
                            # Deal with expressions
                            reference_buffer += list(
                                seg.recursive_crawl("object_reference")
                            )
                elif seen_using and seg.is_type("bracketed"):
                    for subseg in seg.segments:
                        if subseg.is_type("identifier"):
                            using_cols.append(subseg.raw)
                    seen_using = False

    # PURGE any references which are in nested select statements
    for ref in reference_buffer.copy():
        ref_path = segment.path_to(ref)
        # is it in a subselect? i.e. a select which isn't this one.
        if any(
            seg.is_type("select_statement") and seg is not segment for seg in ref_path
        ):
            reference_buffer.remove(ref)

    return SelectStatementColumnsAndTables(
        select_statement=segment,
        table_aliases=table_aliases or [],
        standalone_aliases=standalone_aliases or [],
        reference_buffer=reference_buffer,
        select_targets=select_targets,
        col_aliases=col_aliases,
        using_cols=using_cols,
    )


def get_aliases_from_select(segment, dialect=None):
    """Gets the aliases referred to in the FROM clause.

    Returns a tuple of two lists:
    - Table aliases
    - Value table function aliases
    """
    fc = segment.get_child("from_clause")
    if not fc:
        # If there's no from clause then just abort.
        return None, None
    aliases = fc.get_eventual_aliases()

    # We only want table aliases, so filter out aliases for value table
    # functions and pivot columns.
    table_aliases = []
    standalone_aliases = _get_pivot_table_columns(segment, dialect)
    for table_expr, alias_info in aliases:
        if _has_value_table_function(table_expr, dialect):
            if alias_info[0] not in standalone_aliases:
                standalone_aliases.append(alias_info[0])
        elif alias_info not in standalone_aliases:
            table_aliases.append(alias_info)

    return table_aliases, standalone_aliases


def _has_value_table_function(table_expr, dialect):
    if not dialect:
        # We need the dialect to get the value table function names. If
        # we don't have it, assume the clause does not have a value table
        # function.
        return False

    for function_name in table_expr.recursive_crawl("function_name"):
        # Other rules can increase whitespace in the function name, so use strip to remove
        # See: https://github.com/sqlfluff/sqlfluff/issues/1304
        if function_name.raw.lower().strip() in dialect.sets("value_table_functions"):
            return True
    return False


def _get_pivot_table_columns(segment, dialect):
    if not dialect:
        # We need the dialect to get the pivot table column names. If
        # we don't have it, assume the clause does not have a pivot table
        return []

    fc = segment.get_child("from_pivot_expression")
    if not fc:
        # If there's no pivot clause then just abort.
        return []

    pivot_table_column_aliases = []

    for pivot_table_column_alias in segment.recursive_crawl("pivot_column_reference"):
        if pivot_table_column_alias.raw not in pivot_table_column_aliases:
            pivot_table_column_aliases.append(pivot_table_column_alias.raw)

    return pivot_table_column_aliases
