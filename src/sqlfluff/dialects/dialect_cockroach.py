"""The Cockroach dialect."""

from sqlfluff.core.parser import (
    OneOf,
    Ref,
    Sequence,
    Bracketed,
    Anything,
    BaseSegment,
    Delimited,
    RegexLexer,
    CodeSegment,
    NamedParser,
    RegexParser,
    StringParser,
    SymbolSegment,
)

from sqlfluff.core.dialects import load_raw_dialect

ansi_dialect = load_raw_dialect("ansi")

postgres_dialect = load_raw_dialect("postgres")

cockroach_dialect = postgres_dialect.copy_as("cockroach")

cockroach_dialect.insert_lexer_matchers(
    # this is needed for Cockroach's hideous index optimiser hint syntax, "tablename@indexname"
    [
        RegexLexer(
            "at",
            r"(?<![<])@(?![>])",
            CodeSegment,
        )
    ],
    before="json_operator",
)

            # r"[_A-Z]*[_A-Z0-9]@[_A-Z]*[_A-Z0-9]",

cockroach_dialect.add(
    AtSegment=StringParser(
        "@", SymbolSegment, name="at", type="at"
    ),
)

@cockroach_dialect.segment(replace=True)
class DropIndexStatementSegment(BaseSegment):
    """A `DROP INDEX` statement."""

    type = "drop_statement"
    # DROP INDEX <Index name> [CONCURRENTLY] [IF EXISTS] {RESTRICT | CASCADE}
    match_grammar = Sequence(
        "DROP",
        "INDEX",
        Ref.keyword("CONCURRENTLY", optional=True),
        Ref("IfExistsGrammar", optional=True),
        Ref("IndexExpressionSegment"),
        OneOf("RESTRICT", Ref.keyword("CASCADE", optional=True), optional=True),
    )


@cockroach_dialect.segment(replace=True)
class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` statement."""

    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "INDEX",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexExpressionSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence(
            Bracketed(
                Delimited(
                    Ref("IndexColumnDefinitionSegment"),
                ),
            )
        ),
    )


@cockroach_dialect.segment(replace=True)
class TableExpressionSegment(BaseSegment):
    """The main table expression e.g. within a FROM clause."""

    type = "table_expression"
    match_grammar = OneOf(
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("TableReferenceSegment"),
        # you can use these in all DML
        Ref("HintedTableReferenceSegment"), 
        # Nested Selects
        Bracketed(Ref("SelectableGrammar")),
        # Values clause?
    )


@cockroach_dialect.segment()
class IndexExpressionSegment(BaseSegment):
    """An index expression."""

    type = "index_expression"
    match_grammar = OneOf(
        Ref("IndexReferenceSegment"),
        # you can use these in all DML
        Ref("HintedTableReferenceSegment"), 
    )


@cockroach_dialect.segment()
class HintedTableReferenceSegment(BaseSegment):
    """Cockroach index hints for the optimiser."""

    type = "hinted_table"
    match_grammar = Sequence(
        Ref("TableReferenceSegment"),
        Ref("AtSegment"),
        Ref("IndexReferenceSegment"),
    )

    parse_grammar = Sequence(
        Ref("TableReferenceSegment"),
        Ref("AtSegment"),
        Ref("IndexReferenceSegment"),
    )


@cockroach_dialect.segment()
class HintedIndexReferenceSegment(BaseSegment):
    """Cockroach index hints for the optimiser."""

    type = "hinted_index"
    match_grammar = Sequence(
        Ref("TableReferenceSegment"),
        Ref("AtSegment"),
        Ref("IndexReferenceSegment"),
    )

    parse_grammar = Sequence(
        Ref("TableReferenceSegment"),
        Ref("AtSegment"),
        Ref("IndexReferenceSegment"),
    )

