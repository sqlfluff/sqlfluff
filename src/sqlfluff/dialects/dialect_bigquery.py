"""The BigQuery dialect.

This inherits from the ansi dialect, with changes as specified by
https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
and
https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
"""

import itertools

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    Anything,
    BaseSegment,
    OneOf,
    Ref,
    Sequence,
    Bracketed,
    Delimited,
    AnyNumberOf,
    KeywordSegment,
    SymbolSegment,
    RegexLexer,
    StringLexer,
    CodeSegment,
    NamedParser,
    StringParser,
    RegexParser,
    Nothing,
    StartsWith,
    OptionallyBracketed,
    Indent,
    Dedent,
    Matchable,
)
from sqlfluff.core.parser.segments.base import BracketedSegment
from sqlfluff.dialects.dialect_bigquery_keywords import (
    bigquery_reserved_keywords,
    bigquery_unreserved_keywords,
)

ansi_dialect = load_raw_dialect("ansi")
bigquery_dialect = ansi_dialect.copy_as("bigquery")

bigquery_dialect.insert_lexer_matchers(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [
        StringLexer("right_arrow", "=>", CodeSegment),
        StringLexer("question_mark", "?", CodeSegment),
        RegexLexer("atsign_literal", r"@[a-zA-Z_][\w]*", CodeSegment),
    ],
    before="equals",
)

bigquery_dialect.patch_lexer_matchers(
    [
        # Quoted literals can have r or b (case insensitive) prefixes, in any order, to
        # indicate a raw/regex string or byte sequence, respectively.  Allow escaped quote
        # characters inside strings by allowing \" with an optional even multiple of
        # backslashes in front of it.
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
    SelectClauseElementListGrammar=Delimited(
        Ref("SelectClauseElementSegment"),
        delimiter=Ref("CommaSegment"),
        allow_trailing=True,
    ),
    QuestionMarkSegment=StringParser(
        "?", SymbolSegment, name="question_mark", type="question_mark"
    ),
    AtSignLiteralSegment=NamedParser(
        "atsign_literal",
        CodeSegment,
        name="atsign_literal",
        type="literal",
        trim_chars=("@",),
    ),
    # Add a Full equivalent which also allow keywords
    NakedIdentifierSegmentFull=RegexParser(
        r"[A-Z0-9_]*[A-Z][A-Z0-9_]*",
        CodeSegment,
        name="naked_identifier_all",
        type="identifier",
    ),
    SingleIdentifierGrammarFull=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("NakedIdentifierSegmentFull"),
    ),
    DefaultDeclareOptionsGrammar=Sequence(
        "DEFAULT",
        OneOf(
            Ref("LiteralGrammar"),
            Bracketed(Ref("SelectStatementSegment")),
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Ref("ArrayLiteralSegment"),
            Ref("TypelessStructSegment"),
            Ref("TupleSegment"),
            Ref("BaseExpressionElementGrammar"),
        ),
    ),
)


