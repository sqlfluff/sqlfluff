"""The Materialize dialect.

This is based on postgres dialect, since it was initially based off of Postgres.
We should monitor in future and see if it should be rebased off of ANSI
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    Anything,
    BaseSegment,
    Bracketed,
    Delimited,
    KeywordSegment,
    MultiStringParser,
    OneOf,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_materialize_keywords import (
    materialize_reserved_keywords,
    materialize_unreserved_keywords,
)

postgres_dialect = load_raw_dialect("postgres")

materialize_dialect = postgres_dialect.copy_as("materialize")
materialize_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", materialize_unreserved_keywords
)

materialize_dialect.sets("reserved_keywords").clear()
materialize_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", materialize_reserved_keywords
)


class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("AlterOwnerStatementSegment"),
            Ref("AlterConnectionRotateKeys"),
            Ref("AlterDefaultPrivilegesStatementSegment"),
            Ref("AlterIndexStatementSegment"),
            Ref("AlterRenameStatementSegment"),
            Ref("AlterSecretStatementSegment"),
            Ref("AlterSetClusterStatementSegment"),
            Ref("AlterSourceSinkSizeStatementSegment"),
            Ref("CloseStatementSegment"),
            Ref("CopyToStatementSegment"),
            Ref("CopyFromStatementSegment"),
            Ref("CreateClusterStatementSegment"),
            Ref("CreateClusterReplicaStatementSegment"),
            Ref("CreateConnectionStatementSegment"),
            Ref("CreateIndexStatementSegment"),
            Ref("CreateMaterializedViewStatementSegment"),
            Ref("CreateSecretStatementSegment"),
            Ref("CreateSinkKafkaStatementSegment"),
            Ref("CreateSourceKafkaStatementSegment"),
            Ref("CreateSourceLoadGeneratorStatementSegment"),
            Ref("CreateSourcePostgresStatementSegment"),
            Ref("CreateSourceWebhookStatementSegment"),
            Ref("CreateTypeStatementSegment"),
            Ref("CreateViewStatementSegment"),
            Ref("DropStatementSegment"),
            Ref("FetchStatementSegment"),
            Ref("GrantStatementSegment"),
            Ref("MaterializeExplainStatementSegment"),
            Ref("ShowStatementSegment"),
            Ref("ShowCreateStatementSegment"),
            Ref("ShowIndexesStatementSegment"),
            Ref("ShowMaterializedViewsStatementSegment"),
            Ref("DeclareStatementSegment"),
        ],
        remove=[
            Ref("CreateIndexStatementSegment"),
            Ref("DropIndexStatementSegment"),
        ],
    )


materialize_dialect.sets("materialize_sizes").clear()
materialize_dialect.sets("materialize_sizes").update(
    [
        "3xsmall",
        "2xsmall",
        "xsmall",
        "small",
        "medium",
        "large",
        "xlarge",
        "2xlarge",
        "3xlarge",
        "4xlarge",
        "5xlarge",
        "6xlarge",
    ],
)


materialize_dialect.add(
    InstanceSizes=OneOf(
        MultiStringParser(
            materialize_dialect.sets("materialize_sizes"),
            KeywordSegment,
            type="materialize_size",
        ),
        MultiStringParser(
            [
                f"'{compression}'"
                for compression in materialize_dialect.sets("materialize_sizes")
            ],
            KeywordSegment,
            type="compression_type",
        ),
    ),
    InCluster=Sequence(
        "IN",
        "CLUSTER",
        Ref("ObjectReferenceSegment"),
    ),
    Privileges=OneOf(
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "USAGE",
        "CREATEROLE",
        "CREATEDB",
        "CREATECLUSTER",
        Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
    ),
)


class AlterOwnerStatementSegment(BaseSegment):
    """A `ALTER OWNER` statement."""

    type = "alter_owner_statement"

    match_grammar = Sequence(
        "ALTER",
        OneOf(
            "CONNECTION",
            "CLUSTER",
            Sequence("CLUSTER", "REPLICA"),
            "INDEX",
            "SOURCE",
            "SINK",
            "VIEW",
            Sequence("MATERIALIZED", "VIEW"),
            "TABLE",
            "SECRET",
        ),
        Ref("ObjectReferenceSegment"),
        Sequence("OWNER", "TO"),
        Ref("ObjectReferenceSegment"),
    )


class AlterConnectionRotateKeys(BaseSegment):
    """`ALTER CONNECTION` statement."""

    type = "alter_connection_rotate_keys"

    match_grammar = Sequence(
        "ALTER",
        "CONNECTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "ROTATE",
        "KEYS",
    )


class AlterDefaultPrivilegesStatementSegment(BaseSegment):
    """A `ALTER DEFAULT PRIVILEGES` statement."""

    type = "alter_default_privileges_statement"

    match_grammar = Sequence(
        Sequence("ALTER", "DEFAULT", "PRIVILEGES", "FOR"),
        OneOf(
            Sequence(
                OneOf("ROLE", "USER"),
                Ref("ObjectReferenceSegment"),
            ),
            Sequence("ALL", "ROLES"),
        ),
        Sequence(
            "IN",
            OneOf("SCHEMA", "DATABASE"),
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        "GRANT",
        Ref("Privileges"),
        "ON",
        OneOf(
            "TABLES",
            "TYPES",
            "SECRETS",
            "CONNECTIONS",
            "DATABASES",
            "SCHEMAS",
            "CLUSTERS",
        ),
        "TO",
        Ref("ObjectReferenceSegment"),
    )


class AlterRenameStatementSegment(BaseSegment):
    """A `ALTER RENAME` statement."""

    type = "alter_rename_statement"

    match_grammar = Sequence(
        "ALTER",
        OneOf(
            "CONNECTION",
            Sequence("CLUSTER", Ref.keyword("REPLICA", optional=True)),
            "INDEX",
            "SOURCE",
            "SINK",
            "VIEW",
            Sequence("MATERIALIZED", "VIEW"),
            "TABLE",
            "SECRET",
        ),
        Ref("ObjectReferenceSegment"),
        Sequence("RENAME", "TO"),
        Ref("ObjectReferenceSegment"),
    )


class AlterIndexStatementSegment(BaseSegment):
    """A `ALTER INDEX` statement."""

    type = "alter_index_statement"

    match_grammar = Sequence(
        "ALTER",
        "INDEX",
        Ref("ObjectReferenceSegment"),
        Sequence("SET", "ENABLED"),
    )


class AlterSecretStatementSegment(BaseSegment):
    """A `ALTER SECRET` statement."""

    type = "alter_secret_statement"

    match_grammar = Sequence(
        "ALTER",
        "SECRET",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "AS",
        Anything(),
    )


class AlterSetClusterStatementSegment(BaseSegment):
    """A `ALTER SET CLUSTER` statement."""

    type = "alter_set_cluster_statement"

    match_grammar = Sequence(
        Sequence("ALTER", "MATERIALIZED", "VIEW"),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Sequence("IN", "CLUSTER"),
        Ref("ObjectReferenceSegment"),
    )


class AlterSourceSinkSizeStatementSegment(BaseSegment):
    """A `ALTER SOURCE/SINK SET SIZE` statement."""

    type = "alter_source_sink_size_statement"

    match_grammar = Sequence(
        "ALTER",
        OneOf("SOURCE", "SINK"),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "SET",
        Bracketed(
            "SIZE",
            Ref("InstanceSizes"),
        ),
    )


class CloseStatementSegment(BaseSegment):
    """A `CLOSE` statement."""

    type = "close_statement"
    match_grammar = Sequence(
        "CLOSE",
        Ref("ObjectReferenceSegment"),
    )


class CopyToStatementSegment(BaseSegment):
    """A `COPY TO` statement."""

    type = "copy_to_statement"
    match_grammar = Sequence(
        "COPY",
        Bracketed(
            # SELECT statement or SUBSCRIBE statement
            OneOf(
                Ref("SelectStatementSegment"),
                Sequence(
                    "SUBSCRIBE",
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "VALUES",
                    Delimited(
                        Anything(),
                    ),
                ),
            ),
        ),
        "TO",
        "STDOUT",
        Sequence(
            "WITH",
            Bracketed(
                Anything(),
            ),
            optional=True,
        ),
    )


class CopyFromStatementSegment(BaseSegment):
    """A `COPY FROM` statement."""

    type = "copy_from_statement"
    match_grammar = Sequence(
        "COPY",
        Ref("ObjectReferenceSegment"),
        Bracketed(
            Anything(),
            optional=True,
        ),
        "FROM",
        "STDIN",
        Sequence(
            Sequence(
                "WITH",
                optional=True,
            ),
            Bracketed(
                Anything(),
            ),
            optional=True,
        ),
    )


class CreateClusterStatementSegment(BaseSegment):
    """A `CREATE CLUSTER` statement."""

    type = "create_cluster_statement"
    match_grammar = Sequence(
        "CREATE",
        "CLUSTER",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(
                "REPLICAS",
                Bracketed(
                    Delimited(
                        Anything(),
                    )
                ),
                optional=True,
            ),
            Sequence(
                Anything(),
                optional=True,
            ),
        ),
    )


class CreateClusterReplicaStatementSegment(BaseSegment):
    """A `CREATE CLUSTER REPLICA` statement."""

    type = "create_cluster_replica_statement"
    match_grammar = Sequence(
        "CREATE",
        "CLUSTER",
        "REPLICA",
        Ref("ObjectReferenceSegment"),
        Sequence(
            Anything(),
            optional=True,
        ),
    )


class CreateConnectionStatementSegment(BaseSegment):
    """A `CREATE CONNECTION` statement."""

    type = "create_connection_statement"
    match_grammar = Sequence(
        "CREATE",
        "CONNECTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "TO",
        OneOf(
            Sequence(
                "AWS",
                "PRIVATELINK",
            ),
            Sequence(
                "CONFLUENT",
                "SCHEMA",
                "REGISTRY",
            ),
            "KAFKA",
            "POSTGRES",
            Sequence(
                "SSH",
                "TUNNEL",
            ),
        ),
        Bracketed(Anything()),
    )


class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` statement."""

    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        OneOf(
            Sequence(
                "INDEX",
                Ref("ObjectReferenceSegment"),
                Ref("InCluster", optional=True),
                "ON",
                Ref("ObjectReferenceSegment"),
                Sequence(
                    "USING",
                    Anything(),
                    optional=True,
                ),
                Bracketed(
                    Delimited(
                        Anything(),
                    )
                ),
            ),
            Sequence(
                "DEFAULT",
                "INDEX",
                Ref("InCluster", optional=True),
                "ON",
                Ref("ObjectReferenceSegment"),
                Sequence(
                    "USING",
                    Anything(),
                    optional=True,
                ),
            ),
        ),
    )


