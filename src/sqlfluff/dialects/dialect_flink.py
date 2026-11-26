"""The FlinkSQL dialect.

Inherits from ANSI SQL.
FlinkSQL is based on ANSI SQL standard but includes additional features
for stream processing and table operations.

Based on:
https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/
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
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_flink_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")
flink_dialect = ansi_dialect.copy_as(
    "flink",
    formatted_name="Apache Flink SQL",
    docstring="""**Default Casing**: FlinkSQL is case insensitive with
both quoted and unquoted identifiers.

**Quotes**: String Literals: ``'`` (single quotes), Identifiers: |back_quotes|.

The dialect for Apache `Flink SQL`_. This dialect includes FlinkSQL-specific
syntax for stream processing, table operations, and connector configurations.

FlinkSQL supports advanced features like:
- ROW data types for complex nested structures
- Table connectors (Kafka, BigQuery, etc.)
- Watermark definitions for event time processing
- Computed columns and metadata columns
- Temporal table functions

.. _`Flink SQL`: https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/
""",
)

# Update keywords - extend ANSI keywords instead of replacing them
flink_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
flink_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)

# Add FlinkSQL-specific lexer patterns
flink_dialect.patch_lexer_matchers(
    [
        # FlinkSQL uses -- for single-line comments
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--",)},
        ),
        # Support for backtick-quoted identifiers
        RegexLexer(
            "back_quote",
            r"`([^`]|``)*`",
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r"`((?:[^`]|``)*)`", 1),
                "escape_replacements": [(r"``", "`")],
            },
        ),
        # Support for numeric literals with precision/scale
        RegexLexer(
            "numeric_literal",
            (
                r"(?>(?>\d+\.\d+|\d+\.|\.\d+)([eE][+-]?\d+)?([dDfF]|BD|bd)?"
                r"|\d+[eE][+-]?\d+([dDfF]|BD|bd)?"
                r"|\d+([dDfFlLsSyY]|BD|bd)?)"
                r"((?<=\.)|(?=\b))"
            ),
            CodeSegment,
        ),
        # Support for string literals with single quotes, including
        # doubled quotes used to escape a quote.
        RegexLexer(
            "single_quote",
            r"'([^'\\]|\\.|'')*'",
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r"'((?:[^'\\]|\\.|'')*)'", 1),
                "escape_replacements": [(r"\\'|''", "'")],
            },
        ),
        # Support for == equality operator
        RegexLexer("equals", r"==|=", CodeSegment),
    ]
)

flink_dialect.insert_lexer_matchers(
    [
        # Named argument arrow for Process Table Functions (param => value)
        StringLexer("right_arrow", "=>", CodeSegment),
    ],
    before="equals",
)

# Add FlinkSQL-specific datetime units
flink_dialect.sets("datetime_units").clear()
flink_dialect.sets("datetime_units").update(
    [
        "YEAR",
        "MONTH",
        "DAY",
        "HOUR",
        "MINUTE",
        "SECOND",
        "MICROSECOND",
        "MILLISECOND",
        "NANOSECOND",
        "EPOCH",
        "DECADE",
        "CENTURY",
        "MILLENNIUM",
        "QUARTER",
        "WEEK",
        "DOW",
        "ISODOW",
        "DOY",
        "ISOYEAR",
    ]
)

# Add FlinkSQL-specific bare functions
flink_dialect.sets("bare_functions").clear()
flink_dialect.sets("bare_functions").update(
    [
        "CURRENT_DATE",
        "CURRENT_TIME",
        "CURRENT_TIMESTAMP",
        "CURRENT_USER",
        "LOCALTIME",
        "LOCALTIMESTAMP",
        "NOW",
        "CURRENT_WATERMARK",
        "PROCTIME",
    ]
)

# Add FlinkSQL-specific date part functions
flink_dialect.sets("date_part_function_name").update(["TIMESTAMPDIFF"])

# Add angle brackets for generic types
flink_dialect.bracket_sets("angle_bracket_pairs").update(
    [
        ("angle", "StartAngleBracketSegment", "EndAngleBracketSegment", False),
    ]
)

# Add FlinkSQL-specific segments
flink_dialect.add(
    # Angle bracket segments
    StartAngleBracketSegment=StringParser(
        "<",
        SymbolSegment,
        type="start_angle_bracket",
    ),
    EndAngleBracketSegment=StringParser(
        ">",
        SymbolSegment,
        type="end_angle_bracket",
    ),
    # Backtick identifier support
    BackQuotedIdentifierSegment=TypedParser(
        "back_quote",
        IdentifierSegment,
        type="quoted_identifier",
        trim_chars=("`",),
        casefold=str.upper,
    ),
    # Double equals operator for connector options
    DoubleEqualsSegment=StringParser("==", SymbolSegment, type="double_equals"),
    # Named argument arrow for Process Table Functions
    RightArrowSegment=StringParser("=>", SymbolSegment, type="right_arrow"),
    # Row pattern quantifier used by MATCH_RECOGNIZE
    QuestionMarkSegment=StringParser("?", SymbolSegment, type="question_mark"),
    # Connector option list: ('key' = 'value', ...)
    FlinkOptionsListGrammar=Bracketed(
        Delimited(
            Sequence(
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NakedIdentifierSegment"),
                ),
                OneOf(
                    Ref("EqualsSegment"),
                    Ref("DoubleEqualsSegment"),
                ),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NakedIdentifierSegment"),
                ),
            ),
        ),
    ),
    # Option key list for RESET ('key1', 'key2', ...)
    FlinkOptionKeyListGrammar=Bracketed(
        Delimited(
            Ref("QuotedLiteralSegment"),
        ),
    ),
    # Start mode clause for MATERIALIZED TABLE (Flink 2.3 FLIP-557)
    FlinkStartModeClauseGrammar=Sequence(
        "START_MODE",
        Ref("EqualsSegment"),
        OneOf(
            "FROM_BEGINNING",
            Sequence(
                "FROM_NOW",
                Bracketed(Ref("IntervalExpressionSegment"), optional=True),
            ),
            Sequence(
                "FROM_TIMESTAMP",
                Bracketed(Ref("ExpressionSegment")),
            ),
            "RESUME_OR_FROM_BEGINNING",
            Sequence(
                "RESUME_OR_FROM_NOW",
                Bracketed(Ref("IntervalExpressionSegment"), optional=True),
            ),
            Sequence(
                "RESUME_OR_FROM_TIMESTAMP",
                Bracketed(Ref("ExpressionSegment")),
            ),
        ),
    ),
    FlinkFreshnessClauseGrammar=Sequence(
        "FRESHNESS",
        Ref("EqualsSegment"),
        Ref("IntervalExpressionSegment"),
    ),
    FlinkRefreshModeClauseGrammar=Sequence(
        "REFRESH_MODE",
        Ref("EqualsSegment"),
        OneOf("FULL", "CONTINUOUS"),
    ),
    FlinkMaterializedAlterColumnPositionGrammar=OneOf(
        "FIRST",
        Sequence("AFTER", Ref("ColumnReferenceSegment")),
    ),
    FlinkMaterializedAlterSchemaComponentGrammar=OneOf(
        Sequence(
            Ref("MetadataColumnDefinitionSegment"),
            Ref("FlinkMaterializedAlterColumnPositionGrammar", optional=True),
        ),
        Sequence(
            Ref("ComputedColumnDefinitionSegment"),
            Ref("FlinkMaterializedAlterColumnPositionGrammar", optional=True),
        ),
        Sequence(
            Ref("ColumnDefinitionSegment"),
            Ref("FlinkMaterializedAlterColumnPositionGrammar", optional=True),
        ),
        Ref("WatermarkDefinitionSegment"),
        Ref("FlinkTableConstraintSegment"),
    ),
    FlinkMaterializedAlterDistributionGrammar=Sequence(
        "DISTRIBUTION",
        OneOf(
            Sequence(
                "BY",
                OneOf("HASH", "RANGE", optional=True),
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                ),
                Sequence(
                    "INTO",
                    Ref("NumericLiteralSegment"),
                    OneOf("BUCKETS", "BUCKET"),
                    optional=True,
                ),
            ),
            Sequence(
                "INTO",
                Ref("NumericLiteralSegment"),
                OneOf("BUCKETS", "BUCKET"),
            ),
        ),
    ),
    FlinkPropertyNamePartSegment=Sequence(
        Ref("SingleIdentifierGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("MinusSegment"),
                Ref("SingleIdentifierGrammar"),
                allow_gaps=False,
            ),
        ),
    ),
    FlinkPropertyNameSegment=OneOf(
        Delimited(
            Ref("FlinkPropertyNamePartSegment"),
            delimiter=Ref("DotSegment"),
            allow_gaps=False,
        ),
        Ref("QuotedLiteralSegment"),
    ),
    FlinkPropertyValueSegment=OneOf(
        Ref("LiteralGrammar"),
        Delimited(
            Ref("FlinkPropertyNamePartSegment"),
            delimiter=Ref("DotSegment"),
            allow_gaps=False,
        ),
    ),
    # Connector options for CREATE TABLE
    CreateTableConnectorOptionsSegment=Sequence(
        "WITH",
        Bracketed(
            Delimited(
                Sequence(
                    OneOf(
                        Ref("QuotedLiteralSegment"),  # 'key' format
                        Ref("NakedIdentifierSegment"),  # key format
                    ),
                    OneOf(
                        Ref("EqualsSegment"),  # single =
                        Ref("DoubleEqualsSegment"),  # double == format
                    ),
                    OneOf(
                        Ref("QuotedLiteralSegment"),  # 'value' format
                        Ref("NakedIdentifierSegment"),  # value format
                    ),
                ),
            ),
        ),
    ),
    # Watermark definition
    WatermarkDefinitionSegment=Sequence(
        "WATERMARK",
        "FOR",
        Ref("ColumnReferenceSegment"),
        "AS",
        Ref("ExpressionSegment"),
    ),
    # Computed column definition
    ComputedColumnDefinitionSegment=Sequence(
        Ref("SingleIdentifierGrammar"),  # column name
        "AS",
        Ref("ExpressionSegment"),  # computed expression
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
    ),
    # Metadata column definition
    MetadataColumnDefinitionSegment=Sequence(
        Ref("SingleIdentifierGrammar"),  # column name
        Ref("DatatypeSegment"),  # column type
        "METADATA",
        Sequence("FROM", Ref("QuotedLiteralSegment"), optional=True),
        Sequence("VIRTUAL", optional=True),
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
    ),
    # Table constraint
    FlinkTableConstraintSegment=Sequence(
        Sequence("CONSTRAINT", Ref("NakedIdentifierSegment"), optional=True),
        "PRIMARY",
        "KEY",
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
            ),
        ),
        "NOT",
        "ENFORCED",
    ),
    # Partition definition
    PartitionDefinitionSegment=Sequence(
        "PARTITIONED",
        "BY",
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
            ),
        ),
    ),
    # Distribution definition
    DistributionDefinitionSegment=OneOf(
        # DISTRIBUTED BY [HASH|RANGE] (columns) [INTO n BUCKETS]
        Sequence(
            "DISTRIBUTED",
            "BY",
            OneOf("HASH", "RANGE", optional=True),
            Bracketed(
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
            ),
            Sequence("INTO", Ref("NumericLiteralSegment"), "BUCKETS", optional=True),
        ),
        # DISTRIBUTED INTO n BUCKETS
        Sequence(
            "DISTRIBUTED",
            "INTO",
            Ref("NumericLiteralSegment"),
            "BUCKETS",
        ),
    ),
    # LIKE options
    LikeOptionsSegment=Delimited(
        OneOf(
            # INCLUDING/EXCLUDING with ALL/CONSTRAINTS/DISTRIBUTION/PARTITIONS
            Sequence(
                OneOf("INCLUDING", "EXCLUDING"),
                OneOf("ALL", "CONSTRAINTS", "DISTRIBUTION", "PARTITIONS"),
            ),
            # INCLUDING/EXCLUDING/OVERWRITING with GENERATED/OPTIONS/WATERMARKS
            Sequence(
                OneOf("INCLUDING", "EXCLUDING", "OVERWRITING"),
                OneOf("GENERATED", "OPTIONS", "WATERMARKS"),
            ),
        ),
    ),
    # LIKE clause
    LikeClauseSegment=Sequence(
        "LIKE",
        Ref("TableReferenceSegment"),
        Bracketed(
            Ref("LikeOptionsSegment"),
            optional=True,
        ),
    ),
    # DESCRIPTOR(col1, col2, ...) - used in windowing TVFs and PTFs
    DescriptorSegment=Sequence(
        "DESCRIPTOR",
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
            ),
        ),
    ),
    # TABLE t [PARTITION BY ...] [ORDER BY ...] - table argument for TVFs/PTFs
    TableArgSegment=Sequence(
        "TABLE",
        OneOf(
            Bracketed(Ref("SelectableGrammar")),
            Ref("TableReferenceSegment"),
        ),
        Sequence(
            "PARTITION",
            "BY",
            OneOf(
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                ),
                Ref("ColumnReferenceSegment"),
            ),
            optional=True,
        ),
        Sequence(
            "ORDER",
            "BY",
            OneOf(
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            OneOf("ASC", "DESC", optional=True),
                            Sequence(
                                "NULLS",
                                OneOf("FIRST", "LAST"),
                                optional=True,
                            ),
                        ),
                    ),
                ),
                Sequence(
                    Ref("ColumnReferenceSegment"),
                    OneOf("ASC", "DESC", optional=True),
                    Sequence(
                        "NULLS",
                        OneOf("FIRST", "LAST"),
                        optional=True,
                    ),
                ),
            ),
            optional=True,
        ),
    ),
    # MODEL m - model argument for ML_PREDICT
    ModelArgSegment=Sequence(
        "MODEL",
        Ref("ObjectReferenceSegment"),
    ),
    # Named argument for Process Table Functions: param => value
    FlinkNamedArgumentSegment=Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("RightArrowSegment"),
        OneOf(
            Ref("TableArgSegment"),
            Ref("ModelArgSegment"),
            Ref("DescriptorSegment"),
            Ref("ExpressionSegment"),
        ),
    ),
    # Row pattern quantifiers for MATCH_RECOGNIZE.
    FlinkPatternQuantifierGrammar=Sequence(
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
        allow_gaps=False,
    ),
    FlinkPatternTermGrammar=OneOf(
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("FlinkPatternQuantifierGrammar", optional=True),
            allow_gaps=False,
        ),
        Bracketed(
            Ref("FlinkPatternSegment"),
        ),
    ),
)


class FlinkArrayExpressionSegment(BaseSegment):
    """An `ARRAY[...]` constructor for FlinkSQL."""

    type = "array_expression"
    match_grammar = Sequence(
        "ARRAY",
        Bracketed(
            Delimited(
                Ref("BaseExpressionElementGrammar"),
                optional=True,
            ),
            bracket_type="square",
        ),
    )


class FunctionNameSegment(ansi.FunctionNameSegment):
    """A function name that supports Flink backtick-quoted identifiers."""

    match_grammar = Sequence(
        AnyNumberOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Ref("DotSegment"),
            ),
            terminators=[Ref("BracketedSegment")],
        ),
        OneOf(
            Ref("FunctionNameIdentifierSegment"),
            Ref("QuotedIdentifierSegment"),
            Ref("BackQuotedIdentifierSegment"),
            terminators=[Ref("BracketedSegment")],
        ),
        allow_gaps=False,
    )


flink_dialect.replace(
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BackQuotedIdentifierSegment"),
    ),
    FunctionNameSegment=FunctionNameSegment,
    # Extended to support named, TABLE, MODEL, and DESCRIPTOR arguments in TVFs/PTFs
    FunctionContentsExpressionGrammar=OneOf(
        Ref("FlinkNamedArgumentSegment"),
        Ref("TableArgSegment"),
        Ref("ModelArgSegment"),
        Ref("DescriptorSegment"),
        Ref("ExpressionSegment"),
    ),
    # Flink supports ARRAY[...] and MAP[...] constructors.
    ArrayExpressionSegment=FlinkArrayExpressionSegment,
    Expression_D_Potential_Select_Statement_Without_Brackets=flink_dialect.get_grammar(
        "Expression_D_Potential_Select_Statement_Without_Brackets"
    ).copy(
        insert=[Ref("FlinkMapExpressionSegment")],
        before=Ref("ColumnReferenceSegment"),
    ),
    # Flink supports LATERAL TABLE(...) in a FROM clause.
    PreTableFunctionKeywordsGrammar=OneOf("LATERAL"),
    # Flink supports MATCH_RECOGNIZE as a join-like clause.
    JoinLikeClauseGrammar=Sequence(
        Ref("MatchRecognizeClauseSegment"),
        Ref("AliasExpressionSegment", optional=True),
    ),
)


class TemporalQuerySegment(BaseSegment):
    """A segment for `FOR SYSTEM_TIME AS OF`."""

    type = "temporal_query"
    match_grammar = Sequence(
        "FOR",
        "SYSTEM_TIME",
        "AS",
        "OF",
        Ref("ExpressionSegment"),
    )


class CreateViewStatementSegment(ansi.CreateViewStatementSegment):
    """A `CREATE VIEW` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/create/#create-view
    """

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Column list (optional)
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
            ),
            optional=True,
        ),
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
        "AS",
        Ref("SelectableGrammar"),
    )


class IntervalExpressionSegment(ansi.IntervalExpressionSegment):
    """An interval expression segment for FlinkSQL.

    Flink supports precision for datetime units, e.g., SECOND(3).
    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/queries/window-tvf/
    """

    type = "interval_expression"

    # Datetime unit with optional precision, e.g., SECOND or SECOND(3)
    _datetime_unit_with_precision = Sequence(
        Ref("DatetimeUnitSegment"),
        Bracketed(
            Ref("NumericLiteralSegment"),
            optional=True,
        ),
    )

    match_grammar = Sequence(
        "INTERVAL",
        OneOf(
            # The Numeric Version
            Sequence(
                Ref("NumericLiteralSegment"),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    _datetime_unit_with_precision,
                ),
            ),
            # The String version
            Ref("QuotedLiteralSegment"),
            # Combine version (most common in Flink)
            Sequence(
                Ref("QuotedLiteralSegment"),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    _datetime_unit_with_precision,
                ),
            ),
        ),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement for FlinkSQL."""

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns definition with FlinkSQL-specific elements
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            # Physical column definition
                            Ref("ColumnDefinitionSegment"),
                            # Metadata column definition
                            Ref("MetadataColumnDefinitionSegment"),
                            # Computed column definition
                            Ref("ComputedColumnDefinitionSegment"),
                            # Watermark definition
                            Ref("WatermarkDefinitionSegment"),
                            # Table constraint
                            Ref("FlinkTableConstraintSegment"),
                        ),
                    ),
                ),
                # Table comment
                Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
                # Partition definition
                Ref("PartitionDefinitionSegment", optional=True),
                # Distribution definition
                Ref("DistributionDefinitionSegment", optional=True),
                # Connector options
                Ref("CreateTableConnectorOptionsSegment", optional=True),
                # LIKE clause
                Ref("LikeClauseSegment", optional=True),
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Ref("LikeClauseSegment"),
        ),
    )


