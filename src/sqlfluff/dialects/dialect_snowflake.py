"""The Snowflake dialect.

Inherits from ANSI.

Based on https://docs.snowflake.com/en/sql-reference-commands.html
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    KeywordSegment,
    LiteralSegment,
    Matchable,
    MultiStringParser,
    Nothing,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
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
        RegexLexer(
            "single_quote",
            r"'([^'\\]|\\.|'')*'",
            CodeSegment,
        ),
        RegexLexer(
            "inline_comment",
            r"(--|#|//)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--", "#", "//")},
        ),
    ]
)

snowflake_dialect.insert_lexer_matchers(
    [
        # Keyword assigner needed for keyword functions.
        StringLexer("parameter_assigner", "=>", CodeSegment),
        StringLexer("function_assigner", "->", CodeSegment),
        RegexLexer("stage_path", r"(?:@[^\s;)]+|'@[^']+')", CodeSegment),
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
        RegexLexer(
            "inline_dollar_sign",
            r"[a-zA-Z_][a-zA-Z0-9_$]*\$[a-zA-Z0-9_$]*",
            CodeSegment,
        ),
        RegexLexer(
            # For use with https://docs.snowflake.com/en/sql-reference/sql/get.html
            # Accepts unquoted file paths that begin file://.
            # Unquoted file paths cannot include special characters.
            "unquoted_file_path",
            r"file://(?:[a-zA-Z]+:|/)+(?:[0-9a-zA-Z\\/_*?-]+)(?:\.[0-9a-zA-Z]+)?",
            CodeSegment,
        ),
        StringLexer("question_mark", "?", CodeSegment),
        StringLexer("exclude_bracket_open", "{-", CodeSegment),
        StringLexer("exclude_bracket_close", "-}", CodeSegment),
    ],
    before="like_operator",
)

# Check for ":=" operator before the equals operator to correctly parse walrus operator
# for Snowflake scripting block statements
# https://docs.snowflake.com/en/developer-guide/snowflake-scripting/variables
snowflake_dialect.insert_lexer_matchers(
    [
        StringLexer("walrus_operator", ":=", CodeSegment),
    ],
    before="equals",
)

snowflake_dialect.bracket_sets("bracket_pairs").add(
    ("exclude", "StartExcludeBracketSegment", "EndExcludeBracketSegment", True)
)

# Set the bare functions
snowflake_dialect.sets("bare_functions").clear()
snowflake_dialect.sets("bare_functions").update(
    [
        "CURRENT_DATE",
        "CURRENT_TIME",
        "CURRENT_TIMESTAMP",
        "CURRENT_USER",
        "LOCALTIME",
        "LOCALTIMESTAMP",
    ]
)

# Add all Snowflake compression types
snowflake_dialect.sets("compression_types").clear()
snowflake_dialect.sets("compression_types").update(
    [
        "AUTO",
        "AUTO_DETECT",
        "GZIP",
        "BZ2",
        "BROTLI",
        "ZSTD",
        "DEFLATE",
        "RAW_DEFLATE",
        "LZO",
        "NONE",
        "SNAPPY",
    ],
)

# Add all Snowflake supported file types
snowflake_dialect.sets("files_types").clear()
snowflake_dialect.sets("files_types").update(
    ["CSV", "JSON", "AVRO", "ORC" "PARQUET", "XML"],
)

snowflake_dialect.sets("warehouse_types").clear()
snowflake_dialect.sets("warehouse_types").update(
    [
        "STANDARD",
        "SNOWPARK-OPTIMIZED",
    ],
)

snowflake_dialect.sets("warehouse_sizes").clear()
snowflake_dialect.sets("warehouse_sizes").update(
    [
        "XSMALL",
        "SMALL",
        "MEDIUM",
        "LARGE",
        "XLARGE",
        "XXLARGE",
        "X2LARGE",
        "XXXLARGE",
        "X3LARGE",
        "X4LARGE",
        "X5LARGE",
        "X6LARGE",
        "X-SMALL",
        "X-LARGE",
        "2X-LARGE",
        "3X-LARGE",
        "4X-LARGE",
        "5X-LARGE",
        "6X-LARGE",
    ],
)

snowflake_dialect.sets("warehouse_scaling_policies").clear()
snowflake_dialect.sets("warehouse_scaling_policies").update(
    [
        "STANDARD",
        "ECONOMY",
    ],
)

snowflake_dialect.add(
    # In snowflake, these are case sensitive even though they're not quoted
    # so they need a different `name` and `type` so they're not picked up
    # by other rules.
    ParameterAssignerSegment=StringParser(
        "=>", SymbolSegment, type="parameter_assigner"
    ),
    FunctionAssignerSegment=StringParser("->", SymbolSegment, type="function_assigner"),
    # Walrus operator for Snowflake scripting block statements
    WalrusOperatorSegment=StringParser(":=", SymbolSegment, type="assignment_operator"),
    QuotedStarSegment=StringParser(
        "'*'",
        IdentifierSegment,
        type="quoted_star",
        trim_chars=("'",),
    ),
    # Any identifier is valid as a semi-structured element in Snowflake
    # as long as it's not a reserved keyword
    # https://docs.snowflake.com/en/sql-reference/identifiers-syntax
    NakedSemiStructuredElementSegment=RegexParser(
        r"[a-zA-Z_][a-zA-Z0-9_$]*",
        CodeSegment,
        type="semi_structured_element",
    ),
    QuotedSemiStructuredElementSegment=TypedParser(
        "double_quote",
        CodeSegment,
        type="semi_structured_element",
    ),
    ColumnIndexIdentifierSegment=RegexParser(
        r"\$[0-9]+",
        IdentifierSegment,
        type="column_index_identifier_segment",
    ),
    LocalVariableNameSegment=RegexParser(
        r"[a-zA-Z0-9_]*",
        CodeSegment,
        type="variable",
    ),
    ReferencedVariableNameSegment=RegexParser(
        r"\$[A-Z_][A-Z0-9_]*",
        CodeSegment,
        type="variable",
        trim_chars=("$",),
    ),
    # We use a RegexParser instead of keywords as some (those with dashes) require
    # quotes:
    WarehouseType=OneOf(
        MultiStringParser(
            [
                type
                for type in snowflake_dialect.sets("warehouse_types")
                if "-" not in type
            ],
            CodeSegment,
            type="warehouse_size",
        ),
        MultiStringParser(
            [f"'{type}'" for type in snowflake_dialect.sets("warehouse_types")],
            CodeSegment,
            type="warehouse_size",
        ),
    ),
    WarehouseSize=OneOf(
        MultiStringParser(
            [
                size
                for size in snowflake_dialect.sets("warehouse_sizes")
                if "-" not in size
            ],
            CodeSegment,
            type="warehouse_size",
        ),
        MultiStringParser(
            [f"'{size}'" for size in snowflake_dialect.sets("warehouse_sizes")],
            CodeSegment,
            type="warehouse_size",
        ),
    ),
    CompressionType=OneOf(
        MultiStringParser(
            snowflake_dialect.sets("compression_types"),
            KeywordSegment,
            type="compression_type",
        ),
        MultiStringParser(
            [
                f"'{compression}'"
                for compression in snowflake_dialect.sets("compression_types")
            ],
            KeywordSegment,
            type="compression_type",
        ),
    ),
    ScalingPolicy=OneOf(
        MultiStringParser(
            snowflake_dialect.sets("warehouse_scaling_policies"),
            KeywordSegment,
            type="scaling_policy",
        ),
        MultiStringParser(
            [
                f"'{scaling_policy}'"
                for scaling_policy in snowflake_dialect.sets(
                    "warehouse_scaling_policies"
                )
            ],
            KeywordSegment,
            type="scaling_policy",
        ),
    ),
    ValidationModeOptionSegment=RegexParser(
        r"'?RETURN_(?:\d+_ROWS|ERRORS|ALL_ERRORS)'?",
        CodeSegment,
        type="validation_mode_option",
    ),
    CopyOptionOnErrorSegment=RegexParser(
        r"'?CONTINUE'?|'?SKIP_FILE(?:_[0-9]+%?)?'?|'?ABORT_STATEMENT'?",
        LiteralSegment,
        type="copy_on_error_option",
    ),
    DoubleQuotedUDFBody=TypedParser(
        "double_quote",
        CodeSegment,
        type="udf_body",
        trim_chars=('"',),
    ),
    SingleQuotedUDFBody=TypedParser(
        "single_quote",
        CodeSegment,
        type="udf_body",
        trim_chars=("'",),
    ),
    DollarQuotedUDFBody=TypedParser(
        "dollar_quote",
        CodeSegment,
        type="udf_body",
        trim_chars=("$",),
    ),
    StagePath=RegexParser(
        r"(?:@[^\s;)]+|'@[^']+')",
        IdentifierSegment,
        type="stage_path",
    ),
    S3Path=RegexParser(
        # https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
        r"'s3://.*'",
        CodeSegment,
        type="bucket_path",
    ),
    GCSPath=RegexParser(
        # https://cloud.google.com/storage/docs/naming-buckets
        r"'gcs://.*",
        CodeSegment,
        type="bucket_path",
    ),
    AzureBlobStoragePath=RegexParser(
        # https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftstorage
        r"'azure://.*",
        CodeSegment,
        type="bucket_path",
    ),
    UnquotedFilePath=TypedParser(
        "unquoted_file_path",
        CodeSegment,
        type="unquoted_file_path",
    ),
    SnowflakeEncryptionOption=MultiStringParser(
        ["'SNOWFLAKE_FULL'", "'SNOWFLAKE_SSE'"],
        CodeSegment,
        type="stage_encryption_option",
    ),
    S3EncryptionOption=MultiStringParser(
        ["'AWS_CSE'", "'AWS_SSE_S3'", "'AWS_SSE_KMS'"],
        CodeSegment,
        type="stage_encryption_option",
    ),
    GCSEncryptionOption=StringParser(
        "'GCS_SSE_KMS'",
        CodeSegment,
        type="stage_encryption_option",
    ),
    AzureBlobStorageEncryptionOption=StringParser(
        "'AZURE_CSE'",
        CodeSegment,
        type="stage_encryption_option",
    ),
    FileType=OneOf(
        MultiStringParser(
            snowflake_dialect.sets("file_types"),
            CodeSegment,
            type="file_type",
        ),
        MultiStringParser(
            [f"'{file_type}'" for file_type in snowflake_dialect.sets("file_types")],
            CodeSegment,
            type="file_type",
        ),
    ),
    IntegerSegment=RegexParser(
        # An unquoted integer that can be passed as an argument to Snowflake functions.
        r"[0-9]+",
        LiteralSegment,
        type="integer_literal",
    ),
    SystemFunctionName=RegexParser(
        r"SYSTEM\$([A-Za-z0-9_]*)",
        CodeSegment,
        type="system_function_name",
    ),
    GroupByContentsGrammar=Delimited(
        OneOf(
            Ref("ColumnReferenceSegment"),
            # Can `GROUP BY 1`
            Ref("NumericLiteralSegment"),
            # Can `GROUP BY coalesce(col, 1)`
            Ref("ExpressionSegment"),
        ),
        terminators=[
            "ORDER",
            "LIMIT",
            "FETCH",
            "OFFSET",
            "HAVING",
            "QUALIFY",
            "WINDOW",
        ],
    ),
    LimitLiteralGrammar=OneOf(
        Ref("NumericLiteralSegment"),
        "NULL",
        # '' and $$$$ are allowed as alternatives to NULL.
        Ref("QuotedLiteralSegment"),
    ),
    StartExcludeBracketSegment=StringParser(
        "{-", SymbolSegment, type="start_exclude_bracket"
    ),
    EndExcludeBracketSegment=StringParser(
        "-}", SymbolSegment, type="end_exclude_bracket"
    ),
    QuestionMarkSegment=StringParser("?", SymbolSegment, type="question_mark"),
    CaretSegment=StringParser("^", SymbolSegment, type="caret"),
    DollarSegment=StringParser("$", SymbolSegment, type="dollar"),
    PatternQuantifierGrammar=Sequence(
        OneOf(
            Ref("PositiveSegment"),
            Ref("StarSegment"),
            Ref("QuestionMarkSegment"),
            Bracketed(
                OneOf(
                    Ref("NumericLiteralSegment"),
                    Sequence(
                        Ref("NumericLiteralSegment"),
                        Ref("CommaSegment"),
                    ),
                    Sequence(
                        Ref("CommaSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                    Sequence(
                        Ref("NumericLiteralSegment"),
                        Ref("CommaSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                ),
                bracket_type="curly",
                bracket_pairs_set="bracket_pairs",
            ),
        ),
        # To put a quantifier into “reluctant mode”.
        Ref("QuestionMarkSegment", optional=True),
        allow_gaps=False,
    ),
    PatternSymbolGrammar=Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("PatternQuantifierGrammar", optional=True),
        allow_gaps=False,
    ),
    PatternOperatorGrammar=OneOf(
        Ref("PatternSymbolGrammar"),
        Sequence(
            OneOf(
                Bracketed(
                    OneOf(
                        AnyNumberOf(
                            Ref("PatternOperatorGrammar"),
                        ),
                        Delimited(
                            Ref("PatternOperatorGrammar"),
                            delimiter=Ref("BitwiseOrSegment"),
                        ),
                    ),
                    bracket_type="exclude",
                    bracket_pairs_set="bracket_pairs",
                ),
                Bracketed(
                    OneOf(
                        AnyNumberOf(
                            Ref("PatternOperatorGrammar"),
                        ),
                        Delimited(
                            Ref("PatternOperatorGrammar"),
                            delimiter=Ref("BitwiseOrSegment"),
                        ),
                    ),
                ),
                Sequence(
                    "PERMUTE",
                    Bracketed(
                        Delimited(
                            Ref("PatternSymbolGrammar"),
                        ),
                    ),
                ),
            ),
            # Operators can also be followed by a quantifier.
            Ref("PatternQuantifierGrammar", optional=True),
            allow_gaps=False,
        ),
    ),
    ContextHeadersGrammar=OneOf(
        "CURRENT_ACCOUNT",
        "CURRENT_CLIENT",
        "CURRENT_DATABASE",
        "CURRENT_DATE",
        "CURRENT_IP_ADDRESS",
        "CURRENT_REGION",
        "CURRENT_ROLE",
        "CURRENT_SCHEMA",
        "CURRENT_SCHEMAS",
        "CURRENT_SESSION",
        "CURRENT_STATEMENT",
        "CURRENT_TIME",
        "CURRENT_TIMESTAMP",
        "CURRENT_TRANSACTION",
        "CURRENT_USER",
        "CURRENT_VERSION",
        "CURRENT_WAREHOUSE",
        "LAST_QUERY_ID",
        "LAST_TRANSACTION",
        "LOCALTIME",
        "LOCALTIMESTAMP",
    ),
)

snowflake_dialect.replace(
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            # See https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html
            r"[a-zA-Z_][a-zA-Z0-9_$]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("ReferencedVariableNameSegment"),
        ]
    ),
    AccessorGrammar=AnyNumberOf(
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
        AnySetOf(
            Ref("MatchRecognizeClauseSegment"),
            Ref("ChangesClauseSegment"),
            Ref("ConnectByClauseSegment"),
            Ref("FromBeforeExpressionSegment"),
            Ref("FromPivotExpressionSegment"),
            AnyNumberOf(Ref("FromUnpivotExpressionSegment")),
            Ref("SamplingExpressionSegment"),
            min_times=1,
        ),
        Ref("AliasExpressionSegment", optional=True),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("ColumnIndexIdentifierSegment"),
        Ref("ReferencedVariableNameSegment"),
        Ref("StagePath"),
        Sequence(
            "IDENTIFIER",
            Bracketed(
                OneOf(
                    Ref("SingleQuotedIdentifierSegment"),
                    Ref("ReferencedVariableNameSegment"),
                ),
            ),
        ),
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
    BaseExpressionElementGrammar=ansi_dialect.get_grammar(
        "BaseExpressionElementGrammar"
    ).copy(
        insert=[
            # Allow use of CONNECT_BY_ROOT pseudo-columns.
            # https://docs.snowflake.com/en/sql-reference/constructs/connect-by.html#:~:text=Snowflake%20supports%20the%20CONNECT_BY_ROOT,the%20Examples%20section%20below.
            Sequence("CONNECT_BY_ROOT", Ref("ColumnReferenceSegment")),
        ],
        before=Ref("LiteralGrammar"),
    ),
    QuotedLiteralSegment=OneOf(
        # https://docs.snowflake.com/en/sql-reference/data-types-text.html#string-constants
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
    LikeGrammar=OneOf(
        # https://docs.snowflake.com/en/sql-reference/functions/like.html
        Sequence("LIKE", OneOf("ALL", "ANY", optional=True)),
        "RLIKE",
        Sequence("ILIKE", Ref.keyword("ANY", optional=True)),
        "REGEXP",
    ),
    SelectClauseTerminatorGrammar=OneOf(
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        "FETCH",
        "OFFSET",
        Ref("SetOperatorSegment"),
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        "FETCH",
        "OFFSET",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "QUALIFY",
        "WINDOW",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("WithDataClauseSegment"),
    ),
    WhereClauseTerminatorGrammar=OneOf(
        "LIMIT",
        "FETCH",
        "OFFSET",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "QUALIFY",
        "WINDOW",
        "OVERLAPS",
    ),
    OrderByClauseTerminators=OneOf(
        "LIMIT",
        "HAVING",
        "QUALIFY",
        # For window functions
        "WINDOW",
        Ref("FrameClauseUnitGrammar"),
        "SEPARATOR",
        "FETCH",
        "OFFSET",
        "MEASURES",
    ),
    TrimParametersGrammar=Nothing(),
    GroupByClauseTerminatorGrammar=OneOf(
        "ORDER", "LIMIT", "FETCH", "OFFSET", "HAVING", "QUALIFY", "WINDOW"
    ),
    HavingClauseTerminatorGrammar=OneOf(
        Sequence("ORDER", "BY"),
        "LIMIT",
        "QUALIFY",
        "WINDOW",
        "FETCH",
        "OFFSET",
    ),
)

# Add all Snowflake keywords
snowflake_dialect.sets("unreserved_keywords").clear()
snowflake_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", snowflake_unreserved_keywords
)

snowflake_dialect.sets("reserved_keywords").clear()
snowflake_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", snowflake_reserved_keywords
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


class FunctionNameSegment(ansi.FunctionNameSegment):
    """Function name, including any prefix bits, e.g. project or schema.

    Overriding FunctionNameSegment to support Snowflake's IDENTIFIER pseudo-function.
    """

    type = "function_name"
    match_grammar: Matchable = Sequence(
        # Project name, schema identifier, etc.
        AnyNumberOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Ref("DotSegment"),
            ),
            terminators=[Ref("BracketedSegment")],
        ),
        # Base function name
        OneOf(
            Ref("FunctionNameIdentifierSegment"),
            Ref("QuotedIdentifierSegment"),
            # Snowflake's IDENTIFIER pseudo-function
            # https://docs.snowflake.com/en/sql-reference/identifier-literal.html
            Sequence(
                "IDENTIFIER",
                Bracketed(
                    OneOf(
                        Ref("SingleQuotedIdentifierSegment"),
                        Ref("ReferencedVariableNameSegment"),
                    ),
                ),
            ),
        ),
        allow_gaps=False,
    )


class DatabaseRoleReferenceSegment(ansi.ObjectReferenceSegment):
    """Database role reference ([database_name.]rolename).

    See https://docs.snowflake.com/en/sql-reference/sql/create-database-role
    (the <name> item of the "Required parameters" section).
    """

    type = "database_role_reference"
    match_grammar: Matchable = OneOf(
        Sequence(
            Sequence(Ref("SingleIdentifierGrammar"), Ref("DotSegment"), optional=True),
            Ref("SingleIdentifierGrammar"),
        ),
    )


class ConnectByClauseSegment(BaseSegment):
    """A `CONNECT BY` clause.

    https://docs.snowflake.com/en/sql-reference/constructs/connect-by.html
    """

    type = "connectby_clause"
    match_grammar = Sequence(
        "START",
        "WITH",
        Ref("ExpressionSegment"),
        "CONNECT",
        "BY",
        Delimited(
            Sequence(
                Ref.keyword("PRIOR", optional=True),
                Ref("ColumnReferenceSegment"),
                Ref("EqualsSegment"),
                Ref.keyword("PRIOR", optional=True),
                Ref("ColumnReferenceSegment"),
            ),
        ),
    )


class GroupByClauseSegment(ansi.GroupByClauseSegment):
    """A `GROUP BY` clause like in `SELECT`.

    Snowflake supports Cube, Rollup, and Grouping Sets

    https://docs.snowflake.com/en/sql-reference/constructs/group-by.html
    """

    match_grammar: Matchable = Sequence(
        "GROUP",
        "BY",
        Indent,
        OneOf(
            Sequence(
                OneOf("CUBE", "ROLLUP", Sequence("GROUPING", "SETS")),
                Bracketed(
                    Ref("GroupByContentsGrammar"),
                ),
            ),
            "ALL",
            Ref("GroupByContentsGrammar"),
        ),
        Dedent,
    )


class ValuesClauseSegment(ansi.ValuesClauseSegment):
    """A `VALUES` clause like in `INSERT`."""

    match_grammar = Sequence(
        "VALUES",
        Delimited(
            Bracketed(
                Delimited(
                    # DEFAULT and NULL keywords used in
                    # INSERT INTO statement.
                    "DEFAULT",
                    "NULL",
                    Ref("ExpressionSegment"),
                ),
                parse_mode=ParseMode.GREEDY,
            ),
        ),
    )


class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    https://docs.snowflake.com/en/sql-reference/sql/insert.html
    https://docs.snowflake.com/en/sql-reference/sql/insert-multi-table.html
    """

    type = "insert_statement"
    match_grammar = Sequence(
        "INSERT",
        Ref.keyword("OVERWRITE", optional=True),
        OneOf(
            # Single table INSERT INTO.
            Sequence(
                "INTO",
                Ref("TableReferenceSegment"),
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                Ref("SelectableGrammar"),
            ),
            # Unconditional multi-table INSERT INTO.
            Sequence(
                "ALL",
                AnyNumberOf(
                    Sequence(
                        "INTO",
                        Ref("TableReferenceSegment"),
                        Ref("BracketedColumnReferenceListGrammar", optional=True),
                        Ref("ValuesClauseSegment", optional=True),
                    ),
                    min_times=1,
                ),
                Ref("SelectStatementSegment"),
            ),
            # Conditional multi-table INSERT INTO.
            Sequence(
                OneOf(
                    "FIRST",
                    "ALL",
                ),
                AnyNumberOf(
                    Sequence(
                        "WHEN",
                        Ref("ExpressionSegment"),
                        "THEN",
                        AnyNumberOf(
                            Sequence(
                                "INTO",
                                Ref("TableReferenceSegment"),
                                Ref(
                                    "BracketedColumnReferenceListGrammar", optional=True
                                ),
                                Ref("ValuesClauseSegment", optional=True),
                            ),
                            min_times=1,
                        ),
                    ),
                    min_times=1,
                ),
                Sequence(
                    "ELSE",
                    "INTO",
                    Ref("TableReferenceSegment"),
                    Ref("BracketedColumnReferenceListGrammar", optional=True),
                    Ref("ValuesClauseSegment", optional=True),
                    optional=True,
                ),
                Ref("SelectStatementSegment"),
            ),
        ),
    )


