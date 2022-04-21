"""The BigQuery dialect.

This inherits from the ansi dialect, with changes as specified by
https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
and
https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
"""

import itertools

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    CodeSegment,
    Dedent,
    Delimited,
    Indent,
    KeywordSegment,
    Matchable,
    NamedParser,
    Nothing,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    StartsWith,
    StringLexer,
    StringParser,
    SymbolSegment,
)
from sqlfluff.core.parser.segments.base import BracketedSegment
from sqlfluff.dialects.dialect_bigquery_keywords import (
    bigquery_reserved_keywords,
    bigquery_unreserved_keywords,
)
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")
bigquery_dialect = ansi_dialect.copy_as("bigquery")

bigquery_dialect.insert_lexer_matchers(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [
        StringLexer("right_arrow", "=>", CodeSegment),
        StringLexer("question_mark", "?", CodeSegment),
        RegexLexer("at_sign_literal", r"@[a-zA-Z_][\w]*", CodeSegment),
    ],
    before="equals",
)

bigquery_dialect.patch_lexer_matchers(
    [
        # Quoted literals can have r or b (case insensitive) prefixes, in any order, to
        # indicate a raw/regex string or byte sequence, respectively.  Allow escaped
        # quote characters inside strings by allowing \" with an optional even multiple
        # of backslashes in front of it.
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
        # Triple quoted variant first, then single quoted
        RegexLexer(
            "single_quote",
            r"([rR]?[bB]?|[bB]?[rR]?)?('''((?<!\\)(\\{2})*\\'|'{,2}(?!')|[^'])"
            r"*(?<!\\)(\\{2})*'''|'((?<!\\)(\\{2})*\\'|[^'])*(?<!\\)(\\{2})*')",
            CodeSegment,
        ),
        RegexLexer(
            "double_quote",
            r"([rR]?[bB]?|[bB]?[rR]?)?(\"\"\"((?<!\\)(\\{2})*\\\"|\"{,2}(?!\")"
            r'|[^\"])*(?<!\\)(\\{2})*\"\"\"|"((?<!\\)(\\{2})*\\"|[^"])*(?<!\\)'
            r'(\\{2})*")',
            CodeSegment,
        ),
    ]
)

bigquery_dialect.add(
    DoubleQuotedLiteralSegment=NamedParser(
        "double_quote",
        CodeSegment,
        name="quoted_literal",
        type="literal",
        trim_chars=('"',),
    ),
    SingleQuotedLiteralSegment=NamedParser(
        "single_quote",
        CodeSegment,
        name="quoted_literal",
        type="literal",
        trim_chars=("'",),
    ),
    DoubleQuotedUDFBody=NamedParser(
        "double_quote",
        CodeSegment,
        name="udf_body",
        type="udf_body",
        trim_chars=('"',),
    ),
    SingleQuotedUDFBody=NamedParser(
        "single_quote",
        CodeSegment,
        name="udf_body",
        type="udf_body",
        trim_chars=("'",),
    ),
    StructKeywordSegment=StringParser("struct", KeywordSegment, name="struct"),
    StartAngleBracketSegment=StringParser(
        "<", SymbolSegment, name="start_angle_bracket", type="start_angle_bracket"
    ),
    EndAngleBracketSegment=StringParser(
        ">", SymbolSegment, name="end_angle_bracket", type="end_angle_bracket"
    ),
    RightArrowSegment=StringParser(
        "=>", SymbolSegment, name="right_arrow", type="right_arrow"
    ),
    DashSegment=StringParser("-", SymbolSegment, name="dash", type="dash"),
    SelectClauseElementListGrammar=Delimited(
        Ref("SelectClauseElementSegment"),
        delimiter=Ref("CommaSegment"),
        allow_trailing=True,
    ),
    QuestionMarkSegment=StringParser(
        "?", SymbolSegment, name="question_mark", type="question_mark"
    ),
    AtSignLiteralSegment=NamedParser(
        "at_sign_literal",
        CodeSegment,
        name="at_sign_literal",
        type="literal",
        trim_chars=("@",),
    ),
    # Add a Full equivalent which also allow keywords
    NakedIdentifierFullSegment=RegexParser(
        r"[A-Z_][A-Z0-9_]*",
        CodeSegment,
        name="naked_identifier_all",
        type="identifier",
    ),
    SingleIdentifierFullGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("NakedIdentifierFullSegment"),
    ),
    DefaultDeclareOptionsGrammar=Sequence(
        "DEFAULT",
        OneOf(
            Ref("LiteralGrammar"),
            Bracketed(Ref("SelectStatementSegment")),
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Ref("ArrayLiteralSegment"),
            Ref("TupleSegment"),
            Ref("BaseExpressionElementGrammar"),
        ),
    ),
)


