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
                      OneOf, Delimited, Bracketed, AnyNumberOf, Ref,
                      Anything, LambdaSegment, Indent, Dedent)
from .base import Dialect


ansi_dialect = Dialect('ansi')


ansi_dialect.set_lexer_struct([
    # name, type, pattern, kwargs
    ("whitespace", "regex", r"[\t ]*", dict(type='whitespace')),
    ("inline_comment", "regex", r"(--|#)[^\n]*", dict(is_comment=True)),
    ("block_comment", "regex", r"\/\*([^\*]|\*[^\/])*\*\/", dict(is_comment=True)),
    ("single_quote", "regex", r"'[^']*'", dict(is_code=True)),
    ("double_quote", "regex", r'"[^"]*"', dict(is_code=True)),
    ("back_quote", "regex", r"`[^`]*`", dict(is_code=True)),
    ("numeric_literal", "regex", r"([0-9]+(\.[0-9]+)?)", dict(is_code=True)),
    ("not_equal", "regex", r"!=|<>", dict(is_code=True)),
    ("greater_than_or_equal", "regex", r">=", dict(is_code=True)),
    ("less_than_or_equal", "regex", r"<=", dict(is_code=True)),
    ("newline", "regex", r"\r\n", dict(type='newline')),
    ("casting_operator", "regex", r"::", dict(is_code=True)),
    ("newline", "singleton", "\n", dict(type='newline')),
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


ansi_dialect.add(
    # NB The NonCode Segment is not really for matching, mostly just for use as a terminator
    _NonCodeSegment=LambdaSegment.make(lambda x: not x.is_code, is_code=False, name='non_code'),
    # Real segments
    SemicolonSegment=KeywordSegment.make(';', name="semicolon"),
    SliceSegment=KeywordSegment.make(':', name="slice"),
    StartBracketSegment=KeywordSegment.make('(', name='start_bracket', type='start_bracket'),
    EndBracketSegment=KeywordSegment.make(')', name='end_bracket', type='end_bracket'),
    StartSquareBracketSegment=KeywordSegment.make('[', name='start_square_bracket', type='start_square_bracket'),
    EndSquareBracketSegment=KeywordSegment.make(']', name='end_square_bracket', type='end_square_bracket'),
    CommaSegment=KeywordSegment.make(',', name='comma', type='comma'),
    DotSegment=KeywordSegment.make('.', name='dot', type='dot'),
    StarSegment=KeywordSegment.make('*', name='star'),
    TildeSegment=KeywordSegment.make('~', name='tilde'),
    CastOperatorKeywordSegment=KeywordSegment.make('::', name='casting_operator', type='casting_operator'),
    PlusSegment=KeywordSegment.make('+', name='plus', type='binary_operator'),
    MinusSegment=KeywordSegment.make('-', name='minus', type='binary_operator'),
    DivideSegment=KeywordSegment.make('/', name='divide', type='binary_operator'),
    MultiplySegment=KeywordSegment.make('*', name='multiply', type='binary_operator'),
    EqualsSegment=KeywordSegment.make('=', name='equals', type='comparison_operator'),
    GreaterThanSegment=KeywordSegment.make('>', name='greater_than', type='comparison_operator'),
    LessThanSegment=KeywordSegment.make('<', name='less_than', type='comparison_operator'),
    GreaterThanOrEqualToSegment=KeywordSegment.make('>=', name='greater_than_equal_to', type='comparison_operator'),
    LessThanOrEqualToSegment=KeywordSegment.make('<=', name='less_than_equal_to', type='comparison_operator'),
    NotEqualToSegment_a=KeywordSegment.make('!=', name='not_equal_to', type='comparison_operator'),
    NotEqualToSegment_b=KeywordSegment.make('<>', name='not_equal_to', type='comparison_operator'),
    # The strange regex here it to make sure we don't accidentally match numeric literals. We
    # also use a regex to explicitly exclude disallowed keywords.
    NakedIdentifierSegment=ReSegment.make(
        r"[A-Z0-9_]*[A-Z][A-Z0-9_]*", name='identifier', type='naked_identifier',
        _anti_template=r"^(SELECT|JOIN|ON|USING|CROSS|INNER|LEFT|RIGHT|OUTER|INTERVAL|CASE|FULL)$"),
    FunctionNameSegment=ReSegment.make(r"[A-Z][A-Z0-9_]*", name='function_name', type='function_name'),
    # Maybe data types should be more restrictive?
    DatatypeIdentifierSegment=ReSegment.make(r"[A-Z][A-Z0-9_]*", name='data_type_identifier', type='data_type_identifier'),
    # Maybe date parts should be more restrictive
    DatepartSegment=ReSegment.make(r"[A-Z][A-Z0-9_]*", name='date_part', type='date_part'),
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
    BooleanBinaryOperatorGrammar=OneOf(
        Ref('AndKeywordSegment'), Ref('OrKeywordSegment')),
    ComparisonOperatorGrammar=OneOf(
        Ref('EqualsSegment'), Ref('GreaterThanSegment'), Ref('LessThanSegment'),
        Ref('GreaterThanOrEqualToSegment'), Ref('LessThanOrEqualToSegment'),
        Ref('NotEqualToSegment_a'), Ref('NotEqualToSegment_b')),
    # Keywords
    AsKeywordSegment=KeywordSegment.make('as'),
    FromKeywordSegment=KeywordSegment.make('from'),
    DistinctKeywordSegment=KeywordSegment.make('distinct'),
    ExistsKeywordSegment=KeywordSegment.make('exists'),
    OverKeywordSegment=KeywordSegment.make('over'),
    RowsKeywordSegment=KeywordSegment.make('rows'),
    PartitionKeywordSegment=KeywordSegment.make('partition'),
    CaseKeywordSegment=KeywordSegment.make('case'),
    WhenKeywordSegment=KeywordSegment.make('when'),
    ThenKeywordSegment=KeywordSegment.make('then'),
    ElseKeywordSegment=KeywordSegment.make('else'),
    EndKeywordSegment=KeywordSegment.make('end'),
    AllKeywordSegment=KeywordSegment.make('all'),
    LimitKeywordSegment=KeywordSegment.make('limit'),
    UnionKeywordSegment=KeywordSegment.make('union'),
    MinusKeywordSegment=KeywordSegment.make('minus'),
    ExceptKeywordSegment=KeywordSegment.make('except'),
    IntersectKeywordSegment=KeywordSegment.make('intersect'),
    OnKeywordSegment=KeywordSegment.make('on'),
    OuterKeywordSegment=KeywordSegment.make('outer'),
    JoinKeywordSegment=KeywordSegment.make('join'),
    FullKeywordSegment=KeywordSegment.make('full'),
    InnerKeywordSegment=KeywordSegment.make('inner'),
    LeftKeywordSegment=KeywordSegment.make('left'),
    CrossKeywordSegment=KeywordSegment.make('cross'),
    UsingKeywordSegment=KeywordSegment.make('using'),
    WhereKeywordSegment=KeywordSegment.make('where'),
    GroupKeywordSegment=KeywordSegment.make('group'),
    OrderKeywordSegment=KeywordSegment.make('order'),
    HavingKeywordSegment=KeywordSegment.make('having'),
    OverwriteKeywordSegment=KeywordSegment.make('overwrite'),
    ByKeywordSegment=KeywordSegment.make('by'),
    InKeywordSegment=KeywordSegment.make('in'),
    IsKeywordSegment=KeywordSegment.make('is'),
    BetweenKeywordSegment=KeywordSegment.make('between'),
    NullKeywordSegment=KeywordSegment.make('null'),
    NanKeywordSegment=KeywordSegment.make('nan'),
    AndKeywordSegment=KeywordSegment.make('and', type='binary_operator'),
    OrKeywordSegment=KeywordSegment.make('or', type='binary_operator'),
    NotKeywordSegment=KeywordSegment.make('not'),
    AscKeywordSegment=KeywordSegment.make('asc'),
    DescKeywordSegment=KeywordSegment.make('desc'),
    ValueKeywordSegment=KeywordSegment.make('value'),
    ValuesKeywordSegment=KeywordSegment.make('values'),
    SelectKeywordSegment=KeywordSegment.make('select'),
    WithKeywordSegment=KeywordSegment.make('with'),
    OffsetKeywordSegment=KeywordSegment.make('offset'),
    InsertKeywordSegment=KeywordSegment.make('insert'),
    IntoKeywordSegment=KeywordSegment.make('into'),
    CommitKeywordSegment=KeywordSegment.make('commit'),
    WorkKeywordSegment=KeywordSegment.make('work'),
    NoKeywordSegment=KeywordSegment.make('no'),
    ChainKeywordSegment=KeywordSegment.make('chain'),
    RollbackKeywordSegment=KeywordSegment.make('rollback'),
    CreateKeywordSegment=KeywordSegment.make('create'),
    DropKeywordSegment=KeywordSegment.make('drop'),
    TableKeywordSegment=KeywordSegment.make('table'),
    ConstraintKeywordSegment=KeywordSegment.make('constraint'),
    UniqueKeywordSegment=KeywordSegment.make('unique'),
    PrimaryKeywordSegment=KeywordSegment.make('primary'),
    ForeignKeywordSegment=KeywordSegment.make('foreign'),
    KeyKeywordSegment=KeywordSegment.make('key'),
    AutoIncrementKeywordSegment=KeywordSegment.make('auto_increment'),
    CommentKeywordSegment=KeywordSegment.make('comment'),
    ReferencesKeywordSegment=KeywordSegment.make('references'),
    DefaultKeywordSegment=KeywordSegment.make('default'),
    IfKeywordSegment=KeywordSegment.make('if'),
    ViewKeywordSegment=KeywordSegment.make('view'),
    ReplaceKeywordSegment=KeywordSegment.make('replace'),
    RestrictKeywordSegment=KeywordSegment.make('restrict'),
    CascadeKeywordSegment=KeywordSegment.make('cascade'),
    GrantKeywordSegment=KeywordSegment.make('grant'),
    RevokeKeywordSegment=KeywordSegment.make('revoke'),
    TablesKeywordSegment=KeywordSegment.make('tables'),
    SchemaKeywordSegment=KeywordSegment.make('schema'),
    ForKeywordSegment=KeywordSegment.make('for'),
    ToKeywordSegment=KeywordSegment.make('to'),
    OptionKeywordSegment=KeywordSegment.make('option'),
    PrivilegesKeywordSegment=KeywordSegment.make('privileges'),
    UpdateKeywordSegment=KeywordSegment.make('update'),
    LikeKeywordSegment=KeywordSegment.make('like'),
    ILikeKeywordSegment=KeywordSegment.make('ilike'),
    RLikeKeywordSegment=KeywordSegment.make('rlike'),
    RoleKeywordSegment=KeywordSegment.make('role'),
    UserKeywordSegment=KeywordSegment.make('user'),
    # Some more grammars:
    IntervalKeywordSegment=KeywordSegment.make('interval'),
    LiteralGrammar=OneOf(
        Ref('QuotedLiteralSegment'), Ref('NumericLiteralSegment'),
        Ref('BooleanLiteralGrammar'), Ref('QualifiedNumericLiteralSegment'),
        Ref('IntervalLiteralSegment')
    ),
)


@ansi_dialect.segment()
class IntervalLiteralSegment(BaseSegment):
    """An interval literal segment."""
    type = 'interval_literal'
    match_grammar = Sequence(
        Ref('IntervalKeywordSegment'),
        Ref('NumericLiteralSegment'),
        OneOf(
            Ref('QuotedLiteralSegment'),
            Ref('DatepartSegment')
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
        delimiter=Ref('DotSegment'),
        terminator=OneOf(
            Ref('_NonCodeSegment'), Ref('CommaSegment'),
            Ref('CastOperatorKeywordSegment'), Ref('StartSquareBracketSegment'),
            Ref('StartBracketSegment'), Ref('ArithmeticBinaryOperatorGrammar'),
            Ref('ComparisonOperatorGrammar')
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
    match_grammar = Sequence(Ref('AsKeywordSegment', optional=True), Ref('SingleIdentifierGrammar'))


@ansi_dialect.segment()
class ShorthandCastSegment(BaseSegment):
    """A casting operation using '::'."""
    type = 'cast_expression'
    match_grammar = Sequence(
        Ref('CastOperatorKeywordSegment'),
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
            Ref('OverKeywordSegment'),
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
                OneOf(
                    # A Cast-like function
                    Sequence(
                        Ref('ExpressionSegment'),
                        Ref('AsKeywordSegment'),
                        Ref('DatatypeSegment')
                    ),
                    # An extract-like function
                    Sequence(
                        Ref('DatepartSegment'),
                        Ref('FromKeywordSegment'),
                        Ref('ExpressionSegment')
                    ),
                    Sequence(
                        # Allow an optional distinct keyword here.
                        Ref('DistinctKeywordSegment', optional=True),
                        OneOf(
                            # Most functions will be using the delimited route
                            # but for COUNT(*) or similar we allow the star segment
                            # here.
                            Ref('StarSegment'),
                            Delimited(
                                Ref('ExpressionSegment'),
                                delimiter=Ref('CommaSegment')
                            ),
                        ),
                    ),
                    # The brackets might be empty for some functions...
                    optional=True
                )
            ),
        ),
        # Optional suffix for window functions.
        # TODO: Should this be in a different dialect?
        Sequence(
            Ref('OverKeywordSegment'),
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
        Ref('PartitionKeywordSegment'),
        terminator=OneOf(
            Ref('OrderKeywordSegment'),
            Ref('RowsKeywordSegment')
        )
    )
    parse_grammar = Sequence(
        Ref('PartitionKeywordSegment'),
        Ref('ByKeywordSegment'),
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
        Ref('RowsKeywordSegment')
    )
    # TODO: Expand a parse statement here properly to actually
    # parse rather than assuming that it's good.
    # parse_grammar = Sequence(
    #    Ref('RowsKeywordSegment'),
    #    ...
    # )


@ansi_dialect.segment()
class TableExpressionSegment(BaseSegment):
    """A table expression."""
    type = 'table_expression'
    match_grammar = Sequence(
        OneOf(
            # Functions allowed here for table expressions.
            # Perhaps this should just be in a dialect, but
            # it seems sensible here for now.
            Ref('FunctionSegment'),
            Ref('ObjectReferenceSegment'),
            # Nested Selects
            Bracketed(
                Ref('SelectStatementSegment'),
                Ref('WithCompoundStatementSegment')
            )
            # Values clause?
        ),
        Ref('AliasExpressionSegment', optional=True),
        Sequence(
            Ref('WithKeywordSegment'),
            Ref('OffsetKeywordSegment'),
            Ref('AsKeywordSegment'),
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
        # *
        Ref('StarSegment'),
        # blah.*
        Sequence(Ref('SingleIdentifierGrammar'), Ref('DotSegment'), Ref('StarSegment'), code_only=False),
        Sequence(
            OneOf(
                Ref('LiteralGrammar'),
                Ref('FunctionSegment'),
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
            Ref('FromKeywordSegment'),
            Ref('LimitKeywordSegment')
        )
    )
    # We should edit the parse grammar to deal with DISTINCT, ALL or similar
    parse_grammar = Sequence(
        Ref('SelectKeywordSegment'),
        OneOf(
            Ref('DistinctKeywordSegment'),
            Ref('AllKeywordSegment'),
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
            Ref('FullKeywordSegment'),
            Ref('InnerKeywordSegment'),
            Ref('LeftKeywordSegment'),
            Ref('CrossKeywordSegment'),
            max_times=1,
            optional=True
        ),
        Ref('OuterKeywordSegment', optional=True),
        Ref('JoinKeywordSegment'),
        Indent,
        Ref('TableExpressionSegment'),
        # NB: this is optional
        AnyNumberOf(
            # ON clause
            Sequence(
                Ref('OnKeywordSegment'),
                Indent,
                OneOf(
                    Ref('ExpressionSegment'),
                    Bracketed(Ref('ExpressionSegment'))
                ),
                Dedent
            ),
            # USING clause
            Sequence(
                Ref('UsingKeywordSegment'),
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
        Ref('FromKeywordSegment'),
        terminator=OneOf(
            Ref('WhereKeywordSegment'),
            Ref('LimitKeywordSegment'),
            Ref('GroupKeywordSegment'),
            Ref('OrderKeywordSegment'),
            Ref('HavingKeywordSegment')
        )
    )
    parse_grammar = Sequence(
        Ref('FromKeywordSegment'),
        Indent,
        Delimited(
            # Optional old school delimited joins
            Ref('TableExpressionSegment'),
            delimiter=Ref('CommaSegment'),
            terminator=OneOf(
                Ref('JoinKeywordSegment'),
                Ref('CrossKeywordSegment'),
                Ref('InnerKeywordSegment'),
                Ref('LeftKeywordSegment'),
                Ref('FullKeywordSegment')
            )
        ),
        # NB: The JOIN clause is *part of* the FROM clause
        # and so should be on a sub-indent of it. That isn't
        # common practice however, so for now it will be assumed
        # to be on the same level as the FROM clause. To change
        # this behaviour, the Dedent would come after the AnyNumberOf
        # rather than before. TODO: In future this might be
        # configurable.
        Dedent,
        AnyNumberOf(
            Ref('JoinClauseSegment'),
            optional=True
        ),
    )


@ansi_dialect.segment()
class CaseExpressionSegment(BaseSegment):
    """A `CASE WHEN` clause."""
    type = 'case_expression'
    # This method of matching doesn't work with nested case statements.
    # TODO: Develop something more powerful for this.
    # match_grammar = StartsWith(
    #     Ref('CaseKeywordSegment'),
    #     terminator=Ref('EndKeywordSegment'),
    #     include_terminator=True
    # )
    match_grammar = Sequence(
        Ref('CaseKeywordSegment'),
        Indent,
        AnyNumberOf(
            Sequence(
                # We use the unbound version of Expression here, so that we
                # deal with potentially nested case statements where the
                # parsing gets confused by which WHERE and END goes with
                # which CASE. TODO: Come up with a better solution for this.
                Ref('WhenKeywordSegment'),
                Indent,
                Ref('ExpressionSegment_NoMatch'),
                Ref('ThenKeywordSegment'),
                Ref('ExpressionSegment_NoMatch'),
                Dedent
            )
        ),
        Sequence(
            Ref('ElseKeywordSegment'),
            Indent,
            Ref('ExpressionSegment_NoMatch'),
            Dedent,
            optional=True
        ),
        Dedent,
        Ref('EndKeywordSegment')
    )


ansi_dialect.add(
    Expression_A_Grammar=Sequence(
        OneOf(
            Ref('Expression_C_Grammar'),
            Sequence(
                OneOf(
                    # Ref('PlusSegment'),
                    # Ref('MinusSegment'),
                    # Ref('TildeSegment'),
                    Ref('NotKeywordSegment')
                ),
                Ref('Expression_A_Grammar')
            )
        ),
        AnyNumberOf(
            OneOf(
                Sequence(
                    OneOf(
                        Ref('ArithmeticBinaryOperatorGrammar'),
                        Ref('ComparisonOperatorGrammar'),
                        Ref('BooleanBinaryOperatorGrammar'),
                        Sequence(
                            Ref('NotKeywordSegment', optional=True),
                            OneOf(
                                Ref('LikeKeywordSegment'),
                                Ref('RLikeKeywordSegment'),
                                Ref('ILikeKeywordSegment')
                            )
                        )
                        # We need to add a lot more here...
                    ),
                    Ref('Expression_A_Grammar')
                ),
                Sequence(
                    Ref('NotKeywordSegment', optional=True),
                    Ref('InKeywordSegment'),
                    Bracketed(
                        OneOf(
                            Delimited(
                                Ref('LiteralGrammar'),
                                delimiter=Ref('CommaSegment')
                            ),
                            Ref('SelectStatementSegment')
                        )
                    )
                ),
                Sequence(
                    Ref('IsKeywordSegment'),
                    Ref('NotKeywordSegment', optional=True),
                    OneOf(
                        Ref('NullKeywordSegment'),
                        Ref('NanKeywordSegment'),
                        # TODO: True and False might not be allowed here in some
                        # dialects (e.g. snowflake) so we should probably
                        # revisit this at some point. Perhaps abstract this clause
                        # into an "is-statement grammar", which could be overridden.
                        Ref('BooleanLiteralGrammar')
                    )
                ),
                Sequence(
                    Ref('NotKeywordSegment', optional=True),
                    Ref('BetweenKeywordSegment'),
                    Ref('Expression_C_Grammar'),
                    Ref('AndKeywordSegment'),
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
            Ref('ExistsKeywordSegment'),
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
            Ref('ObjectReferenceSegment')
        ),
        AnyNumberOf(
            Ref('ArrayAccessorSegment')
        ),
        Ref('ShorthandCastSegment', optional=True),
        code_only=False
    ),
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
        Ref('AsKeywordSegment'),
        Ref('AscKeywordSegment'),
        Ref('DescKeywordSegment'),
        Ref('InnerKeywordSegment'),
        Ref('LeftKeywordSegment'),
        Ref('CrossKeywordSegment'),
        Ref('JoinKeywordSegment'),
        Ref('WhereKeywordSegment'),
        Ref('GroupKeywordSegment'),
        Ref('OrderKeywordSegment'),
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
        Ref('WhenKeywordSegment'),
        Ref('ElseKeywordSegment'),
        Ref('EndKeywordSegment')
    )


@ansi_dialect.segment()
class ExpressionSegment_TermThen(ExpressionSegment):
    """Expression terminated by THEN."""
    match_grammar = GreedyUntil(Ref('ThenKeywordSegment'))


@ansi_dialect.segment()
class ExpressionSegment_TermEnd(ExpressionSegment):
    """Expression terminated by END."""
    match_grammar = GreedyUntil(Ref('EndKeywordSegment'))


@ansi_dialect.segment()
class WhereClauseSegment(BaseSegment):
    """A `WHERE` clause like in `SELECT` or `INSERT`."""
    type = 'where_clause'
    match_grammar = StartsWith(
        Ref('WhereKeywordSegment'),
        terminator=OneOf(
            Ref('LimitKeywordSegment'),
            Ref('GroupKeywordSegment'),
            Ref('OrderKeywordSegment'),
            Ref('HavingKeywordSegment')
        )
    )
    parse_grammar = Sequence(
        Ref('WhereKeywordSegment'),
        Indent,
        Ref('ExpressionSegment'),
        Dedent
    )


@ansi_dialect.segment()
class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`."""
    type = 'orderby_clause'
    match_grammar = StartsWith(
        Ref('OrderKeywordSegment'),
        terminator=OneOf(
            Ref('LimitKeywordSegment'),
            Ref('HavingKeywordSegment'),
            # For window functions
            Ref('RowsKeywordSegment')
        )
    )
    parse_grammar = Sequence(
        Ref('OrderKeywordSegment'),
        Ref('ByKeywordSegment'),
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
                    Ref('AscKeywordSegment'),
                    Ref('DescKeywordSegment'),
                    optional=True
                ),
            ),
            delimiter=Ref('CommaSegment'),
            terminator=Ref('LimitKeywordSegment')
        ),
        Dedent
    )


@ansi_dialect.segment()
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""
    type = 'groupby_clause'
    match_grammar = StartsWith(
        Sequence(
            Ref('GroupKeywordSegment'),
            Ref('ByKeywordSegment')
        ),
        terminator=OneOf(
            Ref('OrderKeywordSegment'),
            Ref('LimitKeywordSegment'),
            Ref('HavingKeywordSegment')
        )
    )
    parse_grammar = Sequence(
        Ref('GroupKeywordSegment'),
        Ref('ByKeywordSegment'),
        Indent,
        Delimited(
            OneOf(
                Ref('ObjectReferenceSegment'),
                # Can `GROUP BY 1`
                Ref('NumericLiteralSegment')
            ),
            delimiter=Ref('CommaSegment'),
            terminator=OneOf(
                Ref('OrderKeywordSegment'),
                Ref('LimitKeywordSegment'),
                Ref('HavingKeywordSegment')
            )
        ),
        Dedent
    )


@ansi_dialect.segment()
class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`."""
    type = 'having_clause'
    match_grammar = StartsWith(
        Ref('HavingKeywordSegment'),
        terminator=OneOf(
            Ref('OrderKeywordSegment'),
            Ref('LimitKeywordSegment')
        )
    )
    parse_grammar = Sequence(
        Ref('HavingKeywordSegment'),
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
        Ref('LimitKeywordSegment'),
        Ref('NumericLiteralSegment')
    )


@ansi_dialect.segment()
class ValuesClauseSegment(BaseSegment):
    """A `VALUES` clause like in `INSERT`."""
    type = 'values_clause'
    match_grammar = Sequence(
        OneOf(
            Ref('ValueKeywordSegment'),
            Ref('ValuesKeywordSegment')
        ),
        Delimited(
            Bracketed(
                Delimited(
                    Ref('LiteralGrammar'),
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
    match_grammar = StartsWith(Ref('SelectKeywordSegment'))
    parse_grammar = Sequence(
        Ref('SelectClauseSegment'),
        Ref('FromClauseSegment', optional=True),
        Ref('WhereClauseSegment', optional=True),
        Ref('GroupByClauseSegment', optional=True),
        Ref('HavingClauseSegment', optional=True),
        Ref('OrderByClauseSegment', optional=True),
        Ref('LimitClauseSegment', optional=True)
        # GreedyUntil(KeywordSegment.make('limit'), optional=True)
    )


@ansi_dialect.segment()
class WithCompoundStatementSegment(BaseSegment):
    """A `SELECT` statement preceeded by a selection of `WITH` clauses."""
    type = 'with_compound_statement'
    # match grammar
    match_grammar = StartsWith(Ref('WithKeywordSegment'))
    parse_grammar = Sequence(
        Ref('WithKeywordSegment'),
        Delimited(
            Sequence(
                Ref('ObjectReferenceSegment'),
                Ref('AsKeywordSegment'),
                Bracketed(
                    OneOf(
                        Ref('SetExpressionSegment'),
                        Ref('SelectStatementSegment')
                    )
                )
            ),
            delimiter=Ref('CommaSegment'),
            terminator=Ref('SelectKeywordSegment')
        ),
        Ref('SelectStatementSegment')
    )


@ansi_dialect.segment()
class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Minus, Exept or Intersect."""
    type = 'set_operator'
    match_grammar = OneOf(
        Sequence(
            Ref('UnionKeywordSegment'),
            OneOf(
                Ref('DistinctKeywordSegment'),
                Ref('AllKeywordSegment'),
                optional=True
            )
        ),
        Ref('IntersectKeywordSegment'),
        Ref('ExceptKeywordSegment'),
        Ref('MinusKeywordSegment')
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
    match_grammar = StartsWith(Ref('InsertKeywordSegment'))
    parse_grammar = Sequence(
        Ref('InsertKeywordSegment'),
        Ref('OverwriteKeywordSegment', optional=True),  # Maybe this is just snowflake?
        Ref('IntoKeywordSegment', optional=True),
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
            Ref('CommitKeywordSegment'),
            Ref('WorkKeywordSegment', optional=True),
            Sequence(
                Ref('AndKeywordSegment'),
                Ref('NoKeywordSegment', optional=True),
                Ref('ChainKeywordSegment'),
                optional=True
            )
        ),
        # NOTE: "TO SAVEPOINT" is not yet supported
        # ROLLBACK [ WORK ] [ AND [ NO ] CHAIN ]
        Sequence(
            Ref('RollbackKeywordSegment'),
            Ref('WorkKeywordSegment', optional=True),
            Sequence(
                Ref('AndKeywordSegment'),
                Ref('NoKeywordSegment', optional=True),
                Ref('ChainKeywordSegment'),
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
            Ref('ConstraintKeywordSegment'),
            Ref('ObjectReferenceSegment'),  # Constraint name
            optional=True
        ),
        OneOf(
            Sequence(  # NOT NULL or NULL
                Ref('NotKeywordSegment', optional=True),
                Ref('NullKeywordSegment')
            ),
            Sequence(  # DEFAULT <value>
                Ref('DefaultKeywordSegment'),
                Ref('LiteralGrammar'),
            ),
            Sequence(  # PRIMARY KEY
                Ref('PrimaryKeywordSegment'),
                Ref('KeyKeywordSegment'),
            ),
            Ref('UniqueKeywordSegment'),  # UNIQUE
            Ref('AutoIncrementKeywordSegment'),  # AUTO_INCREMENT (MySQL)
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                Ref('ReferencesKeywordSegment'),
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
                Ref('CommentKeywordSegment'),
                Ref('QuotedLiteralSegment'),
            ),
        ),
    )


@ansi_dialect.segment()
class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""
    type = 'column_definition'
    match_grammar = Sequence(
        Ref('ObjectReferenceSegment'),  # Column name
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
            Ref('ConstraintKeywordSegment'),
            Ref('ObjectReferenceSegment'),
            optional=True
        ),
        OneOf(
            Sequence(  # UNIQUE ( column_name [, ... ] )
                Ref('UniqueKeywordSegment'),
                Bracketed(  # Columns making up UNIQUE constraint
                    Delimited(
                        Ref('ObjectReferenceSegment'),
                        delimiter=Ref('CommaSegment')
                    ),
                ),
                # Later add support for index_parameters?
            ),
            Sequence(  # PRIMARY KEY ( column_name [, ... ] ) index_parameters
                Ref('PrimaryKeywordSegment'),
                Ref('KeyKeywordSegment'),
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
                Ref('ForeignKeywordSegment'),
                Ref('KeyKeywordSegment'),
                Bracketed(  # Local columns making up FOREIGN KEY constraint
                    Delimited(
                        Ref('ObjectReferenceSegment'),
                        delimiter=Ref('CommaSegment')
                    ),
                ),
                Ref('ReferencesKeywordSegment'),
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
        Ref('CreateKeywordSegment'),
        Ref('TableKeywordSegment'),
        Sequence(
            Ref('IfKeywordSegment'),
            Ref('NotKeywordSegment'),
            Ref('ExistsKeywordSegment'),
            optional=True
        ),
        Ref('ObjectReferenceSegment'),
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
            Ref('CommentKeywordSegment'),
            Ref('QuotedLiteralSegment'),
            optional=True
        ),
    )


@ansi_dialect.segment()
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement."""
    type = 'create_view_statement'
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html#create-view-statement
    # https://dev.mysql.com/doc/refman/8.0/en/create-view.html
    # https://www.postgresql.org/docs/12/sql-createview.html
    match_grammar = Sequence(
        Ref('CreateKeywordSegment'),
        Sequence(
            Ref('OrKeywordSegment'),
            Ref('ReplaceKeywordSegment'),
            optional=True
        ),
        Ref('ViewKeywordSegment'),
        Ref('ObjectReferenceSegment'),
        Bracketed(  # Optional list of column names
            Delimited(
                Ref('ObjectReferenceSegment'),
                delimiter=Ref('CommaSegment')
            ),
            optional=True
        ),
        Ref('AsKeywordSegment'),
        Ref('SelectStatementSegment'),
    )


@ansi_dialect.segment()
class DropStatementSegment(BaseSegment):
    """A `DROP` statement."""
    type = 'drop_statement'
    # DROP {TABLE | VIEW} <Table name> [IF EXISTS} {RESTRICT | CASCADE}
    match_grammar = Sequence(
        Ref('DropKeywordSegment'),
        OneOf(
            Ref('TableKeywordSegment'),
            Ref('ViewKeywordSegment'),
        ),
        Sequence(
            Ref('IfKeywordSegment'),
            Ref('ExistsKeywordSegment'),
            optional=True
        ),
        Ref('ObjectReferenceSegment'),
        OneOf(
            Ref('RestrictKeywordSegment'),
            Ref('CascadeKeywordSegment', optional=True),
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
            Ref('GrantKeywordSegment'),
            Delimited(  # List of permission types
                Sequence(
                    OneOf(  # Permission type
                        Sequence(
                            Ref('AllKeywordSegment'),
                            Ref('PrivilegesKeywordSegment', optional=True)
                        ),
                        Ref('SelectKeywordSegment'),
                        Ref('UpdateKeywordSegment'),
                        Ref('InsertKeywordSegment'),
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
            Ref('OnKeywordSegment'),
            OneOf(
                Sequence(
                    Ref('TableKeywordSegment', optional=True),
                    Ref('ObjectReferenceSegment'),
                ),
                Sequence(
                    Ref('AllKeywordSegment'),
                    Ref('TablesKeywordSegment'),
                    Ref('InKeywordSegment'),
                    Ref('SchemaKeywordSegment'),
                    Ref('ObjectReferenceSegment'),
                )
            ),
            Ref('ToKeywordSegment'),
            OneOf(
                Ref('GroupKeywordSegment'),
                Ref('UserKeywordSegment'),
                Ref('RoleKeywordSegment'),
                optional=True
            ),
            Ref('ObjectReferenceSegment'),
            Sequence(
                Ref('WithKeywordSegment'),
                Ref('GrantKeywordSegment'),
                Ref('OptionKeywordSegment'),
                optional=True
            ),
        ),
        # Based on https://www.postgresql.org/docs/12/sql-revoke.html
        Sequence(
            Ref('RevokeKeywordSegment'),
            Delimited(  # List of permission types
                Sequence(
                    Sequence(
                        Ref('GrantKeywordSegment'),
                        Ref('OptionKeywordSegment'),
                        Ref('ForKeywordSegment'),
                        optional=True
                    ),
                    OneOf(  # Permission type
                        Sequence(
                            Ref('AllKeywordSegment'),
                            Ref('PrivilegesKeywordSegment', optional=True)
                        ),
                        Ref('SelectKeywordSegment'),
                        Ref('UpdateKeywordSegment'),
                        Ref('InsertKeywordSegment'),
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
            Ref('OnKeywordSegment'),
            OneOf(
                Sequence(
                    Ref('TableKeywordSegment', optional=True),
                    Ref('ObjectReferenceSegment'),
                ),
                Sequence(
                    Ref('AllKeywordSegment'),
                    Ref('TablesKeywordSegment'),
                    Ref('InKeywordSegment'),
                    Ref('SchemaKeywordSegment'),
                    Ref('ObjectReferenceSegment'),
                )
            ),
            Ref('FromKeywordSegment'),
            OneOf(
                Ref('GroupKeywordSegment'),
                Ref('UserKeywordSegment'),
                Ref('RoleKeywordSegment'),
                optional=True
            ),
            Ref('ObjectReferenceSegment'),
            OneOf(
                Ref('RestrictKeywordSegment'),
                Ref('CascadeKeywordSegment', optional=True),
                optional=True
            )
        ),
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
    )
    match_grammar = GreedyUntil(Ref('SemicolonSegment'))
