"""The Greenplum dialect.

Greenplum (http://www.greenplum.org/) is a Massively Parallel Postgres,
so we base this dialect on Postgres.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects import dialect_postgres as postgres
from sqlfluff.core.parser import (
    AnyNumberOf,
    Bracketed,
    Delimited,
    OneOf,
    Ref,
    Sequence,
)

postgres_dialect = load_raw_dialect("postgres")

greenplum_dialect = postgres_dialect.copy_as("greenplum")

greenplum_dialect.sets("reserved_keywords").update(
    ["DISTRIBUTED", "RANDOMLY", "REPLICATED"]
)


class CreateTableStatementSegment(postgres.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    As specified in
    https://docs.vmware.com/en/VMware-Tanzu-Greenplum/6/greenplum-database/GUID-ref_guide-sql_commands-CREATE_TABLE.html
    This is overriden from Postgres to add the `DISTRIBUTED` clause.
    """

    match_grammar = Sequence(
        "CREATE",
        OneOf(
            Sequence(
                OneOf("GLOBAL", "LOCAL", optional=True),
                Ref("TemporaryGrammar", optional=True),
            ),
            "UNLOGGED",
            optional=True,
        ),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Sequence(
                                Ref("ColumnReferenceSegment"),
                                Ref("DatatypeSegment"),
                                AnyNumberOf(
                                    # A single COLLATE segment can come before or after
                                    # constraint segments
                                    OneOf(
                                        Ref("ColumnConstraintSegment"),
                                        Sequence(
                                            "COLLATE",
                                            Ref("CollationReferenceSegment"),
                                        ),
                                    ),
                                ),
                            ),
                            Ref("TableConstraintSegment"),
                            Sequence(
                                "LIKE",
                                Ref("TableReferenceSegment"),
                                AnyNumberOf(Ref("LikeOptionSegment"), optional=True),
                            ),
                        ),
                    )
                ),
                Sequence(
                    "INHERITS",
                    Bracketed(Delimited(Ref("TableReferenceSegment"))),
                    optional=True,
                ),
            ),
            # Create OF syntax:
            Sequence(
                "OF",
                Ref("ParameterNameSegment"),
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            Sequence("WITH", "OPTIONS", optional=True),
                            AnyNumberOf(Ref("ColumnConstraintSegment")),
                        ),
                        Ref("TableConstraintSegment"),
                    ),
                    optional=True,
                ),
            ),
            # Create PARTITION OF syntax
            Sequence(
                "PARTITION",
                "OF",
                Ref("TableReferenceSegment"),
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            Sequence("WITH", "OPTIONS", optional=True),
                            AnyNumberOf(Ref("ColumnConstraintSegment")),
                        ),
                        Ref("TableConstraintSegment"),
                    ),
                    optional=True,
                ),
                OneOf(
                    Sequence("FOR", "VALUES", Ref("PartitionBoundSpecSegment")),
                    "DEFAULT",
                ),
            ),
        ),
        AnyNumberOf(
            Sequence(
                "PARTITION",
                "BY",
                OneOf("RANGE", "LIST", "HASH"),
                Bracketed(
                    AnyNumberOf(
                        Delimited(
                            Sequence(
                                OneOf(
                                    Ref("ColumnReferenceSegment"),
                                    Ref("FunctionSegment"),
                                ),
                                AnyNumberOf(
                                    Sequence(
                                        "COLLATE",
                                        Ref("CollationReferenceSegment"),
                                        optional=True,
                                    ),
                                    Ref("ParameterNameSegment", optional=True),
                                ),
                            ),
                        )
                    )
                ),
            ),
            Sequence("USING", Ref("ParameterNameSegment")),
            Sequence(
                "WITH",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ParameterNameSegment"),
                            Sequence(
                                Ref("EqualsSegment"),
                                Ref("LiteralGrammar"),
                                optional=True,
                            ),
                        ),
                    )
                ),
            ),
            Sequence(
                "ON",
                "COMMIT",
                OneOf(Sequence("PRESERVE", "ROWS"), Sequence("DELETE", "ROWS"), "DROP"),
            ),
            Sequence("TABLESPACE", Ref("TablespaceReferenceSegment")),
            Sequence(
                "DISTRIBUTED",
                OneOf(
                    "RANDOMLY",
                    "REPLICATED",
                    Sequence("BY", Bracketed(Ref("ColumnReferenceSegment"))),
                ),
            ),
        ),
    )