bigquery_dialect.replace(
    FunctionContentsExpressionGrammar=OneOf(
        Ref("DatetimeUnitSegment"),
        Sequence(
            Ref("ExpressionSegment"),
            Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
        ),
        Ref("NamedArgumentSegment"),
    ),
    SimpleArrayTypeGrammar=Sequence(
        "ARRAY",
        Bracketed(
            Ref("DatatypeIdentifierSegment"),
            bracket_type="angle",
            bracket_pairs_set="angle_bracket_pairs",
        ),
    ),
    # BigQuery also supports the special "Struct" construct.
    BaseExpressionElementGrammar=ansi_dialect.get_grammar(
        "BaseExpressionElementGrammar"
    ).copy(insert=[Ref("TypelessStructSegment")]),
    FunctionContentsGrammar=ansi_dialect.get_grammar("FunctionContentsGrammar").copy(
        insert=[Ref("TypelessStructSegment")],
        before=Ref("ExpressionSegment"),
    ),
    # BigQuery allows underscore in parameter names, and also anything if quoted in backticks
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
        Ref("TableAliasExpressionSegment", optional=True),
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
# https://cloud.google.com/bigquery/docs/reference/standard-sql/date_functions#extract
bigquery_dialect.sets("datetime_units").update(
    ["MICROSECOND", "DAYOFWEEK", "ISOWEEK", "ISOYEAR", "DATE", "DATETIME", "TIME"]
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


@bigquery_dialect.segment()
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


@bigquery_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """Enhance `SELECT` statement to include QUALIFY."""

    type = "select_statement"
    match_grammar = ansi_dialect.get_segment(
        "SelectStatementSegment"
    ).match_grammar.copy()

    parse_grammar = ansi_dialect.get_segment(
        "SelectStatementSegment"
    ).parse_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OrderByClauseSegment", optional=True),
    )


@bigquery_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(BaseSegment):
    """Enhance unordered `SELECT` statement to include QUALIFY."""

    type = "select_statement"
    match_grammar = ansi_dialect.get_segment(
        "UnorderedSelectStatementSegment"
    ).match_grammar.copy()

    parse_grammar = ansi_dialect.get_segment(
        "UnorderedSelectStatementSegment"
    ).parse_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OverlapsClauseSegment", optional=True),
    )


@bigquery_dialect.segment(replace=True)
class ArrayLiteralSegment(BaseSegment):
    """Override array literal segment to add Typeless Struct."""

    type = "array_literal"
    match_grammar = Bracketed(
        Delimited(
            OneOf(
                Ref("ExpressionSegment"),
                Ref("TypelessStructSegment"),
            ),
            optional=True,
        ),
        bracket_type="square",
    )


@bigquery_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[Ref("DeclareStatementSegment"), Ref("SetStatementSegment")],
    )


@bigquery_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = Sequence(
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
        Sequence("AS", OneOf("STRUCT", "VALUE"), optional=True),
        OneOf("DISTINCT", "ALL", optional=True),
    )


# BigQuery allows functions in INTERVAL
@bigquery_dialect.segment(replace=True)
class IntervalExpressionSegment(BaseSegment):
    """An interval with a function as value segment."""

    type = "interval_expression"
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


@bigquery_dialect.segment(replace=True)
class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    type = "function"
    match_grammar = Sequence(
        Sequence(
            Ref("FunctionNameSegment"),
            Bracketed(
                Ref(
                    "FunctionContentsGrammar",
                    # The brackets might be empty for some functions...
                    optional=True,
                    ephemeral_name="FunctionContentsGrammar",
                )
            ),
            # Functions returning ARRYS in BigQuery can have optional
            # OFFSET or ORDINAL clauses
            Sequence(
                Bracketed(
                    OneOf(
                        "OFFSET",
                        "ORDINAL",
                    ),
                    Bracketed(
                        Ref("NumericLiteralSegment"),
                    ),
                    bracket_type="square",
                ),
                optional=True,
            ),
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
        ),
        Ref("PostFunctionGrammar", optional=True),
    )


@bigquery_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement."""

    match_grammar = Sequence(
        AnyNumberOf(
            Sequence(
                OneOf("DETERMINISTIC", Sequence("NOT", "DETERMINISTIC")),
                optional=True,
            ),
            Sequence(
                "LANGUAGE",
                # Not really a parameter, but best fit for now.
                Ref("ParameterNameSegment"),
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


@bigquery_dialect.segment(replace=True)
class WildcardExpressionSegment(BaseSegment):
    """An extension of the star expression for Bigquery."""

    type = "wildcard_expression"
    match_grammar = ansi_dialect.get_segment(
        "WildcardExpressionSegment"
    ).match_grammar.copy(
        insert=[
            # Optional EXCEPT or REPLACE clause
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#select_replace
            Ref("ExceptClauseSegment", optional=True),
            Ref("ReplaceClauseSegment", optional=True),
        ]
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
                    Ref("SelectClauseElementSegment"),
                    delimiter=Ref("CommaSegment"),
                )
            ),
            # Single replace not in brackets.
            Ref("SelectClauseElementSegment"),
        ),
    )


@bigquery_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment.

    In particular here, this enabled the support for
    the STRUCT datatypes.
    """

    type = "data_type"
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
                    ),
                    delimiter=Ref("CommaSegment"),
                    bracket_pairs_set="angle_bracket_pairs",
                ),
                bracket_type="angle",
                bracket_pairs_set="angle_bracket_pairs",
            ),
        ),
    )


