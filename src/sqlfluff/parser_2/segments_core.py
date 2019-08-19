"""
This is the core SQL grammar. We'll probably extend this or make it pluggable
for other dialects. Here we encode the structure of the language.

There shouldn't be any underlying "machinery" here, that should all
be defined elsewhere.
"""

from .segments_base import (BaseSegment)
from .segments_common import (KeywordSegment, ReSegment, NamedSegment)
from .grammar import (Sequence, GreedyUntil, StartsWith, ContainsOnly,
                      OneOf, Delimited)

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


class IdentifierSegment(BaseSegment):
    type = 'identifier'
    match_grammar = Delimited(OneOf(NakedIdentifierSegment, QuotedIdentifierSegment), delimiter=DotSegment, code_only=False)


class ColumnExpressionSegment(BaseSegment):
    type = 'column_expression'
    match_grammar = OneOf(IdentifierSegment, code_only=False)  # QuotedIdentifierSegment


class TableExpressionSegment(BaseSegment):
    type = 'table_expression'
    # match grammar (don't allow whitespace)
    match_grammar = Delimited(IdentifierSegment, delimiter=DotSegment, code_only=False)


class SelectTargetGroupStatementSegment(BaseSegment):
    type = 'select_target_group'
    match_grammar = GreedyUntil(KeywordSegment.make('from'))
    # We should edit the parse grammar to deal with DISTINCT, ALL or similar
    # parse_grammar = Sequence(GreedyUntil(KeywordSegment.make('from')))


class FromClauseSegment(BaseSegment):
    type = 'from_clause'
    # From here down, comments are printed seperately.
    comment_seperate = True
    match_grammar = Sequence(KeywordSegment.make('from'), Delimited(TableExpressionSegment, delimiter=CommaSegment))


class SelectStatementSegment(BaseSegment):
    type = 'select_statement'
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith(KeywordSegment.make('select'))
    parse_grammar = Sequence(
        KeywordSegment.make('select'),
        SelectTargetGroupStatementSegment,
        FromClauseSegment.as_optional(),
        # GreedyUntil(KeywordSegment.make('limit'), optional=True)
    )


class WithCompoundStatementSegment(BaseSegment):
    type = 'with_compound_statement'
    # match grammar
    match_grammar = StartsWith(KeywordSegment.make('with'))
    # TODO: Re-enable this to parse the segment properly
    # parse_grammar = Sequence(KeywordSegment.make('select'), SelectTargetGroupStatementSegment, GreedyUntil(KeywordSegment.make('limit')))


class InsertStatementSegment(BaseSegment):
    type = 'insert_statement'
    grammar = StartsWith(KeywordSegment.make('insert'))


class EmptyStatementSegment(BaseSegment):
    type = 'empty_statement'
    grammar = ContainsOnly('comment', 'newline')
    # TODO: At some point - we should lint that these are only
    # allowed at the END - otherwise it's probably a parsing error


class StatementSegment(BaseSegment):
    type = 'statement'
    parse_grammar = OneOf(SelectStatementSegment, InsertStatementSegment, EmptyStatementSegment, WithCompoundStatementSegment)
    match_grammar = GreedyUntil(KeywordSegment.make(';', name='semicolon'))