class FunctionDefinitionGrammar(ansi.FunctionDefinitionGrammar):
    """This is the body of a `CREATE FUNCTION AS` statement."""

    match_grammar = Sequence(
        "AS",
        Ref("QuotedLiteralSegment"),
        Sequence(
            "LANGUAGE",
            Ref("NakedIdentifierSegment"),
            optional=True,
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("AccessStatementSegment"),
            Ref("CreateStatementSegment"),
            Ref("CreateTaskSegment"),
            Ref("CreateUserSegment"),
            Ref("CreateCloneStatementSegment"),
            Ref("CreateProcedureStatementSegment"),
            Ref("AlterProcedureStatementSegment"),
            Ref("ScriptingBlockStatementSegment"),
            Ref("ScriptingLetStatementSegment"),
            Ref("ReturnStatementSegment"),
            Ref("ShowStatementSegment"),
            Ref("AlterAccountStatementSegment"),
            Ref("AlterUserStatementSegment"),
            Ref("AlterSessionStatementSegment"),
            Ref("AlterTaskStatementSegment"),
            Ref("SetAssignmentStatementSegment"),
            Ref("CallStoredProcedureSegment"),
            Ref("MergeStatementSegment"),
            Ref("CopyIntoTableStatementSegment"),
            Ref("CopyIntoLocationStatementSegment"),
            Ref("FormatTypeOptions"),
            Ref("AlterWarehouseStatementSegment"),
            Ref("AlterShareStatementSegment"),
            Ref("CreateExternalTableSegment"),
            Ref("AlterExternalTableStatementSegment"),
            Ref("CreateSchemaStatementSegment"),
            Ref("AlterSchemaStatementSegment"),
            Ref("CreateFunctionStatementSegment"),
            Ref("AlterFunctionStatementSegment"),
            Ref("CreateExternalFunctionStatementSegment"),
            Ref("CreateStageSegment"),
            Ref("AlterStageSegment"),
            Ref("CreateStreamStatementSegment"),
            Ref("AlterStreamStatementSegment"),
            Ref("UnsetStatementSegment"),
            Ref("UndropStatementSegment"),
            Ref("CommentStatementSegment"),
            Ref("CallStatementSegment"),
            Ref("AlterViewStatementSegment"),
            Ref("AlterMaterializedViewStatementSegment"),
            Ref("DropProcedureStatementSegment"),
            Ref("DropExternalTableStatementSegment"),
            Ref("DropMaterializedViewStatementSegment"),
            Ref("DropObjectStatementSegment"),
            Ref("CreateFileFormatSegment"),
            Ref("AlterFileFormatSegment"),
            Ref("AlterPipeSegment"),
            Ref("ListStatementSegment"),
            Ref("GetStatementSegment"),
            Ref("PutStatementSegment"),
            Ref("RemoveStatementSegment"),
            Ref("CreateDatabaseFromShareStatementSegment"),
            Ref("CreateDatabaseRoleStatementSegment"),
            Ref("AlterRoleStatementSegment"),
            Ref("AlterStorageIntegrationSegment"),
            Ref("ExecuteImmediateClauseSegment"),
            Ref("ExecuteTaskClauseSegment"),
            Ref("CreateResourceMonitorStatementSegment"),
            Ref("AlterResourceMonitorStatementSegment"),
            Ref("CreateSequenceStatementSegment"),
            Ref("AlterSequenceStatementSegment"),
            Ref("AlterDatabaseSegment"),
            Ref("AlterMaskingPolicySegment"),
            Ref("AlterNetworkPolicyStatementSegment"),
        ],
        remove=[
            Ref("CreateIndexStatementSegment"),
            Ref("DropIndexStatementSegment"),
        ],
    )


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
            Bracketed(Delimited(Ref("LocalVariableNameSegment"))),
            Ref("EqualsSegment"),
            Bracketed(
                Delimited(
                    Ref("ExpressionSegment"),
                ),
            ),
        ),
    )


class CallStoredProcedureSegment(BaseSegment):
    """This is a CALL statement used to execute a stored procedure.

    https://docs.snowflake.com/en/sql-reference/sql/call.html
    """

    type = "call_segment"

    match_grammar = Sequence(
        "CALL",
        Ref("FunctionSegment"),
    )