bigquery_dialect.replace(
    # Override to allow _01 type identifiers which are valid in BigQuery
    # The strange regex here it to make sure we don't accidentally match numeric
    # literals. We also use a regex to explicitly exclude disallowed keywords.
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z_][A-Z0-9_]*",
            CodeSegment,
            name="naked_identifier",
            type="identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("DatetimeUnitSegment"),
        Sequence(
            Ref("ExpressionSegment"),
            Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
        ),
        Ref("NamedArgumentSegment"),
    ),
    TrimParametersGrammar=Nothing(),
    SimpleArrayTypeGrammar=Sequence(
        "ARRAY",
        Bracketed(
            Ref("DatatypeSegment"),
            bracket_type="angle",
            bracket_pairs_set="angle_bracket_pairs",
        ),
    ),
    # BigQuery allows underscore in parameter names, and also anything if quoted in
    # backticks
    ParameterNameSegment=OneOf(
        RegexParser(
            r"[A-Z_][A-Z0-9_]*", CodeSegment, name="parameter", type="parameter"
        ),
        RegexParser(r"`[^`]*`", CodeSegment, name="parameter", type="parameter"),
    ),
    DateTimeLiteralGrammar=Nothing(),
    JoinLikeClauseGrammar=Sequence(
        AnyNumberOf(
            Ref("FromPivotExpressionSegment"),
            Ref("FromUnpivotExpressionSegment"),
            min_times=1,
        ),
        Ref("AliasExpressionSegment", optional=True),
    ),
    NaturalJoinKeywordsGrammar=Nothing(),
    MergeIntoLiteralGrammar=Sequence("MERGE", Ref.keyword("INTO", optional=True)),
    Accessor_Grammar=AnyNumberOf(
        Ref("ArrayAccessorSegment"),
        # Add in semi structured expressions
        Ref("SemiStructuredAccessorSegment"),
    ),
)


# Set Keywords
bigquery_dialect.sets("unreserved_keywords").clear()
bigquery_dialect.sets("unreserved_keywords").update(
    [n.strip().upper() for n in bigquery_unreserved_keywords.split("\n")]
)

bigquery_dialect.sets("reserved_keywords").clear()
bigquery_dialect.sets("reserved_keywords").update(
    [n.strip().upper() for n in bigquery_reserved_keywords.split("\n")]
)

# Add additional datetime units
# https://cloud.google.com/bigquery/docs/reference/standard-sql/timestamp_functions#extract
bigquery_dialect.sets("datetime_units").update(
    [
        "MICROSECOND",
        "MILLISECOND",
        "SECOND",
        "MINUTE",
        "HOUR",
        "DAY",
        "DAYOFWEEK",
        "DAYOFYEAR",
        "WEEK",
        "ISOWEEK",
        "MONTH",
        "QUARTER",
        "YEAR",
        "ISOYEAR",
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    ]
)

bigquery_dialect.sets("date_part_function_name").clear()
bigquery_dialect.sets("date_part_function_name").update(
    [
        "DATE_DIFF",
        "DATE_TRUNC",
        "DATETIME_DIFF",
        "DATETIME_TRUNC",
        "EXTRACT",
        "LAST_DAY",
        "TIME_DIFF",
        "TIME_TRUNC",
        "TIMESTAMP_DIFF",
        "TIMESTAMP_TRUNC",
        "WEEK",
    ]
)


# In BigQuery, UNNEST() returns a "value table".
# https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#value_tables
bigquery_dialect.sets("value_table_functions").update(["unnest"])

# Bracket pairs (a set of tuples). Note that BigQuery inherits the default
# "bracket_pairs" set from ANSI. Here, we're adding a different set of bracket
# pairs that are only available in specific contexts where they are
# applicable. This limits the scope where BigQuery allows angle brackets,
# eliminating many potential parsing errors with the "<" and ">" operators.
bigquery_dialect.sets("angle_bracket_pairs").update(
    [
        ("angle", "StartAngleBracketSegment", "EndAngleBracketSegment", False),
    ]
)


