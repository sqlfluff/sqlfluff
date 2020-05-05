"""The core ANSI dialect.

This is the core SQL grammar. We'll probably extend this or make it pluggable
for other dialects. Here we encode the structure of the language.

There shouldn't be any underlying "machinery" here, that should all
be defined elsewhere.

A lot of the inspiration for this sql grammar is taken from the cockroach
labs full sql grammar. In particular their way for dividing up the expression
grammar. Check out their docs, they're awesome.
https://www.cockroachlabs.com/docs/stable/sql-grammar.html#select_stmt
"""

from ..parser import (BaseSegment, KeywordSegment, ReSegment, NamedSegment,
                      Sequence, GreedyUntil, StartsWith, ContainsOnly,
                      OneOf, Delimited, Bracketed, AnyNumberOf, Ref, SegmentGenerator,
                      Anything, LambdaSegment, Indent, Dedent, Nothing)
from .base import Dialect
from .ansi_keywords import ansi_reserved_keywords, ansi_unreserved_keywords


ansi_dialect = Dialect('ansi')


ansi_dialect.set_lexer_struct([
    # name, type, pattern, kwargs
    ("whitespace", "regex", r"[\t ]+", dict(type='whitespace')),
    ("inline_comment", "regex", r"(--|#)[^\n]*", dict(is_comment=True, type='comment')),
    (
        "block_comment", "regex", r"\/\*([^\*]|\*(?!\/))*\*\/",
        dict(
            is_comment=True, type='comment',
            subdivide=dict(type='newline', name='newline', regex=r"\r\n|\n"),
            trim_post_subdivide=dict(type='whitespace', name='whitespace', regex=r"[\t ]+")
        )
    ),
    ("single_quote", "regex", r"'[^']*'", dict(is_code=True)),
    ("double_quote", "regex", r'"[^"]*"', dict(is_code=True)),
    ("back_quote", "regex", r"`[^`]*`", dict(is_code=True)),
    ("numeric_literal", "regex", r"([0-9]+(\.[0-9]+)?)", dict(is_code=True)),
    ("not_equal", "regex", r"!=|<>", dict(is_code=True)),
    ("greater_than_or_equal", "regex", r">=", dict(is_code=True)),
    ("less_than_or_equal", "regex", r"<=", dict(is_code=True)),
    ("newline", "regex", r"\r\n|\n", dict(type='newline')),
    ("casting_operator", "regex", r"::", dict(is_code=True)),
    ("concat_operator", "regex", r"\|\|", dict(is_code=True)),
    ("equals", "singleton", "=", dict(is_code=True)),
    ("greater_than", "singleton", ">", dict(is_code=True)),
    ("less_than", "singleton", "<", dict(is_code=True)),
    ("dot", "singleton", ".", dict(is_code=True)),
    ("comma", "singleton", ",", dict(is_code=True, type='comma')),
    ("plus", "singleton", "+", dict(is_code=True)),
    ("tilde", "singleton", "~", dict(is_code=True)),
    ("minus", "singleton", "-", dict(is_code=True)),
    ("divide", "singleton", "/", dict(is_code=True)),
    ("star", "singleton", "*", dict(is_code=True)),
    ("bracket_open", "singleton", "(", dict(is_code=True)),
    ("bracket_close", "singleton", ")", dict(is_code=True)),
    ("sq_bracket_open", "singleton", "[", dict(is_code=True)),
    ("sq_bracket_close", "singleton", "]", dict(is_code=True)),
    ("colon", "singleton", ":", dict(is_code=True)),
    ("semicolon", "singleton", ";", dict(is_code=True)),
    ("code", "regex", r"[0-9a-zA-Z_]*", dict(is_code=True))
])

# Set the datetime units
ansi_dialect.sets('datetime_units').update([
    'DAY', 'DAYOFYEAR', 'HOUR', 'MILLISECOND', 'MINUTE', 'MONTH',
    'QUARTER', 'SECOND', 'WEEK', 'WEEKDAY', 'YEAR'
])

# Set Keywords
ansi_dialect.sets('unreserved_keywords').update(
    [n.strip().upper() for n in ansi_unreserved_keywords.split('\n')]
)

ansi_dialect.sets('reserved_keywords').update(
    [n.strip().upper() for n in ansi_reserved_keywords.split('\n')]
)

