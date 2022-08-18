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


class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint_segment"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar: Matchable = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),  # Constraint name
            optional=True,
        ),
        OneOf(
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
            Sequence("CHECK", Bracketed(Ref("ExpressionSegment"))),
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    Ref("BareFunctionSegment"),
                ),
            ),
            Ref("PrimaryKeyGrammar"),
            Ref("UniqueKeyGrammar"),  # UNIQUE
            "AUTO_INCREMENT",  # AUTO_INCREMENT (MySQL)
            Ref("ReferenceDefinitionGrammar"),  # REFERENCES reftable [ ( refcolumn) ]x
            OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
            OneOf(
                Sequence("INITIALLY", "DEFERRED"),
                Sequence("INITIALLY", "IMMEDIATE"),
                optional=True,
            ),
            Ref("CommentClauseSegment"),
        ),
    )