class CreateMaterializedViewStatementSegment(BaseSegment):
    """A `CREATE MATERIALIZED VIEW` statement."""

    type = "create_materialized_view_statement"
    match_grammar = Sequence(
        "CREATE",
        OneOf(
            Sequence(
                "MATERIALIZED",
                "VIEW",
                Ref("IfNotExistsGrammar", optional=True),
                Ref("ObjectReferenceSegment"),
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                    optional=True,
                ),
                Ref("InCluster", optional=True),
                "AS",
                Anything(),
            ),
            Sequence(
                Ref("OrReplaceGrammar"),
                "MATERIALIZED",
                "VIEW",
                Ref("ObjectReferenceSegment"),
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                    optional=True,
                ),
                Ref("InCluster", optional=True),
                "AS",
                Anything(),
            ),
        ),
    )


class CreateSecretStatementSegment(BaseSegment):
    """A `CREATE SECRET` statement."""

    type = "create_secret_statement"
    match_grammar = Sequence(
        "CREATE",
        "SECRET",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "AS",
        Anything(),
    )


class CreateSinkKafkaStatementSegment(BaseSegment):
    """A `CREATE SINK KAFKA` statement."""

    type = "create_sink_kafka_statement"
    match_grammar = Sequence(
        "CREATE",
        "SINK",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref("InCluster", optional=True),
        "FROM",
        Ref("ObjectReferenceSegment"),
        "INTO",
        Anything(),
        Sequence(
            "KEY",
            Bracketed(
                Delimited(
                    Ref("ColumnReferenceSegment"),
                )
            ),
            optional=True,
        ),
        Sequence(
            "FORMAT",
            Anything(),
            optional=True,
        ),
        Sequence(
            "ENVELOPE",
            OneOf(
                "DEBEZIUM",
                "UPSERT",
            ),
            optional=True,
        ),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Anything(),
                )
            ),
            optional=True,
        ),
    )