ansi_dialect.add(
    # NB The NonCode Segment is not really for matching, mostly just for use as a terminator
    _NonCodeSegment=LambdaSegment.make(lambda x: not x.is_code, is_code=False, name='non_code'),
    # Real segments
    SemicolonSegment=KeywordSegment.make(';', name="semicolon"),
    ColonSegment=KeywordSegment.make(':', name="colon"),
    SliceSegment=KeywordSegment.make(':', name="slice"),
    StartBracketSegment=KeywordSegment.make('(', name='start_bracket', type='start_bracket'),
    EndBracketSegment=KeywordSegment.make(')', name='end_bracket', type='end_bracket'),
    StartSquareBracketSegment=KeywordSegment.make('[', name='start_square_bracket', type='start_square_bracket'),
    EndSquareBracketSegment=KeywordSegment.make(']', name='end_square_bracket', type='end_square_bracket'),
    CommaSegment=KeywordSegment.make(',', name='comma', type='comma'),
    DotSegment=KeywordSegment.make('.', name='dot', type='dot'),
    StarSegment=KeywordSegment.make('*', name='star'),
    TildeSegment=KeywordSegment.make('~', name='tilde'),
    CastOperatorSegment=KeywordSegment.make('::', name='casting_operator', type='casting_operator'),
    PlusSegment=KeywordSegment.make('+', name='plus', type='binary_operator'),
    MinusSegment=KeywordSegment.make('-', name='minus', type='binary_operator'),
    DivideSegment=KeywordSegment.make('/', name='divide', type='binary_operator'),
    MultiplySegment=KeywordSegment.make('*', name='multiply', type='binary_operator'),
    ConcatSegment=KeywordSegment.make('||', name='concatenate', type='binary_operator'),
    EqualsSegment=KeywordSegment.make('=', name='equals', type='comparison_operator'),
    GreaterThanSegment=KeywordSegment.make('>', name='greater_than', type='comparison_operator'),
    LessThanSegment=KeywordSegment.make('<', name='less_than', type='comparison_operator'),
    GreaterThanOrEqualToSegment=KeywordSegment.make('>=', name='greater_than_equal_to', type='comparison_operator'),
    LessThanOrEqualToSegment=KeywordSegment.make('<=', name='less_than_equal_to', type='comparison_operator'),
    NotEqualToSegment_a=KeywordSegment.make('!=', name='not_equal_to', type='comparison_operator'),
    NotEqualToSegment_b=KeywordSegment.make('<>', name='not_equal_to', type='comparison_operator'),
    # The strange regex here it to make sure we don't accidentally match numeric literals. We
    # also use a regex to explicitly exclude disallowed keywords.
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: ReSegment.make(
            r"[A-Z0-9_]*[A-Z][A-Z0-9_]*", name='identifier', type='naked_identifier',
            _anti_template=r"^(" + r'|'.join(dialect.sets('reserved_keywords')) + r")$")
    ),
    FunctionNameSegment=ReSegment.make(r"[A-Z][A-Z0-9_]*", name='function_name', type='function_name'),
    # Maybe data types should be more restrictive?
    DatatypeIdentifierSegment=ReSegment.make(r"[A-Z][A-Z0-9_]*", name='data_type_identifier', type='data_type_identifier'),
    # Ansi Intervals
    DatetimeUnitSegment=SegmentGenerator(
        lambda dialect: ReSegment.make(
            r"^(" + r"|".join(dialect.sets('datetime_units')) + r")$",
            name='date_part', type='date_part')
    ),
    QuotedIdentifierSegment=NamedSegment.make('double_quote', name='identifier', type='quoted_identifier'),
    QuotedLiteralSegment=NamedSegment.make('single_quote', name='literal', type='quoted_literal'),
    NumericLiteralSegment=NamedSegment.make('numeric_literal', name='literal', type='numeric_literal'),
    TrueSegment=KeywordSegment.make('true', name='true', type='boolean_literal'),
    FalseSegment=KeywordSegment.make('false', name='false', type='boolean_literal'),
    # We use a GRAMMAR here not a Segment. Otherwise we get an unecessary layer
    SingleIdentifierGrammar=OneOf(Ref('NakedIdentifierSegment'), Ref('QuotedIdentifierSegment')),
    BooleanLiteralGrammar=OneOf(Ref('TrueSegment'), Ref('FalseSegment')),
    # We specifically define a group of arithmetic operators to make it easier to override this
    # if some dialects have different available operators
    ArithmeticBinaryOperatorGrammar=OneOf(
        Ref('PlusSegment'), Ref('MinusSegment'), Ref('DivideSegment'), Ref('MultiplySegment')),
    StringBinaryOperatorGrammar=OneOf(
        Ref('ConcatSegment')),
    BooleanBinaryOperatorGrammar=OneOf(
        Ref('AndKeywordSegment'), Ref('OrKeywordSegment')),
    ComparisonOperatorGrammar=OneOf(
        Ref('EqualsSegment'), Ref('GreaterThanSegment'), Ref('LessThanSegment'),
        Ref('GreaterThanOrEqualToSegment'), Ref('LessThanOrEqualToSegment'),
        Ref('NotEqualToSegment_a'), Ref('NotEqualToSegment_b')),
    LiteralGrammar=OneOf(
        Ref('QuotedLiteralSegment'), Ref('NumericLiteralSegment'),
        Ref('BooleanLiteralGrammar'), Ref('QualifiedNumericLiteralSegment'),
        # NB: Null is included in the literals, because it is a keyword which
        # can otherwise be easily mistaken for an identifier.
        Ref('NullKeywordSegment')
    ),
    AndKeywordSegment=KeywordSegment.make('and', type='binary_operator'),
    OrKeywordSegment=KeywordSegment.make('or', type='binary_operator'),
    # This is a placeholder for other dialects.
    PreTableFunctionKeywordsGrammar=Nothing(),
)


@ansi_dialect.segment()
class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment."""
    type = 'interval_expression'
    match_grammar = Sequence(
        Ref.keyword('INTERVAL'),
        OneOf(
            # The Numeric Version
            Sequence(
                Ref('NumericLiteralSegment'),
                OneOf(
                    Ref('QuotedLiteralSegment'),
                    Ref('DatetimeUnitSegment')
                )
            ),
            # The String version
            Ref('QuotedLiteralSegment'),
        )
    )


@ansi_dialect.segment()
class DatatypeSegment(BaseSegment):
    """A data type segment."""
    type = 'data_type'
    match_grammar = Sequence(
        Ref('DatatypeIdentifierSegment'),
        Bracketed(
            OneOf(
                Delimited(
                    Ref('ExpressionSegment'),
                    delimiter=Ref('CommaSegment')
                ),
                # The brackets might be empty for some cases...
                optional=True
            ),
            # There may be no brackets for some data types
            optional=True
        )
    )


@ansi_dialect.segment()
class ColumnExpressionSegment(BaseSegment):
    """A reference to a column."""
    type = 'column_expression'
    match_grammar = OneOf(Ref('SingleIdentifierGrammar'), code_only=False)  # QuotedIdentifierSegment


@ansi_dialect.segment()
class ObjectReferenceSegment(BaseSegment):
    """A reference to an object."""
    type = 'object_reference'
    # match grammar (don't allow whitespace)
    match_grammar = Delimited(
        Ref('SingleIdentifierGrammar'),
        delimiter=OneOf(
            Ref('DotSegment'),
            Sequence(
                Ref('DotSegment')
            )
        ),
        terminator=OneOf(
            Ref('_NonCodeSegment'), Ref('CommaSegment'),
            Ref('CastOperatorSegment'), Ref('StartSquareBracketSegment'),
            Ref('StartBracketSegment'), Ref('ArithmeticBinaryOperatorGrammar'),
            Ref('StringBinaryOperatorGrammar'),
            Ref('ComparisonOperatorGrammar'), Ref('ColonSegment'),
            Ref('SemicolonSegment')
        ),
        code_only=False
    )


@ansi_dialect.segment()
class ArrayAccessorSegment(BaseSegment):
    """An array accessor e.g. [3:4]."""
    type = 'array_accessor'
    match_grammar = Bracketed(
        Anything(),
        # Use square brackets
        square=True
    )
    parse_grammar = Bracketed(
        Delimited(
            # We use the no-match version here so we get the correct
            # handling of the potential colon. We also use Delimited
            # so that we look for the colon FIRST, because we should
            # know to expect one and the parser gets confused otherwise.
            OneOf(
                Ref('NumericLiteralSegment'),
                Ref('ExpressionSegment_NoMatch')
            ),
            delimiter=Ref('SliceSegment')
        ),
        # Use square brackets
        square=True
    )


@ansi_dialect.segment()
class AliasedObjectReferenceSegment(BaseSegment):
    """A reference to an object with an `AS` clause."""
    type = 'object_reference'
    match_grammar = Sequence(Ref('ObjectReferenceSegment'), Ref('AliasExpressionSegment'))


@ansi_dialect.segment()
class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    """
    type = 'alias_expression'
    match_grammar = Sequence(Ref.keyword('AS', optional=True), Ref('SingleIdentifierGrammar'))


