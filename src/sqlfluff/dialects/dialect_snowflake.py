"""The Snowflake dialect.

Inherits from Postgres.

Based on https://docs.snowflake.com/en/sql-reference-commands.html
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    CodeSegment,
    Dedent,
    Delimited,
    Indent,
    NamedParser,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    StartsWith,
    StringLexer,
    StringParser,
    SymbolSegment,
)
from sqlfluff.dialects.dialect_snowflake_keywords import (
    snowflake_reserved_keywords,
    snowflake_unreserved_keywords,
)

ansi_dialect = load_raw_dialect("ansi")
snowflake_dialect = ansi_dialect.copy_as("snowflake")

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
        RegexLexer("atsign_literal", r"@[a-zA-Z_][\w]*", CodeSegment),
        # Column selector
        # https://docs.snowflake.com/en/sql-reference/sql/select.html#parameters
        RegexLexer("column_selector", r"\$[0-9]+", CodeSegment),
        RegexLexer(
            "dollar_quote",
            r"\$\$.*\$\$",
            CodeSegment,
        ),
        RegexLexer(
            "dollar_literal",
            r"[$][a-zA-Z0-9_.]*",
            CodeSegment,
        ),
        RegexLexer("inline_dollar_sign", r"[a-zA-Z_][a-zA-Z0-9_$]*", CodeSegment),
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
        trim_chars=("$"),
    ),
    # We use a RegexParser instead of keywords as some (those with dashes) require quotes:
    WarehouseSize=RegexParser(
        r"('?XSMALL'?|'?SMALL'?|'?MEDIUM'?|'?LARGE'?|'?XLARGE'?|'?XXLARGE'?|'?X2LARGE'?|"
        r"'?XXXLARGE'?|'?X3LARGE'?|'?X4LARGE'?|'?X5LARGE|'?X6LARGE'?|"
        r"'X-SMALL'|'X-LARGE'|'2X-LARGE'|'3X-LARGE'|'4X-LARGE'|'5X-LARGE'|'6X-LARGE')",
        CodeSegment,
        name="warehouse_size",
        type="warehouse_size",
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
    CopyOptionOnErrorSegment=RegexParser(
        r"(?:'?CONTINUE'?)|(?:'?SKIP_FILE(_[0-9]+%?)?'?)|(?:'?ABORT_STATEMENT'?)",
        CodeSegment,
        name="literal",
        type="literal",
    ),
    DoubleQuotedUDFBody=NamedParser(
        "double_quote",
        CodeSegment,
        name="udf_body",
        type="udf_body",
        trim_chars=('"',),
    ),
    SingleQuotedUDFBody=NamedParser(
        "single_quote",
        CodeSegment,
        name="udf_body",
        type="udf_body",
        trim_chars=("'",),
    ),
    DollarQuotedUDFBody=NamedParser(
        "dollar_quote",
        CodeSegment,
        name="udf_body",
        type="udf_body",
        trim_chars=("$",),
    ),
    S3Path=RegexParser(
        # See https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
        r"'s3://[a-z0-9][a-z0-9\.-]{1,61}[a-z0-9](?:/.+)?'",
        CodeSegment,
        name="s3_path",
        type="bucket_path",
    ),
    GCSPath=RegexParser(
        # See https://cloud.google.com/storage/docs/naming-buckets
        r"'gcs://[a-z0-9][\w\.-]{1,61}[a-z0-9](?:/.+)?'",
        CodeSegment,
        name="gcs_path",
        type="bucket_path",
    ),
    AzureBlobStoragePath=RegexParser(
        # See https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftstorage
        r"'azure://[a-z0-9][a-z0-9-]{1,61}[a-z0-9]\.blob\.core\.windows\.net/[a-z0-9][a-z0-9\.-]{1,61}[a-z0-9](?:/.+)?'",
        CodeSegment,
        name="azure_blob_storage_path",
        type="bucket_path",
    ),
    SnowflakeEncryptionOption=RegexParser(
        r"(?:'SNOWFLAKE_FULL')|(?:'SNOWFLAKE_SSE')",
        CodeSegment,
        name="snowflake_encryption_option",
        type="stage_encryption_option",
    ),
    S3EncryptionOption=RegexParser(
        r"(?:'AWS_CSE')|(?:'AWS_SSE_S3')|(?:'AWS_SSE_KMS')",
        CodeSegment,
        name="s3_encryption_option",
        type="stage_encryption_option",
    ),
    GCSEncryptionOption=RegexParser(
        r"'GCS_SSE_KMS'",
        CodeSegment,
        name="gcs_encryption_option",
        type="stage_encryption_option",
    ),
    AzureBlobStorageEncryptionOption=RegexParser(
        r"'AZURE_CSE'",
        CodeSegment,
        name="azure_blob_storage_encryption_option",
        type="stage_encryption_option",
    ),
    FileType=RegexParser(
        r"(?:'?CSV'?)|(?:'?JSON'?)|(?:'?AVRO'?)|(?:'?ORC'?)|(?:'?PARQUET'?)|(?:'?XML'?)",
        CodeSegment,
        name="file_type",
        type="file_type",
    ),
)

snowflake_dialect.replace(
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            # See https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html
            r"[a-zA-Z_][a-zA-Z0-9_$]*",
            CodeSegment,
            name="naked_identifier",
            type="identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
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
        Ref("ReferencedVariableNameSegment"),
        Ref("AtSignLiteralSegment"),
    ),
    PostFunctionGrammar=Sequence(
        Ref("WithinGroupClauseSegment", optional=True),
        Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
        Ref("OverClauseSegment", optional=True),
    ),
    TemporaryGrammar=Sequence(
        OneOf("LOCAL", "GLOBAL", optional=True),
        OneOf("TEMP", "TEMPORARY", optional=True),
        Sequence("VOLATILE", optional=True),
        optional=True,
    ),
    TemporaryTransientGrammar=OneOf(Ref("TemporaryGrammar"), "TRANSIENT"),
)

# Add all Snowflake keywords
snowflake_dialect.sets("unreserved_keywords").clear()
snowflake_dialect.sets("unreserved_keywords").update(
    [n.strip().upper() for n in snowflake_unreserved_keywords.split("\n")]
)

snowflake_dialect.sets("reserved_keywords").clear()
snowflake_dialect.sets("reserved_keywords").update(
    [n.strip().upper() for n in snowflake_reserved_keywords.split("\n")]
)

# Add datetime units and their aliases from
# https://docs.snowflake.com/en/sql-reference/functions-date-time.html#label-supported-date-time-parts
snowflake_dialect.sets("datetime_units").clear()
snowflake_dialect.sets("datetime_units").update(
    [
        "YEAR",
        "Y",
        "YY",
        "YYY",
        "YYYY",
        "YR",
        "YEARS",
        "YRS",
        "MONTH",
        "MM",
        "MON",
        "MONS",
        "MONTHS",
        "DAY",
        "D",
        "DD",
        "DAYS",
        "DAYOFMONTH",
        "DAYOFWEEK",
        "WEEKDAY",
        "DOW",
        "DW",
        "DAYOFWEEKISO",
        "WEEKDAY_ISO",
        "DOW_ISO",
        "DW_ISO",
        "DAYOFYEAR",
        "YEARDAY",
        "DOY",
        "DY",
        "WEEK",
        "W",
        "WK",
        "WEEKOFYEAR",
        "WOY",
        "WY",
        "WEEKISO",
        "WEEK_ISO",
        "WEEKOFYEARISO",
        "WEEKOFYEAR_ISO",
        "QUARTER",
        "Q",
        "QTR",
        "QTRS",
        "QUARTERS",
        "YEAROFWEEK",
        "YEAROFWEEKISO",
        "HOUR",
        "H",
        "HH",
        "HR",
        "HOURS",
        "HRS",
        "MINUTE",
        "M",
        "MI",
        "MIN",
        "MINUTES",
        "MINS",
        "SECOND",
        "S",
        "SEC",
        "SECONDS",
        "SECS",
        "MILLISECOND",
        "MS",
        "MSEC",
        "MILLISECONDS",
        "MICROSECOND",
        "US",
        "USEC",
        "MICROSECONDS",
        "NANOSECOND",
        "NS",
        "NSEC",
        "NANOSEC",
        "NSECOND",
        "NANOSECONDS",
        "NANOSECS",
        "NSECONDS",
        "EPOCH_SECOND",
        "EPOCH",
        "EPOCH_SECONDS",
        "EPOCH_MILLISECOND",
        "EPOCH_MILLISECONDS",
        "EPOCH_MICROSECOND",
        "EPOCH_MICROSECONDS",
        "EPOCH_NANOSECOND",
        "EPOCH_NANOSECONDS",
        "TIMEZONE_HOUR",
        "TZH",
        "TIMEZONE_MINUTE",
        "TZM",
    ]
)


@snowflake_dialect.segment(replace=True)
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`.

    Snowflake supports Cube, Rollup, and Grouping Sets

    https://docs.snowflake.com/en/sql-reference/constructs/group-by.html
    """

    type = "groupby_clause"
    match_grammar = StartsWith(
        Sequence("GROUP", "BY"),
        terminator=OneOf("ORDER", "LIMIT", "HAVING", "QUALIFY", "WINDOW"),
        enforce_whitespace_preceding_terminator=True,
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
            Sequence("ORDER", "BY"),
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
            Sequence("ORDER", "BY"),
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
            Ref("CreateTaskSegment"),
            Ref("CreateCloneStatementSegment"),
            Ref("CreateProcedureStatementSegment"),
            Ref("ShowStatementSegment"),
            Ref("AlterUserSegment"),
            Ref("AlterSessionStatementSegment"),
            Ref("AlterTaskStatementSegment"),
            Ref("SetAssignmentStatementSegment"),
            Ref("CallStoredProcedureSegment"),
            Ref("MergeStatementSegment"),
            Ref("AlterTableColumnStatementSegment"),
            Ref("CopyIntoStatementSegment"),
            Ref("AlterWarehouseStatementSegment"),
            Ref("CreateExternalTableSegment"),
            Ref("CreateSchemaStatementSegment"),
            Ref("AlterSchemaStatementSegment"),
            Ref("CreateFunctionStatementSegment"),
            Ref("AlterFunctionStatementSegment"),
            Ref("CreateStageSegment"),
            Ref("AlterStageSegment"),
        ],
        remove=[
            Ref("CreateTypeStatementSegment"),
            Ref("CreateExtensionStatementSegment"),
            Ref("CreateIndexStatementSegment"),
            Ref("DropIndexStatementSegment"),
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


@snowflake_dialect.segment(replace=True)
class SamplingExpressionSegment(BaseSegment):
    """A sampling expression."""

    type = "sample_expression"
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
            Sequence("ORDER", "BY"),
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
        OneOf(
            Sequence(
                "DROP",
                Ref.keyword("COLUMN", optional=True),
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence(
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
                                        OneOf("SET", "DROP", optional=True),
                                        "NOT",
                                        "NULL",
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
            ),
        ),
    )


@snowflake_dialect.segment()
class AlterWarehouseStatementSegment(BaseSegment):
    """An `ALTER WAREHOUSE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse.html

    """

    type = "alter_warehouse_statement"
    match_grammar = Sequence(
        "ALTER",
        "WAREHOUSE",
        Sequence("IF", "EXISTS", optional=True),
        OneOf(
            Sequence(
                Ref("NakedIdentifierSegment", optional=True),
                OneOf(
                    "SUSPEND",
                    Sequence(
                        "RESUME",
                        Sequence("IF", "SUSPENDED", optional=True),
                    ),
                ),
            ),
            Sequence(
                Ref("NakedIdentifierSegment", optional=True),
                Sequence(
                    "ABORT",
                    "ALL",
                    "QUERIES",
                ),
            ),
            Sequence(
                Ref("NakedIdentifierSegment"),
                "RENAME",
                "TO",
                Ref("NakedIdentifierSegment"),
            ),
            Sequence(
                Ref("NakedIdentifierSegment"),
                "SET",
                OneOf(
                    AnyNumberOf(
                        Ref("WarehouseObjectPropertiesSegment"),
                        Ref("CommentEqualsClauseSegment"),
                        Ref("WarehouseObjectParamsSegment"),
                    ),
                    Ref("TagEqualsSegment"),
                ),
            ),
            Sequence(
                Ref("NakedIdentifierSegment"),
                "UNSET",
                OneOf(
                    Delimited(Ref("NakedIdentifierSegment")),
                    Sequence("TAG", Delimited(Ref("NakedIdentifierSegment"))),
                ),
            ),
        ),
    )


@snowflake_dialect.segment(replace=True)
class CommentClauseSegment(BaseSegment):
    """A comment clause.

    e.g. COMMENT 'column description'
    """

    type = "comment_clause"
    match_grammar = Sequence("COMMENT", Ref("QuotedLiteralSegment"))


@snowflake_dialect.segment()
class CommentEqualsClauseSegment(BaseSegment):
    """A comment clause.

    e.g. COMMENT = 'view/table description'
    """

    type = "comment_equals_clause"
    match_grammar = Sequence(
        "COMMENT", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")
    )


@snowflake_dialect.segment()
class TagBracketedEqualsSegment(BaseSegment):
    """A tag clause.

    e.g. TAG (tag1 = 'value1', tag2 = 'value2')
    """

    type = "tag_bracketed_equals"
    match_grammar = Sequence(
        Sequence("WITH", optional=True),
        "TAG",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("NakedIdentifierSegment"),
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                )
            ),
        ),
    )


