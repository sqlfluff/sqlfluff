"""MariaDB Dialect."""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    Bracketed,
    Delimited,
    Ref,
    OneOf,
    OptionallyBracketed,
    Sequence,
)
from sqlfluff.dialects import dialect_mysql as mysql
from sqlfluff.dialects.dialect_mariadb_keywords import (
    mariadb_reserved_keywords,
    mariadb_unreserved_keywords,
)

# ansi_dialect = load_raw_dialect("ansi")
mysql_dialect = load_raw_dialect("mysql")
mariadb_dialect = mysql_dialect.copy_as("mariadb")
mariadb_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", mariadb_unreserved_keywords
)
mariadb_dialect.sets("reserved_keywords").clear()
mariadb_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", mariadb_reserved_keywords
)


class CreateUserStatementSegment(mysql.CreateUserStatementSegment):
    """`CREATE USER` statement.

    TODO: https://mariadb.com/kb/en/create-user/
    """

    match_grammar = mysql.CreateUserStatementSegment.match_grammar.copy(
        insert=[Ref("OrReplaceGrammar", optional=True)],
        before=Ref.keyword("USER"),
    )


class CreateTableStatementSegment(mysql.CreateTableStatementSegment):
    """A CREATE TABLE segment.

    https://mariadb.com/kb/en/create-table/
    """

    match_grammar = mysql.CreateTableStatementSegment.match_grammar.copy(
        insert=[Ref("OrReplaceGrammar", optional=True)],
        before=Ref("TemporaryTransientGrammar", optional=True),
    ).copy(
        insert=[
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
        ],
        before=Ref("TableEndClauseSegment", optional=True),
        remove=[
            OneOf(
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
                ),
                Sequence(
                    "AS",
                    OptionallyBracketed(Ref("SelectableGrammar")),
                ),
                Sequence("LIKE", Ref("TableReferenceSegment")),
            ),
        ],
    )