@ansi_dialect.segment()
class ShorthandCastSegment(BaseSegment):
    """A casting operation using '::'."""
    type = 'cast_expression'
    match_grammar = Sequence(
        Ref('CastOperatorSegment'),
        Ref('DatatypeSegment'),
        code_only=False
    )


@ansi_dialect.segment()
class QualifiedNumericLiteralSegment(BaseSegment):
    """A numeric literal with a + or - sign preceeding.

    The qualified numeric literal is a compound of a raw
    literal and a plus/minus sign. We do it this way rather
    than at the lexing step because the lexer doesn't deal
    well with ambiguity.
    """

    type = 'numeric_literal'
    match_grammar = Sequence(
        OneOf(Ref('PlusSegment'), Ref('MinusSegment')),
        Ref('NumericLiteralSegment'),
        code_only=False)


ansi_dialect.add(
    # FunctionContentsExpressionGrammar intended as a hook to override
    # in other dialects
    FunctionContentsExpressionGrammar=Ref('ExpressionSegment'),
    FunctionContentsGrammar=OneOf(
        # A Cast-like function
        Sequence(
            Ref('ExpressionSegment'),
            Ref.keyword('AS'),
            Ref('DatatypeSegment')
        ),
        # An extract-like function
        Sequence(
            Ref('DatetimeUnitSegment'),
            Ref.keyword('FROM'),
            Ref('ExpressionSegment')
        ),
        Sequence(
            # Allow an optional distinct keyword here.
            Ref.keyword('DISTINCT', optional=True),
            OneOf(
                # Most functions will be using the delimited route
                # but for COUNT(*) or similar we allow the star segment
                # here.
                Ref('StarSegment'),
                Delimited(
                    Ref('FunctionContentsExpressionGrammar'),
                    delimiter=Ref('CommaSegment')
                ),
            ),
        )
    )
)


@ansi_dialect.segment()
class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """
    type = 'function'
    match_grammar = Sequence(
        Sequence(
            Ref('FunctionNameSegment'),
            Bracketed(
                Anything(optional=True)
            ),
        ),
        Sequence(
            Ref.keyword('OVER'),
            Bracketed(
                Anything(optional=True)
            ),
            optional=True
        )
    )
    parse_grammar = Sequence(
        Sequence(
            Ref('FunctionNameSegment'),
            Bracketed(
                Ref(
                    'FunctionContentsGrammar',
                    # The brackets might be empty for some functions...
                    optional=True)
            ),
        ),
        # Optional suffix for window functions.
        # TODO: Should this be in a different dialect?
        Sequence(
            Ref.keyword('OVER'),
            Bracketed(
                Sequence(
                    Ref('PartitionClauseSegment', optional=True),
                    Ref('OrderByClauseSegment', optional=True),
                    Ref('FrameClauseSegment', optional=True)
                )
            ),
            optional=True
        )
    )


@ansi_dialect.segment()
class PartitionClauseSegment(BaseSegment):
    """A `PARTITION BY` for window functions."""
    type = 'partitionby_clause'
    match_grammar = StartsWith(
        Ref.keyword('PARTITION'),
        terminator=OneOf(
            Ref.keyword('ORDER'),
            Ref.keyword('ROWS')
        )
    )
    parse_grammar = Sequence(
        Ref.keyword('PARTITION'),
        Ref.keyword('BY'),
        Indent,
        Delimited(
            Ref('ExpressionSegment'),
            delimiter=Ref('CommaSegment')
        ),
        Dedent,
    )


@ansi_dialect.segment()
class FrameClauseSegment(BaseSegment):
    """A frame clause for window functions."""
    type = 'frame_clause'
    match_grammar = StartsWith(
        Ref.keyword('ROWS')
    )
    # TODO: Expand a parse statement here properly to actually
    # parse rather than assuming that it's good.
    # parse_grammar = Sequence(
    #    Ref.keyword('ROWS'),
    #    ...
    # )


@ansi_dialect.segment()
class TableExpressionSegment(BaseSegment):
    """A table expression."""
    type = 'table_expression'
    match_grammar = Sequence(
        Ref('PreTableFunctionKeywordsGrammar', optional=True),
        OneOf(
            # Functions allowed here for table expressions.
            # Perhaps this should just be in a dialect, but
            # it seems sensible here for now.
            Ref('FunctionSegment'),
            Ref('ObjectReferenceSegment'),
            # Nested Selects
            Bracketed(
                OneOf(
                    Ref('SetExpressionSegment'),
                    Ref('SelectStatementSegment')
                ),
                Ref('WithCompoundStatementSegment')
            ),
            # Values clause?
        ),
        Ref('AliasExpressionSegment', optional=True),
        Sequence(
            Ref.keyword('WITH'),
            Ref.keyword('OFFSET'),
            Ref.keyword('AS'),
            Ref('SingleIdentifierGrammar'),
            optional=True
        ),
    )


@ansi_dialect.segment()
class SelectTargetElementSegment(BaseSegment):
    """An element in the targets of a select statement."""
    type = 'select_target_element'
    # Important to split elements before parsing, otherwise debugging is really hard.
    match_grammar = GreedyUntil(Ref('CommaSegment'))
    parse_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Sequence(
            AnyNumberOf(
                Sequence(
                    Ref('SingleIdentifierGrammar'),
                    Ref('DotSegment'),
                    code_only=True
                )
            ),
            Ref('StarSegment'), code_only=False
        ),
        Sequence(
            OneOf(
                Ref('LiteralGrammar'),
                Ref('FunctionSegment'),
                Ref('IntervalExpressionSegment'),
                Ref('ObjectReferenceSegment')
            ),
            Ref('AliasExpressionSegment', optional=True)
        ),
        Sequence(
            OneOf(
                # We use the unbound version here, so that we can optionally
                # have space for our Alias at the end. This is potentially
                # very slow. There's probably a better way for this, but
                # it's not obvious what that is right now.
                Ref('ExpressionSegment_NoMatch'),
            ),
            Ref('AliasExpressionSegment', optional=True)
        ),
    )


@ansi_dialect.segment()
class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement."""
    type = 'select_clause'
    match_grammar = GreedyUntil(
        OneOf(
            Ref.keyword('FROM'),
            Ref.keyword('LIMIT')
        )
    )
    # We should edit the parse grammar to deal with DISTINCT, ALL or similar
    parse_grammar = Sequence(
        Ref.keyword('SELECT'),
        OneOf(
            Ref.keyword('DISTINCT'),
            Ref.keyword('ALL'),
            optional=True
        ),
        Indent,
        Delimited(
            Ref('SelectTargetElementSegment'),
            delimiter=Ref('CommaSegment')
        ),
        Dedent
    )


