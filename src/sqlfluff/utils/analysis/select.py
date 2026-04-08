"""Basic code analysis tools for SELECT statements."""

from typing import NamedTuple, Optional, cast

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo, ColumnAliasInfo
from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.dialects.dialect_ansi import (
    FromClauseSegment,
    JoinClauseSegment,
    ObjectReferenceSegment,
    SelectClauseElementSegment,
)


class SelectStatementColumnsAndTables(NamedTuple):
    """Structure returned by get_select_statement_info()."""

    select_statement: BaseSegment
    table_aliases: list[AliasInfo]
    standalone_aliases: list[BaseSegment]  # value table function aliases
    reference_buffer: list[ObjectReferenceSegment]
    select_targets: list[SelectClauseElementSegment]
    col_aliases: list[ColumnAliasInfo]
    using_cols: list[BaseSegment]
    table_reference_buffer: list[ObjectReferenceSegment]


def _get_struct_alias_refs(segment: BaseSegment) -> set[int]:
    """Get the ids of object references that are aliases inside STRUCT functions.

    In dialects like Databricks, SparkSQL, and Hive, STRUCT() is parsed as a
    regular function where aliases appear as column_reference segments:
        STRUCT(expr AS alias_name, ...)
    These alias names are not real column references and should be excluded
    from linting rules that check column references.
    """
    struct_alias_ids: set[int] = set()
    for func in segment.recursive_crawl(
        "function",
        no_recursive_seg_type=["select_statement", "merge_statement"],
    ):
        fn = func.get_child("function_name")
        if not fn or fn.raw_upper != "STRUCT":
            continue
        contents = func.get_child("function_contents")
        if not contents:
            continue
        brack = contents.get_child("bracketed")
        if not brack:
            continue
        prev_was_index = False
        for seg in brack.segments:
            if seg.is_type("index_column_definition"):
                prev_was_index = True
            elif prev_was_index and not seg.is_type(
                "whitespace", "newline", "indent", "dedent"
            ):
                # This segment is the alias expression after AS inside STRUCT.
                # Collect all object_reference descendants - they are alias
                # names, not real column references.
                for ref in seg.recursive_crawl("object_reference"):
                    struct_alias_ids.add(id(ref))
                prev_was_index = False
    return struct_alias_ids