class CreateSourceKafkaStatementSegment(BaseSegment):
    """A `CREATE SOURCE KAFKA` statement."""

    type = "create_source_kafka_statement"
    match_grammar = Sequence(
        "CREATE",
        "SOURCE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref("InCluster", optional=True),
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
            ),
            optional=True,
        ),
        "FROM",
        "KAFKA",
        "CONNECTION",
        Ref("ObjectReferenceSegment"),
        Bracketed(
            Delimited(
                Anything(),
            )
        ),
        Sequence(
            "KEY",
            "FORMAT",
            Anything(),
            "VALUE",
            "FORMAT",
            Anything(),
            optional=True,
        ),
        Sequence(
            "FORMAT",
            Anything(),
            optional=True,
        ),
        Sequence(
            "INCLUDE",
            Delimited(
                Anything(),
            ),
            optional=True,
        ),
        Sequence(
            "ENVELOPE",
            OneOf(
                "NONE",
                "DEBEZIUM",
                "UPSERT",
            ),
            optional=True,
        ),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Anything(),
                )
            ),
            optional=True,
        ),
    )


class CreateSourceLoadGeneratorStatementSegment(BaseSegment):
    """A `CREATE SOURCE LOAD GENERATOR` statement."""

    type = "create_source_load_generator_statement"
    match_grammar = Sequence(
        "CREATE",
        "SOURCE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref("InCluster", optional=True),
        Sequence(
            "FROM",
            "LOAD",
            "GENERATOR",
        ),
        OneOf(
            "AUCTION",
            "COUNTER",
            "MARKETING",
            "TPCH",
        ),
        Bracketed(
            Delimited(
                Anything(),
            ),
            optional=True,
        ),
        Sequence(
            "FOR",
            "ALL",
            "TABLES",
            optional=True,
        ),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Anything(),
                )
            ),
            optional=True,
        ),
    )