@ansi_dialect.segment()
class JoinClauseSegment(BaseSegment):
    """Any number of join clauses, including the `JOIN` keyword."""
    type = 'join_clause'
    match_grammar = Sequence(
        # NB These qualifiers are optional
        AnyNumberOf(
            Ref.keyword('FULL'),
            Ref.keyword('INNER'),
            Ref.keyword('LEFT'),
            Ref.keyword('CROSS'),
            max_times=1,
            optional=True
        ),
        Ref.keyword('OUTER', optional=True),
        Ref.keyword('JOIN'),
        Indent,
        Ref('TableExpressionSegment'),
        # NB: this is optional
        AnyNumberOf(
            # ON clause
            Sequence(
                Ref.keyword('ON'),
                Indent,
                OneOf(
                    Ref('ExpressionSegment'),
                    Bracketed(Ref('ExpressionSegment'))
                ),
                Dedent
            ),
            # USING clause
            Sequence(
                Ref.keyword('USING'),
                Indent,
                Bracketed(
                    Delimited(
                        Ref('SingleIdentifierGrammar'),
                        delimiter=Ref('CommaSegment')
                    )
                ),
                Dedent
            ),
            # Unqualified joins *are* allowed. They just might not
            # be a good idea.
            min_times=0
        ),
        Dedent
    )


