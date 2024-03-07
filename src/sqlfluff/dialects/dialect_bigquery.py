"""The BigQuery dialect.

This inherits from the ansi dialect, with changes as specified by
https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
and
https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#string_and_bytes_literals
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseFileSegment,
    BaseSegment,
    Bracketed,
    BracketedSegment,
    CodeSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    LiteralSegment,
    Matchable,
    MultiStringParser,
    Nothing,
    OneOf,
    OptionallyBracketed,
    ParseMode,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    StringLexer,
    StringParser,
    SymbolSegment,
    TypedParser,
)
from sqlfluff.dialects import dialect_ansi as ansi
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
        RegexLexer(
            "at_sign_literal",
            r"@[a-zA-Z_][\w]*",
            LiteralSegment,
            segment_kwargs={"trim_chars": ("@",)},
        ),
        RegexLexer(
            "double_at_sign_literal",
            r"@@[a-zA-Z_][\w]*",
            LiteralSegment,
            segment_kwargs={"trim_chars": ("@@",)},
        ),
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
    DoubleQuotedLiteralSegment=TypedParser(
        "double_quote",
        LiteralSegment,
        type="quoted_literal",
        trim_chars=('"',),
    ),
    SingleQuotedLiteralSegment=TypedParser(
        "single_quote",
        LiteralSegment,
        type="quoted_literal",
        trim_chars=("'",),
    ),
    DoubleQuotedUDFBody=TypedParser(
        "double_quote",
        CodeSegment,
        type="udf_body",
        trim_chars=('"',),
    ),
    SingleQuotedUDFBody=TypedParser(
        "single_quote",
        CodeSegment,
        type="udf_body",
        trim_chars=("'",),
    ),
    StartAngleBracketSegment=StringParser(
        "<", SymbolSegment, type="start_angle_bracket"
    ),
    EndAngleBracketSegment=StringParser(">", SymbolSegment, type="end_angle_bracket"),
    RightArrowSegment=StringParser("=>", SymbolSegment, type="right_arrow"),
    DashSegment=StringParser("-", SymbolSegment, type="dash"),
    SelectClauseElementListGrammar=Delimited(
        Ref("SelectClauseElementSegment"),
        allow_trailing=True,
    ),
    QuestionMarkSegment=StringParser("?", SymbolSegment, type="question_mark"),
    AtSignLiteralSegment=TypedParser(
        "at_sign_literal",
        LiteralSegment,
        type="at_sign_literal",
    ),
    DoubleAtSignLiteralSegment=TypedParser(
        "double_at_sign_literal",
        LiteralSegment,
        type="double_at_sign_literal",
    ),
    # Add a Full equivalent which also allow keywords
    NakedIdentifierFullSegment=RegexParser(
        r"[A-Z_][A-Z0-9_]*",
        IdentifierSegment,
        type="naked_identifier_all",
    ),
    NakedIdentifierPart=RegexParser(
        # The part of a an identifier after a hyphen.
        # NOTE: This one can match an "all numbers" variant.
        # https://cloud.google.com/resource-manager/docs/creating-managing-projects
        r"[A-Z0-9_]+",
        IdentifierSegment,
        type="naked_identifier",
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
            terminators=[
                Ref("SemicolonSegment"),
            ],
        ),
    ),
    ExtendedDatetimeUnitSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("extended_datetime_units"),
            CodeSegment,
            type="date_part",
        )
    ),
    ProcedureNameIdentifierSegment=OneOf(
        # In BigQuery struct() has a special syntax, so we don't treat it as a function
        RegexParser(
            r"[A-Z_][A-Z0-9_]*",
            CodeSegment,
            type="procedure_name_identifier",
            anti_template=r"STRUCT",
        ),
        RegexParser(
            r"`[^`]*`",
            CodeSegment,
            type="procedure_name_identifier",
        ),
    ),
    ProcedureParameterGrammar=OneOf(
        Sequence(
            OneOf("IN", "OUT", "INOUT", optional=True),
            Ref("ParameterNameSegment", optional=True),
            OneOf(Sequence("ANY", "TYPE"), Ref("DatatypeSegment")),
        ),
        OneOf(Sequence("ANY", "TYPE"), Ref("DatatypeSegment")),
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
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("DatetimeUnitSegment"),
        Ref("DatePartWeekSegment"),
        Sequence(
            Ref("ExpressionSegment"),
            Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
        ),
        Sequence(Ref("ExpressionSegment"), "HAVING", OneOf("MIN", "MAX")),
        Ref("NamedArgumentSegment"),
    ),
    TrimParametersGrammar=Nothing(),
    # BigQuery allows underscore in parameter names, and also anything if quoted in
    # backticks
    ParameterNameSegment=OneOf(
        RegexParser(r"[A-Z_][A-Z0-9_]*", CodeSegment, type="parameter"),
        RegexParser(r"`[^`]*`", CodeSegment, type="parameter"),
    ),
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "DATETIME", "TIME", "TIMESTAMP"),
        TypedParser("single_quote", LiteralSegment, type="date_constructor_literal"),
    ),
    JoinLikeClauseGrammar=Sequence(
        AnyNumberOf(
            Ref("FromPivotExpressionSegment"),
            Ref("FromUnpivotExpressionSegment"),
            min_times=1,
        ),
        Ref("AliasExpressionSegment", optional=True),
    ),
    ConditionalCrossJoinKeywordsGrammar=Nothing(),
    NaturalJoinKeywordsGrammar=Nothing(),
    UnconditionalCrossJoinKeywordsGrammar=Ref.keyword("CROSS"),
    MergeIntoLiteralGrammar=Sequence("MERGE", Ref.keyword("INTO", optional=True)),
    AccessorGrammar=AnyNumberOf(
        Ref("ArrayAccessorSegment"),
        # Add in semi structured expressions
        Ref("SemiStructuredAccessorSegment"),
    ),
    BracketedSetExpressionGrammar=Bracketed(Ref("SetExpressionSegment")),
)


# Set Keywords
bigquery_dialect.sets("unreserved_keywords").clear()
bigquery_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", bigquery_unreserved_keywords
)

bigquery_dialect.sets("reserved_keywords").clear()
bigquery_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", bigquery_reserved_keywords
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
    ]
)

# Add additional datetime units only recognised in some functions (e.g. extract)
bigquery_dialect.sets("extended_datetime_units").update(["DATE", "DATETIME", "TIME"])

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
    ]
)


# In BigQuery, UNNEST() returns a "value table".
# https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#value_tables
bigquery_dialect.sets("value_table_functions").update(["UNNEST"])

# Bracket pairs (a set of tuples). Note that BigQuery inherits the default
# "bracket_pairs" set from ANSI. Here, we're adding a different set of bracket
# pairs that are only available in specific contexts where they are
# applicable. This limits the scope where BigQuery allows angle brackets,
# eliminating many potential parsing errors with the "<" and ">" operators.
bigquery_dialect.bracket_sets("angle_bracket_pairs").update(
    [
        ("angle", "StartAngleBracketSegment", "EndAngleBracketSegment", False),
    ]
)


class ArrayTypeSegment(ansi.ArrayTypeSegment):
    """Prefix for array literals specifying the type."""

    type = "array_type"
    match_grammar = Sequence(
        "ARRAY",
        Bracketed(
            Ref("DatatypeSegment"),
            bracket_type="angle",
            bracket_pairs_set="angle_bracket_pairs",
        ),
    )


class QualifyClauseSegment(BaseSegment):
    """A `QUALIFY` clause like in `SELECT`."""

    type = "qualify_clause"
    match_grammar = Sequence(
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

    match_grammar = ansi.SelectStatementSegment.match_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OrderByClauseSegment", optional=True),
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """Enhance unordered `SELECT` statement to include QUALIFY."""

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[Ref("QualifyClauseSegment", optional=True)],
        before=Ref("OverlapsClauseSegment", optional=True),
    )


class MultiStatementSegment(BaseSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    type = "multi_statement_segment"
    match_grammar: Matchable = OneOf(
        Ref("ForInStatementSegment"),
        Ref("RepeatStatementSegment"),
        Ref("WhileStatementSegment"),
        Ref("LoopStatementSegment"),
        Ref("IfStatementSegment"),
        Ref("CreateProcedureStatementSegment"),
        Ref("BeginStatementSegment"),
    )


class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    match_grammar = Sequence(
        Sequence(
            OneOf(
                Ref("MultiStatementSegment"),
                Ref("StatementSegment"),
            ),
        ),
        AnyNumberOf(
            Ref("DelimiterGrammar"),
            OneOf(
                Ref("MultiStatementSegment"),
                Ref("StatementSegment"),
            ),
        ),
        Ref("DelimiterGrammar", optional=True),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("DeclareStatementSegment"),
            Ref("SetStatementSegment"),
            Ref("ExportStatementSegment"),
            Ref("CreateExternalTableStatementSegment"),
            Ref("AssertStatementSegment"),
            Ref("CallStatementSegment"),
            Ref("ReturnStatementSegment"),
            Ref("BreakStatementSegment"),
            Ref("LeaveStatementSegment"),
            Ref("ContinueStatementSegment"),
            Ref("RaiseStatementSegment"),
            Ref("AlterViewStatementSegment"),
            Ref("CreateMaterializedViewStatementSegment"),
            Ref("AlterMaterializedViewStatementSegment"),
            Ref("DropMaterializedViewStatementSegment"),
        ],
    )


class AssertStatementSegment(BaseSegment):
    """ASSERT segment.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/debugging-statements
    """

    type = "assert_statement"
    match_grammar: Matchable = Sequence(
        "ASSERT",
        Ref("ExpressionSegment"),
        Sequence(
            "AS",
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


class ForInStatementsSegment(BaseSegment):
    """Statements within a FOR..IN...DO...END FOR statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#for-in
    """

    type = "for_in_statements"
    match_grammar = AnyNumberOf(
        Sequence(
            OneOf(
                Ref("StatementSegment"),
                Ref("MultiStatementSegment"),
            ),
            Ref("DelimiterGrammar"),
        ),
        terminators=[Sequence("END", "FOR")],
        parse_mode=ParseMode.GREEDY,
    )


class ForInStatementSegment(BaseSegment):
    """FOR..IN...DO...END FOR statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#for-in
    """

    type = "for_in_statement"
    match_grammar = Sequence(
        "FOR",
        Ref("SingleIdentifierGrammar"),
        "IN",
        Indent,
        Ref("SelectableGrammar"),
        Dedent,
        "DO",
        Indent,
        Ref("ForInStatementsSegment"),
        Dedent,
        "END",
        "FOR",
    )


class RepeatStatementsSegment(BaseSegment):
    """Statements within a REPEAT...UNTIL... END REPEAT statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#repeat
    """

    type = "repeat_statements"
    match_grammar = AnyNumberOf(
        Sequence(
            OneOf(
                Ref("StatementSegment"),
                Ref("MultiStatementSegment"),
            ),
            Ref("DelimiterGrammar"),
        ),
        terminators=["UNTIL"],
        parse_mode=ParseMode.GREEDY,
    )


class RepeatStatementSegment(BaseSegment):
    """REPEAT...END REPEAT statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#repeat
    """

    type = "repeat_statement"
    match_grammar = Sequence(
        "REPEAT",
        Indent,
        Ref("RepeatStatementsSegment"),
        "UNTIL",
        Ref("ExpressionSegment"),
        Dedent,
        "END",
        "REPEAT",
    )


class IfStatementsSegment(BaseSegment):
    """Statements within a IF... END IF statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#if
    """

    type = "if_statements"
    match_grammar = AnyNumberOf(
        Sequence(
            OneOf(
                Ref("StatementSegment"),
                Ref("MultiStatementSegment"),
            ),
            Ref("DelimiterGrammar"),
        ),
        terminators=[
            "ELSE",
            "ELSEIF",
            Sequence("END", "IF"),
        ],
        parse_mode=ParseMode.GREEDY,
    )


class IfStatementSegment(BaseSegment):
    """IF...END IF statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#if
    """

    type = "if_statement"
    match_grammar = Sequence(
        "IF",
        Ref("ExpressionSegment"),
        "THEN",
        Indent,
        Ref("IfStatementsSegment"),
        Dedent,
        AnyNumberOf(
            Sequence(
                "ELSEIF",
                Ref("ExpressionSegment"),
                "THEN",
                Indent,
                Ref("IfStatementsSegment"),
                Dedent,
            ),
        ),
        Sequence(
            "ELSE",
            Indent,
            Ref("IfStatementsSegment"),
            Dedent,
            optional=True,
        ),
        "END",
        "IF",
    )


class LoopStatementsSegment(BaseSegment):
    """Statements within a LOOP... END LOOP statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#loop
    """

    type = "loop_statements"
    match_grammar = AnyNumberOf(
        Sequence(
            OneOf(
                Ref("StatementSegment"),
                Ref("MultiStatementSegment"),
            ),
            Ref("DelimiterGrammar"),
        ),
        terminators=[Sequence("END", "LOOP")],
        parse_mode=ParseMode.GREEDY,
    )


class LoopStatementSegment(BaseSegment):
    """LOOP...END LOOP statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#loop
    """

    type = "loop_statement"
    match_grammar = Sequence(
        "LOOP",
        Indent,
        Ref("LoopStatementsSegment"),
        Dedent,
        "END",
        "LOOP",
    )


class WhileStatementsSegment(BaseSegment):
    """Statements within a WHILE... END WHILE statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#while
    """

    type = "while_statements"
    match_grammar = AnyNumberOf(
        Sequence(
            Ref("StatementSegment"),
            Ref("DelimiterGrammar"),
        ),
        terminators=[Sequence("END", "WHILE")],
        parse_mode=ParseMode.GREEDY,
    )


class WhileStatementSegment(BaseSegment):
    """WHILE...END WHILE statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#while
    """

    type = "while_statement"
    match_grammar = Sequence(
        "WHILE",
        Ref("ExpressionSegment"),
        "DO",
        Indent,
        Ref("WhileStatementsSegment"),
        Dedent,
        "END",
        "WHILE",
    )


class SelectClauseModifierSegment(ansi.SelectClauseModifierSegment):
    """Things that come after SELECT but before the columns."""

    match_grammar = Sequence(
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
        OneOf("DISTINCT", "ALL", optional=True),
        Sequence("AS", OneOf("STRUCT", "VALUE"), optional=True),
    )


# BigQuery allows functions in INTERVAL
class IntervalExpressionSegment(ansi.IntervalExpressionSegment):
    """An interval with a function as value segment."""

    match_grammar = Sequence(
        "INTERVAL",
        Ref("ExpressionSegment"),
        OneOf(
            Ref("QuotedLiteralSegment"),
            Ref("DatetimeUnitSegment"),
            Sequence(
                Ref("DatetimeUnitSegment"),
                "TO",
                Ref("DatetimeUnitSegment"),
            ),
        ),
    )


bigquery_dialect.replace(
    QuotedIdentifierSegment=TypedParser(
        "back_quote",
        IdentifierSegment,
        type="quoted_identifier",
        trim_chars=("`",),
    ),
    # Add ParameterizedSegment to the ansi NumericLiteralSegment
    NumericLiteralSegment=OneOf(
        TypedParser("numeric_literal", LiteralSegment, type="numeric_literal"),
        Ref("ParameterizedSegment"),
    ),
    QuotedLiteralSegment=OneOf(
        Ref("SingleQuotedLiteralSegment"),
        Ref("DoubleQuotedLiteralSegment"),
    ),
    # Add elements to the ansi LiteralGrammar
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("ParameterizedSegment"),
            Ref("SystemVariableSegment"),
        ]
    ),
    PostTableExpressionGrammar=Sequence(
        Sequence(
            "FOR",
            OneOf("SYSTEM_TIME", Sequence("SYSTEM", "TIME")),
            "AS",
            "OF",
            Ref("ExpressionSegment"),
            optional=True,
        ),
        Sequence(
            "WITH",
            "OFFSET",
            Sequence("AS", Ref("SingleIdentifierGrammar"), optional=True),
            optional=True,
        ),
    ),
    FunctionNameIdentifierSegment=OneOf(
        # In BigQuery struct() and array() have a special syntax,
        # so we don't treat them as functions
        RegexParser(
            r"[A-Z_][A-Z0-9_]*",
            CodeSegment,
            type="function_name_identifier",
            anti_template=r"^(STRUCT|ARRAY)$",
        ),
        RegexParser(
            r"`[^`]*`",
            CodeSegment,
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
        type="function_name_identifier",
    )


class ArrayFunctionNameSegment(BaseSegment):
    """ARRAY function name segment.

    Need to be able to specify this as type `function_name_identifier`
    within a `function_name` so that linting rules identify it properly.
    """

    type = "function_name"
    match_grammar: Matchable = StringParser(
        "ARRAY",
        CodeSegment,
        type="function_name_identifier",
    )


class DatePartWeekSegment(BaseSegment):
    """WEEK(<WEEKDAY>) in EXTRACT, DATE_DIFF, DATE_TRUNC, LAST_DAY.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/date_functions#extract
    https://cloud.google.com/bigquery/docs/reference/standard-sql/date_functions#date_diff
    https://cloud.google.com/bigquery/docs/reference/standard-sql/date_functions#date_trunc
    https://cloud.google.com/bigquery/docs/reference/standard-sql/date_functions#last_day
    """

    type = "date_part_week"
    match_grammar: Matchable = Sequence(
        "WEEK",
        Bracketed(
            OneOf(
                "SUNDAY",
                "MONDAY",
                "TUESDAY",
                "WEDNESDAY",
                "THURSDAY",
                "FRIDAY",
                "SATURDAY",
            ),
        ),
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
            type="function_name_identifier",
        ),
        StringParser(
            "NORMALIZE_AND_CASEFOLD",
            CodeSegment,
            type="function_name_identifier",
        ),
    )


class FunctionNameSegment(ansi.FunctionNameSegment):
    """Describes the name of a function.

    This includes any prefix bits, e.g. project, schema or the SAFE keyword.
    """

    match_grammar: Matchable = Sequence(
        # Project name, schema identifier, etc.
        AnyNumberOf(
            Sequence(
                # BigQuery Function names can be prefixed by the keyword SAFE to
                # return NULL instead of error.
                # https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-reference#safe_prefix
                OneOf("SAFE", Ref("SingleIdentifierGrammar")),
                Ref("DotSegment"),
            ),
            terminators=[Ref("BracketedSegment")],
        ),
        # Base function name
        OneOf(
            Ref("FunctionNameIdentifierSegment"),
            Ref("QuotedIdentifierSegment"),
            terminators=[Ref("BracketedSegment")],
        ),
        # BigQuery allows whitespaces between the `.` of a function refrence or
        # SAFE prefix. Keeping the explicit `allow_gaps=True` here to
        # make the distinction from `ansi.FunctionNameSegment` clear.
        allow_gaps=True,
    )


class FunctionSegment(ansi.FunctionSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    match_grammar = Sequence(
        OneOf(
            Sequence(
                # BigQuery EXTRACT allows optional TimeZone
                Ref("ExtractFunctionNameSegment"),
                Bracketed(
                    OneOf(
                        Ref("DatetimeUnitSegment"),
                        Ref("DatePartWeekSegment"),
                        Ref("ExtendedDatetimeUnitSegment"),
                    ),
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
                        Ref("DatePartWeekSegment"),
                        Ref(
                            "FunctionContentsGrammar",
                        ),
                    ),
                    parse_mode=ParseMode.GREEDY,
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
                        ),
                        parse_mode=ParseMode.GREEDY,
                    ),
                ),
                # Functions returning ARRAYS in BigQuery can have optional
                # Array Accessor clauses
                Ref("ArrayAccessorSegment", optional=True),
                # Functions returning STRUCTs in BigQuery can have the fields
                # elements referenced (e.g. ".a"), including wildcards (e.g. ".*")
                # or multiple nested fields (e.g. ".a.b", or ".a.b.c")
                Ref("SemiStructuredAccessorSegment", optional=True),
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
        Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
    )


class BeginStatementSegment(BaseSegment):
    """A `BEGIN...EXCEPTION...END` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#beginexceptionend
    """

    type = "begin_statement"

    match_grammar = Sequence(
        "BEGIN",
        Indent,
        AnyNumberOf(
            Sequence(
                Ref("StatementSegment"),
                Ref("DelimiterGrammar"),
            ),
            min_times=1,
            terminators=["END", "EXCEPTION"],
            parse_mode=ParseMode.GREEDY,
        ),
        Dedent,
        Sequence(
            "EXCEPTION",
            "WHEN",
            "ERROR",
            "THEN",
            Indent,
            AnyNumberOf(
                Sequence(
                    Ref("StatementSegment"),
                    Ref("DelimiterGrammar"),
                ),
                min_times=1,
                terminators=["END"],
                parse_mode=ParseMode.GREEDY,
            ),
            Dedent,
            optional=True,
        ),
        "END",
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
            )
        ),
    )


class DatatypeSegment(ansi.DatatypeSegment):
    """A data type segment.

    In particular here, this enabled the support for
    the STRUCT datatypes.
    """

    match_grammar = OneOf(  # Parameter type
        Sequence(
            Ref("DatatypeIdentifierSegment"),  # Simple type
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#parameterized_data_types
            Ref("BracketedArguments", optional=True),
        ),
        Sequence("ANY", "TYPE"),  # SQL UDFs can specify this "type"
        Ref("ArrayTypeSegment"),
        Ref("StructTypeSegment"),
    )


class StructTypeSegment(ansi.StructTypeSegment):
    """Expression to construct a STRUCT datatype."""

    match_grammar = Sequence(
        "STRUCT",
        Ref("StructTypeSchemaSegment", optional=True),
    )


class StructTypeSchemaSegment(BaseSegment):
    """Expression to construct the schema of a STRUCT datatype."""

    type = "struct_type_schema"
    match_grammar = Bracketed(
        Delimited(  # Comma-separated list of field names/types
            Sequence(
                OneOf(
                    # ParameterNames can look like Datatypes so can't use
                    # Optional=True here and instead do a OneOf in order
                    # with DataType only first, followed by both.
                    Ref("DatatypeSegment"),
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("DatatypeSegment"),
                    ),
                ),
                AnyNumberOf(Ref("ColumnConstraintSegment")),
                Ref("OptionsSegment", optional=True),
            ),
        ),
        bracket_type="angle",
        bracket_pairs_set="angle_bracket_pairs",
    )


class ArrayExpressionSegment(ansi.ArrayExpressionSegment):
    """Expression to construct a ARRAY from a subquery.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/array_functions#array
    """

    match_grammar = Sequence(
        Ref("ArrayFunctionNameSegment"),
        Bracketed(
            Ref("SelectableGrammar"),
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


class SemiStructuredAccessorSegment(BaseSegment):
    """A semi-structured data accessor segment."""

    type = "semi_structured_expression"
    match_grammar = Sequence(
        AnyNumberOf(
            Sequence(
                Ref("DotSegment"),
                OneOf(
                    Ref("SingleIdentifierGrammar"),
                    Ref("StarSegment"),
                ),
                allow_gaps=True,
            ),
            Ref("ArrayAccessorSegment", optional=True),
            allow_gaps=True,
            min_times=1,
        ),
        allow_gaps=True,
    )


class ColumnReferenceSegment(ansi.ObjectReferenceSegment):
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
            Ref("ObjectReferenceDelimiterGrammar"),
            Delimited(
                Ref("SingleIdentifierFullGrammar"),
                delimiter=Ref("ObjectReferenceDelimiterGrammar"),
                terminators=[
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
                ],
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


class TableReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an object that may contain embedded hyphens."""

    type = "table_reference"

    match_grammar: Matchable = Delimited(
        Sequence(
            Ref("SingleIdentifierGrammar"),
            AnyNumberOf(
                Sequence(
                    Ref("DashSegment"),
                    Ref("NakedIdentifierPart"),
                    allow_gaps=False,
                ),
                optional=True,
            ),
            allow_gaps=False,
        ),
        delimiter=Ref("ObjectReferenceDelimiterGrammar"),
        terminators=[
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
        ],
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
        parts = []
        elems_for_parts = []

        def flush():
            nonlocal parts, elems_for_parts
            result = self.ObjectReferencePart("".join(parts), elems_for_parts)
            parts = []
            elems_for_parts = []
            return result

        for elem in self.recursive_crawl(
            "identifier", "literal", "dash", "dot", "star"
        ):
            if not elem.is_type("dot"):
                if elem.is_type("identifier"):
                    # Found an identifier (potentially with embedded dots).
                    elem_subparts = elem.raw_trimmed().split(".")
                    for idx, part in enumerate(elem_subparts):
                        # Save each part of the segment.
                        parts.append(part)
                        elems_for_parts.append(elem)

                        if idx != len(elem_subparts) - 1:
                            # For each part except the last, flush.
                            yield flush()

                else:
                    # For non-identifier segments, save the whole segment.
                    parts.append(elem.raw_trimmed())
                    elems_for_parts.append(elem)
            else:
                yield flush()

        # Flush any leftovers.
        if parts:
            yield flush()


class SystemVariableSegment(BaseSegment):
    """BigQuery supports usage of system-level variables, which are prefixed with @@.

    These are also used in exception blocks in the @@error object.

    https://cloud.google.com/bigquery/docs/reference/system-variables
    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#beginexceptionend
    """

    type = "system_variable"
    match_grammar = Ref("DoubleAtSignLiteralSegment")


class DeclareStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/scripting#declare
    """

    type = "declare_segment"
    match_grammar = Sequence(
        "DECLARE",
        Delimited(Ref("SingleIdentifierFullGrammar")),
        OneOf(
            Ref("DefaultDeclareOptionsGrammar"),
            Sequence(
                Ref("DatatypeSegment"),
                Ref("DefaultDeclareOptionsGrammar", optional=True),
            ),
        ),
    )


class SetStatementSegment(BaseSegment):
    """Setting an already declared variable.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/scripting#set
    """

    type = "set_segment"
    match_grammar = Sequence(
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
                Ref("ExpressionSegment"),
            ),
        ),
    )


class PartitionBySegment(BaseSegment):
    """PARTITION BY partition_expression."""

    type = "partition_by_segment"
    match_grammar = Sequence(
        "PARTITION",
        "BY",
        Ref("ExpressionSegment"),
    )


class ClusterBySegment(BaseSegment):
    """CLUSTER BY clustering_column_list."""

    type = "cluster_by_segment"
    match_grammar = Sequence(
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


class TableConstraintSegment(ansi.TableConstraintSegment):
    """A table constraint segment.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#table_constraints
    """

    type = "table_constraint"
    match_grammar = OneOf(
        Sequence(
            Ref("PrimaryKeyGrammar"),
            Ref("BracketedColumnReferenceListGrammar"),
            "NOT",
            "ENFORCED",
        ),
        Sequence(
            Ref("ForeignKeyGrammar"),
            Ref("BracketedColumnReferenceListGrammar"),
            "REFERENCES",
            Ref("TableReferenceSegment"),
            Ref("BracketedColumnReferenceListGrammar"),
            "NOT",
            "ENFORCED",
        ),
    )


class ColumnDefinitionSegment(ansi.ColumnDefinitionSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE.

    Override ANSI support to allow passing of column options
    """

    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        Ref("DatatypeSegment"),  # Column type
        AnyNumberOf(Ref("ColumnConstraintSegment")),
        Ref("OptionsSegment", optional=True),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """`CREATE TABLE` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#create_table_statement
    """

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryTransientGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Sequence(
            OneOf("COPY", "LIKE", "CLONE"),
            Ref("TableReferenceSegment"),
            optional=True,
        ),
        # Column list
        Sequence(
            Bracketed(
                Delimited(
                    OneOf(
                        Ref("ColumnDefinitionSegment"),
                        Ref("TableConstraintSegment"),
                    ),
                    allow_trailing=True,
                )
            ),
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


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """A `ALTER TABLE` statement."""

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#alter_table_set_options_statement
            Sequence(
                "SET",
                Ref("OptionsSegment"),
            ),
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#alter_table_add_column_statement
            Delimited(
                Sequence(
                    "ADD",
                    "COLUMN",
                    Ref("IfNotExistsGrammar", optional=True),
                    Ref("ColumnDefinitionSegment"),
                ),
                allow_trailing=True,
            ),
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#alter_table_rename_to_statement
            Sequence(
                "RENAME",
                "TO",
                Ref("TableReferenceSegment"),
            ),
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#alter_table_rename_column_statement
            Delimited(
                Sequence(
                    "RENAME",
                    "COLUMN",
                    Ref("IfExistsGrammar", optional=True),
                    Ref("SingleIdentifierGrammar"),  # Column name
                    "TO",
                    Ref("SingleIdentifierGrammar"),  # Column name
                ),
                allow_trailing=True,
            ),
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#alter_table_drop_column_statement
            Delimited(
                Sequence(
                    "DROP",
                    "COLUMN",
                    Ref("IfExistsGrammar", optional=True),
                    Ref("SingleIdentifierGrammar"),  # Column name
                ),
            ),
            # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#alter_column_set_options_statement
            Delimited(
                Sequence(
                    "ALTER",
                    "COLUMN",
                    Ref("IfExistsGrammar", optional=True),
                    Ref("SingleIdentifierGrammar"),  # Column name
                    OneOf(
                        Sequence(
                            "SET",
                            OneOf(
                                Ref("OptionsSegment"),
                                Sequence(
                                    "DATA",
                                    "TYPE",
                                    Ref("DatatypeSegment"),
                                ),
                                Sequence(
                                    "DEFAULT",
                                    OneOf(
                                        Ref("LiteralGrammar"),
                                        Ref("FunctionSegment"),
                                    ),
                                ),
                            ),
                        ),
                        Sequence("DROP", OneOf("DEFAULT", Sequence("NOT", "NULL"))),
                    ),
                ),
            ),
        ),
    )