class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions.

    https://docs.snowflake.com/en/sql-reference/functions/listagg.html.
    https://docs.snowflake.com/en/sql-reference/functions/array_agg.html.
    """

    type = "withingroup_clause"

    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(
            Ref("OrderByClauseSegment", optional=True), parse_mode=ParseMode.GREEDY
        ),
    )


class FromExpressionElementSegment(ansi.FromExpressionElementSegment):
    """A table expression."""

    type = "from_expression_element"
    match_grammar = Sequence(
        Ref("PreTableFunctionKeywordsGrammar", optional=True),
        OptionallyBracketed(Ref("TableExpressionSegment")),
        Ref(
            "AliasExpressionSegment",
            exclude=OneOf(
                Ref("FromClauseTerminatorGrammar"),
                Ref("SamplingExpressionSegment"),
                Ref("ChangesClauseSegment"),
                Ref("JoinLikeClauseGrammar"),
                "CROSS",
            ),
            optional=True,
        ),
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#flattening_arrays
        Sequence("WITH", "OFFSET", Ref("AliasExpressionSegment"), optional=True),
        Ref("SamplingExpressionSegment", optional=True),
        Ref("PostTableExpressionGrammar", optional=True),
    )


class PatternSegment(BaseSegment):
    """A `PATTERN` expression.

    https://docs.snowflake.com/en/sql-reference/constructs/match_recognize.html
    """

    type = "pattern_expression"
    match_grammar = Sequence(
        # https://docs.snowflake.com/en/sql-reference/constructs/match_recognize.html#pattern-specifying-the-pattern-to-match
        Ref("CaretSegment", optional=True),
        OneOf(
            AnyNumberOf(
                Ref("PatternOperatorGrammar"),
            ),
            Delimited(
                Ref("PatternOperatorGrammar"),
                delimiter=Ref("BitwiseOrSegment"),
            ),
        ),
        Ref("DollarSegment", optional=True),
    )


class MatchRecognizeClauseSegment(BaseSegment):
    """A `MATCH_RECOGNIZE` clause.

    https://docs.snowflake.com/en/sql-reference/constructs/match_recognize.html
    """

    type = "match_recognize_clause"
    match_grammar = Sequence(
        "MATCH_RECOGNIZE",
        Bracketed(
            Ref("PartitionClauseSegment", optional=True),
            Ref("OrderByClauseSegment", optional=True),
            Sequence(
                "MEASURES",
                Delimited(
                    Sequence(
                        # The edges of the window frame can be specified
                        # by using either RUNNING or FINAL semantics.
                        # https://docs.snowflake.com/en/sql-reference/constructs/match_recognize.html#expressions-in-define-and-measures-clauses
                        OneOf(
                            "FINAL",
                            "RUNNING",
                            optional=True,
                        ),
                        Ref("ExpressionSegment"),
                        Ref("AliasExpressionSegment"),
                    ),
                ),
                optional=True,
            ),
            OneOf(
                Sequence(
                    "ONE",
                    "ROW",
                    "PER",
                    "MATCH",
                ),
                Sequence(
                    "ALL",
                    "ROWS",
                    "PER",
                    "MATCH",
                    OneOf(
                        Sequence(
                            "SHOW",
                            "EMPTY",
                            "MATCHES",
                        ),
                        Sequence(
                            "OMIT",
                            "EMPTY",
                            "MATCHES",
                        ),
                        Sequence(
                            "WITH",
                            "UNMATCHED",
                            "ROWS",
                        ),
                        optional=True,
                    ),
                ),
                optional=True,
            ),
            Sequence(
                "AFTER",
                "MATCH",
                "SKIP",
                OneOf(
                    Sequence(
                        "PAST",
                        "LAST",
                        "ROW",
                    ),
                    Sequence(
                        "TO",
                        "NEXT",
                        "ROW",
                    ),
                    Sequence(
                        "TO",
                        OneOf("FIRST", "LAST", optional=True),
                        Ref("SingleIdentifierGrammar"),
                    ),
                ),
                optional=True,
            ),
            "PATTERN",
            Bracketed(
                Ref("PatternSegment"),
            ),
            "DEFINE",
            Delimited(
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    "AS",
                    Ref("ExpressionSegment"),
                ),
            ),
        ),
    )


class ChangesClauseSegment(BaseSegment):
    """A `CHANGES` clause.

    https://docs.snowflake.com/en/sql-reference/constructs/changes.html
    """

    type = "changes_clause"
    match_grammar = Sequence(
        "CHANGES",
        Bracketed(
            "INFORMATION",
            Ref("ParameterAssignerSegment"),
            OneOf("DEFAULT", "APPEND_ONLY"),
        ),
        OneOf(
            Sequence(
                "AT",
                Bracketed(
                    OneOf("TIMESTAMP", "OFFSET", "STATEMENT"),
                    Ref("ParameterAssignerSegment"),
                    Ref("ExpressionSegment"),
                ),
            ),
            Sequence(
                "BEFORE",
                Bracketed(
                    "STATEMENT",
                    Ref("ParameterAssignerSegment"),
                    Ref("ExpressionSegment"),
                ),
            ),
        ),
        Sequence(
            "END",
            Bracketed(
                OneOf("TIMESTAMP", "OFFSET", "STATEMENT"),
                Ref("ParameterAssignerSegment"),
                Ref("ExpressionSegment"),
            ),
            optional=True,
        ),
    )


class FromAtExpressionSegment(BaseSegment):
    """An AT expression."""

    type = "from_at_expression"
    match_grammar = Sequence(
        "AT",
        Bracketed(
            OneOf("TIMESTAMP", "OFFSET", "STATEMENT"),
            Ref("ParameterAssignerSegment"),
            Ref("ExpressionSegment"),
        ),
    )


class FromBeforeExpressionSegment(BaseSegment):
    """A BEFORE expression."""

    type = "from_before_expression"
    match_grammar = Sequence(
        "BEFORE",
        Bracketed(
            OneOf("TIMESTAMP", "OFFSET", "STATEMENT"),
            Ref("ParameterAssignerSegment"),
            Ref("ExpressionSegment"),
            parse_mode=ParseMode.GREEDY,
        ),
    )


class FromPivotExpressionSegment(BaseSegment):
    """A PIVOT expression."""

    type = "from_pivot_expression"
    match_grammar = Sequence(
        "PIVOT",
        Bracketed(
            Ref("FunctionSegment"),
            "FOR",
            Ref("SingleIdentifierGrammar"),
            "IN",
            Bracketed(Delimited(Ref("LiteralGrammar"))),
        ),
    )


class FromUnpivotExpressionSegment(BaseSegment):
    """An UNPIVOT expression."""

    type = "from_unpivot_expression"
    match_grammar = Sequence(
        "UNPIVOT",
        Bracketed(
            Ref("SingleIdentifierGrammar"),
            "FOR",
            Ref("SingleIdentifierGrammar"),
            "IN",
            Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
        ),
    )


class SamplingExpressionSegment(ansi.SamplingExpressionSegment):
    """A sampling expression."""

    match_grammar = Sequence(
        OneOf("SAMPLE", "TABLESAMPLE"),
        OneOf("BERNOULLI", "ROW", "SYSTEM", "BLOCK", optional=True),
        Bracketed(
            OneOf(Ref("NumericLiteralSegment"), Ref("ReferencedVariableNameSegment")),
            Ref.keyword("ROWS", optional=True),
        ),
        Sequence(
            OneOf("REPEATABLE", "SEED"),
            Bracketed(Ref("NumericLiteralSegment")),
            optional=True,
        ),
    )


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


class SemiStructuredAccessorSegment(BaseSegment):
    """A semi-structured data accessor segment.

    https://docs.snowflake.com/en/user-guide/semistructured-considerations.html
    """

    type = "semi_structured_expression"
    match_grammar = Sequence(
        OneOf(
            # If a field is already a VARIANT, this could
            # be initiated by a colon or a dot. This is particularly
            # useful when a field is an ARRAY of objects.
            Ref("DotSegment"),
            Ref("ColonSegment"),
        ),
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
                allow_gaps=True,
            ),
            Ref("ArrayAccessorSegment", optional=True),
            allow_gaps=True,
        ),
        allow_gaps=True,
    )


class QualifyClauseSegment(BaseSegment):
    """A `QUALIFY` clause like in `SELECT`.

    https://docs.snowflake.com/en/sql-reference/constructs/qualify.html
    """

    type = "qualify_clause"
    match_grammar = Sequence(
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


class SelectStatementSegment(ansi.SelectStatementSegment):
    """A snowflake `SELECT` statement including optional Qualify.

    https://docs.snowflake.com/en/sql-reference/constructs/qualify.html
    """

    type = "select_statement"

    match_grammar = ansi.SelectStatementSegment.match_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OrderByClauseSegment", optional=True),
    )


class SelectClauseElementSegment(ansi.SelectClauseElementSegment):
    """Inherit from ansi but also allow for Snowflake System Functions.

    https://docs.snowflake.com/en/sql-reference/functions-system
    """

    match_grammar = ansi.SelectClauseElementSegment.match_grammar.copy(
        insert=[
            Sequence(
                Ref("SystemFunctionName"),
                Bracketed(Ref("QuotedLiteralSegment")),
            )
        ],
        before=Ref("WildcardExpressionSegment"),
    )


class WildcardExpressionSegment(ansi.WildcardExpressionSegment):
    """An extension of the star expression for Snowflake."""

    match_grammar = ansi.WildcardExpressionSegment.match_grammar.copy(
        insert=[
            # Optional Exclude or Rename clause
            Ref("ExcludeClauseSegment", optional=True),
            Ref("ReplaceClauseSegment", optional=True),
            Ref("RenameClauseSegment", optional=True),
        ]
    )


class ExcludeClauseSegment(BaseSegment):
    """A snowflake SELECT EXCLUDE clause.

    https://docs.snowflake.com/en/sql-reference/sql/select.html
    """

    type = "select_exclude_clause"
    match_grammar = Sequence(
        "EXCLUDE",
        OneOf(
            Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
            Ref("SingleIdentifierGrammar"),
        ),
    )


class RenameClauseSegment(BaseSegment):
    """A snowflake SELECT RENAME clause.

    https://docs.snowflake.com/en/sql-reference/sql/select.html
    """

    type = "select_rename_clause"
    match_grammar = Sequence(
        "RENAME",
        OneOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                "AS",
                Ref("SingleIdentifierGrammar"),
            ),
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("SingleIdentifierGrammar"),
                        "AS",
                        Ref("SingleIdentifierGrammar"),
                    )
                )
            ),
        ),
    )


class ReplaceClauseSegment(BaseSegment):
    """A snowflake SELECT REPLACE clause.

    https://docs.snowflake.com/en/sql-reference/sql/select.html
    """

    type = "select_replace_clause"
    match_grammar = Sequence(
        "REPLACE",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ExpressionSegment"),
                    "AS",
                    Ref("SingleIdentifierGrammar"),
                )
            )
        ),
    )


class SelectClauseModifierSegment(ansi.SelectClauseModifierSegment):
    """Things that come after SELECT but before the columns, specifically for Snowflake.

    https://docs.snowflake.com/en/sql-reference/constructs.html
    """

    match_grammar = Sequence(
        OneOf("DISTINCT", "ALL", optional=True),
        # TOP N is unique to Snowflake, and we can optionally add DISTINCT/ALL in front
        # of it.
        Sequence("TOP", Ref("NumericLiteralSegment"), optional=True),
    )


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """An `ALTER TABLE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-table.html
    If possible, please keep the order below the same as Snowflake's doc:
    """

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Rename
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            # Swap With
            Sequence(
                "SWAP",
                "WITH",
                Ref("TableReferenceSegment"),
            ),
            # searchOptimizationAction
            # N.B. Since SEARCH and OPTIMIZATION are unreserved keywords
            # we move this above AlterTableTableColumnActionSegment
            # in order to avoid matching these as columns.
            Sequence(
                OneOf(
                    "ADD",
                    "DROP",
                ),
                "SEARCH",
                "OPTIMIZATION",
            ),
            Ref("AlterTableClusteringActionSegment"),
            Ref("AlterTableConstraintActionSegment"),
            # @TODO: constraintAction
            # @TODO: extTableColumnAction
            # SET Table options
            # @TODO: Restrict the list of parameters supported per Snowflake doc.
            Sequence(
                Ref.keyword("SET"),
                OneOf(
                    Ref("ParameterNameSegment"),
                    Ref.keyword("COMMENT"),
                ),
                Ref("EqualsSegment", optional=True),
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("NakedIdentifierSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            # @TODO: add more constraint actions
            Sequence(
                "DROP",
                Ref("PrimaryKeyGrammar"),
            ),
            Sequence(
                "ADD",
                Ref("PrimaryKeyGrammar"),
                Bracketed(Delimited(Ref("ColumnReferenceSegment"), optional=True)),
            ),
            Ref("AlterTableTableColumnActionSegment"),
            # @TODO: Set/unset TAG
            # UNSET Table options
            Sequence(
                Ref.keyword("UNSET"),
                Delimited(
                    OneOf(
                        Ref("ParameterNameSegment"),
                        Ref.keyword("COMMENT"),
                    ),
                ),
            ),
            # @TODO: Add/drop row access policies
        ),
    )


class AlterTableTableColumnActionSegment(BaseSegment):
    """ALTER TABLE `tableColumnAction` per defined in Snowflake's grammar.

    https://docs.snowflake.com/en/sql-reference/sql/alter-table.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-table-column.html

    If possible, please match the order of this sequence with what's defined in
    Snowflake's tableColumnAction grammar.
    """

    type = "alter_table_table_column_action"

    match_grammar = OneOf(
        # Add Column
        Sequence(
            "ADD",
            Ref.keyword("COLUMN", optional=True),
            # @TODO: Cannot specify IF NOT EXISTS if also specifying
            # DEFAULT, AUTOINCREMENT, IDENTITY UNIQUE, PRIMARY KEY, FOREIGN KEY
            Ref("IfNotExistsGrammar", optional=True),
            # Handle Multiple Columns
            Delimited(
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    Ref("DatatypeSegment"),
                    OneOf(
                        # Default
                        Sequence(
                            "DEFAULT",
                            Ref("ExpressionSegment"),
                        ),
                        # Auto-increment/identity column
                        Sequence(
                            OneOf(
                                "AUTOINCREMENT",
                                "IDENTITY",
                            ),
                            OneOf(
                                # ( <start_num>, <step_num> )
                                Bracketed(
                                    Ref("NumericLiteralSegment"),
                                    Ref("CommaSegment"),
                                    Ref("NumericLiteralSegment"),
                                ),
                                # START <num> INCREMENT <num>
                                Sequence(
                                    "START",
                                    Ref("NumericLiteralSegment"),
                                    "INCREMENT",
                                    Ref("NumericLiteralSegment"),
                                ),
                                optional=True,
                            ),
                        ),
                        optional=True,
                    ),
                    # @TODO: Add support for `inlineConstraint`
                    Sequence(
                        Ref.keyword("WITH", optional=True),
                        "MASKING",
                        "POLICY",
                        Ref("FunctionNameSegment"),
                        Sequence(
                            "USING",
                            Bracketed(
                                Delimited(
                                    OneOf(
                                        Ref("ColumnReferenceSegment"),
                                        Ref("ExpressionSegment"),
                                    )
                                ),
                            ),
                            optional=True,
                        ),
                        optional=True,
                    ),
                    Ref("CommentClauseSegment", optional=True),
                ),
            ),
        ),
        # Rename column
        Sequence(
            "RENAME",
            "COLUMN",
            Ref("ColumnReferenceSegment"),
            "TO",
            Ref("ColumnReferenceSegment"),
        ),
        # Alter/Modify column(s)
        Sequence(
            OneOf("ALTER", "MODIFY"),
            OptionallyBracketed(
                Delimited(
                    OneOf(
                        # Add things
                        Sequence(
                            Ref.keyword("COLUMN", optional=True),
                            Ref("ColumnReferenceSegment"),
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
                                Ref("CommentClauseSegment"),
                            ),
                        ),
                        Sequence(
                            "COLUMN",
                            Ref("ColumnReferenceSegment"),
                            "SET",
                            "MASKING",
                            "POLICY",
                            Ref("FunctionNameSegment"),
                            Sequence(
                                "USING",
                                Bracketed(
                                    Delimited(
                                        OneOf(
                                            Ref("ColumnReferenceSegment"),
                                            Ref("ExpressionSegment"),
                                        )
                                    ),
                                ),
                                optional=True,
                            ),
                            Ref.keyword("FORCE", optional=True),
                        ),
                        Sequence(
                            "COLUMN",
                            Ref("ColumnReferenceSegment"),
                            "UNSET",
                            "MASKING",
                            "POLICY",
                        ),
                        Sequence(
                            "COLUMN",
                            Ref("ColumnReferenceSegment"),
                            "SET",
                            "TAG",
                            Ref("TagReferenceSegment"),
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        Sequence(
                            "COLUMN",
                            Ref("ColumnReferenceSegment"),
                            "UNSET",
                            "TAG",
                            Ref("TagReferenceSegment"),
                        ),
                    ),
                ),
            ),
        ),
        # Drop column
        Sequence(
            "DROP",
            Ref.keyword("COLUMN", optional=True),
            Delimited(Ref("ColumnReferenceSegment")),
        ),
        # @TODO: Drop columns
        # vvvvv COPIED FROM ANSI vvvvv
        # @TODO: Removed these once `tableColumnAction` is properly supported.
        Sequence(
            OneOf("ADD", "MODIFY"),
            Ref.keyword("COLUMN", optional=True),
            Ref("ColumnDefinitionSegment"),
            OneOf(
                Sequence(OneOf("FIRST", "AFTER"), Ref("ColumnReferenceSegment")),
                # Bracketed Version of the same
                Ref("BracketedColumnReferenceListGrammar"),
                optional=True,
            ),
        ),
    )


class AlterTableClusteringActionSegment(BaseSegment):
    """ALTER TABLE `clusteringAction` per defined in Snowflake's grammar.

    https://docs.snowflake.com/en/sql-reference/sql/alter-table.html#clustering-actions-clusteringaction
    """

    type = "alter_table_clustering_action"

    match_grammar = OneOf(
        Sequence(
            "CLUSTER",
            "BY",
            OneOf(
                Ref("FunctionSegment"),
                Bracketed(Delimited(Ref("ExpressionSegment"))),
            ),
        ),
        # N.B. RECLUSTER is deprecated:
        # https://docs.snowflake.com/en/user-guide/tables-clustering-manual.html
        Sequence(
            "RECLUSTER",
            Sequence(
                "MAX_SIZE",
                Ref("EqualsSegment"),
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
            Ref("WhereClauseSegment", optional=True),
        ),
        Sequence(
            OneOf(
                "SUSPEND",
                "RESUME",
            ),
            "RECLUSTER",
        ),
        Sequence(
            "DROP",
            "CLUSTERING",
            "KEY",
        ),
    )


class AlterTableConstraintActionSegment(BaseSegment):
    """ALTER TABLE `constraintAction` per defined in Snowflake's grammar.

    https://docs.snowflake.com/en/sql-reference/sql/alter-table.html#constraint-actions-constraintaction
    """

    type = "alter_table_constraint_action"

    match_grammar = OneOf(
        # Add Column
        Sequence(
            "ADD",
            Sequence(
                "CONSTRAINT",
                OneOf(
                    Ref("NakedIdentifierSegment"),
                    Ref("QuotedIdentifierSegment"),
                ),
                optional=True,
            ),
            OneOf(
                Sequence(
                    Ref("PrimaryKeyGrammar"),
                    Bracketed(
                        Delimited(
                            Ref("ColumnReferenceSegment"),
                        ),
                    ),
                ),
                Sequence(
                    Sequence(
                        Ref("ForeignKeyGrammar"),
                        Bracketed(
                            Delimited(
                                Ref("ColumnReferenceSegment"),
                            )
                        ),
                    ),
                    "REFERENCES",
                    Ref("TableReferenceSegment"),
                    Bracketed(
                        Delimited(
                            Ref("ColumnReferenceSegment"),
                        ),
                        optional=True,
                    ),
                ),
                Sequence(
                    "UNIQUE", Bracketed(Ref("ColumnReferenceSegment"), optional=True)
                ),
            ),
        ),
        Sequence(
            "DROP",
            Sequence("CONSTRAINT", Ref("NakedIdentifierSegment"), optional=True),
            OneOf(
                Ref("PrimaryKeyGrammar"),
                Ref("ForeignKeyGrammar"),
                "UNIQUE",
            ),
            Delimited(Ref("ColumnReferenceSegment")),
        ),
        Sequence(
            "RENAME",
            "CONSTRAINT",
            Ref("NakedIdentifierSegment"),
            "TO",
            Ref("NakedIdentifierSegment"),
        ),
    )


class AlterWarehouseStatementSegment(BaseSegment):
    """An `ALTER WAREHOUSE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse.html

    """

    type = "alter_warehouse_statement"
    match_grammar = Sequence(
        "ALTER",
        "WAREHOUSE",
        Ref("IfExistsGrammar", optional=True),
        OneOf(
            Sequence(
                Ref("ObjectReferenceSegment", optional=True),
                OneOf(
                    "SUSPEND",
                    Sequence(
                        "RESUME",
                        Sequence("IF", "SUSPENDED", optional=True),
                    ),
                ),
            ),
            Sequence(
                Ref("ObjectReferenceSegment", optional=True),
                Sequence(
                    "ABORT",
                    "ALL",
                    "QUERIES",
                ),
            ),
            Sequence(
                Ref("ObjectReferenceSegment"),
                "RENAME",
                "TO",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                Ref("ObjectReferenceSegment", optional=True),
                "SET",
                OneOf(
                    AnyNumberOf(
                        Ref("CommaSegment", optional=True),
                        Ref("WarehouseObjectPropertiesSegment"),
                        Ref("CommentEqualsClauseSegment"),
                        Ref("WarehouseObjectParamsSegment"),
                    ),
                    Ref("TagEqualsSegment"),
                ),
            ),
            Sequence(
                Ref("ObjectReferenceSegment"),
                "UNSET",
                OneOf(
                    Delimited(Ref("NakedIdentifierSegment")),
                    Sequence("TAG", Delimited(Ref("TagReferenceSegment"))),
                ),
            ),
        ),
    )


class AlterShareStatementSegment(BaseSegment):
    """An `ALTER SHARE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-share.html

    """

    type = "alter_share_statement"
    match_grammar = Sequence(
        "ALTER",
        "SHARE",
        Ref("IfExistsGrammar", optional=True),
        Ref("NakedIdentifierSegment"),
        OneOf(
            Sequence(
                OneOf(
                    "ADD",
                    "REMOVE",
                ),
                "ACCOUNTS",
                Ref("EqualsSegment"),
                Delimited(Ref("NakedIdentifierSegment")),
                Sequence(
                    "SHARE_RESTRICTIONS",
                    Ref("EqualsSegment"),
                    Ref("BooleanLiteralGrammar"),
                    optional=True,
                ),
            ),
            Sequence(
                "SET",
                "ACCOUNTS",
                Ref("EqualsSegment"),
                Delimited(Ref("NakedIdentifierSegment")),
                Ref("CommentEqualsClauseSegment", optional=True),
            ),
            Sequence(
                "SET",
                Ref("TagEqualsSegment"),
            ),
            Sequence(
                "UNSET",
                "TAG",
                Ref("TagReferenceSegment"),
                AnyNumberOf(
                    Ref("CommaSegment"), Ref("TagReferenceSegment"), optional=True
                ),
            ),
            Sequence("UNSET", "COMMENT"),
        ),
    )


class AlterStorageIntegrationSegment(BaseSegment):
    """An `ALTER STORAGE INTEGRATION` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-storage-integration
    """

    type = "alter_storage_integration_statement"

    match_grammar = Sequence(
        "ALTER",
        Ref.keyword("STORAGE", optional=True),
        "INTEGRATION",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(
                "SET",
                OneOf(
                    Ref("TagEqualsSegment", optional=True),
                    AnySetOf(
                        Sequence(
                            "COMMENT", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")
                        ),
                        Sequence(
                            "ENABLED",
                            Ref("EqualsSegment"),
                            Ref("BooleanLiteralGrammar"),
                        ),
                        OneOf(
                            AnySetOf(
                                Sequence(
                                    "STORAGE_AWS_ROLE_ARN",
                                    Ref("EqualsSegment"),
                                    Ref("QuotedLiteralSegment"),
                                ),
                                Sequence(
                                    "STORAGE_AWS_OBJECT_ACL",
                                    Ref("EqualsSegment"),
                                    Ref("QuotedLiteralSegment"),
                                ),
                            ),
                            AnySetOf(
                                Sequence(
                                    "AZURE_TENANT_ID",
                                    Ref("EqualsSegment"),
                                    Ref("QuotedLiteralSegment"),
                                ),
                            ),
                        ),
                        Sequence(
                            "STORAGE_ALLOWED_LOCATIONS",
                            Ref("EqualsSegment"),
                            OneOf(
                                Bracketed(
                                    Delimited(
                                        OneOf(
                                            Ref("S3Path"),
                                            Ref("GCSPath"),
                                            Ref("AzureBlobStoragePath"),
                                        )
                                    )
                                ),
                                Bracketed(
                                    Ref("QuotedStarSegment"),
                                ),
                            ),
                        ),
                        Sequence(
                            "STORAGE_BLOCKED_LOCATIONS",
                            Ref("EqualsSegment"),
                            Bracketed(
                                Delimited(
                                    OneOf(
                                        Ref("S3Path"),
                                        Ref("GCSPath"),
                                        Ref("AzureBlobStoragePath"),
                                    )
                                )
                            ),
                        ),
                    ),
                ),
            ),
            Sequence(
                "UNSET",
                OneOf(
                    Sequence(
                        "TAG", Delimited(Ref("TagReferenceSegment")), optional=True
                    ),
                    "COMMENT",
                    "ENABLED",
                    "STORAGE_BLOCKED_LOCATIONS",
                ),
            ),
        ),
    )


class AlterExternalTableStatementSegment(BaseSegment):
    """An `ALTER EXTERNAL TABLE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-external-table.html
    """

    type = "alter_external_table_statement"

    match_grammar = Sequence(
        "ALTER",
        "EXTERNAL",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence("REFRESH", Ref("QuotedLiteralSegment", optional=True)),
            Sequence(
                OneOf("ADD", "REMOVE"),
                "FILES",
                Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
            ),
            Sequence(
                "SET",
                Sequence(
                    "AUTO_REFRESH",
                    Ref("EqualsSegment"),
                    Ref("BooleanLiteralGrammar"),
                    optional=True,
                ),
                Ref("TagEqualsSegment", optional=True),
            ),
            Sequence("UNSET", Ref("TagEqualsSegment")),
            Sequence("DROP", "PARTITION", "LOCATION", Ref("QuotedLiteralSegment")),
            Sequence(
                "ADD",
                "PARTITION",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            Ref("EqualsSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                    ),
                ),
                "LOCATION",
                Ref("QuotedLiteralSegment"),
            ),
        ),
    )


class CommentEqualsClauseSegment(BaseSegment):
    """A comment clause.

    e.g. COMMENT = 'view/table description'
    """

    type = "comment_equals_clause"
    match_grammar = Sequence(
        "COMMENT", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")
    )


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
                    Ref("TagReferenceSegment"),
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                )
            ),
        ),
    )


class TagEqualsSegment(BaseSegment):
    """A tag clause.

    e.g. TAG tag1 = 'value1', tag2 = 'value2'
    """

    type = "tag_equals"
    match_grammar = Sequence(
        "TAG",
        Delimited(
            Sequence(
                Ref("TagReferenceSegment"),
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            )
        ),
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """A snowflake unordered `SELECT` statement including optional Qualify.

    https://docs.snowflake.com/en/sql-reference/constructs/qualify.html
    """

    type = "select_statement"

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OverlapsClauseSegment", optional=True),
    )


class AccessStatementSegment(BaseSegment):
    """A `GRANT` or `REVOKE` statement.

    Grant specific information:
     * https://docs.snowflake.com/en/sql-reference/sql/grant-privilege.html

    Revoke specific information:
     * https://docs.snowflake.com/en/sql-reference/sql/revoke-role.html
     * https://docs.snowflake.com/en/sql-reference/sql/revoke-privilege.html
     * https://docs.snowflake.com/en/sql-reference/sql/revoke-privilege-share.html
    """

    type = "access_statement"

    # Privileges that can be set on the account (specific to snowflake)
    _global_permissions = OneOf(
        Sequence(
            "CREATE",
            OneOf(
                "ACCOUNT",
                "ROLE",
                "USER",
                "WAREHOUSE",
                "DATABASE",
                "INTEGRATION",
                "SHARE",
                Sequence("DATA", "EXCHANGE", "LISTING"),
                Sequence("NETWORK", "POLICY"),
            ),
        ),
        Sequence("APPLY", "MASKING", "POLICY"),
        Sequence("APPLY", "ROW", "ACCESS", "POLICY"),
        Sequence("APPLY", "SESSION", "POLICY"),
        Sequence("APPLY", "TAG"),
        Sequence("ATTACH", "POLICY"),
        Sequence("EXECUTE", "TASK"),
        Sequence("IMPORT", "SHARE"),
        Sequence(
            "MANAGE",
            OneOf(
                "GRANTS",
                Sequence(OneOf("ACCOUNT", "ORGANIZATION", "USER"), "SUPPORT", "CASES"),
            ),
        ),
        Sequence("MONITOR", OneOf("EXECUTION", "USAGE")),
        Sequence("OVERRIDE", "SHARE", "RESTRICTIONS"),
    )

    _schema_object_names = [
        "TABLE",
        "VIEW",
        "STAGE",
        "FUNCTION",
        "PROCEDURE",
        "ROUTINE",
        "SEQUENCE",
        "STREAM",
        "TASK",
        "PIPE",
    ]

    _schema_object_types = OneOf(
        *_schema_object_names,
        Sequence("MATERIALIZED", "VIEW"),
        Sequence("EXTERNAL", "TABLE"),
        Sequence(OneOf("TEMP", "TEMPORARY"), "TABLE"),
        Sequence("FILE", "FORMAT"),
        Sequence("SESSION", "POLICY"),
        Sequence("MASKING", "POLICY"),
        Sequence("ROW", "ACCESS", "POLICY"),
    )

    # We reuse the object names above and simply append an `S` to the end of them to get
    # plurals
    _schema_object_types_plural = OneOf(
        *[f"{object_name}S" for object_name in _schema_object_names]
    )

    _permissions = Sequence(
        OneOf(
            Sequence(
                "CREATE",
                OneOf(
                    "SCHEMA",
                    # Sequence("MASKING", "POLICY"),
                    _schema_object_types,
                ),
            ),
            Sequence("IMPORTED", "PRIVILEGES"),
            "APPLY",
            "CONNECT",
            "CREATE",
            "DELETE",
            "EXECUTE",
            "INSERT",
            "MODIFY",
            "MONITOR",
            "OPERATE",
            "OWNERSHIP",
            "READ",
            "REFERENCE_USAGE",
            "REFERENCES",
            "SELECT",
            "TEMP",
            "TEMPORARY",
            "TRIGGER",
            "TRUNCATE",
            "UPDATE",
            "USAGE",
            "USE_ANY_ROLE",
            "WRITE",
            Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
        ),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
    )

    # All of the object types that we can grant permissions on.
    _objects = OneOf(
        "ACCOUNT",
        Sequence(
            OneOf(
                Sequence("RESOURCE", "MONITOR"),
                "WAREHOUSE",
                "DATABASE",
                "DOMAIN",
                "INTEGRATION",
                "SCHEMA",
                "ROLE",
                Sequence("ALL", "SCHEMAS", "IN", "DATABASE"),
                Sequence("FUTURE", "SCHEMAS", "IN", "DATABASE"),
                _schema_object_types,
                Sequence(
                    "ALL",
                    OneOf(
                        _schema_object_types_plural,
                        Sequence("MATERIALIZED", "VIEWS"),
                        Sequence("EXTERNAL", "TABLES"),
                        Sequence("FILE", "FORMATS"),
                    ),
                    "IN",
                    OneOf("SCHEMA", "DATABASE"),
                ),
                Sequence(
                    "FUTURE",
                    OneOf(
                        _schema_object_types_plural,
                        Sequence("MATERIALIZED", "VIEWS"),
                        Sequence("EXTERNAL", "TABLES"),
                        Sequence("FILE", "FORMATS"),
                    ),
                    "IN",
                    OneOf("DATABASE", "SCHEMA"),
                ),
                Sequence("DATABASE", "ROLE"),
                optional=True,
            ),
            Delimited(
                Ref("ObjectReferenceSegment"),
                Sequence(
                    Ref("FunctionNameSegment"),
                    Ref("FunctionParameterListGrammar", optional=True),
                ),
                terminators=["TO", "FROM"],
            ),
        ),
    )

    match_grammar: Matchable = OneOf(
        # https://docs.snowflake.com/en/sql-reference/sql/grant-privilege.html
        Sequence(
            "GRANT",
            OneOf(
                Sequence(
                    Delimited(
                        OneOf(_global_permissions, _permissions),
                        terminators=["ON"],
                    ),
                    "ON",
                    _objects,
                ),
                Sequence("ROLE", Ref("ObjectReferenceSegment")),
                Sequence("DATABASE", "ROLE", Ref("DatabaseRoleReferenceSegment")),
                Sequence("OWNERSHIP", "ON", "USER", Ref("ObjectReferenceSegment")),
                Sequence(
                    "ADD",
                    "SEARCH",
                    "OPTIMIZATION",
                    "ON",
                    "SCHEMA",
                    Ref("SchemaReferenceSegment"),
                ),
                # In the case where a role is granted non-explicitly,
                # e.g. GRANT ROLE_NAME TO OTHER_ROLE_NAME
                # See https://docs.snowflake.com/en/sql-reference/sql/grant-role.html
                Ref("ObjectReferenceSegment"),
            ),
            "TO",
            OneOf("USER", "ROLE", "SHARE", Sequence("DATABASE", "ROLE"), optional=True),
            Delimited(
                OneOf(
                    Ref("RoleReferenceSegment"),
                    Ref("FunctionSegment"),
                    Ref("DatabaseRoleReferenceSegment"),
                    "PUBLIC",
                ),
            ),
            OneOf(
                Sequence("WITH", "GRANT", "OPTION"),
                Sequence("WITH", "ADMIN", "OPTION"),
                Sequence(OneOf("REVOKE", "COPY"), "CURRENT", "GRANTS"),
                optional=True,
            ),
            Sequence(
                "GRANTED",
                "BY",
                OneOf(
                    "CURRENT_USER",
                    "SESSION_USER",
                    Ref("ObjectReferenceSegment"),
                ),
                optional=True,
            ),
        ),
        # https://docs.snowflake.com/en/sql-reference/sql/revoke-privilege.html
        Sequence(
            "REVOKE",
            Sequence("GRANT", "OPTION", "FOR", optional=True),
            OneOf(
                Sequence(
                    Delimited(
                        OneOf(_global_permissions, _permissions),
                        terminators=["ON"],
                    ),
                    "ON",
                    _objects,
                ),
                Sequence("ROLE", Ref("ObjectReferenceSegment")),
                Sequence("DATABASE", "ROLE", Ref("DatabaseRoleReferenceSegment")),
                Sequence("OWNERSHIP", "ON", "USER", Ref("ObjectReferenceSegment")),
            ),
            "FROM",
            OneOf("USER", "ROLE", "SHARE", Sequence("DATABASE", "ROLE"), optional=True),
            Delimited(
                Ref("ObjectReferenceSegment"),
            ),
            Ref("DropBehaviorGrammar", optional=True),
        ),
    )


class CreateCloneStatementSegment(BaseSegment):
    """A snowflake `CREATE ... CLONE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-clone.html
    """

    type = "create_clone_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
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
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "CLONE",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Ref("FromAtExpressionSegment"),
            Ref("FromBeforeExpressionSegment"),
            optional=True,
        ),
    )


class CreateDatabaseFromShareStatementSegment(BaseSegment):
    """A snowflake `CREATE ... DATABASE FROM SHARE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-database.html
    """

    type = "create_database_from_share_statement"
    match_grammar = Sequence(
        "CREATE",
        "DATABASE",
        Ref("ObjectReferenceSegment"),
        Sequence("FROM", "SHARE"),
        Ref("ObjectReferenceSegment"),
    )


class CreateProcedureStatementSegment(BaseSegment):
    """A snowflake `CREATE ... PROCEDURE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-procedure.html
    """

    type = "create_procedure_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("SECURE", optional=True),
        "PROCEDURE",
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence("COPY", "GRANTS", optional=True),
        "RETURNS",
        OneOf(
            Ref("DatatypeSegment"),
            Sequence(
                "TABLE",
                Bracketed(Delimited(Ref("ColumnDefinitionSegment"), optional=True)),
            ),
        ),
        AnySetOf(
            Sequence("NOT", "NULL", optional=True),
            Sequence(
                "LANGUAGE",
                OneOf(
                    "JAVA",
                    "JAVASCRIPT",
                    "PYTHON",
                    "SCALA",
                    "SQL",
                ),
                optional=True,
            ),
            OneOf(
                Sequence("CALLED", "ON", "NULL", "INPUT"),
                Sequence("RETURNS", "NULL", "ON", "NULL", "INPUT"),
                "STRICT",
                optional=True,
            ),
            OneOf("VOLATILE", "IMMUTABLE", optional=True),
            Sequence(
                "RUNTIME_VERSION",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Ref("CommentEqualsClauseSegment", optional=True),
            Sequence(
                "IMPORTS",
                Ref("EqualsSegment"),
                Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
                optional=True,
            ),
            Sequence(
                "PACKAGES",
                Ref("EqualsSegment"),
                Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
                optional=True,
            ),
            Sequence(
                "HANDLER",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "TARGET_PATH",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Sequence("EXECUTE", "AS", OneOf("CALLER", "OWNER"), optional=True),
            optional=True,
        ),
        "AS",
        OneOf(
            # Either a foreign programming language UDF...
            Ref("DoubleQuotedUDFBody"),
            Ref("SingleQuotedUDFBody"),
            Ref("DollarQuotedUDFBody"),
            # ...or a SQL UDF
            Ref("ScriptingBlockStatementSegment"),
        ),
    )


class AlterProcedureStatementSegment(BaseSegment):
    """A snowflake `ALTER ... PROCEDURE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-procedure.html
    """

    type = "alter_procedure_statement"
    match_grammar = Sequence(
        "ALTER",
        "PROCEDURE",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        OneOf(
            Sequence("RENAME", "TO", Ref("FunctionNameSegment")),
            Sequence("EXECUTE", "AS", OneOf("CALLER", "OWNER")),
            Sequence(
                "SET", OneOf(Ref("TagEqualsSegment"), Ref("CommentEqualsClauseSegment"))
            ),
            Sequence(
                "UNSET",
                OneOf(
                    Sequence("TAG", Delimited(Ref("TagReferenceSegment"))), "COMMENT"
                ),
            ),
        ),
    )


class AlterNetworkPolicyStatementSegment(BaseSegment):
    """An ALTER NETWORK POLICY statement.

    As per https://docs.snowflake.com/en/sql-reference/sql/alter-network-policy
    """

    type = "alter_network_policy_statement"

    match_grammar = Sequence(
        "ALTER",
        "NETWORK",
        "POLICY",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
        OneOf(
            Sequence(
                "SET",
                AnySetOf(
                    Sequence(
                        "ALLOWED_NETWORK_RULE_LIST",
                        Ref("EqualsSegment"),
                        Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
                    ),
                    Sequence(
                        "BLOCKED_NETWORK_RULE_LIST",
                        Ref("EqualsSegment"),
                        Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
                    ),
                    Sequence(
                        "ALLOWED_IP_LIST",
                        Ref("EqualsSegment"),
                        Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
                    ),
                    Sequence(
                        "BLOCKED_IP_LIST",
                        Ref("EqualsSegment"),
                        Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
                    ),
                    Sequence(
                        "COMMENT",
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            Sequence(
                "UNSET",
                "COMMENT",
            ),
            Sequence(
                OneOf(
                    "ADD",
                    "REMOVE",
                ),
                OneOf(
                    "ALLOWED_NETWORK_RULE_LIST",
                    "BLOCKED_NETWORK_RULE_LIST",
                ),
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence("RENAME", "TO", Ref("SingleIdentifierGrammar")),
            Sequence("SET", Ref("TagEqualsSegment")),
            Sequence(
                "UNSET",
                "TAG",
                Ref("TagReferenceSegment"),
                AnyNumberOf(
                    Ref("CommaSegment"), Ref("TagReferenceSegment"), optional=True
                ),
            ),
        ),
    )


class ReturnStatementSegment(BaseSegment):
    """A snowflake `RETURN` statement for SQL scripting.

    https://docs.snowflake.com/en/sql-reference/snowflake-scripting/return
    """

    type = "return_statement"
    match_grammar = Sequence(
        "RETURN",
        Ref("ExpressionSegment"),
    )


class ScriptingBlockStatementSegment(BaseSegment):
    """A snowflake `BEGIN ... END` statement for SQL scripting.

    https://docs.snowflake.com/en/sql-reference/snowflake-scripting/begin
    """

    type = "scripting_block_statement"
    match_grammar = OneOf(
        Sequence(
            "BEGIN",
            Delimited(
                Ref("StatementSegment"),
            ),
        ),
        Sequence("END"),
    )


class ScriptingLetStatementSegment(BaseSegment):
    """A snowflake `LET` statement for SQL scripting.

    https://docs.snowflake.com/en/sql-reference/snowflake-scripting/let
    https://docs.snowflake.com/en/developer-guide/snowflake-scripting/variables
    """

    type = "scripting_let_statement"
    match_grammar = OneOf(
        # Initial declaration and assignment
        Sequence(
            "LET",
            Ref("LocalVariableNameSegment"),
            OneOf(
                # Variable assigment
                OneOf(
                    Sequence(
                        Ref("DatatypeSegment"),
                        OneOf("DEFAULT", Ref("WalrusOperatorSegment")),
                        Ref("ExpressionSegment"),
                    ),
                    Sequence(
                        OneOf("DEFAULT", Ref("WalrusOperatorSegment")),
                        Ref("ExpressionSegment"),
                    ),
                ),
                # Cursor assignment
                Sequence(
                    "CURSOR",
                    "FOR",
                    OneOf(Ref("LocalVariableNameSegment"), Ref("SelectableGrammar")),
                ),
                # Resultset assignment
                Sequence(
                    "RESULTSET",
                    Ref("WalrusOperatorSegment"),
                    Bracketed(Ref("SelectableGrammar")),
                ),
            ),
        ),
        # Subsequent assignment, see
        # https://docs.snowflake.com/en/developer-guide/snowflake-scripting/variables
        Sequence(
            Ref("LocalVariableNameSegment"),
            Ref("WalrusOperatorSegment"),
            OneOf(
                # Variable reassigment
                Ref("ExpressionSegment"),
                # Cursors cannot be reassigned
                # no code
                # Resultset reassigment
                Bracketed(Ref("SelectableGrammar")),
            ),
        ),
    )


class CreateFunctionStatementSegment(BaseSegment):
    """A snowflake `CREATE ... FUNCTION` statement for SQL and JavaScript functions.

    https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    """

    type = "create_function_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("SECURE", optional=True),
        "FUNCTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        "RETURNS",
        OneOf(
            Ref("DatatypeSegment"),
            Sequence("TABLE", Bracketed(Delimited(Ref("ColumnDefinitionSegment")))),
        ),
        AnySetOf(
            Sequence("NOT", "NULL", optional=True),
            Sequence(
                "LANGUAGE",
                OneOf("JAVASCRIPT", "SQL", "PYTHON", "JAVA", "SCALA"),
                optional=True,
            ),
            OneOf(
                Sequence("CALLED", "ON", "NULL", "INPUT"),
                Sequence("RETURNS", "NULL", "ON", "NULL", "INPUT"),
                "STRICT",
                optional=True,
            ),
            OneOf("VOLATILE", "IMMUTABLE", optional=True),
            Sequence(
                "RUNTIME_VERSION",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Ref("CommentEqualsClauseSegment", optional=True),
            Sequence(
                "IMPORTS",
                Ref("EqualsSegment"),
                Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
                optional=True,
            ),
            Sequence(
                "PACKAGES",
                Ref("EqualsSegment"),
                Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
                optional=True,
            ),
            Sequence(
                "HANDLER",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "TARGET_PATH",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            optional=True,
        ),
        Sequence(
            "AS",
            OneOf(
                # Either a foreign programming language UDF...
                Ref("DoubleQuotedUDFBody"),
                Ref("SingleQuotedUDFBody"),
                Ref("DollarQuotedUDFBody"),
                # ...or a SQL UDF
                Ref("ScriptingBlockStatementSegment"),
            ),
            optional=True,
        ),
    )


class AlterFunctionStatementSegment(BaseSegment):
    """A snowflake `ALTER ... FUNCTION` and `ALTER ... EXTERNAL FUNCTION` statements.

    NOTE: `ALTER ... EXTERNAL FUNCTION` statements always use the `ALTER ... FUNCTION`
    syntax.

    https://docs.snowflake.com/en/sql-reference/sql/alter-function.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-external-function.html
    """

    type = "alter_function_statement"
    match_grammar = Sequence(
        "ALTER",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        OneOf(
            Sequence("RENAME", "TO", Ref("FunctionNameSegment")),
            Sequence(
                "SET",
                OneOf(
                    Ref("CommentEqualsClauseSegment"),
                    Sequence(
                        "API_INTEGRATION",
                        Ref("EqualsSegment"),
                        Ref("SingleIdentifierGrammar"),
                    ),
                    Sequence(
                        "HEADERS",
                        Ref("EqualsSegment"),
                        Bracketed(
                            Delimited(
                                Sequence(
                                    Ref("SingleQuotedIdentifierSegment"),
                                    Ref("EqualsSegment"),
                                    Ref("SingleQuotedIdentifierSegment"),
                                ),
                            ),
                        ),
                    ),
                    Sequence(
                        "CONTEXT_HEADERS",
                        Ref("EqualsSegment"),
                        Bracketed(
                            Delimited(
                                Ref("ContextHeadersGrammar"),
                            ),
                        ),
                    ),
                    Sequence(
                        "MAX_BATCH_ROWS",
                        Ref("EqualsSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                    Sequence(
                        "COMPRESSION",
                        Ref("EqualsSegment"),
                        Ref("CompressionType"),
                    ),
                    "SECURE",
                    Sequence(
                        OneOf("REQUEST_TRANSLATOR", "RESPONSE_TRANSLATOR"),
                        Ref("EqualsSegment"),
                        Ref("FunctionNameSegment"),
                    ),
                ),
            ),
            Sequence(
                "UNSET",
                OneOf(
                    "COMMENT",
                    "HEADERS",
                    "CONTEXT_HEADERS",
                    "MAX_BATCH_ROWS",
                    "COMPRESSION",
                    "SECURE",
                    "REQUEST_TRANSLATOR",
                    "RESPONSE_TRANSLATOR",
                ),
            ),
            Sequence(
                "RENAME",
                "TO",
                Ref("SingleIdentifierGrammar"),
            ),
        ),
    )


class CreateExternalFunctionStatementSegment(BaseSegment):
    """A snowflake `CREATE ... EXTERNAL FUNCTION` statement for API integrations.

    https://docs.snowflake.com/en/sql-reference/sql/create-external-function.html
    """

    type = "create_external_function_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("SECURE", optional=True),
        "EXTERNAL",
        "FUNCTION",
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        "RETURNS",
        Ref("DatatypeSegment"),
        Sequence(Ref.keyword("NOT", optional=True), "NULL", optional=True),
        OneOf(
            Sequence("CALLED", "ON", "NULL", "INPUT"),
            Sequence("RETURNS", "NULL", "ON", "NULL", "INPUT"),
            "STRICT",
            optional=True,
        ),
        OneOf("VOLATILE", "IMMUTABLE", optional=True),
        Ref("CommentEqualsClauseSegment", optional=True),
        "API_INTEGRATION",
        Ref("EqualsSegment"),
        Ref("SingleIdentifierGrammar"),
        Sequence(
            "HEADERS",
            Ref("EqualsSegment"),
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("SingleQuotedIdentifierSegment"),
                        Ref("EqualsSegment"),
                        Ref("SingleQuotedIdentifierSegment"),
                    ),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "CONTEXT_HEADERS",
            Ref("EqualsSegment"),
            Bracketed(
                Delimited(
                    Ref("ContextHeadersGrammar"),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "MAX_BATCH_ROWS",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
            optional=True,
        ),
        Sequence(
            "COMPRESSION",
            Ref("EqualsSegment"),
            Ref("CompressionType"),
            optional=True,
        ),
        Sequence(
            "REQUEST_TRANSLATOR",
            Ref("EqualsSegment"),
            Ref("FunctionNameSegment"),
            optional=True,
        ),
        Sequence(
            "RESPONSE_TRANSLATOR",
            Ref("EqualsSegment"),
            Ref("FunctionNameSegment"),
            optional=True,
        ),
        "AS",
        Ref("SingleQuotedIdentifierSegment"),
    )


class WarehouseObjectPropertiesSegment(BaseSegment):
    """A snowflake Warehouse Object Properties segment.

    https://docs.snowflake.com/en/sql-reference/sql/create-warehouse.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse.html

    Note: comments are handled separately so not incorrectly marked as
    warehouse object.
    """

    type = "warehouse_object_properties"

    match_grammar = AnySetOf(
        Sequence(
            "WAREHOUSE_TYPE",
            Ref("EqualsSegment"),
            Ref("WarehouseType"),
        ),
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
            Ref("ScalingPolicy"),
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


class WarehouseObjectParamsSegment(BaseSegment):
    """A snowflake Warehouse Object Param segment.

    https://docs.snowflake.com/en/sql-reference/sql/create-warehouse.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse.html
    """

    type = "warehouse_object_properties"

    match_grammar = AnySetOf(
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


class ConstraintPropertiesSegment(BaseSegment):
    """CONSTRAINT clause for CREATE TABLE or ALTER TABLE command.

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
        AnySetOf(
            OneOf(Sequence("NOT", optional=True), "ENFORCED"),
            OneOf(Sequence("NOT", optional=True), "DEFERRABLE"),
            OneOf("INITIALLY", OneOf("DEFERRED", "IMMEDIATE")),
        ),
    )


class ColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """A column option; each CREATE TABLE column can have 0 or more.

    https://docs.snowflake.com/en/sql-reference/sql/create-table.html
    """

    match_grammar = AnySetOf(
        Sequence("COLLATE", Ref("CollationReferenceSegment")),
        Sequence(
            "DEFAULT",
            Ref("ExpressionSegment"),
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
            Ref("OrderNoOrderGrammar", optional=True),
        ),
        Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
        Sequence(
            Sequence("WITH", optional=True),
            "MASKING",
            "POLICY",
            Ref("FunctionNameSegment"),
            Sequence(
                "USING",
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("ColumnReferenceSegment"),
                            Ref("ExpressionSegment"),
                        )
                    ),
                ),
                optional=True,
            ),
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


class CopyOptionsSegment(BaseSegment):
    """A Snowflake CopyOptions statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-table.html
    https://docs.snowflake.com/en/sql-reference/sql/copy-into-location.html
    https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html
    """

    type = "copy_options"

    match_grammar = OneOf(
        AnySetOf(
            Sequence("ON_ERROR", Ref("EqualsSegment"), Ref("CopyOptionOnErrorSegment")),
            Sequence("SIZE_LIMIT", Ref("EqualsSegment"), Ref("NumericLiteralSegment")),
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
        ),
        AnySetOf(
            Sequence("OVERWRITE", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")),
            Sequence("SINGLE", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")),
            Sequence(
                "MAX_FILE_SIZE", Ref("EqualsSegment"), Ref("NumericLiteralSegment")
            ),
            Sequence(
                "INCLUDE_QUERY_ID", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")
            ),
            Sequence(
                "DETAILED_OUTPUT", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")
            ),
        ),
    )


class CreateSchemaStatementSegment(ansi.CreateSchemaStatementSegment):
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


class AlterRoleStatementSegment(BaseSegment):
    """An `ALTER ROLE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-role.html
    """

    type = "alter_role_statement"
    match_grammar = Sequence(
        "ALTER",
        "ROLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("RoleReferenceSegment"),
        OneOf(
            Sequence(
                "SET",
                OneOf(
                    Ref("RoleReferenceSegment"),
                    Ref("TagEqualsSegment"),
                    Sequence(
                        "COMMENT", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")
                    ),
                ),
            ),
            Sequence(
                "UNSET",
                OneOf(
                    Ref("RoleReferenceSegment"),
                    Sequence("TAG", Delimited(Ref("TagReferenceSegment"))),
                    Sequence("COMMENT"),
                ),
            ),
            Sequence(
                "RENAME",
                "TO",
                OneOf(
                    Ref("RoleReferenceSegment"),
                ),
            ),
        ),
    )


class CreateSequenceStatementSegment(BaseSegment):
    """A `CREATE SEQUENCE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-sequence
    """

    type = "create_sequence_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "SEQUENCE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SequenceReferenceSegment"),
        Sequence("WITH", optional=True),
        Sequence(
            "START",
            Sequence("WITH", optional=True),
            Ref("EqualsSegment", optional=True),
            Ref("IntegerSegment"),
            optional=True,
        ),
        Sequence(
            "INCREMENT",
            Sequence("BY", optional=True),
            Ref("EqualsSegment", optional=True),
            Ref("IntegerSegment"),
            optional=True,
        ),
        Ref("OrderNoOrderGrammar", optional=True),
        Ref("CommentEqualsClauseSegment", optional=True),
    )


class AlterSequenceStatementSegment(BaseSegment):
    """An `ALTER SEQUENCE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-sequence
    """

    type = "alter_sequence_statement"
    match_grammar = Sequence(
        "ALTER",
        "SEQUENCE",
        Ref("IfExistsGrammar", optional=True),
        Ref("SequenceReferenceSegment"),
        Sequence(
            Sequence("SET", optional=True),
            AnySetOf(
                Sequence(
                    "INCREMENT",
                    Sequence("BY", optional=True),
                    Ref("EqualsSegment", optional=True),
                    Ref("IntegerSegment"),
                    optional=True,
                ),
                Ref("OrderNoOrderGrammar", optional=True),
                Ref("CommentEqualsClauseSegment"),
            ),
            optional=True,
        ),
        Sequence("UNSET", "COMMENT", optional=True),
        Sequence("RENAME", "TO", Ref("SequenceReferenceSegment"), optional=True),
    )


class AlterSchemaStatementSegment(BaseSegment):
    """An `ALTER SCHEMA` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-schema.html

    """

    type = "alter_schema_statement"
    match_grammar = Sequence(
        "ALTER",
        "SCHEMA",
        Ref("IfExistsGrammar", optional=True),
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
                    Sequence("TAG", Delimited(Ref("TagReferenceSegment"))),
                ),
            ),
            Sequence(OneOf("ENABLE", "DISABLE"), Sequence("MANAGED", "ACCESS")),
        ),
    )