class QualifyClauseSegment(BaseSegment):
    """A `QUALIFY` clause like in `SELECT`."""

    type = "qualify_clause"
    match_grammar = StartsWith(
        "QUALIFY",
        terminator=OneOf("WINDOW", "ORDER", "LIMIT"),
        enforce_whitespace_preceding_terminator=True,
    )

    parse_grammar = Sequence(
        "QUALIFY",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


class SetOperatorSegment(BaseSegment):
    """A set operator UNION, INTERSECT or EXCEPT.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#set_operators
    """

    type = "set_operator"
    match_grammar = OneOf(
        Sequence("UNION", OneOf("DISTINCT", "ALL")),
        Sequence("INTERSECT", "DISTINCT"),
        Sequence("EXCEPT", "DISTINCT"),
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """Enhance `SELECT` statement to include QUALIFY."""

    match_grammar = ansi.SelectStatementSegment.match_grammar
    parse_grammar = ansi.SelectStatementSegment.parse_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OrderByClauseSegment", optional=True),
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """Enhance unordered `SELECT` statement to include QUALIFY."""

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar
    parse_grammar = ansi.UnorderedSelectStatementSegment.parse_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OverlapsClauseSegment", optional=True),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar
    parse_grammar = ansi.StatementSegment.parse_grammar.copy(
        insert=[Ref("DeclareStatementSegment"), Ref("SetStatementSegment")],
    )


class SelectClauseModifierSegment(ansi.SelectClauseModifierSegment):
    """Things that come after SELECT but before the columns."""

    match_grammar = Sequence(
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
        Sequence("AS", OneOf("STRUCT", "VALUE"), optional=True),
        OneOf("DISTINCT", "ALL", optional=True),
    )


# BigQuery allows functions in INTERVAL
class IntervalExpressionSegment(ansi.IntervalExpressionSegment):
    """An interval with a function as value segment."""

    match_grammar = Sequence(
        "INTERVAL",
        Ref("ExpressionSegment"),
        OneOf(Ref("QuotedLiteralSegment"), Ref("DatetimeUnitSegment")),
    )


bigquery_dialect.replace(
    QuotedIdentifierSegment=NamedParser(
        "back_quote",
        CodeSegment,
        name="quoted_identifier",
        type="identifier",
        trim_chars=("`",),
    ),
    # Add ParameterizedSegment to the ansi NumericLiteralSegment
    NumericLiteralSegment=OneOf(
        NamedParser(
            "numeric_literal", CodeSegment, name="numeric_literal", type="literal"
        ),
        Ref("ParameterizedSegment"),
    ),
    # Add three elements to the ansi LiteralGrammar
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("DoubleQuotedLiteralSegment"),
            Ref("LiteralCoercionSegment"),
            Ref("ParameterizedSegment"),
        ]
    ),
    PostTableExpressionGrammar=Sequence(
        Sequence(
            "FOR", "SYSTEM_TIME", "AS", "OF", Ref("ExpressionSegment"), optional=True
        ),
        Sequence(
            "WITH",
            "OFFSET",
            Sequence("AS", Ref("SingleIdentifierGrammar"), optional=True),
            optional=True,
        ),
    ),
    FunctionNameIdentifierSegment=OneOf(
        # In BigQuery struct() has a special syntax, so we don't treat it as a function
        RegexParser(
            r"[A-Z_][A-Z0-9_]*",
            CodeSegment,
            name="function_name_identifier",
            type="function_name_identifier",
            anti_template=r"STRUCT",
        ),
        RegexParser(
            r"`[^`]*`",
            CodeSegment,
            name="function_name_identifier",
            type="function_name_identifier",
        ),
    ),
)


class ExtractFunctionNameSegment(BaseSegment):
    """EXTRACT function name segment.

    Need to be able to specify this as type `function_name_identifier`
    within a `function_name` so that linting rules identify it properly.
    """

    type = "function_name"
    match_grammar: Matchable = StringParser(
        "EXTRACT",
        CodeSegment,
        name="function_name_identifier",
        type="function_name_identifier",
    )


class NormalizeFunctionNameSegment(BaseSegment):
    """NORMALIZE function name segment.

    Need to be able to specify this as type `function_name_identifier`
    within a `function_name` so that linting rules identify it properly.
    """

    type = "function_name"
    match_grammar: Matchable = OneOf(
        StringParser(
            "NORMALIZE",
            CodeSegment,
            name="function_name_identifier",
            type="function_name_identifier",
        ),
        StringParser(
            "NORMALIZE_AND_CASEFOLD",
            CodeSegment,
            name="function_name_identifier",
            type="function_name_identifier",
        ),
    )