@snowflake_dialect.segment()
class TagEqualsSegment(BaseSegment):
    """A tag clause.

    e.g. TAG tag1 = 'value1', tag2 = 'value2'
    """

    type = "tag_equals"
    match_grammar = Sequence(
        "TAG",
        Delimited(
            Sequence(
                Ref("NakedIdentifierSegment"),
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            )
        ),
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
class CreateProcedureStatementSegment(BaseSegment):
    """A snowflake `CREATE ... PROCEDURE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-procedure.html
    """

    type = "create_procedure_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        "PROCEDURE",
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        "RETURNS",
        Ref("DatatypeSegment"),
        Sequence("NOT", "NULL", optional=True),
        "LANGUAGE",
        "JAVASCRIPT",
        OneOf(
            Sequence("CALLED", "ON", "NULL", "INPUT"),
            Sequence("RETURNS", "NULL", "ON", "NULL", "INPUT"),
            "STRICT",
            optional=True,
        ),
        OneOf("VOLATILE", "IMMUTABLE", optional=True),
        Ref("CommentEqualsClauseSegment", optional=True),
        Sequence("EXECUTE", "AS", OneOf("CALLER", "OWNER"), optional=True),
        "AS",
        OneOf(
            Ref("DoubleQuotedUDFBody"),
            Ref("SingleQuotedUDFBody"),
            Ref("DollarQuotedUDFBody"),
        ),
    )


