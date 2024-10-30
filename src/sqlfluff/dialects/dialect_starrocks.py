"""The StarRocks dialect.

This dialect extends MySQL grammar with specific StarRocks syntax features.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnySetOf,
    BaseSegment,
    Bracketed,
    Delimited,
    OneOf,
    OptionallyBracketed,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_mysql as mysql
from sqlfluff.dialects.dialect_starrocks_keywords import (
    starrocks_reserved_keywords,
    starrocks_unreserved_keywords,
)

mysql_dialect = load_raw_dialect("mysql")
starrocks_dialect = mysql_dialect.copy_as(
    "starrocks",
    formatted_name="StarRocks",
    docstring="""**Default Casing**: ``lowercase``

    **Quotes**: String Literals: ``''``, ``"``,
    Identifiers: |back_quotes|.

    The dialect for `StarRocks <https://www.starrocks.io/>`_.""",
)
starrocks_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", starrocks_unreserved_keywords
)
starrocks_dialect.sets("reserved_keywords").clear()
starrocks_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", starrocks_reserved_keywords
)

# Set the table properties specific to StarRocks
# These are used in PROPERTIES clause
starrocks_dialect.sets("table_properties").update(
    [
        "storage_medium",
        "storage_cooldown_time",
        "storage_cooldown_ttl",
        "replication_num",
        "bloom_filter_columns",
        "colocate_with",
        "dynamic_partition.enable",
        "dynamic_partition.time_unit",
        "dynamic_partition.start",
        "dynamic_partition.end",
        "dynamic_partition.prefix",
        "dynamic_partition.buckets",
        "storage_volume",
        "datacache.enable",
        "datacache.partition_duration",
        "fast_schema_evolution"
    ]
)

class CreateTableStatementSegment(mysql.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    StarRocks-specific version that handles:
    - Different ENGINE types
    - Storage and bucketing options
    - Specific partition syntax
    - Specific table properties
    """

    type = "create_table_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref.keyword("EXTERNAL", optional=True),
        Ref.keyword("TEMPORARY", optional=True),
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
                # StarRocks specific
                Sequence(
                    "ENGINE",
                    Ref("EqualsSegment", optional=True),
                    OneOf(
                        "olap",
                        "mysql",
                        "elasticsearch",
                        "hive",
                        "hudi",
                        "iceberg",
                        "jdbc"
                    ),
                    optional=True
                ),
                # Key type
                Sequence(
                    OneOf(
                        Sequence("AGGREGATE", "KEY"),
                        Sequence("UNIQUE", "KEY"),
                        Sequence("PRIMARY", "KEY"),
                        Sequence("DUPLICATE", "KEY"),
                    ),
                    Bracketed(
                        Delimited(
                            Ref("ColumnReferenceSegment")
                        )
                    ),
                    optional=True
                ),
                Ref("CommentClauseSegment", optional=True),
                # Partitioning
                Ref("PartitionSegment", optional=True),
                # Distribution
                Ref("DistributionSegment", optional=True),
                # Order by
                Sequence(
                    "ORDER",
                    "BY",
                    Bracketed(
                        Delimited(
                            Ref("ColumnReferenceSegment")
                        )
                    ),
                    optional=True
                ),
                Sequence(
                    "PROPERTIES",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("QuotedLiteralSegment"),
                                Ref("EqualsSegment"),
                                Ref("QuotedLiteralSegment")
                            )
                        )
                    ),
                    optional=True
                ),
            ),
            # Create table like
            Sequence(
                "LIKE",
                Ref("TableReferenceSegment")
            ),
            # Create table as
            Sequence(
                Ref.keyword("AS", optional=True),
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
        ),
    )