@bigquery_dialect.segment(replace=True)
class FunctionParameterListGrammar(BaseSegment):
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


@bigquery_dialect.segment()
class TypelessStructSegment(BaseSegment):
    """Expression to construct a STRUCT with implicit types.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#typeless_struct_syntax
    """

    type = "typeless_struct"
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


@bigquery_dialect.segment()
class TupleSegment(BaseSegment):
    """Expression to construct a TUPLE.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#tuple_syntax
    """

    type = "tuple"
    match_grammar = Bracketed(Delimited(Ref("BaseExpressionElementGrammar")))


@bigquery_dialect.segment()
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


@bigquery_dialect.segment()
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


# Dialects should not use Python "import" to access other dialects. Instead,
# get a reference to the ANSI ObjectReferenceSegment this way so we can inherit
# from it.
ObjectReferenceSegment = ansi_dialect.get_segment("ObjectReferenceSegment")


@bigquery_dialect.segment(replace=True)
class ColumnReferenceSegment(ObjectReferenceSegment):  # type: ignore
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
                Ref("SingleIdentifierGrammarFull"),
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
                    Ref("DelimiterSegment"),
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
        """Extract possible references of a given level."""
        level = self._level_to_int(level)
        refs = list(self.iter_raw_references())
        if level == self.ObjectReferenceLevel.SCHEMA.value and len(refs) >= 3:
            return [refs[0]]  # pragma: no cover
        if level == self.ObjectReferenceLevel.TABLE.value and len(refs) >= 3:
            # Ambiguous case: The table could be the first or second part, so
            # return both.
            return [refs[0], refs[1]]
        if level == self.ObjectReferenceLevel.OBJECT.value and len(refs) >= 3:
            # Ambiguous case: The object (i.e. column) could be the first or
            # second part, so return both.
            return [refs[1], refs[2]]  # pragma: no cover
        return super().extract_possible_references(level)


@bigquery_dialect.segment()
class HyphenatedObjectReferenceSegment(ObjectReferenceSegment):  # type: ignore
    """A reference to an object that may contain embedded hyphens."""

    type = "hyphenated_object_reference"
    match_grammar = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).match_grammar.copy()
    match_grammar.delimiter = OneOf(
        Ref("DotSegment"),
        Sequence(Ref("DotSegment"), Ref("DotSegment")),
        Sequence(Ref("MinusSegment")),
    )

    def iter_raw_references(self):
        """Generate a list of reference strings and elements.

        Each reference is an ObjectReferencePart. Overrides the base class
        because hyphens (MinusSegment) causes one logical part of the name to
        be split across multiple elements, e.g. "table-a" is parsed as three
        segments.
        """
        # For each descendant element, group them, using "dot" elements as a
        # delimiter.
        for is_dot, elems in itertools.groupby(
            self.recursive_crawl("identifier", "binary_operator", "dot"),
            lambda e: e.is_type("dot"),
        ):
            if not is_dot:
                segments = list(elems)
                parts = [seg.raw_trimmed() for seg in segments]
                yield self.ObjectReferencePart("".join(parts), segments)


@bigquery_dialect.segment(replace=True)
class TableExpressionSegment(BaseSegment):
    """Main table expression e.g. within a FROM clause, with hyphen support."""

    type = "table_expression"
    match_grammar = ansi_dialect.get_segment(
        "TableExpressionSegment"
    ).match_grammar.copy(
        insert=[
            Ref("HyphenatedObjectReferenceSegment"),
        ]
    )


