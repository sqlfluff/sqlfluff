"""The Snowflake dialect.

Inherits from Postgres.

Based on https://docs.snowflake.com/en/sql-reference-commands.html
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    OneOf,
    Ref,
    Sequence,
    AnyNumberOf,
    SymbolSegment,
    Bracketed,
    Anything,
    Delimited,
    StartsWith,
    Indent,
    Dedent,
    RegexLexer,
    StringLexer,
    CodeSegment,
    StringParser,
    NamedParser,
    RegexParser,
)


ansi_dialect = load_raw_dialect("ansi")
postgres_dialect = load_raw_dialect("postgres")

snowflake_dialect = postgres_dialect.copy_as("snowflake")

snowflake_dialect.patch_lexer_matchers(
    [
        # In snowflake, a double single quote resolves as a single quote in the string.
        # https://docs.snowflake.com/en/sql-reference/data-types-text.html#single-quoted-string-constants
        RegexLexer("single_quote", r"'([^']|'')*'", CodeSegment),
    ]
)

snowflake_dialect.insert_lexer_matchers(
    [
        # Keyword assigner needed for keyword functions.
        StringLexer("parameter_assigner", "=>", CodeSegment),
        # Column selector
        # https://docs.snowflake.com/en/sql-reference/sql/select.html#parameters
        RegexLexer("column_selector", r"\$[0-9]+", CodeSegment),
    ],
    before="not_equal",
)

snowflake_dialect.sets("unreserved_keywords").update(
    [
        "API",
        "AUTHORIZATIONS",
        "BERNOULLI",
        "BLOCK",
        "DELEGATED",
        "HISTORY",
        "LATERAL",
        "NETWORK",
        "PIPE",
        "PIPES",
        "QUERIES",
        "REGIONS",
        "REMOVE",
        "SECURE",
        "SEED",
        "TERSE",
        "UNSET",
        "TABULAR",
    ]
)


snowflake_dialect.sets("reserved_keywords").update(
    [
        "CLONE",
        "MASKING",
        "NOTIFICATION",
        "PIVOT",
        "SAMPLE",
        "TABLESAMPLE",
        "UNPIVOT",
    ]
)


snowflake_dialect.add(
    # In snowflake, these are case sensitive even though they're not quoted
    # so they need a different `name` and `type` so they're not picked up
    # by other rules.
    ParameterAssignerSegment=StringParser(
        "=>", SymbolSegment, name="parameter_assigner", type="parameter_assigner"
    ),
    NakedSemiStructuredElementSegment=RegexParser(
        r"[A-Z0-9_]*",
        CodeSegment,
        name="naked_semi_structured_element",
        type="semi_structured_element",
    ),
    QuotedSemiStructuredElementSegment=NamedParser(
        "double_quote",
        CodeSegment,
        name="quoted_semi_structured_element",
        type="semi_structured_element",
    ),
    ColumnIndexIdentifierSegment=RegexParser(
        r"\$[0-9]+",
        CodeSegment,
        name="column_index_identifier_segment",
        type="identifier",
    ),
)

snowflake_dialect.replace(
    Accessor_Grammar=AnyNumberOf(
        Ref("ArrayAccessorSegment"),
        # Add in semi structured expressions
        Ref("SemiStructuredAccessorSegment"),
    ),
    PreTableFunctionKeywordsGrammar=OneOf(Ref("LateralKeywordSegment")),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("DatetimeUnitSegment"),
        Ref("NamedParameterExpressionSegment"),
        Sequence(
            Ref("ExpressionSegment"),
            Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
        ),
    ),
    JoinLikeClauseGrammar=Sequence(
        AnyNumberOf(
            Ref("FromAtExpressionSegment"),
            Ref("FromBeforeExpressionSegment"),
            Ref("FromPivotExpressionSegment"),
            Ref("FromUnpivotExpressionSegment"),
            Ref("SamplingExpressionSegment"),
            min_times=1,
        ),
        Ref("TableAliasExpressionSegment", optional=True),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("ColumnIndexIdentifierSegment"),
    ),
    PostFunctionGrammar=Sequence(
        Ref("WithinGroupClauseSegment", optional=True),
        Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
        Ref("OverClauseSegment", optional=True),
    ),
)


@snowflake_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """A generic segment, to any of its child subsegments."""

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("UseStatementSegment"),
            Ref("CreateStatementSegment"),
            Ref("CreateCloneStatementSegment"),
            Ref("ShowStatementSegment"),
            Ref("AlterUserSegment"),
            Ref("AlterSessionStatementSegment"),
        ],
        remove=[
            Ref("CreateTypeStatementSegment"),
            Ref("CreateExtensionStatementSegment"),
            Ref("CreateIndexStatementSegment"),
            Ref("DropIndexStatementSegment"),
            Ref("CreateFunctionStatementSegment"),
        ],
    )


@snowflake_dialect.segment()
class CreateStatementCommentSegment(BaseSegment):
    """A comment in a create view/table statement.

    e.g. comment = 'a new view/table'
    Please note that, for column comment, the syntax in Snowflake is
    `COMMENT 'text'` (Without the `=`).
    """

    type = "snowflake_comment"
    match_grammar = Sequence(
        Ref.keyword("COMMENT"),
        Ref("EqualsSegment"),
        Ref("LiteralGrammar"),
    )


@snowflake_dialect.segment()
class TableAliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause, optionally with column aliasing."""

    type = "table_alias_expression"
    match_grammar = Sequence(
        Ref("AliasExpressionSegment"),
        # Optional column aliases too.
        Bracketed(
            Delimited(Ref("SingleIdentifierGrammar"), delimiter=Ref("CommaSegment")),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class FromAtExpressionSegment(BaseSegment):
    """An AT expression."""

    type = "from_at_expression"
    match_grammar = Sequence("AT", Bracketed(Anything()))

    parse_grammar = Sequence(
        "AT",
        Bracketed(
            OneOf("TIMESTAMP", "OFFSET", "STATEMENT"),
            Ref("ParameterAssignerSegment"),
            Ref("ExpressionSegment"),
        ),
    )


@snowflake_dialect.segment()
class FromBeforeExpressionSegment(BaseSegment):
    """A BEFORE expression."""

    type = "from_before_expression"
    match_grammar = Sequence("BEFORE", Bracketed(Anything()))

    parse_grammar = Sequence(
        "BEFORE",
        Bracketed(
            OneOf("TIMESTAMP", "OFFSET", "STATEMENT"),
            Ref("ParameterAssignerSegment"),
            Ref("ExpressionSegment"),
        ),
    )


@snowflake_dialect.segment()
class FromPivotExpressionSegment(BaseSegment):
    """A PIVOT expression."""

    type = "from_pivot_expression"
    match_grammar = Sequence("PIVOT", Bracketed(Anything()))

    parse_grammar = Sequence(
        "PIVOT",
        Bracketed(
            Ref("FunctionSegment"),
            "FOR",
            Ref("SingleIdentifierGrammar"),
            "IN",
            Bracketed(Delimited(Ref("LiteralGrammar"), delimiter=Ref("CommaSegment"))),
        ),
    )


@snowflake_dialect.segment()
class FromUnpivotExpressionSegment(BaseSegment):
    """An UNPIVOT expression."""

    type = "from_unpivot_expression"
    match_grammar = Sequence("UNPIVOT", Bracketed(Anything()))

    parse_grammar = Sequence(
        "UNPIVOT",
        Bracketed(
            Ref("SingleIdentifierGrammar"),
            "FOR",
            Ref("SingleIdentifierGrammar"),
            "IN",
            Bracketed(
                Delimited(Ref("SingleIdentifierGrammar"), delimiter=Ref("CommaSegment"))
            ),
        ),
    )


@snowflake_dialect.segment()
class SamplingExpressionSegment(BaseSegment):
    """A sampling expression."""

    type = "snowflake_sample_expression"
    match_grammar = Sequence(
        OneOf("SAMPLE", "TABLESAMPLE"),
        OneOf("BERNOULLI", "ROW", "SYSTEM", "BLOCK", optional=True),
        Bracketed(Ref("NumericLiteralSegment"), Ref.keyword("ROWS", optional=True)),
        Sequence(
            OneOf("REPEATABLE", "SEED"),
            Bracketed(Ref("NumericLiteralSegment")),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class NamedParameterExpressionSegment(BaseSegment):
    """A keyword expression.

    e.g. 'input => custom_fields'

    """

    type = "snowflake_keyword_expression"
    match_grammar = Sequence(
        Ref("ParameterNameSegment"),
        Ref("ParameterAssignerSegment"),
        OneOf(
            Ref("LiteralGrammar"),
            Ref("ColumnReferenceSegment"),
            Ref("ExpressionSegment"),
        ),
    )


@snowflake_dialect.segment()
class SemiStructuredAccessorSegment(BaseSegment):
    """A semi-structured data accessor segment.

    https://docs.snowflake.com/en/user-guide/semistructured-considerations.html
    """

    type = "snowflake_semi_structured_expression"
    match_grammar = Sequence(
        Ref("ColonSegment"),
        OneOf(
            Ref("NakedSemiStructuredElementSegment"),
            Ref("QuotedSemiStructuredElementSegment"),
        ),
        Ref("ArrayAccessorSegment", optional=True),
        AnyNumberOf(
            Sequence(
                OneOf(
                    # Can be delimited by dots or colons
                    Ref("DotSegment"),
                    Ref("ColonSegment"),
                ),
                OneOf(
                    Ref("NakedSemiStructuredElementSegment"),
                    Ref("QuotedSemiStructuredElementSegment"),
                ),
                Ref("ArrayAccessorSegment", optional=True),
                allow_gaps=True,
            ),
            allow_gaps=True,
        ),
        allow_gaps=True,
    )


@snowflake_dialect.segment(replace=True)
class SelectClauseModifierSegment(
    ansi_dialect.get_segment("SelectClauseModifierSegment")  # type: ignore
):
    """Things that come after SELECT but before the columns.

    In snowflake we go back to similar functionality as the ANSI
    version in the root dialect, without the things added in
    postgres.
    """


@snowflake_dialect.segment()
class QualifyClauseSegment(BaseSegment):
    """A `QUALIFY` clause like in `SELECT`.

    https://docs.snowflake.com/en/sql-reference/constructs/qualify.html
    """

    type = "having_clause"
    match_grammar = StartsWith(
        "QUALIFY",
        terminator=OneOf(
            "ORDER",
            "LIMIT",
        ),
    )
    parse_grammar = Sequence(
        "QUALIFY",
        Indent,
        OneOf(
            Bracketed(
                Ref("ExpressionSegment"),
            ),
            Ref("ExpressionSegment"),
        ),
        Dedent,
    )


@snowflake_dialect.segment(replace=True)
class SelectStatementSegment(ansi_dialect.get_segment("SelectStatementSegment")):  # type: ignore
    """A snowflake `SELECT` statement including optional Qualify.

    https://docs.snowflake.com/en/sql-reference/constructs/qualify.html
    """

    type = "select_statement"
    match_grammar = StartsWith(
        # NB: In bigquery, the select clause may include an EXCEPT, which
        # will also match the set operator, but by starting with the whole
        # select clause rather than just the SELECT keyword, we normally
        # mitigate that here. But this isn't BigQuery! So we can be more
        # efficient and just just the keyword.
        "SELECT",
        terminator=Ref("SetOperatorSegment"),
    )

    parse_grammar = ansi_dialect.get_segment(
        "SelectStatementSegment"
    ).parse_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OrderByClauseSegment", optional=True),
    )


@snowflake_dialect.segment()
class CreateCloneStatementSegment(BaseSegment):
    """A snowflake `CREATE ... CLONE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-clone.html
    """

    type = "create_clone_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        OneOf(
            "DATABASE",
            "SCHEMA",
            "TABLE",
            "SEQUENCE",
            Sequence("FILE", "FORMAT"),
            "STAGE",
            "STREAM",
            "TASK",
        ),
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("SingleIdentifierGrammar"),
        "CLONE",
        Ref("SingleIdentifierGrammar"),
        OneOf(
            Ref("FromAtExpressionSegment"),
            Ref("FromBeforeExpressionSegment"),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class CreateStatementSegment(BaseSegment):
    """A snowflake `CREATE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create.html
    """

    type = "create_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        OneOf(
            Sequence("NETWORK", "POLICY"),
            Sequence("RESOURCE", "MONITOR"),
            "SHARE",
            "ROLE",
            "USER",
            "WAREHOUSE",
            Sequence("NOTIFICATION", "INTEGRATION"),
            Sequence("SECURITY", "INTEGRATION"),
            Sequence("STORAGE", "INTEGRATION"),
            Sequence("EXTERNAL", "TABLE"),
            "VIEW",
            Sequence("MATERIALIZED", "VIEW"),
            Sequence("SECURE", "VIEW"),
            Sequence("MASKING", "POLICY"),
            "PIPE",
            "FUNCTION",
            Sequence("EXTERNAL", "FUNCTION"),
            "PROCEDURE",
            # Objects that also support clone
            "DATABASE",
            "SCHEMA",
            "TABLE",
            "SEQUENCE",
            Sequence("FILE", "FORMAT"),
            "STAGE",
            "STREAM",
            "TASK",
        ),
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref("CreateStatementCommentSegment", optional=True),
        Ref.keyword("AS", optional=True),
        Ref("SelectStatementSegment", optional=True),
    )


@snowflake_dialect.segment()
class ShowStatementSegment(BaseSegment):
    """A snowflake `SHOW` statement.

    https://docs.snowflake.com/en/sql-reference/sql/show.html
    """

    _object_types_plural = OneOf(
        "PARAMETERS",
        Sequence("GLOBAL", "ACCOUNTS"),
        "REGIONS",
        Sequence("REPLICATION", "ACCOUNTS"),
        Sequence("REPLICATION", "DATABASES"),
        "PARAMETERS",
        "VARIABLES",
        "TRANSACTIONS",
        "LOCKS",
        "PARAMETERS",
        "FUNCTIONS",
        Sequence("NETWORK", "POLICIES"),
        "SHARES",
        "ROLES",
        "GRANTS",
        "USERS",
        "WAREHOUSES",
        "DATABASES",
        Sequence(
            OneOf("API", "NOTIFICATION", "SECURITY", "STORAGE", optional=True),
            "INTEGRATIONS",
        ),
        "SCHEMAS",
        "OBJECTS",
        "TABLES",
        Sequence("EXTERNAL", "TABLES"),
        "VIEWS",
        Sequence("MATERIALIZED", "VIEWS"),
        Sequence("MASKING", "POLICIES"),
        "COLUMNS",
        Sequence("FILE", "FORMATS"),
        "SEQUENCES",
        "STAGES",
        "PIPES",
        "STREAMS",
        "TASKS",
        Sequence("USER", "FUNCTIONS"),
        Sequence("EXTERNAL", "FUNCTIONS"),
        "PROCEDURES",
        Sequence("FUTURE", "GRANTS"),
    )

    _object_scope_types = OneOf(
        "ACCOUNT",
        "SESSION",
        Sequence(
            OneOf(
                "DATABASE",
                "SCHEMA",
                "SHARE",
                "ROLE",
                "TABLE",
                "TASK",
                "USER",
                "WAREHOUSE",
                "VIEW",
            ),
            Ref("ObjectReferenceSegment", optional=True),
        ),
    )

    type = "show_statement"

    match_grammar = Sequence(
        "SHOW",
        OneOf("TERSE", optional=True),
        _object_types_plural,
        OneOf("HISTORY", optional=True),
        Sequence("LIKE", Ref("QuotedLiteralSegment"), optional=True),
        Sequence(
            OneOf("ON", "TO", "OF", "IN"),
            OneOf(
                Sequence(_object_scope_types),
                Ref("ObjectReferenceSegment"),
            ),
            optional=True,
        ),
        Sequence("STARTS", "WITH", Ref("QuotedLiteralSegment"), optional=True),
        Sequence("WITH", "PRIMARY", Ref("ObjectReferenceSegment"), optional=True),
        Sequence(
            Ref("LimitClauseSegment"),
            Sequence("FROM", Ref("QuotedLiteralSegment"), optional=True),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class AlterUserSegment(BaseSegment):
    """`ALTER USER` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-user.html

    All user parameters can be found here
    https://docs.snowflake.com/en/sql-reference/parameters.html
    """

    type = "alter_user"

    match_grammar = StartsWith(
        Sequence("ALTER", "USER"),
    )
    parse_grammar = Sequence(
        "ALTER",
        "USER",
        Sequence("IF", "EXISTS", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("ObjectReferenceSegment")),
            Sequence("RESET", "PASSWORD"),
            Sequence("ABORT", "ALL", "QUERIES"),
            Sequence(
                "ADD",
                "DELEGATED",
                "AUTHORIZATION",
                "OF",
                "ROLE",
                Ref("ObjectReferenceSegment"),
                "TO",
                "SECURITY",
                "INTEGRATION",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "REMOVE",
                "DELEGATED",
                OneOf(
                    Sequence(
                        "AUTHORIZATION", "OF", "ROLE", Ref("ObjectReferenceSegment")
                    ),
                    "AUTHORIZATIONS",
                ),
                "FROM",
                "SECURITY",
                "INTEGRATION",
                Ref("ObjectReferenceSegment"),
            ),
            # Snowflake supports the SET command with space delimitted parameters, but it also supports
            # using commas which is better supported by `Delimited`, so we will just use that.
            Sequence(
                "SET",
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        OneOf(Ref("LiteralGrammar"), Ref("ObjectReferenceSegment")),
                    ),
                ),
            ),
            Sequence("UNSET", Delimited(Ref("ParameterNameSegment"))),
        ),
    )


