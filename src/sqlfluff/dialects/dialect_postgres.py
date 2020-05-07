"""The PostgreSQL dialect."""

from ..parser import (OneOf, Ref, Sequence, Bracketed, Anything, BaseSegment)

from .dialect_ansi import ansi_dialect

# At the moment this is just a placeholder. Unique syntax to be added later.
postgres_dialect = ansi_dialect.copy_as('postgres')

postgres_dialect.replace(
    PostFunctionGrammar=OneOf(
        Ref('OverClauseSegment'),
        Ref('WithinGroupClauseSegment')
    )
)


# Reserve WITHIN (required for the WithinGroupClauseSegment)
postgres_dialect.sets('unreserved_keywords').remove('WITHIN')
postgres_dialect.sets('reserved_keywords').add('WITHIN')


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
            Sequence(
                Ref('OrderByClauseSegment', optional=True)
            )
        ),
    )
