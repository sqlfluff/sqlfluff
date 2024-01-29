"""The clickhouse dialect.

https://clickhouse.com/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    BaseSegment,
    Bracketed,
    Conditional,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    LiteralSegment,
    Matchable,
    Nothing,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    Sequence,
    StringLexer,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_clickhouse_keywords import UNRESERVED_KEYWORDS

ansi_dialect = load_raw_dialect("ansi")

clickhouse_dialect = ansi_dialect.copy_as("clickhouse")
clickhouse_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)


clickhouse_dialect.insert_lexer_matchers(
    # https://clickhouse.com/docs/en/sql-reference/functions#higher-order-functions---operator-and-lambdaparams-expr-function
    [StringLexer("lambda", r"->", SymbolSegment)],
    before="newline",
)

clickhouse_dialect.add(
    BackQuotedIdentifierSegment=TypedParser(
        "back_quote",
        IdentifierSegment,
        type="quoted_identifier",
    ),
    LambdaFunctionSegment=TypedParser("lambda", SymbolSegment, type="lambda"),
)

clickhouse_dialect.replace(
    BinaryOperatorGrammar=OneOf(
        Ref("ArithmeticBinaryOperatorGrammar"),
        Ref("StringBinaryOperatorGrammar"),
        Ref("BooleanBinaryOperatorGrammar"),
        Ref("ComparisonOperatorGrammar"),
        # Add Lambda Function
        Ref("LambdaFunctionSegment"),
    ),
    # https://clickhouse.com/docs/en/sql-reference/statements/select/join/#supported-types-of-join
    JoinTypeKeywordsGrammar=Sequence(
        Ref.keyword("GLOBAL", optional=True),
        OneOf(
            # This case INNER [ANY,ALL] JOIN
            Sequence("INNER", OneOf("ALL", "ANY", optional=True)),
            # This case [ANY,ALL] INNER JOIN
            Sequence(OneOf("ALL", "ANY", optional=True), "INNER"),
            # This case FULL ALL OUTER JOIN
            Sequence(
                "FULL",
                Ref.keyword("ALL", optional=True),
                Ref.keyword("OUTER", optional=True),
            ),
            # This case ALL FULL OUTER JOIN
            Sequence(
                Ref.keyword("ALL", optional=True),
                "FULL",
                Ref.keyword("OUTER", optional=True),
            ),
            # This case LEFT [OUTER,ANTI,SEMI,ANY,ASOF] JOIN
            Sequence(
                "LEFT",
                OneOf(
                    "ANTI",
                    "SEMI",
                    OneOf("ANY", "ALL", optional=True),
                    "ASOF",
                    optional=True,
                ),
                Ref.keyword("OUTER", optional=True),
            ),
            # This case [ANTI,SEMI,ANY,ASOF] LEFT JOIN
            Sequence(
                OneOf(
                    "ANTI",
                    "SEMI",
                    OneOf("ANY", "ALL", optional=True),
                    "ASOF",
                ),
                "LEFT",
            ),
            # This case RIGHT [OUTER,ANTI,SEMI,ANY,ASOF] JOIN
            Sequence(
                "RIGHT",
                OneOf(
                    "OUTER",
                    "ANTI",
                    "SEMI",
                    OneOf("ANY", "ALL", optional=True),
                    optional=True,
                ),
                Ref.keyword("OUTER", optional=True),
            ),
            # This case [OUTER,ANTI,SEMI,ANY] RIGHT JOIN
            Sequence(
                OneOf(
                    "ANTI",
                    "SEMI",
                    OneOf("ANY", "ALL", optional=True),
                    optional=True,
                ),
                "RIGHT",
            ),
            # This case ASOF JOIN
            "ASOF",
            # This case ANY JOIN
            "ANY",
            # This case ALL JOIN
            "ALL",
        ),
    ),
    JoinUsingConditionGrammar=Sequence(
        "USING",
        Conditional(Indent, indented_using_on=False),
        Delimited(
            OneOf(
                Bracketed(
                    Delimited(Ref("SingleIdentifierGrammar")),
                    parse_mode=ParseMode.GREEDY,
                ),
                Delimited(Ref("SingleIdentifierGrammar")),
            ),
        ),
        Conditional(Dedent, indented_using_on=False),
    ),
    ConditionalCrossJoinKeywordsGrammar=Nothing(),
    UnconditionalCrossJoinKeywordsGrammar=Sequence(
        Ref.keyword("GLOBAL", optional=True),
        Ref.keyword("CROSS"),
    ),
    HorizontalJoinKeywordsGrammar=Sequence(
        Ref.keyword("GLOBAL", optional=True),
        Ref.keyword("PASTE"),
    ),
    NaturalJoinKeywordsGrammar=Nothing(),
    JoinLikeClauseGrammar=Sequence(
        AnyNumberOf(
            Ref("ArrayJoinClauseSegment"),
            min_times=1,
        ),
        Ref("AliasExpressionSegment", optional=True),
    ),
    QuotedLiteralSegment=OneOf(
        TypedParser(
            "single_quote",
            LiteralSegment,
            type="quoted_literal",
        ),
        TypedParser(
            "dollar_quote",
            LiteralSegment,
            type="quoted_literal",
        ),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("SingleQuotedIdentifierSegment"),
        Ref("BackQuotedIdentifierSegment"),
    ),
    InOperatorGrammar=ansi_dialect.get_grammar("InOperatorGrammar").copy(
        insert=[Ref.keyword("GLOBAL", optional=True)],
        before=Ref.keyword("NOT", optional=True),
    ),
)


class BracketedArguments(ansi.BracketedArguments):
    """A series of bracketed arguments.

    e.g. the bracketed part of numeric(1, 3)
    """

    match_grammar = Bracketed(
        Delimited(
            OneOf(
                # Dataypes like Nullable allow optional datatypes here.
                Ref("DatatypeIdentifierSegment"),
                Ref("NumericLiteralSegment"),
            ),
            # The brackets might be empty for some cases...
            optional=True,
        ),
    )


class ArrayJoinClauseSegment(BaseSegment):
    """[LEFT] ARRAY JOIN does not support Join conditions and doesn't work as real JOIN.

    https://clickhouse.com/docs/en/sql-reference/statements/select/array-join
    """

    type = "array_join_clause"

    match_grammar: Matchable = Sequence(
        Ref.keyword("LEFT", optional=True),
        "ARRAY",
        Ref("JoinKeywordsGrammar"),
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
        ),
        Dedent,
    )


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
                Ref("SelectableGrammar"),
                parse_mode=ParseMode.GREEDY,
            ),
        ),
        Sequence(
            Ref("ExpressionSegment"),
            "AS",
            Ref("SingleIdentifierGrammar"),
        ),
    )


class AliasExpressionSegment(ansi.AliasExpressionSegment):
    """A reference to an object with an `AS` clause."""

    type = "alias_expression"
    match_grammar: Matchable = Sequence(
        Indent,
        Ref.keyword("AS", optional=True),
        OneOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                # Column alias in VALUES clause
                Bracketed(Ref("SingleIdentifierListSegment"), optional=True),
            ),
            Ref("SingleQuotedIdentifierSegment"),
            exclude=OneOf(
                "LATERAL",
                "WINDOW",
                "KEYS",
            ),
        ),
        Dedent,
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
                Ref("FromClauseTerminatorGrammar"),
                Ref("SamplingExpressionSegment"),
                Ref("JoinLikeClauseGrammar"),
                "FINAL",
                Ref("JoinClauseSegment"),
            ),
            optional=True,
        ),
        Ref.keyword("FINAL", optional=True),
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#flattening_arrays
        Sequence("WITH", "OFFSET", Ref("AliasExpressionSegment"), optional=True),
        Ref("SamplingExpressionSegment", optional=True),
        Ref("PostTableExpressionGrammar", optional=True),
    )


class TableEngineFunctionSegment(BaseSegment):
    """A ClickHouse `ENGINE` clause function.

    With this segment we attempt to match all possible engines.
    """

    type = "table_engine_function"
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
                ),
                # Engine functions may omit brackets.
                optional=True,
                parse_mode=ParseMode.GREEDY,
            ),
        ),
    )


class OnClusterClauseSegment(BaseSegment):
    """A `ON CLUSTER` clause."""

    type = "on_cluster_clause"
    match_grammar = Sequence(
        "ON",
        "CLUSTER",
        Ref("SingleIdentifierGrammar"),
    )


class TableEngineSegment(BaseSegment):
    """An `ENGINE` used in `CREATE TABLE`."""

    type = "engine"
    match_grammar = Sequence(
        "ENGINE",
        Ref("EqualsSegment"),
        Sequence(
            Ref("TableEngineFunctionSegment"),
            AnySetOf(
                Sequence(
                    "ORDER",
                    "BY",
                    OneOf(
                        Ref("BracketedColumnReferenceListGrammar"),
                        Ref("ColumnReferenceSegment"),
                    ),
                ),
                Sequence(
                    "PARTITION",
                    "BY",
                    Ref("ExpressionSegment"),
                ),
                Sequence(
                    "PRIMARY",
                    "KEY",
                    Ref("ExpressionSegment"),
                ),
                Sequence(
                    "SAMPLE",
                    "BY",
                    Ref("ExpressionSegment"),
                ),
                Sequence(
                    "SETTINGS",
                    Delimited(
                        Sequence(
                            Ref("NakedIdentifierSegment"),
                            Ref("EqualsSegment"),
                            OneOf(
                                Ref("NumericLiteralSegment"),
                                Ref("QuotedLiteralSegment"),
                            ),
                            optional=True,
                        ),
                    ),
                ),
            ),
        ),
    )


class DatabaseEngineFunctionSegment(BaseSegment):
    """A ClickHouse `ENGINE` clause function.

    With this segment we attempt to match all possible engines.
    """

    type = "engine_function"
    match_grammar: Matchable = Sequence(
        Sequence(
            OneOf(
                "ATOMIC",
                "MYSQL",
                "MATERIALIZEDMYSQL",
                "LAZY",
                "POSTGRESQL",
                "MATERIALIZEDPOSTGRESQL",
                "REPLICATED",
                "SQLITE",
            ),
            Bracketed(
                Ref(
                    "FunctionContentsGrammar",
                    # The brackets might be empty for some functions...
                    optional=True,
                ),
                # Engine functions may omit brackets.
                optional=True,
                parse_mode=ParseMode.GREEDY,
            ),
        ),
    )


class DatabaseEngineSegment(BaseSegment):
    """An `ENGINE` used in `CREATE TABLE`."""

    type = "database_engine"

    match_grammar = Sequence(
        "ENGINE",
        Ref("EqualsSegment"),
        Sequence(
            Ref("DatabaseEngineFunctionSegment"),
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


class CreateDatabaseStatementSegment(ansi.CreateDatabaseStatementSegment):
    """A `CREATE DATABASE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/create/database
    """

    type = "create_database_statement"

    match_grammar = Sequence(
        "CREATE",
        "DATABASE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        AnySetOf(
            Ref("OnClusterClauseSegment", optional=True),
            Ref("DatabaseEngineSegment", optional=True),
            Sequence(
                "COMMENT",
                Ref("SingleIdentifierGrammar"),
                optional=True,
            ),
            Sequence(
                "SETTINGS",
                Delimited(
                    Sequence(
                        Ref("NakedIdentifierSegment"),
                        Ref("EqualsSegment"),
                        OneOf(
                            Ref("NakedIdentifierSegment"),
                            Ref("NumericLiteralSegment"),
                            Ref("QuotedLiteralSegment"),
                            Ref("BooleanLiteralGrammar"),
                        ),
                        optional=True,
                    ),
                ),
                optional=True,
            ),
        ),
        AnyNumberOf(
            "TABLE",
            "OVERRIDE",
            Ref("TableReferenceSegment"),
            Bracketed(
                Delimited(
                    Ref("TableConstraintSegment"),
                    Ref("ColumnDefinitionSegment"),
                    Ref("ColumnConstraintSegment"),
                ),
                optional=True,
            ),
            optional=True,
        ),
    )


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
        Ref("OnClusterClauseSegment", optional=True),
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
                Ref("TableEngineSegment"),
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
                Ref("TableEngineSegment", optional=True),
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
                OneOf(
                    Ref("SingleIdentifierGrammar"),
                    Ref("QuotedIdentifierSegment"),
                ),
            ),
            Ref("TableTTLSegment"),
            optional=True,
        ),
        Ref("TableEndClauseSegment", optional=True),
    )


class CreateMaterializedViewStatementSegment(BaseSegment):
    """A `CREATE MATERIALIZED VIEW` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/create/table/
    """

    type = "create_materialized_view_statement"

    match_grammar = Sequence(
        "CREATE",
        "MATERIALIZED",
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        OneOf(
            Sequence(
                "TO",
                Ref("TableReferenceSegment"),
                Ref("TableEngineSegment", optional=True),
            ),
            Sequence(
                Ref("TableEngineSegment", optional=True),
                Sequence("POPULATE", optional=True),
            ),
        ),
        "AS",
        Ref("SelectableGrammar"),
        Ref("TableEndClauseSegment", optional=True),
    )


class DropTableStatementSegment(ansi.DropTableStatementSegment):
    """A `DROP TABLE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_table_statement"

    match_grammar = Sequence(
        "DROP",
        Ref.keyword("TEMPORARY", optional=True),
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        Ref.keyword("SYNC", optional=True),
    )


