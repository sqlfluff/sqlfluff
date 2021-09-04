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
from sqlfluff.core.parser.grammar.anyof import OptionallyBracketed

ansi_dialect = load_raw_dialect("ansi")
snowflake_dialect = ansi_dialect.copy_as("snowflake")

# Add all Snowflake keywords


# These are Reserved Keywords in Snowflake so move them
snowflake_dialect.sets("unreserved_keywords").discard("ILIKE")
snowflake_dialect.sets("unreserved_keywords").discard("INCREMENT")
snowflake_dialect.sets("unreserved_keywords").discard("MINUS")
snowflake_dialect.sets("unreserved_keywords").discard("QUALIFY")
snowflake_dialect.sets("unreserved_keywords").discard("REGEXP")
snowflake_dialect.sets("unreserved_keywords").discard("RLIKE")
snowflake_dialect.sets("unreserved_keywords").discard("SOME")
snowflake_dialect.sets("unreserved_keywords").discard("TABLESAMPLE")

# Add above along with the
snowflake_dialect.sets("reserved_keywords").update(
    [
        "ILIKE",
        "INCREMENT",
        "MINUS",
        "PIVOT",
        "QUALIFY",
        "REGEXP",
        "RLIKE",
        "SAMPLE",
        "SOME",
        "TABLESAMPLE",
    ]
)

snowflake_dialect.sets("unreserved_keywords").update(
    [
        "ALLOW_OVERLAPPING_EXECUTION",
        "API",
        "AUTHORIZATIONS",
        "AUTO_INGEST",
        "AVRO",
        "AWS_SNS_TOPIC",
        "BERNOULLI",
        "BLOCK",
        "CLONE",
        "DELEGATED",
        "FILES",
        "FILE_FORMAT",
        "FORMAT_NAME",
        "HISTORY",
        "LATERAL",
        "MASKING",
        "NETWORK",
        "NEXTVAL",
        "NOTIFICATION",
        "ORC",
        "PARQUET",
        "PATTERN",
        "PIPE",
        "PIPES",
        "POLICY",
        "QUERIES",
        "REGIONS",
        "REMOVE",
        "RESUME",
        "SAMPLE",
        "SCHEDULE",
        "SECURE",
        "SEED",
        "SIZE_LIMIT",
        "SUSPEND",
        "TERSE",
        "UNPIVOT",
        "UNSET",
        "TABULAR",
    ]
)

snowflake_dialect.patch_lexer_matchers(
    [
        # In snowflake, a double single quote resolves as a single quote in the string.
        # https://docs.snowflake.com/en/sql-reference/data-types-text.html#single-quoted-string-constants
        RegexLexer("single_quote", r"'([^'\\]|\\.|'')*'", CodeSegment),
    ]
)

snowflake_dialect.insert_lexer_matchers(
    [
        # Keyword assigner needed for keyword functions.
        StringLexer("parameter_assigner", "=>", CodeSegment),
        StringLexer("function_assigner", "->", CodeSegment),
        StringLexer("atsign", "@", CodeSegment),
        # Column selector
        # https://docs.snowflake.com/en/sql-reference/sql/select.html#parameters
        RegexLexer("column_selector", r"\$[0-9]+", CodeSegment),
        RegexLexer(
            "dollar_literal",
            r"[$][a-zA-Z0-9_.]*",
            CodeSegment,
        ),
    ],
    before="not_equal",
)