class SchemaObjectParamsSegment(BaseSegment):
    """A Snowflake Schema Object Param segment.

    https://docs.snowflake.com/en/sql-reference/sql/create-schema.html
    https://docs.snowflake.com/en/sql-reference/sql/alter-schema.html
    """

    type = "schema_object_properties"

    match_grammar = AnySetOf(
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


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    A lot more options than ANSI
    https://docs.snowflake.com/en/sql-reference/sql/create-table.html
    """

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryTransientGrammar", optional=True),
        Ref.keyword("DYNAMIC", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Sequence(
            "TARGET_LAG",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
        Sequence(
            "WAREHOUSE",
            Ref("EqualsSegment"),
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        # Columns and comment syntax:
        AnySetOf(
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
                OneOf(
                    Ref("FunctionSegment"),
                    Bracketed(Delimited(Ref("ExpressionSegment"))),
                ),
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
                Bracketed(Ref("CopyOptionsSegment")),
                optional=True,
            ),
            Sequence(
                "DATA_RETENTION_TIME_IN_DAYS",
                Ref("EqualsSegment"),
                Ref("NumericLiteralSegment"),
                optional=True,
            ),
            Sequence(
                "MAX_DATA_EXTENSION_TIME_IN_DAYS",
                Ref("EqualsSegment"),
                Ref("NumericLiteralSegment"),
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
                Ref("ObjectReferenceSegment"),
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
        ),
    )


class CreateTaskSegment(BaseSegment):
    """A snowflake `CREATE TASK` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-task.html
    """

    type = "create_task_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "TASK",
        Ref("IfNotExistsGrammar", optional=True),
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
            Sequence(
                "USER_TASK_TIMEOUT_MS",
                Ref("EqualsSegment"),
                Ref("NumericLiteralSegment"),
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
                "COPY",
                "GRANTS",
            ),
            Ref("CommentEqualsClauseSegment"),
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
            Ref("TaskExpressionSegment"),
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


class TaskExpressionSegment(BaseSegment):
    """Expressions for WHEN clause in TASK.

    e.g. "SYSTEM$STREAM_HAS_DATA('MYSTREAM')"

    """

    type = "snowflake_task_expression_segment"
    match_grammar = Sequence(
        Delimited(
            OneOf(
                Ref("ExpressionSegment"),
                Sequence(
                    Ref("SystemFunctionName"),
                    Bracketed(Ref("QuotedLiteralSegment")),
                ),
            ),
            delimiter=OneOf(Ref("BooleanBinaryOperatorGrammar")),
        )
    )


class CreateStatementSegment(BaseSegment):
    """A snowflake `CREATE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create.html
    """

    type = "create_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        OneOf(
            Sequence("NETWORK", "POLICY"),
            Sequence("RESOURCE", "MONITOR"),
            "SHARE",
            "ROLE",
            "USER",
            "TAG",
            "WAREHOUSE",
            Sequence("NOTIFICATION", "INTEGRATION"),
            Sequence("SECURITY", "INTEGRATION"),
            Sequence("STORAGE", "INTEGRATION"),
            Sequence("MATERIALIZED", "VIEW"),
            Sequence("MASKING", "POLICY"),
            "PIPE",
            Sequence("EXTERNAL", "FUNCTION"),
            # Objects that also support clone
            "DATABASE",
            "SEQUENCE",
        ),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        # Next set are Notification Integration statements
        # https://docs.snowflake.com/en/sql-reference/sql/create-notification-integration.html
        AnySetOf(
            Sequence("TYPE", Ref("EqualsSegment"), "QUEUE"),
            Sequence("ENABLED", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")),
            Sequence(
                "NOTIFICATION_PROVIDER",
                Ref("EqualsSegment"),
                OneOf(
                    "AWS_SNS",
                    "AZURE_EVENT_GRID",
                    "GCP_PUBSUB",
                    "AZURE_STORAGE_QUEUE",
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            # AWS specific params:
            Sequence(
                "AWS_SNS_TOPIC_ARN",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "AWS_SNS_ROLE_ARN",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            # Azure specific params:
            Sequence(
                "AZURE_TENANT_ID", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")
            ),
            OneOf(
                Sequence(
                    "AZURE_STORAGE_QUEUE_PRIMARY_URI",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
                Sequence(
                    "AZURE_EVENT_GRID_TOPIC_ENDPOINT",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            # GCP specific params:
            OneOf(
                Sequence(
                    "GCP_PUBSUB_SUBSCRIPTION_NAME",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
                Sequence(
                    "GCP_PUBSUB_TOPIC_NAME",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                "DIRECTION",
                Ref("EqualsSegment"),
                "OUTBOUND",
                optional=True,
            ),
            Sequence(
                "COMMENT",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            # For tags
            Sequence(
                "ALLOWED_VALUES",
                Delimited(
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            # For network policy
            Sequence(
                "ALLOWED_IP_LIST",
                Ref("EqualsSegment"),
                Bracketed(
                    Delimited(
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            # For network policy
            Sequence(
                "BLOCKED_IP_LIST",
                Ref("EqualsSegment"),
                Bracketed(
                    Delimited(
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
        ),
        # Next set are Storage Integration statements
        # https://docs.snowflake.com/en/sql-reference/sql/create-storage-integration.html
        AnySetOf(
            Sequence("TYPE", Ref("EqualsSegment"), "EXTERNAL_STAGE"),
            Sequence("ENABLED", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")),
            Sequence(
                "STORAGE_PROVIDER",
                Ref("EqualsSegment"),
                OneOf("S3", "AZURE", "GCS", Ref("QuotedLiteralSegment")),
            ),
            # Azure specific params:
            Sequence(
                "AZURE_TENANT_ID", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")
            ),
            # AWS specific params:
            Sequence(
                "STORAGE_AWS_ROLE_ARN",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "STORAGE_AWS_OBJECT_ACL",
                Ref("EqualsSegment"),
                StringParser("'bucket-owner-full-control'", LiteralSegment),
            ),
            Sequence(
                "STORAGE_ALLOWED_LOCATIONS",
                Ref("EqualsSegment"),
                OneOf(
                    Bracketed(
                        Delimited(
                            OneOf(
                                Ref("S3Path"),
                                Ref("GCSPath"),
                                Ref("AzureBlobStoragePath"),
                            )
                        )
                    ),
                    Bracketed(
                        Ref("QuotedStarSegment"),
                    ),
                ),
            ),
            Sequence(
                "STORAGE_BLOCKED_LOCATIONS",
                Ref("EqualsSegment"),
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("S3Path"),
                            Ref("GCSPath"),
                            Ref("AzureBlobStoragePath"),
                        )
                    )
                ),
            ),
            Sequence(
                "COMMENT",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
        ),
        # Next set are Pipe statements
        # https://docs.snowflake.com/en/sql-reference/sql/create-pipe.html
        Sequence(
            Sequence(
                "AUTO_INGEST",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
                optional=True,
            ),
            Sequence(
                "ERROR_INTEGRATION",
                Ref("EqualsSegment"),
                Ref("ObjectReferenceSegment"),
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
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("ObjectReferenceSegment"),
                ),
                optional=True,
            ),
            optional=True,
        ),
        # Next are WAREHOUSE options
        # https://docs.snowflake.com/en/sql-reference/sql/create-warehouse.html
        Sequence(
            Sequence("WITH", optional=True),
            AnyNumberOf(
                Ref("WarehouseObjectPropertiesSegment"),
                Ref("CommentEqualsClauseSegment"),
                Ref("WarehouseObjectParamsSegment"),
            ),
            Ref("TagBracketedEqualsSegment", optional=True),
            optional=True,
        ),
        Ref("CommentEqualsClauseSegment", optional=True),
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
            Ref("CopyIntoTableStatementSegment"),
            optional=True,
        ),
    )


class CreateUserSegment(BaseSegment):
    """A snowflake `CREATE USER` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-user.html
    """

    type = "create_user_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "USER",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Indent,
        AnyNumberOf(
            Sequence(
                "PASSWORD",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "LOGIN_NAME",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                "DISPLAY_NAME",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                "FIRST_NAME",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                "MIDDLE_NAME",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                "LAST_NAME",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                "EMAIL",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "MUST_CHANGE_PASSWORD",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
            Sequence(
                "DISABLED",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
            Sequence(
                "DAYS_TO_EXPIRY",
                Ref("EqualsSegment"),
                Ref("NumericLiteralSegment"),
            ),
            Sequence(
                "MINS_TO_UNLOCK",
                Ref("EqualsSegment"),
                Ref("NumericLiteralSegment"),
            ),
            Sequence(
                "DEFAULT_WAREHOUSE",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                "DEFAULT_NAMESPACE",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                "DEFAULT_ROLE",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            Sequence(
                "DEFAULT_SECONDARY_ROLES",
                Ref("EqualsSegment"),
                Bracketed(Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                "MINS_TO_BYPASS_MFA",
                Ref("EqualsSegment"),
                Ref("NumericLiteralSegment"),
            ),
            Sequence(
                "RSA_PUBLIC_KEY",
                Ref("EqualsSegment"),
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "RSA_PUBLIC_KEY_2",
                Ref("EqualsSegment"),
                Ref("ObjectReferenceSegment"),
            ),
            Ref("CommentEqualsClauseSegment"),
        ),
        Dedent,
    )


class CreateViewStatementSegment(ansi.CreateViewStatementSegment):
    """A `CREATE VIEW` statement, specifically for Snowflake's dialect.

    https://docs.snowflake.com/en/sql-reference/sql/create-view.html
    """

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        AnySetOf(
            "SECURE",
            "RECURSIVE",
        ),
        Ref("TemporaryGrammar", optional=True),
        Sequence("MATERIALIZED", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        AnySetOf(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Sequence(
                            Ref.keyword("WITH", optional=True),
                            "MASKING",
                            "POLICY",
                            Ref("FunctionNameSegment"),
                            Sequence(
                                "USING",
                                Bracketed(
                                    Delimited(
                                        OneOf(
                                            Ref("ColumnReferenceSegment"),
                                            Ref("ExpressionSegment"),
                                        )
                                    ),
                                ),
                                optional=True,
                            ),
                            optional=True,
                        ),
                        Ref("CommentClauseSegment", optional=True),
                    ),
                ),
            ),
            Sequence(
                Ref.keyword("WITH", optional=True),
                "ROW",
                "ACCESS",
                "POLICY",
                Ref("ObjectReferenceSegment"),
                "ON",
                Bracketed(
                    Delimited(Ref("ColumnReferenceSegment")),
                ),
            ),
            Ref("TagBracketedEqualsSegment"),
            Sequence("COPY", "GRANTS"),
            Ref("CommentEqualsClauseSegment"),
            # @TODO: Support column-level masking policy & tagging.
        ),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
    )


class AlterViewStatementSegment(BaseSegment):
    """An `ALTER VIEW` statement, specifically for Snowflake's dialect.

    https://docs.snowflake.com/en/sql-reference/sql/alter-view.html
    """

    type = "alter_view_statement"

    match_grammar = Sequence(
        "ALTER",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "COMMENT",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "UNSET",
                "COMMENT",
            ),
            Sequence(
                OneOf("SET", "UNSET"),
                "SECURE",
            ),
            Sequence("SET", Ref("TagEqualsSegment")),
            Sequence("UNSET", "TAG", Delimited(Ref("TagReferenceSegment"))),
            Delimited(
                Sequence(
                    "ADD",
                    "ROW",
                    "ACCESS",
                    "POLICY",
                    Ref("FunctionNameSegment"),
                    "ON",
                    Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                ),
                Sequence(
                    "DROP",
                    "ROW",
                    "ACCESS",
                    "POLICY",
                    Ref("FunctionNameSegment"),
                ),
            ),
            Sequence(
                OneOf("ALTER", "MODIFY"),
                OneOf(
                    Delimited(
                        Sequence(
                            Ref.keyword("COLUMN", optional=True),
                            Ref("ColumnReferenceSegment"),
                            OneOf(
                                Sequence(
                                    "SET",
                                    "MASKING",
                                    "POLICY",
                                    Ref("FunctionNameSegment"),
                                    Sequence(
                                        "USING",
                                        Bracketed(
                                            Delimited(Ref("ColumnReferenceSegment"))
                                        ),
                                        optional=True,
                                    ),
                                    Ref.keyword("FORCE", optional=True),
                                ),
                                Sequence("UNSET", "MASKING", "POLICY"),
                                Sequence("SET", Ref("TagEqualsSegment")),
                            ),
                        ),
                        Sequence(
                            "COLUMN",
                            Ref("ColumnReferenceSegment"),
                            "UNSET",
                            "TAG",
                            Delimited(Ref("TagReferenceSegment")),
                        ),
                    ),
                ),
            ),
        ),
    )


class AlterMaterializedViewStatementSegment(BaseSegment):
    """An `ALTER MATERIALIZED VIEW` statement, specifically for Snowflake's dialect.

    https://docs.snowflake.com/en/sql-reference/sql/alter-materialized-view.html
    """

    type = "alter_materialized_view_statement"

    match_grammar = Sequence(
        "ALTER",
        "MATERIALIZED",
        "VIEW",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("TableReferenceSegment")),
            Sequence("CLUSTER", "BY", Delimited(Ref("ExpressionSegment"))),
            Sequence("DROP", "CLUSTERING", "KEY"),
            Sequence("SUSPEND", "RECLUSTER"),
            Sequence("RESUME", "RECLUSTER"),
            "SUSPEND",
            "RESUME",
            Sequence(
                OneOf("SET", "UNSET"),
                OneOf(
                    "SECURE",
                    Ref("CommentEqualsClauseSegment"),
                    Ref("TagEqualsSegment"),
                ),
            ),
        ),
    )


class CreateFileFormatSegment(BaseSegment):
    """A snowflake `CREATE FILE FORMAT` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html
    """

    type = "create_file_format_segment"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("FILE", "FORMAT"),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        # TYPE = <FILE_FORMAT> is included in below parameter segments.
        # It is valid syntax to have TYPE = <FILE_FORMAT> after other parameters.
        # Below parameters are either Delimited/AnyNumberOf.
        # Snowflake does allow mixed but this is not supported.
        # @TODO: Update below when an OptionallyDelimited Class is available.
        OneOf(
            Ref("CsvFileFormatTypeParameters"),
            Ref("JsonFileFormatTypeParameters"),
            Ref("AvroFileFormatTypeParameters"),
            Ref("OrcFileFormatTypeParameters"),
            Ref("ParquetFileFormatTypeParameters"),
            Ref("XmlFileFormatTypeParameters"),
        ),
        Sequence(
            # Use a Sequence and include an optional CommaSegment here.
            # This allows a preceding comma when above parameters are delimited.
            Ref("CommaSegment", optional=True),
            Ref("CommentEqualsClauseSegment"),
            optional=True,
        ),
    )


class AlterFileFormatSegment(BaseSegment):
    """A snowflake `Alter FILE FORMAT` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-file-format.html
    """

    type = "alter_file_format_segment"
    match_grammar = Sequence(
        "ALTER",
        Sequence("FILE", "FORMAT"),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("ObjectReferenceSegment")),
            Sequence(
                "SET",
                OneOf(
                    Ref("CsvFileFormatTypeParameters"),
                    Ref("JsonFileFormatTypeParameters"),
                    Ref("AvroFileFormatTypeParameters"),
                    Ref("OrcFileFormatTypeParameters"),
                    Ref("ParquetFileFormatTypeParameters"),
                    Ref("XmlFileFormatTypeParameters"),
                ),
            ),
        ),
        Sequence(
            # Use a Sequence and include an optional CommaSegment here.
            # This allows a preceding comma when above parameters are delimited.
            Ref("CommaSegment", optional=True),
            Ref("CommentEqualsClauseSegment"),
            optional=True,
        ),
    )


class CsvFileFormatTypeParameters(BaseSegment):
    """A Snowflake File Format Type Options segment for CSV.

    https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html
    """

    type = "csv_file_format_type_parameters"

    _file_format_type_parameter = OneOf(
        Sequence(
            "TYPE",
            Ref("EqualsSegment"),
            OneOf(
                StringParser(
                    "'CSV'",
                    CodeSegment,
                    type="file_type",
                ),
                StringParser(
                    "CSV",
                    CodeSegment,
                    type="file_type",
                ),
            ),
        ),
        Sequence(
            "COMPRESSION",
            Ref("EqualsSegment"),
            Ref("CompressionType"),
        ),
        Sequence("FILE_EXTENSION", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")),
        Sequence(
            "SKIP_HEADER",
            Ref("EqualsSegment"),
            Ref("IntegerSegment"),
        ),
        Sequence(
            OneOf(
                "DATE_FORMAT",
                "TIME_FORMAT",
                "TIMESTAMP_FORMAT",
            ),
            Ref("EqualsSegment"),
            OneOf("AUTO", Ref("QuotedLiteralSegment")),
        ),
        Sequence("BINARY_FORMAT", Ref("EqualsSegment"), OneOf("HEX", "BASE64", "UTF8")),
        Sequence(
            OneOf(
                "RECORD_DELIMITER",
                "FIELD_DELIMITER",
                "ESCAPE",
                "ESCAPE_UNENCLOSED_FIELD",
                "FIELD_OPTIONALLY_ENCLOSED_BY",
            ),
            Ref("EqualsSegment"),
            OneOf("NONE", Ref("QuotedLiteralSegment")),
        ),
        Sequence(
            "NULL_IF",
            Ref("EqualsSegment"),
            Bracketed(Delimited(Ref("QuotedLiteralSegment"), optional=True)),
        ),
        Sequence(
            OneOf(
                "SKIP_BLANK_LINES",
                "ERROR_ON_COLUMN_COUNT_MISMATCH",
                "REPLACE_INVALID_CHARACTERS",
                "VALIDATE_UTF8",
                "EMPTY_FIELD_AS_NULL",
                "SKIP_BYTE_ORDER_MARK",
                "TRIM_SPACE",
            ),
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
        ),
        Sequence(
            "ENCODING",
            Ref("EqualsSegment"),
            OneOf(
                "UTF8",
                Ref("QuotedLiteralSegment"),
            ),
        ),
    )

    match_grammar = OneOf(
        Delimited(_file_format_type_parameter), AnyNumberOf(_file_format_type_parameter)
    )


class JsonFileFormatTypeParameters(BaseSegment):
    """A Snowflake File Format Type Options segment for JSON.

    https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html
    """

    type = "json_file_format_type_parameters"

    _file_format_type_parameter = OneOf(
        Sequence(
            "TYPE",
            Ref("EqualsSegment"),
            OneOf(
                StringParser(
                    "'JSON'",
                    CodeSegment,
                    type="file_type",
                ),
                StringParser(
                    "JSON",
                    CodeSegment,
                    type="file_type",
                ),
            ),
        ),
        Sequence(
            "COMPRESSION",
            Ref("EqualsSegment"),
            Ref("CompressionType"),
        ),
        Sequence(
            OneOf(
                "DATE_FORMAT",
                "TIME_FORMAT",
                "TIMESTAMP_FORMAT",
            ),
            Ref("EqualsSegment"),
            OneOf(Ref("QuotedLiteralSegment"), "AUTO"),
        ),
        Sequence("BINARY_FORMAT", Ref("EqualsSegment"), OneOf("HEX", "BASE64", "UTF8")),
        Sequence(
            "NULL_IF",
            Ref("EqualsSegment"),
            Bracketed(Delimited(Ref("QuotedLiteralSegment"), optional=True)),
        ),
        Sequence("FILE_EXTENSION", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")),
        Sequence(
            OneOf(
                "TRIM_SPACE",
                "ENABLE_OCTAL",
                "ALLOW_DUPLICATE",
                "STRIP_OUTER_ARRAY",
                "STRIP_NULL_VALUES",
                "REPLACE_INVALID_CHARACTERS",
                "IGNORE_UTF8_ERRORS",
                "SKIP_BYTE_ORDER_MARK",
            ),
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
        ),
    )

    match_grammar = OneOf(
        Delimited(_file_format_type_parameter), AnyNumberOf(_file_format_type_parameter)
    )


class AvroFileFormatTypeParameters(BaseSegment):
    """A Snowflake File Format Type Options segment for AVRO.

    https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html
    """

    type = "avro_file_format_type_parameters"

    _file_format_type_parameter = OneOf(
        Sequence(
            "TYPE",
            Ref("EqualsSegment"),
            OneOf(
                StringParser(
                    "'AVRO'",
                    CodeSegment,
                    type="file_type",
                ),
                StringParser(
                    "AVRO",
                    CodeSegment,
                    type="file_type",
                ),
            ),
        ),
        Sequence("COMPRESSION", Ref("EqualsSegment"), Ref("CompressionType")),
        Sequence("TRIM_SPACE", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")),
        Sequence(
            "NULL_IF",
            Ref("EqualsSegment"),
            Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
        ),
    )

    match_grammar = OneOf(
        Delimited(_file_format_type_parameter), AnyNumberOf(_file_format_type_parameter)
    )


class OrcFileFormatTypeParameters(BaseSegment):
    """A Snowflake File Format Type Options segment for ORC.

    https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html
    """

    type = "orc_file_format_type_parameters"

    _file_format_type_parameter = OneOf(
        Sequence(
            "TYPE",
            Ref("EqualsSegment"),
            OneOf(
                StringParser(
                    "'ORC'",
                    CodeSegment,
                    type="file_type",
                ),
                StringParser(
                    "ORC",
                    CodeSegment,
                    type="file_type",
                ),
            ),
        ),
        Sequence("TRIM_SPACE", Ref("EqualsSegment"), Ref("BooleanLiteralGrammar")),
        Sequence(
            "NULL_IF",
            Ref("EqualsSegment"),
            Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
        ),
    )

    match_grammar = OneOf(
        Delimited(_file_format_type_parameter), AnyNumberOf(_file_format_type_parameter)
    )


class ParquetFileFormatTypeParameters(BaseSegment):
    """A Snowflake File Format Type Options segment for PARQUET.

    https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html
    """

    type = "parquet_file_format_type_parameters"

    _file_format_type_parameter = OneOf(
        Sequence(
            "TYPE",
            Ref("EqualsSegment"),
            OneOf(
                StringParser(
                    "'PARQUET'",
                    CodeSegment,
                    type="file_type",
                ),
                StringParser(
                    "PARQUET",
                    CodeSegment,
                    type="file_type",
                ),
            ),
        ),
        Sequence(
            "COMPRESSION",
            Ref("EqualsSegment"),
            Ref("CompressionType"),
        ),
        Sequence(
            OneOf(
                "SNAPPY_COMPRESSION",
                "BINARY_AS_TEXT",
                "TRIM_SPACE",
            ),
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
        ),
        Sequence(
            "NULL_IF",
            Ref("EqualsSegment"),
            Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
        ),
    )

    match_grammar = OneOf(
        Delimited(_file_format_type_parameter), AnyNumberOf(_file_format_type_parameter)
    )


class XmlFileFormatTypeParameters(BaseSegment):
    """A Snowflake File Format Type Options segment for XML.

    https://docs.snowflake.com/en/sql-reference/sql/create-file-format.html
    """

    type = "xml_file_format_type_parameters"

    _file_format_type_parameter = OneOf(
        Sequence(
            "TYPE",
            Ref("EqualsSegment"),
            OneOf(
                StringParser(
                    "'XML'",
                    CodeSegment,
                    type="file_type",
                ),
                StringParser(
                    "XML",
                    CodeSegment,
                    type="file_type",
                ),
            ),
        ),
        Sequence(
            "COMPRESSION",
            Ref("EqualsSegment"),
            Ref("CompressionType"),
        ),
        Sequence(
            OneOf(
                "IGNORE_UTF8_ERRORS",
                "PRESERVE_SPACE",
                "STRIP_OUTER_ELEMENT",
                "DISABLE_SNOWFLAKE_DATA",
                "DISABLE_AUTO_CONVERT",
                "SKIP_BYTE_ORDER_MARK",
            ),
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
        ),
    )

    match_grammar = OneOf(
        Delimited(_file_format_type_parameter), AnyNumberOf(_file_format_type_parameter)
    )


class AlterPipeSegment(BaseSegment):
    """A snowflake `Alter PIPE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-pipe.html
    """

    type = "alter_pipe_segment"
    match_grammar = Sequence(
        "ALTER",
        "PIPE",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(
                "SET",
                AnyNumberOf(
                    Sequence(
                        "PIPE_EXECUTION_PAUSED",
                        Ref("EqualsSegment"),
                        Ref("BooleanLiteralGrammar"),
                    ),
                    Ref("CommentEqualsClauseSegment"),
                ),
            ),
            Sequence(
                "UNSET",
                OneOf("PIPE_EXECUTION_PAUSED", "COMMENT"),
            ),
            Sequence(
                "SET",
                Ref("TagEqualsSegment"),
            ),
            Sequence(
                "UNSET",
                Sequence("TAG", Delimited(Ref("TagReferenceSegment"))),
            ),
            Sequence(
                "REFRESH",
                Sequence(
                    "PREFIX",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
                Sequence(
                    "MODIFIED_AFTER",
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
            ),
        ),
        Ref("CommaSegment", optional=True),
    )


class FileFormatSegment(BaseSegment):
    """A Snowflake FILE_FORMAT Segment.

    https://docs.snowflake.com/en/sql-reference/sql/create-table.html
    https://docs.snowflake.com/en/sql-reference/sql/create-external-table.html
    https://docs.snowflake.com/en/sql-reference/sql/create-stage.html
    """

    type = "file_format_segment"
    match_grammar = OneOf(
        OneOf(
            Ref("QuotedLiteralSegment"),
            Ref("ObjectReferenceSegment"),
        ),
        Bracketed(
            Sequence(
                OneOf(
                    Sequence(
                        "FORMAT_NAME",
                        Ref("EqualsSegment"),
                        OneOf(
                            Ref("QuotedLiteralSegment"),
                            Ref("ObjectReferenceSegment"),
                        ),
                    ),
                    OneOf(
                        Ref("CsvFileFormatTypeParameters"),
                        Ref("JsonFileFormatTypeParameters"),
                        Ref("AvroFileFormatTypeParameters"),
                        Ref("OrcFileFormatTypeParameters"),
                        Ref("ParquetFileFormatTypeParameters"),
                        Ref("XmlFileFormatTypeParameters"),
                    ),
                ),
                Ref("FormatTypeOptions", optional=True),
            ),
        ),
    )


class FormatTypeOptions(BaseSegment):
    """A Snowflake formatTypeOptions.

    https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html#format-type-options
    https://docs.snowflake.com/en/sql-reference/sql/copy-into-location.html#format-type-options

    This part specifically works for the format:
        `FILE_FORMAT = (FORMAT_NAME = myformatname)`
    Another case:
        `FILE_FORMAT = (TYPE = mytype)` their fileFormatOptions are implemented in
    their specific `FormatTypeParameters`
    """

    type = "format_type_options"

    match_grammar = OneOf(
        # COPY INTO <location>, open for extension
        AnySetOf(
            Sequence(
                "COMPRESSION",
                Ref("EqualsSegment"),
                Ref("CompressionType"),
            ),
            Sequence(
                "RECORD_DELIMITER",
                Ref("EqualsSegment"),
                OneOf("NONE", Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                "FIELD_DELIMITER",
                Ref("EqualsSegment"),
                OneOf("NONE", Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                "ESCAPE",
                Ref("EqualsSegment"),
                OneOf("NONE", Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                "ESCAPE_UNENCLOSED_FIELD",
                Ref("EqualsSegment"),
                OneOf("NONE", Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                "DATA_FORMAT",
                Ref("EqualsSegment"),
                OneOf("AUTO", Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                "TIME_FORMAT",
                Ref("EqualsSegment"),
                OneOf("NONE", Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                "TIMESTAMP_FORMAT",
                Ref("EqualsSegment"),
                OneOf("NONE", Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                "BINARY_FORMAT", Ref("EqualsSegment"), OneOf("HEX", "BASE64", "UTF8")
            ),
            Sequence(
                "FIELD_OPTIONALITY_ENCLOSED_BY",
                Ref("EqualsSegment"),
                OneOf("NONE", Ref("QuotedLiteralSegment")),
            ),
            Sequence(
                "NULL_IF",
                Ref("EqualsSegment"),
                Bracketed(Delimited(Ref("QuotedLiteralSegment"))),
            ),
            Sequence(
                "EMPTY_FIELD_AS_NULL",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
            Sequence(
                "SNAPPY_COMPRESSION",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
        ),
        # COPY INTO <table>, open for extension
        AnySetOf(),
    )


class CreateExternalTableSegment(BaseSegment):
    """A snowflake `CREATE EXTERNAL TABLE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-external-table.html
    """

    type = "create_external_table_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "EXTERNAL",
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Columns:
        Bracketed(
            Delimited(
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    Ref("DatatypeSegment"),
                    "AS",
                    OptionallyBracketed(
                        Sequence(
                            Ref("ExpressionSegment"),
                            Ref("TableConstraintSegment", optional=True),
                            Sequence(
                                Ref.keyword("NOT", optional=True), "NULL", optional=True
                            ),
                        )
                    ),
                )
            ),
            optional=True,
        ),
        # The use of AnySetOf is not strictly correct here, because LOCATION and
        # FILE_FORMAT are required parameters. They can however be in arbitrary order
        # with the other parameters.
        AnySetOf(
            Sequence("INTEGRATION", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")),
            Sequence(
                "PARTITION",
                "BY",
                Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
            ),
            Sequence(
                Sequence("WITH", optional=True),
                "LOCATION",
                Ref("EqualsSegment"),
                Ref("StagePath"),
            ),
            Sequence(
                "REFRESH_ON_CREATE",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
            Sequence(
                "AUTO_REFRESH",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
            Sequence(
                "PATTERN",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "FILE_FORMAT",
                Ref("EqualsSegment"),
                Ref("FileFormatSegment"),
            ),
            Sequence(
                "AWS_SNS_TOPIC",
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "COPY",
                "GRANTS",
            ),
            Sequence(
                Sequence("WITH", optional=True),
                "ROW",
                "ACCESS",
                "POLICY",
                Ref("ObjectReferenceSegment"),
            ),
            Ref("TagBracketedEqualsSegment"),
            Ref("CommentEqualsClauseSegment"),
        ),
    )


class TableExpressionSegment(ansi.TableExpressionSegment):
    """The main table expression e.g. within a FROM clause."""

    match_grammar = OneOf(
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("TableReferenceSegment"),
        # Nested Selects
        Bracketed(Ref("SelectableGrammar")),
        Ref("ValuesClauseSegment"),
        Sequence(
            Ref("StagePath"),
            Bracketed(
                Delimited(
                    Sequence(
                        "FILE_FORMAT",
                        Ref("ParameterAssignerSegment"),
                        Ref("FileFormatSegment"),
                    ),
                    Sequence(
                        "PATTERN",
                        Ref("ParameterAssignerSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
                optional=True,
            ),
        ),
    )


class PartitionBySegment(BaseSegment):
    """A `PARTITION BY` for `copy_into_location` functions."""

    type = "partition_by_segment"

    match_grammar: Matchable = Sequence(
        "PARTITION",
        "BY",
        Indent,
        # Brackets are optional in a partition by statement
        OptionallyBracketed(Delimited(Ref("ExpressionSegment"))),
        Dedent,
    )


class CopyIntoLocationStatementSegment(BaseSegment):
    """A Snowflake `COPY INTO <location>` statement.

    # https://docs.snowflake.com/en/sql-reference/sql/copy-into-location.html
    """

    type = "copy_into_location_statement"

    match_grammar = Sequence(
        "COPY",
        "INTO",
        Ref("StorageLocation"),
        Bracketed(Delimited(Ref("ColumnReferenceSegment")), optional=True),
        Sequence(
            "FROM",
            OneOf(
                Ref("TableReferenceSegment"),
                Bracketed(Ref("SelectStatementSegment")),
            ),
            optional=True,
        ),
        OneOf(
            Ref("S3ExternalStageParameters"),
            Ref("AzureBlobStorageExternalStageParameters"),
            optional=True,
        ),
        Ref("InternalStageParameters", optional=True),
        AnySetOf(
            Ref("PartitionBySegment"),
            Sequence(
                "FILE_FORMAT",
                Ref("EqualsSegment"),
                Ref("FileFormatSegment"),
            ),
            Ref("CopyOptionsSegment"),
            Sequence(
                "VALIDATION_MODE",
                Ref("EqualsSegment"),
                Ref("ValidationModeOptionSegment"),
            ),
            Sequence(
                "HEADER",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
        ),
    )


class CopyIntoTableStatementSegment(BaseSegment):
    """A Snowflake `COPY INTO <table>` statement.

    # https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html
    """

    type = "copy_into_table_statement"

    match_grammar = Sequence(
        "COPY",
        "INTO",
        Ref("TableReferenceSegment"),
        Bracketed(Delimited(Ref("ColumnReferenceSegment")), optional=True),
        Sequence(
            "FROM",
            OneOf(
                Ref("StorageLocation"),
                Bracketed(Ref("SelectStatementSegment")),
            ),
            optional=True,
        ),
        OneOf(
            Ref("S3ExternalStageParameters"),
            Ref("AzureBlobStorageExternalStageParameters"),
            optional=True,
        ),
        Ref("InternalStageParameters", optional=True),
        AnySetOf(
            Sequence(
                "FILES",
                Ref("EqualsSegment"),
                Bracketed(
                    Delimited(
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            Sequence(
                "PATTERN",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("ReferencedVariableNameSegment"),
                ),
            ),
            Sequence(
                "FILE_FORMAT",
                Ref("EqualsSegment"),
                Ref("FileFormatSegment"),
            ),
            Ref("CopyOptionsSegment"),
        ),
        Sequence(
            "VALIDATION_MODE",
            Ref("EqualsSegment"),
            Ref("ValidationModeOptionSegment"),
            optional=True,
        ),
    )


class StorageLocation(BaseSegment):
    """A Snowflake storage location.

    https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html#syntax
    """

    type = "storage_location"

    match_grammar = OneOf(
        Ref("StagePath"),
        Ref("S3Path"),
        Ref("GCSPath"),
        Ref("AzureBlobStoragePath"),
    )


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


class CreateStageSegment(BaseSegment):
    """A Snowflake CREATE STAGE statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-stage.html
    """

    type = "create_stage_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref.keyword("TEMPORARY", optional=True),
        "STAGE",
        Ref("IfNotExistsGrammar", optional=True),
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
            Sequence(
                "URL",
                Ref("EqualsSegment"),
                OneOf(
                    # External S3 stage
                    Sequence(
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
            Bracketed(Ref("CopyOptionsSegment")),
            optional=True,
        ),
        Ref("TagBracketedEqualsSegment", optional=True),
        Ref("CommentEqualsClauseSegment", optional=True),
        Dedent,
    )


class AlterStageSegment(BaseSegment):
    """A Snowflake ALTER STAGE statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-stage.html
    """

    type = "alter_stage_statement"

    match_grammar = Sequence(
        "ALTER",
        "STAGE",
        Ref("IfExistsGrammar", optional=True),
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
                            Bracketed(Ref("CopyOptionsSegment")),
                            optional=True,
                        ),
                        Ref("CommentEqualsClauseSegment", optional=True),
                    ),
                    Ref("TagEqualsSegment"),
                ),
                Dedent,
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


class CreateStreamStatementSegment(BaseSegment):
    """A Snowflake `CREATE STREAM` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-stream.html
    """

    type = "create_stream_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "STREAM",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Sequence("COPY", "GRANTS", optional=True),
        "ON",
        OneOf(
            Sequence(
                OneOf("TABLE", "VIEW"),
                Ref("ObjectReferenceSegment"),
                OneOf(
                    Ref("FromAtExpressionSegment"),
                    Ref("FromBeforeExpressionSegment"),
                    optional=True,
                ),
                Sequence(
                    "APPEND_ONLY",
                    Ref("EqualsSegment"),
                    Ref("BooleanLiteralGrammar"),
                    optional=True,
                ),
                Sequence(
                    "SHOW_INITIAL_ROWS",
                    Ref("EqualsSegment"),
                    Ref("BooleanLiteralGrammar"),
                    optional=True,
                ),
            ),
            Sequence(
                "EXTERNAL",
                "TABLE",
                Ref("ObjectReferenceSegment"),
                OneOf(
                    Ref("FromAtExpressionSegment"),
                    Ref("FromBeforeExpressionSegment"),
                    optional=True,
                ),
                Sequence(
                    "INSERT_ONLY",
                    Ref("EqualsSegment"),
                    Ref("TrueSegment"),
                    optional=True,
                ),
            ),
            Sequence(
                "STAGE",
                Ref("ObjectReferenceSegment"),
            ),
        ),
        Ref("CommentEqualsClauseSegment", optional=True),
    )


class AlterStreamStatementSegment(BaseSegment):
    """A Snowflake `ALTER STREAM` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-stream.html
    """

    type = "alter_stream_statement"

    match_grammar = Sequence(
        "ALTER",
        "STREAM",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(
                "SET",
                Sequence(
                    "APPEND_ONLY",
                    Ref("EqualsSegment"),
                    Ref("BooleanLiteralGrammar"),
                    optional=True,
                ),
                Sequence(
                    "INSERT_ONLY",
                    Ref("EqualsSegment"),
                    Ref("TrueSegment"),
                    optional=True,
                ),
                Ref("TagEqualsSegment", optional=True),
                Ref("CommentEqualsClauseSegment", optional=True),
            ),
            Sequence(
                "UNSET",
                OneOf(
                    Sequence("TAG", Delimited(Ref("TagReferenceSegment"))),
                    "COMMENT",
                ),
            ),
        ),
    )


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


class AlterAccountStatementSegment(BaseSegment):
    """`ALTER ACCOUNT` statement.

    ALTER ACCOUNT SET { [ accountParams ] [ objectParams ] [ sessionParams ] }

    ALTER ACCOUNT UNSET <param_name> [ , ... ]

    ALTER ACCOUNT SET RESOURCE_MONITOR = <monitor_name>

    ALTER ACCOUNT SET { PASSWORD | SESSION } POLICY <policy_name>

    ALTER ACCOUNT UNSET { PASSWORD | SESSION } POLICY

    ALTER ACCOUNT SET TAG <tag_name> = '<tag_value>' [, <tag_name> = '<tag_value>' ...]

    ALTER ACCOUNT UNSET TAG <tag_name> [ , <tag_name> ... ]

    https://docs.snowflake.com/en/sql-reference/sql/alter-account

    All the account parameters can be found here
    https://docs.snowflake.com/en/sql-reference/parameters
    """

    type = "alter_account_statement"

    match_grammar = Sequence(
        "ALTER",
        "ACCOUNT",
        OneOf(
            Sequence(
                "SET",
                "RESOURCE_MONITOR",
                Ref("EqualsSegment"),
                Ref("NakedIdentifierSegment"),
            ),
            Sequence(
                "SET",
                OneOf("PASSWORD", "SESSION"),
                "POLICY",
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "SET",
                Ref("TagEqualsSegment"),
            ),
            Sequence(
                "SET",
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        OneOf(
                            Ref("BooleanLiteralGrammar"),
                            Ref("QuotedLiteralSegment"),
                            Ref("NumericLiteralSegment"),
                            Ref("NakedIdentifierSegment"),
                        ),
                    ),
                ),
            ),
            Sequence(
                "UNSET",
                OneOf("PASSWORD", "SESSION"),
                "POLICY",
            ),
            Sequence(
                "UNSET",
                OneOf(
                    Sequence("TAG", Delimited(Ref("TagReferenceSegment"))),
                    Delimited(Ref("NakedIdentifierSegment")),
                ),
            ),
        ),
    )


class AlterUserStatementSegment(BaseSegment):
    """`ALTER USER` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-user.html

    All user parameters can be found here
    https://docs.snowflake.com/en/sql-reference/parameters.html
    """

    type = "alter_user_statement"

    match_grammar = Sequence(
        "ALTER",
        "USER",
        Ref("IfExistsGrammar", optional=True),
        Ref("RoleReferenceSegment"),
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
            # Snowflake supports the SET command with space delimited parameters, but
            # it also supports using commas which is better supported by `Delimited`, so
            # we will just use that.
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


class CreateRoleStatementSegment(ansi.CreateRoleStatementSegment):
    """A `CREATE ROLE` statement.

    Redefined because it's much simpler than postgres.
    https://docs.snowflake.com/en/sql-reference/sql/create-role.html
    """

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "ROLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("RoleReferenceSegment"),
        Sequence(
            "COMMENT",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


class CreateDatabaseRoleStatementSegment(BaseSegment):
    """A `CREATE DATABASE ROLE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-database-role
    """

    type = "create_database_role_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref(
            "OrReplaceGrammar",
            optional=True,
        ),
        "DATABASE",
        "ROLE",
        Ref(
            "IfNotExistsGrammar",
            optional=True,
        ),
        Ref("DatabaseRoleReferenceSegment"),
        Sequence(
            "COMMENT",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


class ResourceMonitorOptionsSegment(BaseSegment):
    """A `RESOURCE MONITOR` options statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-resource-monitor
    https://docs.snowflake.com/en/sql-reference/sql/alter-resource-monitor
    """

    type = "resource_monitor_options"
    match_grammar = AnySetOf(
        Sequence(
            "CREDIT_QUOTA",
            Ref("EqualsSegment"),
            Ref("IntegerSegment"),
            optional=True,
        ),
        Sequence(
            "FREQUENCY",
            Ref("EqualsSegment"),
            OneOf("MONTHLY", "DAILY", "WEEKLY", "YEARLY", "NEVER"),
            optional=True,
        ),
        Sequence(
            "START_TIMESTAMP",
            Ref("EqualsSegment"),
            OneOf(Ref("QuotedLiteralSegment"), "IMMEDIATELY"),
            optional=True,
        ),
        Sequence(
            "END_TIMESTAMP",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
        Sequence(
            "NOTIFY_USERS",
            Ref("EqualsSegment"),
            Bracketed(
                Delimited(
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "TRIGGERS",
            AnyNumberOf(
                Sequence(
                    "ON",
                    Ref("IntegerSegment"),
                    "PERCENT",
                    "DO",
                    OneOf("SUSPEND", "SUSPEND_IMMEDIATE", "NOTIFY"),
                ),
            ),
            optional=True,
        ),
    )


class CreateResourceMonitorStatementSegment(BaseSegment):
    """A `CREATE RESOURCE MONITOR` statement.

    https://docs.snowflake.com/en/sql-reference/sql/create-resource-monitor
    """

    type = "create_resource_monitor_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("RESOURCE", "MONITOR"),
        Ref("ObjectReferenceSegment"),
        "WITH",
        Ref("ResourceMonitorOptionsSegment"),
    )


class AlterResourceMonitorStatementSegment(BaseSegment):
    """An `ALTER RESOURCE MONITOR` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-resource-monitor
    """

    type = "alter_resource_monitor_statement"
    match_grammar = Sequence(
        "ALTER",
        Sequence("RESOURCE", "MONITOR"),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "SET",
        Ref("ResourceMonitorOptionsSegment"),
    )


class ExplainStatementSegment(ansi.ExplainStatementSegment):
    """An `Explain` statement.

    EXPLAIN [ USING { TABULAR | JSON | TEXT } ] <statement>

    https://docs.snowflake.com/en/sql-reference/sql/explain.html
    """

    match_grammar = Sequence(
        "EXPLAIN",
        Sequence(
            "USING",
            OneOf("TABULAR", "JSON", "TEXT"),
            optional=True,
        ),
        ansi.ExplainStatementSegment.explainable_stmt,
    )


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
        Delimited(Ref("ParameterNameSegment")),
    )


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
        Ref("IfExistsGrammar", optional=True),
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
                ansi.ExplainStatementSegment.explainable_stmt,
            ),
            Sequence("MODIFY", "WHEN", Ref("BooleanLiteralGrammar")),
        ),
    )


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
        AnySetOf(
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
        ),
    )


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
        Delimited(Ref("ParameterNameSegment")),
    )


class ExecuteImmediateClauseSegment(BaseSegment):
    """Snowflake's EXECUTE IMMEDIATE clause.

    ```
    EXECUTE IMMEDIATE '<string_literal>'
        [ USING ( <bind_variable> [ , <bind_variable> ... ] ) ]

    EXECUTE IMMEDIATE <variable>
        [ USING ( <bind_variable> [ , <bind_variable> ... ] ) ]

    EXECUTE IMMEDIATE $<session_variable>
        [ USING ( <bind_variable> [ , <bind_variable> ... ] ) ]
    ```

    https://docs.snowflake.com/en/sql-reference/sql/execute-immediate
    """

    type = "execute_immediate_clause"

    match_grammar = Sequence(
        "EXECUTE",
        "IMMEDIATE",
        OneOf(
            Ref("QuotedLiteralSegment"),
            Ref("ReferencedVariableNameSegment"),
            Sequence(
                Ref("ColonSegment"),
                Ref("LocalVariableNameSegment"),
            ),
        ),
        Sequence(
            "USING",
            Bracketed(Delimited(Ref("LocalVariableNameSegment"))),
            optional=True,
        ),
    )


class ExecuteTaskClauseSegment(BaseSegment):
    """Snowflake's EXECUTE TASK clause.

    ```
        EXECUTE TASK <name>
    ```

    https://docs.snowflake.com/en/sql-reference/sql/execute-task
    """

    type = "execute_task_clause"
    match_grammar = Sequence(
        "EXECUTE",
        "TASK",
        Ref("ObjectReferenceSegment"),
    )


############################
# MERGE
############################
class MergeUpdateClauseSegment(ansi.MergeUpdateClauseSegment):
    """`UPDATE` clause within the `MERGE` statement."""

    match_grammar = Sequence(
        "UPDATE",
        Ref("SetClauseListSegment"),
        Ref("WhereClauseSegment", optional=True),
    )


class MergeDeleteClauseSegment(ansi.MergeDeleteClauseSegment):
    """`DELETE` clause within the `MERGE` statement."""

    match_grammar = Sequence(
        "DELETE",
        Ref("WhereClauseSegment", optional=True),
    )


class MergeInsertClauseSegment(ansi.MergeInsertClauseSegment):
    """`INSERT` clause within the `MERGE` statement."""

    match_grammar = Sequence(
        "INSERT",
        Indent,
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Dedent,
        Ref("ValuesClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
    )


class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/delete.html
    """

    type = "delete_statement"
    match_grammar = Sequence(
        "DELETE",
        "FROM",
        Ref("TableReferenceSegment"),
        Ref("AliasExpressionSegment", optional=True),
        Sequence(
            "USING",
            Indent,
            Delimited(
                Sequence(
                    Ref("TableExpressionSegment"),
                    Ref("AliasExpressionSegment", optional=True),
                ),
            ),
            Dedent,
            optional=True,
        ),
        Ref("WhereClauseSegment", optional=True),
    )


class DescribeStatementSegment(BaseSegment):
    """`DESCRIBE` statement grammar.

    https://docs.snowflake.com/en/sql-reference/sql/desc.html
    """

    type = "describe_statement"
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
                OneOf("API", "NOTIFICATION", "SECURITY", "STORAGE", optional=True),
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


class TransactionStatementSegment(ansi.TransactionStatementSegment):
    """`BEGIN`, `START TRANSACTION`, `COMMIT`, AND `ROLLBACK` statement grammar.

    Overwrites ANSI to match correct Snowflake grammar.

    https://docs.snowflake.com/en/sql-reference/sql/begin.html
    https://docs.snowflake.com/en/sql-reference/sql/commit.html
    https://docs.snowflake.com/en/sql-reference/sql/rollback.html
    """

    match_grammar = OneOf(
        Sequence(
            "BEGIN",
            OneOf("WORK", "TRANSACTION", optional=True),
            Sequence("NAME", Ref("ObjectReferenceSegment"), optional=True),
        ),
        Sequence(
            "START",
            "TRANSACTION",
            Sequence("NAME", Ref("ObjectReferenceSegment"), optional=True),
        ),
        Sequence(
            "COMMIT",
            Sequence("WORK", optional=True),
        ),
        "ROLLBACK",
    )


class TruncateStatementSegment(ansi.TruncateStatementSegment):
    """`TRUNCATE TABLE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/truncate-table.html
    """

    match_grammar = Sequence(
        "TRUNCATE",
        Ref.keyword("TABLE", optional=True),
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
    )


class UnsetStatementSegment(BaseSegment):
    """An `UNSET` statement.

    https://docs.snowflake.com/en/sql-reference/sql/unset.html
    """

    type = "unset_statement"

    match_grammar = Sequence(
        "UNSET",
        OneOf(
            Ref("LocalVariableNameSegment"),
            Bracketed(
                Delimited(
                    Ref("LocalVariableNameSegment"),
                ),
            ),
        ),
    )


class UndropStatementSegment(BaseSegment):
    """`UNDROP` statement.

    DATABASE: https://docs.snowflake.com/en/sql-reference/sql/undrop-database.html
    SCHEMA: https://docs.snowflake.com/en/sql-reference/sql/undrop-schema.html
    TABLE: https://docs.snowflake.com/en/sql-reference/sql/undrop-table.html
    """

    type = "undrop_statement"
    match_grammar = Sequence(
        "UNDROP",
        OneOf(
            Sequence(
                "DATABASE",
                Ref("DatabaseReferenceSegment"),
            ),
            Sequence(
                "SCHEMA",
                Ref("SchemaReferenceSegment"),
            ),
            Sequence(
                "TABLE",
                Ref("TableReferenceSegment"),
            ),
        ),
    )


class CommentStatementSegment(BaseSegment):
    """`COMMENT` statement grammar.

    https://docs.snowflake.com/en/sql-reference/sql/comment.html

    N.B. this applies to all objects, so there may be some I've missed
    here so add any others to the OneOf grammar below.
    """

    type = "comment_statement"
    match_grammar = Sequence(
        "COMMENT",
        Ref("IfExistsGrammar", optional=True),
        "ON",
        OneOf(
            "COLUMN",
            "TABLE",
            "VIEW",
            "SCHEMA",
            "DATABASE",
            "WAREHOUSE",
            "USER",
            "STAGE",
            "FUNCTION",
            "PROCEDURE",
            "SEQUENCE",
            "SHARE",
            "PIPE",
            "STREAM",
            "TASK",
            Sequence(
                "NETWORK",
                "POLICY",
            ),
            Sequence(
                OneOf(
                    "API",
                    "NOTIFICATION",
                    "SECURITY",
                    "STORAGE",
                ),
                "INTEGRATION",
            ),
            Sequence(
                "SESSION",
                "POLICY",
            ),
            Sequence(
                "EXTERNAL",
                "TABLE",
            ),
            Sequence(
                "MATERIALIZED",
                "VIEW",
            ),
            Sequence(
                "MASKING",
                "POLICY",
            ),
            Sequence(
                "ROW",
                "ACCESS",
                "POLICY",
            ),
            Sequence(
                "FILE",
                "FORMAT",
            ),
        ),
        Ref("ObjectReferenceSegment"),
        "IS",
        Ref("QuotedLiteralSegment"),
    )


class UseStatementSegment(ansi.UseStatementSegment):
    """A `USE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/use.html
    """

    match_grammar = Sequence(
        "USE",
        OneOf(
            Sequence("ROLE", Ref("ObjectReferenceSegment")),
            Sequence("WAREHOUSE", Ref("ObjectReferenceSegment")),
            Sequence(
                Ref.keyword("DATABASE", optional=True),
                Ref("DatabaseReferenceSegment"),
            ),
            Sequence(
                Ref.keyword("SCHEMA", optional=True),
                Ref("SchemaReferenceSegment"),
            ),
            Sequence(
                "SECONDARY",
                "ROLES",
                OneOf(
                    "ALL",
                    "NONE",
                ),
            ),
        ),
    )


class CallStatementSegment(BaseSegment):
    """`CALL` statement.

    https://docs.snowflake.com/en/sql-reference/sql/call.html
    """

    type = "call_statement"
    match_grammar = Sequence(
        "CALL",
        Sequence(
            Ref("FunctionNameSegment"),
            Bracketed(
                Ref(
                    "FunctionContentsGrammar",
                    # The brackets might be empty for some functions...
                    optional=True,
                ),
                parse_mode=ParseMode.GREEDY,
            ),
        ),
    )


class LimitClauseSegment(ansi.LimitClauseSegment):
    """A `LIMIT` clause.

    https://docs.snowflake.com/en/sql-reference/constructs/limit.html
    """

    match_grammar = OneOf(
        Sequence(
            "LIMIT",
            Indent,
            Ref("LimitLiteralGrammar"),
            Dedent,
            Sequence(
                "OFFSET",
                Indent,
                Ref("LimitLiteralGrammar"),
                Dedent,
                optional=True,
            ),
        ),
        Sequence(
            Sequence(
                "OFFSET",
                Indent,
                Ref("LimitLiteralGrammar"),
                OneOf(
                    "ROW",
                    "ROWS",
                    optional=True,
                ),
                Dedent,
                optional=True,
            ),
            "FETCH",
            Indent,
            OneOf(
                "FIRST",
                "NEXT",
                optional=True,
            ),
            Ref("LimitLiteralGrammar"),
            OneOf(
                "ROW",
                "ROWS",
                optional=True,
            ),
            Ref.keyword("ONLY", optional=True),
            Dedent,
        ),
    )


class SelectClauseSegment(ansi.SelectClauseSegment):
    """A group of elements in a select target statement."""

    match_grammar = ansi.SelectClauseSegment.match_grammar.copy(
        terminators=[Ref.keyword("FETCH"), Ref.keyword("OFFSET")],
    )


class OrderByClauseSegment(ansi.OrderByClauseSegment):
    """An `ORDER BY` clause.

    https://docs.snowflake.com/en/sql-reference/constructs/order-by.html
    """

    match_grammar = Sequence(
        "ORDER",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    # Can `ORDER BY 1`
                    Ref("NumericLiteralSegment"),
                    # Can order by an expression
                    Ref("ExpressionSegment"),
                ),
                OneOf("ASC", "DESC", optional=True),
                Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
            ),
            terminators=["LIMIT", "FETCH", "OFFSET", Ref("FrameClauseUnitGrammar")],
        ),
        Dedent,
    )


