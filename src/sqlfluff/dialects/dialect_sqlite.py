"""The sqlite dialect.

https://www.sqlite.org/
"""

from sqlfluff.core.parser import (
    BaseSegment,
    Matchable,
    OneOf,
    Ref,
    Sequence,
    OptionallyBracketed,
    Bracketed,
    Delimited,
)

from sqlfluff.core.dialects import load_raw_dialect

ansi_dialect = load_raw_dialect("ansi")

sqlite_dialect = ansi_dialect.copy_as("sqlite")

sqlite_dialect.sets("reserved_keywords").update(["AUTOINCREMENT"])
sqlite_dialect.sets("unreserved_keywords").update(["FAIL"])

sqlite_dialect.replace(
    BooleanBinaryOperatorGrammar=OneOf(
        Ref("AndOperatorGrammar"), Ref("OrOperatorGrammar"), "REGEXP"
    ),
    PrimaryKeyGrammar=Sequence(
        "PRIMARY", "KEY", Sequence("AUTOINCREMENT", optional=True)
    ),
)


class TableEndClauseSegment(BaseSegment):
    """Support WITHOUT ROWID at end of tables.

    https://www.sqlite.org/withoutrowid.html
    """

    type = "table_end_clause_segment"
    match_grammar: Matchable = Sequence("WITHOUT", "ROWID")


class IndexColumnDefinitionSegment(BaseSegment):
    """A column definition for CREATE INDEX.

    Overridden from ANSI to allow expressions
    https://www.sqlite.org/expridx.html.
    """

    type = "index_column_definition"
    match_grammar: Matchable = Sequence(
        OneOf(
            Ref("SingleIdentifierGrammar"),  # Column name
            Ref("ExpressionSegment"),  # Expression for simple functions
        ),
        OneOf("ASC", "DESC", optional=True),
    )


class InsertStatementSegment(BaseSegment):
    """An`INSERT` statement.

    https://www.sqlite.org/lang_insert.html
    """

    type = "insert_statement"
    match_grammar = Sequence(
        OneOf(
            Sequence(
                "INSERT",
                Sequence(
                    "OR",
                    OneOf(
                        "ABORT",
                        "FAIL",
                        "IGNORE",
                        "REPLACE",
                        "ROLLBACK",
                    ),
                    optional=True,
                ),
            ),
            # REPLACE is just an alias for INSERT OR REPLACE
            "REPLACE",
        ),
        "INTO",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        OneOf(
            Ref("ValuesClauseSegment"),
            OptionallyBracketed(Ref("SelectableGrammar")),
            Sequence("DEFAULT", "VALUES"),
        ),
    )


class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar: Matchable = Sequence(
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
                    ),
                    OneOf(
                        "DEFERRABLE",
                        Sequence("NOT", "DEFERRABLE"),
                        optional=True,
                    ),
                    OneOf(
                        Sequence("INITIALLY", "IMMEDIATE"),
                        Sequence("INITIALLY", "DEFERRED"),
                        optional=True,
                    ),
                ),
                Ref("CommentClauseSegment", optional=True),
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref("TableEndClauseSegment", optional=True),
    )