snowflake_dialect.add(
    # In snowflake, these are case sensitive even though they're not quoted
    # so they need a different `name` and `type` so they're not picked up
    # by other rules.
    ParameterAssignerSegment=StringParser(
        "=>", SymbolSegment, name="parameter_assigner", type="parameter_assigner"
    ),
    FunctionAssignerSegment=StringParser(
        "->", SymbolSegment, name="function_assigner", type="function_assigner"
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
    LocalVariableNameSegment=RegexParser(
        r"[a-zA-Z0-9_]*",
        CodeSegment,
        name="declared_variable",
        type="variable",
    ),
    ReferencedVariableNameSegment=RegexParser(
        r"\$[A-Z][A-Z0-9_]*",
        CodeSegment,
        name="referenced_variable",
        type="variable",
        trim_chars=("$",),
    ),
    DoubleQuotedLiteralSegment=NamedParser(
        "double_quote",
        CodeSegment,
        name="quoted_literal",
        type="literal",
        trim_chars=('"',),
    ),
    AtSignLiteralSegment=NamedParser(
        "atsign",
        CodeSegment,
        name="atsign_literal",
        type="literal",
        trim_chars=("@",),
    ),
    ReturnNRowsSegment=RegexParser(
        r"RETURN_[0-9][0-9]*_ROWS",
        CodeSegment,
        name="literal",
        type="literal",
    ),
)

snowflake_dialect.replace(
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("ReferencedVariableNameSegment"),
        ]
    ),
    Accessor_Grammar=AnyNumberOf(
        Ref("ArrayAccessorSegment"),
        # Add in semi structured expressions
        Ref("SemiStructuredAccessorSegment"),
    ),
    PreTableFunctionKeywordsGrammar=OneOf(Ref("LateralKeywordSegment")),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("DatetimeUnitSegment"),
        Ref("NamedParameterExpressionSegment"),
        Ref("ReferencedVariableNameSegment"),
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
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`.

    Snowflake supports Cube, Rollup, and Grouping Sets

    https://docs.snowflake.com/en/sql-reference/constructs/group-by.html
    """

    type = "group_by_clause"
    match_grammar = StartsWith(
        Sequence("GROUP", "BY"),
        terminator=OneOf("ORDER", "LIMIT", "HAVING", "QUALIFY", "WINDOW"),
        enforce_whitespace_preceeding_terminator=True,
    )
    parse_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        Delimited(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingSetsClauseSegment"),
            ),
            terminator=OneOf("ORDER", "LIMIT", "HAVING", "QUALIFY", "WINDOW"),
        ),
        Dedent,
    )


@snowflake_dialect.segment()
class CubeRollupClauseSegment(BaseSegment):
    """`CUBE` / `ROLLUP` clause within the `GROUP BY` clause."""

    type = "cube_rollup_clause"
    match_grammar = StartsWith(
        OneOf("CUBE", "ROLLUP"),
        terminator=OneOf(
            "HAVING",
            "QUALIFY",
            "ORDER",
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
    )
    parse_grammar = Sequence(
        OneOf("CUBE", "ROLLUP"),
        Bracketed(
            Ref("GroupingExpressionList"),
        ),
    )


@snowflake_dialect.segment()
class GroupingSetsClauseSegment(BaseSegment):
    """`GROUPING SETS` clause within the `GROUP BY` clause."""

    type = "grouping_sets_clause"
    match_grammar = StartsWith(
        Sequence("GROUPING", "SETS"),
        terminator=OneOf(
            "HAVING",
            "QUALIFY",
            "ORDER",
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
    )
    parse_grammar = Sequence(
        "GROUPING",
        "SETS",
        Bracketed(
            Delimited(
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingExpressionList"),
                Bracketed(),  # Allows empty parentheses
            )
        ),
    )


@snowflake_dialect.segment()
class GroupingExpressionList(BaseSegment):
    """Grouping expression list within `CUBE` / `ROLLUP` `GROUPING SETS`."""

    type = "grouping_expression_list"
    match_grammar = Delimited(
        OneOf(
            Bracketed(Delimited(Ref("ExpressionSegment"))),
            Ref("ExpressionSegment"),
        )
    )


@snowflake_dialect.segment(replace=True)
class ValuesClauseSegment(BaseSegment):
    """A `VALUES` clause like in `INSERT`."""

    type = "values_clause"
    match_grammar = Sequence(
        OneOf("VALUE", "VALUES"),
        Delimited(
            Bracketed(
                Delimited(
                    Ref("LiteralGrammar"),
                    Ref("IntervalExpressionSegment"),
                    Ref("FunctionSegment"),
                    "DEFAULT",  # not in `FROM` clause, rule?
                    ephemeral_name="ValuesClauseElements",
                )
            ),
        ),
        Ref("AliasExpressionSegment", optional=True),
    )


@snowflake_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement."""

    match_grammar = Sequence(
        "AS",
        OneOf(Ref("QuotedLiteralSegment"), Ref("DollarQuotedLiteralSegment")),
        Sequence(
            "LANGUAGE",
            # Not really a parameter, but best fit for now.
            Ref("ParameterNameSegment"),
            optional=True,
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
            Ref("AlterTaskStatementSegment"),
            Ref("SetAssignmentStatementSegment"),
            Ref("CallStoredProcedureSegment"),
            Ref("MergeStatementSegment"),
            Ref("AlterTableColumnStatementSegment"),
            Ref("CopyIntoStatementSegment"),
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
class SetAssignmentStatementSegment(BaseSegment):
    """A `SET` statement.

    https://docs.snowflake.com/en/sql-reference/sql/set.html
    """

    type = "set_statement"

    match_grammar = OneOf(
        Sequence(
            "SET",
            Ref("LocalVariableNameSegment"),
            Ref("EqualsSegment"),
            Ref("ExpressionSegment"),
        ),
        Sequence(
            "SET",
            Bracketed(
                Delimited(
                    Ref("LocalVariableNameSegment"), delimiter=Ref("CommaSegment")
                )
            ),
            Ref("EqualsSegment"),
            Bracketed(
                Delimited(
                    Ref("ExpressionSegment"),
                    delimiter=Ref("CommaSegment"),
                ),
            ),
        ),
    )


@snowflake_dialect.segment()
class CallStoredProcedureSegment(BaseSegment):
    """This is a CALL statement used to execute a stored procedure.

    https://docs.snowflake.com/en/sql-reference/sql/call.html
    """

    type = "call_segment"

    match_grammar = Sequence(
        "CALL",
        Ref("FunctionSegment"),
    )


@snowflake_dialect.segment()
class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions.

    https://docs.snowflake.com/en/sql-reference/functions/listagg.html.
    https://docs.snowflake.com/en/sql-reference/functions/array_agg.html.
    """

    type = "withingroup_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Anything(optional=True)),
    )

    parse_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Ref("OrderByClauseSegment", optional=True)),
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
class AlterTableColumnStatementSegment(BaseSegment):
    """An `ALTER TABLE .. ALTER COLUMN` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-table-column.html

    """

    type = "alter_table_column_statement"
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf("ALTER", "MODIFY"),
        OptionallyBracketed(
            Delimited(
                OneOf(
                    # Add things
                    Sequence(
                        Ref.keyword("COLUMN", optional=True),
                        Ref("SingleIdentifierGrammar"),
                        OneOf(
                            Sequence("DROP", "DEFAULT"),
                            Sequence(
                                "SET",
                                "DEFAULT",
                                Ref("NakedIdentifierSegment"),
                                Ref("DotSegment"),
                                "NEXTVAL",
                            ),
                            Sequence(
                                OneOf("SET", "DROP", optional=True), "NOT", "NULL"
                            ),
                            Sequence(
                                Sequence(
                                    Sequence("SET", "DATA", optional=True),
                                    "TYPE",
                                    optional=True,
                                ),
                                Ref("DatatypeSegment"),
                            ),
                            Sequence("COMMENT", Ref("QuotedLiteralSegment")),
                        ),
                    ),
                    Sequence(
                        "COLUMN",
                        Ref("SingleIdentifierGrammar"),
                        OneOf("SET", "UNSET"),
                        "MASKING",
                        "POLICY",
                        Ref("FunctionNameIdentifierSegment", optional=True),
                    ),
                ),
            ),
        ),
    )


@snowflake_dialect.segment(replace=True)
class CommentClauseSegment(BaseSegment):
    """A comment clause.

    e.g. COMMENT 'view/table/column description'
    """

    type = "comment_clause"
    match_grammar = Sequence(
        "COMMENT", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")
    )


@snowflake_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(ansi_dialect.get_segment("SelectStatementSegment")):  # type: ignore
    """A snowflake unordered `SELECT` statement including optional Qualify.

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
        "UnorderedSelectStatementSegment"
    ).parse_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OverlapsClauseSegment", optional=True),
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
        # Next set are Pipe statements https://docs.snowflake.com/en/sql-reference/sql/create-pipe.html
        Sequence(
            Sequence(
                "AUTO_INGEST",
                Ref("EqualsSegment"),
                OneOf("TRUE", "FALSE"),
                optional=True,
            ),
            Sequence(
                "AWS_SNS_TOPIC",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "INTEGRATION",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            optional=True,
        ),
        Ref("CreateStatementCommentSegment", optional=True),
        Ref.keyword("AS", optional=True),
        OneOf(
            Ref("SelectStatementSegment", optional=True),
            Sequence(
                Bracketed(Ref("FunctionContentsGrammar"), optional=True),
                "RETURNS",
                Ref("DatatypeSegment"),
                Ref("FunctionAssignerSegment"),
                Ref("ExpressionSegment"),
                Sequence(
                    "COMMENT",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
                optional=True,
            ),
            Ref("CopyIntoStatementSegment"),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class CopyIntoStatementSegment(BaseSegment):
    """A snowflake `COPY INTO` statement.

    # https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html
    """

    type = "copy_into_statement"

    match_grammar = Sequence(
        "COPY",
        "INTO",
        Ref("ObjectReferenceSegment"),
        Sequence(
            "FROM",
            OneOf(
                Ref("IntExtStageLocation"),
                Ref("QuotedLiteralSegment"),
                Ref("SelectStatementSegment"),
            ),
            AnyNumberOf(
                Sequence(
                    "FILES",
                    Ref("EqualsSegment"),
                    Bracketed(
                        Delimited(
                            Ref("QuotedLiteralSegment"),
                        ),
                    ),
                    optional=True,
                ),
                Sequence(
                    "PATTERN",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
                Sequence(
                    "FILE_FORMAT",
                    Ref("EqualsSegment"),
                    Bracketed(
                        OneOf(
                            Sequence(
                                "FORMAT_NAME",
                                Ref("EqualsSegment"),
                                OneOf(
                                    Ref("NakedIdentifierSegment"),
                                    Ref("QuotedLiteralSegment"),
                                ),
                            ),
                            Sequence(
                                "TYPE",
                                Ref("EqualsSegment"),
                                OneOf(
                                    "CSV",
                                    "JSON",
                                    "AVRO",
                                    "ORC",
                                    "PARQUET",
                                    "XML",
                                    Ref("QuotedLiteralSegment"),
                                ),
                                AnyNumberOf(
                                    # Copy Options
                                    Ref("NakedIdentifierSegment"),
                                    Ref("EqualsSegment"),
                                    OneOf(
                                        Ref("NakedIdentifierSegment"),
                                        Ref("QuotedLiteralSegment"),
                                        Bracketed(
                                            Delimited(
                                                Ref("QuotedLiteralSegment"),
                                            )
                                        ),
                                    ),
                                    optional=True,
                                ),
                            ),
                        ),
                    ),
                    optional=True,
                ),
            ),
            optional=True,
        ),
        # Copy Options
        AnyNumberOf(
            Ref("NakedIdentifierSegment"),
            Ref("EqualsSegment"),
            OneOf(
                Ref("NakedIdentifierSegment"),
                Ref("QuotedLiteralSegment"),
                Bracketed(
                    Delimited(
                        Ref("QuotedLiteralSegment"),
                    )
                ),
            ),
        ),
        Sequence(
            "VALIDATION_MODE",
            Ref("EqualsSegment"),
            OneOf(
                Ref("ReturnNRowsSegment"),
                "RETURN_ERRORS",
                "RETURN_ALL_ERRORS",
            ),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class IntExtStageLocation(BaseSegment):
    """A snowflake internalStage / externalStage segment used by copy into tables.

    https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html#syntax
    """

    type = "internal_external_stage"

    # TODO - currently Paths are not supported nor External Locations
    match_grammar = Sequence(
        Ref("AtSignLiteralSegment"),
        Sequence(
            AnyNumberOf(
                Sequence(
                    Ref("NakedIdentifierSegment"),
                    Ref("DotSegment"),
                ),
                optional=True,
            ),
            Ref("ModuloSegment", optional=True),
            Ref("NakedIdentifierSegment"),
        ),
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


@snowflake_dialect.segment()
class AlterTaskStatementSegment(BaseSegment):
    """Snowflake's ALTER TASK statement.

    ```
    ALTER TASK [IF EXISTS] <name> RESUME;
    ALTER TASK [IF EXISTS] <name> SUSPEND;
    ALTER TASK [IF EXISTS] <name> REMOVE AFTER <value>;
    ALTER TASK [IF EXISTS] <name> ADD AFTER <value>;
    ALTER TASK [IF EXISTS] <name> SET
        [WAREHOUSE = <value>]
        [SCHEDULE = <value>]
        [ALLOW_OVERLAPPING_EXECUTION = TRUE|FALSE];
    ALTER TASK [IF EXISTS] <name> SET
        <param_name> = <param_value> [ , <param_name> = <param_value> , ...];
    ALTER TASK [IF EXISTS] <name> UNSET <param_name> [ , <param_name> , ... ];
    ALTER TASK [IF EXISTS] <name> MODIFY AS <sql>;
    ALTER TASK [IF EXISTS] <name> MODIFY WHEN <boolean>;
    ```

    https://docs.snowflake.com/en/sql-reference/sql/alter-task.html
    """

    type = "alter_task_statement"

    match_grammar = Sequence(
        "ALTER",
        "TASK",
        Sequence("IF", "EXISTS", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            "RESUME",
            "SUSPEND",
            Sequence("REMOVE", "AFTER", Ref("ObjectReferenceSegment")),
            Sequence("ADD", "AFTER", Ref("ObjectReferenceSegment")),
            Ref("AlterTaskSpecialSetClauseSegment"),
            Ref("AlterTaskSetClauseSegment"),
            Ref("AlterTaskUnsetClauseSegment"),
            Sequence(
                "MODIFY",
                "AS",
                ansi_dialect.get_segment("ExplainStatementSegment").explainable_stmt,
            ),
            Sequence("MODIFY", "WHEN", Ref("BooleanLiteralGrammar")),
        ),
    )


@snowflake_dialect.segment()
class AlterTaskSpecialSetClauseSegment(BaseSegment):
    """Snowflake's ALTER TASK special SET clause.

    ```
    [ALTER TASK <name>] SET
        [WAREHOUSE = <value>]
        [SCHEDULE = <value>]
        [ALLOW_OVERLAPPING_EXECUTION = TRUE|FALSE];
    ```

    https://docs.snowflake.com/en/sql-reference/sql/alter-task.html
    """

    type = "alter_task_special_set_clause"

    match_grammar = Sequence(
        "SET",
        AnyNumberOf(
            Sequence(
                "WAREHOUSE",
                Ref("EqualsSegment"),
                Ref("ObjectReferenceSegment"),
                optional=True,
            ),
            Sequence(
                "SCHEDULE",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "ALLOW_OVERLAPPING_EXECUTION",
                Ref("EqualsSegment"),
                OneOf("TRUE", "FALSE"),
                optional=True,
            ),
            min_times=1,
        ),
    )


@snowflake_dialect.segment()
class AlterTaskSetClauseSegment(BaseSegment):
    """Snowflake's ALTER TASK SET clause.

    ```
    [ALTER TASK <name>] SET
        <param_name> = <param_value> [ , <param_name> = <param_value> , ...];
    ```

    https://docs.snowflake.com/en/sql-reference/sql/alter-task.html
    """

    type = "alter_task_set_clause"

    match_grammar = Sequence(
        "SET",
        Delimited(
            Sequence(
                Ref("ParameterNameSegment"),
                Ref("EqualsSegment"),
                OneOf(
                    Ref("BooleanLiteralGrammar"),
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                ),
            ),
            delimiter=Ref("CommaSegment"),
        ),
    )


@snowflake_dialect.segment()
class AlterTaskUnsetClauseSegment(BaseSegment):
    """Snowflake's ALTER TASK UNSET clause.

    ```
    [ALTER TASK <name>] UNSET <param_name> [ , <param_name> , ... ];
    ```

    https://docs.snowflake.com/en/sql-reference/sql/alter-task.html
    """

    type = "alter_task_unset_clause"

    match_grammar = Sequence(
        "UNSET",
        Delimited(Ref("ParameterNameSegment"), delimiter=Ref("CommaSegment")),
    )


############################
# MERGE
############################
@snowflake_dialect.segment()
class MergeStatementSegment(BaseSegment):
    """`MERGE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/merge.html
    """

    type = "merge_statement"

    is_ddl = False
    is_dml = True
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        Sequence("MERGE", "INTO"),
    )
    parse_grammar = Sequence(
        "MERGE",
        "INTO",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        "USING",
        OneOf(
            Ref("TableReferenceSegment"),  # tables/views
            Bracketed(
                Ref("SelectableGrammar"),
            ),  # subquery
        ),
        Ref("AliasExpressionSegment", optional=True),
        Ref("JoinOnConditionSegment"),
        Ref("MergeMatchedClauseSegment", optional=True),
        Ref("MergeNotMatchedClauseSegment", optional=True),
    )


@snowflake_dialect.segment()
class MergeMatchedClauseSegment(BaseSegment):
    """The `WHEN MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_matched_clause"
    match_grammar = StartsWith(
        Sequence(
            "WHEN",
            "MATCHED",
            Sequence("AND", Ref("ExpressionSegment"), optional=True),
            "THEN",
            OneOf("UPDATE", "DELETE"),
        ),
        terminator=Ref("MergeNotMatchedClauseSegment"),
    )
    parse_grammar = Sequence(
        "WHEN",
        "MATCHED",
        Sequence("AND", Ref("ExpressionSegment"), optional=True),
        "THEN",
        OneOf(
            Ref("MergeUpdateClauseSegment"),
            Ref("MergeDeleteClauseSegment"),
        ),
    )


@snowflake_dialect.segment()
class MergeNotMatchedClauseSegment(BaseSegment):
    """The `WHEN NOT MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_not_matched_clause"
    match_grammar = StartsWith(
        Sequence(
            "WHEN",
            "NOT",
            "MATCHED",
            "THEN",
        ),
    )
    parse_grammar = Sequence(
        "WHEN",
        "NOT",
        "MATCHED",
        "THEN",
        Ref("MergeInsertClauseSegment"),
    )


