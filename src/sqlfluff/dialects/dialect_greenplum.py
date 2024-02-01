"""The Greenplum dialect.

Greenplum (http://www.greenplum.org/) is a Massively Parallel Postgres,
so we base this dialect on Postgres.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    Anything,
    BaseSegment,
    Bracketed,
    Dedent,
    Delimited,
    Indent,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects import dialect_postgres as postgres
from sqlfluff.dialects.dialect_greenplum_keywords import greenplum_keywords
from sqlfluff.dialects.dialect_postgres_keywords import get_keywords

postgres_dialect = load_raw_dialect("postgres")

greenplum_dialect = postgres_dialect.copy_as("greenplum")

greenplum_dialect.sets("reserved_keywords").update(
    get_keywords(greenplum_keywords, "reserved")
)

greenplum_dialect.sets("unreserved_keywords").update(
    get_keywords(greenplum_keywords, "non-reserved")
)


class StatementSegment(postgres.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = postgres.StatementSegment.match_grammar.copy(
        insert=[
            Ref("FetchClauseSegment"),
            Ref("DeclareStatement"),
            Ref("CloseStatementSegment"),
            Ref("AnalizeSegment"),
        ],
    )


class SelectClauseSegment(postgres.SelectClauseSegment):
    """Overrides Postgres to allow DISTRIBUTED as a terminator."""

    match_grammar = Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
            # In Postgres you don't need an element so make it optional
            optional=True,
            allow_trailing=True,
        ),
        Dedent,
        terminators=[
            "INTO",
            "FROM",
            "WHERE",
            Sequence("ORDER", "BY"),
            "LIMIT",
            "OVERLAPS",
            Ref("SetOperatorSegment"),
            Sequence("WITH", Ref.keyword("NO", optional=True), "DATA"),
            Ref("WithCheckOptionSegment"),
            Ref("DistributedBySegment"),
        ],
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
    )


class DistributedBySegment(BaseSegment):
    """A DISTRIBUTED BY clause."""

    type = "distributed_by"

    match_grammar = Sequence(
        "DISTRIBUTED",
        OneOf(
            "RANDOMLY",
            "REPLICATED",
            Sequence("BY", Bracketed(Delimited(Ref("ColumnReferenceSegment")))),
        ),
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
                OneOf("RANGE", "LIST"),
                Bracketed(
                    Ref("ColumnReferenceSegment"),
                ),
                AnyNumberOf(
                    Sequence(
                        "SUBPARTITION",
                        "BY",
                        OneOf("RANGE", "LIST"),
                        Bracketed(
                            Ref("ColumnReferenceSegment"),
                        ),
                        Sequence(
                            "SUBPARTITION",
                            "TEMPLATE",
                            Bracketed(
                                # TODO: Is this too permissive?
                                Anything(),
                            ),
                            optional=True,
                        ),
                    ),
                ),
                Bracketed(
                    # TODO: Is this too permissive?
                    Anything(),
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
                                OneOf(
                                    Ref("LiteralGrammar"),
                                    Ref("NakedIdentifierSegment"),
                                    Ref("QuotedIdentifierSegment"),
                                ),
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
            Ref("DistributedBySegment"),
        ),
    )


class CreateTableAsStatementSegment(postgres.CreateTableAsStatementSegment):
    """A `CREATE TABLE AS` statement.

    As specified in
    https://docs.vmware.com/en/VMware-Tanzu-Greenplum/6/greenplum-database/GUID-ref_guide-sql_commands-CREATE_TABLE_AS.html
    This is overriden from Postgres to add the `DISTRIBUTED` clause.
    """

    match_grammar = Sequence(
        "CREATE",
        OneOf(
            Sequence(
                OneOf("GLOBAL", "LOCAL", optional=True),
                Ref("TemporaryGrammar"),
            ),
            "UNLOGGED",
            optional=True,
        ),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        AnyNumberOf(
            Bracketed(
                Delimited(Ref("ColumnReferenceSegment")),
                optional=True,
            ),
            Sequence("USING", Ref("ParameterNameSegment"), optional=True),
            OneOf(
                Sequence(
                    "WITH",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("ParameterNameSegment"),
                                Sequence(
                                    Ref("EqualsSegment"),
                                    OneOf(
                                        Ref("LiteralGrammar"),
                                        Ref("NakedIdentifierSegment"),
                                        Ref("QuotedIdentifierSegment"),
                                    ),
                                    optional=True,
                                ),
                            )
                        )
                    ),
                ),
                Sequence("WITHOUT", "OIDS"),
                optional=True,
            ),
            Sequence(
                "ON",
                "COMMIT",
                OneOf(Sequence("PRESERVE", "ROWS"), Sequence("DELETE", "ROWS"), "DROP"),
                optional=True,
            ),
            Sequence("TABLESPACE", Ref("TablespaceReferenceSegment"), optional=True),
        ),
        "AS",
        OneOf(
            OptionallyBracketed(Ref("SelectableGrammar")),
            OptionallyBracketed(Sequence("TABLE", Ref("TableReferenceSegment"))),
            Ref("ValuesClauseSegment"),
            OptionallyBracketed(Sequence("EXECUTE", Ref("FunctionSegment"))),
        ),
        Ref("WithDataClauseSegment", optional=True),
        Ref("DistributedBySegment", optional=True),
    )


class UnorderedSelectStatementSegment(postgres.UnorderedSelectStatementSegment):
    """Overrides Postgres Statement, adding DISTRIBUTED BY as a terminator."""

    match_grammar = postgres.UnorderedSelectStatementSegment.match_grammar.copy(
        terminators=[
            Ref("DistributedBySegment"),
        ],
    )


class SelectStatementSegment(postgres.SelectStatementSegment):
    """Overrides Postgres Statement, adding DISTRIBUTED BY as a terminator."""

    match_grammar = postgres.SelectStatementSegment.match_grammar.copy(
        terminators=[
            Ref("DistributedBySegment"),
        ],
    )


class AnalizeSegment(BaseSegment):
    """ANALYZE statement.

    https://docs.vmware.com/en/VMware-Greenplum/6/greenplum-database/ref_guide-sql_commands-ANALYZE.html
    """

    type = "analize_statement"

    match_grammar = Sequence(
        OneOf("ANALYZE", "ANALYSE"),
        Ref.keyword("VERBOSE", optional=True),
        Ref.keyword("ROOTPARTITION", optional=True),
        OneOf(
            Sequence(
                Ref("TableReferenceSegment"),
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                        allow_trailing=True,
                    ),
                    optional=True,
                ),
            ),
            "ALL",
            optional=True,
        ),
    )


class FetchClauseSegment(ansi.FetchClauseSegment):
    """FETCH statement.

    https://docs.vmware.com/en/VMware-Greenplum/6/greenplum-database/ref_guide-sql_commands-FETCH.html
    """

    type = "fetch_clause"
    match_grammar = Sequence(
        "FETCH",
        Sequence(
            OneOf(
                "FIRST",
                "NEXT",
                Sequence("ABSOLUTE", Ref("NumericLiteralSegment")),
                Sequence("RELATIVE", Ref("NumericLiteralSegment")),
                Ref("NumericLiteralSegment"),
                "ALL",
                "FORWARD",
                Sequence("FORWARD", Ref("NumericLiteralSegment")),
                Sequence("FORWARD", "ALL"),
            ),
            OneOf("FROM", "IN"),
            optional=True,
        ),
        Ref("TableReferenceSegment"),
    )


class DeclareStatement(BaseSegment):
    """DECLARE statement.

    https://docs.vmware.com/en/VMware-Greenplum/6/greenplum-database/ref_guide-sql_commands-DECLARE.html
    """

    type = "declare_statement"

    match_grammar = Sequence(
        "DECLARE",
        Ref("TableReferenceSegment"),
        AnySetOf(
            Ref.keyword("BINARY", optional=True),
            Ref.keyword("INSENSITIVE", optional=True),
            Sequence(
                "NO",
                "SCROLL",
                optional=True,
            ),
            Sequence(
                "PARALLEL",
                "RETRIEVE",
                optional=True,
            ),
            optional=True,
        ),
        "CURSOR",
        Sequence(
            OneOf("WITH", "WITHOUT"),
            "HOLD",
            optional=True,
        ),
        "FOR",
        Ref("StatementSegment"),
        Sequence(
            "FOR",
            "READ",
            "ONLY",
            optional=True,
        ),
    )


class CloseStatementSegment(BaseSegment):
    """CLOSE statement.

    https://docs.vmware.com/en/VMware-Greenplum/7/greenplum-database/ref_guide-sql_commands-CLOSE.html
    """

    type = "close_statement"

    match_grammar = Sequence(
        "CLOSE",
        OneOf(Ref("TableReferenceSegment"), "ALL"),
    )


class CopyStatementSegment(postgres.CopyStatementSegment):
    """COPY statement.

    https://docs.vmware.com/en/VMware-Greenplum/6/greenplum-database/ref_guide-sql_commands-COPY.html
    """

    type = "copy_statement"

    _target_subset = OneOf(
        Ref("QuotedLiteralSegment"),
        Sequence("PROGRAM", Ref("QuotedLiteralSegment")),
    )

    _table_definition = Sequence(
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("ColumnReferenceSegment"),
                allow_trailing=True,
            ),
            optional=True,
        ),
    )

    _option = Sequence(
        AnySetOf(
            Sequence("FORMAT", Ref("SingleIdentifierGrammar")),
            Sequence("ON", "SEGMENT"),
            "BINARY",
            Sequence("OIDS", Ref("BooleanLiteralGrammar", optional=True)),
            Sequence("FREEZE", Ref("BooleanLiteralGrammar", optional=True)),
            Sequence(
                "DELIMITER",
                Ref.keyword("AS", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "NULL",
                Ref.keyword("AS", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence("HEADER", Ref("BooleanLiteralGrammar", optional=True)),
            Sequence("QUOTE", Ref("QuotedLiteralSegment")),
            Sequence(
                "ESCAPE",
                Ref.keyword("AS", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "NEWLINE",
                Ref.keyword("AS", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "FORCE_QUOTE",
                OneOf(
                    Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    Ref("StarSegment"),
                ),
            ),
            Sequence(
                "FORCE_NOT_NULL",
                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            ),
            Sequence(
                "FORCE_NULL",
                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            ),
            Sequence("ENCODING", Ref("QuotedLiteralSegment")),
            Sequence("FILL", "MISSING", "FIELDS"),
            Sequence(
                "LOG",
                "ERRORS",
                Sequence(
                    "SEGMENT",
                    "REJECT",
                    "LIMIT",
                    Ref("NumericLiteralSegment"),
                    OneOf(
                        "ROWS",
                        "PERCENT",
                        optional=True,
                    ),
                    optional=True,
                ),
            ),
            Sequence(
                "CSV",
                Sequence(
                    "QUOTE",
                    Ref.keyword("AS", optional=True),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
                OneOf(
                    Sequence(
                        "FORCE",
                        "NOT",
                        "NULL",
                        Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    ),
                    Sequence(
                        "FORCE",
                        "QUOTE",
                        Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    ),
                    optional=True,
                ),
            ),
            Sequence("IGNORE", "EXTERNAL", "PARTITIONS"),
        ),
        optional=True,
    )

    _bracketed_option = Sequence(
        Bracketed(
            Delimited(
                _option,
            )
        )
    )

    match_grammar = Sequence(
        "COPY",
        OneOf(
            Sequence(
                _table_definition,
                "FROM",
                OneOf(
                    _target_subset,
                    Sequence("STDIN"),
                ),
                Ref.keyword("WITH", optional=True),
                OneOf(_option, _bracketed_option, optional=True),
                Sequence("ON", "SEGMENT", optional=True),
            ),
            Sequence(
                OneOf(
                    _table_definition,
                    Bracketed(Ref("UnorderedSelectStatementSegment")),
                ),
                "TO",
                OneOf(
                    _target_subset,
                    Sequence("STDOUT"),
                ),
                OneOf(
                    Sequence(
                        Ref.keyword("WITH", optional=True),
                        OneOf(_option, _bracketed_option, optional=True),
                    ),
                    Ref("StarSegment"),
                    optional=True,
                ),
                Sequence("ON", "SEGMENT", optional=True),
            ),
        ),
    )
