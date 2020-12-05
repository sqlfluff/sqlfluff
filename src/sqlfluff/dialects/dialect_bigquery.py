"""The BigQuery dialect.

This inherits from the ansi dialect, with changes as specified by
https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
and
https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
"""

from ..parser import (BaseSegment, NamedSegment, OneOf, Ref, Sequence, Bracketed, Delimited, AnyNumberOf, GreedyUntil, StartsWith, Indent, Dedent)

from .dialect_ansi import ansi_dialect


bigquery_dialect = ansi_dialect.copy_as('bigquery')

bigquery_dialect.patch_lexer_struct([
    # Quoted literals can have r or b (case insensitive) prefixes, in any order, to
    # indicate a raw/regex string or byte sequence, respectively.  Allow escaped quote
    # characters inside strings by allowing \" with an optional even multiple of
    # backslashes in front of it.
    # https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals

    # Triple quoted variant first, then single quoted
    ("single_quote", "regex", r"([rR]?[bB]?|[bB]?[rR]?)?('''((?<!\\)(\\{2})*\\'|'{,2}(?!')|[^'])*(?<!\\)(\\{2})*'''|'((?<!\\)(\\{2})*\\'|[^'])*(?<!\\)(\\{2})*')", dict(is_code=True)),
    ("double_quote", "regex", r'([rR]?[bB]?|[bB]?[rR]?)?(\"\"\"((?<!\\)(\\{2})*\\\"|\"{,2}(?!\")|[^\"])*(?<!\\)(\\{2})*\"\"\"|"((?<!\\)(\\{2})*\\"|[^"])*(?<!\\)(\\{2})*")', dict(is_code=True))
])

bigquery_dialect.add(
    DoubleQuotedLiteralSegment=NamedSegment.make('double_quote', name='quoted_literal', type='literal', trim_chars=('"',))
)

# Add the microsecond unit
bigquery_dialect.sets('datetime_units').add('MICROSECOND')
# Add the ISO date parts
bigquery_dialect.sets('datetime_units').update(['ISOWEEK', 'ISOYEAR'])

# Unreserved Keywords
bigquery_dialect.sets('unreserved_keywords').add('SYSTEM_TIME')
bigquery_dialect.sets('unreserved_keywords').remove('FOR')
# Reserved Keywords
bigquery_dialect.sets('reserved_keywords').add('FOR')


# BigQuery allows functions in INTERVAL
class IntervalExpressionSegment(BaseSegment):
    """An interval with a function as value segment."""
    type = 'interval_expression'
    match_grammar = Sequence(
        'INTERVAL',
        OneOf(
            Ref('NumericLiteralSegment'),
            Ref('FunctionSegment')
        ),
        OneOf(
            Ref('QuotedLiteralSegment'),
            Ref('DatetimeUnitSegment')
        )
    )


@bigquery_dialect.segment()
class ExceptSegment(BaseSegment):
    """select * except(some_column).

    https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#select_replace
    """
    type = 'except'
    match_grammar = Sequence(
        'EXCEPT',
        Bracketed(
            Delimited(
                Ref('SingleIdentifierGrammar'),
                delimiter=Ref('CommaSegment')
            )
        ),
    )


@bigquery_dialect.segment()
class ReplaceSegment(BaseSegment):
    type = "replace"

    match_grammar = Sequence(
        'REPLACE',
        OneOf(
            # Multiple replace in brackets
            Bracketed(
                Delimited(
                    # Not *really* a select target element. It behaves exactly
                    # the same way however.
                    Ref('SelectTargetElementSegment'),
                    delimiter=Ref('CommaSegment')
                )
            ),
            # Single replace not in brackets.
            Ref('SelectTargetElementSegment')
        ),
        optional=True
    )


class WildcardSelectTargetElementGrammar(BaseSegment):
    match_grammar = Sequence(
        AnyNumberOf(
            Sequence(
                Ref('SingleIdentifierGrammar'),
                Ref('DotSegment'),
                code_only=True
            ),
            Ref('StarSegment'),
            Ref('ExceptSegment', optional=True),
            Ref('ReplaceSegment', optional=True),
        ),
        code_only=False
    )


bigquery_dialect.replace(
    QuotedIdentifierSegment=NamedSegment.make('back_quote', name='quoted_identifier', type='identifier', trim_chars=('`',)),
    IntervalExpressionSegment=IntervalExpressionSegment,
    LiteralGrammar=OneOf(
        Ref('QuotedLiteralSegment'), Ref('DoubleQuotedLiteralSegment'), Ref('NumericLiteralSegment'),
        Ref('BooleanLiteralGrammar'), Ref('QualifiedNumericLiteralSegment'), Ref('NullKeywordSegment')
    ),
    PostTableExpressionGrammar=Sequence(
        Sequence(
            'FOR', 'SYSTEM_TIME', 'AS', 'OF',
            Ref('ExpressionSegment'),
            optional=True
        ),
        Sequence(
            'WITH',
            'OFFSET',
            'AS',
            Ref('SingleIdentifierGrammar'),
            optional=True
        )
    ),
    WildcardSelectTargetElementGrammar=WildcardSelectTargetElementGrammar,
)