class CreateExternalTableStatementSegment(BaseSegment):
    """A `CREATE EXTERNAL TABLE` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#create_external_table_statement
    """

    type = "create_external_table_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "EXTERNAL",
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(
                Ref("ColumnDefinitionSegment"),
                allow_trailing=True,
            ),
            optional=True,
        ),
        # Although not specified in the BigQuery documentation optional arguments for
        # CREATE EXTERNAL TABLE statements can be ordered arbitrarily.
        AnyNumberOf(
            # connection names have the same rules as table names in BigQuery
            Sequence("WITH", "CONNECTION", Ref("TableReferenceSegment"), optional=True),
            Sequence(
                "WITH",
                "PARTITION",
                "COLUMNS",
                Bracketed(
                    Delimited(
                        Ref("ColumnDefinitionSegment"),
                        allow_trailing=True,
                    ),
                    optional=True,
                ),
                optional=True,
            ),
            Ref("OptionsSegment", optional=True),
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


class AlterViewStatementSegment(BaseSegment):
    """A `ALTER VIEW` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#alter_view_set_options_statement
    """

    type = "alter_view_statement"

    match_grammar = Sequence(
        "ALTER",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        "SET",
        Ref("OptionsSegment"),
    )


class CreateMaterializedViewStatementSegment(BaseSegment):
    """A `CREATE MATERIALIZED VIEW` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#create_materialized_view_statement
    """

    type = "create_materialized_view_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "MATERIALIZED",
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("PartitionBySegment", optional=True),
        Ref("ClusterBySegment", optional=True),
        Ref("OptionsSegment", optional=True),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
    )


