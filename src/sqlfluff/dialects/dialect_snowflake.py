"""The Snowflake dialect.

Inherits from Postgres.

Based on https://docs.snowflake.com/en/sql-reference-commands.html
"""

from .dialect_postgres import postgres_dialect
from ..parser import (BaseSegment, NamedSegment, OneOf, Ref, Sequence,
                      AnyNumberOf, ReSegment, KeywordSegment, Bracketed,
                      Anything)


snowflake_dialect = postgres_dialect.copy_as('snowflake')

snowflake_dialect.patch_lexer_struct([
    # In snowflake, a double single quote resolves as a single quote in the string.
    # https://docs.snowflake.com/en/sql-reference/data-types-text.html#single-quoted-string-constants
    ("single_quote", "regex", r"'([^']|'')*'", dict(is_code=True)),
])

snowflake_dialect.insert_lexer_struct(
    # Keyword assigner needed for keyword functions.
    [("keyword_assigner", "regex", r"=>", dict(is_code=True))],
    before='not_equal'
)

snowflake_dialect.sets('unreserved_keywords').update([
    'LATERAL'
])


snowflake_dialect.add(
    # In snowflake, these are case sensitive even though they're not quoted
    # so they need a different `name` and `type` so they're not picked up
    # by other rules.
    KeywordAssignerSegment=KeywordSegment.make('=>', name="keyword_assigner"),
    KeywordNameSegment=ReSegment.make(
        r"[A-Z][A-Z0-9_]*", name='keyword_name',
        type='keyword_name'),
    NakedSemiStructuredElementSegment=ReSegment.make(
        r"[A-Z][A-Z0-9_]*", name='naked_semi_structured_element',
        type='semi_structured_element'),
    QuotedSemiStructuredElementSegment=NamedSegment.make(
        'double_quote', name='quoted_semi_structured_element',
        type='semi_structured_element'),
)

snowflake_dialect.replace(
    Accessor_Grammar=AnyNumberOf(
        # Snowflake doesn't support arrays, so they come out.
        # Ref('ArrayAccessorSegment')
        # Add in semi structured expressions
        Ref('SemiStructuredAccessorSegment')
    ),
    PreTableFunctionKeywordsGrammar=OneOf(
        Ref('LateralKeywordSegment')
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref('KeywordExpressionSegment'),
        Ref('ExpressionSegment')
    ),
    PostTableExpressionGrammar=Ref('SamplingExpressionSegment'),
    JoinLikeClauseGrammar=OneOf(
        Ref('FromAtExpressionSegment'),
        Ref('FromBeforeExpressionSegment'),
        Ref('FromPivotExpressionSegment'),
        Ref('FromUnpivotExpressionSegment')
    )
)


@snowflake_dialect.segment()
class FromAtExpressionSegment(BaseSegment):
    """An AT expression."""
    type = 'from_at_expression'
    match_grammar = Sequence(
        'AT',
        Bracketed(
            Anything()
        )
    )

    parse_grammar = Sequence(
        'AT',
        Bracketed(
            OneOf('TIMESTAMP', 'OFFSET', 'STATEMENT'),
            Ref('KeywordAssignerSegment'),
            Ref('ExpressionSegment')
        )
    )


@snowflake_dialect.segment()
class FromBeforeExpressionSegment(BaseSegment):
    """A BEFORE expression."""
    type = 'from_before_expression'
    match_grammar = Sequence(
        'BEFORE',
        Bracketed(
            Anything()
        )
    )

    parse_grammar = Sequence(
        'BEFORE',
        Bracketed(
            'STATEMENT',
            Ref('KeywordAssignerSegment'),
            Ref('StringLiteral')
        )
    )


@snowflake_dialect.segment()
class FromPivotExpressionSegment(BaseSegment):
    """A PIVOT expression."""
    type = 'from_pivot_expression'
    match_grammar = Sequence(
        'PIVOT',
        Bracketed(
            Anything()
        )
    )

    parse_grammar = Sequence(
        'PIVOT',
        Bracketed(
            Ref('FunctionNameSegment'),
            Bracketed(
                Ref('SingleIdentifierGrammar'),
            ),
            'FOR',
            Ref('SingleIdentifierGrammar'),
            'IN',
            Bracketed(
                Delimited(
                    Ref('SingleIdentifierGrammar'),
                    delimiter=Ref('CommaSegment')
                )
            )
        )
    )


@snowflake_dialect.segment()
class FromUnpivotExpressionSegment(BaseSegment):
    """An UNPIVOT expression."""
    type = 'from_unpivot_expression'
    match_grammar = Sequence(
        'UNPIVOT',
        Bracketed(
            Anything()
        )
    )

    parse_grammar = Sequence(
        'UNPIVOT',
        Bracketed(
            Ref('SingleIdentifierGrammar'),
            'FOR',
            Ref('SingleIdentifierGrammar'),
            'IN',
            Bracketed(
                Delimited(
                    Ref('SingleIdentifierGrammar'),
                    delimiter=Ref('CommaSegment')
                )
            )
        )
    )


@snowflake_dialect.segment()
class SamplingExpressionSegment(BaseSegment):
    """A sampling expression."""
    type = 'snowflake_sample_expression'
    match_grammar = Sequence(
        OneOf('SAMPLE', 'TABLESAMPLE'),
        OneOf('BERNOILLI', 'ROW', 'SYSTEM', 'BLOCK', optional=True),
        Bracketed(
            Ref('NumericLiteralSegment'),
            Ref.keyword('ROWS', optional=True)
        ),
        Sequence(
            OneOf('REPEATABLE', 'SEED'),
            Bracketed(
                Ref('NumericLiteralSegment')
            )
        )
    )


@snowflake_dialect.segment()
class KeywordExpressionSegment(BaseSegment):
    """A keyword expression.

    e.g. 'input => custom_fields'

    """
    type = 'snowflake_keyword_expression'
    match_grammar = Sequence(
        Ref('KeywordNameSegment'),
        Ref('KeywordAssignerSegment'),
        OneOf(
            Ref('LiteralGrammar'),
            Ref('ObjectReferenceSegment'),
            Ref('ExpressionSegment')
        )
    )


@snowflake_dialect.segment()
class SemiStructuredAccessorSegment(BaseSegment):
    """A semi-structured data accessor segment.

    https://docs.snowflake.com/en/user-guide/semistructured-considerations.html
    """
    type = 'snowflake_semi_structured_expression'
    match_grammar = Sequence(
        Ref('ColonSegment'),
        OneOf(
            Ref('NakedSemiStructuredElementSegment'),
            Ref('QuotedSemiStructuredElementSegment')
        ),
        Ref('ArrayAccessorSegment', optional=True),
        AnyNumberOf(
            Sequence(
                OneOf(
                    # Can be delimited by dots or colons
                    Ref('DotSegment'),
                    Ref('ColonSegment'),
                ),
                OneOf(
                    Ref('NakedSemiStructuredElementSegment'),
                    Ref('QuotedSemiStructuredElementSegment')
                ),
                Ref('ArrayAccessorSegment', optional=True),
                # No extra whitespace
                code_only=False
            ),
            # No extra whitespace
            code_only=False
        ),
        # No extra whitespace
        code_only=False
    )
