"""MariaDB Dialect.

https://mariadb.com/kb/en/sql-statements-structure/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseSegment,
    Bracketed,
    Dedent,
    Delimited,
    Indent,
    Matchable,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_mysql as mysql
from sqlfluff.dialects.dialect_mariadb_keywords import (
    mariadb_reserved_keywords,
    mariadb_unreserved_keywords,
)

# ansi_dialect = load_raw_dialect("ansi")
mysql_dialect = load_raw_dialect("mysql")
mariadb_dialect = mysql_dialect.copy_as(
    "mariadb",
    formatted_name="MariaDB",
    docstring="""**Default Casing**: ``lowercase``

**Quotes**: String Literals: ``''``, ``""`` or ``@``,
Identifiers: |back_quotes|.

The dialect for `MariaDB <https://www.mariadb.org/>`_.""",
)
mariadb_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", mariadb_unreserved_keywords
)
mariadb_dialect.sets("reserved_keywords").clear()
mariadb_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", mariadb_reserved_keywords
)


class ColumnConstraintSegment(mysql.ColumnConstraintSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    match_grammar: Matchable = OneOf(
        mysql.ColumnConstraintSegment.match_grammar,
        Sequence(
            Sequence("GENERATED", "ALWAYS", optional=True),
            "AS",
            Bracketed(Ref("ExpressionSegment")),
            OneOf("PERSISTENT", "STORED", "VIRTUAL", optional=True),
        ),
    )


class CreateUserStatementSegment(mysql.CreateUserStatementSegment):
    """`CREATE USER` statement.

    https://mariadb.com/kb/en/create-user/
    """

    match_grammar = mysql.CreateUserStatementSegment.match_grammar.copy(
        insert=[Ref("OrReplaceGrammar", optional=True)],
        before=Ref.keyword("USER"),
    )


class CreateTableStatementSegment(mysql.CreateTableStatementSegment):
    """`CREATE TABLE` segment.

    https://mariadb.com/kb/en/create-table/
    """

    ES = Ref("ExpressionSegment")
    CRS = Ref("ColumnReferenceSegment")
    NLS = Ref("NumericLiteralSegment")
    ORS = Ref("ObjectReferenceSegment")
    TRS = Ref("TableReferenceSegment")
    SQIS = Ref("SingleQuotedIdentifierSegment")

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryTransientGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                        ),
                    )
                ),
                Ref("CommentClauseSegment", optional=True),
                Sequence(
                    Ref.keyword("AS", optional=True),
                    OptionallyBracketed(Ref("SelectableGrammar")),
                    optional=True,
                ),
            ),
            # Create AS syntax:
            Sequence(
                Ref.keyword("AS", optional=True),
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref("TableEndClauseSegment", optional=True),
        AnyNumberOf(
            Sequence(
                Ref.keyword("DEFAULT", optional=True),
                OneOf(
                    Ref("ParameterNameSegment"),
                    Sequence("CHARACTER", "SET"),
                    Sequence(OneOf("DATA", "INDEX"), "DIRECTORY"),
                    Sequence("WITH", "SYSTEM"),
                ),
                Ref("EqualsSegment", optional=True),
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("ParameterNameSegment"),
                    Ref("QuotedLiteralSegment"),
                    Ref("SingleQuotedIdentifierSegment"),
                    Ref("NumericLiteralSegment"),
                    # Union option
                    Bracketed(
                        Delimited(Ref("TableReferenceSegment")),
                    ),
                ),
            ),
            # Partition Options
            # https://dev.mysql.com/doc/refman/8.0/en/create-table.html#create-table-partitioning
            Sequence(
                "PARTITION",
                "BY",
                OneOf(
                    Sequence(
                        Ref.keyword("LINEAR", optional=True),
                        OneOf(
                            Sequence("HASH", Ref("ExpressionSegment")),
                            Sequence(
                                "KEY",
                                Sequence(
                                    "ALGORITHM",
                                    Ref("EqualsSegment"),
                                    Ref("NumericLiteralSegment"),
                                    optional=True,
                                ),
                                Delimited(Ref("ColumnReferenceSegment")),
                            ),
                        ),
                    ),
                    Sequence(
                        OneOf("RANGE", "LIST"),
                        OneOf(
                            Ref("ExpressionSegment"),
                            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                        ),
                    ),
                ),
                Sequence("PARTITIONS", Ref("NumericLiteralSegment"), optional=True),
                Sequence(
                    "SUBPARTITION",
                    "BY",
                    Sequence(
                        Ref.keyword("LINEAR", optional=True),
                        OneOf(
                            Sequence("HASH", Ref("ExpressionSegment")),
                            Sequence(
                                "KEY",
                                Sequence(
                                    "ALGORITHM",
                                    Ref("EqualsSegment"),
                                    Ref("NumericLiteralSegment"),
                                    optional=True,
                                ),
                                Bracketed(Ref("ColumnReferenceSegment")),
                            ),
                        ),
                    ),
                    Sequence(
                        "SUBPARTITIONS",
                        Ref("NumericLiteralSegment"),
                        optional=True,
                    ),
                    optional=True,
                ),
                # optional partition_definition(s)
                AnyNumberOf(
                    Bracketed(
                        Delimited(
                            Sequence(
                                "PARTITION",
                                Ref("ColumnReferenceSegment"),
                                AnyNumberOf(
                                    Sequence(
                                        "VALUES",
                                        OneOf(
                                            Sequence(
                                                "LESS",
                                                "THAN",
                                                OneOf(
                                                    "MAXVALUE",
                                                    Bracketed(
                                                        OneOf(
                                                            ES,
                                                            CRS,
                                                            NLS,
                                                            Ref("LiteralGrammar"),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                            Sequence(
                                                "IN",
                                                Bracketed(
                                                    Ref("ObjectReferenceSegment")
                                                ),
                                            ),
                                        ),
                                    ),
                                    Sequence(
                                        OneOf(
                                            Ref("ParameterNameSegment"),
                                            Sequence("CHARACTER", "SET"),
                                            Sequence(
                                                OneOf("DATA", "INDEX"),
                                                "DIRECTORY",
                                            ),
                                            Sequence("WITH", "SYSTEM"),
                                        ),
                                        Ref("EqualsSegment", optional=True),
                                        OneOf(
                                            Ref("LiteralGrammar"),
                                            Ref("ParameterNameSegment"),
                                            Ref("QuotedLiteralSegment"),
                                            Ref("SingleQuotedIdentifierSegment"),
                                            Ref("NumericLiteralSegment"),
                                            # Union option
                                            Bracketed(
                                                Delimited(Ref("TableReferenceSegment")),
                                            ),
                                        ),
                                    ),
                                    # optional subpartition_definition(s)
                                    Sequence(
                                        Ref.keyword("SUBPARTITION", optional=True),
                                        Ref("LiteralGrammar"),
                                        AnyNumberOf(
                                            Sequence(
                                                "VALUES",
                                                OneOf(
                                                    Sequence(
                                                        "LESS",
                                                        "THAN",
                                                        OneOf(
                                                            "MAXVALUE",
                                                            Bracketed(ES),
                                                            Bracketed(CRS),
                                                        ),
                                                    ),
                                                    Sequence(
                                                        "IN",
                                                        Bracketed(ORS),
                                                    ),
                                                ),
                                            ),
                                            Sequence(
                                                OneOf(
                                                    Ref("ParameterNameSegment"),
                                                    Sequence("CHARACTER", "SET"),
                                                    Sequence(
                                                        OneOf("DATA", "INDEX"),
                                                        "DIRECTORY",
                                                    ),
                                                    Sequence("WITH", "SYSTEM"),
                                                ),
                                                Ref(
                                                    "EqualsSegment",
                                                    optional=True,
                                                ),
                                                OneOf(
                                                    Ref("LiteralGrammar"),
                                                    Ref("ParameterNameSegment"),
                                                    Ref("QuotedLiteralSegment"),
                                                    SQIS,
                                                    Ref("NumericLiteralSegment"),
                                                    # Union option
                                                    Bracketed(
                                                        Delimited(TRS),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    https://mariadb.com/kb/en/delete/
    """

    type = "delete_statement"
    match_grammar = Sequence(
        "DELETE",
        Ref.keyword("LOW_PRIORITY", optional=True),
        Ref.keyword("QUICK", optional=True),
        Ref.keyword("IGNORE", optional=True),
        OneOf(
            Sequence(
                "FROM",
                Delimited(
                    Ref("DeleteTargetTableSegment"),
                    terminators=["USING"],
                ),
                Ref("DeleteUsingClauseSegment"),
                Ref("WhereClauseSegment", optional=True),
            ),
            Sequence(
                Delimited(
                    Ref("DeleteTargetTableSegment"),
                    terminators=["FROM"],
                ),
                Ref("FromClauseSegment"),
                Ref("WhereClauseSegment", optional=True),
            ),
            Sequence(
                Ref("FromClauseSegment"),
                Ref("SelectPartitionClauseSegment", optional=True),
                Ref("WhereClauseSegment", optional=True),
                Ref("OrderByClauseSegment", optional=True),
                Ref("LimitClauseSegment", optional=True),
                Ref("ReturningClauseSegment", optional=True),
            ),
        ),
    )


