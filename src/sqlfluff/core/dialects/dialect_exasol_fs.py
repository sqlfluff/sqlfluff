"""The EXASOL dialect for script and function create statements.

This is seperated from the common EXASOL dialect because
`CREATE FUNCTION` and `CREATE SCRIPT` statements are not terminated
by a semicolon. They terminated by a trailing / at the end of the function / script.
A semicolon is the terminator of the statement within the function / script
https://docs.exasol.com
"""

# TODO: How to turn off Jinja templating? In LUA language its possible to use {{}}. this is parsed as Jinja
# TODO: How to prevent bracket check in script body?
#       e.g. LUA: local _stmt = [[SOME ASSIGNMENT WITH OPEN BRACKET ( ]]
#                 ...do some stuff ...
#                 local _stmt = _stmt .. [[ ) ]]
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    Delimited,
    GreedyUntil,
    NamedSegment,
    OneOf,
    Ref,
    ReSegment,
    Sequence,
    StartsWith,
    SymbolSegment,
)
from sqlfluff.core.dialects.dialect_exasol import ObjectReferenceSegment, exasol_dialect

exasol_fs_dialect = exasol_dialect.copy_as("exasol_fs")
exasol_fs_dialect.sets("unreserved_keywords").add("ROWCOUNT")
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
            # TODO: this expression matches multiple functions within a raw string.
            # but it only matches one script per raw string, because the statement terminator (;)
            # is not required for scripts (e.g. not present in Python)
            # need to find another solution but don't mess up with the divide operator.
            r";\s+\/(?!\*)|\s+\/$",
            dict(
                is_code=True,
                type="statement_terminator",
                subdivide=dict(type="semicolon", name="semicolon", regex=r";"),
                trim_post_subdivide=dict(
                    type="newline", name="newline", regex=r"(\n|\r\n)*"
                ),
            ),
        ),
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
    VariableNameSegment=ReSegment.make(
        r"[A-Z][A-Z0-9_]*",
        name="function_variable",
        type="variable",
    ),
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
        Ref("CreateScriptingLuaScriptStatementSegment"),
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


@exasol_fs_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement."""

    type = "create_function_statement"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        Sequence(
            "CREATE",
            Ref("OrReplaceGrammar", optional=True),
            "FUNCTION",
        )
    )
    parse_grammar = Sequence(
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
                ),
                optional=True,
            ),
        ),
        "RETURN",
        Ref("DatatypeSegment"),
        OneOf("IS", "AS", optional=True),
        AnyNumberOf(
            Sequence(
                Ref("VariableNameSegment"),
                Ref("DatatypeSegment"),
                Ref("SemicolonSegment"),
            ),
            optional=True,
        ),
        "BEGIN",
        AnyNumberOf(Ref("FunctionBodySegment")),
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
        Ref("VariableNameSegment"),
        Ref("WalrusOperatorSegment"),
        OneOf(
            Ref("FunctionSegment"),
            Ref("VariableNameSegment"),
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
                OneOf("ELSIF", "ELSEIF"),
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
                Ref("RangeOperator"),
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
class CreateScriptingLuaScriptStatementSegment(BaseSegment):
    """`CREATE SCRIPT` statement to create a Lua scripting script.

    https://docs.exasol.com/sql/create_script.htm
    """

    type = "create_scripting_lua_script"

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        Sequence(
            "CREATE",
            Ref("OrReplaceGrammar", optional=True),
            Ref.keyword("LUA", optional=True),
            "SCRIPT",
        )
    )
    parse_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref.keyword("LUA", optional=True),
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        Bracketed(
            Delimited(
                Sequence(
                    Ref.keyword("ARRAY", optional=True), Ref("SingleIdentifierGrammar")
                ),
                optional=True,
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

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        Sequence(
            "CREATE",
            Ref("OrReplaceGrammar", optional=True),
            OneOf(
                "JAVA",
                "PYTHON",
                "LUA",
                "R",
                Ref("SingleIdentifierGrammar"),
                optional=True,
            ),
            OneOf("SCALAR", "SET"),
            "SCRIPT",
        )
    )
    parse_grammar = Sequence(
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
                Delimited(Ref("ColumnDatatypeSegment")),
                Ref("OrderByClauseSegment", optional=True),
                optional=True,
            ),
            optional=True,
        ),
        OneOf(
            Sequence("RETURNS", Ref("DatatypeSegment")),
            Sequence(
                "EMITS",
                Bracketed(
                    OneOf(
                        # EMITS (A NUMBER, B VARCHAR) or EMITS(...)
                        Delimited(Ref("ColumnDatatypeSegment")),
                        Sequence(Ref("RangeOperator"), Ref("DotSegment")),
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

    is_ddl = True
    is_dml = False
    is_dql = False
    is_dcl = False

    match_grammar = StartsWith(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        OneOf("JAVA", "PYTHON", Ref("SingleIdentifierGrammar"), optional=True),
        "ADAPTER",
        "SCRIPT",
    )
    parse_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        OneOf("JAVA", "PYTHON", Ref("SingleIdentifierGrammar"), optional=True),
        "ADAPTER",
        "SCRIPT",
        Ref("ScriptReferenceSegment"),
        Ref("ScriptContentSegment"),
    )