class PartitionSegment(BaseSegment):
    """A partition segment supporting StarRocks specific syntax.
    
    Supports three types of partitioning:
    1. Range partitioning (PARTITION BY RANGE)
    2. Expression partitioning using time functions (date_trunc/time_slice)
    3. Expression partitioning using column expressions
    """
    
    type = "partition_segment"
    match_grammar = Sequence(
        "PARTITION",
        "BY",
        OneOf(
            # Range partitioning
            Sequence(
                "RANGE",
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment")
                    )
                ),
                OneOf(
                    # Fixed partitions
                    Bracketed(
                        Delimited(
                            Sequence(
                                "PARTITION",
                                Ref("ObjectReferenceSegment"),
                                "VALUES",
                                OneOf(
                                    # LESS THAN syntax
                                    Sequence(
                                        "LESS",
                                        "THAN",
                                        OneOf(
                                            "MAXVALUE",
                                            Bracketed(
                                                Delimited(
                                                    Ref("LiteralGrammar")
                                                )
                                            )
                                        )
                                    ),
                                    # Fixed range syntax
                                    Sequence(
                                        "[",
                                        Bracketed(
                                            Delimited(
                                                Ref("LiteralGrammar")
                                            )
                                        ),
                                        ",",
                                        Bracketed(
                                            Delimited(
                                                Ref("LiteralGrammar")
                                            )
                                        ),
                                        ")"
                                    )
                                )
                            )
                        )
                    ),
                    # Dynamic partitions
                    Bracketed(
                        Sequence(
                            "START",
                            Bracketed(Ref("QuotedLiteralSegment")),
                            "END",
                            Bracketed(Ref("QuotedLiteralSegment")),
                            "EVERY",
                            Bracketed(
                                OneOf(
                                    Ref("QuotedLiteralSegment"),
                                    Sequence(
                                        "INTERVAL",
                                        Ref("NumericLiteralSegment"),
                                        OneOf(
                                            "YEAR",
                                            "MONTH",
                                            "DAY",
                                            "HOUR"
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ),
            # Expression partitioning - time function expressions
            OneOf(
                # date_trunc function
                Sequence(
                    "date_trunc",
                    Bracketed(
                        Delimited(
                            OneOf(
                                Ref("QuotedLiteralSegment"),  # time unit
                                Ref("ColumnReferenceSegment")  # partition column
                            )
                        )
                    )
                ),
                # time_slice function
                Sequence(
                    "time_slice",
                    Bracketed(
                        Delimited(
                            Ref("ColumnReferenceSegment"),  # partition column
                            Sequence(
                                "INTERVAL",
                                Ref("NumericLiteralSegment"),
                                OneOf(
                                    "YEAR",
                                    "MONTH", 
                                    "DAY",
                                    "HOUR"
                                )
                            ),
                            # Optional boundary parameter always defaults to floor
                            Ref("QuotedLiteralSegment", optional=True)  # boundary
                        )
                    )
                )
            ),
            # Expression partitioning - column expressions
            Bracketed(
                Delimited(
                    Ref("ColumnReferenceSegment")
                )
            )
        )
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
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment")
                    )
                ),
                Sequence(
                    "BUCKETS",
                    Ref("NumericLiteralSegment"),
                    optional=True
                )
            ),
            Sequence(
                "RANDOM",
                Sequence(
                    "BUCKETS",
                    Ref("NumericLiteralSegment"),
                    optional=True
                )
            )
        )
    )

class IndexDefinitionSegment(BaseSegment):
    """Bitmap index definition specific to StarRocks."""

    type = "index_definition"
    match_grammar = Sequence(
        "INDEX",
        Ref("IndexReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment")
            )
        ),
        Sequence(
            "USING",
            "BITMAP",
            optional=True
        ),
        Sequence(
            "COMMENT",
            Ref("QuotedLiteralSegment"),
            optional=True
        )
    )

class CreateRoutineLoadStatementSegment(BaseSegment):
    """A `CREATE ROUTINE LOAD` statement for StarRocks.

    Handles continuous data loading from Kafka into StarRocks, supporting CSV, JSON, and Avro formats.
    """

    type = "create_routine_load_statement"
    match_grammar = Sequence(
        "CREATE",
        "ROUTINE",
        "LOAD",
        Sequence(
            Ref("DatabaseReferenceSegment"),
            Ref("DotSegment"),
            optional=True
        ),
        Ref("ObjectReferenceSegment"),  # job_name
        "ON",
        Ref("TableReferenceSegment"),  # table_name
        # Load Properties section
        AnySetOf(
            # Column separator for CSV
            Sequence(
                "COLUMNS",
                "TERMINATED",
                "BY",
                Ref("QuotedLiteralSegment")
            ),
            # Row separator for CSV
            Sequence(
                "ROWS",
                "TERMINATED",
                "BY",
                Ref("QuotedLiteralSegment")
            ),
            # Column mapping
            Sequence(
                "COLUMNS",
                Bracketed(
                    Delimited(
                        OneOf(
                            # Simple column reference with optional backticks
                            Ref("QuotedIdentifierSegment"),
                            Ref("NakedIdentifierSegment"),
                            # Column with expression
                            Sequence(
                                OneOf(
                                    Ref("QuotedIdentifierSegment"),
                                    Ref("NakedIdentifierSegment")
                                ),
                                Ref("EqualsSegment"),
                                Ref("ExpressionSegment")
                            )
                        )
                    )
                ),
            ),
            # Filter conditions
            Sequence(
                "WHERE",
                Ref("ExpressionSegment")
            ),
            # Target partitions
            Sequence(
                "PARTITION",
                Bracketed(
                    Delimited(
                        Ref("ObjectReferenceSegment")
                    )
                )
            ),
            # Temporary partitions
            Sequence(
                "TEMPORARY",
                "PARTITION",
                Bracketed(
                    Delimited(
                        Ref("ObjectReferenceSegment")
                    )
                )
            ),
            optional=True
        ),
        # Job Properties section
        Sequence(
            "PROPERTIES",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("QuotedLiteralSegment"),  # property key
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment")   # property value
                    )
                )
            ),
            optional=True
        ),
        # Data Source section
        "FROM",
        "KAFKA",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("QuotedLiteralSegment"),  # property key
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment")   # property value
                )
            )
        )
    )

