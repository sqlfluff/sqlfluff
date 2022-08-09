"""The Oracle dialect.

This inherits from the ansi dialect.
"""
from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    BaseFileSegment,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Delimited,
    GreedyUntil,
    Matchable,
    Ref,
    RegexLexer,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    OneOf,
)

from sqlfluff.core.parser.segments.base import BracketedSegment
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")
oracle_dialect = ansi_dialect.copy_as("oracle")

oracle_dialect.sets("unreserved_keywords").difference_update(["COMMENT"])
oracle_dialect.sets("reserved_keywords").update(
    ["COMMENT", "ON", "UPDATE", "INDEXTYPE", "PROMPT"]
)


oracle_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "prompt_command",
            r"PROMPT([^(\r\n)])*((?=\n)|(?=\r\n))?",
            CommentSegment,
        ),
        StringLexer("at_sign", "@", CodeSegment),
    ],
    before="code",
)

oracle_dialect.add(
    AtSignSegment=StringParser("@", SymbolSegment, type="at_sign"),
)


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """An `ALTER TABLE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html
    If possible, please keep the order below the same as Oracle's doc:
    """

    match_grammar: Matchable = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # @TODO all stuff inside this "Delimited" is not validated for Oracle
            Delimited(
                OneOf(
                    # Table options
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment", optional=True),
                        OneOf(Ref("LiteralGrammar"), Ref("NakedIdentifierSegment")),
                    ),
                ),
            ),
            Ref("AlterTablePropertiesSegment"),
            Ref("AlterTableColumnClausesSegment"),
            Ref("AlterTableConstraintClauses"),
        ),
    )


class AlterTablePropertiesSegment(BaseSegment):
    """ALTER TABLE `alter_table_properties` per defined in Oracle's grammar.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html

    If possible, please match the order of this sequence with what's defined in
    Oracle's alter_table_properties grammar.
    """

    type = "alter_table_properties"

    # TODO: There are many more alter_table_properties to implement
    match_grammar = OneOf(
        # Rename
        Sequence(
            "RENAME",
            "TO",
            Ref("TableReferenceSegment"),
        ),
    )


class AlterTableColumnClausesSegment(BaseSegment):
    """ALTER TABLE `column_clauses` per defined in Oracle's grammar.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html

    If possible, please match the order of this sequence with what's defined in
    Oracle's column_clauses grammar.
    """

    type = "alter_table_column_clauses"

    match_grammar = OneOf(
        # add_column_clause
        # modify_column_clause
        Sequence(
            OneOf(
                "ADD",
                "MODIFY",
            ),
            OneOf(
                Ref("ColumnDefinitionSegment"),
                Bracketed(Delimited(Ref("ColumnDefinitionSegment"))),
            ),
        ),
        # drop_column_clause
        # @TODO: extend drop_column_clause
        Sequence(
            "DROP",
            OneOf(
                Sequence("COLUMN", Ref("ColumnReferenceSegment")),
                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            ),
        ),
        # @TODO: add_period_clause
        # @TODO: drop_period_clause
        # rename_column_clause
        Sequence(
            "RENAME",
            "COLUMN",
            Ref("ColumnReferenceSegment"),
            "TO",
            Ref("ColumnReferenceSegment"),
        )
        # @TODO: modify_collection_retrieval
        # @TODO: modify_LOB_storage_clause
        # @TODO: alter_varray_col_properties
    )


class AlterTableConstraintClauses(BaseSegment):
    """ALTER TABLE `constraint_clauses` per defined in Oracle's grammar.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html

    If possible, please match the order of this sequence with what's defined in
    Oracle's constraint_clauses grammar.
    """

    type = "alter_table_constraint_clauses"

    match_grammar = OneOf(
        Sequence(
            "ADD",
            Ref("TableConstraintSegment"),
        ),
        # @TODO MODIFY
        # @TODO RENAME
        # @TODO DROP
        # drop_constraint_clause
        Sequence(
            "DROP",
            OneOf(
                Sequence(
                    "PRIMARY",
                    "KEY",
                ),
                Sequence(
                    "UNIQUE",
                    Bracketed(Ref("ColumnReferenceSegment")),
                ),
                Sequence("CONSTRAINT", Ref("ObjectReferenceSegment")),
            ),
            Ref.keyword("CASCADE", optional=True),
            Sequence(
                OneOf(
                    "KEEP",
                    "DROP",
                ),
                "INDEX",
                optional=True,
            ),
            Ref.keyword("ONLINE", optional=True),
        ),
    )


class ExecuteFileSegment(BaseSegment):
    """A reference to an indextype."""

    type = "execute_file_statement"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                Ref("AtSignSegment"),
                Ref("AtSignSegment", optional=True),
            ),
            "START",
        ),
        # Probably should have a better file definition but this will do for now
        AnyNumberOf(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            Ref("DivideSegment"),
        ),
    )


class IndexTypeReferenceSegment(BaseSegment):
    """A reference to an indextype."""

    type = "indextype_reference"

    match_grammar = ansi.ObjectReferenceSegment.match_grammar.copy()


# Adding Oracle specific statements.
class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments.

    Override ANSI to allow exclusion of ExecuteFileSegment.
    """

    type = "statement"

    match_grammar = OneOf(
        GreedyUntil(Ref("DelimiterGrammar")), exclude=Ref("ExecuteFileSegment")
    )
    parse_grammar = ansi.StatementSegment.parse_grammar.copy(
        insert=[
            Ref("CommentStatementSegment"),
        ],
    )


class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.

    Override ANSI to allow addition of ExecuteFileSegment without
    ending in DelimiterGrammar
    """

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    parse_grammar = AnyNumberOf(
        Ref("ExecuteFileSegment"),
        Delimited(
            Ref("StatementSegment"),
            delimiter=AnyNumberOf(Ref("DelimiterGrammar"), min_times=1),
            allow_gaps=True,
            allow_trailing=True,
        ),
    )


class CommentStatementSegment(BaseSegment):
    """A `Comment` statement.

    COMMENT [text]
    https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_4009.htm
    """

    type = "comment_statement"

    match_grammar = Sequence(
        "COMMENT",
        "ON",
        Sequence(
            OneOf(
                Sequence(
                    "TABLE",
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "COLUMN",
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    "OPERATOR",
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "INDEXTYPE",
                    Ref("IndexTypeReferenceSegment"),
                ),
                Sequence(
                    "MATERIALIZED",
                    "VIEW",
                    Ref("TableReferenceSegment"),
                ),
            ),
            Sequence("IS", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
        ),
    )


# Inherit from the ANSI ObjectReferenceSegment this way so we can inherit
# other segment types from it.
class ObjectReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an object."""

    pass


# need to ignore type due to mypy rules on type variables
# see https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
# for details
class TableReferenceSegment(ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias.

    Extended from ANSI to allow Database Link syntax using AtSignSegment
    """

    type = "table_reference"
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=OneOf(
            Ref("DotSegment"),
            Sequence(Ref("DotSegment"), Ref("DotSegment")),
            Ref("AtSignSegment"),
        ),
        terminator=OneOf(
            "ON",
            "AS",
            "USING",
            Ref("CommaSegment"),
            Ref("CastOperatorSegment"),
            Ref("StartSquareBracketSegment"),
            Ref("StartBracketSegment"),
            Ref("BinaryOperatorGrammar"),
            Ref("ColonSegment"),
            Ref("DelimiterGrammar"),
            Ref("JoinLikeClauseGrammar"),
            BracketedSegment,
        ),
        allow_gaps=False,
    )