class CreateCatalogStatementSegment(BaseSegment):
    """A `CREATE CATALOG` statement."""

    type = "create_catalog_statement"
    match_grammar = Sequence(
        "CREATE",
        "CATALOG",
        Ref("NakedIdentifierSegment"),
        Ref("CreateTableConnectorOptionsSegment"),
    )


class CreateDatabaseStatementSegment(BaseSegment):
    """A `CREATE DATABASE` statement for FlinkSQL."""

    type = "create_database_statement"
    match_grammar = Sequence(
        "CREATE",
        "DATABASE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
        Ref("CreateTableConnectorOptionsSegment", optional=True),
    )


class DescribeStatementSegment(BaseSegment):
    """A `DESCRIBE` statement for FlinkSQL."""

    type = "describe_statement"
    match_grammar = Sequence(
        "DESCRIBE",
        Ref("TableReferenceSegment"),
    )


class ExplainStatementSegment(ansi.ExplainStatementSegment):
    """An `EXPLAIN` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/explain/
    """

    type = "explain_statement"
    match_grammar = Sequence(
        "EXPLAIN",
        Delimited(
            OneOf(
                "ESTIMATED_COST",
                "CHANGELOG_MODE",
                "JSON_EXECUTION_PLAN",
                "PLAN_ADVICE",
            ),
            optional=True,
        ),
        Sequence("PLAN", "FOR", optional=True),
        OneOf(
            Ref("SelectableGrammar"),
            Ref("InsertStatementSegment"),
            Ref("ExecuteStatementSetSegment"),
        ),
    )