@ansi_dialect.segment()
class FromClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT`."""
    type = 'from_clause'
    match_grammar = StartsWith(
        Ref.keyword('FROM'),
        terminator=OneOf(
            Ref.keyword('WHERE'),
            Ref.keyword('LIMIT'),
            Ref.keyword('GROUP'),
            Ref.keyword('ORDER'),
            Ref.keyword('HAVING')
        )
    )
    parse_grammar = Sequence(
        Ref.keyword('FROM'),
        Indent,
        Delimited(
            # Optional old school delimited joins
            Ref('TableExpressionSegment'),
            delimiter=Ref('CommaSegment'),
            terminator=OneOf(
                Ref.keyword('JOIN'),
                Ref.keyword('CROSS'),
                Ref.keyword('INNER'),
                Ref.keyword('LEFT'),
                Ref.keyword('FULL')
            )
        ),
        # NB: The JOIN clause is *part of* the FROM clause
        # and so should be on a sub-indent of it. That isn't
        # common practice however, so for now it will be assumed
        # to be on the same level as the FROM clause. To change
        # this behaviour, set the `indented_joins` config value
        # to True.
        Dedent.when(indented_joins=False),
        AnyNumberOf(
            Ref('JoinClauseSegment'),
            optional=True
        ),
        Dedent.when(indented_joins=True)
    )


@ansi_dialect.segment()
class CaseExpressionSegment(BaseSegment):
    """A `CASE WHEN` clause."""
    type = 'case_expression'
    # This method of matching doesn't work with nested case statements.
    # TODO: Develop something more powerful for this.
    # match_grammar = StartsWith(
    #     Ref.keyword('CASE'),
    #     terminator=Ref.keyword('END'),
    #     include_terminator=True
    # )
    match_grammar = Sequence(
        Ref.keyword('CASE'),
        Indent,
        AnyNumberOf(
            Sequence(
                # We use the unbound version of Expression here, so that we
                # deal with potentially nested case statements where the
                # parsing gets confused by which WHERE and END goes with
                # which CASE. TODO: Come up with a better solution for this.
                Ref.keyword('WHEN'),
                Indent,
                Ref('ExpressionSegment_NoMatch'),
                Ref.keyword('THEN'),
                Ref('ExpressionSegment_NoMatch'),
                Dedent
            )
        ),
        Sequence(
            Ref.keyword('ELSE'),
            Indent,
            Ref('ExpressionSegment_NoMatch'),
            Dedent,
            optional=True
        ),
        Dedent,
        Ref.keyword('END')
    )


ansi_dialect.add(
    Expression_A_Grammar=Sequence(
        OneOf(
            Ref('Expression_C_Grammar'),
            Sequence(
                OneOf(
                    Ref('PlusSegment'),
                    Ref('MinusSegment'),
                    Ref('TildeSegment'),
                    Ref.keyword('NOT')
                ),
                Ref('Expression_A_Grammar')
            )
        ),
        AnyNumberOf(
            OneOf(
                Sequence(
                    OneOf(
                        Ref('ArithmeticBinaryOperatorGrammar'),
                        Ref('StringBinaryOperatorGrammar'),
                        Ref('ComparisonOperatorGrammar'),
                        Ref('BooleanBinaryOperatorGrammar'),
                        Sequence(
                            Ref.keyword('NOT', optional=True),
                            OneOf(
                                Ref.keyword('LIKE'),
                                Ref.keyword('RLIKE'),
                                Ref.keyword('ILIKE')
                            )
                        )
                        # We need to add a lot more here...
                    ),
                    Ref('Expression_A_Grammar')
                ),
                Sequence(
                    Ref.keyword('NOT', optional=True),
                    Ref.keyword('IN'),
                    Bracketed(
                        OneOf(
                            Delimited(
                                Ref('LiteralGrammar'),
                                Ref('IntervalExpressionSegment'),
                                delimiter=Ref('CommaSegment')
                            ),
                            Ref('SelectStatementSegment')
                        )
                    )
                ),
                Sequence(
                    Ref.keyword('IS'),
                    Ref.keyword('NOT', optional=True),
                    OneOf(
                        Ref.keyword('NULL'),
                        Ref.keyword('NAN'),
                        # TODO: True and False might not be allowed here in some
                        # dialects (e.g. snowflake) so we should probably
                        # revisit this at some point. Perhaps abstract this clause
                        # into an "is-statement grammar", which could be overridden.
                        Ref('BooleanLiteralGrammar')
                    )
                ),
                Sequence(
                    Ref.keyword('NOT', optional=True),
                    Ref.keyword('BETWEEN'),
                    Ref('Expression_C_Grammar'),
                    Ref.keyword('AND'),
                    Ref('Expression_C_Grammar')
                )
            )
        )
    ),
    Expression_B_Grammar=None,  # TODO
    Expression_C_Grammar=OneOf(
        Ref('Expression_D_Grammar'),
        Ref('CaseExpressionSegment'),
        Sequence(
            Ref.keyword('EXISTS'),
            Ref('SelectStatementSegment')
        )
    ),
    Expression_D_Grammar=Sequence(
        OneOf(
            Ref('FunctionSegment'),
            Bracketed(
                Ref('Expression_A_Grammar')
            ),
            Bracketed(
                Ref('SelectStatementSegment')
            ),
            # Allow potential select statement without brackets
            Ref('SelectStatementSegment'),
            Ref('LiteralGrammar'),
            Ref('IntervalExpressionSegment'),
            Ref('ObjectReferenceSegment')
        ),
        Ref('Accessor_Grammar', optional=True),
        Ref('ShorthandCastSegment', optional=True),
        code_only=False
    ),
    Accessor_Grammar=AnyNumberOf(
        Ref('ArrayAccessorSegment')
    )
)


@ansi_dialect.segment()
class ExpressionSegment(BaseSegment):
    """A expression, either arithmetic or boolean.

    NB: This is potentially VERY recursive and
    mostly uses the grammars above.
    """
    type = 'expression'
    match_grammar = GreedyUntil(
        Ref('CommaSegment'),
        Ref.keyword('AS'),
        Ref.keyword('ASC'),
        Ref.keyword('DESC'),
        Ref.keyword('INNER'),
        Ref.keyword('LEFT'),
        Ref.keyword('CROSS'),
        Ref.keyword('JOIN'),
        Ref.keyword('WHERE'),
        Ref.keyword('GROUP'),
        Ref.keyword('ORDER'),
    )
    parse_grammar = Ref('Expression_A_Grammar')


@ansi_dialect.segment()
class ExpressionSegment_NoMatch(ExpressionSegment):
    """A expression, either arithmetic or boolean.

    NB: This is potentially VERY recursive and
    mostly uses the grammars above. This version
    also doesn't bound itself first, and so is potentially
    VERY SLOW. I don't really like this solution.

    The purpose of this particular version of the segment
    is so that we can make sure we don't swallow a potential
    alias following the epxression. The other expression
    segments are more efficient but potentially parse
    alias expressions incorrectly if no AS keyword is used.
    """
    match_grammar = Ref('Expression_A_Grammar')
    parse_grammar = None


@ansi_dialect.segment()
class ExpressionSegment_TermWhenElse(ExpressionSegment):
    """Expression terminated by WHEN, END or ELSE."""
    match_grammar = GreedyUntil(
        Ref.keyword('WHEN'),
        Ref.keyword('ELSE'),
        Ref.keyword('END')
    )


@ansi_dialect.segment()
class ExpressionSegment_TermThen(ExpressionSegment):
    """Expression terminated by THEN."""
    match_grammar = GreedyUntil(Ref.keyword('THEN'))


@ansi_dialect.segment()
class ExpressionSegment_TermEnd(ExpressionSegment):
    """Expression terminated by END."""
    match_grammar = GreedyUntil(Ref.keyword('END'))


@ansi_dialect.segment()
class WhereClauseSegment(BaseSegment):
    """A `WHERE` clause like in `SELECT` or `INSERT`."""
    type = 'where_clause'
    match_grammar = StartsWith(
        Ref.keyword('WHERE'),
        terminator=OneOf(
            Ref.keyword('LIMIT'),
            Ref.keyword('GROUP'),
            Ref.keyword('ORDER'),
            Ref.keyword('HAVING')
        )
    )
    parse_grammar = Sequence(
        Ref.keyword('WHERE'),
        Indent,
        Ref('ExpressionSegment'),
        Dedent
    )


@ansi_dialect.segment()
class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`."""
    type = 'orderby_clause'
    match_grammar = StartsWith(
        Ref.keyword('ORDER'),
        terminator=OneOf(
            Ref.keyword('LIMIT'),
            Ref.keyword('HAVING'),
            # For window functions
            Ref.keyword('ROWS')
        )
    )
    parse_grammar = Sequence(
        Ref.keyword('ORDER'),
        Ref.keyword('BY'),
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    Ref('ObjectReferenceSegment'),
                    # Can `ORDER BY 1`
                    Ref('NumericLiteralSegment'),
                    # Can order by an expression
                    Ref('ExpressionSegment')
                ),
                OneOf(
                    Ref.keyword('ASC'),
                    Ref.keyword('DESC'),
                    optional=True
                ),
            ),
            delimiter=Ref('CommaSegment'),
            terminator=Ref.keyword('LIMIT')
        ),
        Dedent
    )


@ansi_dialect.segment()
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""
    type = 'groupby_clause'
    match_grammar = StartsWith(
        Sequence(
            Ref.keyword('GROUP'),
            Ref.keyword('BY')
        ),
        terminator=OneOf(
            Ref.keyword('ORDER'),
            Ref.keyword('LIMIT'),
            Ref.keyword('HAVING')
        )
    )
    parse_grammar = Sequence(
        Ref.keyword('GROUP'),
        Ref.keyword('BY'),
        Indent,
        Delimited(
            OneOf(
                Ref('ObjectReferenceSegment'),
                # Can `GROUP BY 1`
                Ref('NumericLiteralSegment')
            ),
            delimiter=Ref('CommaSegment'),
            terminator=OneOf(
                Ref.keyword('ORDER'),
                Ref.keyword('LIMIT'),
                Ref.keyword('HAVING')
            )
        ),
        Dedent
    )


@ansi_dialect.segment()
class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`."""
    type = 'having_clause'
    match_grammar = StartsWith(
        Ref.keyword('HAVING'),
        terminator=OneOf(
            Ref.keyword('ORDER'),
            Ref.keyword('LIMIT')
        )
    )
    parse_grammar = Sequence(
        Ref.keyword('HAVING'),
        Indent,
        OneOf(
            Bracketed(
                Ref('ExpressionSegment'),
            ),
            Ref('ExpressionSegment')
        ),
        Dedent
    )


