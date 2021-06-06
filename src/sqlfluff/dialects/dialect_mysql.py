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
    )
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
)

mysql_dialect.replace(
    DelimiterSegment=OneOf(Ref("SemicolonSegment"), Ref("TildeSegment")),
    TildeSegment=StringParser(
        "~", SymbolSegment, name="tilde", type="statement_terminator"
    ),
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
    # purposefully left out DEFINER
    # will be addressed when issue [#1131](https://github.com/sqlfluff/sqlfluff/issues/1131) is addressed
    match_grammar = Sequence(
        "CREATE",
        "PROCEDURE",
        Anything(),
    )

    parse_grammar = Sequence(
        "CREATE",
        "PROCEDURE",
        Ref("FunctionNameSegment"),
        Ref("ProcedureParameterListGrammar", optional=True),
        Ref("CommentClauseSegment", optional=True),
        Ref("CharacteristicStatement", optional=True),
        Ref("FunctionDefinitionGrammar"),
    )


@mysql_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("DelimiterStatement"),
            Ref("CreateProcedureStatementSegment"),
        ],
    )


@mysql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION` statement."""

    match_grammar = Sequence(
        Ref("TransactionStatementSegment"),
        Ref("StatementSegment"),
    )


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
        "FUNCTION",
        Anything(),
    )
    # purposefully left out DEFINER
    # will be addressed when issue [#1131](https://github.com/sqlfluff/sqlfluff/issues/1131) is addressed
    parse_grammar = Sequence(
        "CREATE",
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

    # Function parameter list
    match_grammar = Bracketed(
        Delimited(
            Ref("ProcedureParameterGrammar"),
            delimiter=Ref("CommaSegment"),
            optional=True,
        ),
    )
