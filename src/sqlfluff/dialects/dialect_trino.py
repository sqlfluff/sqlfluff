"""The Trino dialect.

See https://trino.io/docs/current/language.html
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    Delimited,
    LiteralSegment,
    Matchable,
    Nothing,
    OneOf,
    Ref,
    Sequence,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_trino_keywords import (
    trino_reserved_keywords,
    trino_unreserved_keywords,
)

ansi_dialect = load_raw_dialect("ansi")
trino_dialect = ansi_dialect.copy_as("trino")

# Set the bare functions: https://trino.io/docs/current/functions/datetime.html
trino_dialect.sets("bare_functions").update(
    ["current_date", "current_time", "current_timestamp", "localtime", "localtimestamp"]
)

# Set keywords
trino_dialect.sets("unreserved_keywords").clear()
trino_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", trino_unreserved_keywords
)

trino_dialect.sets("reserved_keywords").clear()
trino_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", trino_reserved_keywords
)

trino_dialect.replace(
    DateTimeLiteralGrammar=OneOf(
        Sequence(
            OneOf("DATE", "TIME", "TIMESTAMP"),
            TypedParser(
                "single_quote", LiteralSegment, type="date_constructor_literal"
            ),
        ),
        Ref("IntervalExpressionSegment"),
    ),
    LikeGrammar=Sequence("LIKE"),
    # TODO: There are no custom SQL functions in Trino! How to handle this?
    MLTableExpressionSegment=Nothing(),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "WINDOW",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("WithDataClauseSegment"),
        "FETCH",
    ),
    OrderByClauseTerminators=OneOf(
        "LIMIT",
        "HAVING",
        # For window functions
        "WINDOW",
        Ref("FrameClauseUnitGrammar"),
        "FETCH",
    ),
    SelectClauseTerminatorGrammar=OneOf(
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        Ref("SetOperatorSegment"),
        "FETCH",
    ),
    WhereClauseTerminatorGrammar=OneOf(
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "WINDOW",
        "FETCH",
    ),
    HavingClauseTerminatorGrammar=OneOf(
        Sequence("ORDER", "BY"),
        "LIMIT",
        "WINDOW",
        "FETCH",
    ),
    GroupByClauseTerminatorGrammar=OneOf(
        Sequence("ORDER", "BY"),
        "LIMIT",
        "HAVING",
        "WINDOW",
        "FETCH",
    ),
    # NOTE: This block was copy/pasted from dialect_ansi.py with these changes made:
    #  - "PRIOR" keyword removed
    Expression_A_Unary_Operator_Grammar=OneOf(
        Ref(
            "SignedSegmentGrammar",
            exclude=Sequence(Ref("QualifiedNumericLiteralSegment")),
        ),
        Ref("TildeSegment"),
        Ref("NotOperatorGrammar"),
    ),
    PostFunctionGrammar=ansi_dialect.get_grammar("PostFunctionGrammar").copy(
        insert=[
            Ref("WithinGroupClauseSegment"),
        ],
    ),
    FunctionContentsGrammar=AnyNumberOf(
        Ref("ExpressionSegment"),
        # A Cast-like function
        Sequence(Ref("ExpressionSegment"), "AS", Ref("DatatypeSegment")),
        # Trim function
        Sequence(
            Ref("TrimParametersGrammar"),
            Ref("ExpressionSegment", optional=True, exclude=Ref.keyword("FROM")),
            "FROM",
            Ref("ExpressionSegment"),
        ),
        # An extract-like or substring-like function
        Sequence(
            OneOf(Ref("DatetimeUnitSegment"), Ref("ExpressionSegment")),
            "FROM",
            Ref("ExpressionSegment"),
        ),
        Sequence(
            # Allow an optional distinct keyword here.
            Ref.keyword("DISTINCT", optional=True),
            OneOf(
                # Most functions will be using the delimited route
                # but for COUNT(*) or similar we allow the star segment
                # here.
                Ref("StarSegment"),
                Delimited(Ref("FunctionContentsExpressionGrammar")),
            ),
        ),
        Ref(
            "OrderByClauseSegment"
        ),  # used by string_agg (postgres), group_concat (exasol),listagg (snowflake)..
        # like a function call: POSITION ( 'QL' IN 'SQL')
        Sequence(
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
            "IN",
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
        ),
        Ref("IgnoreRespectNullsGrammar"),
        Ref("IndexColumnDefinitionSegment"),
        Ref("EmptyStructLiteralSegment"),
        Ref("ListaggOverflowClauseSegment"),
    ),
)


class DatatypeSegment(BaseSegment):
    """Data type segment.

    See https://trino.io/docs/current/language/types.html
    """

    type = "data_type"
    match_grammar = OneOf(
        # Boolean
        "BOOLEAN",
        # Integer
        "TINYINT",
        "SMALLINT",
        "INTEGER",
        "BIGINT",
        # Floating-point
        "REAL",
        "DOUBLE",
        # Fixed-precision
        Sequence(
            "DECIMAL",
            Ref("BracketedArguments", optional=True),
        ),
        # String
        Sequence(
            OneOf("CHAR", "VARCHAR"),
            Ref("BracketedArguments", optional=True),
        ),
        "VARBINARY",
        "JSON",
        # Date and time
        "DATE",
        Sequence(
            OneOf("TIME", "TIMESTAMP"),
            Bracketed(Ref("NumericLiteralSegment"), optional=True),
            Sequence(OneOf("WITH", "WITHOUT"), "TIME", "ZONE", optional=True),
        ),
        # Structural
        "ARRAY",
        "MAP",
        "ROW",
        # Others
        "IPADDRESS",
        "UUID",
    )


class OverlapsClauseSegment(BaseSegment):
    """An `OVERLAPS` clause like in `SELECT."""

    type = "overlaps_clause"
    match_grammar: Matchable = Nothing()


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """A `SELECT` statement without any ORDER clauses or later."""

    match_grammar: Matchable = Sequence(
        Ref("SelectClauseSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("NamedWindowSegment", optional=True),
    )


class ValuesClauseSegment(ansi.ValuesClauseSegment):
    """A `VALUES` clause within in `WITH`, `SELECT`, `INSERT`."""

    match_grammar = Sequence(
        "VALUES",
        Delimited(Ref("ExpressionSegment")),
    )


class IntervalExpressionSegment(BaseSegment):
    """An interval representing a span of time.

    https://trino.io/docs/current/language/types.html#interval-year-to-month
    https://trino.io/docs/current/functions/datetime.html#date-and-time-operators
    """

    type = "interval_expression"
    match_grammar = Sequence(
        "INTERVAL",
        Ref("QuotedLiteralSegment"),
        OneOf("YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND"),
    )


class FrameClauseSegment(BaseSegment):
    """A frame clause for window functions.

    https://trino.io/blog/2021/03/10/introducing-new-window-features.html
    """

    type = "frame_clause"

    _frame_extent = OneOf(
        Sequence("CURRENT", "ROW"),
        Sequence(
            OneOf(
                Ref("NumericLiteralSegment"), Ref("DateTimeLiteralGrammar"), "UNBOUNDED"
            ),
            OneOf("PRECEDING", "FOLLOWING"),
        ),
    )

    match_grammar: Matchable = Sequence(
        Ref("FrameClauseUnitGrammar"),
        OneOf(_frame_extent, Sequence("BETWEEN", _frame_extent, "AND", _frame_extent)),
    )


class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Intersect or Except."""

    type = "set_operator"
    match_grammar: Matchable = OneOf(
        Sequence("UNION", OneOf("DISTINCT", "ALL", optional=True)),
        Sequence(
            OneOf(
                "INTERSECT",
                "EXCEPT",
            ),
            Ref.keyword("ALL", optional=True),
        ),
        exclude=Sequence("EXCEPT", Bracketed(Anything())),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[Ref("AnalyzeStatementSegment")],
        remove=[
            Ref("TransactionStatementSegment"),
        ],
    )


class AnalyzeStatementSegment(BaseSegment):
    """An 'ANALYZE' statement.

    As per docs https://trino.io/docs/current/sql/analyze.html
    """

    type = "analyze_statement"
    match_grammar = Sequence(
        "ANALYZE",
        Ref("TableReferenceSegment"),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        Ref("ExpressionSegment"),
                    ),
                ),
            ),
            optional=True,
        ),
    )


class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions.

    https://trino.io/docs/current/functions/aggregate.html#array_agg
    """

    type = "withingroup_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Ref("OrderByClauseSegment", optional=False)),
    )


class ListaggOverflowClauseSegment(BaseSegment):
    """ON OVERFLOW clause of listagg function.

    https://trino.io/docs/current/functions/aggregate.html#array_agg
    """

    type = "listagg_overflow_clause"
    match_grammar = Sequence(
        "ON",
        "OVERFLOW",
        OneOf(
            "ERROR",
            Sequence(
                "TRUNCATE",
                Ref("SingleQuotedIdentifierSegment", optional=True),
                OneOf("WITH", "WITHOUT", optional=True),
                Ref.keyword("COUNT", optional=True),
            ),
        ),
    )