class CreateRoutineLoadPropertiesSegment(BaseSegment):
    """Properties segment for CREATE ROUTINE LOAD statement."""

    type = "routine_load_properties"

    # Set of valid property keys
    valid_properties = [
        "desired_concurrent_number",
        "max_batch_interval",
        "max_batch_rows",
        "max_error_number",
        "max_filter_ratio",
        "strict_mode",
        "timezone",
        "format",
        "trim_space",
        "enclose",
        "escape",
        "strip_outer_array",
        "jsonpaths",
        "json_root",
        "task_consume_second",
        "task_timeout_second",
        "log_rejected_record_num"
    ]

class CreateRoutineLoadDataSourcePropertiesSegment(BaseSegment):
    """Data source properties segment for CREATE ROUTINE LOAD statement."""

    type = "routine_load_data_source_properties"

    # Set of valid data source property keys
    valid_properties = [
        "kafka_broker_list",
        "kafka_topic",
        "kafka_partitions",
        "kafka_offsets",
        "property.kafka_default_offsets",
        "confluent.schema.registry.url",
        "property.security.protocol",
        "property.ssl.ca.location",
        "property.ssl.certificate.location",
        "property.ssl.key.location",
        "property.ssl.key.password",
        "property.sasl.mechanism",
        "property.sasl.username",
        "property.sasl.password"
    ]

"""Grammar for STOP ROUTINE LOAD statement in StarRocks."""

class StopRoutineLoadStatementSegment(BaseSegment):
    """A `STOP ROUTINE LOAD` statement.
    
    Stops a running routine load job.
    
    STOP ROUTINE LOAD FOR [db_name.]<job_name>
    """
    
    type = "stop_routine_load_statement"
    match_grammar = Sequence(
        "STOP",
        "ROUTINE",
        "LOAD",
        "FOR",
        OneOf(
            # db_name.job_name format
            Sequence(
                Ref("DatabaseReferenceSegment"),
                Ref("DotSegment"),
                Ref("ObjectReferenceSegment")
            ),
            # job_name only format
            Ref("ObjectReferenceSegment")
        )
    )

class PauseRoutineLoadStatementSegment(BaseSegment):
    """A `PAUSE ROUTINE LOAD` statement.
    
    Pauses a running routine load job.
    """
    
    type = "pause_routine_load_statement"
    match_grammar = Sequence(
        "PAUSE",
        "ROUTINE",
        "LOAD",
        "FOR",
        OneOf(
            Sequence(
                Ref("DatabaseNameSegment"),
                Ref("DotSegment"),
                Ref("ObjectReferenceSegment")
            ),
            Ref("ObjectReferenceSegment")
        )
    )

class ResumeRoutineLoadStatementSegment(BaseSegment):
    """A `RESUME ROUTINE LOAD` statement.

    Resumes a paused routine load job.
    """

    type = "resume_routine_load_statement"
    match_grammar = Sequence(
        "RESUME",
        "ROUTINE",
        "LOAD",
        "FOR",
        OneOf(
            Sequence(
                Ref("DatabaseNameSegment"),
                Ref("DotSegment"),
                Ref("ObjectReferenceSegment")
            ),
            Ref("ObjectReferenceSegment")
        )
    )

class StatementSegment(mysql.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = mysql.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CreateRoutineLoadStatementSegment"),
            Ref("StopRoutineLoadStatementSegment"),
            Ref("PauseRoutineLoadStatementSegment"),
            Ref("ResumeRoutineLoadStatementSegment")
            ]
    )