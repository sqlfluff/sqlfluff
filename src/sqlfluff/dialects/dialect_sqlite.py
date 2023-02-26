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
    Delimited,
    TypedParser,
    Nothing,
    AnyNumberOf,
    Anything,
    StartsWith,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_sqlite_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")

sqlite_dialect = ansi_dialect.copy_as("sqlite")

sqlite_dialect.sets("reserved_keywords").clear()
sqlite_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
sqlite_dialect.sets("unreserved_keywords").clear()
sqlite_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)

sqlite_dialect.replace(
    BooleanBinaryOperatorGrammar=OneOf(
        Ref("AndOperatorGrammar"), Ref("OrOperatorGrammar"), "REGEXP"
    ),
    PrimaryKeyGrammar=Sequence(
        "PRIMARY", "KEY", Sequence("AUTOINCREMENT", optional=True)
    ),
    TemporaryTransientGrammar=Ref("TemporaryGrammar"),
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "DATETIME"),
        TypedParser(
            "single_quote", ansi.LiteralSegment, type="date_constructor_literal"
        ),
    ),
    BaseExpressionElementGrammar=OneOf(
        Ref("LiteralGrammar"),
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("ColumnReferenceSegment"),
        Ref("ExpressionSegment"),
        Sequence(
            Ref("DatatypeSegment"),
            Ref("LiteralGrammar"),
        ),
    ),
    AutoIncrementGrammar=Nothing(),
    CommentClauseSegment=Nothing(),
    IntervalExpressionSegment=Nothing(),
    TimeZoneGrammar=Nothing(),
    TrimParametersGrammar=Nothing(),
    LikeGrammar=Sequence("LIKE"),
    OverlapsClauseSegment=Nothing(),
    MLTableExpressionSegment=Nothing(),
    MergeIntoLiteralGrammar=Nothing(),
    SamplingExpressionSegment=Nothing(),
    OrderByClauseTerminators=OneOf(
        "LIMIT",
        # For window functions
        "WINDOW",
        Ref("FrameClauseUnitGrammar"),
    ),
    WhereClauseTerminatorGrammar=OneOf(
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "WINDOW",
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "WINDOW",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("WithDataClauseSegment"),
    ),
    SelectClauseElementTerminatorGrammar=OneOf(
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        Ref("SetOperatorSegment"),
    ),
    FunctionContentsGrammar=AnyNumberOf(
        Ref("ExpressionSegment"),
        # A Cast-like function
        Sequence(Ref("ExpressionSegment"), "AS", Ref("DatatypeSegment")),
        # Trim function
        Sequence(
            Ref("TrimParametersGrammar"),
            Ref("ExpressionSegment", optional=True, exclude=Ref.keyword("FROM")),
            "FROM",
            Ref("ExpressionSegment"),
        ),
        # An extract-like or substring-like function
        Sequence(
            OneOf(Ref("DatetimeUnitSegment"), Ref("ExpressionSegment")),
            "FROM",
            Ref("ExpressionSegment"),
        ),
        Sequence(
            # Allow an optional distinct keyword here.
            Ref.keyword("DISTINCT", optional=True),
            OneOf(
                # Most functions will be using the delimited route
                # but for COUNT(*) or similar we allow the star segment
                # here.
                Ref("StarSegment"),
                Delimited(Ref("FunctionContentsExpressionGrammar")),
            ),
        ),
        Ref(
            "OrderByClauseSegment"
        ),  # used by string_agg (postgres), group_concat (exasol),listagg (snowflake)..
        # like a function call: POSITION ( 'QL' IN 'SQL')
        Sequence(
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
            "IN",
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
        ),
        Ref("IndexColumnDefinitionSegment"),
    ),
    Expression_A_Grammar=Sequence(
        OneOf(
            Ref("Expression_C_Grammar"),
            Sequence(
                OneOf(
                    Ref("SignedSegmentGrammar"),
                    # Ref('TildeSegment'),
                    Ref("NotOperatorGrammar"),
                    # used in CONNECT BY clauses (EXASOL, Snowflake, Postgres...)
                ),
                Ref("Expression_C_Grammar"),
            ),
        ),
        AnyNumberOf(
            OneOf(
                Sequence(
                    OneOf(
                        Sequence(
                            Ref.keyword("NOT", optional=True),
                            Ref("LikeGrammar"),
                        ),
                        Sequence(
                            Ref("BinaryOperatorGrammar"),
                            Ref.keyword("NOT", optional=True),
                        ),
                        # We need to add a lot more here...
                    ),
                    Ref("Expression_C_Grammar"),
                    Sequence(
                        Ref.keyword("ESCAPE"),
                        Ref("Expression_C_Grammar"),
                        optional=True,
                    ),
                ),
                Sequence(
                    Ref.keyword("NOT", optional=True),
                    "IN",
                    Bracketed(
                        OneOf(
                            Delimited(
                                Ref("Expression_A_Grammar"),
                            ),
                            Ref("SelectableGrammar"),
                            ephemeral_name="InExpression",
                        )
                    ),
                ),
                Sequence(
                    Ref.keyword("NOT", optional=True),
                    "IN",
                    Ref("FunctionSegment"),  # E.g. UNNEST()
                ),
                Sequence(
                    "IS",
                    Ref.keyword("NOT", optional=True),
                    Ref("IsClauseGrammar"),
                ),
                Ref("IsNullGrammar"),
                Ref("NotNullGrammar"),
                Ref("CollateGrammar"),
                Sequence(
                    # e.g. NOT EXISTS, but other expressions could be met as
                    # well by inverting the condition with the NOT operator
                    "NOT",
                    Ref("Expression_C_Grammar"),
                ),
                Sequence(
                    Ref.keyword("NOT", optional=True),
                    "BETWEEN",
                    Ref("Expression_B_Grammar"),
                    "AND",
                    Ref("Expression_A_Grammar"),
                ),
            )
        ),
    ),
)