class CreateModelStatementSegment(ansi.CreateModelStatementSegment):
    """A `CREATE MODEL` statement for FlinkSQL (Flink 2.0+).

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/create/#create-model
    """

    type = "create_model_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("TemporaryGrammar", optional=True),
        "MODEL",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Sequence(
            "INPUT",
            Bracketed(
                Delimited(
                    Ref("ColumnDefinitionSegment"),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "OUTPUT",
            Bracketed(
                Delimited(
                    Ref("ColumnDefinitionSegment"),
                ),
            ),
            optional=True,
        ),
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
        Ref("CreateTableConnectorOptionsSegment", optional=True),
        Sequence(
            "AS",
            OptionallyBracketed(Ref("SelectableGrammar")),
            optional=True,
        ),
    )


class AlterModelStatementSegment(BaseSegment):
    """An `ALTER MODEL` statement for FlinkSQL (Flink 2.0+).

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/alter/#alter-model
    """

    type = "alter_model_statement"
    match_grammar = Sequence(
        "ALTER",
        "MODEL",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("ObjectReferenceSegment")),
            Sequence("SET", Ref("FlinkOptionsListGrammar")),
            Sequence("RESET", Ref("FlinkOptionKeyListGrammar")),
        ),
    )


class DropModelStatementSegment(ansi.DropModelStatementSegment):
    """A `DROP MODEL` statement for FlinkSQL (Flink 2.0+).

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/drop/#drop-model
    """

    type = "drop_model_statement"
    match_grammar = Sequence(
        "DROP",
        Ref("TemporaryGrammar", optional=True),
        "MODEL",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
    )