class AlterMaterializedViewStatementSegment(BaseSegment):
    """A `ALTER MATERIALIZED VIEW SET OPTIONS` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#alter_materialized_view_set_options_statement
    """

    type = "alter_materialized_view_set_options_statement"

    match_grammar = Sequence(
        "ALTER",
        "MATERIALIZED",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        "SET",
        Ref("OptionsSegment"),
    )


class DropMaterializedViewStatementSegment(BaseSegment):
    """A `DROP MATERIALIZED VIEW` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#drop_materialized_view_statement
    """

    type = "drop_materialized_view_statement"

    match_grammar = Sequence(
        "DROP",
        "MATERIALIZED",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
    )


class ParameterizedSegment(BaseSegment):
    """BigQuery allows named and argument based parameters to prevent SQL Injection.

    https://cloud.google.com/bigquery/docs/parameterized-queries
    """

    type = "parameterized_expression"
    match_grammar = OneOf(Ref("AtSignLiteralSegment"), Ref("QuestionMarkSegment"))


class PivotForClauseSegment(BaseSegment):
    """The FOR part of a PIVOT expression.

    Needed to avoid BaseExpressionElementGrammar swallowing up the IN part
    """

    type = "pivot_for_clause"
    match_grammar = Sequence(
        Ref("BaseExpressionElementGrammar"),
        terminators=["IN"],
        parse_mode=ParseMode.GREEDY,
    )


