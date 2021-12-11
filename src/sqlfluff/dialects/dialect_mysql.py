"""The MySQL dialect.

For now the only change is the parsing of comments.
https://dev.mysql.com/doc/refman/8.0/en/differences-from-ansi.html
"""

from sqlfluff.core.parser import (
    BaseSegment,
    Ref,
    AnyNumberOf,
    Sequence,
    OneOf,
    Bracketed,
    RegexLexer,
    CommentSegment,
    NamedParser,
    CodeSegment,
    StringParser,
    SymbolSegment,
    Delimited,
    RegexParser,
    Anything,
)
from sqlfluff.core.dialects import load_raw_dialect

ansi_dialect = load_raw_dialect("ansi")
mysql_dialect = ansi_dialect.copy_as("mysql")

mysql_dialect.patch_lexer_matchers(
    [
        RegexLexer(
            "inline_comment",
            r"(-- |#)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("-- ", "#")},
        )
    ]
)

# Reserve USE, FORCE & IGNORE
mysql_dialect.sets("unreserved_keywords").difference_update(
    [
        "FORCE",
        "IGNORE",
        "USE",
        "SQL_BUFFER_RESULT",
        "SQL_NO_CACHE",
        "SQL_CACHE",
        "DUMPFILE",
        "SKIP",
        "LOCKED",
        "CLASS_ORIGIN",
        "SUBCLASS_ORIGIN",
        "RETURNED_SQLSTATE",
        "MESSAGE_TEXT",
        "MYSQL_ERRNO",
        "CONSTRAINT_CATALOG",
        "CONSTRAINT_SCHEMA",
        "CONSTRAINT_NAME",
        "CATALOG_NAME",
        "SCHEMA_NAME",
        "TABLE_NAME",
        "COLUMN_NAME",
        "CURSOR_NAME",
        "STACKED",
    ]
)
mysql_dialect.sets("reserved_keywords").update(
    [
        "FORCE",
        "IGNORE",
        "USE",
        "SQL_BUFFER_RESULT",
        "SQL_NO_CACHE",
        "SQL_CACHE",
        "DUMPFILE",
        "SKIP",
        "LOCKED",
        "CLASS_ORIGIN",
        "SUBCLASS_ORIGIN",
        "RETURNED_SQLSTATE",
        "MESSAGE_TEXT",
        "MYSQL_ERRNO",
        "CONSTRAINT_CATALOG",
        "CONSTRAINT_SCHEMA",
        "CONSTRAINT_NAME",
        "CATALOG_NAME",
        "SCHEMA_NAME",
        "TABLE_NAME",
        "COLUMN_NAME",
        "CURSOR_NAME",
        "STACKED",
        "ALGORITHM",
        "LOCK",
        "DEFAULT",
        "INPLACE",
        "COPY",
        "NONE",
        "SHARED",
        "EXCLUSIVE",
    ]
)

mysql_dialect.replace(
    QuotedIdentifierSegment=NamedParser(
        "back_quote",
        CodeSegment,
        name="quoted_identifier",
        type="identifier",
        trim_chars=("`",),
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("DoubleQuotedLiteralSegment"),
        ]
    ),
    FromClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "FromClauseTerminatorGrammar"
    ).copy(
        insert=[
            Ref("IndexHintClauseSegment"),
            Ref("SelectPartitionClauseSegment"),
            Ref("ForClauseSegment"),
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
        ]
    ),
    BaseExpressionElementGrammar=ansi_dialect.get_grammar(
        "BaseExpressionElementGrammar"
    ).copy(
        insert=[
            Ref("SessionVariableNameSegment"),
            Ref("LocalVariableNameSegment"),
        ]
    ),
)

mysql_dialect.add(
    DoubleQuotedLiteralSegment=NamedParser(
        "double_quote",
        CodeSegment,
        name="quoted_literal",
        type="literal",
        trim_chars=('"',),
    ),
    AtSignLiteralSegment=NamedParser(
        "atsign",
        CodeSegment,
        name="atsign_literal",
        type="literal",
        trim_chars=("@",),
    ),
)