class FlushStatementSegment(mysql.FlushStatementSegment):
    """A `Flush` statement.

    https://mariadb.com/kb/en/flush/
    """

    match_grammar: Matchable = Sequence(
        "FLUSH",
        OneOf(
            "NO_WRITE_TO_BINLOG",
            "LOCAL",
            optional=True,
        ),
        OneOf(
            Delimited(
                Sequence("BINARY", "LOGS"),
                Sequence("ENGINE", "LOGS"),
                Sequence("ERROR", "LOGS"),
                Sequence("GENERAL", "LOGS"),
                Sequence("QUERY", "CACHE"),
                Sequence("SLOW", "LOGS"),
                Sequence(Ref.keyword("RESET", optional=True), "MASTER"),
                Sequence(OneOf("GLOBAL", "SESSION", optional=True), "STATUS"),
                Sequence(
                    "RELAY",
                    "LOGS",
                    Sequence("FOR", "CHANNEL", optional=True),
                    Ref("ObjectReferenceSegment"),
                ),
                "HOSTS",
                "LOGS",
                "PRIVILEGES",
                "CHANGED_PAGE_BITMAPS",
                "CLIENT_STATISTICS",
                "DES_KEY_FILE",
                "INDEX_STATISTICS",
                "QUERY_RESPONSE_TIME",
                "SLAVE",
                "SSL",
                "TABLE_STATISTICS",
                "USER_STATISTICS",
                "USER_VARIABLES",
                "USER_RESOURCES",
            ),
            Sequence(
                "TABLES",
                Sequence(
                    Delimited(Ref("TableReferenceSegment"), terminators=["WITH"]),
                    optional=True,
                ),
                Sequence(
                    "WITH",
                    "READ",
                    "LOCK",
                    Sequence("AND", "DISABLE", "CHECKPOINT", optional=True),
                    optional=True,
                ),
            ),
            Sequence(
                "TABLES",
                Sequence(
                    Delimited(Ref("TableReferenceSegment"), terminators=["FOR"]),
                    optional=False,
                ),
                Sequence("FOR", "EXPORT", optional=True),
            ),
        ),
    )