class FunctionSegment(ansi.FunctionSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    match_grammar = Sequence(
        # BigQuery Function names can be prefixed by the keyword SAFE to
        # return NULL instead of error.
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-reference#safe_prefix
        Sequence("SAFE", Ref("DotSegment"), optional=True),
        OneOf(
            Sequence(
                # BigQuery EXTRACT allows optional TimeZone
                Ref("ExtractFunctionNameSegment"),
                Bracketed(
                    Ref("DatetimeUnitSegment"),
                    "FROM",
                    Ref("ExpressionSegment"),
                ),
            ),
            Sequence(
                # BigQuery NORMALIZE allows optional normalization_mode
                # https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-and-operators#normalize
                Ref("NormalizeFunctionNameSegment"),
                Bracketed(
                    Ref("ExpressionSegment"),
                    Sequence(
                        Ref("CommaSegment"),
                        OneOf("NFC", "NFKC", "NFD", "NFKD"),
                        optional=True,
                    ),
                ),
            ),
            Sequence(
                # Treat functions which take date parts separately
                # So those functions parse date parts as DatetimeUnitSegment
                # rather than identifiers.
                Ref(
                    "DatePartFunctionNameSegment",
                    exclude=Ref("ExtractFunctionNameSegment"),
                ),
                Bracketed(
                    Delimited(
                        Ref("DatetimeUnitSegment"),
                        Ref(
                            "FunctionContentsGrammar",
                            ephemeral_name="FunctionContentsGrammar",
                        ),
                    ),
                ),
            ),
            Sequence(
                Sequence(
                    Ref(
                        "FunctionNameSegment",
                        exclude=OneOf(
                            Ref("DatePartFunctionNameSegment"),
                            Ref("NormalizeFunctionNameSegment"),
                            Ref("ValuesClauseSegment"),
                        ),
                    ),
                    Bracketed(
                        Ref(
                            "FunctionContentsGrammar",
                            # The brackets might be empty for some functions...
                            optional=True,
                            ephemeral_name="FunctionContentsGrammar",
                        )
                    ),
                ),
                # Functions returning ARRAYS in BigQuery can have optional
                # Array Accessor clauses
                Ref("ArrayAccessorSegment", optional=True),
                # Functions returning STRUCTs in BigQuery can have the fields
                # elements referenced (e.g. ".a"), including wildcards (e.g. ".*")
                # or multiple nested fields (e.g. ".a.b", or ".a.b.c")
                Sequence(
                    Ref("DotSegment"),
                    AnyNumberOf(
                        Sequence(
                            Ref("ParameterNameSegment"),
                            Ref("DotSegment"),
                        ),
                    ),
                    OneOf(
                        Ref("ParameterNameSegment"),
                        Ref("StarSegment"),
                    ),
                    optional=True,
                ),
                Ref("PostFunctionGrammar", optional=True),
            ),
        ),
        allow_gaps=False,
    )


class FunctionDefinitionGrammar(ansi.FunctionDefinitionGrammar):
    """This is the body of a `CREATE FUNCTION AS` statement."""

    match_grammar = Sequence(
        AnyNumberOf(
            Sequence(
                OneOf("DETERMINISTIC", Sequence("NOT", "DETERMINISTIC")),
                optional=True,
            ),
            Sequence(
                "LANGUAGE",
                Ref("NakedIdentifierSegment"),
                Sequence(
                    "OPTIONS",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("ParameterNameSegment"),
                                Ref("EqualsSegment"),
                                Anything(),
                            ),
                            delimiter=Ref("CommaSegment"),
                        )
                    ),
                    optional=True,
                ),
            ),
            # There is some syntax not implemented here,
            Sequence(
                "AS",
                OneOf(
                    Ref("DoubleQuotedUDFBody"),
                    Ref("SingleQuotedUDFBody"),
                    Bracketed(
                        OneOf(Ref("ExpressionSegment"), Ref("SelectStatementSegment"))
                    ),
                ),
            ),
        )
    )


class WildcardExpressionSegment(ansi.WildcardExpressionSegment):
    """An extension of the star expression for Bigquery."""

    match_grammar = ansi.WildcardExpressionSegment.match_grammar.copy(
        insert=[
            # Optional EXCEPT or REPLACE clause
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#select_replace
            Ref("ExceptClauseSegment", optional=True),
            Ref("ReplaceClauseSegment", optional=True),
        ]
    )


class ExceptClauseSegment(BaseSegment):
    """SELECT EXCEPT clause."""

    type = "select_except_clause"
    match_grammar = Sequence(
        "EXCEPT",
        Bracketed(
            Delimited(Ref("SingleIdentifierGrammar"), delimiter=Ref("CommaSegment"))
        ),
    )


class ReplaceClauseSegment(BaseSegment):
    """SELECT REPLACE clause."""

    type = "select_replace_clause"
    match_grammar = Sequence(
        "REPLACE",
        Bracketed(
            Delimited(
                # Not *really* a select target element. It behaves exactly
                # the same way however.
                Ref("SelectClauseElementSegment"),
                delimiter=Ref("CommaSegment"),
            )
        ),
    )