class FromPivotExpressionSegment(BaseSegment):
    """A PIVOT expression.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#pivot_operator
    """

    type = "from_pivot_expression"
    match_grammar = Sequence(
        "PIVOT",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("FunctionSegment"),
                    Ref("AliasExpressionSegment", optional=True),
                ),
            ),
            "FOR",
            Ref("PivotForClauseSegment"),
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
        Indent,
        Ref.keyword("AS", optional=True),
        OneOf(
            Ref("QuotedLiteralSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Dedent,
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
            # single column unpivot
            Bracketed(
                Ref("SingleIdentifierGrammar"),
                "FOR",
                Ref("SingleIdentifierGrammar"),
                "IN",
                Bracketed(
                    Delimited(
                        Sequence(
                            Delimited(Ref("SingleIdentifierGrammar")),
                            Ref("UnpivotAliasExpressionSegment", optional=True),
                        ),
                    ),
                ),
            ),
            # multi column unpivot
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

    match_grammar = Sequence(
        "INSERT",
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Ref("SelectableGrammar"),
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
            Ref("ValuesClauseSegment", optional=True),
        ),
        Sequence("INSERT", "ROW"),
    )


class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax#delete_statement
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar: Matchable = Sequence(
        "DELETE",
        Ref.keyword("FROM", optional=True),
        Ref("TableReferenceSegment"),
        Ref("AliasExpressionSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
    )


class ExportStatementSegment(BaseSegment):
    """`EXPORT` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/other-statements#export_data_statement
    """

    type = "export_statement"
    match_grammar: Matchable = Sequence(
        "EXPORT",
        "DATA",
        Sequence("WITH", "CONNECTION", Ref("ObjectReferenceSegment"), optional=True),
        "OPTIONS",
        Bracketed(
            Delimited(
                # String options
                # Note: adding as own type, rather than keywords as convention with
                # Bigquery, as per the docs, is to put Keywords in uppercase, and these
                # in lowercase.
                Sequence(
                    OneOf(
                        StringParser(
                            "compression",
                            CodeSegment,
                            type="export_option",
                        ),
                        StringParser(
                            "field_delimiter",
                            CodeSegment,
                            type="export_option",
                        ),
                        StringParser(
                            "format",
                            CodeSegment,
                            type="export_option",
                        ),
                        StringParser(
                            "uri",
                            CodeSegment,
                            type="export_option",
                        ),
                    ),
                    Ref("EqualsSegment"),
                    Ref("QuotedLiteralSegment"),
                ),
                # Bool options
                # Note: adding as own type, rather than keywords as convention with
                # Bigquery, as per the docs, is to put Keywords in uppercase, and these
                # in lowercase.
                Sequence(
                    OneOf(
                        StringParser(
                            "header",
                            CodeSegment,
                            type="export_option",
                        ),
                        StringParser(
                            "overwrite",
                            CodeSegment,
                            type="export_option",
                        ),
                        StringParser(
                            "use_avro_logical_types",
                            CodeSegment,
                            type="export_option",
                        ),
                    ),
                    Ref("EqualsSegment"),
                    OneOf("TRUE", "FALSE"),
                ),
            ),
        ),
        "AS",
        Ref("SelectableGrammar"),
    )


class ProcedureNameSegment(BaseSegment):
    """Procedure name, including any prefix bits, e.g. project or schema."""

    type = "procedure_name"
    match_grammar: Matchable = Sequence(
        # Project name, schema identifier, etc.
        AnyNumberOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Ref("DotSegment"),
            ),
        ),
        # Base procedure name
        OneOf(
            Ref("ProcedureNameIdentifierSegment"),
            Ref("QuotedIdentifierSegment"),
        ),
        allow_gaps=False,
    )


