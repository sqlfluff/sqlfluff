"""The EXASOL dialect for script and function create statements.

!! DEPRECATED !! PLEASE USE THE `EXASOL` DIALECT INSTEAD !!
!! THIS DIALECT WILL BE REMOVED IN FURTHER RELEASES !!


This is seperated from the common EXASOL dialect because
`CREATE FUNCTION` and `CREATE SCRIPT` statements are not terminated
by a semicolon. They terminated by a trailing / at the end of the function / script.
A semicolon is the terminator of the statement within the function / script
https://docs.exasol.com
"""

from sqlfluff.core.parser import (
    BaseSegment,
    Delimited,
    BaseFileSegment,
    GreedyUntil,
    OneOf,
    Ref,
    SymbolSegment,
    StringParser,
)
from sqlfluff.core.dialects import load_raw_dialect
import warnings

exasol_dialect = load_raw_dialect("exasol")
exasol_fs_dialect = exasol_dialect.copy_as("exasol_fs")


exasol_fs_dialect.replace(
    SemicolonSegment=StringParser(
        ";", SymbolSegment, name="semicolon", type="semicolon"
    ),
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
class FileSegment(BaseFileSegment):
    """This ovewrites the FileSegment from ANSI.

    The reason is because SCRIPT and FUNCTION statements
    are terminated by a trailing / at the end.
    A semicolon is the terminator of the statement within the function / script
    """

    warnings.simplefilter("default")
    warnings.warn(
        (
            "The `exasol_fs` dialect is deprecated and will be removed"
            " in further releases. Please use the `exasol` dialect instead"
        ),
        DeprecationWarning,
        stacklevel=2,
    )
    parse_grammar = Delimited(
        Ref("StatementSegment"),
        delimiter=Ref("FunctionScriptTerminatorSegment"),
        allow_gaps=True,
        allow_trailing=True,
    )