class DatatypeSegment(ansi.DatatypeSegment):
    """A data type segment.

    In particular here, this enabled the support for
    the STRUCT datatypes.
    """

    match_grammar = OneOf(  # Parameter type
        Ref("DatatypeIdentifierSegment"),  # Simple type
        Sequence("ANY", "TYPE"),  # SQL UDFs can specify this "type"
        Sequence(
            "ARRAY",
            Bracketed(
                Ref("DatatypeSegment"),
                bracket_type="angle",
                bracket_pairs_set="angle_bracket_pairs",
            ),
        ),
        Sequence(
            "STRUCT",
            Bracketed(
                Delimited(  # Comma-separated list of field names/types
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("DatatypeSegment"),
                        Ref("OptionsSegment", optional=True),
                    ),
                    delimiter=Ref("CommaSegment"),
                    bracket_pairs_set="angle_bracket_pairs",
                ),
                bracket_type="angle",
                bracket_pairs_set="angle_bracket_pairs",
            ),
        ),
    )


class FunctionParameterListGrammar(ansi.FunctionParameterListGrammar):
    """The parameters for a function ie. `(string, number)`."""

    # Function parameter list. Note that the only difference from the ANSI
    # grammar is that BigQuery provides overrides bracket_pairs_set.
    match_grammar = Bracketed(
        Delimited(
            Ref("FunctionParameterGrammar"),
            delimiter=Ref("CommaSegment"),
            bracket_pairs_set="angle_bracket_pairs",
            optional=True,
        )
    )


class TypelessStructSegment(ansi.TypelessStructSegment):
    """Expression to construct a STRUCT with implicit types.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#typeless_struct_syntax
    """

    match_grammar = Sequence(
        "STRUCT",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("BaseExpressionElementGrammar"),
                    Ref("AliasExpressionSegment", optional=True),
                ),
            ),
        ),
    )


class TupleSegment(BaseSegment):
    """Expression to construct a TUPLE.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#tuple_syntax
    """

    type = "tuple"
    match_grammar = Bracketed(Delimited(Ref("BaseExpressionElementGrammar")))


class NamedArgumentSegment(BaseSegment):
    """Named argument to a function.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/geography_functions#st_geogfromgeojson
    """

    type = "named_argument"
    match_grammar = Sequence(
        Ref("NakedIdentifierSegment"),
        Ref("RightArrowSegment"),
        Ref("ExpressionSegment"),
    )


class LiteralCoercionSegment(BaseSegment):
    """A casting operation with a type name preceding a string literal.

    BigQuery allows string literals to be explicitly coerced to one of the
    following 4 types:
    - DATE
    - DATETIME
    - TIME
    - TIMESTAMP

    https://cloud.google.com/bigquery/docs/reference/standard-sql/conversion_rules#literal_coercion

    """

    type = "cast_expression"
    match_grammar = Sequence(
        OneOf("DATE", "DATETIME", "TIME", "TIMESTAMP"),
        Ref("QuotedLiteralSegment"),
    )


