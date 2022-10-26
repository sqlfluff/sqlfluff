"""The clickhouse dialect.

https://clickhouse.com/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    BaseSegment,
    Bracketed,
    Delimited,
    Matchable,
    OneOf,
    OptionallyBracketed,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_clickhouse_keywords import (
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")

clickhouse_dialect = ansi_dialect.copy_as("clickhouse")
clickhouse_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
clickhouse_dialect.sets("reserved_keywords").clear()


class CTEDefinitionSegment(ansi.CTEDefinitionSegment):
    """A CTE Definition from a WITH statement.

    Overridden from ANSI to allow expression CTEs.
    https://clickhouse.com/docs/en/sql-reference/statements/select/with/
    """

    type = "common_table_expression"
    match_grammar: Matchable = OneOf(
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("CTEColumnList", optional=True),
            "AS",
            Bracketed(
                # Ephemeral here to subdivide the query.
                Ref("SelectableGrammar", ephemeral_name="SelectableGrammar")
            ),
        ),
        Sequence(
            Ref("ExpressionSegment"),
            "AS",
            Ref("SingleIdentifierGrammar"),
        ),
    )


class FromExpressionElementSegment(ansi.FromExpressionElementSegment):
    """A table expression.

    Overridden from ANSI to allow FINAL modifier.
    https://clickhouse.com/docs/en/sql-reference/statements/select/from#final-modifier
    """

    type = "from_expression_element"
    match_grammar: Matchable = Sequence(
        Ref("PreTableFunctionKeywordsGrammar", optional=True),
        OptionallyBracketed(Ref("TableExpressionSegment")),
        Ref(
            "AliasExpressionSegment",
            exclude=OneOf(
                Ref("SamplingExpressionSegment"),
                Ref("JoinLikeClauseGrammar"),
                Ref.keyword("Final"),
            ),
            optional=True,
        ),
        Ref.keyword("FINAL", optional=True),
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#flattening_arrays
        Sequence("WITH", "OFFSET", Ref("AliasExpressionSegment"), optional=True),
        Ref("SamplingExpressionSegment", optional=True),
        Ref("PostTableExpressionGrammar", optional=True),
    )


class EngineFunctionSegment(BaseSegment):
    """A ClickHouse `ENGINE` clause function.

    With this segment we attempt to match all possible engines.
    """

    type = "engine_function"
    match_grammar: Matchable = Sequence(
        Sequence(
            Ref(
                "FunctionNameSegment",
                exclude=OneOf(
                    Ref("DatePartFunctionNameSegment"),
                    Ref("ValuesClauseSegment"),
                ),
            ),
            Bracketed(
                Ref(
                    "FunctionContentsGrammar",
                    # The brackets might be empty for some functions...
                    optional=True,
                    ephemeral_name="FunctionContentsGrammar",
                ),
                # Engine functions may omit brackets.
                optional=True,
            ),
        ),
    )


class EngineSegment(BaseSegment):
    """An `ENGINE` used in `CREATE TABLE`."""

    type = "engine"

    match_grammar = Sequence(
        "ENGINE",
        Ref("EqualsSegment"),
        Sequence(
            Ref("EngineFunctionSegment"),
            AnySetOf(
                Sequence(
                    "ORDER",
                    "BY",
                    OneOf(
                        Ref("BracketedColumnReferenceListGrammar"),
                        Ref("ColumnReferenceSegment"),
                    ),
                    optional=True,
                ),
                Sequence(
                    "PARTITION",
                    "BY",
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
                Sequence(
                    "PRIMARY",
                    "KEY",
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
                Sequence(
                    "SAMPLE",
                    "BY",
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
                Sequence(
                    "SETTINGS",
                    Delimited(
                        AnyNumberOf(
                            Sequence(
                                Ref("NakedIdentifierSegment"),
                                Ref("EqualsSegment"),
                                OneOf(
                                    Ref("NumericLiteralSegment"),
                                    Ref("QuotedLiteralSegment"),
                                ),
                                optional=True,
                            ),
                        )
                    ),
                    optional=True,
                ),
            ),
        ),
    )


class ColumnTTLSegment(BaseSegment):
    """A TTL clause for columns as used in CREATE TABLE.

    Specified in
    https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-column-ttl
    """

    type = "column_ttl_segment"

    match_grammar = Sequence(
        "TTL",
        Ref("ExpressionSegment"),
    )


class TableTTLSegment(BaseSegment):
    """A TTL clause for tables as used in CREATE TABLE.

    Specified in
    https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#mergetree-table-ttl
    """

    type = "table_ttl_segment"

    match_grammar = Sequence(
        "TTL",
        Delimited(
            Sequence(
                Ref("ExpressionSegment"),
                OneOf(
                    "DELETE",
                    Sequence(
                        "TO",
                        "VOLUME",
                        Ref("QuotedLiteralSegment"),
                    ),
                    Sequence(
                        "TO",
                        "DISK",
                        Ref("QuotedLiteralSegment"),
                    ),
                    optional=True,
                ),
                Ref("WhereClauseSegment", optional=True),
                Ref("GroupByClauseSegment", optional=True),
            )
        ),
    )


class ColumnConstraintSegment(BaseSegment):
    """ClickHouse specific column constraints.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/create/table#constraints
    """

    type = "column_constraint_segment"

    match_grammar = AnySetOf(
        Sequence(
            Sequence(
                "CONSTRAINT",
                Ref("ObjectReferenceSegment"),
                optional=True,
            ),
            OneOf(
                Sequence(Ref.keyword("NOT", optional=True), "NULL"),
                Sequence("CHECK", Bracketed(Ref("ExpressionSegment"))),
                Sequence(
                    OneOf(
                        "DEFAULT",
                        "MATERIALIZED",
                        "ALIAS",
                    ),
                    OneOf(
                        Ref("LiteralGrammar"),
                        Ref("FunctionSegment"),
                        Ref("BareFunctionSegment"),
                    ),
                ),
                Sequence(
                    "EPHEMERAL",
                    OneOf(
                        Ref("LiteralGrammar"),
                        Ref("FunctionSegment"),
                        Ref("BareFunctionSegment"),
                        optional=True,
                    ),
                ),
                Ref("PrimaryKeyGrammar"),
                Sequence(
                    "CODEC",
                    Ref("FunctionContentsGrammar"),
                    optional=True,
                ),
                Ref("ColumnTTLSegment"),
            ),
        )
    )


class ClusterReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to a cluster."""

    type = "cluster_reference"


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/create/table/
    """

    type = "create_table_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        OneOf(
            Ref("OrReplaceGrammar"),
            Ref.keyword("TEMPORARY"),
            optional=True,
        ),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Sequence(
            "ON",
            "CLUSTER",
            Ref("ClusterReferenceSegment"),
            optional=True,
        ),
        OneOf(
            # CREATE TABLE (...):
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                            Ref("ColumnConstraintSegment"),
                        ),
                    ),
                    # Column definition may be missing if using AS SELECT
                    optional=True,
                ),
                Ref("EngineSegment"),
                # CREATE TABLE (...) AS SELECT:
                Sequence(
                    "AS",
                    Ref("SelectableGrammar"),
                    optional=True,
                ),
            ),
            # CREATE TABLE AS other_table:
            Sequence(
                "AS",
                Ref("TableReferenceSegment"),
                Ref("EngineSegment", optional=True),
            ),
            # CREATE TABLE AS table_function():
            Sequence(
                "AS",
                Ref("FunctionSegment"),
            ),
        ),
        AnySetOf(
            Sequence(
                "COMMENT",
                Ref("SingleQuotedIdentifierSegment"),
            ),
            Ref("TableTTLSegment"),
            optional=True,
        ),
        Ref("TableEndClauseSegment", optional=True),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar
    parse_grammar = ansi.StatementSegment.parse_grammar.copy(
        insert=[
            Ref("EngineSegment"),
            Ref("ClusterReferenceSegment"),
            Ref("ColumnTTLSegment"),
            Ref("TableTTLSegment"),
        ]
    )