class CreateConnectionStatementSegment(BaseSegment):
    """A `CREATE CONNECTION` statement for FlinkSQL (Flink 2.2+ FLIP-529)."""

    type = "create_connection_statement"
    match_grammar = Sequence(
        "CREATE",
        OneOf(
            Sequence("TEMPORARY", "SYSTEM"),
            "TEMPORARY",
            optional=True,
        ),
        "CONNECTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
        Ref("CreateTableConnectorOptionsSegment"),
    )


class AlterConnectionStatementSegment(BaseSegment):
    """An `ALTER CONNECTION` statement for FlinkSQL (Flink 2.2+ FLIP-529)."""

    type = "alter_connection_statement"
    match_grammar = Sequence(
        "ALTER",
        "CONNECTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("ObjectReferenceSegment")),
            Sequence("SET", Ref("FlinkOptionsListGrammar")),
            Sequence("RESET", Ref("FlinkOptionKeyListGrammar")),
        ),
    )


class DropConnectionStatementSegment(BaseSegment):
    """A `DROP CONNECTION` statement for FlinkSQL (Flink 2.2+ FLIP-529)."""

    type = "drop_connection_statement"
    match_grammar = Sequence(
        "DROP",
        OneOf(
            Sequence("TEMPORARY", "SYSTEM"),
            "TEMPORARY",
            optional=True,
        ),
        "CONNECTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
    )