@bigquery_dialect.segment()
class DeclareStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/scripting#declare
    """

    type = "declare_segment"
    match_grammar = StartsWith("DECLARE")
    parse_grammar = Sequence(
        "DECLARE",
        Delimited(Ref("NakedIdentifierSegment")),
        OneOf(
            Ref("DatatypeSegment"),
            Ref("DefaultDeclareOptionsGrammar"),
            Sequence(
                Ref("DatatypeSegment"),
                Ref("DefaultDeclareOptionsGrammar"),
            ),
        ),
    )


@bigquery_dialect.segment()
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


@bigquery_dialect.segment()
class PartitionBySegment(BaseSegment):
    """PARTITION BY partition_expression."""

    type = "partition_by_segment"
    match_grammar = StartsWith(
        "PARTITION",
        terminator=OneOf("CLUSTER", "OPTIONS", "AS", Ref("DelimiterSegment")),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "PARTITION",
        "BY",
        Ref("ExpressionSegment"),
    )


@bigquery_dialect.segment()
class ClusterBySegment(BaseSegment):
    """CLUSTER BY clustering_column_list."""

    type = "cluster_by_segment"
    match_grammar = StartsWith(
        "CLUSTER",
        terminator=OneOf("OPTIONS", "AS", Ref("DelimiterSegment")),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "CLUSTER",
        "BY",
        Delimited(Ref("ExpressionSegment")),
    )


@bigquery_dialect.segment()
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
                    Ref("LiteralGrammar"),
                )
            )
        ),
    )


@bigquery_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
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


@bigquery_dialect.segment()
class ParameterizedSegment(BaseSegment):
    """BigQuery allows named and argument based parameters to help preven SQL Injection.

    https://cloud.google.com/bigquery/docs/parameterized-queries
    """

    type = "parameterized_expression"
    match_grammar = OneOf(Ref("AtSignLiteralSegment"), Ref("QuestionMarkSegment"))


@bigquery_dialect.segment()
class FromPivotExpressionSegment(BaseSegment):
    """A PIVOT expression.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#pivot_operator
    """

    type = "from_pivot_expression"
    match_grammar = Sequence("PIVOT", Bracketed(Anything()))

    parse_grammar = Sequence(
        "PIVOT",
        Bracketed(
            Ref("FunctionSegment"),
            Ref("AliasExpressionSegment", optional=True),
            "FOR",
            Ref("SingleIdentifierGrammar"),
            "IN",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("LiteralGrammar"),
                        Ref("AliasExpressionSegment", optional=True),
                    ),
                    delimiter=Ref("CommaSegment"),
                )
            ),
        ),
    )


@bigquery_dialect.segment()
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
                    Ref("AliasExpressionSegment", optional=True),
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
                            Ref("AliasExpressionSegment", optional=True),
                        ),
                    ),
                ),
            ),
        ),
    )


@bigquery_dialect.segment()
class TableAliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause, optionally with column aliasing."""

    type = "table_alias_expression"
    match_grammar = Sequence(
        Ref("AliasExpressionSegment"),
        # Optional column aliases too.
        Bracketed(
            Delimited(Ref("SingleIdentifierGrammar"), delimiter=Ref("CommaSegment")),
            optional=True,
        ),
    )


@bigquery_dialect.segment(replace=True)
class InsertStatementSegment(BaseSegment):
    """A `INSERT` statement.

    N.B. not a complete implementation.
    """

    type = "insert_statement"
    match_grammar = StartsWith("INSERT")
    parse_grammar = Sequence(
        "INSERT",
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Ref("SelectableGrammar"),
    )


@bigquery_dialect.segment(replace=True)
class SamplingExpressionSegment(BaseSegment):
    """A sampling expression.

    As per https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#tablesample_operator
    """

    type = "sample_expression"
    match_grammar = Sequence(
        "TABLESAMPLE", "SYSTEM", Bracketed(Ref("NumericLiteralSegment"), "PERCENT")
    )
