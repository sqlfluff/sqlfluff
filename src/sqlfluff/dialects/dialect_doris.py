"""The Apache Doris dialect.

This dialect extends MySQL grammar with specific Apache Doris syntax features.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    Bracketed,
    CodeSegment,
    Delimited,
    Matchable,
    MultiStringParser,
    OneOf,
    OptionallyBracketed,
    Ref,
    SegmentGenerator,
    Sequence,
)
from sqlfluff.dialects import dialect_mysql as mysql
from sqlfluff.dialects.dialect_doris_keywords import (
    doris_reserved_keywords,
    doris_unreserved_keywords,
)

mysql_dialect = load_raw_dialect("mysql")
doris_dialect = mysql_dialect.copy_as(
    "doris",
    formatted_name="Apache Doris",
    docstring="""**Default Casing**: ``lowercase``

    **Quotes**: String Literals: ``''``, ``"``,
    Identifiers: |back_quotes|.

    The dialect for `Apache Doris <https://doris.apache.org/>`_.""",
)
doris_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", doris_unreserved_keywords
)
doris_dialect.sets("reserved_keywords").clear()
doris_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", doris_reserved_keywords
)


# Add the engine types set for Doris
doris_dialect.sets("engine_types").update(
    ["olap", "mysql", "elasticsearch", "hive", "hudi", "iceberg", "jdbc", "broker"]
)


doris_dialect.add(
    EngineTypeSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("engine_types"),
            CodeSegment,
            type="engine_type",
        )
    ),
)


class ColumnDefinitionSegment(mysql.ColumnDefinitionSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE.

    Doris-specific version that supports aggregation functions like
    MAX, MIN, REPLACE, SUM.
    """

    match_grammar = mysql.ColumnDefinitionSegment.match_grammar.copy(
        insert=[
            OneOf(
                "MAX",
                "MIN",
                "REPLACE",
                "SUM",
                "BITMAP_UNION",
                "HLL_UNION",
                "QUANTILE_UNION",
                optional=True,
            ),
        ]
    )