class CreateSourcePostgresStatementSegment(BaseSegment):
    """A `CREATE SOURCE POSTGRES` statement."""

    type = "create_source_postgres_statement"
    match_grammar = Sequence(
        "CREATE",
        "SOURCE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref("InCluster", optional=True),
        Sequence(
            "FROM",
            "POSTGRES",
            "CONNECTION",
            Ref("ObjectReferenceSegment"),
            Bracketed(
                Delimited(
                    Anything(),
                )
            ),
            optional=True,
        ),
        OneOf(
            Sequence(
                "FOR",
                "ALL",
                "TABLES",
            ),
            Sequence(
                "FOR",
                "TABLES",
                Bracketed(
                    Delimited(
                        Anything(),
                    )
                ),
            ),
            optional=True,
        ),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Anything(),
                )
            ),
            optional=True,
        ),
    )


class CreateSourceWebhookStatementSegment(BaseSegment):
    """A `CREATE SOURCE WEBHOOK` statement."""

    type = "create_source_load_generator_statement"
    match_grammar = Sequence(
        "CREATE",
        "SOURCE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref("InCluster", optional=True),
        Sequence(
            "FROM",
            "WEBHOOK",
            "BODY",
            "FORMAT",
        ),
        OneOf(
            "TEXT",
            "JSON",
            "BYTES",
        ),
        OneOf(
            Sequence(
                "INCLUDE",
                "HEADER",
                Sequence(
                    Anything(),
                    optional=True,
                ),
            ),
            Sequence(
                "INCLUDE",
                "HEADERS",
                Bracketed(
                    Delimited(
                        Anything(),
                    )
                ),
            ),
            optional=True,
        ),
        Sequence(
            "CHECK",
            Bracketed(
                "WITH",
                Bracketed(
                    Delimited(
                        Anything(),
                    )
                ),
            ),
            optional=True,
        ),
        Sequence(
            Anything(),
            optional=True,
        ),
    )