class DropDatabaseStatementSegment(ansi.DropDatabaseStatementSegment):
    """A `DROP DATABASE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_database_statement"

    match_grammar = Sequence(
        "DROP",
        "DATABASE",
        Ref("IfExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        Ref.keyword("SYNC", optional=True),
    )


class DropDictionaryStatementSegment(BaseSegment):
    """A `DROP DICTIONARY` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_dictionary_statement"

    match_grammar = Sequence(
        "DROP",
        "DICTIONARY",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref.keyword("SYNC", optional=True),
    )


class DropUserStatementSegment(ansi.DropUserStatementSegment):
    """A `DROP USER` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_user_statement"

    match_grammar = Sequence(
        "DROP",
        "USER",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class DropRoleStatementSegment(ansi.DropRoleStatementSegment):
    """A `DROP ROLE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_user_statement"

    match_grammar = Sequence(
        "DROP",
        "ROLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class DropQuotaStatementSegment(BaseSegment):
    """A `DROP QUOTA` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_quota_statement"

    match_grammar = Sequence(
        "DROP",
        "QUOTA",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class DropSettingProfileStatementSegment(BaseSegment):
    """A `DROP setting PROFILE` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_setting_profile_statement"

    match_grammar = Sequence(
        "DROP",
        Delimited(
            Ref("NakedIdentifierSegment"),
            min_delimiters=0,
        ),
        "PROFILE",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class DropViewStatementSegment(ansi.DropViewStatementSegment):
    """A `DROP VIEW` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_view_statement"

    match_grammar = Sequence(
        "DROP",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("OnClusterClauseSegment", optional=True),
        Ref.keyword("SYNC", optional=True),
    )


class DropFunctionStatementSegment(ansi.DropFunctionStatementSegment):
    """A `DROP FUNCTION` statement.

    As specified in
    https://clickhouse.com/docs/en/sql-reference/statements/drop/
    """

    type = "drop_function_statement"

    match_grammar = Sequence(
        "DROP",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        Ref("OnClusterClauseSegment", optional=True),
    )


class SystemMergesSegment(BaseSegment):
    """A `SYSTEM ... MERGES` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_merges_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "MERGES",
        OneOf(
            Sequence(
                "ON",
                "VOLUME",
                Ref("ObjectReferenceSegment"),
            ),
            Ref("TableReferenceSegment"),
        ),
    )


class SystemTTLMergesSegment(BaseSegment):
    """A `SYSTEM ... TTL MERGES` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_ttl_merges_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "TTL",
        "MERGES",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemMovesSegment(BaseSegment):
    """A `SYSTEM ... MOVES` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_moves_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "MOVES",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemReplicaSegment(BaseSegment):
    """A `SYSTEM ... REPLICA` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_replica_segment"

    match_grammar = OneOf(
        Sequence(
            "SYNC",
            "REPLICA",
            Ref("OnClusterClauseSegment", optional=True),
            Ref("TableReferenceSegment"),
            Sequence("STRICT", optional=True),
        ),
        Sequence(
            "DROP",
            "REPLICA",
            Ref("SingleIdentifierGrammar"),
            Sequence(
                "FROM",
                OneOf(
                    Sequence(
                        "DATABASE",
                        Ref("ObjectReferenceSegment"),
                    ),
                    Sequence(
                        "TABLE",
                        Ref("TableReferenceSegment"),
                    ),
                    Sequence(
                        "ZKPATH",
                        Ref("PathSegment"),
                    ),
                ),
                optional=True,
            ),
        ),
        Sequence(
            "RESTART",
            "REPLICA",
            Ref("TableReferenceSegment"),
        ),
        Sequence(
            "RESTORE",
            "REPLICA",
            Ref("TableReferenceSegment"),
            Ref("OnClusterClauseSegment", optional=True),
        ),
    )


class SystemFilesystemSegment(BaseSegment):
    """A `SYSTEM ... FILESYSTEM` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_filesystem_segment"

    match_grammar = Sequence(
        "DROP",
        "FILESYSTEM",
        "CACHE",
    )


class SystemReplicatedSegment(BaseSegment):
    """A `SYSTEM ... REPLICATED` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_replicated_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "REPLICATED",
        "SENDS",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemReplicationSegment(BaseSegment):
    """A `SYSTEM ... REPLICATION` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_replication_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "REPLICATION",
        "QUEUES",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemFetchesSegment(BaseSegment):
    """A `SYSTEM ... FETCHES` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_fetches_segment"

    match_grammar = Sequence(
        OneOf(
            "START",
            "STOP",
        ),
        "FETCHES",
        Ref("TableReferenceSegment", optional=True),
    )


class SystemDistributedSegment(BaseSegment):
    """A `SYSTEM ... DISTRIBUTED` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_distributed_segment"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                OneOf(
                    "START",
                    "STOP",
                ),
                "DISTRIBUTED",
                "SENDS",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "FLUSH",
                "DISTRIBUTED",
                Ref("TableReferenceSegment"),
            ),
        ),
        # Ref("TableReferenceSegment"),
    )


class SystemModelSegment(BaseSegment):
    """A `SYSTEM ... MODEL` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_model_segment"

    match_grammar = Sequence(
        "RELOAD",
        OneOf(
            Sequence(
                "MODELS",
                Ref("OnClusterClauseSegment", optional=True),
            ),
            Sequence(
                "MODEL",
                AnySetOf(
                    Ref("OnClusterClauseSegment", optional=True),
                    Ref("PathSegment"),
                ),
            ),
        ),
    )


class SystemFileSegment(BaseSegment):
    """A `SYSTEM ... FILE` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_file_segment"

    match_grammar = Sequence(
        "SYNC",
        "FILE",
        "CACHE",
    )


class SystemUnfreezeSegment(BaseSegment):
    """A `SYSTEM ... UNFREEZE` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_unfreeze_segment"

    match_grammar = Sequence(
        "UNFREEZE",
        "WITH",
        "NAME",
        Ref("ObjectReferenceSegment"),
    )


class SystemStatementSegment(BaseSegment):
    """A `SYSTEM ...` statement.

    https://clickhouse.com/docs/en/sql-reference/statements/system
    """

    type = "system_statement"

    match_grammar: Matchable = Sequence(
        "SYSTEM",
        OneOf(
            Ref("SystemMergesSegment"),
            Ref("SystemTTLMergesSegment"),
            Ref("SystemMovesSegment"),
            Ref("SystemReplicaSegment"),
            Ref("SystemReplicatedSegment"),
            Ref("SystemReplicationSegment"),
            Ref("SystemFetchesSegment"),
            Ref("SystemDistributedSegment"),
            Ref("SystemFileSegment"),
            Ref("SystemFilesystemSegment"),
            Ref("SystemUnfreezeSegment"),
            Ref("SystemModelSegment"),
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CreateMaterializedViewStatementSegment"),
            Ref("DropDictionaryStatementSegment"),
            Ref("DropQuotaStatementSegment"),
            Ref("DropSettingProfileStatementSegment"),
            Ref("SystemStatementSegment"),
        ]
    )
