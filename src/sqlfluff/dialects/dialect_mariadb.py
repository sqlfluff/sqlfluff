"""The MariaDB dialect.

MariaDB is a fork of MySQL, so the dialect is very similar.
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnySetOf,
    BaseSegment,
    Bracketed,
    Dedent,
    Delimited,
    Indent,
    Matchable,
    OneOf,
    ParseMode,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects import dialect_mysql as mysql
from sqlfluff.dialects.dialect_mariadb_keywords import (
    mariadb_reserved_keywords,
    mariadb_unreserved_keywords,
)

mysql_dialect = load_raw_dialect("mysql")
ansi_dialect = load_raw_dialect("ansi")
mariadb_dialect = mysql_dialect.copy_as("mariadb")

# Set Keywords
# Do not clear inherited unreserved ansi keywords. Too many are needed to parse well.
# Just add MariaDB unreserved keywords.
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
        AnySetOf(
            OneOf(
                Ref("ValuesClauseSegment"),
                Ref("SetClauseListSegment"),
                Ref("SelectStatementSegment"),
                optional=False,
            ),
            Ref("InsertRowAliasSegment", optional=True),
            Ref("UpsertClauseListSegment", optional=True),
            Ref("ReturningClauseSegment", optional=True),
        ),
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


class SelectStatementSegment(ansi.SelectStatementSegment):
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