@mysql_dialect.segment(replace=True)
class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        OneOf(  # Column type
            # DATETIME and TIMESTAMP take special logic
            AnyNumberOf(
                Ref("DatatypeSegment"),
                max_times=1,
                min_times=1,
                exclude=OneOf("DATETIME", "TIMESTAMP"),
            ),
            Sequence(
                OneOf("DATETIME", "TIMESTAMP"),
                Sequence(
                    Bracketed(Ref("NumericLiteralSegment"), optional=True),
                    optional=True,
                ),
                Sequence(Sequence("NOT", optional=True), "NULL", optional=True),
                Sequence("DEFAULT", optional=True),
                OneOf(
                    Sequence(
                        "CURRENT_TIMESTAMP",
                        Sequence(
                            Bracketed(Ref("NumericLiteralSegment")),
                            optional=True,
                        ),
                    ),
                    Ref("NumericLiteralSegment"),
                    Ref("QuotedLiteralSegment"),
                    optional=True,
                ),
                Sequence(
                    Sequence("ON", "UPDATE", optional=True),
                    "CURRENT_TIMESTAMP",
                    Sequence(
                        Bracketed(Ref("NumericLiteralSegment")),
                        optional=True,
                    ),
                    optional=True,
                ),
            ),
        ),
        Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
        AnyNumberOf(
            Ref("ColumnConstraintSegment", optional=True),
        ),
    )


@mysql_dialect.segment(replace=True)
class CreateTableStatementSegment(
    ansi_dialect.get_segment("CreateTableStatementSegment")  # type: ignore
):
    """Create table segment.

    https://dev.mysql.com/doc/refman/8.0/en/create-table.html
    """

    match_grammar = ansi_dialect.get_segment(
        "CreateTableStatementSegment"
    ).match_grammar.copy(
        insert=[
            AnyNumberOf(
                Sequence(
                    Ref.keyword("DEFAULT", optional=True),
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment"),
                    OneOf(Ref("LiteralGrammar"), Ref("ParameterNameSegment")),
                ),
            ),
        ],
    )


@mysql_dialect.segment(replace=True)
class TableConstraintSegment(BaseSegment):
    """A table constraint, e.g. for CREATE TABLE."""

    type = "table_constraint_segment"
    # Later add support for CHECK constraint, others?
    # e.g. CONSTRAINT constraint_1 PRIMARY KEY(column_1)
    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        OneOf(
            Sequence(  # UNIQUE [INDEX | KEY] [index_name] ( column_name [, ... ] )
                "UNIQUE",
                OneOf("INDEX", "KEY", optional=True),
                Ref("ObjectReferenceSegment", optional=True),
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
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                # Later add support for [MATCH FULL/PARTIAL/SIMPLE] ?
                # Later add support for [ ON DELETE/UPDATE action ] ?
            ),
        ),
    )


mysql_dialect.add(
    DoubleForwardSlashSegment=StringParser(
        "//", SymbolSegment, name="doubleforwardslash", type="statement_terminator"
    ),
    DoubleDollarSignSegment=StringParser(
        "$$", SymbolSegment, name="doubledollarsign", type="statement_terminator"
    ),
    AtSignSignSegment=StringParser(
        "@", SymbolSegment, name="atsign", type="user_designator"
    ),
    OutputParameterSegment=StringParser(
        "OUT", SymbolSegment, name="inputparameter", type="parameter_direction"
    ),
    InputParameterSegment=StringParser(
        "IN", SymbolSegment, name="outputparameter", type="parameter_direction"
    ),
    InputOutputParameterSegment=StringParser(
        "INOUT", SymbolSegment, name="inputoutputparameter", type="parameter_direction"
    ),
    ProcedureParameterGrammar=OneOf(
        Sequence(
            OneOf(
                Ref("OutputParameterSegment"),
                Ref("InputParameterSegment"),
                Ref("InputOutputParameterSegment"),
                optional=True,
            ),
            Ref("ParameterNameSegment", optional=True),
            Ref("DatatypeSegment"),
        ),
        Ref("DatatypeSegment"),
    ),
    LocalVariableNameSegment=RegexParser(
        r"`?[a-zA-Z0-9_]*`?",
        CodeSegment,
        name="declared_variable",
        type="variable",
    ),
    SessionVariableNameSegment=RegexParser(
        r"[@][a-zA-Z0-9_]*",
        CodeSegment,
        name="declared_variable",
        type="variable",
    ),
)