@ansi_dialect.segment()
class LimitClauseSegment(BaseSegment):
    """A `LIMIT` clause like in `SELECT`."""
    type = 'limit_clause'
    match_grammar = Sequence(
        Ref.keyword('LIMIT'),
        Ref('NumericLiteralSegment')
    )


@ansi_dialect.segment()
class ValuesClauseSegment(BaseSegment):
    """A `VALUES` clause like in `INSERT`."""
    type = 'values_clause'
    match_grammar = Sequence(
        OneOf(
            Ref.keyword('VALUE'),
            Ref.keyword('VALUES')
        ),
        Delimited(
            Bracketed(
                Delimited(
                    Ref('LiteralGrammar'),
                    Ref('IntervalExpressionSegment'),
                    delimiter=Ref('CommaSegment')
                )
            ),
            delimiter=Ref('CommaSegment')
        )
    )


@ansi_dialect.segment()
class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement."""
    type = 'select_statement'
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith(Ref.keyword('SELECT'))
    parse_grammar = Sequence(
        Ref('SelectClauseSegment'),
        Ref('FromClauseSegment', optional=True),
        Ref('WhereClauseSegment', optional=True),
        Ref('GroupByClauseSegment', optional=True),
        Ref('HavingClauseSegment', optional=True),
        Ref('OrderByClauseSegment', optional=True),
        Ref('LimitClauseSegment', optional=True),
        # GreedyUnt.keywordil(.make('limit'), optional=True)
    )


@ansi_dialect.segment()
class WithCompoundStatementSegment(BaseSegment):
    """A `SELECT` statement preceeded by a selection of `WITH` clauses."""
    type = 'with_compound_statement'
    # match grammar
    match_grammar = StartsWith(Ref.keyword('WITH'))
    parse_grammar = Sequence(
        Ref.keyword('WITH'),
        Delimited(
            Sequence(
                Ref('SingleIdentifierGrammar'),
                Ref.keyword('AS'),
                Bracketed(
                    OneOf(
                        Ref('SetExpressionSegment'),
                        Ref('SelectStatementSegment')
                    )
                )
            ),
            delimiter=Ref('CommaSegment'),
            terminator=Ref.keyword('SELECT')
        ),
        Ref('SelectStatementSegment')
    )


@ansi_dialect.segment()
class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Minus, Exept or Intersect."""
    type = 'set_operator'
    match_grammar = OneOf(
        Sequence(
            Ref.keyword('UNION'),
            OneOf(
                Ref.keyword('DISTINCT'),
                Ref.keyword('ALL'),
                optional=True
            )
        ),
        Ref.keyword('INTERSECT'),
        Ref.keyword('EXCEPT'),
        Ref.keyword('MINUS')
    )


@ansi_dialect.segment()
class SetExpressionSegment(BaseSegment):
    """A set expression with either Union, Minus, Exept or Intersect."""
    type = 'set_expression'
    # match grammar
    match_grammar = Delimited(
        OneOf(
            Ref('SelectStatementSegment'),
            Ref('ValuesClauseSegment'),
            Ref('WithCompoundStatementSegment')
        ),
        delimiter=Ref('SetOperatorSegment'),
        min_delimiters=1
    )


@ansi_dialect.segment()
class InsertStatementSegment(BaseSegment):
    """A `INSERT` statement."""
    type = 'insert_statement'
    match_grammar = StartsWith(Ref.keyword('INSERT'))
    parse_grammar = Sequence(
        Ref.keyword('INSERT'),
        Ref.keyword('OVERWRITE', optional=True),  # Maybe this is just snowflake?
        Ref.keyword('INTO', optional=True),
        Ref('ObjectReferenceSegment'),
        Bracketed(Delimited(Ref('ObjectReferenceSegment'), delimiter=Ref('CommaSegment')), optional=True),
        OneOf(
            Ref('SelectStatementSegment'),
            Ref('ValuesClauseSegment'),
            Ref('WithCompoundStatementSegment')
        )
    )


@ansi_dialect.segment()
class EmptyStatementSegment(BaseSegment):
    """A placeholder for a statement containing nothing but whitespace and comments."""
    type = 'empty_statement'
    grammar = ContainsOnly('comment', 'newline')
    # TODO: At some point - we should lint that these are only
    # allowed at the END - otherwise it's probably a parsing error