# Inherit from the ANSI ObjectReferenceSegment this way so we can inherit
# other segment types from it.
class ObjectReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an object."""

    pass


class SemiStructuredAccessorSegment(BaseSegment):
    """A semi-structured data accessor segment."""

    type = "semi_structured_expression"
    match_grammar = Sequence(
        Ref("DotSegment"),
        Ref("SingleIdentifierGrammar"),
        Ref("ArrayAccessorSegment", optional=True),
        AnyNumberOf(
            Sequence(
                Ref("DotSegment"),
                Ref("SingleIdentifierGrammar"),
                allow_gaps=True,
            ),
            Ref("ArrayAccessorSegment", optional=True),
            allow_gaps=True,
        ),
        allow_gaps=True,
    )


class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias.

    We override this for BigQuery to allow keywords in structures
    (using Full segments) and to properly return references for objects.

    Ref: https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical
    "A reserved keyword must be a quoted identifier if it is a standalone
    keyword or the first component of a path expression. It may be unquoted
    as the second or later component of a path expression."
    """

    type = "column_reference"
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),
        Sequence(
            OneOf(Ref("DotSegment"), Sequence(Ref("DotSegment"), Ref("DotSegment"))),
            Delimited(
                Ref("SingleIdentifierFullGrammar"),
                delimiter=OneOf(
                    Ref("DotSegment"), Sequence(Ref("DotSegment"), Ref("DotSegment"))
                ),
                terminator=OneOf(
                    "ON",
                    "AS",
                    "USING",
                    Ref("CommaSegment"),
                    Ref("CastOperatorSegment"),
                    Ref("StartSquareBracketSegment"),
                    Ref("StartBracketSegment"),
                    Ref("BinaryOperatorGrammar"),
                    Ref("ColonSegment"),
                    Ref("DelimiterGrammar"),
                    BracketedSegment,
                ),
                allow_gaps=False,
            ),
            allow_gaps=False,
            optional=True,
        ),
        allow_gaps=False,
    )

    def extract_possible_references(self, level):
        """Extract possible references of a given level.

        Overrides the parent-class function. BigQuery's support for things like
        the following:
        - Functions that take a table as a parameter (e.g. TO_JSON_STRING)
          https://cloud.google.com/bigquery/docs/reference/standard-sql/
          json_functions#to_json_string
        - STRUCT

        means that, without schema information (which SQLFluff does not have),
        references to data are often ambiguous.
        """
        level = self._level_to_int(level)
        refs = list(self.iter_raw_references())
        if level == self.ObjectReferenceLevel.SCHEMA.value and len(refs) >= 3:
            return [refs[0]]  # pragma: no cover
        if level == self.ObjectReferenceLevel.TABLE.value:
            # One part: Could be a table, e.g. TO_JSON_STRING(t)
            # Two parts: Could be dataset.table or table.column.
            # Three parts: Could be table.column.struct or dataset.table.column.
            # Four parts: dataset.table.column.struct
            # Five parts: project.dataset.table.column.struct
            # So... return the first 3 parts.
            return refs[:3]
        if (
            level == self.ObjectReferenceLevel.OBJECT.value and len(refs) >= 3
        ):  # pragma: no cover
            # Ambiguous case: The object (i.e. column) could be the first or
            # second part, so return both.
            return [refs[1], refs[2]]
        return super().extract_possible_references(level)  # pragma: no cover

    def extract_possible_multipart_references(self, levels):
        """Extract possible multipart references, e.g. schema.table."""
        levels_tmp = [self._level_to_int(level) for level in levels]
        min_level = min(levels_tmp)
        max_level = max(levels_tmp)
        refs = list(self.iter_raw_references())
        if max_level == self.ObjectReferenceLevel.SCHEMA.value and len(refs) >= 3:
            return [tuple(refs[0 : max_level - min_level + 1])]
        # Note we aren't handling other possible cases. We'll add these as
        # needed.
        return super().extract_possible_multipart_references(levels)


class HyphenatedTableReferenceSegment(ObjectReferenceSegment):
    """A reference to an object that may contain embedded hyphens."""

    type = "table_reference"

    match_grammar: Matchable = Delimited(
        Sequence(
            Ref("SingleIdentifierGrammar"),
            AnyNumberOf(
                Sequence(
                    Ref("DashSegment"),
                    OneOf(Ref("SingleIdentifierGrammar"), Ref("NumericLiteralSegment")),
                    allow_gaps=False,
                ),
                optional=True,
            ),
            allow_gaps=False,
        ),
        delimiter=OneOf(
            Ref("DotSegment"), Sequence(Ref("DotSegment"), Ref("DotSegment"))
        ),
        terminator=OneOf(
            "ON",
            "AS",
            "USING",
            Ref("CommaSegment"),
            Ref("CastOperatorSegment"),
            Ref("StartSquareBracketSegment"),
            Ref("StartBracketSegment"),
            Ref("ColonSegment"),
            Ref("DelimiterGrammar"),
            Ref("JoinLikeClauseGrammar"),
            BracketedSegment,
        ),
        allow_gaps=False,
    )

    def iter_raw_references(self):
        """Generate a list of reference strings and elements.

        Each reference is an ObjectReferencePart. Overrides the base class
        because hyphens (DashSegment) causes one logical part of the name to
        be split across multiple elements, e.g. "table-a" is parsed as three
        segments.
        """
        # For each descendant element, group them, using "dot" elements as a
        # delimiter.
        for is_dot, elems in itertools.groupby(
            self.recursive_crawl("identifier", "literal", "dash", "dot"),
            lambda e: e.is_type("dot"),
        ):
            if not is_dot:
                segments = list(elems)
                parts = [seg.raw_trimmed() for seg in segments]
                yield self.ObjectReferencePart("".join(parts), segments)


class TableExpressionSegment(ansi.TableExpressionSegment):
    """Main table expression e.g. within a FROM clause, with hyphen support."""

    match_grammar = ansi.TableExpressionSegment.match_grammar.copy(
        insert=[
            Ref("HyphenatedTableReferenceSegment"),
        ]
    )


class DeclareStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/scripting#declare
    """

    type = "declare_segment"
    match_grammar = Sequence(
        "DECLARE",
        Delimited(Ref("SingleIdentifierFullGrammar")),
        OneOf(
            Ref("DatatypeSegment"),
            Ref("DefaultDeclareOptionsGrammar"),
            Sequence(
                Ref("DatatypeSegment"),
                Ref("DefaultDeclareOptionsGrammar"),
            ),
        ),
    )


class SetStatementSegment(BaseSegment):
    """Setting an already declared variable.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/scripting#set
    """

    type = "set_segment"
    match_grammar = StartsWith("SET")
    parse_grammar = Sequence(
        "SET",
        OneOf(
            Ref("NakedIdentifierSegment"),
            Bracketed(Delimited(Ref("NakedIdentifierSegment"))),
        ),
        Ref("EqualsSegment"),
        Delimited(
            OneOf(
                Ref("LiteralGrammar"),
                Bracketed(Ref("SelectStatementSegment")),
                Ref("BareFunctionSegment"),
                Ref("FunctionSegment"),
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("LiteralGrammar"),
                            Bracketed(Ref("SelectStatementSegment")),
                            Ref("BareFunctionSegment"),
                            Ref("FunctionSegment"),
                        )
                    )
                ),
                Ref("ArrayLiteralSegment"),
            ),
        ),
    )


class PartitionBySegment(BaseSegment):
    """PARTITION BY partition_expression."""

    type = "partition_by_segment"
    match_grammar = StartsWith(
        "PARTITION",
        terminator=OneOf("CLUSTER", "OPTIONS", "AS", Ref("DelimiterGrammar")),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "PARTITION",
        "BY",
        Ref("ExpressionSegment"),
    )


class ClusterBySegment(BaseSegment):
    """CLUSTER BY clustering_column_list."""

    type = "cluster_by_segment"
    match_grammar = StartsWith(
        "CLUSTER",
        terminator=OneOf("OPTIONS", "AS", Ref("DelimiterGrammar")),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "CLUSTER",
        "BY",
        Delimited(Ref("ExpressionSegment")),
    )


class OptionsSegment(BaseSegment):
    """OPTIONS clause for a table."""

    type = "options_segment"
    match_grammar = Sequence(
        "OPTIONS",
        Bracketed(
            Delimited(
                # Table options
                Sequence(
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment"),
                    Ref("BaseExpressionElementGrammar"),
                )
            )
        ),
    )


class ColumnDefinitionSegment(ansi.ColumnDefinitionSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE.

    Override ANSI support to allow passing of column options
    """

    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        Ref("DatatypeSegment"),  # Column type
        Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
        AnyNumberOf(
            Ref("ColumnConstraintSegment", optional=True),
        ),
        Ref("OptionsSegment", optional=True),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement."""

    # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#create_table_statement
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryTransientGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Column list
        Sequence(
            Bracketed(
                Delimited(
                    OneOf(
                        Ref("TableConstraintSegment"),
                        Ref("ColumnDefinitionSegment"),
                    ),
                    allow_trailing=True,
                )
            ),
            Ref("CommentClauseSegment", optional=True),
            optional=True,
        ),
        Ref("PartitionBySegment", optional=True),
        Ref("ClusterBySegment", optional=True),
        Ref("OptionsSegment", optional=True),
        # Create AS syntax:
        Sequence(
            "AS",
            OptionallyBracketed(Ref("SelectableGrammar")),
            optional=True,
        ),
    )


class CreateViewStatementSegment(ansi.CreateViewStatementSegment):
    """A `CREATE VIEW` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#view_option_list
    """

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Optional list of column names
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Ref("OptionsSegment", optional=True),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
    )


class ParameterizedSegment(BaseSegment):
    """BigQuery allows named and argument based parameters to help preven SQL Injection.

    https://cloud.google.com/bigquery/docs/parameterized-queries
    """

    type = "parameterized_expression"
    match_grammar = OneOf(Ref("AtSignLiteralSegment"), Ref("QuestionMarkSegment"))


class FromPivotExpressionSegment(BaseSegment):
    """A PIVOT expression.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#pivot_operator
    """

    type = "from_pivot_expression"
    match_grammar = Sequence("PIVOT", Bracketed(Anything()))

    parse_grammar = Sequence(
        "PIVOT",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("FunctionSegment"),
                    Ref("AliasExpressionSegment", optional=True),
                ),
            ),
            "FOR",
            Ref("SingleIdentifierGrammar"),
            "IN",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("LiteralGrammar"),
                        Ref("AliasExpressionSegment", optional=True),
                    ),
                )
            ),
        ),
    )


class UnpivotAliasExpressionSegment(BaseSegment):
    """In BigQuery UNPIVOT alias's can be single or double quoted or numeric."""

    type = "alias_expression"
    match_grammar = Sequence(
        Ref.keyword("AS", optional=True),
        OneOf(
            Ref("SingleQuotedLiteralSegment"),
            Ref("DoubleQuotedLiteralSegment"),
            Ref("NumericLiteralSegment"),
        ),
    )