@snowflake_dialect.segment()
class MergeUpdateClauseSegment(BaseSegment):
    """`UPDATE` clause within the `MERGE` statement."""

    type = "merge_update_clause"
    match_grammar = Sequence(
        "UPDATE",
        Ref("SetClauseListSegment"),
        Ref("WhereClauseSegment", optional=True),
    )


@snowflake_dialect.segment()
class MergeDeleteClauseSegment(BaseSegment):
    """`DELETE` clause within the `MERGE` statement."""

    type = "merge_delete_clause"
    match_grammar = Sequence(
        "DELETE",
        Ref("WhereClauseSegment", optional=True),
    )


@snowflake_dialect.segment()
class MergeInsertClauseSegment(BaseSegment):
    """`INSERT` clause within the `MERGE` statement."""

    type = "merge_insert_clause"
    match_grammar = Sequence(
        "INSERT",
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "VALUES",
        Bracketed(
            Delimited(
                OneOf(
                    "DEFAULT",
                    Ref("ExpressionSegment"),
                ),
            )
        ),
        Ref("WhereClauseSegment", optional=True),
    )


@snowflake_dialect.segment(replace=True)
class DeleteStatementSegment(ansi_dialect.get_segment("DeleteStatementSegment")):  # type: ignore
    """Update `DELETE` statement to support `USING`."""

    parse_grammar = Sequence(
        "DELETE",
        Ref("FromClauseTerminatingUsingWhereSegment"),
        Ref("DeleteUsingClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
    )


@snowflake_dialect.segment()
class DeleteUsingClauseSegment(BaseSegment):
    """`USING` clause within the `DELETE` statement."""

    type = "using_clause"
    match_grammar = StartsWith(
        "USING",
        terminator=Ref.keyword("WHERE"),
        enforce_whitespace_preceeding_terminator=True,
    )
    parse_grammar = Sequence(
        "USING",
        Delimited(
            Ref("FromExpressionElementSegment"),
        ),
        Ref("AliasExpressionSegment", optional=True),
    )


@snowflake_dialect.segment()
class FromClauseTerminatingUsingWhereSegment(ansi_dialect.get_segment("FromClauseSegment")):  # type: ignore
    """Copy `FROM` terminator statement to support `USING` in specific circumstances."""

    match_grammar = StartsWith(
        "FROM",
        terminator=OneOf(Ref.keyword("USING"), Ref.keyword("WHERE")),
        enforce_whitespace_preceeding_terminator=True,
    )
