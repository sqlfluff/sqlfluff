"""The EXASOL dialect for script and function create statements.

This is seperated from the common EXASOL dialect because
`CREATE FUNCTION` and `CREATE SCRIPT` statements are not terminated
by a semicolon. They terminated by a trailing / at the end of the function / script.
A semicolon is the terminator of the statement within the function / script
https://docs.exasol.com
"""

from ..parser import (
    OneOf,
    Ref,
    Sequence,
    Bracketed,
    BaseSegment,
    AnyNumberOf,
    GreedyUntil,
    Delimited,
    NamedSegment,
    SymbolSegment,
    ReSegment,
    Anything,
)

from .dialect_exasol import ObjectReferenceSegment, exasol_dialect

exasol_fs_dialect = exasol_dialect.copy_as("exasol_fs")

# Add walrus operator to the top
exasol_fs_dialect.set_lexer_struct(
    [
        (
            "walrus_operator",
            "regex",
            r":=",
            dict(is_code=True, type="walrus_operator"),
        ),
        (
            "script_terminator",
            "regex",
            r"(\r\n|\n)\s*\/(?!\*)",
            # r"/$",
            dict(
                is_code=True,
                type="script_terminator",
                subdivide=dict(type="newline", name="newline", regex=r"\r\n|\n"),
            ),
        ),
    ]
    + exasol_fs_dialect.get_lexer_struct()
)

exasol_fs_dialect.add(
    ScriptTerminatorSegment=NamedSegment.make(
        "script_terminator", type="script_terminator"
    ),
    WalrusOperatorSegment=SymbolSegment.make(
        ":=", name="walrus_operator", type="assignment_operator"
    ),
    FunctionVariableNameSegment=ReSegment.make(
        r"[A-Z][A-Z0-9_]*",
        name="function_variable",
        type="variable",
    ),
    FunctionVariableAssignmentSegment=ReSegment.make(
        r"[^;]",
        name="variable_assignment",
        type="variable_assignment",
    ),
)

exasol_fs_dialect.replace(
    SemicolonSegment=SymbolSegment.make(";", name="semicolon", type="semicolon"),
)


@exasol_fs_dialect.segment()
class ParameterDefinitionSegment(BaseSegment):
    """A parameter definition."""

    type = "parameter_definition"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        Ref.keyword("IN", optional=True),
        Ref("DatatypeSegment"),  # Column type
        Ref.keyword("UTF8", optional=True),
    )


############################
# FUNCTION
############################


@exasol_fs_dialect.segment()
class FunctionReferenceSegment(ObjectReferenceSegment):
    """A reference to a function."""

    type = "function_reference"


