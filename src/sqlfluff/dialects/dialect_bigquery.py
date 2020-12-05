"""The BigQuery dialect.

This inherits from the ansi dialect, with changes as specified by
https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
and
https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
"""

from ..parser import (BaseSegment, ReSegment, NamedSegment, OneOf, Ref, Sequence, Bracketed, Delimited, AnyNumberOf, GreedyUntil, StartsWith, Indent, Dedent, KeywordSegment, Not, Anything)

from .dialect_ansi import (
    ansi_dialect,
    SelectTargetElementSegment as AnsiSelectTargetElementSegment,
)


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
    DoubleQuotedLiteralSegment=NamedSegment.make('double_quote', name='quoted_literal', type='literal', trim_chars=('"',)),
    StructKeywordSegment=KeywordSegment.make('struct', name="struct"),
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


@bigquery_dialect.segment()
class StarModifierSegment(BaseSegment):
    match_grammar = Sequence(
        Ref('ExceptSegment', optional=True),
        Ref('ReplaceSegment', optional=True),
    )

class WildcardSelectTargetElementGrammar(BaseSegment):
    match_grammar = Sequence(
        Sequence(
            Sequence(
                Ref('SingleIdentifierGrammar'),
                Ref('DotSegment'),
                optional=True,
            ),
            Ref('StarSegment')
        ),
        Ref('StarModifierSegment', optional=True),
        code_only=True
    )


@bigquery_dialect.segment()
class StructSegment(BaseSegment):
    """Bigquery struct."""
    type = 'struct'
    match_grammar = Sequence(
        'STRUCT',
        Bracketed(
            Delimited(
                AnyNumberOf(
                    Sequence(
                        OneOf(
                            Ref('LiteralGrammar'),
                            Ref('FunctionSegment'),
                            Ref('IntervalExpressionSegment'),
                            Ref('ObjectReferenceSegment'),
                            Ref('ExpressionSegment')
                        ),
                        Ref('AliasExpressionSegment', optional=True)
                    ),
                ),
                delimiter=Ref('CommaSegment'),
            ),
            optional=True
        )
    )


class SelectTargetElementSegment(AnsiSelectTargetElementSegment):
    """An element in the targets of a select statement."""
    parse_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref('WildcardSelectTargetElementGrammar'),
        Sequence(
            OneOf(
                Ref('LiteralGrammar'),
                Ref('StructSegment'),
                Ref('FunctionSegment'),
                Ref('IntervalExpressionSegment'),
                Ref('ObjectReferenceSegment'),
                Ref('ExpressionSegment'),
            ),
            Ref('AliasExpressionSegment', optional=True)
        ),
    )


class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement."""
    type = 'select_clause'
    match_grammar = StartsWith(
        'SELECT',
        terminator=OneOf('FROM', 'LIMIT')
    )

    parse_grammar = Sequence(
        'SELECT',
        Ref('SelectClauseModifierSegment', optional=True),
        Indent,
        OneOf(
            Sequence(
                'AS',
                'STRUCT',
                Ref('StarSegment'),
                Ref('StarModifierSegment', optional=True),
            ),
            Delimited(
                Ref('SelectTargetElementSegment'),
                delimiter=Ref('CommaSegment'),
                allow_trailing=True
            ),
        ),
        Dedent
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
    SelectClauseSegment=SelectClauseSegment,
    SelectTargetElementSegment=SelectTargetElementSegment,
    FunctionNameSegment=ReSegment.make(
        r"[A-Z][A-Z0-9_]*",
        # struct has a special syntax
        # so we deal with it in a
        # separate segment
        _anti_template=r"struct",
        name='function_name',
        type='function_name',
    ),
)