@snowflake_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A snowflake `CREATE ... FUNCTION` statement for SQL and JavaScript functions.

    https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    """

    type = "create_function_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Sequence("SECURE", optional=True),
        "FUNCTION",
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        "RETURNS",
        OneOf(
            Ref("DatatypeSegment"),
            Sequence("TABLE", Bracketed(Delimited(Ref("ColumnDefinitionSegment")))),
        ),
        Sequence("NOT", "NULL", optional=True),
        OneOf("VOLATILE", "IMMUTABLE", optional=True),
        Sequence("LANGUAGE", "JAVASCRIPT", optional=True),
        OneOf(
            Sequence("CALLED", "ON", "NULL", "INPUT"),
            Sequence("RETURNS", "NULL", "ON", "NULL", "INPUT"),
            "STRICT",
            optional=True,
        ),
        OneOf("VOLATILE", "IMMUTABLE", optional=True),
        Ref("CommentEqualsClauseSegment", optional=True),
        "AS",
        OneOf(
            Ref("DoubleQuotedUDFBody"),
            Ref("SingleQuotedUDFBody"),
            Ref("DollarQuotedUDFBody"),
        ),
    )


@snowflake_dialect.segment()
class AlterFunctionStatementSegment(BaseSegment):
    """A snowflake `ALTER ... FUNCTION` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-function.html
    """

    type = "alter_function_statement"
    match_grammar = Sequence(
        "ALTER",
        "FUNCTION",
        Sequence("IF", "EXISTS", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        OneOf(
            Sequence("RENAME", "TO", Ref("FunctionNameSegment")),
            Sequence("SET", OneOf("SECURE", Ref("CommentEqualsClauseSegment"))),
            Sequence("UNSET", OneOf("SECURE", "COMMENT")),
        ),
    )


@snowflake_dialect.segment()
class WarehouseObjectPropertiesSegment(BaseSegment):
    """A snowflake Warehouse Object Properties segment.

    https://docs.snowflake.com/en/sql-reference/sql/create-warehouse.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse.html

    Note: comments are handled seperately so not incorrectly marked as
    warehouse object.
    """

    type = "warehouse_object_properties"

    match_grammar = AnyNumberOf(
        Sequence(
            "WAREHOUSE_SIZE",
            Ref("EqualsSegment"),
            Ref("WarehouseSize"),
        ),
        Sequence(
            "WAIT_FOR_COMPLETION",
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
        ),
        Sequence(
            "MAX_CLUSTER_COUNT",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Sequence(
            "MIN_CLUSTER_COUNT",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Sequence(
            "SCALING_POLICY",
            Ref("EqualsSegment"),
            OneOf(
                "STANDARD",
                "ECONOMY",
            ),
        ),
        Sequence(
            "AUTO_SUSPEND",
            Ref("EqualsSegment"),
            OneOf(
                Ref("NumericLiteralSegment"),
                "NULL",
            ),
        ),
        Sequence(
            "AUTO_RESUME",
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
        ),
        Sequence(
            "INITIALLY_SUSPENDED",
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
        ),
        Sequence(
            "RESOURCE_MONITOR",
            Ref("EqualsSegment"),
            Ref("NakedIdentifierSegment"),
        ),
    )


@snowflake_dialect.segment()
class WarehouseObjectParamsSegment(BaseSegment):
    """A snowflake Warehouse Object Param segment.

    https://docs.snowflake.com/en/sql-reference/sql/create-warehouse.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse.html
    """

    type = "warehouse_object_properties"

    match_grammar = AnyNumberOf(
        Sequence(
            "MAX_CONCURRENCY_LEVEL",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Sequence(
            "STATEMENT_QUEUED_TIMEOUT_IN_SECONDS",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Sequence(
            "STATEMENT_TIMEOUT_IN_SECONDS",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
    )


@snowflake_dialect.segment()
class ConstraintPropertiesSegment(BaseSegment):
    """Constraint properties are specified in the CONSTRAINT clause for a CREATE TABLE or ALTER TABLE command.

    https://docs.snowflake.com/en/sql-reference/constraints-properties.html
    """

    type = "constraint_properties_segment"
    match_grammar = Sequence(
        Sequence("CONSTRAINT", Ref("QuotedLiteralSegment"), optional=True),
        OneOf(
            Sequence("UNIQUE", Bracketed(Ref("ColumnReferenceSegment"), optional=True)),
            Sequence(
                Ref("PrimaryKeyGrammar"),
                Bracketed(Ref("ColumnReferenceSegment"), optional=True),
            ),
            Sequence(
                Sequence(
                    Ref("ForeignKeyGrammar"),
                    Bracketed(Ref("ColumnReferenceSegment"), optional=True),
                    optional=True,
                ),
                "REFERENCES",
                Ref("TableReferenceSegment"),
                Bracketed(Ref("ColumnReferenceSegment")),
            ),
        ),
        AnyNumberOf(
            OneOf(Sequence("NOT", optional=True), "ENFORCED"),
            OneOf(Sequence("NOT", optional=True), "DEFERRABLE"),
            OneOf("INITIALLY", OneOf("DEFERRED", "IMMEDIATE")),
        ),
    )


@snowflake_dialect.segment(replace=True)
class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more.

    https://docs.snowflake.com/en/sql-reference/sql/create-table.html
    """

    type = "column_constraint_segment"
    match_grammar = AnyNumberOf(
        Sequence("COLLATE", Ref("QuotedLiteralSegment")),
        Sequence(
            "DEFAULT",
            OneOf(
                Ref("QuotedLiteralSegment"),
                # https://docs.snowflake.com/en/sql-reference/functions/current_timestamp.html
                Sequence(
                    "CURRENT_TIMESTAMP",
                    Bracketed(
                        Ref("NumericLiteralSegment", optional=True), optional=True
                    ),
                ),
                # https://docs.snowflake.com/en/sql-reference/functions/sysdate.html
                Sequence("SYSDATE", Bracketed()),
            ),
        ),
        Sequence(
            OneOf("AUTOINCREMENT", "IDENTITY"),
            OneOf(
                Bracketed(Delimited(Ref("NumericLiteralSegment"))),
                Sequence(
                    "START",
                    Ref("NumericLiteralSegment"),
                    "INCREMENT",
                    Ref("NumericLiteralSegment"),
                ),
                optional=True,
            ),
        ),
        Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
        Sequence(
            Sequence("WITH", optional=True),
            "MASKING",
            "POLICY",
            Ref("QuotedLiteralSegment"),
        ),
        Ref("TagBracketedEqualsSegment", optional=True),
        Ref("ConstraintPropertiesSegment"),
        Sequence("DEFAULT", Ref("QuotedLiteralSegment")),
        Sequence("CHECK", Bracketed(Ref("ExpressionSegment"))),
        Sequence(  # DEFAULT <value>
            "DEFAULT",
            OneOf(
                Ref("LiteralGrammar"),
                Ref("FunctionSegment"),
                # ?? Ref('IntervalExpressionSegment')
            ),
        ),
        Sequence(  # REFERENCES reftable [ ( refcolumn) ]
            "REFERENCES",
            Ref("ColumnReferenceSegment"),
            # Foreign columns making up FOREIGN KEY constraint
            Ref("BracketedColumnReferenceListGrammar", optional=True),
        ),
    )


