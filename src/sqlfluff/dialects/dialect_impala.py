"""The Impala dialect."""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    BinaryOperatorSegment,
    Bracketed,
    Delimited,
    OneOf,
    Ref,
    Sequence,
    StringParser,
)
from sqlfluff.dialects import dialect_hive as hive
from sqlfluff.dialects.dialect_impala_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

hive_dialect = load_raw_dialect("hive")
impala_dialect = hive_dialect.copy_as(
    "impala",
    formatted_name="Apache Impala",
    docstring="The dialect for Apache `Impala <https://impala.apache.org/>`_.",
)

impala_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
impala_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)

impala_dialect.replace(
    DivideSegment=OneOf(
        StringParser("DIV", BinaryOperatorSegment),
        StringParser("/", BinaryOperatorSegment),
    )
)


class StatementSegment(hive.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    match_grammar = hive.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CreateTableAsSelectStatementSegment"),
            Ref("ComputeStatsStatementSegment"),
            Ref("InsertStatementSegment"),
        ]
    )


class ComputeStatsStatementSegment(BaseSegment):
    """A `COMPUTE STATS statement.

    Full Apache Impala `COMPUTE STATS` reference here:
    https://impala.apache.org/docs/build/html/topics/impala_compute_stats.html
    """

    type = "compute_stats_statement"

    match_grammar = Sequence(
        "COMPUTE",
        OneOf(
            Sequence("STATS", Ref("TableReferenceSegment")),
            Sequence(
                "INCREMENTAL",
                "STATS",
                Ref("TableReferenceSegment"),
                Ref("PartitionSpecGrammar", optional=True),
            ),
        ),
    )


class CreateTableStatementSegment(hive.CreateTableStatementSegment):
    """A `CREATE_TABLE` statement.

    Full Apache Impala `CREATE TABLE` reference here:
    https://impala.apache.org/docs/build/html/topics/impala_create_table.html
    """

    type = "create_table_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref.keyword("EXTERNAL", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(
                OneOf(
                    Ref("TableConstraintSegment", optional=True),
                    Sequence(
                        Ref("ColumnDefinitionSegment"),
                        Ref("CommentGrammar", optional=True),
                    ),
                ),
                bracket_pairs_set="angle_bracket_pairs",
            ),
            optional=True,
        ),
        Sequence(
            "PARTITIONED",
            "BY",
            Bracketed(
                Delimited(
                    Sequence(
                        OneOf(
                            Ref("ColumnDefinitionSegment"),
                            Ref("SingleIdentifierGrammar"),
                        ),
                        Ref("CommentGrammar", optional=True),
                    ),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "SORT",
            "BY",
            Bracketed(Delimited(Sequence(Ref("ColumnReferenceSegment")))),
            optional=True,
        ),
        Ref("CommentGrammar", optional=True),
        Ref("RowFormatClauseSegment", optional=True),
        Ref("SerdePropertiesGrammar", optional=True),
        Ref("StoredAsGrammar", optional=True),
        Ref("LocationGrammar", optional=True),
        Sequence(
            OneOf(
                Sequence(
                    "CACHED",
                    "IN",
                    Delimited(Ref("PoolNameReferenceSegment")),
                    Sequence(
                        "WITH",
                        "REPLICATION",
                        "=",
                        Ref("NumericLiteralSegment"),
                        optional=True,
                    ),
                ),
                Ref.keyword("UNCACHED"),
            ),
            optional=True,
        ),
        Ref("TablePropertiesGrammar", optional=True),
    )


class CreateTableAsSelectStatementSegment(BaseSegment):
    """A `CREATE TABLE ... AS SELECT ...` statement.

    Full Apache Impala reference here:
    https://impala.apache.org/docs/build/html/topics/impala_create_table.html

    Unlike Hive, `AS SELECT ...` cannot be appended to any other SELECT statement,
    so this is implemented as a separate segment.
    """

    type = "create_table_as_select_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref.keyword("EXTERNAL", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Sequence(
            "PARTITIONED",
            "BY",
            Bracketed(
                Delimited(
                    Sequence(
                        OneOf(
                            Ref("ColumnDefinitionSegment"),
                            Ref("SingleIdentifierGrammar"),
                        ),
                        Ref("CommentGrammar", optional=True),
                    ),
                ),
            ),
            optional=True,
        ),
        Sequence(
            "SORT",
            "BY",
            Bracketed(Delimited(Sequence(Ref("ColumnReferenceSegment")))),
            optional=True,
        ),
        Ref("CommentGrammar", optional=True),
        Ref("RowFormatClauseSegment", optional=True),
        Ref("SerdePropertiesGrammar", optional=True),
        Ref("StoredAsGrammar", optional=True),
        Ref("LocationGrammar", optional=True),
        Sequence(
            OneOf(
                Sequence(
                    "CACHED",
                    "IN",
                    Delimited(Ref("PoolNameReferenceSegment")),
                    Sequence(
                        "WITH",
                        "REPLICATION",
                        "=",
                        Ref("NumericLiteralSegment"),
                        optional=True,
                    ),
                ),
                Ref.keyword("UNCACHED"),
            ),
            optional=True,
        ),
        Ref("TablePropertiesGrammar", optional=True),
        "AS",
        Ref("SelectableGrammar"),
    )


class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    Full Apache Impala `INSERT` reference here:
    https://impala.apache.org/docs/build/html/topics/impala_insert.html
    """

    type = "insert_statement"

    match_grammar = Sequence(
        "INSERT",
        OneOf(
            Sequence(
                "OVERWRITE",
                Ref.keyword("TABLE", optional=True),
                Ref("TableReferenceSegment"),
                Ref("PartitionSpecGrammar", optional=True),
                Bracketed(
                    OneOf("SHUFFLE", "NOSHUFFLE"), bracket_type="square", optional=True
                ),
                Ref("IfNotExistsGrammar", optional=True),
                Ref("SelectableGrammar"),
            ),
            Sequence(
                "INTO",
                Ref.keyword("TABLE", optional=True),
                Ref("TableReferenceSegment"),
                Sequence(
                    Bracketed(Delimited(Sequence(Ref("ColumnReferenceSegment")))),
                    optional=True,
                ),
                Ref("PartitionSpecGrammar", optional=True),
                Bracketed(
                    OneOf("SHUFFLE", "NOSHUFFLE"), bracket_type="square", optional=True
                ),
                OneOf(
                    Ref("SelectableGrammar"),
                    Ref("ValuesClauseSegment"),
                ),
            ),
        ),
    )