class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    type = "groupby_clause"

    match_grammar: Matchable = Sequence(
        "GROUP",
        "BY",
        Indent,
        Sequence(
            Delimited(
                Sequence(
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        # Can `GROUP BY 1`
                        Ref("NumericLiteralSegment"),
                        # Can `GROUP BY coalesce(col, 1)`
                        Ref("ExpressionSegment"),
                    ),
                    OneOf("ASC", "DESC", optional=True),
                ),
                terminators=[Ref("GroupByClauseTerminatorGrammar")],
            ),
        ),
        Ref("WithRollupClauseSegment", optional=True),
        Dedent,
    )


class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    https://mariadb.com/kb/en/insert/
    """

    type = "insert_statement"
    match_grammar = Sequence(
        "INSERT",
        OneOf(
            "LOW_PRIORITY",
            "DELAYED",
            "HIGH_PRIORITY",
            optional=True,
        ),
        Ref.keyword("IGNORE", optional=True),
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        Sequence(
            "PARTITION",
            Bracketed(
                Ref("SingleIdentifierListSegment"),
            ),
            optional=True,
        ),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        OneOf(
            Ref("ValuesClauseSegment"),
            Ref("SetClauseListSegment"),
            Ref(
                "SelectableGrammar",
                terminators=[Ref("ReturningClauseSegment")],
            ),
            optional=True,
        ),
        Ref("InsertRowAliasSegment", optional=True),
        Ref("UpsertClauseListSegment", optional=True),
        Ref("ReturningClauseSegment", optional=True),
    )


class ReplaceSegment(BaseSegment):
    """A `REPLACE` statement.

    As per https://mariadb.com/kb/en/replace/
    """

    type = "replace_statement"

    match_grammar = Sequence(
        "REPLACE",
        OneOf("LOW_PRIORITY", "DELAYED", optional=True),
        Sequence("INTO", optional=True),
        Ref("TableReferenceSegment"),
        Ref("SelectPartitionClauseSegment", optional=True),
        OneOf(
            Sequence(
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                Ref("ValuesClauseSegment"),
            ),
            Ref("SetClauseListSegment"),
            Sequence(
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                Ref("SelectStatementSegment"),
            ),
        ),
        Ref("ReturningClauseSegment", optional=True),
    )


class ReturningClauseSegment(BaseSegment):
    """This is a `RETURNING` clause.

    A RETURNING clause returns values modified by a
    INSERT, DELETE or REPLACE query.

    https://mariadb.com/kb/en/insert/
    https://mariadb.com/kb/en/delete/
    https://mariadb.com/kb/en/replace/
    """

    type = "returning_clause"

    match_grammar: Matchable = Sequence(
        "RETURNING",
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
            allow_trailing=True,
        ),
        Dedent,
        terminators=[Ref("SelectClauseTerminatorGrammar")],
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
    )


class SelectStatementSegment(mysql.SelectStatementSegment):
    """A `SELECT` statement.

    https://mariadb.com/kb/en/select/
    """

    # Inherit most of the parse grammar from the original.
    match_grammar = mysql.UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
            Ref("IntoClauseSegment", optional=True),
        ],
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("UpsertClauseListSegment"),
            Ref("WithCheckOptionSegment"),
            Ref("ReturningClauseSegment"),
        ],
        # Overwrite the terminators, because we want to remove some from the
        # expression above.
        replace_terminators=True,
    )


class WithRollupClauseSegment(BaseSegment):
    """A `WITH ROLLUP` clause after the `GROUP BY` clause."""

    type = "with_rollup_clause"

    match_grammar = Sequence(
        "WITH",
        "ROLLUP",
    )
