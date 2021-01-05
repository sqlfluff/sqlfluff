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
            "function_script_terminator",
            "regex",
            r";\s+\/(?!\*)|\s+\/$",  # this will match multiple functions in one file, but only one script per file
            dict(
                is_code=True,
                type="statement_terminator",
                subdivide=dict(type="semicolon", name="semicolon", regex=r";"),
                trim_post_subdivide=dict(
                    type="newline", name="newline", regex=r"(\n|\r\n)*"
                ),
            ),
        ),
        ("double_dot", "regex", r"\.{2}", dict(is_code=True)),
    ]
    + exasol_fs_dialect.get_lexer_struct()
)

exasol_fs_dialect.add(
    FunctionScriptTerminatorSegment=NamedSegment.make(
        "function_script_terminator", type="statement_terminator"
    ),
    WalrusOperatorSegment=NamedSegment.make(
        "walrus_operator", type="assignment_operator"
    ),
    FunctionVariableNameSegment=ReSegment.make(
        r"[A-Z][A-Z0-9_]*",
        name="function_variable",
        type="variable",
    ),
    DoubleDotSegment=NamedSegment.make("double_dot", type="for_loop_between_type"),
)

exasol_fs_dialect.replace(
    SemicolonSegment=SymbolSegment.make(";", name="semicolon", type="semicolon"),
)


@exasol_fs_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    match_grammar = GreedyUntil(Ref("FunctionScriptTerminatorSegment"))
    parse_grammar = OneOf(
        Ref("CreateFunctionStatementSegment"),
        Ref("CreateScriptingScriptStatementSegment"),
        Ref("CreateUDFScriptStatementSegment"),
        Ref("CreateAdapterScriptStatementSegment"),
    )


@exasol_fs_dialect.segment(replace=True)
class FileSegment(BaseSegment):
    """This ovewrites the FileSegment from ANSI.

    The reason is because SCRIPT and FUNCTION statements
    are terminated by a trailing / at the end.
    A semicolon is the terminator of the statement within the function / script
    """

    type = "file"
    can_start_end_non_code = True
    allow_empty = True
    parse_grammar = Delimited(
        Ref("StatementSegment"),
        delimiter=Ref("FunctionScriptTerminatorSegment"),
        allow_gaps=True,
        allow_trailing=True,
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
        Ref("OrReplaceGrammar", optional=True),
        "FUNCTION",
        Ref("FunctionReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("SingleIdentifierGrammar"),  # Column name
                    Ref.keyword("IN", optional=True),
                    Ref("DatatypeSegment"),  # Column type
                    Ref.keyword("UTF8", optional=True),
                ),
                delimiter=Ref("CommaSegment"),
                optional=True,
            ),
        ),
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
        Ref("FunctionContentsExpressionGrammar"),
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
        ),
        Ref("SemicolonSegment"),
    )


@exasol_fs_dialect.segment()
class FunctionIfBranchSegment(BaseSegment):
    """The definition of a if branch within a function body."""

    type = "function_if_branch"
    match_grammar = Sequence(
        "IF",
        AnyNumberOf(Ref("ExpressionSegment")),
        "THEN",
        AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
        AnyNumberOf(
            Sequence(
                "ELSEIF",
                Ref("ExpressionSegment"),
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
        Ref("NakedIdentifierSegment"),
        OneOf(
            #     # for x := 1 to 10 do...
            Sequence(
                Ref("WalrusOperatorSegment"),
                # Anything(),
                Ref("ExpressionSegment"),  # could be a variable
                "TO",
                Ref("ExpressionSegment"),  # could be a variable
                "DO",
                AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
                "END",
                "FOR",
            ),
            # for x IN 1..10...
            Sequence(
                "IN",
                Ref("ExpressionSegment"),  # could be a variable
                Ref("DoubleDotSegment"),
                Ref("ExpressionSegment"),  # could be a variable
                "LOOP",
                AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
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
        Ref("ExpressionSegment"),
        "DO",
        AnyNumberOf(Ref("FunctionBodySegment"), min_times=1),
        "END",
        "WHILE",
        Ref("SemicolonSegment"),
    )


############################
# SCRIPT
############################
@exasol_fs_dialect.segment()
class ScriptReferenceSegment(ObjectReferenceSegment):
    """A reference to a script."""

    type = "script_reference"


@exasol_fs_dialect.segment()
class ScriptContentSegment(BaseSegment):
    """This represents the script content.

    Because the script content could be written in
    LUA, PYTHON, JAVA or R there is no further verification.
    """

    type = "script_content"
    match_grammar = Anything()


@exasol_fs_dialect.segment()
class CreateScriptingScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement to create a scripting script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_scripting_script"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref.keyword("ARRAY", optional=True), Ref("SingleIdentifierGrammar")
                ),
                delimiter=Ref("CommaSegment"),
            ),
            optional=True,
        ),
        Sequence(Ref.keyword("RETURNS"), OneOf("TABLE", "ROWCOUNT"), optional=True),
        "AS",
        Ref("ScriptContentSegment"),
    )


@exasol_fs_dialect.segment()
class CreateUDFScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement create a UDF script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_udf_script"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        OneOf(
            "JAVA", "PYTHON", "LUA", "R", Ref("SingleIdentifierGrammar"), optional=True
        ),
        OneOf("SCALAR", "SET"),
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        Bracketed(
            Sequence(
                Delimited(
                    Sequence(Ref("SingleIdentifierGrammar"), Ref("DatatypeSegment")),
                    delimiter=Ref("CommaSegment"),
                ),
                Sequence(
                    "ORDER",
                    "BY",
                    Delimited(
                        Ref("SingleIdentifierGrammar"),
                        OneOf("ASC", "DESC", optional=True),
                        Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
                        delimiter=Ref("CommaSegment"),
                    ),
                    optional=True,
                ),
            ),
            optional=True,
        ),
        OneOf(
            Sequence("RETURNS", Ref("DatatypeSegment")),
            Sequence(
                "EMITS",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("SingleIdentifierGrammar"), Ref("DatatypeSegment")
                        ),
                        delimiter=Ref("CommaSegment"),
                    )
                ),
            ),
        ),
        "AS",
        Ref("ScriptContentSegment"),
    )


@exasol_fs_dialect.segment()
class CreateAdapterScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement create a adapter script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_udf_script"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        OneOf("JAVA", "PYTHON", Ref("SingleIdentifierGrammar"), optional=True),
        "ADAPTER",
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        Ref("ScriptContentSegment"),
    )
