"""The sqlite dialect.

https://www.sqlite.org/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    CommentSegment,
    Delimited,
    LiteralSegment,
    Matchable,
    NewlineSegment,
    Nothing,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    RegexLexer,
    Sequence,
    TypedParser,
    WhitespaceSegment,
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

sqlite_dialect.patch_lexer_matchers(
    [
        # SQLite allows block comments to be terminated by end of input
        RegexLexer(
            "block_comment",
            r"\/\*([^\*]|\*(?!\/))*(\*\/|\Z)",
            CommentSegment,
            subdivider=RegexLexer(
                "newline",
                r"\r\n|\n",
                NewlineSegment,
            ),
            trim_post_subdivide=RegexLexer(
                "whitespace",
                r"[^\S\r\n]+",
                WhitespaceSegment,
            ),
        ),
    ]
)

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
        TypedParser("single_quote", LiteralSegment, type="date_constructor_literal"),
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
    FetchClauseSegment=Nothing(),
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
    GroupByClauseTerminatorGrammar=OneOf(
        Sequence("ORDER", "BY"),
        "LIMIT",
        "HAVING",
        "WINDOW",
    ),
    PostFunctionGrammar=Ref("FilterClauseGrammar"),
    IgnoreRespectNullsGrammar=Nothing(),
    SelectClauseTerminatorGrammar=OneOf(
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
    # NOTE: This block was copy/pasted from dialect_ansi.py with these changes made:
    #  - "PRIOR" keyword removed from Expression_A_Unary_Operator_Grammar
    Expression_A_Unary_Operator_Grammar=OneOf(
        Ref(
            "SignedSegmentGrammar",
            exclude=Sequence(Ref("QualifiedNumericLiteralSegment")),
        ),
        Ref("TildeSegment"),
        Ref("NotOperatorGrammar"),
    ),
    IsDistinctFromGrammar=Sequence(
        "IS",
        Ref.keyword("NOT", optional=True),
        Sequence("DISTINCT", "FROM", optional=True),
    ),
    NanLiteralSegment=Nothing(),
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
            Ref("BracketedArguments", optional=True),
        ),
    )


class TableEndClauseSegment(BaseSegment):
    """Support Table Options at end of tables.

    https://www.sqlite.org/syntax/table-options.html
    """

    type = "table_end_clause_segment"
    match_grammar: Matchable = Delimited(Sequence("WITHOUT", "ROWID"), "STRICT")


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
                    ),
                    parse_mode=ParseMode.GREEDY,
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


class CreateTriggerStatementSegment(ansi.CreateTriggerStatementSegment):
    """Create Trigger Statement.

    https://www.sqlite.org/lang_createtrigger.html
    """

    type = "create_trigger"

    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("TemporaryGrammar", optional=True),
        "TRIGGER",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TriggerReferenceSegment"),
        OneOf("BEFORE", "AFTER", Sequence("INSTEAD", "OF"), optional=True),
        OneOf(
            "DELETE",
            "INSERT",
            Sequence(
                "UPDATE",
                Sequence(
                    "OF",
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                    optional=True,
                ),
            ),
        ),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence("FOR", "EACH", "ROW", optional=True),
        Sequence("WHEN", Bracketed(Ref("ExpressionSegment")), optional=True),
        "BEGIN",
        Delimited(
            Ref("UpdateStatementSegment"),
            Ref("InsertStatementSegment"),
            Ref("DeleteStatementSegment"),
            Ref("SelectableGrammar"),
            delimiter=AnyNumberOf(Ref("DelimiterGrammar"), min_times=1),
            allow_gaps=True,
            allow_trailing=True,
        ),
        "END",
    )


class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    Replaces (without overriding) ANSI to remove Eager Matcher
    """

    type = "select_statement"

    match_grammar = Sequence(
        Ref("SelectClauseSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("OverlapsClauseSegment", optional=True),
        Ref("NamedWindowSegment", optional=True),
    )


class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    Replaces (without overriding) ANSI to remove Eager Matcher
    """

    type = "select_statement"
    # Remove the Limit and Window statements from ANSI
    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("FetchClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ]
    )


class CreateIndexStatementSegment(ansi.CreateIndexStatementSegment):
    """A `CREATE INDEX` statement.

    As per https://www.sqlite.org/lang_createindex.html
    """

    type = "create_index_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref.keyword("UNIQUE", optional=True),
        "INDEX",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence(
            Bracketed(
                Delimited(
                    Ref("IndexColumnDefinitionSegment"),
                ),
            )
        ),
        Ref("WhereClauseSegment", optional=True),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = OneOf(
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