class CreateTableStatementSegment(mysql.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    Doris-specific version that handles:
    - Different ENGINE types
    - Key types (DUPLICATE, AGGREGATE, UNIQUE)
    - Cluster by clause
    - Specific partition syntax
    - Distribution syntax
    - Rollup definitions
    - Specific table properties
    - CREATE TABLE ... AS SELECT (CTAS)
    - CREATE TABLE ... LIKE
    """

    type = "create_table_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref.keyword("TEMPORARY", optional=True),
        Ref.keyword("EXTERNAL", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Standard column definitions
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                            Ref("IndexDefinitionSegment"),
                        ),
                    )
                ),
                # Doris specific
                Sequence(
                    "ENGINE",
                    Ref("EqualsSegment"),
                    Ref("EngineTypeSegment"),
                    optional=True,
                ),
                # Key type
                Sequence(
                    OneOf(
                        Sequence("DUPLICATE", "KEY"),
                        Sequence("AGGREGATE", "KEY"),
                        Sequence("UNIQUE", "KEY"),
                    ),
                    Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    # Cluster by clause
                    Sequence(
                        "CLUSTER",
                        "BY",
                        Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                        optional=True,
                    ),
                    optional=True,
                ),
                Ref("CommentClauseSegment", optional=True),
                # Partitioning
                Ref("PartitionSegment", optional=True),
                # Distribution
                Ref("DistributionSegment", optional=True),
                # Rollup definitions
                Ref("RollupSegment", optional=True),
                # Properties
                Sequence(
                    "PROPERTIES",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("QuotedLiteralSegment"),
                                Ref("EqualsSegment"),
                                Ref("QuotedLiteralSegment"),
                            )
                        )
                    ),
                    optional=True,
                ),
            ),
            # Create table like
            Sequence("LIKE", Ref("TableReferenceSegment")),
            # Create table as select (CTAS)
            Sequence(
                # Optional ENGINE clause
                Sequence(
                    "ENGINE",
                    Ref("EqualsSegment"),
                    Ref("EngineTypeSegment"),
                    optional=True,
                ),
                # Optional COMMENT clause
                Ref("CommentClauseSegment", optional=True),
                # Optional properties before AS SELECT
                Sequence(
                    "PROPERTIES",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("QuotedLiteralSegment"),
                                Ref("EqualsSegment"),
                                Ref("QuotedLiteralSegment"),
                            )
                        )
                    ),
                    optional=True,
                ),
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
        ),
    )


class ColumnConstraintSegment(mysql.ColumnConstraintSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    match_grammar: Matchable = OneOf(
        mysql.ColumnConstraintSegment.match_grammar,
        Sequence("AS", Ref("ExpressionSegment")),
        Sequence("GENERATED", "ALWAYS", "AS", Bracketed(Ref("ExpressionSegment"))),
    )


class PartitionSegment(BaseSegment):
    """A partition segment supporting Doris specific syntax.

    Supports:
    1. Auto partitioning (AUTO PARTITION BY RANGE)
    2. Manual range partitioning (PARTITION BY RANGE)
    3. List partitioning (PARTITION BY LIST)
    """

    type = "partition_segment"
    match_grammar = OneOf(
        # Auto partitioning
        Sequence(
            "AUTO",
            "PARTITION",
            "BY",
            "RANGE",
            Bracketed(Ref("FunctionSegment")),
            Bracketed(),  # Empty partition list for auto partitioning
        ),
        # Manual partitioning
        Sequence(
            "PARTITION",
            "BY",
            OneOf(
                # Manual range partitioning
                Sequence(
                    "RANGE",
                    Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    Bracketed(
                        Delimited(
                            OneOf(
                                Ref("RangePartitionDefinitionSegment"),
                                Ref("RangePartitionIntervalSegment"),
                            )
                        )
                    ),
                ),
                # List partitioning
                Sequence(
                    "LIST",
                    Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    Bracketed(Delimited(Ref("ListPartitionDefinitionSegment"))),
                ),
            ),
        ),
    )


class RangePartitionDefinitionSegment(BaseSegment):
    """Range partition definition with VALUES LESS THAN or VALUES range."""

    type = "range_partition_definition"
    match_grammar = Sequence(
        "PARTITION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "VALUES",
        OneOf(
            Sequence(
                "LESS",
                "THAN",
                OneOf(
                    "MAXVALUE",
                    Bracketed(Delimited(Ref("LiteralGrammar"))),
                ),
            ),
            Sequence(
                Bracketed(
                    Bracketed(Delimited(Ref("LiteralGrammar"))),
                    ",",
                    Bracketed(Delimited(Ref("LiteralGrammar"))),
                )
            ),
        ),
        # Partition properties
        Sequence(
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("QuotedLiteralSegment"),
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    )
                )
            ),
            optional=True,
        ),
    )


class RangePartitionIntervalSegment(BaseSegment):
    """Range partition definition with FROM TO INTERVAL syntax."""

    type = "range_partition_interval"
    match_grammar = Sequence(
        "FROM",
        Bracketed(Ref("QuotedLiteralSegment")),
        "TO",
        Bracketed(Ref("QuotedLiteralSegment")),
        "INTERVAL",
        Ref("NumericLiteralSegment"),
        OneOf("YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND"),
    )


class ListPartitionDefinitionSegment(BaseSegment):
    """List partition definition with VALUES IN syntax."""

    type = "list_partition_definition"
    match_grammar = Sequence(
        "PARTITION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "VALUES",
        "IN",
        Bracketed(
            Delimited(
                OneOf(
                    Bracketed(Delimited(Ref("LiteralGrammar"))),
                    Ref("LiteralGrammar"),
                )
            )
        ),
    )


class DistributionSegment(BaseSegment):
    """A distribution segment supporting both hash and random distribution."""

    type = "distribution_segment"
    match_grammar = Sequence(
        "DISTRIBUTED",
        "BY",
        OneOf(
            Sequence(
                "HASH",
                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                Sequence(
                    "BUCKETS",
                    OneOf(
                        Ref("NumericLiteralSegment"),
                        "AUTO",
                    ),
                    optional=True,
                ),
            ),
            Sequence(
                "RANDOM",
                Sequence(
                    "BUCKETS",
                    OneOf(
                        Ref("NumericLiteralSegment"),
                        "AUTO",
                    ),
                    optional=True,
                ),
            ),
        ),
    )


class RollupSegment(BaseSegment):
    """Rollup definition for Doris tables."""

    type = "rollup_segment"
    match_grammar = Sequence(
        "ROLLUP",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("ObjectReferenceSegment"),
                    Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    Sequence(
                        "DUPLICATE",
                        "KEY",
                        Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                        optional=True,
                    ),
                )
            )
        ),
    )


class IndexDefinitionSegment(BaseSegment):
    """Index definition specific to Doris."""

    type = "index_definition"
    match_grammar = Sequence(
        "INDEX",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
        Sequence("USING", OneOf("INVERTED", "BITMAP", "BLOOM_FILTER"), optional=True),
        Sequence(
            "PROPERTIES",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("QuotedLiteralSegment"),
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    )
                )
            ),
            optional=True,
        ),
        Sequence("COMMENT", Ref("QuotedLiteralSegment"), optional=True),
    )


class DropTableStatementSegment(BaseSegment):
    """A `DROP TABLE` statement.

    Doris-specific version that supports:
    - IF EXISTS clause
    - Database-qualified table names
    - FORCE option
    """

    type = "drop_table_statement"
    match_grammar = Sequence(
        "DROP",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),  # Single table reference, not delimited
        Sequence("FORCE", optional=True),  # Optional FORCE keyword
    )


class InsertStatementSegment(BaseSegment):
    """A `INSERT` statement.

    Doris-specific version that supports:
    - PARTITION clause
    - WITH LABEL clause
    - DEFAULT values
    """

    type = "insert_statement"
    match_grammar = Sequence(
        "INSERT",
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        # Optional PARTITION clause
        Sequence(
            "PARTITION",
            Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
            optional=True,
        ),
        # Optional WITH LABEL clause
        Sequence(
            "WITH",
            "LABEL",
            Ref("SingleIdentifierGrammar"),
            optional=True,
        ),
        # Optional column list
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        # VALUES or SELECT
        OneOf(
            Ref("ValuesClauseSegment"),
            Ref("SelectableGrammar"),
        ),
    )
