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
    Indent,
    StartsWith,
    GreedyUntil,
    Dedent,
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
    PostTableExpressionGrammar=Sequence(
        Ref("IndexHintClauseSegment"),
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        "GROUP",
        "ORDER",
        "HAVING",
        "QUALIFY",
        "WINDOW",
        Sequence(
            "FOR",
            OneOf("UPDATE", "SHARE"),
        ),
        Sequence("LOCK", "IN", "SHARE", "MODE"),
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
    ),
    BaseExpressionElementGrammar=OneOf(
        Ref("LiteralGrammar"),
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("IntervalExpressionSegment"),
        Ref("ColumnReferenceSegment"),
        Ref("ExpressionSegment"),
        Ref("SessionVariableNameSegment"),
        Ref("LocalVariableNameSegment"),
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

    mysql: https://dev.mysql.com/doc/refman/8.0/en/declare-local-variable.html
    mysql: https://dev.mysql.com/doc/refman/8.0/en/declare-handler.html
    mysql: https://dev.mysql.com/doc/refman/8.0/en/declare-condition.html
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
            Ref("CallStoredProcedureSegment"),
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

    mysql: https://dev.mysql.com/doc/refman/8.0/en/create-procedure.html
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

    mysql: https://dev.mysql.com/doc/refman/8.0/en/create-procedure.html
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

    mysql: https://dev.mysql.com/doc/refman/8.0/en/set-variable.html
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
        ),
    )


@mysql_dialect.segment(replace=True)
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement.

    mysql: https://dev.mysql.com/doc/refman/8.0/en/commit.html
    mysql: https://dev.mysql.com/doc/refman/8.0/en/begin-end.html
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

    mysql:https://dev.mysql.com/doc/refman/8.0/en/if.html
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
                        "TERMINATED", "BY", Ref("QuotedLiteralSegment"), optional=True
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
                        "TERMINATED", "BY", Ref("QuotedLiteralSegment"), optional=True
                    ),
                    optional=True,
                ),
            ),
        ),
    )


# I wanted to do an override and just insert the new Refs but I need
# to have the IntoClause be before FromClauseSegment, but it doesn't work to add the `before` clause
# looking for suggestions on how to do this differently, if possible
@mysql_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.
    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    type = "select_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith(
        # In mysql, the select clause may include an INTO statement
        # to assign values from columns/functions to corresponding
        # local or session variables
        Ref("SelectClauseSegment"),
        terminator=OneOf(
            Ref("IntoClauseSegment"),
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("OrderByClauseSegment"),
            Ref("LimitClauseSegment"),
            Ref("NamedWindowSegment"),
            Ref("ForClauseSegment"),
        ),
        enforce_whitespace_preceeding_terminator=True,
    )

    parse_grammar = Sequence(
        Ref("SelectClauseSegment"),
        # Dedent for the indent in the select clause.
        # It's here so that it can come AFTER any whitespace.
        Dedent,
        Ref("IntoClauseSegment", optional=True),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("ForClauseSegment", optional=True),
    )


# I am unclear why I have to override this segement, but if I don't then new segments won't parse
# looking for suggestions on how to avoid this since it seems unnecessary
@mysql_dialect.segment(replace=True)
class SelectClauseElementSegment(BaseSegment):
    """An element in the targets of a select statement."""

    type = "select_clause_element"
    # Important to split elements before parsing, otherwise debugging is really hard.
    match_grammar = GreedyUntil(
        "INTO",
        "FROM",
        "WHERE",
        "ORDER",
        "LIMIT",
        Ref("CommaSegment"),
        Ref("SetOperatorSegment"),
        enforce_whitespace_preceeding_terminator=True,
    )

    parse_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            Ref("BaseExpressionElementGrammar"),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )


# I am unclear why I have to override this segement, but if I don't then new segments won't parse
# looking for suggestions on how to avoid this since it seems unnecessary
@mysql_dialect.segment(replace=True)
class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement."""

    type = "select_clause"
    match_grammar = StartsWith(
        Sequence("SELECT", Ref("WildcardExpressionSegment", optional=True)),
        terminator=OneOf(
            "INTO",
            "FROM",
            "WHERE",
            "ORDER",
            "LIMIT",
            Ref("SetOperatorSegment"),
        ),
        enforce_whitespace_preceeding_terminator=True,
    )

    parse_grammar = Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        Delimited(
            ansi_dialect.get_segment("SelectClauseElementSegment"),
            allow_trailing=True,
        ),
        # NB: The Dedent for the indent above lives in the
        # SelectStatementSegment so that it sits in the right
        # place corresponding to the whitespace.
    )


# I am unclear why I have to override this segement, but if I don't then new segments don't parse
# looking for suggestions on how to avoid this since it seems unnecessary
@mysql_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    https://dev.mysql.com/doc/refman/5.7/en/select.html
    """

    type = "select_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith(
        # NB: In bigquery, the select clause may include an EXCEPT, which
        # will also match the set operator, but by starting with the whole
        # select clause rather than just the SELECT keyword, we mitigate that
        # here.
        Ref("SelectClauseSegment"),
        terminator=OneOf(
            Ref("SetOperatorSegment"), Ref("WithNoSchemaBindingClauseSegment")
        ),
        enforce_whitespace_preceeding_terminator=True,
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
    """This is the body of a index hint clause."""

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
    )


@mysql_dialect.segment()
class CallStoredProcedureSegment(BaseSegment):
    """This is a CALL statement used to execute a stored procedure.

    mysql: https://dev.mysql.com/doc/refman/8.0/en/call.html
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