@snowflake_dialect.segment(replace=True)
class CreateRoleStatementSegment(BaseSegment):
    """A `CREATE ROLE` statement.

    Redefined because it's much simpler than postgres.
    https://docs.snowflake.com/en/sql-reference/sql/create-role.html
    """

    type = "create_role_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence(
            "OR",
            "REPLACE",
            optional=True,
        ),
        "ROLE",
        Sequence(
            "IF",
            "NOT",
            "EXISTS",
            optional=True,
        ),
        Ref("ObjectReferenceSegment"),
        Sequence(
            "COMMENT",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


@snowflake_dialect.segment(replace=True)
class ExplainStatementSegment(ansi_dialect.get_segment("ExplainStatementSegment")):  # type: ignore
    """An `Explain` statement.

    EXPLAIN [ USING { TABULAR | JSON | TEXT } ] <statement>

    https://docs.snowflake.com/en/sql-reference/sql/explain.html
    """

    parse_grammar = Sequence(
        "EXPLAIN",
        Sequence(
            "USING",
            OneOf("TABULAR", "JSON", "TEXT"),
            optional=True,
        ),
        ansi_dialect.get_segment("ExplainStatementSegment").explainable_stmt,
    )


@snowflake_dialect.segment()
class AlterSessionStatementSegment(BaseSegment):
    """Snowflake's ALTER SESSION statement.

    ```
    ALTER SESSION SET <param_name> = <param_value>;
    ALTER SESSION UNSET <param_name>, [ , <param_name> , ... ];
    ```

    https://docs.snowflake.com/en/sql-reference/sql/alter-session.html
    """

    type = "alter_session_statement"

    match_grammar = Sequence(
        "ALTER",
        "SESSION",
        OneOf(
            Ref("AlterSessionSetClauseSegment"),
            Ref("AlterSessionUnsetClauseSegment"),
        ),
    )


@snowflake_dialect.segment()
class AlterSessionSetClauseSegment(BaseSegment):
    """Snowflake's ALTER SESSION SET clause.

    ```
    [ALTER SESSION] SET <param_name> = <param_value>;
    ```

    https://docs.snowflake.com/en/sql-reference/sql/alter-session.html
    """

    type = "alter_session_set_statement"

    match_grammar = Sequence(
        "SET",
        Ref("ParameterNameSegment"),
        Ref("EqualsSegment"),
        OneOf(
            Ref("BooleanLiteralGrammar"),
            Ref("QuotedLiteralSegment"),
            Ref("NumericLiteralSegment"),
        ),
    )


@snowflake_dialect.segment()
class AlterSessionUnsetClauseSegment(BaseSegment):
    """Snowflake's ALTER SESSION UNSET clause.

    ```
    [ALTER SESSION] UNSET <param_name>, [ , <param_name> , ... ];
    ```

    https://docs.snowflake.com/en/sql-reference/sql/alter-session.html
    """

    type = "alter_session_unset_clause"

    match_grammar = Sequence(
        "UNSET",
        Delimited(Ref("ParameterNameSegment"), delimiter=Ref("CommaSegment")),
    )