class ProcedureParameterListSegment(BaseSegment):
    """The parameters for a prcoedure ie. `(string, number)`."""

    # Procedure parameter list (based on FunctionsParameterListGrammar)
    type = "procedure_parameter_list"
    match_grammar = Bracketed(
        Delimited(
            Ref("ProcedureParameterGrammar"),
            optional=True,
        )
    )


class ProcedureStatements(BaseSegment):
    """Statements within a CREATE PROCEDURE statement.

    https://cloud.google.com/bigquery/docs/procedures
    """

    type = "procedure_statements"
    match_grammar = AnyNumberOf(
        Sequence(
            Ref("StatementSegment"),
            Ref("DelimiterGrammar"),
        ),
        terminators=["END"],
        parse_mode=ParseMode.GREEDY,
    )


class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE PROCEDURE` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#create_procedure
    """

    type = "create_procedure_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "PROCEDURE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ProcedureNameSegment"),
        Ref("ProcedureParameterListSegment"),
        Sequence(
            "OPTIONS",
            "strict_mode",
            StringParser("strict_mode", CodeSegment, type="procedure_option"),
            Ref("EqualsSegment"),
            Ref("BooleanLiteralGrammar"),
            optional=True,
        ),
        "BEGIN",
        Indent,
        Ref("ProcedureStatements"),
        Dedent,
        "END",
    )


class CallStatementSegment(BaseSegment):
    """A `CALL` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#call
    """

    type = "call_statement"

    match_grammar: Matchable = Sequence(
        "CALL",
        Ref("ProcedureNameSegment"),
        Bracketed(
            Delimited(
                Ref("ExpressionSegment"),
                optional=True,
            ),
        ),
    )


class ReturnStatementSegment(BaseSegment):
    """A `RETURN` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#return
    """

    type = "return_statement"

    match_grammar: Matchable = Sequence(
        "RETURN",
    )


class BreakStatementSegment(BaseSegment):
    """A `BREAK` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#break
    """

    type = "break_statement"

    match_grammar: Matchable = Sequence(
        "BREAK",
    )


class LeaveStatementSegment(BaseSegment):
    """A `LEAVE` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#leave
    """

    type = "leave_statement"

    match_grammar: Matchable = Sequence(
        "LEAVE",
    )


class ContinueStatementSegment(BaseSegment):
    """A `CONTINUE` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#continue
    """

    type = "continue_statement"

    match_grammar: Matchable = OneOf(
        "CONTINUE",
        "ITERATE",
    )


class RaiseStatementSegment(BaseSegment):
    """A `RAISE` statement.

    https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language#raise
    """

    type = "raise_statement"

    match_grammar: Matchable = Sequence(
        "RAISE",
        Sequence(
            "USING",
            "MESSAGE",
            Ref("EqualsSegment"),
            Ref("ExpressionSegment"),
            optional=True,
        ),
    )
