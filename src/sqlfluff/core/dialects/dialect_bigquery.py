"""The BigQuery dialect.

This inherits from the ansi dialect, with changes as specified by
https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
and
https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
"""

from ..parser import (
    BaseSegment,
    NamedSegment,
    OneOf,
    Ref,
    Sequence,
    Bracketed,
    Delimited,
    ReSegment,
    AnyNumberOf,
    Anything,
    KeywordSegment,
    Indent,
    Dedent,
)

from .dialect_ansi import (
    ansi_dialect,
    SelectTargetElementSegment as AnsiSelectTargetElementSegment,
    SelectClauseSegment as AnsiSelectClauseSegment,
)


bigquery_dialect = ansi_dialect.copy_as("bigquery")

bigquery_dialect.patch_lexer_struct(
    [
        # Quoted literals can have r or b (case insensitive) prefixes, in any order, to
        # indicate a raw/regex string or byte sequence, respectively.  Allow escaped quote
        # characters inside strings by allowing \" with an optional even multiple of
        # backslashes in front of it.
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
        # Triple quoted variant first, then single quoted
        (
            "single_quote",
            "regex",
            r"([rR]?[bB]?|[bB]?[rR]?)?('''((?<!\\)(\\{2})*\\'|'{,2}(?!')|[^'])*(?<!\\)(\\{2})*'''|'((?<!\\)(\\{2})*\\'|[^'])*(?<!\\)(\\{2})*')",
            dict(is_code=True),
        ),
        (
            "double_quote",
            "regex",
            r'([rR]?[bB]?|[bB]?[rR]?)?(\"\"\"((?<!\\)(\\{2})*\\\"|\"{,2}(?!\")|[^\"])*(?<!\\)(\\{2})*\"\"\"|"((?<!\\)(\\{2})*\\"|[^"])*(?<!\\)(\\{2})*")',
            dict(is_code=True),
        ),
    ]
)

bigquery_dialect.add(
    DoubleQuotedLiteralSegment=NamedSegment.make(
        "double_quote", name="quoted_literal", type="literal", trim_chars=('"',)
    ),
    StructKeywordSegment=KeywordSegment.make('struct', name="struct"),
)

# Add additional datetime units
# https://cloud.google.com/bigquery/docs/reference/standard-sql/date_functions#extract
bigquery_dialect.sets("datetime_units").update(
    ["MICROSECOND", "DAYOFWEEK", "ISOWEEK", "ISOYEAR", "DATE", "DATETIME", "TIME"]
)

# Unreserved Keywords
bigquery_dialect.sets("unreserved_keywords").add("SYSTEM_TIME")
bigquery_dialect.sets("unreserved_keywords").remove("FOR")
# Reserved Keywords
bigquery_dialect.sets("reserved_keywords").add("FOR")


# BigQuery allows functions in INTERVAL
class IntervalExpressionSegment(BaseSegment):
    """An interval with a function as value segment."""

    type = "interval_expression"
    match_grammar = Sequence(
        "INTERVAL",
        OneOf(Ref("NumericLiteralSegment"), Ref("FunctionSegment")),
        OneOf(Ref("QuotedLiteralSegment"), Ref("DatetimeUnitSegment")),
    )


class SelectClauseSegment(AnsiSelectClauseSegment):
    """In BigQuery, select * as struct is valid."""

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

class SelectTargetElementSegment(AnsiSelectTargetElementSegment):
    parse_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            OneOf(
                Ref("LiteralGrammar"),
                Ref("BareFunctionSegment"),
                Ref("FunctionSegment"),
                Ref("IntervalExpressionSegment"),
                Ref("StructSegment"),
                Ref("ColumnReferenceSegment"),
                Ref("ExpressionSegment"),
            ),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )

bigquery_dialect.replace(
    QuotedIdentifierSegment=NamedSegment.make(
        "back_quote", name="quoted_identifier", type="identifier", trim_chars=("`",)
    ),
    IntervalExpressionSegment=IntervalExpressionSegment,
    LiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("DoubleQuotedLiteralSegment"),
        Ref("NumericLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
        Ref("QualifiedNumericLiteralSegment"),
        Ref("NullKeywordSegment"),
    ),
    PostTableExpressionGrammar=Sequence(
        Sequence(
            "FOR", "SYSTEM_TIME", "AS", "OF", Ref("ExpressionSegment"), optional=True
        ),
        Sequence("WITH", "OFFSET", "AS", Ref("SingleIdentifierGrammar"), optional=True),
    ),
    FunctionNameSegment=ReSegment.make(
        # In BigQuery struct() has a special syntax, so we don't treat it as a function
        r"[A-Z][A-Z0-9_]*", name="function_name", type="function_name", _anti_template=r"STRUCT"
    ),
    SelectTargetElementSegment=SelectTargetElementSegment,
    SelectClauseSegment=SelectClauseSegment,
)


@bigquery_dialect.segment(replace=True)
class WildcardExpressionSegment(BaseSegment):
    """An extension of the star expression for Bigquery."""

    type = "wildcard_expression"
    match_grammar = Sequence(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardIdentifierSegment"),
        # Optional EXCEPT or REPLACE clause
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#select_replace
        Ref("ExceptClauseSegment", optional=True),
        Ref("ReplaceClauseSegment", optional=True),
    )


@bigquery_dialect.segment()
class ExceptClauseSegment(BaseSegment):
    """SELECT EXCEPT clause."""

    type = "select_except_clause"
    match_grammar = Sequence(
        "EXCEPT",
        Bracketed(
            Delimited(Ref("SingleIdentifierGrammar"), delimiter=Ref("CommaSegment"))
        ),
    )


@bigquery_dialect.segment()
class ReplaceClauseSegment(BaseSegment):
    """SELECT REPLACE clause."""

    type = "select_replace_clause"
    match_grammar = Sequence(
        "REPLACE",
        OneOf(
            # Multiple replace in brackets
            Bracketed(
                Delimited(
                    # Not *really* a select target element. It behaves exactly
                    # the same way however.
                    Ref("SelectTargetElementSegment"),
                    delimiter=Ref("CommaSegment"),
                )
            ),
            # Single replace not in brackets.
            Ref("SelectTargetElementSegment"),
        ),
    )



@bigquery_dialect.segment()
class StructSegment(BaseSegment):
    """Container of ordered fields each with a type (required) and field name (optional).

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#constructing_a_struct
    """
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
            optional=True,
        )
    )