class CreateTypeStatementSegment(BaseSegment):
    """A `CREATE TYPE` statement."""

    type = "create_type_statement"
    match_grammar = Sequence(
        "CREATE",
        "TYPE",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(
                "AS",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ObjectReferenceSegment"),
                            Ref("DatatypeSegment"),
                        ),
                    ),
                ),
            ),
            Sequence(
                "AS",
                OneOf(
                    "LIST",
                    "MAP",
                ),
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ObjectReferenceSegment"),
                            Ref("EqualsSegment"),
                            Anything(),
                        )
                    )
                ),
            ),
        ),
    )


class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement."""

    type = "create_view_statement"
    match_grammar = Sequence(
        "CREATE",
        OneOf(
            "TEMP",
            "TEMPORARY",
            optional=True,
        ),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
            ),
            optional=True,
        ),
        "AS",
        Ref("SelectableGrammar"),
    )


class DropStatementSegment(BaseSegment):
    """A `DROP` statement."""

    type = "drop_statement"
    match_grammar = Sequence(
        "DROP",
        OneOf(
            "CONNECTION",
            "CLUSTER",
            Sequence(
                "CLUSTER",
                "REPLICA",
            ),
            "DATABASE",
            "INDEX",
            Sequence(
                "MATERIALIZED",
                "VIEW",
            ),
            "ROLE",
            "SECRET",
            "SCHEMA",
            "SINK",
            "SOURCE",
            "TABLE",
            "TYPE",
            "VIEW",
            "USER",
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(
                "CASCADE",
            ),
            Sequence(
                "RESTRICT",
            ),
            optional=True,
        ),
    )


class ShowStatementSegment(BaseSegment):
    """A Materialize `SHOW` statement."""

    type = "show_statement"

    match_grammar = Sequence(
        "SHOW",
        OneOf(
            "COLUMNS",
            "CONNECTIONS",
            "CLUSTERS",
            Sequence("CLUSTER", "REPLICAS"),
            "DATABASES",
            "INDEXES",
            Sequence("MATERIALIZED", "VIEWS"),
            "SECRETS",
            "SCHEMAS",
            "SINKS",
            "SOURCES",
            "TABLES",
            "TYPES",
            "VIEWS",
            "OBJECTS",
        ),
        Ref("ObjectReferenceSegment", optional=True),
        # FROM is optional for some object types
        Sequence(
            "FROM",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        #  Like or where is optional for some object types
        OneOf(
            Sequence(
                "LIKE",
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "WHERE",
                Ref("ExpressionSegment"),
            ),
            optional=True,
        ),
    )


class ShowCreateStatementSegment(BaseSegment):
    """A Materialize `SHOW CREATE` statement."""

    type = "show_create_statement"

    match_grammar = Sequence(
        "SHOW",
        "CREATE",
        OneOf(
            Sequence("CONNECTION", optional=True),
            Sequence("INDEX", optional=True),
            Sequence("MATERIALIZED", "VIEW", optional=True),
            Sequence("SINK", optional=True),
            Sequence("SOURCE", optional=True),
            Sequence("TABLE", optional=True),
            Sequence("VIEW", optional=True),
        ),
        Ref("ObjectReferenceSegment"),
    )


class ShowIndexesStatementSegment(BaseSegment):
    """A Materialize `SHOW INDEXES` statement."""

    type = "show_indexes_statement"

    match_grammar = Sequence(
        "SHOW",
        "INDEXES",
        Sequence(
            "ON",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Sequence(
            "FROM",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Ref("InCluster", optional=True),
        OneOf(
            Sequence(
                "LIKE",
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "WHERE",
                Ref("ExpressionSegment"),
            ),
            optional=True,
        ),
    )


class ShowMaterializedViewsStatementSegment(BaseSegment):
    """A Materialize `SHOW MATERIALIZED VIEWS` statement."""

    type = "show_materialized_views_statement"

    match_grammar = Sequence(
        "SHOW",
        "MATERIALIZED",
        "VIEWS",
        Sequence(
            "FROM",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        Ref("InCluster", optional=True),
    )


class MaterializeExplainStatementSegment(BaseSegment):
    """A `EXPLAIN` statement."""

    type = "explain_statement"
    match_grammar = Sequence(
        "EXPLAIN",
        OneOf(
            Sequence(
                OneOf(
                    "RAW",
                    "DECORRELATED",
                    "OPTIMIZED",
                    "PHYSICAL",
                    optional=True,
                ),
                "PLAN",
                optional=True,
            ),
            optional=True,
        ),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Anything(),
                )
            ),
            optional=True,
        ),
        Sequence(
            "AS",
            OneOf(
                "TEXT",
                "JSON",
            ),
            optional=True,
        ),
        Sequence(
            "FOR",
            optional=True,
        ),
        OneOf(
            Ref("SelectableGrammar"),
            Sequence(
                "VIEW",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "MATERIALIZED",
                "VIEW",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                Anything(),
            ),
        ),
    )


class FetchStatementSegment(BaseSegment):
    """A `FETCH` statement."""

    type = "fetch_statement"
    match_grammar = Sequence(
        "FETCH",
        Sequence(
            "FORWARD",
            optional=True,
        ),
        OneOf(
            "ALL",
            Ref("NumericLiteralSegment"),
            optional=True,
        ),
        Sequence(
            "FROM",
            optional=True,
        ),
        Ref("ObjectReferenceSegment"),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Anything(),
                )
            ),
            optional=True,
        ),
    )


class GrantStatementSegment(BaseSegment):
    """A `GRANT` statement."""

    type = "grant_statement"
    match_grammar = Sequence(
        "GRANT",
        Ref("Privileges"),
        "ON",
        OneOf(
            Sequence(
                OneOf(
                    "TABLE",
                    "TYPE",
                    "SECRET",
                    "CONNECTION",
                    "DATABASE",
                    "SCHEMA",
                    "CLUSTER",
                    optional=True,
                ),
                Delimited(
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            "SYSTEM",
            Sequence(
                "ALL",
                OneOf(
                    Sequence(
                        OneOf(
                            "TABLES",
                            "TYPES",
                            "SECRETS",
                            "CONNECTIONS",
                        ),
                        "IN",
                        "SCHEMA",
                        Delimited(
                            Ref("ObjectReferenceSegment"),
                        ),
                    ),
                    Sequence(
                        OneOf("TABLES", "TYPES", "SECRETS", "CONNECTIONS", "SCHEMAS"),
                        "IN",
                        "DATABASE",
                        Delimited(
                            Ref("ObjectReferenceSegment"),
                        ),
                    ),
                    "DATABASES",
                    "SCHEMAS",
                    "CLUSTERS",
                ),
            ),
        ),
        "TO",
        Sequence("GROUP", optional=True),
        Delimited(
            Ref("ObjectReferenceSegment"),
        ),
    )


class DeclareStatementSegment(BaseSegment):
    """A `DECLARE` statement."""

    type = "declare_statement"
    match_grammar = Sequence(
        "DECLARE",
        Ref("ObjectReferenceSegment"),
        "CURSOR",
        Sequence(
            "WITHOUT",
            "HOLD",
            optional=True,
        ),
        "FOR",
        OneOf(
            Ref("SelectableGrammar"),
            Sequence(
                "VIEW",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "MATERIALIZED",
                "VIEW",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                Anything(),
            ),
        ),
    )
