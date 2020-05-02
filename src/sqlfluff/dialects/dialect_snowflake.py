"""The Snowflake dialect.

Inherits from Postgres.

Based on https://docs.snowflake.com/en/sql-reference-commands.html
"""

from .dialect_postgres import postgres_dialect
from ..parser import (BaseSegment, NamedSegment, OneOf, Ref, Sequence, AnyNumberOf, ReSegment, KeywordSegment)


snowflake_dialect = postgres_dialect.copy_as('snowflake')


snowflake_dialect.insert_lexer_struct(
    # Keyword assigner needed for keyword functions.
    [("keyword_assigner", "regex", r"=>", dict(is_code=True))],
    before='not_equal'
)


snowflake_dialect.add(
    # In snowflake, these are case sensitive even though they're not quoted
    # so they need a different `name` and `type` so they're not picked up
    # by other rules.
    LateralKeywordSegment=KeywordSegment.make('lateral'),
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
            Ref('ObjectReferenceSegment')
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
                Ref('DotSegment'),
                OneOf(
                    Ref('NakedSemiStructuredElementSegment'),
                    Ref('QuotedSemiStructuredElementSegment')
                ),
                Ref('ArrayAccessorSegment', optional=True)
            )
        ),
        # No extra whitespace
        code_only=False
    )
