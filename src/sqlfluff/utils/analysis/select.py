"""Basic code analysis tools for SELECT statements."""

from typing import List, NamedTuple, Optional, cast

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo, ColumnAliasInfo
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.dialects.dialect_ansi import (
    ObjectReferenceSegment,
    SelectClauseElementSegment,
)


class SelectStatementColumnsAndTables(NamedTuple):
    """Structure returned by get_select_statement_info()."""

    select_statement: BaseSegment
    table_aliases: List[AliasInfo]
    standalone_aliases: List[str]  # value table function aliases
    reference_buffer: List[ObjectReferenceSegment]
    select_targets: List[SelectClauseElementSegment]
    col_aliases: List[ColumnAliasInfo]
    using_cols: List[str]


def _get_object_references(segment: BaseSegment) -> List[ObjectReferenceSegment]:
    return list(
        cast(ObjectReferenceSegment, _seg)
        for _seg in segment.recursive_crawl(
            "object_reference", no_recursive_seg_type="select_statement"
        )
    )


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
    # Sometimes there is no select clause (e.g. "SELECT *" is a select_clause_element)
    if not sc:  # pragma: no cover
        # TODO: Review whether this clause should be removed. It might only
        # have existed for an old way of structuring the Exasol dialect.
        return None
    # NOTE: In this first crawl, don't crawl inside any sub-selects, that's very
    # important for both isolation and performance reasons.
    reference_buffer = _get_object_references(sc)
    for potential_clause in (
        "where_clause",
        "groupby_clause",
        "having_clause",
        "orderby_clause",
        "qualify_clause",
    ):
        clause = segment.get_child(potential_clause)
        if clause:
            reference_buffer += _get_object_references(clause)

    # Get all select targets.
    _select_clause = segment.get_child("select_clause")
    assert _select_clause, "Select statement found without select clause."
    select_targets = cast(
        List[SelectClauseElementSegment],
        _select_clause.get_children("select_clause_element"),
    )

    # Get all column aliases. NOTE: In two steps so mypy can follow.
    _pre_aliases = [s.get_alias() for s in select_targets]
    col_aliases = [_alias for _alias in _pre_aliases if _alias is not None]

    # Get any columns referred to in a using clause, and extract anything
    # from ON clauses.
    using_cols = []
    fc = segment.get_child("from_clause")
    if fc:
        for join_clause in fc.recursive_crawl(
            "join_clause", no_recursive_seg_type="select_statement"
        ):
            seen_using = False
            for seg in join_clause.iter_segments():
                if seg.is_type("keyword") and seg.raw_upper == "USING":
                    seen_using = True
                elif seg.is_type("join_on_condition"):
                    for on_seg in seg.segments:
                        if on_seg.is_type("bracketed", "expression"):
                            # Deal with expressions
                            reference_buffer += _get_object_references(seg)
                elif seen_using and seg.is_type("bracketed"):
                    for subseg in seg.segments:
                        if subseg.is_type("identifier"):
                            using_cols.append(subseg.raw)
                    seen_using = False

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
    # functions, lambda parameters and pivot columns.
    standalone_aliases = []
    standalone_aliases += _get_pivot_table_columns(segment, dialect)
    standalone_aliases += _get_lambda_argument_columns(segment, dialect)

    table_aliases = []
    for table_expr, alias_info in aliases:
        if _has_value_table_function(table_expr, dialect):
            if alias_info[0] not in standalone_aliases:
                standalone_aliases.append(alias_info[0])
        elif alias_info not in table_aliases:
            table_aliases.append(alias_info)

    return table_aliases, standalone_aliases


def _has_value_table_function(table_expr, dialect) -> bool:
    if not dialect:
        # We need the dialect to get the value table function names. If
        # we don't have it, assume the clause does not have a value table
        # function.
        return False  # pragma: no cover

    for function_name in table_expr.recursive_crawl("function_name"):
        # Other rules can increase whitespace in the function name, so use strip to
        # remove
        # See: https://github.com/sqlfluff/sqlfluff/issues/1304
        if function_name.raw.upper().strip() in dialect.sets("value_table_functions"):
            return True
    return False


def _get_pivot_table_columns(segment, dialect) -> list:
    if not dialect:
        # We need the dialect to get the pivot table column names. If
        # we don't have it, assume the clause does not have a pivot table
        return []  # pragma: no cover

    fc = segment.recursive_crawl("from_pivot_expression")
    if not fc:
        # If there's no pivot clause then just abort.
        return []  # pragma: no cover

    pivot_table_column_aliases = []

    for pivot_table_column_alias in segment.recursive_crawl("pivot_column_reference"):
        if pivot_table_column_alias.raw not in pivot_table_column_aliases:
            pivot_table_column_aliases.append(pivot_table_column_alias.raw)

    return pivot_table_column_aliases


# Lambda arguments,
# e.g. `x` and `y` in `x -> x is not null` and `(x, y) -> x + y`
# are declared in-place, and are as such standalone – i.e. they do not reference
# identifiers or columns that we should expect to be declared somewhere else.
# These columns are interesting to identify since they can get special
# treatment in some rules.
def _get_lambda_argument_columns(
    segment: BaseSegment, dialect: Dialect
) -> Optional[List[str]]:
    if not dialect or dialect.name not in ["athena", "sparksql"]:
        # Only athena and sparksql are known to have lambda expressions,
        # so all other dialects will have zero lambda columns
        return []

    lambda_argument_columns = []
    for potential_lambda in segment.recursive_crawl("expression"):
        potential_arrow = potential_lambda.get_child("binary_operator")
        if potential_arrow and potential_arrow.raw == "->":
            arrow_operator = potential_arrow
            # The arguments will be before the arrow operator, so we get anything
            # that is a column reference or a set of bracketed column references before
            # the arrow. There should be exactly one segment matching this, if there are
            # more, this doesn't cleanly match a lambda expression
            argument_segments = potential_lambda.select_children(
                stop_seg=arrow_operator,
                select_if=(
                    lambda x: x.is_type("bracketed") or x.is_type("column_reference")
                ),
            )

            assert len(argument_segments) == 1
            child_segment = argument_segments[0]

            if child_segment.is_type("bracketed"):
                start_bracket = child_segment.get_child("start_bracket")
                # There will be a start bracket if it's bracketed.
                assert start_bracket
                if start_bracket.raw == "(":
                    bracketed_arguments = child_segment.get_children("column_reference")
                    raw_arguments = [argument.raw for argument in bracketed_arguments]
                    lambda_argument_columns += raw_arguments

            elif child_segment.is_type("column_reference"):
                lambda_argument_columns.append(child_segment.raw)

    return lambda_argument_columns