@exasol_fs_dialect.segment()
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement."""

    type = "create_function_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        "FUNCTION",
        Ref("FunctionReferenceSegment"),
        # Ref("StartBracketSegment"),
        Bracketed(
            AnyNumberOf(
                Ref("ParameterDefinitionSegment", optional=True),
                Ref("CommaSegment", optional=True),
            ),
        ),
        # Ref("EndBracketSegment"),
        "RETURN",
        Ref("DatatypeSegment"),
        OneOf("IS", "AS", optional=True),
        AnyNumberOf(
            Sequence(
                Ref("FunctionVariableNameSegment"),
                Ref("DatatypeSegment"),
                Ref("SemicolonSegment"),
            ),
            optional=True,
        ),
        "BEGIN",
        AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
        "RETURN",
        Ref("FunctionContentsExpressionGrammar"),  # TODO Expression
        Ref("SemicolonSegment"),
        "END",
        Ref("FunctionReferenceSegment", optional=True),
        Ref("SemicolonSegment", optional=True),
    )


@exasol_fs_dialect.segment()
class FunctionBodySegment(BaseSegment):
    """The definition of the function body."""

    type = "function_body"
    match_grammar = OneOf(
        Ref("FunctionAssignmentSegment"),
        Ref("FunctionIfBranchSegment"),
        Ref("FunctionForLoopSegment"),
        Ref("FunctionWhileLoopSegment"),
    )


@exasol_fs_dialect.segment()
class FunctionAssignmentSegment(BaseSegment):
    """The definition of a assignment within a function body."""

    type = "function_assignment"
    match_grammar = Sequence(
        # assignment
        Ref("FunctionVariableNameSegment"),
        Ref("WalrusOperatorSegment"),
        OneOf(
            Sequence(
                Ref("FunctionReferenceSegment"),
                Bracketed(
                    AnyNumberOf(
                        Ref("ParameterNameSegment"),
                        Ref("CommaSegment", optional=True),
                    ),
                ),
            ),
            Ref("FunctionVariableNameSegment"),
            Ref("LiteralGrammar"),
            Ref("ExpressionSegment"),
            Ref("QuotedIdentifierSegment"),  # TODO: geht das überhaupt?
        ),
        Ref("SemicolonSegment"),
    )


@exasol_fs_dialect.segment()
class FunctionIfBranchSegment(BaseSegment):
    """The definition of a if branch within a function body."""

    type = "function_if_branch"
    match_grammar = Sequence(
        # if branch
        "IF",
        AnyNumberOf(Ref("ExpressionSegment")),  # TODO: condition
        "THEN",
        AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
        AnyNumberOf(
            Sequence(
                "ELSEIF",
                Ref("ExpressionSegment"),  # TODO: condition
                "THEN",
                AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
            ),
            optional=True,
        ),
        Sequence(
            "ELSE", AnyNumberOf(Ref("FunctionBodySegment"), min_times=1), optional=True
        ),
        "END",
        "IF",
        Ref("SemicolonSegment"),
    )


@exasol_fs_dialect.segment()
class FunctionForLoopSegment(BaseSegment):
    """The definition of a for loop within a function body."""

    type = "function_for_loop"
    match_grammar = Sequence(
        "FOR",
        Ref("ColumnReferenceSegment"),  # TODO: identifier
        OneOf(
            Sequence(
                Ref("WalrusOperatorSegment"),
                Ref("NumericLiteralSegment"),
                "TO",
                Ref("NumericLiteralSegment"),
                "DO",
                AnyNumberOf(
                    Ref("FunctionStatementSegment"),
                ),  # TODO min1
                "END",
                "FOR",
            ),
            Sequence(
                "IN",
                Ref("NumericLiteralSegment"),
                "..",
                Ref("NumericLiteralSegment"),
                "LOOP",
                AnyNumberOf(Ref("FunctionStatementSegment")),  # TODO min1
                "END",
                "LOOP",
            ),
        ),
        Ref("SemicolonSegment"),
    )


@exasol_fs_dialect.segment()
class FunctionWhileLoopSegment(BaseSegment):
    """The definition of a while loop within a function body."""

    type = "function_while_loop"
    match_grammar = Sequence(
        "WHILE",
        Ref("ColumnReferenceSegment"),  # TODO: condition
        "DO",
        AnyNumberOf(
            Ref("FunctionStatementSegment"),
        ),  # TODO min1
        "END",
        "WHILE",
        Ref("SemicolonSegment"),
    )


@exasol_fs_dialect.segment(replace=True)
class MLTableExpressionSegment(BaseSegment):
    """Not supported!"""

    pass


@exasol_fs_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    match_grammar = GreedyUntil(Ref("ScriptTerminatorSegment"))
    parse_grammar = Ref("CreateFunctionStatementSegment")


@exasol_fs_dialect.segment(replace=True)
class FileSegment(BaseSegment):
    """A segment representing a whole file or script.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    type = "file"
    # The file segment is the only one which can start or end with non-code
    can_start_end_non_code = True
    # A file can be empty!
    allow_empty = True

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    parse_grammar = Delimited(
        Ref("StatementSegment"),
        delimiter=Ref("ScriptTerminatorSegment"),
        allow_gaps=True,
        allow_trailing=True,
    )


@exasol_fs_dialect.segment()
class ScriptContentSegment(BaseSegment):
    """This represents the script content.

    Because the script content could be written in
    LUA, PYTHON, JAVA or R there is no further verification.
    """

    type = "script_content"
    match_grammar = Anything()
