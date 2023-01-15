"""The DuckDB dialect.

https://duckdb.org/docs/
"""

from typing import Optional

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.core.parser import (
    Bracketed,
    Dedent,
    Delimited,
    Indent,
    Matchable,
    OneOf,
    Ref,
    Sequence,
    StartsWith,
)

postgres_dialect = load_raw_dialect("postgres")

duckdb_dialect = postgres_dialect.copy_as("duckdb")


class SelectClauseElementSegment(ansi.SelectClauseElementSegment):
    """An element in the targets of a select statement."""

    type = "select_clause_element"

    match_grammar = OneOf(
        Sequence(
            Ref("WildcardExpressionSegment"),
            OneOf(
                Sequence(
                    "EXCLUDE",
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    ),
                ),
                Sequence(
                    "REPLACE",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("BaseExpressionElementGrammar"),
                                Ref("AliasExpressionSegment", optional=True),
                            ),
                        )
                    ),
                ),
            ),
        ),
        Sequence(
            Ref("BaseExpressionElementGrammar"),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )


class OrderByClauseSegment(ansi.OrderByClauseSegment):
    """A `ORDER BY` clause like in `SELECT`."""

    match_grammar: Matchable = StartsWith(
        Sequence("ORDER", "BY"),
        terminator=Ref("OrderByClauseTerminators"),
    )

    parse_grammar: Optional[Matchable] = Sequence(
        "ORDER",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    "ALL",
                    Ref("ColumnReferenceSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("ExpressionSegment"),
                ),
                OneOf("ASC", "DESC", optional=True),
                Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
            ),
            allow_trailing=True,
            terminator=OneOf(Ref.keyword("LIMIT"), Ref("FrameClauseUnitGrammar")),
        ),
        Dedent,
    )


class GroupByClauseSegment(ansi.GroupByClauseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    match_grammar: Matchable = StartsWith(
        Sequence("GROUP", "BY"),
        terminator=Ref("GroupByClauseTerminatorGrammar"),
        enforce_whitespace_preceding_terminator=True,
    )

    parse_grammar: Optional[Matchable] = Sequence(
        "GROUP",
        "BY",
        Indent,
        Delimited(
            OneOf(
                "ALL",
                Ref("ColumnReferenceSegment"),
                Ref("NumericLiteralSegment"),
                Ref("ExpressionSegment"),
            ),
            allow_trailing=True,
            terminator=Ref("GroupByClauseTerminatorGrammar"),
        ),
        Dedent,
    )


class ObjectLiteralElementSegment(ansi.ObjectLiteralElementSegment):
    """An object literal element segment."""

    match_grammar: Matchable = Sequence(
        OneOf(
            Ref("NakedIdentifierSegment"),
            Ref("QuotedLiteralSegment"),
        ),
        Ref("ColonSegment"),
        Ref("BaseExpressionElementGrammar"),
    )
