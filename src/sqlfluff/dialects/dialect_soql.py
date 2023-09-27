"""The SOQL dialect.

https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    BaseSegment,
    CodeSegment,
    LiteralSegment,
    OneOf,
    Ref,
    RegexLexer,
    Sequence,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")

soql_dialect = ansi_dialect.copy_as("soql")

soql_dialect.insert_lexer_matchers(
    [
        # Date and datetime literals as per:
        # https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql_select_dateformats.htm
        RegexLexer(
            "datetime_literal",
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|(\+|\-)[0-9]{2}:[0-9]{2})",  # noqa E501
            CodeSegment,
        ),
        RegexLexer(
            "date_literal",
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}",
            CodeSegment,
        ),
    ],
    before="numeric_literal",
)

date_literals = {
    "YESTERDAY",
    "TODAY",
    "TOMORROW",
    "LAST_WEEK",
    "THIS_WEEK",
    "NEXT_WEEK",
    "LAST_MONTH",
    "THIS_MONTH",
    "NEXT_MONTH",
    "LAST_90_DAYS",
    "NEXT_90_DAYS",
    "THIS_QUARTER",
    "LAST_QUARTER",
    "NEXT_QUARTER",
    "THIS_YEAR",
    "LAST_YEAR",
    "NEXT_YEAR",
    "THIS_FISCAL_QUARTER",
    "LAST_FISCAL_QUARTER",
    "NEXT_FISCAL_QUARTER",
    "THIS_FISCAL_YEAR",
    "LAST_FISCAL_YEAR",
    "NEXT_FISCAL_YEAR",
}

date_n_literals = {
    "LAST_N_DAYS",
    "NEXT_N_DAYS",
    "LAST_N_WEEKS",
    "NEXT_N_WEEKS",
    "LAST_N_MONTHS",
    "NEXT_N_MONTHS",
    "LAST_N_QUARTERS",
    "NEXT_N_QUARTERS",
    "LAST_N_YEARS",
    "NEXT_N_YEARS",
    "LAST_N_FISCAL_QUARTERS",
    "NEXT_N_FISCAL_QUARTERS",
    "LAST_N_FISCAL_YEARS",
    "NEXT_N_FISCAL_YEARS",
}

soql_dialect.sets("reserved_keywords").update(date_literals | date_n_literals)

soql_dialect.sets("bare_functions").update(date_literals)


class DateLiteralNSegment(BaseSegment):
    """A Date literal keyword that takes the :n integer suffix.

    https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql_select_dateformats.htm
    """

    type = "date_n_literal"

    match_grammar = Sequence(
        OneOf(*date_n_literals),
        Ref("ColonSegment"),
        Ref("NumericLiteralSegment"),
        allow_gaps=False,
    )


soql_dialect.replace(
    Expression_C_Grammar=ansi_dialect.get_grammar("Expression_C_Grammar").copy(
        insert=[
            Ref("DateLiteralNSegment"),
        ]
    ),
    DateTimeLiteralGrammar=OneOf(
        TypedParser("date_literal", LiteralSegment, type="date_literal"),
        TypedParser("datetime_literal", LiteralSegment, type="datetime_literal"),
        Sequence(
            OneOf("DATE", "TIME", "TIMESTAMP", "INTERVAL"),
            TypedParser(
                "single_quote", LiteralSegment, type="date_constructor_literal"
            ),
        ),
    ),
)


class StatementSegment(ansi.StatementSegment):
    """SOQL seems to only support SELECT statements.

    https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm
    """

    match_grammar = Ref("SelectableGrammar")