def _get_object_references(
    segment: BaseSegment,
    exclude_ids: Optional[set[int]] = None,
) -> list[ObjectReferenceSegment]:
    return list(
        cast(ObjectReferenceSegment, _seg)
        for _seg in segment.recursive_crawl(
            "object_reference",
            no_recursive_seg_type=["select_statement", "merge_statement"],
        )
        # Exclude collation references - they inherit from ObjectReferenceSegment
        # but should not be treated as column/table references for linting purposes
        if not _seg.is_type("collation_reference")
        # Exclude references that are aliases inside STRUCT() functions
        and (exclude_ids is None or id(_seg) not in exclude_ids)
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
    # Identify references that are aliases inside STRUCT() functions so we can
    # exclude them. These are alias definitions, not real column references.
    # See: https://github.com/sqlfluff/sqlfluff/issues/6919
    struct_alias_ids = _get_struct_alias_refs(sc)
    reference_buffer = _get_object_references(sc, exclude_ids=struct_alias_ids)
    table_reference_buffer = []
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
        list[SelectClauseElementSegment],
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
        for table_expression in fc.recursive_crawl(
            "table_expression", no_recursive_seg_type="select_statement"
        ):
            for seg in table_expression.iter_segments():
                # table references can get tricky with what is a schema, table,
                # project, or column. It may be best for now to use the redshift
                # unnest logic for dialects that support arrays or objects/structs
                # in AL05. However, this solves finding other types of references
                # in functions such as LATERAL FLATTEN.
                if not seg.is_type("table_reference"):
                    reference_buffer += _get_object_references(seg)
                elif cast(ObjectReferenceSegment, seg).is_qualified():
                    table_reference_buffer += _get_object_references(seg)
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
                            using_cols.append(subseg)
                    seen_using = False

    return SelectStatementColumnsAndTables(
        select_statement=segment,
        table_aliases=table_aliases or [],
        standalone_aliases=standalone_aliases or [],
        reference_buffer=reference_buffer,
        select_targets=select_targets,
        col_aliases=col_aliases,
        using_cols=using_cols,
        table_reference_buffer=table_reference_buffer,
    )


def get_aliases_from_select(
    segment: BaseSegment, dialect: Optional[Dialect] = None
) -> tuple[Optional[list[AliasInfo]], Optional[list[BaseSegment]]]:
    """Gets the aliases referred to in the FROM clause.

    Returns a tuple of two lists:
    - Table aliases
    - Value table function aliases
    """
    fc = segment.get_child("from_clause")
    if not fc:
        # If there's no from clause then just abort.
        return None, None
    assert isinstance(fc, (FromClauseSegment, JoinClauseSegment))
    aliases = fc.get_eventual_aliases()

    # We only want table aliases, so filter out aliases for value table
    # functions, lambda parameters, pivot columns and unpivot output aliases.
    standalone_aliases: list[BaseSegment] = []
    standalone_aliases += _get_pivot_table_aliases(segment, dialect)
    standalone_aliases += _get_lambda_argument_columns(segment, dialect)
    standalone_aliases += _get_unpivot_table_aliases(segment, dialect)

    table_aliases = []
    for table_expr, alias_info in aliases:
        if _has_value_table_function(table_expr, dialect):
            if alias_info.segment and alias_info.segment not in standalone_aliases:
                standalone_aliases.append(alias_info.segment)
        elif alias_info not in table_aliases:
            table_aliases.append(alias_info)

    return table_aliases, standalone_aliases


def _has_value_table_function(
    table_expr: BaseSegment, dialect: Optional[Dialect]
) -> bool:
    if not dialect:
        # We need the dialect to get the value table function names. If
        # we don't have it, assume the clause does not have a value table
        # function.
        return False  # pragma: no cover

    for function_name in table_expr.recursive_crawl(
        "function_name", no_recursive_seg_type="select_statement"
    ):
        # Other rules can increase whitespace in the function name, so use strip to
        # remove
        # See: https://github.com/sqlfluff/sqlfluff/issues/1304
        if function_name.raw.upper().strip() in dialect.sets("value_table_functions"):
            return True
    return False


def _get_pivot_table_aliases(
    segment: BaseSegment, dialect: Optional[Dialect]
) -> list[BaseSegment]:
    if not dialect:
        # We need the dialect to get the pivot table column names. If
        # we don't have it, assume the clause does not have a pivot table
        return []  # pragma: no cover

    pivot_table_aliases: list[BaseSegment] = []
    for fc in segment.recursive_crawl("from_pivot_expression"):
        for pivot_table_alias in fc.recursive_crawl(
            "pivot_column_reference", "table_reference"
        ):
            if pivot_table_alias.raw not in [a.raw for a in pivot_table_aliases]:
                pivot_table_aliases.append(pivot_table_alias)

    return pivot_table_aliases


def _get_unpivot_table_aliases(
    segment: BaseSegment, dialect: Optional[Dialect]
) -> list[BaseSegment]:
    """Get standalone aliases introduced by UNPIVOT expressions.

    Handles:
    - Redshift ``object_unpivoting``: ``UNPIVOT x.json AS value AT key``
    - Redshift ``array_unnesting``: ``x.array AS value AT key``
        - Redshift ``from_unpivot_expression``:
            ``UNPIVOT (value_col FOR key_col IN (...))``
        - Snowflake/BigQuery (single-column)/DuckDB (single-key)
            ``from_unpivot_expression`` with the same
            ``UNPIVOT (value_col FOR key_col IN (...))`` pattern

    The output aliases (value and key column names) are introduced by the
    UNPIVOT clause and are available as standalone references in the enclosing
    SELECT without needing table qualification.
    """
    if not dialect:
        return []  # pragma: no cover

    unpivot_aliases: list[BaseSegment] = []

    # Handle object_unpivoting (UNPIVOT x.json AS value AT key) and
    # array_unnesting (x.array AS value AT key) - Redshift SUPER type specific.
    # Both segment types introduce output aliases via AS and AT keywords.
    for unpivot_seg in segment.recursive_crawl("object_unpivoting", "array_unnesting"):
        seen_keyword = False
        for seg in unpivot_seg.segments:
            if seg.is_type("keyword") and seg.raw_upper in ("AS", "AT"):
                seen_keyword = True
            elif seen_keyword and not seg.is_type(
                "whitespace", "newline", "indent", "dedent"
            ):
                if seg.raw not in [a.raw for a in unpivot_aliases]:
                    unpivot_aliases.append(seg)
                seen_keyword = False

    # Handle from_unpivot_expression used in Redshift, Snowflake,
    # BigQuery single-column UNPIVOT, and DuckDB single-key UNPIVOT.
    # Pattern: UNPIVOT (value_col FOR key_col IN (...))
    # The value_col (before FOR) and key_col (between FOR and IN) are the output
    # column names introduced by the UNPIVOT and should be standalone aliases.
    for unpivot_seg in segment.recursive_crawl("from_unpivot_expression"):
        for bracketed in unpivot_seg.get_children("bracketed"):
            for seg in bracketed.segments:
                if seg.is_type("keyword") and seg.raw_upper == "IN":
                    # Stop before the IN clause (which lists input columns)
                    break
                if not seg.is_type(
                    "whitespace",
                    "newline",
                    "indent",
                    "dedent",
                    "start_bracket",
                    "end_bracket",
                    "bracketed",
                    "keyword",
                    "comma",
                ) and seg.raw not in [a.raw for a in unpivot_aliases]:
                    unpivot_aliases.append(seg)
            break  # Only process the first bracketed child

    return unpivot_aliases


# Lambda arguments,
# e.g. `x` and `y` in `x -> x is not null` and `(x, y) -> x + y`
# are declared in-place, and are as such standalone – i.e. they do not reference
# identifiers or columns that we should expect to be declared somewhere else.
# These columns are interesting to identify since they can get special
# treatment in some rules.
def _get_lambda_argument_columns(
    segment: BaseSegment, dialect: Optional[Dialect]
) -> list[BaseSegment]:
    if not dialect or dialect.name not in [
        "athena",
        "sparksql",
        "duckdb",
        "trino",
        "databricks",
        "snowflake",
    ]:
        # Only athena and sparksql are known to have lambda expressions,
        # so all other dialects will have zero lambda columns
        return []

    lambda_argument_columns: list[BaseSegment] = []
    for potential_lambda in segment.recursive_crawl("expression", "lambda_function"):
        potential_arrow = potential_lambda.get_child("binary_operator", "lambda_arrow")
        if potential_arrow and potential_arrow.raw == "->":
            arrow_operator = potential_arrow
            # The arguments will be before the arrow operator, so we get anything
            # that is a column reference or a set of bracketed column references before
            # the arrow. There should be exactly one segment matching this, if there are
            # more, this doesn't cleanly match a lambda expression
            argument_segments = potential_lambda.select_children(
                stop_seg=arrow_operator,
                select_if=(
                    lambda x: x.is_type("bracketed", "column_reference", "parameter")
                ),
            )

            assert len(argument_segments) == 1
            child_segment = argument_segments[0]

            if child_segment.is_type("bracketed"):
                start_bracket = child_segment.get_child("start_bracket")
                # There will be a start bracket if it's bracketed.
                assert start_bracket
                if start_bracket.raw == "(":
                    bracketed_arguments = child_segment.get_children(
                        "column_reference", "parameter"
                    )
                    raw_arguments = [argument for argument in bracketed_arguments]
                    lambda_argument_columns += raw_arguments

            elif child_segment.is_type("column_reference", "parameter"):
                lambda_argument_columns.append(child_segment)

    return lambda_argument_columns