mysql_dialect.replace(
    DelimiterSegment=OneOf(Ref("SemicolonSegment"), Ref("TildeSegment")),
    TildeSegment=StringParser(
        "~", SymbolSegment, name="tilde", type="statement_terminator"
    ),
    ParameterNameSegment=RegexParser(
        r"`?[A-Za-z0-9_]*`?", CodeSegment, name="parameter", type="parameter"
    ),
    SingleIdentifierGrammar=ansi_dialect.get_grammar("SingleIdentifierGrammar").copy(
        insert=[Ref("SessionVariableNameSegment")]
    ),
)

mysql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "atsign",
            r"[@][a-zA-Z0-9_]*",
            CodeSegment,
        ),
    ],
    before="code",
)


@mysql_dialect.segment()
class DeclareStatement(BaseSegment):
    """DECLARE statement.

    https://dev.mysql.com/doc/refman/8.0/en/declare-local-variable.html
    https://dev.mysql.com/doc/refman/8.0/en/declare-handler.html
    https://dev.mysql.com/doc/refman/8.0/en/declare-condition.html
    https://dev.mysql.com/doc/refman/8.0/en/declare-cursor.html
    """

    type = "declare_statement"

    match_grammar = OneOf(
        Sequence(
            "DECLARE",
            Ref("NakedIdentifierSegment"),
            "CURSOR",
            "FOR",
            Ref("StatementSegment"),
        ),
        Sequence(
            "DECLARE",
            OneOf("CONTINUE", "EXIT", "UNDO"),
            "HANDLER",
            "FOR",
            OneOf(
                "SQLEXCEPTION",
                "SQLWARNING",
                Sequence("NOT", "FOUND"),
                Sequence(
                    "SQLSTATE",
                    Ref.keyword("VALUE", optional=True),
                    Ref("QuotedLiteralSegment"),
                ),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("NakedIdentifierSegment"),
                ),
            ),
            Sequence(Ref("StatementSegment")),
        ),
        Sequence(
            "DECLARE",
            Ref("NakedIdentifierSegment"),
            "CONDITION",
            "FOR",
            OneOf(Ref("QuotedLiteralSegment"), Ref("NumericLiteralSegment")),
        ),
        Sequence(
            "DECLARE",
            Ref("LocalVariableNameSegment"),
            Ref("DatatypeSegment"),
            Sequence(
                Ref.keyword("DEFAULT"),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("FunctionSegment"),
                ),
                optional=True,
            ),
        ),
    )


@mysql_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("DelimiterStatement"),
            Ref("CreateProcedureStatementSegment"),
            Ref("DeclareStatement"),
            Ref("SetAssignmentStatementSegment"),
            Ref("IfExpressionStatement"),
            Ref("WhileStatementSegment"),
            Ref("IterateStatementSegment"),
            Ref("RepeatStatementSegment"),
            Ref("LoopStatementSegment"),
            Ref("CallStoredProcedureSegment"),
            Ref("PrepareSegment"),
            Ref("ExecuteSegment"),
            Ref("DeallocateSegment"),
            Ref("GetDiagnosticsSegment"),
            Ref("ResignalSegment"),
            Ref("CursorOpenCloseSegment"),
            Ref("CursorFetchSegment"),
            Ref("AlterTableStatementSegment"),
        ],
    )


@mysql_dialect.segment()
class DelimiterStatement(BaseSegment):
    """DELIMITER statement."""

    type = "delimiter_statement"

    match_grammar = Ref.keyword("DELIMITER")


@mysql_dialect.segment()
class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE PROCEDURE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/create-procedure.html
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("DefinerSegment", optional=True),
        "PROCEDURE",
        Ref("FunctionNameSegment"),
        Ref("ProcedureParameterListGrammar", optional=True),
        Ref("CommentClauseSegment", optional=True),
        Ref("CharacteristicStatement", optional=True),
        Ref("FunctionDefinitionGrammar"),
    )


