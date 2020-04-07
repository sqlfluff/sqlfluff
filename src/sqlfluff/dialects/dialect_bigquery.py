"""The BigQuery dialect.

This inherits from the ansi dialect, with changes as specified by
https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
and
https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
"""

from ..parser import (NamedSegment, OneOf, Ref)

from .dialect_ansi import ansi_dialect


bigquery_dialect = ansi_dialect.copy_as('bigquery')

bigquery_dialect.patch_lexer_struct([
    # Quoted literals can have r or b (case insensitive) prefixes, in any order, to 
    # indicate a raw/regex string or byte sequence, respectively.  Allow escaped quote
    # characters inside strings by allowing \" with an optional even multiple of 
    # backslashes in front of it.
    ("single_quote", "regex", r"([rR]?[bB]?|[bB]?[rR]?)?'((?<!\\)(\\{2})*\\'|[^'])*(?<!\\)(\\{2})*'", dict(is_code=True)),
    ("double_quote", "regex", r'([rR]?[bB]?|[bB]?[rR]?)?"((?<!\\)(\\{2})*\\"|[^"])*(?<!\\)(\\{2})*"', dict(is_code=True))
])

bigquery_dialect.add(
    DoubleQuotedLiteralSegment=NamedSegment.make('double_quote', name='literal', type='quoted_literal')
)

bigquery_dialect.replace(
    QuotedIdentifierSegment=NamedSegment.make('back_quote', name='identifier', type='quoted_identifier'),
    LiteralGrammar=OneOf(
        Ref('QuotedLiteralSegment'), Ref('DoubleQuotedLiteralSegment'), Ref('NumericLiteralSegment'),
        Ref('BooleanLiteralGrammar'), Ref('QualifiedNumericLiteralSegment'), Ref('IntervalLiteralSegment')
    ),
)
