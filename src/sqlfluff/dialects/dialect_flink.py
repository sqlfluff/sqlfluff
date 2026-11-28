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
# A word flink lists as unreserved that is reserved, in its own list or in the
# ANSI keywords it adds to, stays reserved, as it always behaved.
flink_reserved = set(RESERVED_KEYWORDS)
flink_dialect.declare_keyword_sets(
    reserved=flink_reserved,
    reserved_mode="add",
    unreserved=set(UNRESERVED_KEYWORDS)
    - flink_reserved
    - set(ansi_dialect.sets("reserved_keywords")),
    unimplemented=[],
    future_reserved=[],
    future_reserved_mode="replace",
    unspecified_parent_keywords="unreserved",
)

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
        "SQL_TSI_FRAC_SECOND",
        "SQL_TSI_SECOND",
        "SQL_TSI_MINUTE",
        "SQL_TSI_HOUR",
        "SQL_TSI_DAY",
        "SQL_TSI_WEEK",
        "SQL_TSI_MONTH",
        "SQL_TSI_QUARTER",
        "SQL_TSI_YEAR",
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
flink_dialect.sets("date_part_function_name").update(
    [
        "TIMESTAMPADD",
        "TIMESTAMPDIFF",
    ]
)

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
    # Row pattern quantifier used by MATCH_RECOGNIZE
    QuestionMarkSegment=StringParser("?", SymbolSegment, type="question_mark"),
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
    # Connector option list: ('key' = 'value', ...)
    FlinkOptionsListGrammar=Bracketed(
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
    # Option key list for RESET ('key1', 'key2', ...)
    FlinkOptionKeyListGrammar=Bracketed(
        Delimited(
            Ref("QuotedLiteralSegment"),
        ),
    ),
    # Partition spec: PARTITION (col1 = val1, col2 = val2)
    FlinkPartitionSpecGrammar=Sequence(
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
    ),
    # Column position modifier in ALTER TABLE ADD/MODIFY
    FlinkAlterColumnPositionGrammar=OneOf(
        "FIRST",
        Sequence("AFTER", Ref("ColumnReferenceSegment")),
    ),
    # Schema component in ALTER TABLE ADD/MODIFY
    FlinkAlterSchemaComponentGrammar=OneOf(
        Sequence(
            Ref("MetadataColumnDefinitionSegment"),
            Ref("FlinkAlterColumnPositionGrammar", optional=True),
        ),
        Sequence(
            Ref("ComputedColumnDefinitionSegment"),
            Ref("FlinkAlterColumnPositionGrammar", optional=True),
        ),
        Sequence(
            Ref("ColumnDefinitionSegment"),
            Ref("FlinkAlterColumnPositionGrammar", optional=True),
        ),
        Ref("WatermarkDefinitionSegment"),
        Ref("FlinkTableConstraintSegment"),
    ),
    # Shared distribution strategy for CREATE TABLE and ALTER TABLE DISTRIBUTION
    FlinkDistributionStrategyGrammar=OneOf(
        # BY [HASH|RANGE] (columns) [INTO n BUCKET[S]]
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
        # INTO n BUCKET[S]
        Sequence(
            "INTO",
            Ref("NumericLiteralSegment"),
            OneOf("BUCKETS", "BUCKET"),
        ),
    ),
    # Distribution clause for ALTER TABLE ADD/MODIFY DISTRIBUTION
    FlinkAlterDistributionGrammar=Sequence(
        "DISTRIBUTION",
        Ref("FlinkDistributionStrategyGrammar"),
    ),
    # Connector options for CREATE TABLE
    CreateTableConnectorOptionsSegment=Sequence(
        "WITH",
        Ref("FlinkOptionsListGrammar"),
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
    DistributionDefinitionSegment=Sequence(
        "DISTRIBUTED",
        Ref("FlinkDistributionStrategyGrammar"),
    ),
    # LIKE options (Flink uses space-separated options; accept optional commas too)
    LikeOptionsSegment=AnyNumberOf(
        Sequence(
            OneOf(
                # INCLUDING/EXCLUDING with ALL/CONSTRAINTS/DISTRIBUTION/METADATA/PARTITIONS
                Sequence(
                    OneOf("INCLUDING", "EXCLUDING"),
                    OneOf(
                        "ALL",
                        "CONSTRAINTS",
                        "DISTRIBUTION",
                        "METADATA",
                        "PARTITIONS",
                    ),
                ),
                # INCLUDING/EXCLUDING/OVERWRITING with GENERATED/OPTIONS/WATERMARKS
                Sequence(
                    OneOf("INCLUDING", "EXCLUDING", "OVERWRITING"),
                    OneOf("GENERATED", "OPTIONS", "WATERMARKS"),
                ),
            ),
            Ref("CommaSegment", optional=True),
        ),
        min_times=1,
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
    # DESCRIPTOR(col) - used in windowing TVFs
    DescriptorSegment=Sequence(
        "DESCRIPTOR",
        Bracketed(
            Ref("ColumnReferenceSegment"),
        ),
    ),
    # TABLE t - table argument for TVFs like TUMBLE, HOP
    TableArgSegment=Sequence(
        "TABLE",
        Ref("TableReferenceSegment"),
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
    # JSON_VALUE / JSON_QUERY / JSON_EXISTS optional clauses
    FlinkJsonOnEmptyErrorBehaviorGrammar=OneOf(
        "ERROR",
        "NULL",
        "TRUE",
        "FALSE",
        "UNKNOWN",
        Sequence("EMPTY", OneOf("ARRAY", "OBJECT")),
        Sequence("DEFAULT", Ref("ExpressionSegment")),
    ),
    FlinkJsonFunctionContentsGrammar=Sequence(
        Ref("ExpressionSegment"),
        Ref("CommaSegment"),
        Ref(
            "ExpressionSegment",
            terminators=[
                "RETURNING",
                "WITH",
                "WITHOUT",
                "ERROR",
                "NULL",
                "TRUE",
                "FALSE",
                "UNKNOWN",
                "EMPTY",
                "DEFAULT",
            ],
        ),
        AnySetOf(
            Sequence(
                "RETURNING",
                Ref("DatatypeSegment"),
            ),
            Sequence(
                OneOf("WITH", "WITHOUT"),
                OneOf("CONDITIONAL", "UNCONDITIONAL", optional=True),
                Ref.keyword("ARRAY", optional=True),
                "WRAPPER",
            ),
            Sequence(
                Ref("FlinkJsonOnEmptyErrorBehaviorGrammar"),
                "ON",
                "EMPTY",
            ),
            Sequence(
                Ref("FlinkJsonOnEmptyErrorBehaviorGrammar"),
                "ON",
                "ERROR",
            ),
            min_times=1,
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
    # Support inline column PRIMARY KEY NOT ENFORCED
    NotEnforcedGrammar=Sequence(Ref.keyword("NOT", optional=True), "ENFORCED"),
    # Support TIMESTAMP(p) WITH LOCAL TIME ZONE and TIME(p) WITHOUT TIME ZONE
    TimeWithTZGrammar=Sequence(
        OneOf("TIME", "TIMESTAMP"),
        Ref("BracketedArguments", optional=True),
        Sequence(
            OneOf("WITH", "WITHOUT"),
            Ref.keyword("LOCAL", optional=True),
            "TIME",
            "ZONE",
            optional=True,
        ),
    ),
    # Support IS [NOT] JSON [VALUE | SCALAR | ARRAY | OBJECT]
    IsClauseGrammar=ansi_dialect.get_grammar("IsClauseGrammar").copy(
        insert=[
            Sequence(
                "JSON",
                OneOf("VALUE", "SCALAR", "ARRAY", "OBJECT", optional=True),
            ),
        ],
    ),
    # Extended to support TABLE and DESCRIPTOR arguments in TVFs
    FunctionContentsExpressionGrammar=OneOf(
        Ref("TableArgSegment"),
        Ref("DescriptorSegment"),
        Ref("ExpressionSegment"),
    ),
    # Support temporal FLOOR/CEIL(ts TO unit) and JSON_VALUE/JSON_QUERY/JSON_EXISTS
    FunctionContentsGrammar=ansi_dialect.get_grammar("FunctionContentsGrammar").copy(
        insert=[
            Sequence(
                Ref("ExpressionSegment"),
                "TO",
                Ref("DatetimeUnitSegment"),
            ),
            Ref("FlinkJsonFunctionContentsGrammar"),
        ],
    ),
    # Flink supports ARRAY[...], MAP[...], and MULTISET[...] constructors.
    ArrayExpressionSegment=FlinkArrayExpressionSegment,
    Expression_D_Potential_Select_Statement_Without_Brackets=flink_dialect.get_grammar(
        "Expression_D_Potential_Select_Statement_Without_Brackets"
    ).copy(
        insert=[
            Ref("FlinkMapExpressionSegment"),
            Ref("FlinkMultisetExpressionSegment"),
        ],
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

    # Datetime unit with optional precision, e.g., SECOND or SECOND(3),
    # optionally followed by TO unit for compound intervals (e.g. DAY TO SECOND).
    _datetime_unit_with_precision = Sequence(
        Ref("DatetimeUnitSegment"),
        Bracketed(
            Ref("NumericLiteralSegment"),
            optional=True,
        ),
    )

    _interval_unit = Sequence(
        _datetime_unit_with_precision,
        Sequence("TO", _datetime_unit_with_precision, optional=True),
    )

    match_grammar = Sequence(
        "INTERVAL",
        OneOf(
            # The Numeric Version
            Sequence(
                Ref("NumericLiteralSegment"),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    _interval_unit,
                ),
            ),
            # The String version
            Ref("QuotedLiteralSegment"),
            # Combine version (most common in Flink)
            Sequence(
                Ref("QuotedLiteralSegment"),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    _interval_unit,
                ),
            ),
        ),
    )


class TableExpressionSegment(ansi.TableExpressionSegment):
    """The main table expression e.g. within a FROM clause.

    Override from ANSI to allow optional `WITH ORDINALITY` on table functions
    such as `UNNEST(...) WITH ORDINALITY`.
    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/queries/joins/#array-expansion
    """

    match_grammar = OneOf(
        Ref("ValuesClauseSegment"),
        Ref("BareFunctionSegment"),
        Sequence(
            Ref("FunctionSegment"),
            Sequence("WITH", "ORDINALITY", optional=True),
        ),
        Ref("TableReferenceSegment"),
        # Nested Selects
        Bracketed(Ref("SelectableGrammar")),
        Bracketed(Ref("MergeStatementSegment")),
    )


class InsertStatementSegment(ansi.InsertStatementSegment):
    """An `INSERT` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/insert/
    """

    match_grammar = Sequence(
        Ref.keyword("EXECUTE", optional=True),
        "INSERT",
        OneOf("INTO", "OVERWRITE"),
        Ref("TableReferenceSegment"),
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
        OneOf(
            Ref(
                "SelectableGrammar",
                terminators=[Sequence("ON", "CONFLICT")],
            ),
            Sequence(
                Ref("BracketedColumnReferenceListGrammar"),
                Ref(
                    "SelectableGrammar",
                    terminators=[Sequence("ON", "CONFLICT")],
                ),
            ),
            Ref("DefaultValuesGrammar"),
        ),
        Sequence(
            "ON",
            "CONFLICT",
            "DO",
            OneOf("ERROR", "NOTHING", "DEDUPLICATE"),
            optional=True,
        ),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` or `[CREATE OR] REPLACE TABLE` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/create/#create-table
    """

    match_grammar = Sequence(
        OneOf(
            Sequence(
                "CREATE",
                Sequence("OR", "REPLACE", optional=True),
            ),
            "REPLACE",
        ),
        Ref("TemporaryGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns definition with FlinkSQL-specific elements
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
            # Bare column identifier list for CTAS/RTAS column reordering
            Bracketed(
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
            ),
            optional=True,
        ),
        # Table comment
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
        # Partition and distribution definitions (either order)
        AnySetOf(
            Ref("PartitionDefinitionSegment"),
            Ref("DistributionDefinitionSegment"),
            optional=True,
        ),
        # Connector options
        Ref("CreateTableConnectorOptionsSegment", optional=True),
        OneOf(
            # LIKE clause
            Ref("LikeClauseSegment"),
            # Create/Replace Table AS SELECT syntax
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            optional=True,
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
    """An `EXPLAIN` statement for FlinkSQL."""

    type = "explain_statement"
    match_grammar = Sequence(
        "EXPLAIN",
        Sequence("PLAN", "FOR", optional=True),
        Ref("SelectableGrammar"),
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


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """An `ALTER TABLE` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/alter/#alter-table
    """

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # RENAME TO new_table_name (before RENAME col TO new_col)
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            # RENAME old_column_name TO new_column_name
            Sequence(
                "RENAME",
                Ref("ColumnReferenceSegment"),
                "TO",
                Ref("ColumnReferenceSegment"),
            ),
            # SET ('k' = 'v', ...)
            Sequence(
                "SET",
                Ref("FlinkOptionsListGrammar"),
            ),
            # RESET ('k1', 'k2', ...)
            Sequence(
                "RESET",
                Ref("FlinkOptionKeyListGrammar"),
            ),
            # ADD partition / distribution / schema component(s)
            Sequence(
                "ADD",
                OneOf(
                    Sequence(
                        Ref("IfNotExistsGrammar", optional=True),
                        AnyNumberOf(
                            Sequence(
                                Ref("FlinkPartitionSpecGrammar"),
                                Ref(
                                    "CreateTableConnectorOptionsSegment", optional=True
                                ),
                            ),
                            min_times=1,
                        ),
                    ),
                    Ref("FlinkAlterDistributionGrammar"),
                    Bracketed(
                        Delimited(
                            Ref("FlinkAlterSchemaComponentGrammar"),
                        ),
                    ),
                    Ref("FlinkAlterSchemaComponentGrammar"),
                ),
            ),
            # MODIFY distribution / schema component(s)
            Sequence(
                "MODIFY",
                OneOf(
                    Ref("FlinkAlterDistributionGrammar"),
                    Bracketed(
                        Delimited(
                            Ref("FlinkAlterSchemaComponentGrammar"),
                        ),
                    ),
                    Ref("FlinkAlterSchemaComponentGrammar"),
                ),
            ),
            # DROP partition(s) / primary key / constraint / distribution /
            # watermark / column(s)
            Sequence(
                "DROP",
                OneOf(
                    Sequence(
                        Ref("IfExistsGrammar", optional=True),
                        Delimited(
                            Ref("FlinkPartitionSpecGrammar"),
                        ),
                    ),
                    Sequence("PRIMARY", "KEY"),
                    Sequence("CONSTRAINT", Ref("SingleIdentifierGrammar")),
                    "DISTRIBUTION",
                    "WATERMARK",
                    Bracketed(
                        Delimited(
                            Ref("ColumnReferenceSegment"),
                        ),
                    ),
                    Sequence(
                        Ref.keyword("COLUMN", optional=True),
                        Ref("IfExistsGrammar", optional=True),
                        Ref("ColumnReferenceSegment"),
                    ),
                ),
            ),
        ),
    )


class AlterCatalogStatementSegment(BaseSegment):
    """An `ALTER CATALOG` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/alter/#alter-catalog
    """

    type = "alter_catalog_statement"
    match_grammar = Sequence(
        "ALTER",
        "CATALOG",
        Ref("SingleIdentifierGrammar"),
        OneOf(
            Sequence("SET", Ref("FlinkOptionsListGrammar")),
            Sequence("RESET", Ref("FlinkOptionKeyListGrammar")),
            Sequence("COMMENT", Ref("QuotedLiteralSegment")),
        ),
    )


class AlterDatabaseStatementSegment(BaseSegment):
    """An `ALTER DATABASE` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/alter/#alter-database
    """

    type = "alter_database_statement"
    match_grammar = Sequence(
        "ALTER",
        "DATABASE",
        Ref("ObjectReferenceSegment"),
        "SET",
        Ref("FlinkOptionsListGrammar"),
    )


class AlterFunctionStatementSegment(BaseSegment):
    """An `ALTER FUNCTION` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/alter/#alter-function
    """

    type = "alter_function_statement"
    match_grammar = Sequence(
        "ALTER",
        OneOf(
            Sequence("TEMPORARY", "SYSTEM"),
            "TEMPORARY",
            optional=True,
        ),
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        "AS",
        OneOf(
            Ref("QuotedLiteralSegment"),
            Ref("ObjectReferenceSegment"),
        ),
        Sequence(
            "LANGUAGE",
            OneOf("JAVA", "SCALA", "PYTHON", "SQL"),
            optional=True,
        ),
    )


class AlterViewStatementSegment(BaseSegment):
    """An `ALTER VIEW` statement for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/alter/#alter-view
    """

    type = "alter_view_statement"
    match_grammar = Sequence(
        "ALTER",
        "VIEW",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("TableReferenceSegment")),
            Sequence("AS", Ref("SelectableGrammar")),
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            # FlinkSQL-specific statements
            Ref("AlterCatalogStatementSegment"),
            Ref("AlterDatabaseStatementSegment"),
            Ref("AlterFunctionStatementSegment"),
            Ref("AlterViewStatementSegment"),
            Ref("CreateCatalogStatementSegment"),
            Ref("CreateDatabaseStatementSegment"),
            Ref("CreateFunctionStatementSegment"),
            Ref("DescribeStatementSegment"),
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


class FlinkMultisetExpressionSegment(BaseSegment):
    """A `MULTISET[...]` constructor for FlinkSQL."""

    type = "multiset_expression"
    match_grammar = Sequence(
        "MULTISET",
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
                        Sequence(
                            Ref.keyword("COMMENT", optional=True),
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
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
                        Sequence(
                            Ref.keyword("COMMENT", optional=True),
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                    ),
                ),
                bracket_type="round",
            ),
        ),
    )


class StructuredDataTypeSegment(BaseSegment):
    """A `STRUCTURED<...>` data type for FlinkSQL.

    https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/types/#structured
    """

    type = "structured_data_type"
    match_grammar = Sequence(
        "STRUCTURED",
        Bracketed(
            Sequence(
                Ref("QuotedLiteralSegment"),
                Sequence(
                    Ref("CommaSegment"),
                    Delimited(
                        Sequence(
                            Ref("SingleIdentifierGrammar"),
                            Ref("DatatypeSegment"),
                            Sequence("NOT", "NULL", optional=True),
                            Sequence(
                                Ref.keyword("COMMENT", optional=True),
                                Ref("QuotedLiteralSegment"),
                                optional=True,
                            ),
                        ),
                    ),
                    optional=True,
                ),
            ),
            bracket_type="angle",
            bracket_pairs_set="angle_bracket_pairs",
        ),
    )


class DatatypeSegment(ansi.DatatypeSegment):
    """Enhanced data type segment for FlinkSQL."""

    type = "data_type"
    match_grammar = Sequence(
        OneOf(
            # FlinkSQL ROW data type
            Ref("RowDataTypeSegment"),
            # FlinkSQL STRUCTURED data type
            Ref("StructuredDataTypeSegment"),
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
                        Sequence("NOT", "NULL", optional=True),
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
        ),
        # Postfix collection modifiers: e.g. STRING ARRAY, INT NOT NULL ARRAY,
        # STRING MULTISET
        AnyNumberOf(
            Sequence(
                Sequence("NOT", "NULL", optional=True),
                OneOf("ARRAY", "MULTISET"),
            ),
            optional=True,
        ),
    )
