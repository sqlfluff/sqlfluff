"""
This is the core SQL grammar. We'll probably extend this or make it pluggable
for other dialects. Here we encode the structure of the language.

There shouldn't be any underlying "machinery" here, that should all
be defined elsewhere.
"""

from .segments_base import (BaseSegment)
from .segments_common import (KeywordSegment, ReSegment, NamedSegment)
from .grammar import (Sequence, GreedyUntil, StartsWith, ContainsOnly,
                      OneOf, Delimited, Bracketed, AnyNumberOf)

# NOTE: There is a concept here, of parallel grammars.
# We use one (slightly more permissive) grammar to MATCH
# and then a more detailed one to PARSE. One is called first,
# then the other - which allows sections of the file to be
# parsed even when others won't.

# Multi stage parser

# First strip comments, potentially extracting special comments (which start with sqlfluff:)
#   - this also makes comment sections, config sections (a subset of comments) and code sections

# Note on SQL Grammar
# https://www.cockroachlabs.com/docs/stable/sql-grammar.html#select_stmt


CommaSegment = KeywordSegment.make(',', name='Comma')
DotSegment = KeywordSegment.make('.', name='Dot', type='dot')

NakedIdentifierSegment = ReSegment.make(r"[A-Z0-9_]*", name='Identifier', type='naked_identifier')
QuotedIdentifierSegment = NamedSegment.make('double_quote', name='Identifier', type='quoted_identifier')
QuotedLiteralSegment = NamedSegment.make('single_quote', name='Literal', type='quoted_literal')
NumericLiteralSegment = NamedSegment.make('numeric_literal', name='Literal', type='numeric_literal')


class IdentifierSegment(BaseSegment):
    type = 'identifier'
    match_grammar = OneOf(NakedIdentifierSegment, QuotedIdentifierSegment)


class QualifiedIdentifierSegment(BaseSegment):
    type = 'identifier'
    match_grammar = Delimited(
        IdentifierSegment,
        delimiter=DotSegment,
        code_only=False,
    )


class LiteralSegment(BaseSegment):
    type = 'literal'
    match_grammar = OneOf(
        QuotedLiteralSegment, NumericLiteralSegment
    )


class ColumnExpressionSegment(BaseSegment):
    type = 'column_expression'
    match_grammar = OneOf(IdentifierSegment, code_only=False)  # QuotedIdentifierSegment


class ObjectNameSegment(BaseSegment):
    type = 'table_expression'
    # match grammar (don't allow whitespace)
    match_grammar = Delimited(IdentifierSegment, delimiter=DotSegment, code_only=False)


class AliasedObjectNameSegment(BaseSegment):
    type = 'table_expression'
    # match grammar (don't allow whitespace)
    match_grammar = Sequence(ObjectNameSegment, KeywordSegment.make('as'), IdentifierSegment)


class TableExpressionSegment(BaseSegment):
    type = 'table_expression'
    # match grammar (don't allow whitespace)
    match_grammar = OneOf(
        AliasedObjectNameSegment,
        ObjectNameSegment
        # Values clause?
    )


class SelectTargetGroupStatementSegment(BaseSegment):
    type = 'select_target_group'
    match_grammar = GreedyUntil(KeywordSegment.make('from'))
    # We should edit the parse grammar to deal with DISTINCT, ALL or similar
    # parse_grammar = Sequence(GreedyUntil(KeywordSegment.make('from')))


class JoinClauseSegment(BaseSegment):
    type = 'join_clause'
    match_grammar = OneOf(
        # Types of join clause

        # Old School Comma style clause
        Sequence(
            CommaSegment,
            TableExpressionSegment
        ),

        # New style Join clauses
        Sequence(
            # NB These qualifiers are optional
            AnyNumberOf(
                KeywordSegment.make('inner'),
                KeywordSegment.make('left'),
                KeywordSegment.make('cross'),
                max_times=1
            ),
            KeywordSegment.make('join'),
            TableExpressionSegment,
            # NB: this is optional
            AnyNumberOf(
                # ON clause
                Sequence(
                    KeywordSegment.make('on'),
                    Bracketed(
                        # This is the lazy option for now...
                        GreedyUntil(
                            KeywordSegment.make('foobar')
                        )
                    )
                ),
                # USING clause
                Sequence(
                    KeywordSegment.make('using'),
                    Bracketed(IdentifierSegment)
                ),
                max_times=1
            )
        )
    )