@ansi_dialect.segment()
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT` or `ROLLBACK` statement."""
    type = 'transaction_statement'
    match_grammar = OneOf(
        # COMMIT [ WORK ] [ AND [ NO ] CHAIN ]
        Sequence(
            Ref.keyword('COMMIT'),
            Ref.keyword('WORK', optional=True),
            Sequence(
                Ref.keyword('AND'),
                Ref.keyword('NO', optional=True),
                Ref.keyword('CHAIN'),
                optional=True
            )
        ),
        # NOTE: "TO SAVEPOINT" is not yet supported
        # ROLLBACK [ WORK ] [ AND [ NO ] CHAIN ]
        Sequence(
            Ref.keyword('ROLLBACK'),
            Ref.keyword('WORK', optional=True),
            Sequence(
                Ref.keyword('AND'),
                Ref.keyword('NO', optional=True),
                Ref.keyword('CHAIN'),
                optional=True
            )
        ),
    )


@ansi_dialect.segment()
class ColumnOptionSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""
    type = 'column_constraint'
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
        Sequence(
            Ref.keyword('CONSTRAINT'),
            Ref('ObjectReferenceSegment'),  # Constraint name
            optional=True
        ),
        OneOf(
            Sequence(  # NOT NULL or NULL
                Ref.keyword('NOT', optional=True),
                Ref.keyword('NULL')
            ),
            Sequence(  # DEFAULT <value>
                Ref.keyword('DEFAULT'),
                Ref('LiteralGrammar'),
                # ?? Ref('IntervalExpressionSegment')
            ),
            Sequence(  # PRIMARY KEY
                Ref.keyword('PRIMARY'),
                Ref.keyword('KEY'),
            ),
            Ref.keyword('UNIQUE'),  # UNIQUE
            Ref.keyword('AUTO_INCREMENT'),  # AUTO_INCREMENT (MySQL)
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                Ref.keyword('REFERENCES'),
                Ref('ObjectReferenceSegment'),
                Bracketed(  # Foreign columns making up FOREIGN KEY constraint
                    Delimited(
                        Ref('ObjectReferenceSegment'),
                        delimiter=Ref('CommaSegment')
                    ),
                    optional=True
                ),
            ),
            Sequence(  # [COMMENT 'string'] (MySQL)
                Ref.keyword('COMMENT'),
                Ref('QuotedLiteralSegment'),
            ),
        ),
    )


@ansi_dialect.segment()
class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""
    type = 'column_definition'
    match_grammar = Sequence(
        Ref('SingleIdentifierGrammar'),  # Column name
        Ref('DatatypeSegment'),  # Column type
        Bracketed(  # For types like VARCHAR(100)
            Anything(),
            optional=True
        ),
        AnyNumberOf(
            Ref('ColumnOptionSegment', optional=True),
        )
    )


@ansi_dialect.segment()
class TableConstraintSegment(BaseSegment):
    """A table constraint, e.g. for CREATE TABLE."""
    type = 'table_constraint_definition'
    # Later add support for CHECK constraint, others?
    # e.g. CONSTRAINT constraint_1 PRIMARY KEY(column_1)
    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            Ref.keyword('CONSTRAINT'),
            Ref('ObjectReferenceSegment'),
            optional=True
        ),
        OneOf(
            Sequence(  # UNIQUE ( column_name [, ... ] )
                Ref.keyword('UNIQUE'),
                Bracketed(  # Columns making up UNIQUE constraint
                    Delimited(
                        Ref('ObjectReferenceSegment'),
                        delimiter=Ref('CommaSegment')
                    ),
                ),
                # Later add support for index_parameters?
            ),
            Sequence(  # PRIMARY KEY ( column_name [, ... ] ) index_parameters
                Ref.keyword('PRIMARY'),
                Ref.keyword('KEY'),
                Bracketed(  # Columns making up PRIMARY KEY constraint
                    Delimited(
                        Ref('ObjectReferenceSegment'),
                        delimiter=Ref('CommaSegment')
                    ),
                ),
                # Later add support for index_parameters?
            ),
            Sequence(  # FOREIGN KEY ( column_name [, ... ] )
                       # REFERENCES reftable [ ( refcolumn [, ... ] ) ]
                Ref.keyword('FOREIGN'),
                Ref.keyword('KEY'),
                Bracketed(  # Local columns making up FOREIGN KEY constraint
                    Delimited(
                        Ref('ObjectReferenceSegment'),
                        delimiter=Ref('CommaSegment')
                    ),
                ),
                Ref.keyword('REFERENCES'),
                Ref('ObjectReferenceSegment'),
                Bracketed(  # Foreign columns making up FOREIGN KEY constraint
                    Delimited(
                        Ref('ObjectReferenceSegment'),
                        delimiter=Ref('CommaSegment')
                    ),
                ),
                # Later add support for [MATCH FULL/PARTIAL/SIMPLE] ?
                # Later add support for [ ON DELETE/UPDATE action ] ?
            ),
        ),
    )


@ansi_dialect.segment()
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""
    type = 'create_table_statement'
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
        Ref.keyword('CREATE'),
        Sequence(
            Ref.keyword('OR'),
            Ref.keyword('REPLACE'),
            optional=True
        ),
        Ref.keyword('TABLE'),
        Sequence(
            Ref.keyword('IF'),
            Ref.keyword('NOT'),
            Ref.keyword('EXISTS'),
            optional=True
        ),
        Ref('ObjectReferenceSegment'),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref('ColumnDefinitionSegment'),
                            Ref('TableConstraintSegment'),
                        ),
                        delimiter=Ref('CommaSegment')
                    )
                ),
                Sequence(  # [COMMENT 'string'] (MySQL)
                    Ref.keyword('COMMENT'),
                    Ref('QuotedLiteralSegment'),
                    optional=True
                )
            ),
            # Create AS syntax:
            Sequence(
                Ref.keyword('AS'),
                OneOf(
                    Ref('SelectStatementSegment'),
                    Ref('WithCompoundStatementSegment')
                )
            ),
            # Create like syntax
            Sequence(
                Ref.keyword('LIKE'),
                Ref('ObjectReferenceSegment')
            )
        )
    )


@ansi_dialect.segment()
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement."""
    type = 'create_view_statement'
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html#create-view-statement
    # https://dev.mysql.com/doc/refman/8.0/en/create-view.html
    # https://www.postgresql.org/docs/12/sql-createview.html
    match_grammar = Sequence(
        Ref.keyword('CREATE'),
        Sequence(
            Ref.keyword('OR'),
            Ref.keyword('REPLACE'),
            optional=True
        ),
        Ref.keyword('VIEW'),
        Ref('ObjectReferenceSegment'),
        Bracketed(  # Optional list of column names
            Delimited(
                Ref('ObjectReferenceSegment'),
                delimiter=Ref('CommaSegment')
            ),
            optional=True
        ),
        Ref.keyword('AS'),
        Ref('SelectStatementSegment'),
    )


@ansi_dialect.segment()
class DropStatementSegment(BaseSegment):
    """A `DROP` statement."""
    type = 'drop_statement'
    # DROP {TABLE | VIEW} <Table name> [IF EXISTS} {RESTRICT | CASCADE}
    match_grammar = Sequence(
        Ref.keyword('DROP'),
        OneOf(
            Ref.keyword('TABLE'),
            Ref.keyword('VIEW'),
        ),
        Sequence(
            Ref.keyword('IF'),
            Ref.keyword('EXISTS'),
            optional=True
        ),
        Ref('ObjectReferenceSegment'),
        OneOf(
            Ref.keyword('RESTRICT'),
            Ref.keyword('CASCADE', optional=True),
            optional=True
        )
    )


@ansi_dialect.segment()
class AccessStatementSegment(BaseSegment):
    """A `GRANT` or `REVOKE` statement."""
    type = 'access_statement'
    # Based on https://www.postgresql.org/docs/12/sql-grant.html
    match_grammar = OneOf(
        Sequence(
            Ref.keyword('GRANT'),
            Delimited(  # List of permission types
                Sequence(
                    OneOf(  # Permission type
                        Sequence(
                            Ref.keyword('ALL'),
                            Ref.keyword('PRIVILEGES', optional=True)
                        ),
                        Ref.keyword('SELECT'),
                        Ref.keyword('UPDATE'),
                        Ref.keyword('INSERT'),
                    ),
                    Bracketed(  # Optional list of column names
                        Delimited(
                            Ref('ObjectReferenceSegment'),
                            delimiter=Ref('CommaSegment')
                        ),
                        optional=True
                    )
                ),
                delimiter=Ref('CommaSegment')
            ),
            Ref.keyword('ON'),
            OneOf(
                Sequence(
                    Ref.keyword('TABLE', optional=True),
                    Ref('ObjectReferenceSegment'),
                ),
                Sequence(
                    Ref.keyword('ALL'),
                    Ref.keyword('TABLES'),
                    Ref.keyword('IN'),
                    Ref.keyword('SCHEMA'),
                    Ref('ObjectReferenceSegment'),
                )
            ),
            Ref.keyword('TO'),
            OneOf(
                Ref.keyword('GROUP'),
                Ref.keyword('USER'),
                Ref.keyword('ROLE'),
                optional=True
            ),
            OneOf(
                Ref('ObjectReferenceSegment'),
                Ref.keyword('PUBLIC'),
            ),
            Sequence(
                Ref.keyword('WITH'),
                Ref.keyword('GRANT'),
                Ref.keyword('OPTION'),
                optional=True
            ),
        ),
        # Based on https://www.postgresql.org/docs/12/sql-revoke.html
        Sequence(
            Ref.keyword('REVOKE'),
            Delimited(  # List of permission types
                Sequence(
                    Sequence(
                        Ref.keyword('GRANT'),
                        Ref.keyword('OPTION'),
                        Ref.keyword('FOR'),
                        optional=True
                    ),
                    OneOf(  # Permission type
                        Sequence(
                            Ref.keyword('ALL'),
                            Ref.keyword('PRIVILEGES', optional=True)
                        ),
                        Ref.keyword('SELECT'),
                        Ref.keyword('UPDATE'),
                        Ref.keyword('INSERT'),
                    ),
                    Bracketed(  # Optional list of column names
                        Delimited(
                            Ref('ObjectReferenceSegment'),
                            delimiter=Ref('CommaSegment')
                        ),
                        optional=True
                    )
                ),
                delimiter=Ref('CommaSegment')
            ),
            Ref.keyword('ON'),
            OneOf(
                Sequence(
                    Ref.keyword('TABLE', optional=True),
                    Ref('ObjectReferenceSegment'),
                ),
                Sequence(
                    Ref.keyword('ALL'),
                    Ref.keyword('TABLES'),
                    Ref.keyword('IN'),
                    Ref.keyword('SCHEMA'),
                    Ref('ObjectReferenceSegment'),
                )
            ),
            Ref.keyword('FROM'),
            OneOf(
                Ref.keyword('GROUP'),
                Ref.keyword('USER'),
                Ref.keyword('ROLE'),
                optional=True
            ),
            Ref('ObjectReferenceSegment'),
            OneOf(
                Ref.keyword('RESTRICT'),
                Ref.keyword('CASCADE', optional=True),
                optional=True
            )
        ),
    )


@ansi_dialect.segment()
class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    DELETE FROM <table name> [ WHERE <search condition> ]
    """
    type = 'delete_statement'
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith(Ref.keyword('DELETE'))
    parse_grammar = Sequence(
        Ref.keyword('DELETE'),
        Ref('FromClauseSegment'),
        Ref('WhereClauseSegment', optional=True),
    )


@ansi_dialect.segment()
class UpdateStatementSegment(BaseSegment):
    """A `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    """
    type = 'delete_statement'
    match_grammar = StartsWith(Ref.keyword('UPDATE'))
    parse_grammar = Sequence(
        Ref.keyword('UPDATE'),
        Ref('ObjectReferenceSegment'),
        Ref('SetClauseListSegment'),
        Ref('WhereClauseSegment', optional=True),
    )


@ansi_dialect.segment()
class SetClauseListSegment(BaseSegment):
    """SQL 1992 set clause list.

    <set clause list> ::=
              <set clause> [ { <comma> <set clause> }... ]

         <set clause> ::=
              <object column> <equals operator> <update source>

         <update source> ::=
                <value expression>
              | <null specification>
              | DEFAULT

         <object column> ::= <column name>
    """
    type = 'set_clause_list'
    match_grammar = Sequence(
        Ref.keyword('SET'),
        Indent,
        OneOf(
            Ref('SetClauseSegment'),
            # set clause
            AnyNumberOf(
                Delimited(
                    Ref('SetClauseSegment'),
                    delimiter=Ref('CommaSegment')
                ),
            ),
        ),
        Dedent,
    )


@ansi_dialect.segment()
class SetClauseSegment(BaseSegment):
    """SQL 1992 set clause.

    <set clause> ::=
              <object column> <equals operator> <update source>

         <update source> ::=
                <value expression>
              | <null specification>
              | DEFAULT

         <object column> ::= <column name>
    """
    type = 'set_clause'

    match_grammar = Sequence(
        Ref('ColumnExpressionSegment'),
        Ref('EqualsSegment'),
        OneOf(
            Ref('LiteralGrammar'),
            Ref('FunctionSegment'),
            Ref('ObjectReferenceSegment'),
            Ref.keyword('NULL'),
            Ref.keyword('DEFAULT'),
        )
    )


@ansi_dialect.segment()
class StatementSegment(BaseSegment):
    """A generic segment, to any of it's child subsegments.

    NOTE: Should this actually be a grammar?
    """
    type = 'statement'
    parse_grammar = OneOf(
        Ref('SetExpressionSegment'),
        Ref('SelectStatementSegment'), Ref('InsertStatementSegment'),
        Ref('EmptyStatementSegment'), Ref('WithCompoundStatementSegment'),
        Ref('TransactionStatementSegment'), Ref('DropStatementSegment'),
        Ref('AccessStatementSegment'), Ref('CreateTableStatementSegment'),
        Ref('CreateViewStatementSegment'),
        Ref('DeleteStatementSegment'), Ref('UpdateStatementSegment'),
    )
    match_grammar = GreedyUntil(Ref('SemicolonSegment'))