class FrameClauseSegment(ansi.FrameClauseSegment):
    """A frame clause for window functions.

    https://docs.snowflake.com/en/sql-reference/functions-analytic.html#window-frame-syntax-and-usage
    """

    type = "frame_clause"

    _frame_extent = OneOf(
        Sequence("CURRENT", "ROW"),
        Sequence(
            OneOf(
                Ref("NumericLiteralSegment"),
                Ref("ReferencedVariableNameSegment"),
                "UNBOUNDED",
            ),
            OneOf("PRECEDING", "FOLLOWING"),
        ),
    )

    match_grammar: Matchable = Sequence(
        Ref("FrameClauseUnitGrammar"),
        OneOf(_frame_extent, Sequence("BETWEEN", _frame_extent, "AND", _frame_extent)),
    )


class DropProcedureStatementSegment(BaseSegment):
    """A snowflake `DROP PROCEDURE ...` statement.

    https://docs.snowflake.com/en/sql-reference/sql/drop-procedure.html
    """

    type = "drop_procedure_statement"
    match_grammar = Sequence(
        "DROP",
        "PROCEDURE",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
    )


class DropExternalTableStatementSegment(BaseSegment):
    """A snowflake `DROP EXTERNAL TABLE ...` statement.

    https://docs.snowflake.com/en/sql-reference/sql/drop-external-table.html
    """

    type = "drop_external_table_statement"
    match_grammar = Sequence(
        "DROP",
        "EXTERNAL",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class DropFunctionStatementSegment(BaseSegment):
    """A `DROP FUNCTION` statement."""

    type = "drop_function_statement"

    match_grammar = Sequence(
        "DROP",
        Ref.keyword("EXTERNAL", optional=True),
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
    )


class DropMaterializedViewStatementSegment(BaseSegment):
    """A snowflake `DROP MATERIALIZED VIEW ...` statement.

    https://docs.snowflake.com/en/sql-reference/sql/drop-materialized-view.html
    """

    type = "drop_materialized_view_statement"
    match_grammar = Sequence(
        "DROP",
        "MATERIALIZED",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
    )


class DropObjectStatementSegment(BaseSegment):
    """A snowflake `DROP <object> ...` statement.

    https://docs.snowflake.com/en/sql-reference/sql/drop.html
    """

    type = "drop_object_statement"
    match_grammar = Sequence(
        "DROP",
        OneOf(
            Sequence(
                OneOf(
                    "CONNECTION",
                    Sequence("FILE", "FORMAT"),
                    Sequence(
                        OneOf(
                            "API", "NOTIFICATION", "SECURITY", "STORAGE", optional=True
                        ),
                        "INTEGRATION",
                    ),
                    "PIPE",
                    Sequence("ROW", "ACCESS", "POLICY"),
                    "STAGE",
                    "STREAM",
                    "TAG",
                    "TASK",
                ),
                Ref("IfExistsGrammar", optional=True),
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                OneOf(Sequence("RESOURCE", "MONITOR"), "SHARE"),
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                OneOf(
                    Sequence("MANAGED", "ACCOUNT"),
                    Sequence("MASKING", "POLICY"),
                ),
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence(
                OneOf(
                    Sequence("NETWORK", "POLICY"),
                ),
                Ref("IfExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence(
                OneOf("WAREHOUSE", Sequence("SESSION", "POLICY")),
                Ref("IfExistsGrammar", optional=True),
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence(
                "SEQUENCE",
                Ref("IfExistsGrammar", optional=True),
                Ref("ObjectReferenceSegment"),
                Ref("DropBehaviorGrammar", optional=True),
            ),
        ),
    )


class ListStatementSegment(BaseSegment):
    """A snowflake `LIST @<stage> ...` statement.

    https://docs.snowflake.com/en/sql-reference/sql/list.html
    """

    type = "list_statement"

    match_grammar = Sequence(
        OneOf("LIST", "LS"),
        Ref("StagePath"),
        Sequence(
            "PATTERN", Ref("EqualsSegment"), Ref("QuotedLiteralSegment"), optional=True
        ),
    )


class GetStatementSegment(BaseSegment):
    """A snowflake `GET @<stage> ...` statement.

    https://docs.snowflake.com/en/sql-reference/sql/get.html
    """

    type = "get_statement"

    match_grammar = Sequence(
        "GET",
        Ref("StagePath"),
        OneOf(
            Ref("UnquotedFilePath"),
            Ref("QuotedLiteralSegment"),
        ),
        AnySetOf(
            Sequence(
                "PARALLEL",
                Ref("EqualsSegment"),
                Ref("IntegerSegment"),
            ),
            Sequence(
                "PATTERN",
                Ref("EqualsSegment"),
                OneOf(
                    Ref("QuotedLiteralSegment"), Ref("ReferencedVariableNameSegment")
                ),
            ),
        ),
    )


class PutStatementSegment(BaseSegment):
    """A snowflake `PUT ...` statement.

    https://docs.snowflake.com/en/sql-reference/sql/put.html
    """

    type = "put_statement"

    match_grammar = Sequence(
        "PUT",
        OneOf(
            Ref("UnquotedFilePath"),
            Ref("QuotedLiteralSegment"),
        ),
        Ref("StagePath"),
        AnySetOf(
            Sequence(
                "PARALLEL",
                Ref("EqualsSegment"),
                Ref("IntegerSegment"),
            ),
            Sequence(
                "AUTO_COMPRESS",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
            Sequence(
                "SOURCE_COMPRESSION", Ref("EqualsSegment"), Ref("CompressionType")
            ),
            Sequence(
                "OVERWRITE",
                Ref("EqualsSegment"),
                Ref("BooleanLiteralGrammar"),
            ),
        ),
    )


class RemoveStatementSegment(BaseSegment):
    """A snowflake `REMOVE @<stage> ...` statement.

    https://docs.snowflake.com/en/sql-reference/sql/remove.html
    """

    type = "remove_statement"

    match_grammar = Sequence(
        OneOf(
            "REMOVE",
            "RM",
        ),
        Ref("StagePath"),
        Sequence(
            "PATTERN",
            Ref("EqualsSegment"),
            OneOf(Ref("QuotedLiteralSegment"), Ref("ReferencedVariableNameSegment")),
            optional=True,
        ),
    )


class SetOperatorSegment(ansi.SetOperatorSegment):
    """A set operator such as Union, Minus, Except or Intersect."""

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
        "MINUS",
    )


class ShorthandCastSegment(BaseSegment):
    """A casting operation using '::'."""

    type = "cast_expression"
    match_grammar: Matchable = Sequence(
        OneOf(
            Ref("Expression_D_Grammar"),
            Ref("CaseExpressionSegment"),
        ),
        AnyNumberOf(
            Sequence(
                Ref("CastOperatorSegment"),
                Ref("DatatypeSegment"),
                OneOf(
                    Ref("TimeZoneGrammar"),
                    AnyNumberOf(
                        Ref("ArrayAccessorSegment"),
                    ),
                    AnyNumberOf(
                        Ref("SemiStructuredAccessorSegment"),
                    ),
                    optional=True,
                ),
            ),
            min_times=1,
        ),
    )


class AlterDatabaseSegment(BaseSegment):
    """An `ALTER DATABASE` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-database
    """

    type = "alter_database_statement"

    match_grammar = Sequence(
        "ALTER",
        "DATABASE",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("ObjectReferenceSegment")),
            Sequence("SWAP", "WITH", Ref("ObjectReferenceSegment")),
            Sequence(
                "SET",
                OneOf(
                    Ref("TagEqualsSegment"),
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
                ),
            ),
            Sequence("UNSET", "TAG", Delimited(Ref("TagReferenceSegment"))),
            Sequence(
                "UNSET",
                Delimited(
                    AnySetOf(
                        "DATA_RETENTION_TIME_IN_DAYS",
                        "MAX_DATA_EXTENSION_TIME_IN_DAYS",
                        "DEFAULT_DDL_COLLATION",
                        "COMMENT",
                    ),
                ),
            ),
        ),
    )


class AlterMaskingPolicySegment(BaseSegment):
    """An `ALTER MASKING POLICY` statement.

    https://docs.snowflake.com/en/sql-reference/sql/alter-masking-policy
    """

    type = "alter_masking_policy"

    match_grammar = Sequence(
        "ALTER",
        "MASKING",
        "POLICY",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("ObjectReferenceSegment")),
            Sequence(
                "SET",
                "BODY",
                Ref("FunctionAssignerSegment"),
                Ref("ExpressionSegment"),
            ),
            Sequence("SET", Ref("TagEqualsSegment")),
            Sequence("UNSET", "TAG", Delimited(Ref("TagReferenceSegment"))),
            Sequence(
                "SET", "COMMENT", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")
            ),
            Sequence("UNSET", "COMMENT"),
        ),
    )
