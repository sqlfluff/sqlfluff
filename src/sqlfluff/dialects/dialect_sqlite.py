"""The sqlite dialect.

https://www.sqlite.org/
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
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
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
    WhitespaceSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_sqlite_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")

sqlite_dialect = ansi_dialect.copy_as(
    "sqlite",
    formatted_name="SQLite",
    docstring="""**Default Casing**: Not specified in the docs,
but through testing it appears that SQLite *stores* column names
in whatever case they were defined, but is always *case-insensitive*
when resolving those names.

**Quotes**: String Literals: ``''`` (or  ``""`` if not otherwise resolved
to an identifier), Identifiers: ``""``, ``[]`` or |back_quotes|. See the
`SQLite Keywords Docs`_ for more details.

The dialect for `SQLite <https://www.sqlite.org/>`_.

.. _`SQLite Keywords Docs`: https://sqlite.org/lang_keywords.html
""",
)

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
        RegexLexer(
            "single_quote",
            r"'([^']|'')*'",
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r"'((?:[^']|'')*)'", 1),
                "escape_replacements": [(r"''", "'")],
            },
        ),
        RegexLexer(
            "double_quote",
            r'"([^"]|"")*"',
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r'"((?:[^"]|"")*)"', 1),
                "escape_replacements": [(r'""', '"')],
            },
        ),
        RegexLexer(
            "back_quote",
            r"`([^`]|``)*`",
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r"`((?:[^`]|``)*)`", 1),
                "escape_replacements": [(r"``", "`")],
            },
        ),
    ]
)

sqlite_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "at_sign_literal",
            r"@[a-zA-Z0-9_]+",
            LiteralSegment,
            segment_kwargs={"type": "at_sign_literal"},
        ),
        RegexLexer(
            "colon_literal",
            r":[a-zA-Z0-9_]+",
            LiteralSegment,
            segment_kwargs={"type": "colon_literal"},
        ),
        RegexLexer(
            "question_literal",
            r"\?[0-9]+",
            LiteralSegment,
            segment_kwargs={"type": "question_literal"},
        ),
        RegexLexer(
            "dollar_literal",
            r"\$[a-zA-Z0-9_]+",
            LiteralSegment,
            segment_kwargs={"type": "dollar_literal"},
        ),
    ],
    before="question",
)

sqlite_dialect.insert_lexer_matchers(
    [
        StringLexer("inline_path_operator", "->>", CodeSegment),
        StringLexer("column_path_operator", "->", CodeSegment),
    ],
    before="greater_than",
)

sqlite_dialect.add(
    BackQuotedIdentifierSegment=TypedParser(
        "back_quote",
        IdentifierSegment,
        type="quoted_identifier",
        # match ANSI's naked identifier casefold, sqlite is case-insensitive.
        casefold=str.upper,
    ),
    ColumnPathOperatorSegment=StringParser(
        "->", SymbolSegment, type="column_path_operator"
    ),
    InlinePathOperatorSegment=StringParser(
        "->>", SymbolSegment, type="column_path_operator"
    ),
    QuestionMarkSegment=StringParser("?", SymbolSegment, type="question_mark"),
    AtSignLiteralSegment=TypedParser(
        "at_sign_literal",
        LiteralSegment,
        type="at_sign_literal",
    ),
    ColonLiteralSegment=TypedParser(
        "colon_literal",
        LiteralSegment,
        type="colon_literal",
    ),
    QuestionLiteralSegment=TypedParser(
        "question_literal",
        LiteralSegment,
        type="question_literal",
    ),
    DollarLiteralSegment=TypedParser(
        "dollar_literal",
        LiteralSegment,
        type="dollar_literal",
    ),
)

sqlite_dialect.replace(
    PrimaryKeyGrammar=Sequence(
        "PRIMARY",
        "KEY",
        OneOf("ASC", "DESC", optional=True),
        Ref("ConflictClauseSegment", optional=True),
        Sequence("AUTOINCREMENT", optional=True),
    ),
    NumericLiteralSegment=OneOf(
        TypedParser("numeric_literal", LiteralSegment, type="numeric_literal"),
        Ref("ParameterizedSegment"),
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[Ref("ParameterizedSegment")]
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
        terminators=[
            Ref("CommaSegment"),
            Ref.keyword("AS"),
        ],
    ),
    AlterTableOptionsGrammar=OneOf(
        Sequence("RENAME", "TO", Ref("SingleIdentifierGrammar")),
        Sequence(
            "RENAME",
            Sequence("COLUMN", optional=True),
            Ref("ColumnReferenceSegment"),
            "TO",
            Ref("SingleIdentifierGrammar"),
        ),
        Sequence(
            "ADD", Sequence("COLUMN", optional=True), Ref("ColumnDefinitionSegment")
        ),
        Sequence(
            "DROP", Sequence("COLUMN", optional=True), Ref("ColumnReferenceSegment")
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
    BinaryOperatorGrammar=ansi_dialect.get_grammar("BinaryOperatorGrammar").copy(
        insert=[
            Ref("ColumnPathOperatorSegment"),
            Ref("InlinePathOperatorSegment"),
        ]
    ),
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
    PostFunctionGrammar=Sequence(
        Ref("FilterClauseGrammar", optional=True),
        Ref("OverClauseSegment", optional=True),
    ),
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
        # Raise Function contents
        OneOf(
            "IGNORE",
            Sequence(
                OneOf(
                    "ABORT",
                    "FAIL",
                    "ROLLBACK",
                ),
                Ref("CommaSegment"),
                Ref("QuotedLiteralSegment"),
            ),
        ),
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
    PatternMatchingGrammar=Sequence(
        Ref.keyword("NOT", optional=True),
        OneOf("GLOB", "REGEXP", "MATCH"),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("SingleQuotedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BackQuotedIdentifierSegment"),
        terminators=[Ref("DotSegment")],
    ),
    # match ANSI's naked identifier casefold, sqlite is case-insensitive.
    QuotedIdentifierSegment=TypedParser(
        "double_quote", IdentifierSegment, type="quoted_identifier", casefold=str.upper
    ),
    SingleQuotedIdentifierSegment=TypedParser(
        "single_quote", IdentifierSegment, type="quoted_identifier", casefold=str.upper
    ),
    ColumnConstraintDefaultGrammar=Ref("ExpressionSegment"),
    FrameClauseUnitGrammar=OneOf("ROWS", "RANGE", "GROUPS"),
)


class FrameClauseSegment(BaseSegment):
    """A frame clause for window functions.

    https://www.sqlite.org/syntax/frame-spec.html
    """

    type = "frame_clause"

    match_grammar: Matchable = Sequence(
        Ref("FrameClauseUnitGrammar"),
        OneOf(
            Sequence("UNBOUNDED", "PRECEDING"),
            Sequence("CURRENT", "ROW"),
            Sequence(Ref("ExpressionSegment"), "PRECEDING"),
            Sequence(
                "BETWEEN",
                OneOf(
                    Sequence("UNBOUNDED", "PRECEDING"),
                    Sequence("CURRENT", "ROW"),
                    Sequence(Ref("ExpressionSegment"), "FOLLOWING"),
                    Sequence(Ref("ExpressionSegment"), "PRECEDING"),
                ),
                "AND",
                OneOf(
                    Sequence("UNBOUNDED", "FOLLOWING"),
                    Sequence("CURRENT", "ROW"),
                    Sequence(Ref("ExpressionSegment"), "FOLLOWING"),
                    Sequence(Ref("ExpressionSegment"), "PRECEDING"),
                ),
            ),
        ),
        Sequence(
            "EXCLUDE",
            OneOf(
                Sequence("NO", "OTHERS"), Sequence("CURRENT", "ROW"), "TIES", "GROUP"
            ),
            optional=True,
        ),
    )


class ParameterizedSegment(BaseSegment):
    """Sqlite allows named and argument based parameters to prevent SQL Injection.

    https://www.sqlite.org/c3ref/bind_blob.html

    """

    type = "parameterized_expression"
    match_grammar = OneOf(
        Ref("AtSignLiteralSegment"),
        Ref("QuestionMarkSegment"),
        Ref("ColonLiteralSegment"),
        Ref("QuestionLiteralSegment"),
        Ref("DollarLiteralSegment"),
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


class ColumnReferenceSegment(ansi.ColumnReferenceSegment):
    """A reference to column, field or alias.

    Also allows `column->path` and `column->>path` for JSON values.
    https://www.sqlite.org/json1.html#jptr
    """

    match_grammar = ansi.ColumnReferenceSegment.match_grammar.copy(
        insert=[
            Sequence(
                OneOf(
                    ansi.ColumnReferenceSegment.match_grammar.copy(),
                    Ref("FunctionSegment"),
                    Ref("BareFunctionSegment"),
                    Ref("LiteralGrammar"),
                ),
            ),
        ]
    )


class TableReferenceSegment(ansi.TableReferenceSegment):
    """A reference to a table.

    Also allows `table->path` and `table->>path` for JSON values.
    https://www.sqlite.org/json1.html#jptr
    """

    match_grammar = ansi.TableReferenceSegment.match_grammar.copy(
        insert=[
            Sequence(
                ansi.TableReferenceSegment.match_grammar.copy(),
                OneOf(
                    Ref("ColumnPathOperatorSegment"),
                    Ref("InlinePathOperatorSegment"),
                ),
                OneOf(
                    Ref("LiteralGrammar"),
                ),
            ),
        ]
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
                Sequence(
                    OneOf("CHARACTER"),
                    OneOf("VARYING", "NATIVE"),
                ),
                Ref("DatatypeIdentifierSegment"),
            ),
            Ref("BracketedArguments", optional=True),
            OneOf("UNSIGNED", optional=True),
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


class ReturningClauseSegment(BaseSegment):
    """A returning clause.

    Per docs https://www.sqlite.org/lang_returning.html
    """

    type = "returning_clause"

    match_grammar = Sequence(
        "RETURNING",
        Indent,
        Delimited(
            Ref("WildcardExpressionSegment"),
            Sequence(
                Ref("ExpressionSegment"),
                Ref("AliasExpressionSegment", optional=True),
            ),
        ),
        Dedent,
    )


class ConflictTargetSegment(BaseSegment):
    """An upsert conflict target.

    https://www.sqlite.org/lang_upsert.html
    """

    type = "conflict_target"
    match_grammar = Sequence(
        Delimited(Ref("IndexColumnDefinitionSegment")),
        Sequence("WHERE", Ref("ExpressionSegment"), optional=True),
    )


class UpsertClauseSegment(BaseSegment):
    """An upsert clause.

    https://www.sqlite.org/lang_upsert.html
    """

    type = "upsert_clause"
    match_grammar = Sequence(
        "ON",
        "CONFLICT",
        Ref("ConflictTargetSegment", optional=True),
        "DO",
        OneOf(
            "NOTHING",
            Sequence(
                "UPDATE",
                "SET",
                Delimited(
                    Sequence(
                        OneOf(
                            Ref("SingleIdentifierGrammar"),
                            Ref("BracketedColumnReferenceListGrammar"),
                        ),
                        Ref("EqualsSegment"),
                        Ref("ExpressionSegment"),
                    ),
                ),
                Sequence(
                    "WHERE",
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
            ),
        ),
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
            Sequence(
                Ref("ValuesClauseSegment"),
                Ref("UpsertClauseSegment", optional=True),
            ),
            Sequence(
                OptionallyBracketed(Ref("SelectableGrammar")),
                Ref("UpsertClauseSegment", optional=True),
            ),
            Ref("DefaultValuesGrammar"),
        ),
        Ref("ReturningClauseSegment", optional=True),
    )


class ConflictClauseSegment(BaseSegment):
    """A conflict clause.

    https://www.sqlite.org/lang_conflict.html
    """

    type = "conflict_clause"
    match_grammar = Sequence(
        "ON",
        "CONFLICT",
        OneOf(
            "ROLLBACK",
            "ABORT",
            "FAIL",
            "IGNORE",
            "REPLACE",
        ),
    )


class ColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """A column option; each CREATE TABLE column can have 0 or more.

    Overriding ColumnConstraintSegment to allow for additional segment parsing
    and to support on conflict clauses.
    """

    match_grammar: Matchable = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),  # Constraint name
            optional=True,
        ),
        OneOf(
            Sequence(
                Ref.keyword("NOT", optional=True),
                "NULL",
                Ref("ConflictClauseSegment", optional=True),
            ),  # NOT NULL or NULL
            Sequence("CHECK", Bracketed(Ref("ExpressionSegment"))),
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                Ref("ColumnConstraintDefaultGrammar"),
            ),
            Ref("PrimaryKeyGrammar"),
            Sequence(
                Ref("UniqueKeyGrammar"), Ref("ConflictClauseSegment", optional=True)
            ),  # UNIQUE
            Ref("AutoIncrementGrammar"),
            Ref("ReferenceDefinitionGrammar"),  # REFERENCES reftable [ ( refcolumn) ]x
            Ref("CommentClauseSegment"),
            Sequence(
                "COLLATE", Ref("CollationReferenceSegment")
            ),  # https://www.sqlite.org/datatype3.html#collation
            Sequence(
                Sequence("GENERATED", "ALWAYS", optional=True),
                "AS",
                Bracketed(Ref("ExpressionSegment")),
                OneOf("STORED", "VIRTUAL", optional=True),
            ),  # https://www.sqlite.org/gencol.html
        ),
        OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
        OneOf(
            Sequence("INITIALLY", "DEFERRED"),
            Sequence("INITIALLY", "IMMEDIATE"),
            optional=True,
        ),
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
                Ref("ConflictClauseSegment", optional=True),
            ),
            Sequence(  # PRIMARY KEY ( column_name [, ... ] ) index_parameters
                Ref("PrimaryKeyGrammar"),
                # Columns making up PRIMARY KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                # Later add support for index_parameters?
                Ref("ConflictClauseSegment", optional=True),
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
        Sequence("WHEN", OptionallyBracketed(Ref("ExpressionSegment")), optional=True),
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


class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement."""

    type = "create_view_statement"
    # https://www.sqlite.org/lang_createview.html
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("TemporaryGrammar", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Optional list of column names
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
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


class DeleteStatementSegment(ansi.DeleteStatementSegment):
    """A `DELETE` statement.

    DELETE FROM <table name> [ WHERE <search condition> ]
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar: Matchable = Sequence(
        "DELETE",
        Ref("FromClauseSegment"),
        Ref("WhereClauseSegment", optional=True),
        Ref("ReturningClauseSegment", optional=True),
    )


class UpdateStatementSegment(ansi.UpdateStatementSegment):
    """An `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    """

    type = "update_statement"
    match_grammar: Matchable = Sequence(
        "UPDATE",
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
        Indent,
        Ref("TableReferenceSegment"),
        Ref("AliasExpressionSegment", optional=True),
        Dedent,
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("ReturningClauseSegment", optional=True),
    )


class SetClauseSegment(ansi.SetClauseSegment):
    """A set clause."""

    match_grammar = Sequence(
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("BracketedColumnReferenceListGrammar"),
        ),
        Ref("EqualsSegment"),
        Ref("ExpressionSegment"),
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


class GroupingSetsClauseSegment(ansi.GroupingSetsClauseSegment):
    """`GROUPING SETS` clause within the `GROUP BY` clause.

    This is `Nothing` for SQLite.
    """

    match_grammar = Nothing()


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


class CreateVirtualTableStatementSegment(BaseSegment):
    """A `CREATE VIRTUAL TABLE` statement.

    As per https://www.sqlite.org/lang_createvtab.html
    """

    type = "create_virtual_table_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "VIRTUAL",
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        "USING",
        Ref("SingleIdentifierGrammar"),
        Bracketed(
            Delimited(
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("SingleIdentifierGrammar"),
                ),
            ),
            optional=True,
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = OneOf(
        Ref("AlterTableStatementSegment"),
        Ref("CreateIndexStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("CreateVirtualTableStatementSegment"),
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
