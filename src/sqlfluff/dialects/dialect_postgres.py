"""The PostgreSQL dialect."""

from ..parser import (OneOf, Ref, Sequence, Bracketed, Anything, BaseSegment, NamedSegment, Delimited, AnyNumberOf)

from .dialect_ansi import ansi_dialect

# At the moment this is just a placeholder. Unique syntax to be added later.
postgres_dialect = ansi_dialect.copy_as('postgres')


postgres_dialect.insert_lexer_struct(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [("json_operator", "regex", r"->>|#>>|->|#>|@>|<@|\?\||\?|\?&|#-", dict(is_code=True))],
    before='not_equal'
)


# Reserve WITHIN (required for the WithinGroupClauseSegment)
postgres_dialect.sets('unreserved_keywords').remove('WITHIN')
postgres_dialect.sets('reserved_keywords').add('WITHIN')


postgres_dialect.add(
    JsonOperatorSegment=NamedSegment.make('json_operator', name='json_operator', type='binary_operator'),
)


postgres_dialect.replace(
    PostFunctionGrammar=OneOf(
        Ref('OverClauseSegment'),
        Ref('WithinGroupClauseSegment')
    ),
    BinaryOperatorGramar=OneOf(
        Ref('ArithmeticBinaryOperatorGrammar'),
        Ref('StringBinaryOperatorGrammar'),
        Ref('BooleanBinaryOperatorGrammar'),
        Ref('ComparisonOperatorGrammar'),
        # Add JSON operators
        Ref('JsonOperatorSegment')
    ),
    # This is a hook point to allow subclassing for other dialects.
    # In the ANSI dialect this is designed to be a basic starting point.
    FunctionDefinitionGrammar=Sequence(
        AnyNumberOf(
            Sequence(
                'LANGUAGE',
                # Not really a parameter, but best fit for now.
                Ref('ParameterNameSegment')
            ),
            'WINDOW',
            'IMMUTABLE',
            'STABLE',
            'VOLATILE',
            'STRICT',
            Sequence('CALLED', 'ON', 'INPUT'),
            Sequence('RETURNS', 'NULL', 'ON', 'NULL', 'INPUT'),
            Sequence(
                Ref.keyword('EXTERNAL', optional=True),
                'SECURITY',
                OneOf('INVOKER', 'DEFINER')
            ),
            # There is some syntax not implemented here,
            Sequence(
                'AS',
                Ref('QuotedLiteralSegment')
            )
        )
    )
)


@postgres_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""
    type = 'select_clause_modifier'
    match_grammar = OneOf(
        Sequence(
            'DISTINCT',
            Sequence(
                'ON',
                Bracketed(Anything()),
                optional=True
            )
        ),
        'ALL',
    )

    parse_grammar = OneOf(
        Sequence(
            'DISTINCT',
            Sequence(
                'ON',
                Bracketed(
                    Delimited(
                        Ref('ExpressionSegment'),
                        delimiter=Ref('CommaSegment')
                    )
                ),
                optional=True
            )
        ),
        'ALL',
    )


@postgres_dialect.segment()
class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions.

    https://www.postgresql.org/docs/current/functions-aggregate.html.
    """
    type = 'withingroup_clause'
    match_grammar = Sequence(
        'WITHIN', 'GROUP',
        Bracketed(
            Anything(optional=True)
        ),
    )

    parse_grammar = Sequence(
        'WITHIN', 'GROUP',
        Bracketed(
            Ref('OrderByClauseSegment', optional=True)
        ),
    )
