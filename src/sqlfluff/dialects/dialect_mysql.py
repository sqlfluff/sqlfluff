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
    AnySetOf,
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
        ),
        RegexLexer(
            "single_quote", r"(?s)('')+?(?!')|('.*?(?<!')(?:'')*'(?!'))", CodeSegment
        ),
    ]
)

# Reserve USE, FORCE & IGNORE
mysql_dialect.sets("unreserved_keywords").difference_update(
    [
        "BTREE",
        "FORCE",
        "HASH",
        "IGNORE",
        "INVISIBLE",
        "KEY_BLOCK_SIZE",
        "PARSER",
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
        "VISIBLE",
    ]
)
mysql_dialect.sets("unreserved_keywords").update(
    [
        "QUICK",
        "FAST",
        "MEDIUM",
        "EXTENDED",
        "CHANGED",
        "UPGRADE",
        "HISTOGRAM",
        "BUCKETS",
        "USE_FRM",
        "REPAIR",
        "DUPLICATE",
    ]
)
mysql_dialect.sets("reserved_keywords").update(
    [
        "HELP",
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
        "MASTER",
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
    DateTimeLiteralGrammar=Sequence(
        # MySQL does not require the keyword to be specified:
        # https://dev.mysql.com/doc/refman/8.0/en/date-and-time-literals.html
        OneOf(
            "DATE",
            "TIME",
            "TIMESTAMP",
            "DATETIME",
            "INTERVAL",
            optional=True,
        ),
        OneOf(
            Ref("QuotedLiteralSegment"),
            Ref("NumericLiteralSegment"),
        ),
    ),
    QuotedLiteralSegment=AnyNumberOf(
        # MySQL allows whitespace-concatenated string literals (#1488).
        # Since these string literals can have comments between them,
        # we use grammar to handle this.
        NamedParser(
            "single_quote",
            CodeSegment,
            name="quoted_literal",
            type="literal",
        ),
        min_times=1,
    ),
    UniqueKeyGrammar=Sequence(
        "UNIQUE",
        Ref.keyword("KEY", optional=True),
    ),
    # Odd syntax, but pr
    CharCharacterSetSegment=Ref.keyword("BINARY"),
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
class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    """

    type = "alias_expression"
    match_grammar = Sequence(
        Ref.keyword("AS", optional=True),
        Ref("SingleIdentifierGrammar"),
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
                        Bracketed(
                            Ref("NumericLiteralSegment", optional=True), optional=True
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


@mysql_dialect.segment()
class UpsertClauseListSegment(BaseSegment):
    """An `ON DUPLICATE KEY UPDATE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/insert-on-duplicate.html
    """

    type = "upsert_clause_list"
    match_grammar = Sequence(
        "ON",
        "DUPLICATE",
        "KEY",
        "UPDATE",
        Delimited(Ref("SetClauseSegment")),
    )


@mysql_dialect.segment()
class InsertRowAliasSegment(BaseSegment):
    """A row alias segment (used in `INSERT` statements).

    https://dev.mysql.com/doc/refman/8.0/en/insert.html
    """

    type = "insert_row_alias"
    match_grammar = Sequence(
        "AS",
        Ref("SingleIdentifierGrammar"),
        Bracketed(
            Ref("SingleIdentifierListSegment"),
            optional=True,
        ),
    )


@mysql_dialect.segment(replace=True)
class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    https://dev.mysql.com/doc/refman/8.0/en/insert.html
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
                Sequence(
                    OneOf(
                        Ref("SelectableGrammar"),
                        Sequence(
                            "TABLE",
                            Ref("TableReferenceSegment"),
                        ),
                    ),
                ),
                optional=False,
            ),
            Ref("InsertRowAliasSegment", optional=True),
            Ref("UpsertClauseListSegment", optional=True),
        ),
    )


@mysql_dialect.segment(replace=True)
class TableConstraintSegment(BaseSegment):
    """A table constraint, e.g. for CREATE TABLE."""

    type = "table_constraint"
    # Later add support for CHECK constraint, others?
    # e.g. CONSTRAINT constraint_1 PRIMARY KEY(column_1)
    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        Delimited(
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
                AnyNumberOf(
                    Sequence(
                        "ON",
                        OneOf("DELETE", "UPDATE"),
                        OneOf(
                            "RESTRICT",
                            "CASCADE",
                            Sequence("SET", "NULL"),
                            Sequence("NO", "ACTION"),
                            Sequence("SET", "DEFAULT"),
                        ),
                        optional=True,
                    ),
                ),
            ),
        ),
    )


@mysql_dialect.segment(replace=True)
class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment.

    https://dev.mysql.com/doc/refman/8.0/en/date-and-time-functions.html#function_adddate
    """

    type = "interval_expression"
    match_grammar = Sequence(
        "INTERVAL",
        OneOf(
            # The Numeric Version
            Sequence(
                Ref("ExpressionSegment"),
                OneOf(Ref("QuotedLiteralSegment"), Ref("DatetimeUnitSegment")),
            ),
            # The String version
            Ref("QuotedLiteralSegment"),
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
    BooleanDynamicSystemVariablesGrammar=OneOf(
        # Boolean dynamic system varaiables can be set to ON/OFF, TRUE/FALSE, or 0/1:
        # https://dev.mysql.com/doc/refman/8.0/en/dynamic-system-variables.html
        # This allows us to match ON/OFF & TRUE/FALSE as keywords and therefore apply
        # the correct capitalisation policy.
        OneOf("ON", "OFF"),
        OneOf("TRUE", "FALSE"),
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
            Ref("DropFunctionStatementSegment"),
            Ref("DropProcedureStatementSegment"),
            Ref("AlterTableStatementSegment"),
            Ref("RenameTableStatementSegment"),
            Ref("ResetMasterStatementSegment"),
            Ref("PurgeBinaryLogsStatementSegment"),
            Ref("HelpStatementSegment"),
            Ref("CheckTableStatementSegment"),
            Ref("ChecksumTableStatementSegment"),
            Ref("AnalyzeTableStatementSegment"),
            Ref("RepairTableStatementSegment"),
            Ref("OptimizeTableStatementSegment"),
            Ref("UpsertClauseListSegment"),
            Ref("InsertRowAliasSegment"),
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

    type = "function_definition"
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
                # Add column
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
                # Add index
                Sequence(
                    "ADD",
                    Ref.keyword("UNIQUE", optional=True),
                    OneOf("INDEX", "KEY", optional=True),
                    Ref("IndexReferenceSegment"),
                    Sequence("USING", OneOf("BTREE", "HASH"), optional=True),
                    Ref("BracketedColumnReferenceListGrammar"),
                    AnySetOf(
                        Sequence(
                            "KEY_BLOCK_SIZE",
                            Ref("EqualsSegment"),
                            Ref("NumericLiteralSegment"),
                        ),
                        Sequence("USING", OneOf("BTREE", "HASH")),
                        Sequence("WITH", "PARSER", Ref("ObjectReferenceSegment")),
                        Ref("CommentClauseSegment"),
                        OneOf("VISIBLE", "INVISIBLE"),
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
                    OneOf(
                        Sequence(
                            Ref.keyword("COLUMN", optional=True),
                            Ref("ColumnReferenceSegment"),
                        ),
                        Sequence(
                            OneOf("INDEX", "KEY", optional=True),
                            Ref("IndexReferenceSegment"),
                        ),
                    ),
                ),
                # Rename
                Sequence(
                    "RENAME",
                    OneOf(
                        # Rename table
                        Sequence(
                            OneOf("AS", "TO", optional=True),
                            Ref("TableReferenceSegment"),
                        ),
                        # Rename index
                        Sequence(
                            "RENAME",
                            OneOf("INDEX", "KEY"),
                            Ref("IndexReferenceSegment"),
                            "TO",
                            Ref("IndexReferenceSegment"),
                        ),
                    ),
                ),
            ),
        ),
    )


@mysql_dialect.segment()
class ProcedureParameterListGrammar(BaseSegment):
    """The parameters for a procedure ie. `(in/out/inout name datatype)`."""

    type = "procedure_parameter_list"
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
            # Match boolean keywords before local variables.
            Ref("BooleanDynamicSystemVariablesGrammar"),
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
        .copy(insert=[Ref("UpsertClauseListSegment")])
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

    get_alias = ansi_dialect.get_segment("SelectClauseElementSegment").get_alias


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
    match_grammar.terminator = match_grammar.terminator.copy(
        insert=[Ref("UpsertClauseListSegment")]
    )

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
    # [ALGORITHM [=] {DEFAULT | INPLACE | COPY} | LOCK [=] {DEFAULT | NONE | SHARED |
    # EXCLUSIVE}]
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


@mysql_dialect.segment()
class DropProcedureStatementSegment(BaseSegment):
    """A `DROP` statement that addresses stored procedures and functions.

    https://dev.mysql.com/doc/refman/8.0/en/drop-procedure.html
    """

    type = "drop_procedure_statement"

    # DROP {PROCEDURE | FUNCTION} [IF EXISTS] sp_name
    match_grammar = Sequence(
        "DROP",
        OneOf("PROCEDURE", "FUNCTION"),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
    )


@mysql_dialect.segment()
class DropFunctionStatementSegment(BaseSegment):
    """A `DROP` statement that addresses loadable functions.

    https://dev.mysql.com/doc/refman/8.0/en/drop-function-loadable.html
    """

    type = "drop_function_ statement"

    # DROP FUNCTION [IF EXISTS] function_name
    match_grammar = Sequence(
        "DROP",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
    )


@mysql_dialect.segment()
class RenameTableStatementSegment(BaseSegment):
    """A `RENAME TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/rename-table.html
    """

    type = "rename_table_statement"
    match_grammar = Sequence(
        "RENAME",
        "TABLE",
        Delimited(
            Sequence(
                Ref("TableReferenceSegment"),
                "TO",
                Ref("TableReferenceSegment"),
            ),
        ),
    )


@mysql_dialect.segment()
class ResetMasterStatementSegment(BaseSegment):
    """A `RESET MASTER` statement.

    https://dev.mysql.com/doc/refman/8.0/en/reset-master.html
    """

    type = "reset_master_statement"
    match_grammar = Sequence(
        "RESET",
        "MASTER",
        Sequence("TO", Ref("NumericLiteralSegment"), optional=True),
    )


@mysql_dialect.segment()
class PurgeBinaryLogsStatementSegment(BaseSegment):
    """A `PURGE BINARY LOGS` statement.

    https://dev.mysql.com/doc/refman/8.0/en/purge-binary-logs.html
    """

    type = "purge_binary_logs_statement"
    match_grammar = Sequence(
        "PURGE",
        OneOf(
            "BINARY",
            "MASTER",
        ),
        "LOGS",
        OneOf(
            Sequence(
                "TO",
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "BEFORE",
                OneOf(
                    Ref("DateTimeLiteralGrammar"),
                ),
            ),
        ),
    )


@mysql_dialect.segment()
class HelpStatementSegment(BaseSegment):
    """A `HELP` statement.

    https://dev.mysql.com/doc/refman/8.0/en/help.html
    """

    type = "help_statement"
    match_grammar = Sequence(
        "HELP",
        Ref("QuotedLiteralSegment"),
    )


@mysql_dialect.segment()
class CheckTableStatementSegment(BaseSegment):
    """A `CHECK TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/check-table.html
    """

    type = "check_table_statement"
    match_grammar = Sequence(
        "CHECK",
        "TABLE",
        Delimited(
            Ref("TableReferenceSegment"),
        ),
        AnyNumberOf(
            Sequence("FOR", "UPGRADE"),
            "QUICK",
            "FAST",
            "MEDIUM",
            "EXTENDED",
            "CHANGED",
            min_times=1,
        ),
    )


@mysql_dialect.segment()
class ChecksumTableStatementSegment(BaseSegment):
    """A `CHECKSUM TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/checksum-table.html
    """

    type = "checksum_table_statement"
    match_grammar = Sequence(
        "CHECKSUM",
        "TABLE",
        Delimited(
            Ref("TableReferenceSegment"),
        ),
        OneOf(
            "QUICK",
            "EXTENDED",
        ),
    )


@mysql_dialect.segment()
class AnalyzeTableStatementSegment(BaseSegment):
    """An `ANALYZE TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/analyze-table.html
    """

    type = "analyze_table_statement"
    match_grammar = Sequence(
        "ANALYZE",
        OneOf(
            "NO_WRITE_TO_BINLOG",
            "LOCAL",
            optional=True,
        ),
        "TABLE",
        OneOf(
            Sequence(
                Delimited(
                    Ref("TableReferenceSegment"),
                ),
            ),
            Sequence(
                Ref("TableReferenceSegment"),
                "UPDATE",
                "HISTOGRAM",
                "ON",
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    "WITH",
                    Ref("NumericLiteralSegment"),
                    "BUCKETS",
                    optional=True,
                ),
            ),
            Sequence(
                Ref("TableReferenceSegment"),
                "DROP",
                "HISTOGRAM",
                "ON",
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
            ),
        ),
    )


@mysql_dialect.segment()
class RepairTableStatementSegment(BaseSegment):
    """A `REPAIR TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/repair-table.html
    """

    type = "repair_table_statement"
    match_grammar = Sequence(
        "REPAIR",
        OneOf(
            "NO_WRITE_TO_BINLOG",
            "LOCAL",
            optional=True,
        ),
        "TABLE",
        Delimited(
            Ref("TableReferenceSegment"),
        ),
        AnyNumberOf(
            "QUICK",
            "EXTENDED",
            "USE_FRM",
        ),
    )


@mysql_dialect.segment()
class OptimizeTableStatementSegment(BaseSegment):
    """An `OPTIMIZE TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/optimize-table.html
    """

    type = "optimize_table_statement"
    match_grammar = Sequence(
        "OPTIMIZE",
        OneOf(
            "NO_WRITE_TO_BINLOG",
            "LOCAL",
            optional=True,
        ),
        "TABLE",
        Delimited(
            Ref("TableReferenceSegment"),
        ),
    )