class FromUnpivotExpressionSegment(BaseSegment):
    """An UNPIVOT expression.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#unpivot_operator
    """

    type = "from_unpivot_expression"
    match_grammar = Sequence(
        "UNPIVOT",
        Sequence(
            OneOf("INCLUDE", "EXCLUDE"),
            "NULLS",
            optional=True,
        ),
        OneOf(
            Bracketed(
                Ref("SingleIdentifierGrammar"),
                "FOR",
                Ref("SingleIdentifierGrammar"),
                "IN",
                Bracketed(
                    Delimited(Ref("SingleIdentifierGrammar")),
                    Ref("UnpivotAliasExpressionSegment", optional=True),
                ),
            ),
            Bracketed(
                Bracketed(
                    Delimited(
                        Ref("SingleIdentifierGrammar"),
                        min_delimiters=1,
                    ),
                ),
                "FOR",
                Ref("SingleIdentifierGrammar"),
                "IN",
                Bracketed(
                    Delimited(
                        Sequence(
                            Bracketed(
                                Delimited(
                                    Ref("SingleIdentifierGrammar"),
                                    min_delimiters=1,
                                ),
                            ),
                            Ref("UnpivotAliasExpressionSegment", optional=True),
                        ),
                    ),
                ),
            ),
        ),
    )


class InsertStatementSegment(ansi.InsertStatementSegment):
    """A `INSERT` statement.

    N.B. not a complete implementation.
    """

    match_grammar = ansi.InsertStatementSegment.match_grammar
    parse_grammar = Sequence(
        "INSERT",
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # As SelectableGrammar can be bracketed too, the parse gets confused
            # so we need slightly odd syntax here to allow those to parse (rather
            # than just add optional=True to BracketedColumnReferenceListGrammar).
            Ref("SelectableGrammar"),
            Sequence(
                Ref("BracketedColumnReferenceListGrammar"),
                Ref("SelectableGrammar"),
            ),
        ),
    )


class SamplingExpressionSegment(ansi.SamplingExpressionSegment):
    """A sampling expression.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#tablesample_operator
    """

    match_grammar = Sequence(
        "TABLESAMPLE", "SYSTEM", Bracketed(Ref("NumericLiteralSegment"), "PERCENT")
    )


class MergeMatchSegment(ansi.MergeMatchSegment):
    """Contains BigQuery specific merge operations.

    Overriding ANSI to allow `NOT MATCHED BY SOURCE` statements
    """

    type = "merge_match"
    match_grammar: Matchable = AnyNumberOf(
        Ref("MergeMatchedClauseSegment"),
        Ref("MergeNotMatchedByTargetClauseSegment"),
        Ref("MergeNotMatchedBySourceClauseSegment"),
        min_times=1,
    )


class MergeNotMatchedByTargetClauseSegment(ansi.MergeNotMatchedClauseSegment):
    """The `WHEN NOT MATCHED [BY TARGET]` clause within a `MERGE` statement.

    Overriding ANSI to allow optionally `NOT MATCHED [BY TARGET]` statements
    """

    type = "not_matched_by_target_clause"
    match_grammar: Matchable = Sequence(
        "WHEN",
        "NOT",
        "MATCHED",
        Sequence("BY", "TARGET", optional=True),
        Sequence("AND", Ref("ExpressionSegment"), optional=True),
        "THEN",
        Indent,
        Ref("MergeInsertClauseSegment"),
        Dedent,
    )


class MergeNotMatchedBySourceClauseSegment(ansi.MergeMatchedClauseSegment):
    """The `WHEN MATCHED BY SOURCE` clause within a `MERGE` statement.

    It inherits from `ansi.MergeMatchedClauseSegment` because NotMatchedBySource clause
    is conceptionally more close to a Matched clause than to NotMatched clause, i.e.
    it get's combined with an UPDATE or DELETE, not with an INSERT.
    """

    type = "merge_when_matched_clause"
    match_grammar: Matchable = Sequence(
        "WHEN",
        "NOT",
        "MATCHED",
        "BY",
        "SOURCE",
        Sequence("AND", Ref("ExpressionSegment"), optional=True),
        "THEN",
        Indent,
        OneOf(
            Ref("MergeUpdateClauseSegment"),
            Ref("MergeDeleteClauseSegment"),
        ),
        Dedent,
    )


class MergeInsertClauseSegment(ansi.MergeInsertClauseSegment):
    """`INSERT` clause within the `MERGE` statement.

    Overriding ANSI to allow `INSERT ROW` statements
    """

    match_grammar: Matchable = OneOf(
        Sequence(
            "INSERT",
            Indent,
            Ref("BracketedColumnReferenceListGrammar", optional=True),
            Dedent,
            Indent,
            Ref("ValuesClauseSegment", optional=True),
            Dedent,
        ),
        Sequence("INSERT", "ROW"),
    )
