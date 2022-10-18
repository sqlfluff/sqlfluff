"""The sqlite dialect.

https://www.sqlite.org/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    Bracketed,
    Matchable,
    OneOf,
    OptionallyBracketed,
    Ref,
    Sequence,
)
from sqlfluff.dialects import dialect_ansi as ansi

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
            Ref("DefaultValuesGrammar"),
        ),
    )


class ColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """Overriding ColumnConstraintSegment to allow for additional segment parsing."""

    match_grammar = ansi.ColumnConstraintSegment.match_grammar.copy(
        insert=[
            OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
            OneOf(
                Sequence("INITIALLY", "DEFERRED"),
                Sequence("INITIALLY", "IMMEDIATE"),
                optional=True,
            ),
        ],
    )


class TableConstraintSegment(ansi.TableConstraintSegment):
    """Overriding TableConstraintSegment to allow for additional segment parsing."""

    match_grammar: Matchable = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        OneOf(
            # CHECK ( <expr> )
            Sequence("CHECK", Bracketed(Ref("ExpressionSegment"))),
            Sequence(  # UNIQUE ( column_name [, ... ] )
                "UNIQUE",
                Ref("BracketedColumnReferenceListGrammar"),
                # Later add support for index_parameters?
            ),
            Sequence(  # PRIMARY KEY ( column_name [, ... ] ) index_parameters
                Ref("PrimaryKeyGrammar"),
                # Columns making up PRIMARY KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                # Later add support for index_parameters?
            ),
            Sequence(  # FOREIGN KEY ( column_name [, ... ] )
                # REFERENCES reftable [ ( refcolumn [, ... ] ) ]
                Ref("ForeignKeyGrammar"),
                # Local columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                Ref(
                    "ReferenceDefinitionGrammar"
                ),  # REFERENCES reftable [ ( refcolumn) ]
            ),
        ),
        OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
        OneOf(
            Sequence("INITIALLY", "DEFERRED"),
            Sequence("INITIALLY", "IMMEDIATE"),
            optional=True,
        ),
    )
