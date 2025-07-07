"""The FlinkSQL dialect.

Inherits from ANSI SQL.
FlinkSQL is based on ANSI SQL standard but includes additional features
for stream processing and table operations.

Based on:
https://nightlies.apache.org/flink/flink-docs-release-1.18/docs/dev/table/sql/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Delimited,
    IdentifierSegment,
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

.. _`Flink SQL`: https://nightlies.apache.org/flink/flink-docs-release-1.18/docs/dev/table/sql/  # noqa: E501
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
            segment_kwargs={"trim_start": "--"},
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
        # Support for string literals with single quotes
        RegexLexer(
            "single_quote",
            r"'([^'\\]|\\.)*'",
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r"'((?:[^'\\]|\\.)*)'", 1),
                "escape_replacements": [(r"''", "'"), (r"\\'", "'")],
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
        Ref("NakedIdentifierSegment"),  # column name
        "AS",
        Ref("ExpressionSegment"),  # computed expression
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
    ),
    # Metadata column definition
    MetadataColumnDefinitionSegment=Sequence(
        Ref("NakedIdentifierSegment"),  # column name
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
)

flink_dialect.replace(
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BackQuotedIdentifierSegment"),
    ),
)


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement for FlinkSQL."""

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
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


class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            # FlinkSQL-specific statements
            Ref("CreateCatalogStatementSegment"),
            Ref("CreateDatabaseStatementSegment"),
            Ref("DescribeStatementSegment"),
            Ref("ShowStatementsSegment"),
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
                        Ref("NakedIdentifierSegment"),  # field name
                        Ref("DatatypeSegment"),  # field type
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
                        Ref("NakedIdentifierSegment"),  # field name
                        Ref("DatatypeSegment"),  # field type
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
                Ref("DatatypeSegment"),
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
                ),
                bracket_type="angle",
                bracket_pairs_set="angle_bracket_pairs",
            ),
        ),
        # Multiset data types
        Sequence(
            "MULTISET",
            Bracketed(
                Ref("DatatypeSegment"),
                bracket_type="angle",
                bracket_pairs_set="angle_bracket_pairs",
            ),
        ),
        # Include standard ANSI data types by inheriting parent match_grammar
        ansi.DatatypeSegment.match_grammar,
    )