class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Minus, Except or Intersect."""

    type = "set_operator"
    match_grammar: Matchable = OneOf(
        Sequence("UNION", OneOf("DISTINCT", "ALL", optional=True)),
        Sequence(
            OneOf(
                "INTERSECT",
                "EXCEPT",
            ),
            Ref.keyword("ALL", optional=True),
        ),
        exclude=Sequence("EXCEPT", Bracketed(Anything())),
    )


class DatatypeSegment(ansi.DatatypeSegment):
    """A data type segment.

    Supports timestamp with(out) time zone. Doesn't currently support intervals.
    """

    type = "data_type"
    match_grammar: Matchable = OneOf(
        Sequence(
            "DOUBLE",
            "PRECISION",
        ),
        Sequence("UNSIGNED", "BIG", "INT"),
        Sequence(
            OneOf(
                Sequence(
                    OneOf("VARYING", "NATIVE"),
                    OneOf("CHARACTER"),
                ),
                Ref("DatatypeIdentifierSegment"),
            ),
            Bracketed(
                OneOf(
                    Delimited(Ref("ExpressionSegment")),
                    # The brackets might be empty for some cases...
                    optional=True,
                ),
                # There may be no brackets for some data types
                optional=True,
            ),
        ),
    )


class TableEndClauseSegment(BaseSegment):
    """Support WITHOUT ROWID at end of tables.

    https://www.sqlite.org/withoutrowid.html
    """

    type = "table_end_clause_segment"
    match_grammar: Matchable = Sequence("WITHOUT", "ROWID")


class ValuesClauseSegment(ansi.ValuesClauseSegment):
    """A `VALUES` clause like in `INSERT`."""

    type = "values_clause"
    match_grammar: Matchable = Sequence(
        "VALUES",
        Delimited(
            Sequence(
                Bracketed(
                    Delimited(
                        "DEFAULT",
                        Ref("ExpressionSegment"),
                        ephemeral_name="ValuesClauseElements",
                    )
                ),
            ),
        ),
    )


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


class SelectClauseSegment(ansi.SelectClauseSegment):
    """A group of elements in a select target statement."""

    type = "select_clause"
    match_grammar: Matchable = StartsWith(
        "SELECT",
        terminator=OneOf(
            "FROM",
            "WHERE",
            Sequence("ORDER", "BY"),
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
        enforce_whitespace_preceding_terminator=True,
    )

    parse_grammar: Matchable = Ref("SelectClauseSegmentGrammar")


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


class TransactionStatementSegment(ansi.TransactionStatementSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement.

    As per https://www.sqlite.org/lang_transaction.html
    """

    type = "transaction_statement"
    match_grammar: Matchable = Sequence(
        OneOf("BEGIN", "COMMIT", "ROLLBACK", "END"),
        OneOf("TRANSACTION", optional=True),
        Sequence("TO", "SAVEPOINT", Ref("ObjectReferenceSegment"), optional=True),
    )


class PragmaReferenceSegment(ansi.ObjectReferenceSegment):
    """A Pragma object."""

    type = "pragma_reference"


class PragmaStatementSegment(BaseSegment):
    """A Pragma Statement.

    As per https://www.sqlite.org/pragma.html
    """

    type = "pragma_statement"

    _pragma_value = OneOf(
        Ref("LiteralGrammar"),
        Ref("BooleanLiteralGrammar"),
        "YES",
        "NO",
        "ON",
        "OFF",
        "NONE",
        "FULL",
        "INCREMENTAL",
        "DELETE",
        "TRUNCATE",
        "PERSIST",
        "MEMORY",
        "WAL",
        "NORMAL",
        "EXCLUSIVE",
        "FAST",
        "EXTRA",
        "DEFAULT",
        "FILE",
        "PASSIVE",
        "RESTART",
        "RESET",
    )

    match_grammar = Sequence(
        "PRAGMA",
        Ref("PragmaReferenceSegment"),
        Bracketed(_pragma_value, optional=True),
        Sequence(
            Ref("EqualsSegment"), OptionallyBracketed(_pragma_value), optional=True
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar

    parse_grammar: Matchable = OneOf(
        Ref("AlterTableStatementSegment"),
        Ref("CreateIndexStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("CreateTriggerStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("DeleteStatementSegment"),
        Ref("DropIndexStatementSegment"),
        Ref("DropTableStatementSegment"),
        Ref("DropTriggerStatementSegment"),
        Ref("DropViewStatementSegment"),
        Ref("ExplainStatementSegment"),
        Ref("InsertStatementSegment"),
        Ref("PragmaStatementSegment"),
        Ref("SelectableGrammar"),
        Ref("TransactionStatementSegment"),
        Ref("UpdateStatementSegment"),
        Bracketed(Ref("StatementSegment")),
    )
