"""The PostgreSQL dialect."""

from ..parser import (OneOf, Ref, Sequence, Bracketed, Anything, BaseSegment,
                      NamedSegment, Delimited, AnyNumberOf, KeywordSegment)

from .dialect_ansi import ansi_dialect

# At the moment this is just a placeholder. Unique syntax to be added later.
postgres_dialect = ansi_dialect.copy_as('postgres')


postgres_dialect.insert_lexer_struct(
    [
        # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
        ("json_operator", "regex", r"->>|#>>|->|#>|@>|<@|\?\||\?|\?&|#-", dict(is_code=True)),
        # The double $$ delimiter for plsql definitions.
        ("plsql_delimiter", "regex", r"\$\$", dict(is_code=True))
    ],
    before='not_equal'
)


# Reserve WITHIN (required for the WithinGroupClauseSegment)
postgres_dialect.sets('unreserved_keywords').remove('WITHIN')
postgres_dialect.sets('reserved_keywords').add('WITHIN')

# Bracket pairs (a set of tuples)
postgres_dialect.sets('bracket_pairs').update([
    # It's important that this is here as it can contain a semicolon.
    # We don't import angle brackets here because they can't contain
    # semicolons.
    ('postgres_$$', 'plSQLDelimiterSegment', 'plSQLDelimiterSegment', True)
])


postgres_dialect.add(
    JsonOperatorSegment=NamedSegment.make('json_operator', name='json_operator', type='binary_operator'),
    # We use the keyword segment here for performance reasons. It has a shortcut but Named Segment does not (or not yet anyway).
    plSQLDelimiterSegment=KeywordSegment.make('$$', name='plsql_delimiter', type='code_section_delimiter'),
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
                OneOf(
                    Ref('QuotedLiteralSegment'),
                    Ref('FunctionSQLCodeSegment')
                )
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


@postgres_dialect.segment()
class FunctionSQLCodeSegment(BaseSegment):
    """A SQL code segment delimited by $$."""
    type = 'function_code'
    match_grammar = Bracketed(
        Anything(optional=True),
        bracket_type='postgres_$$'
    )