class CreateMaterializedTableStatementSegment(BaseSegment):
    """A `CREATE [OR ALTER] MATERIALIZED TABLE` statement for FlinkSQL (Flink 2.0+).

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/materialized-table/statements/
    """

    type = "create_materialized_table_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "MATERIALIZED",
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            Bracketed(
                Delimited(
                    OneOf(
                        Ref("ColumnDefinitionSegment"),
                        Ref("MetadataColumnDefinitionSegment"),
                        Ref("ComputedColumnDefinitionSegment"),
                        Ref("WatermarkDefinitionSegment"),
                        Ref("FlinkTableConstraintSegment"),
                    ),
                ),
            ),
            Bracketed(
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
            ),
            optional=True,
        ),
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
        AnySetOf(
            Ref("DistributionDefinitionSegment"),
            Ref("PartitionDefinitionSegment"),
            optional=True,
        ),
        Ref("CreateTableConnectorOptionsSegment", optional=True),
        AnySetOf(
            Ref("FlinkStartModeClauseGrammar"),
            Ref("FlinkFreshnessClauseGrammar"),
            Ref("FlinkRefreshModeClauseGrammar"),
            optional=True,
        ),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
    )


class AlterMaterializedTableStatementSegment(BaseSegment):
    """An `ALTER MATERIALIZED TABLE` statement for FlinkSQL (Flink 2.0–2.3).

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/materialized-table/statements/#alter-materialized-table
    """

    type = "alter_materialized_table_statement"
    match_grammar = Sequence(
        "ALTER",
        "MATERIALIZED",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            "SUSPEND",
            Sequence(
                "RESUME",
                Ref("CreateTableConnectorOptionsSegment", optional=True),
            ),
            Sequence(
                "REFRESH",
                Sequence(
                    "PARTITION",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("SingleIdentifierGrammar"),
                                Ref("EqualsSegment"),
                                Ref("LiteralGrammar"),
                            ),
                        ),
                    ),
                    optional=True,
                ),
            ),
            Sequence(
                "SET",
                OneOf(
                    Ref("FlinkFreshnessClauseGrammar"),
                    Ref("FlinkRefreshModeClauseGrammar"),
                    Ref("FlinkStartModeClauseGrammar"),
                    Ref("FlinkOptionsListGrammar"),
                ),
            ),
            Sequence("RESET", Ref("FlinkOptionKeyListGrammar")),
            Sequence("RENAME", "TO", Ref("TableReferenceSegment")),
            Sequence(
                Ref("FlinkStartModeClauseGrammar", optional=True),
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            Sequence(
                "ADD",
                OneOf(
                    Ref("FlinkMaterializedAlterDistributionGrammar"),
                    Bracketed(
                        Delimited(
                            Ref("FlinkMaterializedAlterSchemaComponentGrammar"),
                        ),
                    ),
                    Ref("FlinkMaterializedAlterSchemaComponentGrammar"),
                ),
            ),
            Sequence(
                "MODIFY",
                OneOf(
                    Ref("FlinkMaterializedAlterDistributionGrammar"),
                    Bracketed(
                        Delimited(
                            Ref("FlinkMaterializedAlterSchemaComponentGrammar"),
                        ),
                    ),
                    Ref("FlinkMaterializedAlterSchemaComponentGrammar"),
                ),
            ),
            Sequence(
                "DROP",
                OneOf(
                    Sequence("PRIMARY", "KEY"),
                    Sequence("CONSTRAINT", Ref("SingleIdentifierGrammar")),
                    "DISTRIBUTION",
                    "WATERMARK",
                    Bracketed(
                        Delimited(
                            Ref("ColumnReferenceSegment"),
                        ),
                    ),
                    Ref("ColumnReferenceSegment"),
                ),
            ),
        ),
    )