@snowflake_dialect.segment()
class CopyOptionsSegment(BaseSegment):
    """A Snowflake CopyOptions statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-table.html
    """

    type = "copy_options"
    match_grammar = Bracketed(
        AnyNumberOf(
            Sequence("ON_ERROR", Ref("EqualsSegment"), Ref("CopyOptionOnErrorSegment")),
            Sequence("SIZE_LIMIT", Ref("EqualsSegment"), Ref("LiteralNumericSegment")),
            Sequence("PURGE", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")),
            Sequence(
                "RETURN_FAILED_ONLY", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")
            ),
            Sequence(
                "MATCH_BY_COLUMN_NAME",
                Ref("EqualsSegment"),
                OneOf("CASE_SENSITIVE", "CASE_INSENSITIVE", "NONE"),
            ),
            Sequence(
                "ENFORCE_LENGTH", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")
            ),
            Sequence(
                "TRUNCATECOLUMNS", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")
            ),
            Sequence("FORCE", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")),
        )
    )


@snowflake_dialect.segment(replace=True)
class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-schema.html
    """

    type = "create_schema_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryTransientGrammar", optional=True),
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
        Sequence("WITH", "MANAGED", "ACCESS", optional=True),
        Ref("SchemaObjectParamsSegment", optional=True),
        Ref("TagBracketedEqualsSegment", optional=True),
    )


@snowflake_dialect.segment()
class AlterSchemaStatementSegment(BaseSegment):
    """An `ALTER SCHEMA` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-schema.html

    """

    type = "alter_schema_statement"
    match_grammar = Sequence(
        "ALTER",
        "SCHEMA",
        Sequence("IF", "EXISTS", optional=True),
        Ref("SchemaReferenceSegment"),
        OneOf(
            Sequence(
                "RENAME",
                "TO",
                Ref("SchemaReferenceSegment"),
            ),
            Sequence(
                "SWAP",
                "WITH",
                Ref("SchemaReferenceSegment"),
            ),
            Sequence(
                "SET",
                OneOf(Ref("SchemaObjectParamsSegment"), Ref("TagEqualsSegment")),
            ),
            Sequence(
                "UNSET",
                OneOf(
                    Delimited(
                        "DATA_RETENTION_TIME_IN_DAYS",
                        "MAX_DATA_EXTENSION_TIME_IN_DAYS",
                        "DEFAULT_DDL_COLLATION",
                        "COMMENT",
                    ),
                    Sequence("TAG", Delimited(Ref("NakedIdentifierSegment"))),
                ),
            ),
            Sequence(OneOf("ENABLE", "DISABLE"), Sequence("MANAGED", "ACCESS")),
        ),
    )


@snowflake_dialect.segment()
class SchemaObjectParamsSegment(BaseSegment):
    """A Snowflake Schema Object Param segment.

    https://docs.snowflake.com/en/sql-reference/sql/create-schema.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-schema.html
    """

    type = "schema_object_properties"

    match_grammar = AnyNumberOf(
        Sequence(
            "DATA_RETENTION_TIME_IN_DAYS",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Sequence(
            "MAX_DATA_EXTENSION_TIME_IN_DAYS",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Sequence(
            "DEFAULT_DDL_COLLATION",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
        ),
        Ref("CommentEqualsClauseSegment"),
    )


@snowflake_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement.

    A lot more options than ANSI
    https://docs.snowflake.com/en/sql-reference/sql/create-table.html
    """

    type = "create_table_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryTransientGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Columns and comment syntax:
        Sequence(
            Bracketed(
                Delimited(
                    Sequence(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                            Ref("SingleIdentifierGrammar"),
                        ),
                        Ref("CommentClauseSegment", optional=True),
                    ),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "CLUSTER",
            "BY",
            Bracketed(Delimited(Ref("ExpressionSegment"))),
            optional=True,
        ),
        Sequence(
            "STAGE_FILE_FORMAT",
            Ref("EqualsSegment"),
            Ref("FileFormatSegment"),
            optional=True,
        ),
        Sequence(
            "STAGE_COPY_OPTIONS",
            Ref("EqualsSegment"),
            Ref("CopyOptionsSegment"),
            optional=True,
        ),
        Sequence(
            "DATA_RETENTION_TIME_IN_DAYS",
            Ref("EqualsSegment"),
            Ref("LiteralNumericSegment"),
            optional=True,
        ),
        Sequence(
            "MAX_DATA_EXTENSION_TIME_IN_DAYS",
            Ref("EqualsSegment"),
            Ref("LiteralNumericSegment"),
            optional=True,
        ),
        Sequence(
            "CHANGE_TRACKING",
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
            optional=True,
        ),
        Sequence(
            "DEFAULT_DDL_COLLATION",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralGrammar"),
            optional=True,
        ),
        Sequence(
            "COPY",
            "GRANTS",
            optional=True,
        ),
        Sequence(
            Sequence("WITH", optional=True),
            "ROW",
            "ACCESS",
            "POLICY",
            Ref("NakedIdentifierSegment"),
            "ON",
            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            optional=True,
        ),
        Ref("TagBracketedEqualsSegment", optional=True),
        Ref("CommentEqualsClauseSegment", optional=True),
        OneOf(
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
            # Create clone syntax
            Sequence("ClONE", Ref("TableReferenceSegment")),
            Sequence("USING", "TEMPLATE", Ref("SelectableGrammar")),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class CreateTaskSegment(BaseSegment):
    """A snowflake `CREATE TASK` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-task.html
    """

    type = "create_task_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        "TASK",
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("ObjectReferenceSegment"),
        Indent,
        AnyNumberOf(
            OneOf(
                Sequence(
                    "WAREHOUSE",
                    Ref("EqualsSegment"),
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE",
                    Ref("EqualsSegment"),
                    Ref("WarehouseSize"),
                ),
            ),
            Sequence(
                "SCHEDULE",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "ALLOW_OVERLAPPING_EXECUTION",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
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
            ),
            Sequence(
                "USER_TASK_TIMEOUT_MS",
                Ref("EqualsSegment"),
                Ref("NumericLiteralSegment"),
            ),
            Sequence(
                "COPY",
                "GRANTS",
            ),
            Ref("CreateStatementCommentSegment"),
        ),
        Sequence(
            "AFTER",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Dedent,
        Sequence(
            "WHEN",
            Indent,
            Ref("ExpressionSegment"),
            Dedent,
            optional=True,
        ),
        Sequence(
            Ref.keyword("AS"),
            Indent,
            Ref("StatementSegment"),
            Dedent,
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
            "VIEW",
            Sequence("MATERIALIZED", "VIEW"),
            Sequence("SECURE", "VIEW"),
            Sequence("MASKING", "POLICY"),
            "PIPE",
            Sequence("EXTERNAL", "FUNCTION"),
            # Objects that also support clone
            "DATABASE",
            "SEQUENCE",
            Sequence("FILE", "FORMAT"),
            "STREAM",
        ),
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("ObjectReferenceSegment"),
        # Next set are Pipe statements https://docs.snowflake.com/en/sql-reference/sql/create-pipe.html
        Sequence(
            Sequence(
                "AUTO_INGEST",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
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
        # Next are WAREHOUSE options https://docs.snowflake.com/en/sql-reference/sql/create-warehouse.html
        Sequence(
            Sequence("WITH", optional=True),
            AnyNumberOf(
                Ref("WarehouseObjectPropertiesSegment"),
                Ref("WarehouseObjectParamsSegment"),
            ),
            Ref("TagBracketedEqualsSegment", optional=True),
            optional=True,
        ),
        Ref("CreateStatementCommentSegment", optional=True),
        Ref.keyword("AS", optional=True),
        OneOf(
            Ref("SelectStatementSegment"),
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
class FileFormatSegment(BaseSegment):
    """A Snowflake FILE_FORMAT Segment.

    https://docs.snowflake.com/en/sql-reference/sql/create-table.html
    https://docs.snowflake.com/en/sql-reference/sql/create-external-table.html
    https://docs.snowflake.com/en/sql-reference/sql/create-stage.html
    """

    type = "file_format_segment"

    match_grammar = OneOf(
        OneOf(Ref("NakedIdentifierSegment"), Ref("QuotedLiteralSegment")),
        Bracketed(
            OneOf(
                Sequence(
                    "FORMAT_NAME",
                    Ref("EqualsSegment"),
                    OneOf(Ref("NakedIdentifierSegment"), Ref("QuotedLiteralSegment")),
                ),
                Sequence(
                    "TYPE",
                    Ref("EqualsSegment"),
                    Ref("FileType"),
                    # formatTypeOptions - To Do to make this more specific
                    Ref("FormatTypeOptionsSegment", optional=True),
                ),
            ),
        ),
    )


@snowflake_dialect.segment()
class FormatTypeOptionsSegment(BaseSegment):
    """A snowflake `formatTypeOptions` Segment.

    https://docs.snowflake.com/en/sql-reference/sql/create-table.html
    https://docs.snowflake.com/en/sql-reference/sql/create-external-table.html
    https://docs.snowflake.com/en/sql-reference/sql/create-stage.html
    """

    type = "format_type_options_segment"

    match_grammar = AnyNumberOf(
        # formatTypeOptions - To Do to make this more specific
        Ref("NakedIdentifierSegment"),
        Ref("EqualsSegment"),
        OneOf(
            Ref("NakedIdentifierSegment"),
            Ref("QuotedLiteralSegment"),
            Ref("NumericLiteralSegment"),
            Bracketed(
                Delimited(
                    Ref("QuotedLiteralSegment"),
                )
            ),
        ),
    )


@snowflake_dialect.segment()
class CreateExternalTableSegment(BaseSegment):
    """A snowflake `CREATE EXTERNAL TABLE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-external-table.html
    """

    type = "create_external_table_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        "EXTERNAL",
        "TABLE",
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("TableReferenceSegment"),
        # Columns:
        Sequence(
            Bracketed(
                Delimited(
                    OneOf(
                        Ref("TableConstraintSegment"),
                        Ref("ColumnDefinitionSegment"),
                        Ref("SingleIdentifierGrammar"),
                    ),
                ),
            ),
            optional=True,
        ),
        AnyNumberOf(
            Sequence(
                "PARTITION",
                "BY",
                Delimited(
                    Ref("SingleIdentifierGrammar"),
                ),
                optional=True,
            ),
            Sequence(
                Sequence("WITH", optional=True),
                "LOCATION",
                Ref("EqualsSegment"),
                Ref("AtSignLiteralSegment"),
                Bracketed(
                    Ref("NakedIdentifierSegment"),
                    Ref("DotSegment"),
                    bracket_type="square",
                    optional=True,
                ),
                AnyNumberOf(
                    Ref("NakedIdentifierSegment"),
                    Ref("SlashSegment"),
                    allow_gaps=False,
                ),
                optional=True,
            ),
            Sequence(
                "REFRESH_ON_CREATE",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
                optional=True,
            ),
            Sequence(
                "AUTO_REFRESH",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
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
                Ref("FileFormatSegment"),
                optional=True,
            ),
            Sequence(
                "AWS_SNS_TOPIC",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "COPY",
                "GRANTS",
                optional=True,
            ),
            Sequence(
                Sequence("WITH", optional=True),
                "ROW",
                "ACCESS",
                "POLICY",
                Ref("NakedIdentifierSegment"),
                optional=True,
            ),
            Ref("TagBracketedEqualsSegment", optional=True),
            Ref("CreateStatementCommentSegment", optional=True),
        ),
    )


@snowflake_dialect.segment(replace=True)
class TableExpressionSegment(BaseSegment):
    """The main table expression e.g. within a FROM clause."""

    type = "table_expression"
    match_grammar = OneOf(
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("TableReferenceSegment"),
        # Nested Selects
        Bracketed(Ref("SelectableGrammar")),
        # Values clause?
        Ref("IntExtStageLocation"),
        Ref("PathSegment"),
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
        Ref("TableReferenceSegment"),
        Bracketed(Delimited(Ref("ColumnReferenceSegment")), optional=True),
        Sequence(
            "FROM",
            OneOf(
                Ref("IntExtStageLocation"),
                Ref("QuotedLiteralSegment"),
                Bracketed(
                    Ref("SelectStatementSegment"),
                ),
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
                    Ref("FileFormatSegment"),
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
class PathSegment(BaseSegment):
    """Path Segment."""

    type = "path"

    match_grammar = Delimited(
        Ref("NakedIdentifierSegment"), delimiter=Ref("SlashSegment")
    )


@snowflake_dialect.segment()
class IntExtStageLocation(BaseSegment):
    """A snowflake internalStage / externalStage segment used by copy into tables.

    https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html#syntax
    """

    type = "internal_external_stage"

    # TODO - currently External Locations are not supported
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
            Sequence(Ref("SlashSegment"), Ref("PathSegment"), optional=True),
        ),
    )


@snowflake_dialect.segment()
class InternalStageParameters(BaseSegment):
    """Parameters for an internal stage in Snowflake.

    https://docs.snowflake.com/en/sql-reference/sql/create-stage.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-stage.html
    """

    name = "internal_stage_parameters"
    type = "stage_parameters"

    match_grammar = Sequence(
        Sequence(
            "ENCRYPTION",
            Ref("EqualsSegment"),
            Bracketed(
                "TYPE",
                Ref("EqualsSegment"),
                Ref("SnowflakeEncryptionOption"),
            ),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class S3ExternalStageParameters(BaseSegment):
    """Parameters for an S3 external stage in Snowflake.

    https://docs.snowflake.com/en/sql-reference/sql/create-stage.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-stage.html
    """

    name = "s3_external_stage_parameters"
    type = "stage_parameters"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                "STORAGE_INTEGRATION",
                Ref("EqualsSegment"),
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "CREDENTIALS",
                Ref("EqualsSegment"),
                Bracketed(
                    OneOf(
                        Sequence(
                            "AWS_KEY_ID",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                            "AWS_SECRET_KEY",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                            Sequence(
                                "AWS_TOKEN",
                                Ref("EqualsSegment"),
                                Ref("QuotedLiteralSegment"),
                                optional=True,
                            ),
                        ),
                        Sequence(
                            "AWS_ROLE",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                    )
                ),
            ),
            optional=True,
        ),
        Sequence(
            "ENCRYPTION",
            Ref("EqualsSegment"),
            Bracketed(
                OneOf(
                    Sequence(
                        Sequence(
                            "TYPE",
                            Ref("EqualsSegment"),
                            Ref("S3EncryptionOption"),
                            optional=True,
                        ),
                        "MASTER_KEY",
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                    Sequence("TYPE", Ref("EqualsSegment"), Ref("S3EncryptionOption")),
                    Sequence(
                        "TYPE",
                        Ref("EqualsSegment"),
                        Ref("S3EncryptionOption"),
                        Sequence(
                            "KMS_KEY_ID",
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                    ),
                    Sequence("TYPE", Ref("EqualsSegment"), "NONE"),
                )
            ),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class GCSExternalStageParameters(BaseSegment):
    """Parameters for a GCS external stage in Snowflake.

    https://docs.snowflake.com/en/sql-reference/sql/create-stage.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-stage.html
    """

    name = "gcs_external_stage_parameters"
    type = "stage_parameters"

    match_grammar = Sequence(
        Sequence(
            "STORAGE_INTEGRATION",
            Ref("EqualsSegment"),
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Sequence(
            "ENCRYPTION",
            Ref("EqualsSegment"),
            Bracketed(
                Sequence(
                    "TYPE",
                    Ref("EqualsSegment"),
                    OneOf(
                        Sequence(
                            Ref("GCSEncryptionOption"),
                            Sequence(
                                "KMS_KEY_ID",
                                Ref("EqualsSegment"),
                                Ref("QuotedLiteralSegment"),
                                optional=True,
                            ),
                        ),
                        "NONE",
                    ),
                )
            ),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class AzureBlobStorageExternalStageParameters(BaseSegment):
    """Parameters for an Azure Blob Storage external stage in Snowflake.

    https://docs.snowflake.com/en/sql-reference/sql/create-stage.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-stage.html
    """

    name = "azure_blob_storage_external_stage_parameters"
    type = "stage_parameters"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                "STORAGE_INTEGRATION",
                Ref("EqualsSegment"),
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "CREDENTIALS",
                Ref("EqualsSegment"),
                Bracketed(
                    Sequence("AZURE_SAS_TOKEN"),
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "ENCRYPTION",
            Ref("EqualsSegment"),
            Bracketed(
                Sequence(
                    "TYPE",
                    Ref("EqualsSegment"),
                    OneOf(
                        Sequence(
                            Ref("AzureBlobStorageEncryptionOption"),
                            Sequence(
                                "MASTER_KEY",
                                Ref("EqualsSegment"),
                                Ref("QuotedLiteralSegment"),
                                optional=True,
                            ),
                        ),
                        "NONE",
                    ),
                )
            ),
            optional=True,
        ),
    )


@snowflake_dialect.segment()
class CreateStageSegment(BaseSegment):
    """A Snowflake CREATE STAGE statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-stage.html
    """

    type = "create_stage_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref.keyword("TEMPORARY", optional=True),
        "STAGE",
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("ObjectReferenceSegment"),
        Indent,
        OneOf(
            # Internal stages
            Sequence(
                Ref("InternalStageParameters", optional=True),
                Sequence(
                    "DIRECTORY",
                    Ref("EqualsSegment"),
                    Bracketed(
                        Sequence(
                            "ENABLE",
                            Ref("EqualsSegment"),
                            Ref("BooleanLiteralGrammar"),
                        )
                    ),
                    optional=True,
                ),
            ),
            # External S3 stage
            Sequence(
                "URL",
                Ref("EqualsSegment"),
                Ref("S3Path"),
                Ref("S3ExternalStageParameters", optional=True),
                Sequence(
                    "DIRECTORY",
                    Ref("EqualsSegment"),
                    Bracketed(
                        Sequence(
                            "ENABLE",
                            Ref("EqualsSegment"),
                            Ref("BooleanLiteralGrammar"),
                        ),
                        Sequence(
                            "AUTO_REFRESH",
                            Ref("EqualsSegment"),
                            Ref("BooleanLiteralGrammar"),
                            optional=True,
                        ),
                    ),
                    optional=True,
                ),
            ),
            # External GCS stage
            Sequence(
                "URL",
                Ref("EqualsSegment"),
                Ref("GCSPath"),
                Ref("GCSExternalStageParameters", optional=True),
                Sequence(
                    "DIRECTORY",
                    Ref("EqualsSegment"),
                    Bracketed(
                        Sequence(
                            "ENABLE",
                            Ref("EqualsSegment"),
                            Ref("BooleanLiteralGrammar"),
                        ),
                        Sequence(
                            "AUTO_REFRESH",
                            Ref("EqualsSegment"),
                            Ref("BooleanLiteralGrammar"),
                            optional=True,
                        ),
                        Sequence(
                            "NOTIFICATION_INTEGRATION",
                            Ref("EqualsSegment"),
                            OneOf(
                                Ref("NakedIdentifierSegment"),
                                Ref("QuotedLiteralSegment"),
                            ),
                            optional=True,
                        ),
                    ),
                    optional=True,
                ),
            ),
            # External Azure Blob Storage stage
            Sequence(
                "URL",
                Ref("EqualsSegment"),
                Ref("AzureBlobStoragePath"),
                Ref("AzureBlobStorageExternalStageParameters", optional=True),
                Sequence(
                    "DIRECTORY",
                    Ref("EqualsSegment"),
                    Bracketed(
                        Sequence(
                            "ENABLE",
                            Ref("EqualsSegment"),
                            Ref("BooleanLiteralGrammar"),
                        ),
                        Sequence(
                            "AUTO_REFRESH",
                            Ref("EqualsSegment"),
                            Ref("BooleanLiteralGrammar"),
                            optional=True,
                        ),
                        Sequence(
                            "NOTIFICATION_INTEGRATION",
                            Ref("EqualsSegment"),
                            OneOf(
                                Ref("NakedIdentifierSegment"),
                                Ref("QuotedLiteralSegment"),
                            ),
                            optional=True,
                        ),
                    ),
                    optional=True,
                ),
            ),
            optional=True,
        ),
        Sequence(
            "FILE_FORMAT", Ref("EqualsSegment"), Ref("FileFormatSegment"), optional=True
        ),
        Sequence(
            "COPY_OPTIONS",
            Ref("EqualsSegment"),
            Ref("CopyOptionsSegment"),
            optional=True,
        ),
        Ref("TagBracketedEqualsSegment", optional=True),
        Ref("CommentEqualsClauseSegment", optional=True),
    )


@snowflake_dialect.segment()
class AlterStageSegment(BaseSegment):
    """A Snowflake ALTER STAGE statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-stage.html
    """

    type = "alter_stage_statement"

    match_grammar = Sequence(
        "ALTER",
        "STAGE",
        Sequence("IF", "EXISTS", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("ObjectReferenceSegment")),
            Sequence(
                "SET",
                Indent,
                OneOf(
                    Sequence(
                        OneOf(
                            Ref("InternalStageParameters"),
                            Sequence(
                                Sequence(
                                    "URL",
                                    Ref("EqualsSegment"),
                                    Ref("S3Path"),
                                    optional=True,
                                ),
                                Ref(
                                    "S3ExternalStageParameters",
                                    optional=True,
                                ),
                            ),
                            Sequence(
                                Sequence(
                                    "URL",
                                    Ref("EqualsSegment"),
                                    Ref("GCSPath"),
                                    optional=True,
                                ),
                                Ref(
                                    "GCSExternalStageParameters",
                                    optional=True,
                                ),
                            ),
                            Sequence(
                                Sequence(
                                    "URL",
                                    Ref("EqualsSegment"),
                                    Ref("AzureBlobStoragePath"),
                                    optional=True,
                                ),
                                Ref(
                                    "AzureBlobStorageExternalStageParameters",
                                    optional=True,
                                ),
                            ),
                            optional=True,
                        ),
                        Sequence(
                            "FILE_FORMAT",
                            Ref("EqualsSegment"),
                            Ref("FileFormatSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "COPY_OPTIONS",
                            Ref("EqualsSegment"),
                            Ref("CopyOptionsSegment"),
                            optional=True,
                        ),
                        Ref("CommentEqualsClauseSegment", optional=True),
                    ),
                    Ref("TagEqualsSegment"),
                ),
            ),
            Sequence(
                "REFRESH",
                Sequence(
                    "SUBPATH",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
            ),
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
                Ref("BooleanLiteralGrammar"),
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
        enforce_whitespace_preceding_terminator=True,
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
        enforce_whitespace_preceding_terminator=True,
    )


@snowflake_dialect.segment(replace=True)
class DescribeStatementSegment(BaseSegment):
    """`DESCRIBE` statement grammar.

    https://docs.snowflake.com/en/sql-reference/sql/desc.html
    """

    match_grammar = Sequence(
        OneOf("DESCRIBE", "DESC"),
        OneOf(
            # https://docs.snowflake.com/en/sql-reference/sql/desc-result.html
            Sequence(
                "RESULT",
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Sequence("LAST_QUERY_ID", Bracketed()),
                ),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-network-policy.html
            Sequence(
                "NETWORK",
                "POLICY",
                Ref("ObjectReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-share.html
            Sequence(
                "SHARE",
                Ref("ObjectReferenceSegment"),
                Sequence(
                    Ref("DotSegment"),
                    Ref("ObjectReferenceSegment"),
                    optional=True,
                ),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-user.html
            Sequence(
                "USER",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "WAREHOUSE",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "DATABASE",
                Ref("DatabaseReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-integration.html
            Sequence(
                OneOf(
                    "API",
                    "NOTIFICATION",
                    "SECURITY",
                    "STORAGE",
                ),
                "INTEGRATION",
                Ref("ObjectReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-session-policy.html
            Sequence(
                "SESSION",
                "POLICY",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "SCHEMA",
                Ref("SchemaReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-table.html
            Sequence(
                "TABLE",
                Ref("TableReferenceSegment"),
                Sequence(
                    "TYPE",
                    Ref("EqualsSegment"),
                    OneOf("COLUMNS", "STAGE"),
                    optional=True,
                ),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-external-table.html
            Sequence(
                "EXTERNAL",
                "TABLE",
                Ref("TableReferenceSegment"),
                Sequence(
                    "TYPE",
                    Ref("EqualsSegment"),
                    OneOf("COLUMNS", "STAGE"),
                    optional=True,
                ),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-view.html
            Sequence(
                "VIEW",
                Ref("TableReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-materialized-view.html
            Sequence(
                "MATERIALIZED",
                "VIEW",
                Ref("TableReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-sequence.html
            Sequence(
                "SEQUENCE",
                Ref("SequenceReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-masking-policy.html
            Sequence(
                "MASKING",
                "POLICY",
                Ref("ObjectReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-row-access-policy.html
            Sequence(
                "ROW",
                "ACCESS",
                "POLICY",
                Ref("ObjectReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-file-format.html
            Sequence(
                "FILE",
                "FORMAT",
                Ref("ObjectReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-stage.html
            Sequence(
                "STAGE",
                Ref("ObjectReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-pipe.html
            Sequence(
                "PIPE",
                Ref("ObjectReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-stream.html
            Sequence(
                "STREAM",
                Ref("ObjectReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-task.html
            Sequence(
                "TASK",
                Ref("ObjectReferenceSegment"),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-function.html
            Sequence(
                "FUNCTION",
                Ref("FunctionNameSegment"),
                Bracketed(
                    Delimited(
                        Ref("DatatypeSegment"),
                        optional=True,
                    ),
                ),
            ),
            # https://docs.snowflake.com/en/sql-reference/sql/desc-procedure.html
            Sequence(
                "PROCEDURE",
                Ref("FunctionNameSegment"),
                Bracketed(
                    Delimited(
                        Ref("DatatypeSegment"),
                        optional=True,
                    ),
                ),
            ),
        ),
    )
