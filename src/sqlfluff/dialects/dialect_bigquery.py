"""The BigQuery dialect.

This inherits from the ansi dialect, with changes as specified by
https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
and
https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
"""

from ..parser import (BaseSegment, NamedSegment, OneOf, Ref, Sequence, Bracketed,
                      Delimited, AnyNumberOf, Anything, KeywordSegment)

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
    DoubleQuotedLiteralSegment=NamedSegment.make('double_quote', name='quoted_literal', type='literal', trim_chars=('"',)),
    StartAngleBracketSegment=KeywordSegment.make('<', name='start_angle_bracket', type='start_angle_bracket'),
    EndAngleBracketSegment=KeywordSegment.make('>', name='end_angle_bracket', type='end_angle_bracket')
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

# Bracket pairs (a set of tuples)
bigquery_dialect.sets('bracket_pairs').update([
    ('angle', 'StartAngleBracketSegment', 'EndAngleBracketSegment')
])


# BigQuery allows functions in INTERVAL
@bigquery_dialect.segment(replace=True)
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


bigquery_dialect.replace(
    QuotedIdentifierSegment=NamedSegment.make('back_quote', name='quoted_identifier', type='identifier', trim_chars=('`',)),
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
    WildcardSelectTargetElementGrammar=Sequence(
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
        # Optional EXCEPT or REPLACE clause
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#select_replace
        Sequence(
            'EXCEPT',
            Bracketed(
                Delimited(
                    Ref('SingleIdentifierGrammar'),
                    delimiter=Ref('CommaSegment')
                )
            ),
            optional=True
        ),
        Sequence(
            'REPLACE',
            Bracketed(
                Delimited(
                    Ref('AliasedObjectReferenceSegment'),
                    delimiter=Ref('CommaSegment')
                )
            ),
            optional=True
        )
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
                    Ref('DoubleQuotedLiteralSegment'),
                    Ref('QuotedLiteralSegment'),
                    Bracketed(
                        OneOf(
                            Ref('ExpressionSegment'),
                            Ref('SelectStatementSegment')
                        )
                    )
                ),
            )
        )
    ),
    DialectSpecificStatementsGrammar=OneOf(
        Ref('CreateModelStatementSegment'), Ref('DropModelStatementSegment')
    ),
    DialectSpecificTableExpressionGrammar=Ref('MLTableExpressionSegment')
)


@bigquery_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment.

    In particular here, this enabled the support for
    the STRUCT datatypes.
    """
    type = 'data_type'
    match_grammar = Sequence(
        Ref('DatatypeIdentifierSegment'),
        OneOf(
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
            ),
            # Add STRUCT like HERE.
            # <integer> syntax
            Ref('BigqueryCompositeDatatypeSegment'),
            optional=True
        )
    )


@bigquery_dialect.segment()
class BigqueryCompositeDatatypeSegment(BaseSegment):
    """<integer, integer> syntax."""
    type = 'composite_datatype'
    match_grammar = Bracketed(
        Anything(),
        bracket_type='angle'
    )

    parse_grammar = Bracketed(
        Delimited(  # Comma-separated list of field names/types
            Sequence(
                Ref('ParameterNameSegment'),
                # NB: DatatypeSegment can be self referential back to this.
                Ref('DatatypeSegment')
            ),
            delimiter=Ref('CommaSegment')
        ),
        bracket_type='angle'
    )


@bigquery_dialect.segment()
class CreateModelStatementSegment(BaseSegment):
    """A BigQuery `CREATE MODEL` statement."""
    type = 'create_model_statement'
    # https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-create
    match_grammar = Sequence(
        'CREATE',
        Sequence(
            'OR',
            'REPLACE',
            optional=True
        ),
        'MODEL',
        Sequence(
            'IF',
            'NOT',
            'EXISTS',
            optional=True
        ),
        Ref('ObjectReferenceSegment'),
        Sequence(
            'OPTIONS',
            Bracketed(
                Delimited(
                    Sequence(
                        Ref('ParameterNameSegment'),
                        Ref('EqualsSegment'),
                        OneOf(
                            # This covers many but not all the extensive list of
                            # possible 'CREATE MODEL' optiona.
                            Ref('LiteralGrammar'),  # Single value
                            Bracketed(
                                # E.g. input_label_cols: list of column names
                                Delimited(
                                    Ref('QuotedLiteralSegment'),
                                    delimiter=Ref('CommaSegment')
                                ),
                                bracket_type='square',
                                optional=True
                            ),
                        )
                    ),
                    delimiter=Ref('CommaSegment')
                )
            ),
            optional=True
        ),
        'AS',
        Ref('SelectStatementSegment')
    )


@bigquery_dialect.segment()
class DropModelStatementSegment(BaseSegment):
    """A `DROP MODEL` statement."""
    type = 'drop_model_statement'
    # DROP MODEL <Model name> [IF EXISTS}
    # https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-drop-model
    match_grammar = Sequence(
        'DROP',
        'MODEL',
        Sequence(
            'IF',
            'EXISTS',
            optional=True
        ),
        Ref('ObjectReferenceSegment')
    )


@bigquery_dialect.segment()
class MLTableExpressionSegment(BaseSegment):
    """An ML table expression."""
    type = 'ml_table_expression'
    # E.g. ML.WEIGHTS(MODEL `project.dataset.model`)
    match_grammar = Sequence(
        'ML',
        Ref('DotSegment'),
        Ref('SingleIdentifierGrammar'),
        Bracketed(
            Sequence(
                'MODEL',
                Ref('ObjectReferenceSegment')
            ),
            OneOf(
                Sequence(
                    Ref('CommaSegment'),
                    Bracketed(
                        Ref('SelectStatementSegment')
                    )
                ),
                optional=True
            )
        )
    )