class DropMaterializedTableStatementSegment(BaseSegment):
    """A `DROP MATERIALIZED TABLE` statement for FlinkSQL (Flink 2.0+).

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/materialized-table/statements/#drop-materialized-table
    """

    type = "drop_materialized_table_statement"
    match_grammar = Sequence(
        "DROP",
        "MATERIALIZED",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
    )


class ShowStatementsSegment(BaseSegment):
    """A `SHOW` statement for FlinkSQL."""

    type = "show_statement"
    match_grammar = Sequence(
        "SHOW",
        OneOf(
            "CATALOGS",
            "DATABASES",
            "TABLES",
            "VIEWS",
            "FUNCTIONS",
            "MODULES",
            "JARS",
            "JOBS",
        ),
    )


class SetStatementSegment(BaseSegment):
    """A FlinkSQL SET statement."""

    type = "set_statement"
    match_grammar = Sequence(
        "SET",
        OneOf(
            Sequence(
                Ref("FlinkPropertyNameSegment"),
                Ref("EqualsSegment"),
                Ref("FlinkPropertyValueSegment"),
            ),
            Sequence(
                Ref("QuotedLiteralSegment"),
                Ref("EqualsSegment"),
                Ref("QuotedLiteralSegment"),
            ),
            optional=True,
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            # FlinkSQL-specific statements
            Ref("AlterConnectionStatementSegment"),
            Ref("AlterMaterializedTableStatementSegment"),
            Ref("AlterModelStatementSegment"),
            Ref("CreateCatalogStatementSegment"),
            Ref("CreateConnectionStatementSegment"),
            Ref("CreateDatabaseStatementSegment"),
            Ref("CreateFunctionStatementSegment"),
            Ref("CreateMaterializedTableStatementSegment"),
            Ref("DescribeStatementSegment"),
            Ref("DropConnectionStatementSegment"),
            Ref("DropMaterializedTableStatementSegment"),
            Ref("ExecuteStatementSetSegment"),
            Ref("ShowStatementsSegment"),
            Ref("SetStatementSegment"),
        ],
    )


