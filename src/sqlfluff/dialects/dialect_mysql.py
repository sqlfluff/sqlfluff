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
    Anything,
    Delimited,
    RegexParser,
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
mysql_dialect.sets("unreserved_keywords").difference_update(["FORCE", "IGNORE", "USE"])
mysql_dialect.sets("reserved_keywords").update(["FORCE", "IGNORE", "USE"])

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
        OneOf("IGNORE", "FORCE", "USE"),
        OneOf("INDEX", "KEY"),
        Sequence("FOR", OneOf("JOIN"), optional=True),
        Bracketed(Ref("ObjectReferenceSegment")),
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
    AmpersandLiteralSegment=NamedParser(
        "ampersand",
        CodeSegment,
        name="ampersand_literal",
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
    AmpersandSignSegment=StringParser(
        "@", SymbolSegment, name="ampersandsign", type="user_designator"
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

mysql_dialect.patch_lexer_matchers(
    [
        RegexLexer(
            "ampersand",
            r"[@][a-zA-Z0-9_]*",
            CodeSegment,
        ),
    ]
)


@mysql_dialect.segment()
class DeclareStatement(BaseSegment):
    """DECLARE statement.

    mysql: https://dev.mysql.com/doc/refman/8.0/en/declare-local-variable.html
    mysql: https://dev.mysql.com/doc/refman/8.0/en/declare-handler.html
    mysql: https://dev.mysql.com/doc/refman/8.0/en/declare-condition.html
    """

    type = "declare_statement"

    match_grammar = OneOf(
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
            Ref("TransactionStatementSegment"),
            Ref("DeclareStatement"),
            Ref("SetAssignmentStatementSegment"),
            Ref("IfExpressionStatement"),
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
        Ref("AmpersandLiteralSegment"),
        Ref("SingleIdentifierGrammar"),
    )
