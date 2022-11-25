"""The Materialize dialect.

This is based on postgres dialect, since it was initially based off of Postgres.
We should monitor in future and see if it should be rebased off of ANSI
"""
from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    AnySetOf,
    Anything,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    Indent,
    Matchable,
    TypedParser,
    Nothing,
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
    MultiStringParser
)

from sqlfluff.core.parser.segments.raw import KeywordSegment
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects import dialect_postgres as postgres
from sqlfluff.dialects.dialect_materialize_keywords import (
    materialize_reserved_keywords,
    materialize_unreserved_keywords,
)

postgres_dialect = load_raw_dialect("postgres")

materialize_dialect = postgres_dialect.copy_as("materialize")
materialize_dialect.sets("unreserved_keywords").update(
    [n.strip().upper() for n in materialize_unreserved_keywords.split("\n")]
)

materialize_dialect.sets("reserved_keywords").clear()
materialize_dialect.sets("reserved_keywords").update(
    [n.strip().upper() for n in materialize_reserved_keywords.split("\n")]
)

class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = ansi.StatementSegment.match_grammar
    parse_grammar = ansi.StatementSegment.parse_grammar.copy(
        insert=[
            Ref("AlterConnectionRotateKeys"),
            Ref("AlterIndexStatementSegment"),
            Ref("AlterRenameStatementSegment"),
            Ref("AlterSecretStatementSegment"),
            Ref("AlterSourceSinkSizeStatementSegment"),
            Ref("CreateMaterializedViewStatementSegment"),
            Ref("ShowStatementSegment"),
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
)

class CreateMaterializedViewStatementSegment(BaseSegment):
    """A `CREATE MATERIALIZED VIEW` statement.

    https://materialize.com/docs/sql/create-materialized-view/
    """

    type = "create_materialized_view_statement"
    match_grammar = Sequence(
        "CREATE",
        "MATERIALIZED",
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        Anything(),
    )

class ShowStatementSegment(BaseSegment):
    """A Materialize `SHOW` statement.
    """
    _object_types = OneOf(
        "COLUMNS",
        "CONNECTIONS",
        "CLUSTERS",
        Sequence("CLUSTER", "REPLICAS"),
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
    )

    type = "show_statement"

    match_grammar = Sequence(
        "SHOW",
        _object_types,
        Ref("ObjectReferenceSegment", optional=True),
        Ref("WhereClauseSegment", optional=True)
    )

class AlterConnectionRotateKeys(BaseSegment):
    """`ALTER CONNECTION` statement.
    """
    type = "alter_connection_rotate_keys"

    match_grammar = Sequence(
        "ALTER",
        "CONNECTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "ROTATE",
        "KEYS"
    )

class AlterRenameStatementSegment(BaseSegment):
    """A `ALTER RENAME` statement.
    """
    _object_types = OneOf(
        "CONNECTION",
        "INDEX",
        "SOURCE",
        "SINK",
        "VIEW",
        Sequence("MATERIALIZED", "VIEW"),
        "TABLE",
        "SECRET"
    )

    type = "alter_rename_statement"

    match_grammar = Sequence(
        "ALTER",
        _object_types,
        Ref("ObjectReferenceSegment"),
        Sequence("RENAME", "TO"),
        Ref("ObjectReferenceSegment")
    )

class AlterIndexStatementSegment(BaseSegment):
    """A `ALTER INDEX` statement.
    """
    type = "alter_index_statement"

    match_grammar = Sequence(
        "ALTER",
        "INDEX",
        Ref("ObjectReferenceSegment"),
        Sequence("SET", "ENABLED")
    )

class AlterSecretStatementSegment(BaseSegment):
    """A `ALTER SECRET` statement.
    """
    type = "alter_secret_statement"

    match_grammar = Sequence(
        "ALTER",
        "SECRET",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "AS",
        Anything()
    )

class AlterSourceSinkSizeStatementSegment(BaseSegment):
    """A `ALTER SOURCE/SINK SET SIZE` statement.
    """
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
        )
    )