class UseStatementSegment(ansi.UseStatementSegment):
    """A FlinkSQL USE statement."""

    type = "use_statement"
    match_grammar = OneOf(
        # USE CATALOG catalog_name (needs to be first to prevent CATALOG being
        # parsed as database name)
        Sequence(
            "USE",
            "CATALOG",
            Ref("ObjectReferenceSegment"),
        ),
        # USE [catalog_name.]database_name
        Sequence(
            "USE",
            Ref("ObjectReferenceSegment"),
        ),
    )


class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/create/#create-function
    """

    type = "create_function_statement"
    match_grammar = Sequence(
        "CREATE",
        OneOf(
            Sequence("TEMPORARY", "SYSTEM"),
            "TEMPORARY",
            optional=True,
        ),
        "FUNCTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        "AS",
        OneOf(
            Ref("QuotedLiteralSegment"),
            Ref("ObjectReferenceSegment"),
        ),
        Sequence(
            "LANGUAGE",
            OneOf("JAVA", "SCALA", "PYTHON"),
            optional=True,
        ),
        Sequence(
            "USING",
            Delimited(
                Sequence(
                    OneOf("JAR", "ARTIFACT"),
                    Ref("QuotedLiteralSegment"),
                ),
            ),
            optional=True,
        ),
        Ref("CreateTableConnectorOptionsSegment", optional=True),
    )


class ExecuteStatementSetSegment(BaseSegment):
    """An `EXECUTE STATEMENT SET` block for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/insert/#insert-into-multiple-tables
    """

    type = "execute_statement_set"
    match_grammar = OneOf(
        Sequence(
            "EXECUTE",
            "STATEMENT",
            "SET",
            "BEGIN",
            Indent,
            AnyNumberOf(
                Sequence(
                    Ref("InsertStatementSegment"),
                    Ref("DelimiterGrammar"),
                ),
                min_times=1,
            ),
            Dedent,
            "END",
        ),
        Sequence(
            "BEGIN",
            "STATEMENT",
            "SET",
            Ref("DelimiterGrammar"),
            Indent,
            AnyNumberOf(
                Sequence(
                    Ref("InsertStatementSegment"),
                    Ref("DelimiterGrammar"),
                ),
                min_times=1,
            ),
            Dedent,
            "END",
        ),
    )


class FlinkMapExpressionSegment(BaseSegment):
    """A `MAP[...]` constructor for FlinkSQL."""

    type = "map_expression"
    match_grammar = Sequence(
        "MAP",
        Bracketed(
            Delimited(
                Ref("BaseExpressionElementGrammar"),
                optional=True,
            ),
            bracket_type="square",
        ),
    )


class FlinkPatternSegment(BaseSegment):
    """A row pattern for FlinkSQL `MATCH_RECOGNIZE`."""

    type = "pattern_expression"
    match_grammar = Delimited(
        AnyNumberOf(
            Ref("FlinkPatternTermGrammar"),
            min_times=1,
        ),
        delimiter=Ref("BitwiseOrSegment"),
    )


class MatchRecognizeClauseSegment(BaseSegment):
    """A `MATCH_RECOGNIZE` clause for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/queries/match_recognize/
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
                        Ref("ExpressionSegment"),
                        Ref("AliasExpressionSegment"),
                    ),
                ),
                optional=True,
            ),
            Sequence(
                "ONE",
                "ROW",
                "PER",
                "MATCH",
                optional=True,
            ),
            Sequence(
                "AFTER",
                "MATCH",
                "SKIP",
                OneOf(
                    Sequence("PAST", "LAST", "ROW"),
                    Sequence("TO", "NEXT", "ROW"),
                    Sequence("TO", "LAST", Ref("SingleIdentifierGrammar")),
                    Sequence("TO", "FIRST", Ref("SingleIdentifierGrammar")),
                ),
                optional=True,
            ),
            "PATTERN",
            Bracketed(
                Ref("FlinkPatternSegment"),
            ),
            Sequence(
                "WITHIN",
                Ref("IntervalExpressionSegment"),
                optional=True,
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


class RowDataTypeSegment(BaseSegment):
    """A ROW data type for FlinkSQL."""

    type = "row_data_type"
    match_grammar = Sequence(
        "ROW",
        OneOf(
            # ROW<...> syntax
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("SingleIdentifierGrammar"),  # field name
                        Ref("DatatypeSegment"),  # field type
                        Sequence("NOT", "NULL", optional=True),
                        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
                    ),
                ),
                bracket_type="angle",
                bracket_pairs_set="angle_bracket_pairs",
            ),
            # ROW(...) syntax
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("SingleIdentifierGrammar"),  # field name
                        Ref("DatatypeSegment"),  # field type
                        Sequence("NOT", "NULL", optional=True),
                        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
                    ),
                ),
                bracket_type="round",
            ),
        ),
    )