@mysql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION` statement."""

    match_grammar = Ref("TransactionStatementSegment")


@mysql_dialect.segment()
class CharacteristicStatement(BaseSegment):
    """A Characteristics statement for functions/procedures."""

    type = "characteristic_statement"

    match_grammar = Sequence(
        OneOf("DETERMINISTIC", Sequence("NOT", "DETERMINISTIC")),
        Sequence("LANGUAGE", "SQL", optional=True),
        OneOf(
            Sequence("CONTAINS", "SQL", optional=True),
            Sequence("NO", "SQL", optional=True),
            Sequence("READS", "SQL", "DATA", optional=True),
            Sequence("MODIFIES", "SQL", "DATA", optional=True),
            optional=True,
        ),
        Sequence("SQL", "SECURITY", OneOf("DEFINER", "INVOKER"), optional=True),
    )


@mysql_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    https://dev.mysql.com/doc/refman/8.0/en/create-procedure.html
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("DefinerSegment", optional=True),
        "FUNCTION",
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        Sequence(
            "RETURNS",
            Ref("DatatypeSegment"),
        ),
        Ref("CommentClauseSegment", optional=True),
        Ref("CharacteristicStatement"),
        Ref("FunctionDefinitionGrammar"),
    )


@mysql_dialect.segment(replace=True)
class AlterTableStatementSegment(BaseSegment):
    """An `ALTER TABLE .. ALTER COLUMN` statement.

    Overriding ANSI to add `CHANGE COLUMN` and `DROP COLUMN` support.

    https://dev.mysql.com/doc/refman/8.0/en/alter-table.html

    """

    type = "alter_table_statement"
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        Delimited(
            OneOf(
                # Table options
                Sequence(
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment", optional=True),
                    OneOf(Ref("LiteralGrammar"), Ref("NakedIdentifierSegment")),
                ),
                # Add things
                Sequence(
                    OneOf("ADD", "MODIFY"),
                    Ref.keyword("COLUMN", optional=True),
                    Ref("ColumnDefinitionSegment"),
                    OneOf(
                        Sequence(
                            OneOf("FIRST", "AFTER"), Ref("ColumnReferenceSegment")
                        ),
                        # Bracketed Version of the same
                        Ref("BracketedColumnReferenceListGrammar"),
                        optional=True,
                    ),
                ),
                # Change column
                Sequence(
                    "CHANGE",
                    Ref.keyword("COLUMN", optional=True),
                    Ref("ColumnReferenceSegment"),
                    Ref("ColumnDefinitionSegment"),
                    OneOf(
                        Sequence(
                            OneOf(
                                "FIRST",
                                Sequence("AFTER", Ref("ColumnReferenceSegment")),
                            ),
                        ),
                        optional=True,
                    ),
                ),
                # Drop column
                Sequence(
                    "DROP",
                    Ref.keyword("COLUMN", optional=True),
                    Ref("ColumnReferenceSegment"),
                ),
                # Rename
                Sequence(
                    "RENAME",
                    OneOf("AS", "TO", optional=True),
                    Ref("TableReferenceSegment"),
                ),
            ),
        ),
    )


@mysql_dialect.segment(replace=True)
class DropStatementSegment(BaseSegment):
    """A `DROP` statement."""

    type = "drop_statement"

    match_grammar = Sequence(
        "DROP",
        OneOf(
            "TABLE",
            "VIEW",
            "USER",
            "FUNCTION",
            "PROCEDURE",
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
    )


@mysql_dialect.segment()
class ProcedureParameterListGrammar(BaseSegment):
    """The parameters for a procedure ie. `(in/out/inout name datatype)`."""

    match_grammar = Bracketed(
        Delimited(
            Ref("ProcedureParameterGrammar"),
            delimiter=Ref("CommaSegment"),
            optional=True,
        ),
    )


@mysql_dialect.segment()
class SetAssignmentStatementSegment(BaseSegment):
    """A `SET` statement.

    https://dev.mysql.com/doc/refman/8.0/en/set-variable.html
    """

    type = "set_statement"

    match_grammar = Sequence(
        "SET",
        OneOf(Ref("SessionVariableNameSegment"), Ref("LocalVariableNameSegment")),
        Ref("EqualsSegment"),
        AnyNumberOf(
            Ref("QuotedLiteralSegment"),
            Ref("DoubleQuotedLiteralSegment"),
            Ref("SessionVariableNameSegment"),
            Ref("LocalVariableNameSegment"),
            Ref("FunctionSegment"),
            Ref("ArithmeticBinaryOperatorGrammar"),
        ),
    )


@mysql_dialect.segment(replace=True)
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement.

    https://dev.mysql.com/doc/refman/8.0/en/commit.html
    https://dev.mysql.com/doc/refman/8.0/en/begin-end.html
    """

    type = "transaction_statement"

    match_grammar = OneOf(
        Sequence("START", "TRANSACTION"),
        Sequence(
            Sequence(
                Ref("SingleIdentifierGrammar"), Ref("ColonSegment"), optional=True
            ),
            Sequence(
                "BEGIN",
                Ref.keyword("WORK", optional=True),
                Ref("StatementSegment"),
            ),
        ),
        Sequence(
            "LEAVE",
            Ref("SingleIdentifierGrammar", optional=True),
        ),
        Sequence(
            "COMMIT",
            Ref.keyword("WORK", optional=True),
            Sequence("AND", Ref.keyword("NO", optional=True), "CHAIN", optional=True),
        ),
        Sequence(
            "ROLLBACK",
            Ref.keyword("WORK", optional=True),
        ),
        Sequence(
            "END",
            Ref("SingleIdentifierGrammar", optional=True),
        ),
    )


@mysql_dialect.segment()
class IfExpressionStatement(BaseSegment):
    """IF-THEN-ELSE-ELSEIF-END IF statement.

    https://dev.mysql.com/doc/refman/8.0/en/if.html
    """

    type = "if_then_statement"

    match_grammar = AnyNumberOf(
        Sequence(
            "IF",
            Ref("ExpressionSegment"),
            "THEN",
            Ref("StatementSegment"),
        ),
        Sequence(
            "ELSEIF",
            Ref("ExpressionSegment"),
            "THEN",
            Ref("StatementSegment"),
        ),
        Sequence("ELSE", Ref("StatementSegment"), optional=True),
    )


@mysql_dialect.segment()
class DefinerSegment(BaseSegment):
    """This is the body of a `CREATE FUNCTION` statement."""

    type = "definer_segment"

    match_grammar = Sequence(
        "DEFINER",
        Ref("EqualsSegment"),
        Ref("SingleIdentifierGrammar"),
        Ref("AtSignLiteralSegment"),
        Ref("SingleIdentifierGrammar"),
    )


@mysql_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = Sequence(
        OneOf("DISTINCT", "ALL", "DISTINCTROW", optional=True),
        Ref.keyword("HIGH_PRIORITY", optional=True),
        Ref.keyword("STRAIGHT_JOIN", optional=True),
        Ref.keyword("SQL_SMALL_RESULT", optional=True),
        Ref.keyword("SQL_BIG_RESULT", optional=True),
        Ref.keyword("SQL_BUFFER_RESULT", optional=True),
        Ref.keyword("SQL_CACHE", optional=True),
        Ref.keyword("SQL_NO_CACHE", optional=True),
        Ref.keyword("SQL_CALC_FOUND_ROWS", optional=True),
        optional=True,
    )


@mysql_dialect.segment()
class IntoClauseSegment(BaseSegment):
    """This is an `INTO` clause for assigning variables in a select statement.

    https://dev.mysql.com/doc/refman/5.7/en/load-data.html
    https://dev.mysql.com/doc/refman/5.7/en/select-into.html
    """

    type = "into_clause"

    match_grammar = Sequence(
        "INTO",
        OneOf(
            Delimited(
                AnyNumberOf(
                    Ref("SessionVariableNameSegment"),
                    Ref("LocalVariableNameSegment"),
                ),
                Sequence("DUMPFILE", Ref("QuotedLiteralSegment")),
                Sequence(
                    "OUTFILE",
                    Ref("QuotedLiteralSegment"),
                    Sequence(
                        "CHARACTER", "SET", Ref("NakedIdentifierSegment"), optional=True
                    ),
                    Sequence(
                        OneOf("FIELDS", "COLUMNS"),
                        Sequence(
                            "TERMINATED",
                            "BY",
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                        Sequence(
                            Ref.keyword("OPTIONALLY", optional=True),
                            "ENCLOSED",
                            "BY",
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "ESCAPED", "BY", Ref("QuotedLiteralSegment"), optional=True
                        ),
                        optional=True,
                    ),
                    Sequence(
                        "LINES",
                        Sequence(
                            "STARTING", "BY", Ref("QuotedLiteralSegment"), optional=True
                        ),
                        Sequence(
                            "TERMINATED",
                            "BY",
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                        optional=True,
                    ),
                ),
            ),
        ),
    )


@mysql_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    type = "select_statement"
    match_grammar = ansi_dialect.get_segment(
        "UnorderedSelectStatementSegment"
    ).match_grammar.copy()
    match_grammar.terminator = (
        match_grammar.terminator.copy(
            insert=[Ref("IntoClauseSegment")],
            before=Ref("SetOperatorSegment"),
        )
        .copy(insert=[Ref("ForClauseSegment")])
        .copy(insert=[Ref("IndexHintClauseSegment")])
        .copy(insert=[Ref("SelectPartitionClauseSegment")])
    )

    parse_grammar = (
        ansi_dialect.get_segment("UnorderedSelectStatementSegment")
        .parse_grammar.copy(
            insert=[Ref("IntoClauseSegment", optional=True)],
            before=Ref("FromClauseSegment", optional=True),
        )
        .copy(insert=[Ref("ForClauseSegment", optional=True)])
        .copy(
            insert=[Ref("IndexHintClauseSegment", optional=True)],
            before=Ref("WhereClauseSegment", optional=True),
        )
        .copy(
            insert=[Ref("SelectPartitionClauseSegment", optional=True)],
            before=Ref("WhereClauseSegment", optional=True),
        )
    )


@mysql_dialect.segment(replace=True)
class SelectClauseElementSegment(BaseSegment):
    """An element in the targets of a select statement."""

    type = "select_clause_element"

    match_grammar = ansi_dialect.get_segment(
        "SelectClauseElementSegment"
    ).match_grammar.copy()

    parse_grammar = ansi_dialect.get_segment(
        "SelectClauseElementSegment"
    ).parse_grammar.copy()


@mysql_dialect.segment(replace=True)
class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement."""

    type = "select_clause"
    match_grammar = ansi_dialect.get_segment("SelectClauseSegment").match_grammar.copy()
    match_grammar.terminator = match_grammar.terminator.copy(
        insert=[Ref("IntoKeywordSegment")]
    )
    parse_grammar = ansi_dialect.get_segment("SelectClauseSegment").parse_grammar.copy()


@mysql_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    https://dev.mysql.com/doc/refman/5.7/en/select.html
    """

    type = "select_statement"
    match_grammar = ansi_dialect.get_segment(
        "SelectStatementSegment"
    ).match_grammar.copy()

    # Inherit most of the parse grammar from the original.
    parse_grammar = UnorderedSelectStatementSegment.parse_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ]
    )


@mysql_dialect.segment()
class ForClauseSegment(BaseSegment):
    """This is the body of a `FOR` clause."""

    type = "for_clause"

    match_grammar = OneOf(
        Sequence(
            Sequence(
                "FOR",
                OneOf("UPDATE", "SHARE"),
            ),
            Sequence("OF", Delimited(Ref("NakedIdentifierSegment")), optional=True),
            OneOf("NOWAIT", Sequence("SKIP", "LOCKED"), optional=True),
        ),
        Sequence("LOCK", "IN", "SHARE", "MODE"),
        optional=True,
    )


@mysql_dialect.segment()
class IndexHintClauseSegment(BaseSegment):
    """This is the body of an index hint clause."""

    type = "index_hint_clause"

    match_grammar = Sequence(
        OneOf("USE", "IGNORE", "FORCE"),
        OneOf("INDEX", "KEY"),
        Sequence(
            "FOR",
            OneOf(
                "JOIN", Sequence("ORDER", "BY"), Sequence("GROUP", "BY"), optional=True
            ),
            optional=True,
        ),
        Bracketed(Ref("ObjectReferenceSegment")),
        Ref("JoinOnConditionSegment", optional=True),
    )


@mysql_dialect.segment()
class CallStoredProcedureSegment(BaseSegment):
    """This is a CALL statement used to execute a stored procedure.

    https://dev.mysql.com/doc/refman/8.0/en/call.html
    """

    type = "call_segment"

    match_grammar = Sequence(
        "CALL",
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("QuotedIdentifierSegment"),
        ),
        Bracketed(
            AnyNumberOf(
                Delimited(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("DoubleQuotedLiteralSegment"),
                    Ref("SessionVariableNameSegment"),
                    Ref("LocalVariableNameSegment"),
                    Ref("FunctionSegment"),
                ),
            ),
        ),
    )


@mysql_dialect.segment()
class SelectPartitionClauseSegment(BaseSegment):
    """This is the body of a partition clause."""

    type = "partition_clause"

    match_grammar = Sequence(
        "PARTITION",
        Bracketed(Delimited(Ref("ObjectReferenceSegment"))),
    )


@mysql_dialect.segment()
class WhileStatementSegment(BaseSegment):
    """A `WHILE-DO-END WHILE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/while.html
    """

    type = "while_statement"

    match_grammar = OneOf(
        Sequence(
            Sequence(
                Ref("SingleIdentifierGrammar"), Ref("ColonSegment"), optional=True
            ),
            Sequence(
                "WHILE",
                Ref("ExpressionSegment"),
                "DO",
                AnyNumberOf(
                    Ref("StatementSegment"),
                ),
            ),
        ),
        Sequence(
            "END",
            "WHILE",
            Ref("SingleIdentifierGrammar", optional=True),
        ),
    )


@mysql_dialect.segment()
class PrepareSegment(BaseSegment):
    """This is the body of a `PREPARE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/prepare.html
    """

    type = "prepare_segment"

    match_grammar = Sequence(
        "PREPARE",
        Ref("NakedIdentifierSegment"),
        "FROM",
        OneOf(
            Ref("QuotedLiteralSegment"),
            Ref("SessionVariableNameSegment"),
            Ref("LocalVariableNameSegment"),
        ),
    )


@mysql_dialect.segment()
class GetDiagnosticsSegment(BaseSegment):
    """This is the body of a `GET DIAGNOSTICS` statement.

    https://dev.mysql.com/doc/refman/8.0/en/get-diagnostics.html
    """

    type = "get_diagnostics_segment"

    match_grammar = Sequence(
        "GET",
        Sequence("CURRENT", "STACKED", optional=True),
        "DIAGNOSTICS",
        Delimited(
            Sequence(
                OneOf(
                    Ref("SessionVariableNameSegment"), Ref("LocalVariableNameSegment")
                ),
                Ref("EqualsSegment"),
                OneOf("NUMBER", "ROW_COUNT"),
            ),
            optional=True,
        ),
        "CONDITION",
        OneOf(
            Ref("SessionVariableNameSegment"),
            Ref("LocalVariableNameSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Delimited(
            Sequence(
                OneOf(
                    Ref("SessionVariableNameSegment"), Ref("LocalVariableNameSegment")
                ),
                Ref("EqualsSegment"),
                OneOf(
                    "CLASS_ORIGIN",
                    "SUBCLASS_ORIGIN",
                    "RETURNED_SQLSTATE",
                    "MESSAGE_TEXT",
                    "MYSQL_ERRNO",
                    "CONSTRAINT_CATALOG",
                    "CONSTRAINT_SCHEMA",
                    "CONSTRAINT_NAME",
                    "CATALOG_NAME",
                    "SCHEMA_NAME",
                    "TABLE_NAME",
                    "COLUMN_NAME",
                    "CURSOR_NAME",
                ),
            ),
            optional=True,
        ),
    )


@mysql_dialect.segment()
class LoopStatementSegment(BaseSegment):
    """A `LOOP` statement.

    https://dev.mysql.com/doc/refman/8.0/en/loop.html
    """

    type = "loop_statement"

    match_grammar = OneOf(
        Sequence(
            Sequence(
                Ref("SingleIdentifierGrammar"), Ref("ColonSegment"), optional=True
            ),
            "LOOP",
            Delimited(
                Ref("StatementSegment"),
            ),
        ),
        Sequence(
            "END",
            "LOOP",
            Ref("SingleIdentifierGrammar", optional=True),
        ),
    )


@mysql_dialect.segment()
class CursorOpenCloseSegment(BaseSegment):
    """This is a CLOSE or Open statement.

    https://dev.mysql.com/doc/refman/8.0/en/close.html
    https://dev.mysql.com/doc/refman/8.0/en/open.html
    """

    type = "cursor_open_close_segment"

    match_grammar = Sequence(
        OneOf("CLOSE", "OPEN"),
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("QuotedIdentifierSegment"),
        ),
    )


@mysql_dialect.segment()
class IterateStatementSegment(BaseSegment):
    """A `ITERATE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/iterate.html
    """

    type = "iterate_statement"

    match_grammar = Sequence(
        "ITERATE",
        Ref("SingleIdentifierGrammar"),
    )


@mysql_dialect.segment()
class ExecuteSegment(BaseSegment):
    """This is the body of a `EXECUTE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/execute.html
    """

    type = "execute_segment"

    match_grammar = Sequence(
        "EXECUTE",
        Ref("NakedIdentifierSegment"),
        Sequence("USING", Delimited(Ref("SessionVariableNameSegment")), optional=True),
    )


@mysql_dialect.segment()
class RepeatStatementSegment(BaseSegment):
    """A `REPEAT-UNTIL` statement.

    https://dev.mysql.com/doc/refman/8.0/en/repeat.html
    """

    type = "repeat_statement"

    match_grammar = OneOf(
        Sequence(
            Sequence(
                Ref("SingleIdentifierGrammar"), Ref("ColonSegment"), optional=True
            ),
            "REPEAT",
            AnyNumberOf(
                Ref("StatementSegment"),
            ),
        ),
        Sequence(
            "UNTIL",
            Ref("ExpressionSegment"),
            Sequence(
                "END",
                "REPEAT",
                Ref("SingleIdentifierGrammar", optional=True),
            ),
        ),
    )


@mysql_dialect.segment()
class DeallocateSegment(BaseSegment):
    """This is the body of a `DEALLOCATE/DROP` statement.

    https://dev.mysql.com/doc/refman/8.0/en/deallocate-prepare.html
    """

    type = "deallocate_segment"

    match_grammar = Sequence(
        Sequence(OneOf("DEALLOCATE", "DROP"), "PREPARE"),
        Ref("NakedIdentifierSegment"),
    )


@mysql_dialect.segment()
class ResignalSegment(BaseSegment):
    """This is the body of a `RESIGNAL` statement.

    https://dev.mysql.com/doc/refman/8.0/en/resignal.html
    """

    type = "resignal_segment"

    match_grammar = Sequence(
        OneOf("SIGNAL", "RESIGNAL"),
        OneOf(
            Sequence(
                "SQLSTATE",
                Ref.keyword("VALUE", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
            Ref("NakedIdentifierSegment"),
            optional=True,
        ),
        Sequence(
            "SET",
            Delimited(
                Sequence(
                    OneOf(
                        "CLASS_ORIGIN",
                        "SUBCLASS_ORIGIN",
                        "RETURNED_SQLSTATE",
                        "MESSAGE_TEXT",
                        "MYSQL_ERRNO",
                        "CONSTRAINT_CATALOG",
                        "CONSTRAINT_SCHEMA",
                        "CONSTRAINT_NAME",
                        "CATALOG_NAME",
                        "SCHEMA_NAME",
                        "TABLE_NAME",
                        "COLUMN_NAME",
                        "CURSOR_NAME",
                    ),
                    Ref("EqualsSegment"),
                    OneOf(
                        Ref("SessionVariableNameSegment"),
                        Ref("LocalVariableNameSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            optional=True,
        ),
    )


@mysql_dialect.segment()
class CursorFetchSegment(BaseSegment):
    """This is a FETCH statement.

    https://dev.mysql.com/doc/refman/8.0/en/fetch.html
    """

    type = "cursor_fetch_segment"

    match_grammar = Sequence(
        "FETCH",
        Sequence(Ref.keyword("NEXT", optional=True), "FROM", optional=True),
        Ref("NakedIdentifierSegment"),
        "INTO",
        Delimited(
            Ref("SessionVariableNameSegment"),
            Ref("LocalVariableNameSegment"),
        ),
    )


@mysql_dialect.segment(replace=True)
class DropIndexStatementSegment(BaseSegment):
    """A `DROP INDEX` statement.

    https://dev.mysql.com/doc/refman/8.0/en/drop-index.html
    """

    type = "drop_statement"
    # DROP INDEX <Index name> ON <table_name>
    # [ALGORITHM [=] {DEFAULT | INPLACE | COPY} | LOCK [=] {DEFAULT | NONE | SHARED | EXCLUSIVE}]
    match_grammar = Sequence(
        "DROP",
        "INDEX",
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "ALGORITHM",
                Ref("EqualsSegment", optional=True),
                OneOf("DEFAULT", "INPLACE", "COPY"),
            ),
            Sequence(
                "LOCK",
                Ref("EqualsSegment", optional=True),
                OneOf("DEFAULT", "NONE", "SHARED", "EXCLUSIVE"),
            ),
            optional=True,
        ),
    )