class FromClauseSegment(BaseSegment):
    type = 'from_clause'
    match_grammar = StartsWith(
        KeywordSegment.make('from'),
        terminator=OneOf(
            KeywordSegment.make('limit'),
            KeywordSegment.make('group'),
            KeywordSegment.make('order'),
            KeywordSegment.make('having')
        )
    )
    parse_grammar = Sequence(
        KeywordSegment.make('from'),
        TableExpressionSegment,
        AnyNumberOf(
            JoinClauseSegment
        )
    )


class OrderByClauseSegment(BaseSegment):
    type = 'orderby_clause'
    match_grammar = StartsWith(
        KeywordSegment.make('order'),
        terminator=OneOf(
            KeywordSegment.make('limit'),
            KeywordSegment.make('having')
        )
    )
    parse_grammar = Sequence(
        KeywordSegment.make('order'),
        KeywordSegment.make('by'),
        Delimited(
            Sequence(
                ObjectNameSegment,
                OneOf(
                    KeywordSegment.make('asc'),
                    KeywordSegment.make('desc'),
                    optional=True
                ),
            ),
            delimiter=CommaSegment,
            terminator=KeywordSegment.make('limit')
        )
    )


class ValuesClauseSegment(BaseSegment):
    type = 'values_clause'
    match_grammar = Sequence(
        OneOf(
            KeywordSegment.make('value'),
            KeywordSegment.make('values')
        ),
        Delimited(
            Bracketed(
                Delimited(
                    LiteralSegment,
                    delimiter=CommaSegment
                )
            ),
            delimiter=CommaSegment
        )
    )


class SelectStatementSegment(BaseSegment):
    type = 'select_statement'
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith(KeywordSegment.make('select'))
    parse_grammar = Sequence(
        KeywordSegment.make('select'),
        SelectTargetGroupStatementSegment,
        FromClauseSegment.as_optional(),
        OrderByClauseSegment.as_optional(),
        # GreedyUntil(KeywordSegment.make('limit'), optional=True)
    )


class WithCompoundStatementSegment(BaseSegment):
    type = 'with_compound_statement'
    # match grammar
    match_grammar = StartsWith(KeywordSegment.make('with'))
    parse_grammar = Sequence(
        KeywordSegment.make('with'),
        Delimited(
            Sequence(
                ObjectNameSegment,
                KeywordSegment.make('as'),
                Bracketed(SelectStatementSegment)
            ),
            delimiter=CommaSegment,
            terminator=KeywordSegment.make('select')
        ),
        SelectStatementSegment
    )


class InsertStatementSegment(BaseSegment):
    type = 'insert_statement'
    match_grammar = StartsWith(KeywordSegment.make('insert'))
    parse_grammar = Sequence(
        KeywordSegment.make('insert'),
        KeywordSegment.make('into', optional=True),
        ObjectNameSegment,
        Bracketed(Delimited(ObjectNameSegment, delimiter=CommaSegment), optional=True),
        OneOf(
            SelectStatementSegment,
            ValuesClauseSegment
        )
    )


class EmptyStatementSegment(BaseSegment):
    type = 'empty_statement'
    grammar = ContainsOnly('comment', 'newline')
    # TODO: At some point - we should lint that these are only
    # allowed at the END - otherwise it's probably a parsing error


class StatementSegment(BaseSegment):
    type = 'statement'
    parse_grammar = OneOf(SelectStatementSegment, InsertStatementSegment, EmptyStatementSegment, WithCompoundStatementSegment)
    match_grammar = GreedyUntil(KeywordSegment.make(';', name='semicolon'))