class DatatypeSegment(ansi.DatatypeSegment):
    """Enhanced data type segment for FlinkSQL."""

    type = "data_type"
    match_grammar = OneOf(
        # FlinkSQL ROW data type
        Ref("RowDataTypeSegment"),
        # Array data types
        Sequence(
            "ARRAY",
            Bracketed(
                Sequence(
                    Ref("DatatypeSegment"),
                    Sequence("NOT", "NULL", optional=True),
                ),
                bracket_type="angle",
                bracket_pairs_set="angle_bracket_pairs",
            ),
        ),
        # Map data types
        Sequence(
            "MAP",
            Bracketed(
                Sequence(
                    Ref("DatatypeSegment"),  # key type
                    Ref("CommaSegment"),
                    Ref("DatatypeSegment"),  # value type
                    Sequence("NOT", "NULL", optional=True),
                ),
                bracket_type="angle",
                bracket_pairs_set="angle_bracket_pairs",
            ),
        ),
        # Multiset data types
        Sequence(
            "MULTISET",
            Bracketed(
                Sequence(
                    Ref("DatatypeSegment"),
                    Sequence("NOT", "NULL", optional=True),
                ),
                bracket_type="angle",
                bracket_pairs_set="angle_bracket_pairs",
            ),
        ),
        # Include standard ANSI data types by inheriting parent match_grammar
        ansi.DatatypeSegment.match_grammar,
    )
