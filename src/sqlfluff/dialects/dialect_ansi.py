"""The core ANSI dialect.

This is the core SQL grammar. We'll probably extend this or make it pluggable
for other dialects. Here we encode the structure of the language.

There shouldn't be any underlying "machinery" here, that should all
be defined elsewhere.

A lot of the inspiration for this sql grammar is taken from the cockroach
labs full sql grammar. In particular their way for dividing up the expression
grammar. Check out their docs, they're awesome.
https://www.cockroachlabs.com/docs/stable/sql-grammar.html#select_stmt
"""

from enum import Enum
from typing import Generator, List, NamedTuple, Optional, Set, Tuple, Union, cast

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo, ColumnAliasInfo
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    Anything,
    BaseFileSegment,
    BaseSegment,
    BinaryOperatorSegment,
    Bracketed,
    BracketedSegment,
    CodeSegment,
    CommentSegment,
    ComparisonOperatorSegment,
    CompositeBinaryOperatorSegment,
    CompositeComparisonOperatorSegment,
    Conditional,
    Dedent,
    Delimited,
    IdentifierSegment,
    ImplicitIndent,
    Indent,
    KeywordSegment,
    LiteralKeywordSegment,
    LiteralSegment,
    Matchable,
    MultiStringParser,
    NewlineSegment,
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
    WhitespaceSegment,
    WordSegment,
)
from sqlfluff.dialects.dialect_ansi_keywords import (
    ansi_reserved_keywords,
    ansi_unreserved_keywords,
)

ansi_dialect = Dialect("ansi", root_segment_name="FileSegment")

ansi_dialect.set_lexer_matchers(
    [
        # Match all forms of whitespace except newlines and carriage returns:
        # https://stackoverflow.com/questions/3469080/match-whitespace-but-not-newlines
        # This pattern allows us to also match non-breaking spaces (#2189).
        RegexLexer("whitespace", r"[^\S\r\n]+", WhitespaceSegment),
        RegexLexer(
            "inline_comment",
            r"(--|#)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--", "#")},
        ),
        RegexLexer(
            "block_comment",
            r"\/\*([^\*]|\*(?!\/))*\*\/",
            CommentSegment,
            subdivider=RegexLexer(
                "newline",
                r"\r\n|\n",
                NewlineSegment,
            ),
            trim_post_subdivide=RegexLexer(
                "whitespace",
                r"[^\S\r\n]+",
                WhitespaceSegment,
            ),
        ),
        RegexLexer("single_quote", r"'([^'\\]|\\.|'')*'", CodeSegment),
        RegexLexer("double_quote", r'"([^"\\]|\\.)*"', CodeSegment),
        RegexLexer("back_quote", r"`[^`]*`", CodeSegment),
        # See https://www.geeksforgeeks.org/postgresql-dollar-quoted-string-constants/
        RegexLexer("dollar_quote", r"\$(\w*)\$[^\1]*?\$\1\$", CodeSegment),
        # Numeric literal matches integers, decimals, and exponential formats,
        # Pattern breakdown:
        # (?>                      Atomic grouping
        #                          (https://www.regular-expressions.info/atomic.html).
        #     \d+\.\d+             e.g. 123.456
        #     |\d+\.(?![\.\w])     e.g. 123.
        #                          (N.B. negative lookahead assertion to ensure we
        #                          don't match range operators `..` in Exasol, and
        #                          that in bigquery we don't match the "."
        #                          in "asd-12.foo").
        #     |\.\d+               e.g. .456
        #     |\d+                 e.g. 123
        # )
        # (\.?[eE][+-]?\d+)?          Optional exponential.
        # (
        #     (?<=\.)              If matched character ends with . (e.g. 123.) then
        #                          don't worry about word boundary check.
        #     |(?=\b)              Check that we are at word boundary to avoid matching
        #                          valid naked identifiers (e.g. 123column).
        # )
        RegexLexer(
            "numeric_literal",
            r"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))",
            LiteralSegment,
        ),
        RegexLexer("like_operator", r"!?~~?\*?", ComparisonOperatorSegment),
        RegexLexer("newline", r"\r\n|\n", NewlineSegment),
        StringLexer("casting_operator", "::", CodeSegment),
        StringLexer("equals", "=", CodeSegment),
        StringLexer("greater_than", ">", CodeSegment),
        StringLexer("less_than", "<", CodeSegment),
        StringLexer("not", "!", CodeSegment),
        StringLexer("dot", ".", CodeSegment),
        StringLexer("comma", ",", CodeSegment),
        StringLexer("plus", "+", CodeSegment),
        StringLexer("minus", "-", CodeSegment),
        StringLexer("divide", "/", CodeSegment),
        StringLexer("percent", "%", CodeSegment),
        StringLexer("question", "?", CodeSegment),
        StringLexer("ampersand", "&", CodeSegment),
        StringLexer("vertical_bar", "|", CodeSegment),
        StringLexer("caret", "^", CodeSegment),
        StringLexer("star", "*", CodeSegment),
        StringLexer("start_bracket", "(", CodeSegment),
        StringLexer("end_bracket", ")", CodeSegment),
        StringLexer("start_square_bracket", "[", CodeSegment),
        StringLexer("end_square_bracket", "]", CodeSegment),
        StringLexer("start_curly_bracket", "{", CodeSegment),
        StringLexer("end_curly_bracket", "}", CodeSegment),
        StringLexer("colon", ":", CodeSegment),
        StringLexer("semicolon", ";", CodeSegment),
        # This is the "fallback" lexer for anything else which looks like SQL.
        RegexLexer("word", r"[0-9a-zA-Z_]+", WordSegment),
    ]
)

# Set the bare functions
ansi_dialect.sets("bare_functions").update(
    ["current_timestamp", "current_time", "current_date"]
)

# Set the datetime units
ansi_dialect.sets("datetime_units").update(
    [
        "DAY",
        "DAYOFYEAR",
        "HOUR",
        "MILLISECOND",
        "MINUTE",
        "MONTH",
        "QUARTER",
        "SECOND",
        "WEEK",
        "WEEKDAY",
        "YEAR",
    ]
)

ansi_dialect.sets("date_part_function_name").update(["DATEADD"])

# Set Keywords
ansi_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", ansi_unreserved_keywords
)
ansi_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", ansi_reserved_keywords
)

# Bracket pairs (a set of tuples).
# (name, startref, endref, persists)
# NOTE: The `persists` value controls whether this type
# of bracket is persisted during matching to speed up other
# parts of the matching process. Round brackets are the most
# common and match the largest areas and so are sufficient.
ansi_dialect.bracket_sets("bracket_pairs").update(
    [
        ("round", "StartBracketSegment", "EndBracketSegment", True),
        ("square", "StartSquareBracketSegment", "EndSquareBracketSegment", False),
        ("curly", "StartCurlyBracketSegment", "EndCurlyBracketSegment", False),
    ]
)

# Set the value table functions. These are functions that, if they appear as
# an item in "FROM", are treated as returning a COLUMN, not a TABLE. Apparently,
# among dialects supported by SQLFluff, only BigQuery has this concept, but this
# set is defined in the ANSI dialect because:
# - It impacts core linter rules (see AL04 and several other rules that subclass
#   from it) and how they interpret the contents of table_expressions
# - At least one other database (DB2) has the same value table function,
#   UNNEST(), as BigQuery. DB2 is not currently supported by SQLFluff.
ansi_dialect.sets("value_table_functions").update([])

ansi_dialect.add(
    # Real segments
    DelimiterGrammar=Ref("SemicolonSegment"),
    SemicolonSegment=StringParser(";", SymbolSegment, type="statement_terminator"),
    ColonSegment=StringParser(":", SymbolSegment, type="colon"),
    SliceSegment=StringParser(":", SymbolSegment, type="slice"),
    # NOTE: The purpose of the colon_delimiter is that it has different layout rules.
    # It assumes no whitespace on either side.
    ColonDelimiterSegment=StringParser(":", SymbolSegment, type="colon_delimiter"),
    StartBracketSegment=StringParser("(", SymbolSegment, type="start_bracket"),
    EndBracketSegment=StringParser(")", SymbolSegment, type="end_bracket"),
    StartSquareBracketSegment=StringParser(
        "[", SymbolSegment, type="start_square_bracket"
    ),
    EndSquareBracketSegment=StringParser("]", SymbolSegment, type="end_square_bracket"),
    StartCurlyBracketSegment=StringParser(
        "{", SymbolSegment, type="start_curly_bracket"
    ),
    EndCurlyBracketSegment=StringParser("}", SymbolSegment, type="end_curly_bracket"),
    CommaSegment=StringParser(",", SymbolSegment, type="comma"),
    DotSegment=StringParser(".", SymbolSegment, type="dot"),
    StarSegment=StringParser("*", SymbolSegment, type="star"),
    TildeSegment=StringParser("~", SymbolSegment, type="tilde"),
    ParameterSegment=StringParser("?", SymbolSegment, type="parameter"),
    CastOperatorSegment=StringParser("::", SymbolSegment, type="casting_operator"),
    PlusSegment=StringParser("+", SymbolSegment, type="binary_operator"),
    MinusSegment=StringParser("-", SymbolSegment, type="binary_operator"),
    PositiveSegment=StringParser("+", SymbolSegment, type="sign_indicator"),
    NegativeSegment=StringParser("-", SymbolSegment, type="sign_indicator"),
    DivideSegment=StringParser("/", SymbolSegment, type="binary_operator"),
    MultiplySegment=StringParser("*", SymbolSegment, type="binary_operator"),
    ModuloSegment=StringParser("%", SymbolSegment, type="binary_operator"),
    SlashSegment=StringParser("/", SymbolSegment, type="slash"),
    AmpersandSegment=StringParser("&", SymbolSegment, type="ampersand"),
    PipeSegment=StringParser("|", SymbolSegment, type="pipe"),
    BitwiseXorSegment=StringParser("^", SymbolSegment, type="binary_operator"),
    LikeOperatorSegment=TypedParser(
        "like_operator", ComparisonOperatorSegment, type="like_operator"
    ),
    RawNotSegment=StringParser("!", SymbolSegment, type="raw_comparison_operator"),
    RawEqualsSegment=StringParser("=", SymbolSegment, type="raw_comparison_operator"),
    RawGreaterThanSegment=StringParser(
        ">", SymbolSegment, type="raw_comparison_operator"
    ),
    RawLessThanSegment=StringParser("<", SymbolSegment, type="raw_comparison_operator"),
    # The following functions can be called without parentheses per ANSI specification
    BareFunctionSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("bare_functions"),
            CodeSegment,
            type="bare_function",
        )
    ),
    # The strange regex here it to make sure we don't accidentally match numeric
    # literals. We also use a regex to explicitly exclude disallowed keywords.
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z0-9_]*[A-Z][A-Z0-9_]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    ParameterNameSegment=RegexParser(
        r"\"?[A-Z][A-Z0-9_]*\"?", CodeSegment, type="parameter"
    ),
    FunctionNameIdentifierSegment=TypedParser(
        "word", WordSegment, type="function_name_identifier"
    ),
    # Maybe data types should be more restrictive?
    DatatypeIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: OneOf(
            RegexParser(
                r"[A-Z_][A-Z0-9_]*",
                CodeSegment,
                type="data_type_identifier",
                anti_template=r"^(NOT)$",
                # TODO - this is a stopgap until we implement explicit data types
            ),
            Ref("SingleIdentifierGrammar", exclude=Ref("NakedIdentifierSegment")),
        ),
    ),
    # Ansi Intervals
    DatetimeUnitSegment=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("datetime_units"),
            CodeSegment,
            type="date_part",
        )
    ),
    DatePartFunctionName=SegmentGenerator(
        lambda dialect: MultiStringParser(
            dialect.sets("date_part_function_name"),
            CodeSegment,
            type="function_name_identifier",
        )
    ),
    QuotedIdentifierSegment=TypedParser(
        "double_quote", IdentifierSegment, type="quoted_identifier"
    ),
    QuotedLiteralSegment=TypedParser(
        "single_quote", LiteralSegment, type="quoted_literal"
    ),
    SingleQuotedIdentifierSegment=TypedParser(
        "single_quote", IdentifierSegment, type="quoted_identifier"
    ),
    NumericLiteralSegment=TypedParser(
        "numeric_literal", LiteralSegment, type="numeric_literal"
    ),
    # NullSegment is defined separately to the keyword, so we can give it a different
    # type
    NullLiteralSegment=StringParser("null", LiteralKeywordSegment, type="null_literal"),
    NanLiteralSegment=StringParser("nan", LiteralKeywordSegment, type="null_literal"),
    TrueSegment=StringParser("true", LiteralKeywordSegment, type="boolean_literal"),
    FalseSegment=StringParser("false", LiteralKeywordSegment, type="boolean_literal"),
    # We use a GRAMMAR here not a Segment. Otherwise, we get an unnecessary layer
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        terminators=[Ref("DotSegment")],
    ),
    BooleanLiteralGrammar=OneOf(Ref("TrueSegment"), Ref("FalseSegment")),
    # We specifically define a group of arithmetic operators to make it easier to
    # override this if some dialects have different available operators
    ArithmeticBinaryOperatorGrammar=OneOf(
        Ref("PlusSegment"),
        Ref("MinusSegment"),
        Ref("DivideSegment"),
        Ref("MultiplySegment"),
        Ref("ModuloSegment"),
        Ref("BitwiseAndSegment"),
        Ref("BitwiseOrSegment"),
        Ref("BitwiseXorSegment"),
        Ref("BitwiseLShiftSegment"),
        Ref("BitwiseRShiftSegment"),
    ),
    SignedSegmentGrammar=OneOf(Ref("PositiveSegment"), Ref("NegativeSegment")),
    StringBinaryOperatorGrammar=OneOf(Ref("ConcatSegment")),
    BooleanBinaryOperatorGrammar=OneOf(
        Ref("AndOperatorGrammar"), Ref("OrOperatorGrammar")
    ),
    IsDistinctFromGrammar=Sequence(
        "IS", Ref.keyword("NOT", optional=True), "DISTINCT", "FROM"
    ),
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment"),
        Ref("LikeOperatorSegment"),
        Ref("IsDistinctFromGrammar"),
    ),
    # hookpoint for other dialects
    # e.g. EXASOL str to date cast with DATE '2021-01-01'
    # Give it a different type as needs to be single quotes and
    # should not be changed by rules (e.g. rule CV10)
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "TIME", "TIMESTAMP", "INTERVAL"),
        TypedParser("single_quote", LiteralSegment, type="date_constructor_literal"),
    ),
    # Hookpoint for other dialects
    # e.g. INTO is optional in BIGQUERY
    MergeIntoLiteralGrammar=Sequence("MERGE", "INTO"),
    LiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("NumericLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
        Ref("QualifiedNumericLiteralSegment"),
        # NB: Null is included in the literals, because it is a keyword which
        # can otherwise be easily mistaken for an identifier.
        Ref("NullLiteralSegment"),
        Ref("DateTimeLiteralGrammar"),
        Ref("ArrayLiteralSegment"),
        Ref("TypedArrayLiteralSegment"),
        Ref("ObjectLiteralSegment"),
    ),
    AndOperatorGrammar=StringParser("AND", BinaryOperatorSegment),
    OrOperatorGrammar=StringParser("OR", BinaryOperatorSegment),
    NotOperatorGrammar=StringParser("NOT", KeywordSegment, type="keyword"),
    # This is a placeholder for other dialects.
    PreTableFunctionKeywordsGrammar=Nothing(),
    BinaryOperatorGrammar=OneOf(
        Ref("ArithmeticBinaryOperatorGrammar"),
        Ref("StringBinaryOperatorGrammar"),
        Ref("BooleanBinaryOperatorGrammar"),
        Ref("ComparisonOperatorGrammar"),
    ),
    # This pattern is used in a lot of places.
    # Defined here to avoid repetition.
    BracketedColumnReferenceListGrammar=Bracketed(
        Delimited(
            Ref("ColumnReferenceSegment"),
        ),
    ),
    OrReplaceGrammar=Sequence("OR", "REPLACE"),
    TemporaryTransientGrammar=OneOf("TRANSIENT", Ref("TemporaryGrammar")),
    TemporaryGrammar=OneOf("TEMP", "TEMPORARY"),
    IfExistsGrammar=Sequence("IF", "EXISTS"),
    IfNotExistsGrammar=Sequence("IF", "NOT", "EXISTS"),
    LikeGrammar=OneOf("LIKE", "RLIKE", "ILIKE"),
    UnionGrammar=Sequence("UNION", OneOf("DISTINCT", "ALL", optional=True)),
    IsClauseGrammar=OneOf(
        Ref("NullLiteralSegment"),
        Ref("NanLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
    ),
    InOperatorGrammar=Sequence(
        Ref.keyword("NOT", optional=True),
        "IN",
        OneOf(
            Bracketed(
                OneOf(
                    Delimited(
                        Ref("Expression_A_Grammar"),
                    ),
                    Ref("SelectableGrammar"),
                ),
                parse_mode=ParseMode.GREEDY,
            ),
            Ref("FunctionSegment"),  # E.g. UNNEST()
        ),
    ),
    SelectClauseTerminatorGrammar=OneOf(
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        "OVERLAPS",
        Ref("SetOperatorSegment"),
        "FETCH",
    ),
    # Define these as grammars to allow child dialects to enable them (since they are
    # non-standard keywords)
    IsNullGrammar=Nothing(),
    NotNullGrammar=Nothing(),
    CollateGrammar=Nothing(),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "QUALIFY",
        "WINDOW",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("WithDataClauseSegment"),
        "FETCH",
    ),
    WhereClauseTerminatorGrammar=OneOf(
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "QUALIFY",
        "WINDOW",
        "OVERLAPS",
        "FETCH",
    ),
    GroupByClauseTerminatorGrammar=OneOf(
        Sequence("ORDER", "BY"),
        "LIMIT",
        "HAVING",
        "QUALIFY",
        "WINDOW",
        "FETCH",
    ),
    HavingClauseTerminatorGrammar=OneOf(
        Sequence("ORDER", "BY"),
        "LIMIT",
        "QUALIFY",
        "WINDOW",
        "FETCH",
    ),
    OrderByClauseTerminators=OneOf(
        "LIMIT",
        "HAVING",
        "QUALIFY",
        # For window functions
        "WINDOW",
        Ref("FrameClauseUnitGrammar"),
        "SEPARATOR",
        "FETCH",
    ),
    PrimaryKeyGrammar=Sequence("PRIMARY", "KEY"),
    ForeignKeyGrammar=Sequence("FOREIGN", "KEY"),
    UniqueKeyGrammar=Sequence("UNIQUE"),
    # Odd syntax, but prevents eager parameters being confused for data types
    FunctionParameterGrammar=OneOf(
        Sequence(
            Ref("ParameterNameSegment", optional=True),
            OneOf(Sequence("ANY", "TYPE"), Ref("DatatypeSegment")),
        ),
        OneOf(Sequence("ANY", "TYPE"), Ref("DatatypeSegment")),
    ),
    AutoIncrementGrammar=Sequence("AUTO_INCREMENT"),
    # Base Expression element is the right thing to reference for everything
    # which functions as an expression, but could include literals.
    BaseExpressionElementGrammar=OneOf(
        Ref("LiteralGrammar"),
        Ref("BareFunctionSegment"),
        Ref("IntervalExpressionSegment"),
        Ref("FunctionSegment"),
        Ref("ColumnReferenceSegment"),
        Ref("ExpressionSegment"),
        Sequence(
            Ref("DatatypeSegment"),
            Ref("LiteralGrammar"),
        ),
        # These terminators allow better performance by giving a signal
        # of a likely complete match if they come after a match. For
        # example "123," only needs to match against the LiteralGrammar
        # and because a comma follows, never be matched against
        # ExpressionSegment or FunctionSegment, which are both much
        # more complicated.
        terminators=[
            Ref("CommaSegment"),
            Ref.keyword("AS"),
            # TODO: We can almost certainly add a few more here.
        ],
    ),
    FilterClauseGrammar=Sequence(
        "FILTER", Bracketed(Sequence("WHERE", Ref("ExpressionSegment")))
    ),
    IgnoreRespectNullsGrammar=Sequence(OneOf("IGNORE", "RESPECT"), "NULLS"),
    FrameClauseUnitGrammar=OneOf("ROWS", "RANGE"),
    # Some dialects do not support `ON` or `USING` with `CROSS JOIN`
    ConditionalCrossJoinKeywordsGrammar=Ref.keyword("CROSS"),
    JoinTypeKeywordsGrammar=OneOf(
        "INNER",
        Sequence(
            OneOf(
                "FULL",
                "LEFT",
                "RIGHT",
            ),
            Ref.keyword("OUTER", optional=True),
        ),
    ),
    # Extensible in individual dialects
    NonStandardJoinTypeKeywordsGrammar=Nothing(),
    ConditionalJoinKeywordsGrammar=OneOf(
        Ref("JoinTypeKeywordsGrammar"),
        Ref("ConditionalCrossJoinKeywordsGrammar"),
        Ref("NonStandardJoinTypeKeywordsGrammar"),
    ),
    JoinUsingConditionGrammar=Sequence(
        "USING",
        Indent,
        Bracketed(
            # NB: We don't use BracketedColumnReferenceListGrammar
            # here because we're just using SingleIdentifierGrammar,
            # rather than ObjectReferenceSegment or
            # ColumnReferenceSegment.
            # This is a) so that we don't lint it as a reference and
            # b) because the column will probably be returned anyway
            # during parsing.
            Delimited(Ref("SingleIdentifierGrammar")),
            parse_mode=ParseMode.GREEDY,
        ),
        Dedent,
    ),
    # It's as a sequence to allow to parametrize that in Postgres dialect with LATERAL
    JoinKeywordsGrammar=Sequence("JOIN"),
    # NATURAL joins are not supported in all dialects (e.g. not in Bigquery
    # or T-SQL). So define here to allow override with Nothing() for those.
    NaturalJoinKeywordsGrammar=Sequence(
        "NATURAL",
        Ref("JoinTypeKeywordsGrammar", optional=True),
    ),
    UnconditionalCrossJoinKeywordsGrammar=Nothing(),
    # Some dialects such as DuckDB and Clickhouse support a row by row
    # join between two tables (e.g. POSITIONAL and PASTE)
    HorizontalJoinKeywordsGrammar=Nothing(),
    UnconditionalJoinKeywordsGrammar=OneOf(
        Ref("NaturalJoinKeywordsGrammar"),
        Ref("UnconditionalCrossJoinKeywordsGrammar"),
        Ref("HorizontalJoinKeywordsGrammar"),
    ),
    # This can be overwritten by dialects
    ExtendedNaturalJoinKeywordsGrammar=Nothing(),
    NestedJoinGrammar=Nothing(),
    ReferentialActionGrammar=OneOf(
        "RESTRICT",
        "CASCADE",
        Sequence("SET", "NULL"),
        Sequence("NO", "ACTION"),
        Sequence("SET", "DEFAULT"),
    ),
    DropBehaviorGrammar=OneOf("RESTRICT", "CASCADE", optional=True),
    ColumnConstraintDefaultGrammar=OneOf(
        Ref("ShorthandCastSegment"),
        Ref("LiteralGrammar"),
        Ref("FunctionSegment"),
        Ref("BareFunctionSegment"),
    ),
    ReferenceDefinitionGrammar=Sequence(
        "REFERENCES",
        Ref("TableReferenceSegment"),
        # Foreign columns making up FOREIGN KEY constraint
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Sequence(
            "MATCH",
            OneOf(
                "FULL",
                "PARTIAL",
                "SIMPLE",
            ),
            optional=True,
        ),
        AnySetOf(
            # ON DELETE clause, e.g. ON DELETE NO ACTION
            Sequence(
                "ON",
                "DELETE",
                Ref("ReferentialActionGrammar"),
            ),
            # ON UPDATE clause, e.g. ON UPDATE SET NULL
            Sequence(
                "ON",
                "UPDATE",
                Ref("ReferentialActionGrammar"),
            ),
        ),
    ),
    TrimParametersGrammar=OneOf("BOTH", "LEADING", "TRAILING"),
    DefaultValuesGrammar=Sequence("DEFAULT", "VALUES"),
    ObjectReferenceDelimiterGrammar=OneOf(
        Ref("DotSegment"),
        # NOTE: The double dot syntax allows for default values.
        Sequence(Ref("DotSegment"), Ref("DotSegment")),
    ),
    ObjectReferenceTerminatorGrammar=OneOf(
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
        Ref("JoinLikeClauseGrammar"),
        BracketedSegment,
    ),
    AlterTableOptionsGrammar=OneOf(
        # Table options
        Sequence(
            Ref("ParameterNameSegment"),
            Ref("EqualsSegment", optional=True),
            OneOf(Ref("LiteralGrammar"), Ref("NakedIdentifierSegment")),
        ),
        # Add things
        Sequence(
            OneOf("ADD", "MODIFY"),
            Ref.keyword("COLUMN", optional=True),
            Ref("ColumnDefinitionSegment"),
            OneOf(
                Sequence(OneOf("FIRST", "AFTER"), Ref("ColumnReferenceSegment")),
                # Bracketed Version of the same
                Ref("BracketedColumnReferenceListGrammar"),
                optional=True,
            ),
        ),
        # Rename
        Sequence(
            "RENAME",
            OneOf("AS", "TO", optional=True),
            Ref("TableReferenceSegment"),
        ),
    ),
    OrderNoOrderGrammar=OneOf("ORDER", "NOORDER"),
    ColumnsExpressionNameGrammar=Nothing(),
    # Uses grammar for LT06 support
    ColumnsExpressionGrammar=Nothing(),
)


class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    match_grammar = Delimited(
        Ref("StatementSegment"),
        delimiter=AnyNumberOf(Ref("DelimiterGrammar"), min_times=1),
        allow_gaps=True,
        allow_trailing=True,
    )

    def get_table_references(self) -> Set[str]:
        """Use parsed tree to extract table references."""
        references = set()
        for stmt in self.get_children("statement"):
            stmt = cast(StatementSegment, stmt)
            references |= stmt.get_table_references()
        return references


class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment."""

    type = "interval_expression"
    match_grammar: Matchable = Sequence(
        "INTERVAL",
        OneOf(
            # The Numeric Version
            Sequence(
                Ref("NumericLiteralSegment"),
                OneOf(Ref("QuotedLiteralSegment"), Ref("DatetimeUnitSegment")),
            ),
            # The String version
            Ref("QuotedLiteralSegment"),
            # Combine version
            Sequence(
                Ref("QuotedLiteralSegment"),
                OneOf(Ref("QuotedLiteralSegment"), Ref("DatetimeUnitSegment")),
            ),
        ),
    )


class ArrayTypeSegment(BaseSegment):
    """Prefix for array literals specifying the type.

    Often "ARRAY" or "ARRAY<type>"
    """

    type = "array_type"
    match_grammar: Matchable = Nothing()


class SizedArrayTypeSegment(BaseSegment):
    """Array type with a size."""

    type = "sized_array_type"
    match_grammar = Sequence(
        Ref("ArrayTypeSegment"),
        Ref("ArrayAccessorSegment"),
    )


class ArrayLiteralSegment(BaseSegment):
    """An array literal segment.

    An unqualified array literal:
    e.g. [1, 2, 3]
    """

    type = "array_literal"
    match_grammar: Matchable = Bracketed(
        Delimited(Ref("BaseExpressionElementGrammar"), optional=True),
        bracket_type="square",
    )


class TypedArrayLiteralSegment(BaseSegment):
    """An array literal segment."""

    type = "typed_array_literal"
    match_grammar: Matchable = Sequence(
        Ref("ArrayTypeSegment"),
        Ref("ArrayLiteralSegment"),
    )


class StructTypeSegment(BaseSegment):
    """Expression to construct a STRUCT datatype.

    (Used in BigQuery for example)
    """

    type = "struct_type"
    match_grammar: Matchable = Nothing()


class StructLiteralSegment(BaseSegment):
    """An array literal segment.

    An unqualified struct literal:
    e.g. (1, 2 as foo, 3)

    NOTE: This rarely exists without a preceding type
    and exists mostly for structural & layout reasons.
    """

    type = "struct_literal"
    match_grammar: Matchable = Bracketed(
        Delimited(
            Sequence(
                Ref("BaseExpressionElementGrammar"),
                Ref("AliasExpressionSegment", optional=True),
            ),
        ),
    )


class TypedStructLiteralSegment(BaseSegment):
    """An array literal segment."""

    type = "typed_struct_literal"
    match_grammar: Matchable = Sequence(
        Ref("StructTypeSegment"),
        Ref("StructLiteralSegment"),
    )


class EmptyStructLiteralBracketsSegment(BaseSegment):
    """An empty struct literal segment - `()`.

    NOTE: This is only to set the right type so spacing rules are applied correctly.
    """

    type = "struct_literal"
    match_grammar: Matchable = Bracketed()


class EmptyStructLiteralSegment(BaseSegment):
    """An empty array literal segment - `STRUCT()`."""

    type = "typed_struct_literal"
    match_grammar: Matchable = Sequence(
        Ref("StructTypeSegment"),
        Ref("EmptyStructLiteralBracketsSegment"),
    )


class ObjectLiteralSegment(BaseSegment):
    """An object literal segment."""

    type = "object_literal"
    match_grammar: Matchable = Bracketed(
        Delimited(
            Ref("ObjectLiteralElementSegment"),
            optional=True,
        ),
        bracket_type="curly",
    )


class ObjectLiteralElementSegment(BaseSegment):
    """An object literal element segment."""

    type = "object_literal_element"
    match_grammar: Matchable = Sequence(
        Ref("QuotedLiteralSegment"),
        Ref("ColonSegment"),
        Ref("BaseExpressionElementGrammar"),
    )


class TimeZoneGrammar(BaseSegment):
    """Casting to Time Zone."""

    type = "time_zone_grammar"
    match_grammar = AnyNumberOf(
        Sequence("AT", "TIME", "ZONE", Ref("ExpressionSegment")),
    )


class BracketedArguments(BaseSegment):
    """A series of bracketed arguments.

    e.g. the bracketed part of numeric(1, 3)
    """

    type = "bracketed_arguments"
    match_grammar = Bracketed(
        # The brackets might be empty for some cases...
        Delimited(Ref("LiteralGrammar"), optional=True),
    )


class DatatypeSegment(BaseSegment):
    """A data type segment.

    Supports timestamp with(out) time zone. Doesn't currently support intervals.
    """

    type = "data_type"
    match_grammar: Matchable = OneOf(
        Sequence(
            OneOf("TIME", "TIMESTAMP"),
            Bracketed(Ref("NumericLiteralSegment"), optional=True),
            Sequence(OneOf("WITH", "WITHOUT"), "TIME", "ZONE", optional=True),
        ),
        Sequence(
            "DOUBLE",
            "PRECISION",
        ),
        Sequence(
            OneOf(
                Sequence(
                    OneOf("CHARACTER", "BINARY"),
                    OneOf("VARYING", Sequence("LARGE", "OBJECT")),
                ),
                Sequence(
                    # Some dialects allow optional qualification of data types with
                    # schemas
                    Sequence(
                        Ref("SingleIdentifierGrammar"),
                        Ref("DotSegment"),
                        allow_gaps=False,
                        optional=True,
                    ),
                    Ref("DatatypeIdentifierSegment"),
                    allow_gaps=False,
                ),
            ),
            # There may be no brackets for some data types
            Ref("BracketedArguments", optional=True),
            OneOf(
                "UNSIGNED",  # UNSIGNED MySQL
                Ref("CharCharacterSetGrammar"),
                optional=True,
            ),
        ),
    )


# hookpoint
ansi_dialect.add(CharCharacterSetGrammar=Nothing())


class ObjectReferenceSegment(BaseSegment):
    """A reference to an object."""

    type = "object_reference"
    # match grammar (don't allow whitespace)
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=Ref("ObjectReferenceDelimiterGrammar"),
        terminators=[Ref("ObjectReferenceTerminatorGrammar")],
        allow_gaps=False,
    )

    class ObjectReferencePart(NamedTuple):
        """Details about a table alias."""

        part: str  # Name of the part
        # Segment(s) comprising the part. Usuaully just one segment, but could
        # be multiple in dialects (e.g. BigQuery) that support unusual
        # characters in names (e.g. "-")
        segments: List[BaseSegment]

    @classmethod
    def _iter_reference_parts(cls, elem) -> Generator[ObjectReferencePart, None, None]:
        """Extract the elements of a reference and yield."""
        # trim on quotes and split out any dots.
        for part in elem.raw_trimmed().split("."):
            yield cls.ObjectReferencePart(part, [elem])

    def iter_raw_references(self) -> Generator[ObjectReferencePart, None, None]:
        """Generate a list of reference strings and elements.

        Each reference is an ObjectReferencePart. If some are split, then a
        segment may appear twice, but the substring will only appear once.
        """
        # Extract the references from those identifiers (because some may be quoted)
        for elem in self.recursive_crawl("identifier"):
            yield from self._iter_reference_parts(elem)

    def is_qualified(self) -> bool:
        """Return if there is more than one element to the reference."""
        return len(list(self.iter_raw_references())) > 1

    def qualification(self) -> str:
        """Return the qualification type of this reference."""
        return "qualified" if self.is_qualified() else "unqualified"

    class ObjectReferenceLevel(Enum):
        """Labels for the "levels" of a reference.

        Note: Since SQLFluff does not have access to database catalog
        information, interpreting references will often be ambiguous.
        Typical example: The first part *may* refer to a schema, but that is
        almost always optional if referring to an object in some default or
        currently "active" schema. For this reason, use of this enum is optional
        and intended mainly to clarify the intent of the code -- no guarantees!
        Additionally, the terminology may vary by dialect, e.g. in BigQuery,
        "project" would be a more accurate term than "schema".
        """

        OBJECT = 1
        TABLE = 2
        SCHEMA = 3

    def extract_possible_references(
        self, level: Union[ObjectReferenceLevel, int]
    ) -> List[ObjectReferencePart]:
        """Extract possible references of a given level.

        "level" may be (but is not required to be) a value from the
        ObjectReferenceLevel enum defined above.

        NOTE: The base implementation here returns at most one part, but
        dialects such as BigQuery that support nesting (e.g. STRUCT) may return
        multiple reference parts.
        """
        level = self._level_to_int(level)
        refs = list(self.iter_raw_references())
        if len(refs) >= level:
            return [refs[-level]]
        return []

    def extract_possible_multipart_references(
        self, levels: List[Union[ObjectReferenceLevel, int]]
    ) -> List[Tuple[ObjectReferencePart, ...]]:
        """Extract possible multipart references, e.g. schema.table."""
        levels_tmp = [self._level_to_int(level) for level in levels]
        min_level = min(levels_tmp)
        max_level = max(levels_tmp)
        refs = list(self.iter_raw_references())
        if len(refs) >= max_level:
            return [tuple(refs[-max_level : 1 - min_level])]
        return []

    @staticmethod
    def _level_to_int(level: Union[ObjectReferenceLevel, int]) -> int:
        # If it's an ObjectReferenceLevel, get the value. Otherwise, assume it's
        # an int.
        level = getattr(level, "value", level)
        assert isinstance(level, int)
        return level


class TableReferenceSegment(ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias."""

    type = "table_reference"


class SchemaReferenceSegment(ObjectReferenceSegment):
    """A reference to a schema."""

    type = "schema_reference"


class DatabaseReferenceSegment(ObjectReferenceSegment):
    """A reference to a database."""

    type = "database_reference"


class IndexReferenceSegment(ObjectReferenceSegment):
    """A reference to an index."""

    type = "index_reference"


class CollationReferenceSegment(ObjectReferenceSegment):
    """A reference to a collation."""

    type = "collation_reference"
    # Some dialects like PostgreSQL want an identifier only, and quoted
    # literals aren't allowed.  Other dialects like Snowflake only accept
    # a quoted string literal.  We'll be a little overly-permissive and
    # accept either... it shouldn't be too greedy since this segment generally
    # occurs only in a Sequence after the "COLLATE" keyword.
    match_grammar: Matchable = OneOf(
        Ref("QuotedLiteralSegment"),
        Delimited(
            Ref("SingleIdentifierGrammar"),
            delimiter=Ref("ObjectReferenceDelimiterGrammar"),
            terminators=[Ref("ObjectReferenceTerminatorGrammar")],
            allow_gaps=False,
        ),
    )


class RoleReferenceSegment(ObjectReferenceSegment):
    """A reference to a role, user, or account."""

    type = "role_reference"
    match_grammar: Matchable = Ref("SingleIdentifierGrammar")


class TablespaceReferenceSegment(ObjectReferenceSegment):
    """A reference to a tablespace."""

    type = "tablespace_reference"


class ExtensionReferenceSegment(ObjectReferenceSegment):
    """A reference to an extension."""

    type = "extension_reference"


class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias."""

    type = "column_reference"


class SequenceReferenceSegment(ObjectReferenceSegment):
    """A reference to a sequence."""

    type = "sequence_reference"


class TagReferenceSegment(ObjectReferenceSegment):
    """A reference to a tag."""

    type = "tag_reference"


class TriggerReferenceSegment(ObjectReferenceSegment):
    """A reference to a trigger."""

    type = "trigger_reference"


class SingleIdentifierListSegment(BaseSegment):
    """A comma delimited list of identifiers."""

    type = "identifier_list"
    match_grammar: Matchable = Delimited(Ref("SingleIdentifierGrammar"))


class ArrayAccessorSegment(BaseSegment):
    """An array accessor e.g. [3:4]."""

    type = "array_accessor"
    match_grammar: Matchable = Bracketed(
        Delimited(
            OneOf(Ref("NumericLiteralSegment"), Ref("ExpressionSegment")),
            delimiter=Ref("SliceSegment"),
        ),
        bracket_type="square",
        parse_mode=ParseMode.GREEDY,
    )


class AliasedObjectReferenceSegment(BaseSegment):
    """A reference to an object with an `AS` clause."""

    type = "object_reference"
    match_grammar: Matchable = Sequence(
        Ref("ObjectReferenceSegment"), Ref("AliasExpressionSegment")
    )


ansi_dialect.add(
    # This is a hook point to allow subclassing for other dialects
    AliasedTableReferenceGrammar=Sequence(
        Ref("TableReferenceSegment"), Ref("AliasExpressionSegment")
    )
)


class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    """

    type = "alias_expression"
    match_grammar: Matchable = Sequence(
        Indent,
        Ref.keyword("AS", optional=True),
        OneOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                # Column alias in VALUES clause
                Bracketed(Ref("SingleIdentifierListSegment"), optional=True),
            ),
            Ref("SingleQuotedIdentifierSegment"),
        ),
        Dedent,
    )


class ShorthandCastSegment(BaseSegment):
    """A casting operation using '::'."""

    type = "cast_expression"
    match_grammar: Matchable = Sequence(
        OneOf(
            Ref("Expression_D_Grammar"),
            Ref("CaseExpressionSegment"),
        ),
        AnyNumberOf(
            Sequence(
                Ref("CastOperatorSegment"),
                Ref("DatatypeSegment"),
                Ref("TimeZoneGrammar", optional=True),
            ),
            min_times=1,
        ),
    )


class QualifiedNumericLiteralSegment(BaseSegment):
    """A numeric literal with one + or - sign preceding.

    The qualified numeric literal is a compound of a raw
    literal and a plus/minus sign. We do it this way rather
    than at the lexing step because the lexer doesn't deal
    well with ambiguity.
    """

    type = "numeric_literal"
    match_grammar: Matchable = Sequence(
        Ref("SignedSegmentGrammar"),
        Ref("NumericLiteralSegment"),
    )


class AggregateOrderByClause(BaseSegment):
    """An order by clause for an aggregate fucntion.

    Defined as a class to allow a specific type for rule AM06
    """

    type = "aggregate_order_by"
    match_grammar: Matchable = Ref("OrderByClauseSegment")


ansi_dialect.add(
    # FunctionContentsExpressionGrammar intended as a hook to override
    # in other dialects.
    FunctionContentsExpressionGrammar=Ref("ExpressionSegment"),
    FunctionContentsGrammar=AnyNumberOf(
        Ref("ExpressionSegment"),
        # A Cast-like function
        Sequence(Ref("ExpressionSegment"), "AS", Ref("DatatypeSegment")),
        # Trim function
        Sequence(
            Ref("TrimParametersGrammar"),
            Ref("ExpressionSegment", optional=True, exclude=Ref.keyword("FROM")),
            "FROM",
            Ref("ExpressionSegment"),
        ),
        # An extract-like or substring-like function
        Sequence(
            OneOf(Ref("DatetimeUnitSegment"), Ref("ExpressionSegment")),
            "FROM",
            Ref("ExpressionSegment"),
        ),
        Sequence(
            # Allow an optional distinct keyword here.
            Ref.keyword("DISTINCT", optional=True),
            OneOf(
                # Most functions will be using the delimited route
                # but for COUNT(*) or similar we allow the star segment
                # here.
                Ref("StarSegment"),
                Delimited(Ref("FunctionContentsExpressionGrammar")),
            ),
        ),
        Ref(
            "AggregateOrderByClause"
        ),  # used by string_agg (postgres), group_concat (exasol),listagg (snowflake)..
        Sequence(Ref.keyword("SEPARATOR"), Ref("LiteralGrammar")),
        # like a function call: POSITION ( 'QL' IN 'SQL')
        Sequence(
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
            "IN",
            OneOf(
                Ref("QuotedLiteralSegment"),
                Ref("SingleIdentifierGrammar"),
                Ref("ColumnReferenceSegment"),
            ),
        ),
        Ref("IgnoreRespectNullsGrammar"),
        Ref("IndexColumnDefinitionSegment"),
        Ref("EmptyStructLiteralSegment"),
    ),
    PostFunctionGrammar=OneOf(
        # Optional OVER suffix for window functions.
        # This is supported in bigquery & postgres (and its derivatives)
        # and so is included here for now.
        Ref("OverClauseSegment"),
        # Filter clause supported by both Postgres and SQLite
        Ref("FilterClauseGrammar"),
    ),
)


class OverClauseSegment(BaseSegment):
    """An OVER clause for window functions."""

    type = "over_clause"
    match_grammar: Matchable = Sequence(
        Indent,
        Ref("IgnoreRespectNullsGrammar", optional=True),
        "OVER",
        OneOf(
            Ref("SingleIdentifierGrammar"),  # Window name
            Bracketed(
                Ref("WindowSpecificationSegment", optional=True),
                parse_mode=ParseMode.GREEDY,
            ),
        ),
        Dedent,
    )


class WindowSpecificationSegment(BaseSegment):
    """Window specification within OVER(...)."""

    type = "window_specification"
    match_grammar: Matchable = Sequence(
        Ref(
            "SingleIdentifierGrammar",
            optional=True,
            exclude=OneOf(Ref.keyword("PARTITION"), Ref.keyword("ORDER")),
        ),  # "Base" window name
        Ref("PartitionClauseSegment", optional=True),
        Ref("OrderByClauseSegment", optional=True),
        Ref("FrameClauseSegment", optional=True),
        optional=True,
    )


class FunctionNameSegment(BaseSegment):
    """Function name, including any prefix bits, e.g. project or schema."""

    type = "function_name"
    match_grammar: Matchable = Sequence(
        # Project name, schema identifier, etc.
        AnyNumberOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
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
        allow_gaps=False,
    )


class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now,
    we treat them the same because they look the same
    for our purposes.
    """

    type = "function"
    match_grammar: Matchable = OneOf(
        Sequence(
            # Treat functions which take date parts separately
            # So those functions parse date parts as DatetimeUnitSegment
            # rather than identifiers.
            Sequence(
                Ref("DatePartFunctionNameSegment"),
                Bracketed(
                    Delimited(
                        Ref("DatetimeUnitSegment"),
                        Ref(
                            "FunctionContentsGrammar",
                            # The brackets might be empty for some functions...
                            optional=True,
                        ),
                    ),
                    parse_mode=ParseMode.GREEDY,
                ),
            ),
        ),
        Ref("ColumnsExpressionGrammar"),
        Sequence(
            Sequence(
                Ref(
                    "FunctionNameSegment",
                    exclude=OneOf(
                        Ref("DatePartFunctionNameSegment"),
                        Ref("ColumnsExpressionFunctionNameSegment"),
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
            Ref("PostFunctionGrammar", optional=True),
        ),
    )


class ColumnsExpressionFunctionNameSegment(BaseSegment):
    """COLUMNS function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar: Matchable = Ref("ColumnsExpressionNameGrammar")


class ColumnsExpressionFunctionContentsSegment(BaseSegment):
    """Columns expression in a select statement.

    From DuckDB:
    https://duckdb.org/docs/sql/expressions/star#columns-expression
    """

    type = "columns_expression"
    match_grammar: Matchable = Nothing()


class PartitionClauseSegment(BaseSegment):
    """A `PARTITION BY` for window functions."""

    type = "partitionby_clause"
    match_grammar: Matchable = Sequence(
        "PARTITION",
        "BY",
        Indent,
        # Brackets are optional in a partition by statement
        OptionallyBracketed(Delimited(Ref("ExpressionSegment"))),
        Dedent,
    )


class FrameClauseSegment(BaseSegment):
    """A frame clause for window functions.

    https://docs.oracle.com/cd/E17952_01/mysql-8.0-en/window-functions-frames.html
    """

    type = "frame_clause"

    _frame_extent = OneOf(
        Sequence("CURRENT", "ROW"),
        Sequence(
            OneOf(
                Ref("NumericLiteralSegment"),
                Sequence("INTERVAL", Ref("QuotedLiteralSegment")),
                "UNBOUNDED",
            ),
            OneOf("PRECEDING", "FOLLOWING"),
        ),
    )

    match_grammar: Matchable = Sequence(
        Ref("FrameClauseUnitGrammar"),
        OneOf(_frame_extent, Sequence("BETWEEN", _frame_extent, "AND", _frame_extent)),
    )


ansi_dialect.add(
    # This is a hook point to allow subclassing for other dialects
    PostTableExpressionGrammar=Nothing()
)


class FromExpressionElementSegment(BaseSegment):
    """A table expression."""

    type = "from_expression_element"

    _base_from_expression_element = Sequence(
        Ref("PreTableFunctionKeywordsGrammar", optional=True),
        OptionallyBracketed(Ref("TableExpressionSegment")),
        Ref(
            "AliasExpressionSegment",
            exclude=OneOf(
                Ref("FromClauseTerminatorGrammar"),
                Ref("SamplingExpressionSegment"),
                Ref("JoinLikeClauseGrammar"),
                Ref("JoinClauseSegment"),
            ),
            optional=True,
        ),
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#flattening_arrays
        Sequence("WITH", "OFFSET", Ref("AliasExpressionSegment"), optional=True),
        Ref("SamplingExpressionSegment", optional=True),
        Ref("PostTableExpressionGrammar", optional=True),
    )

    match_grammar: Matchable = OneOf(
        _base_from_expression_element,
        Bracketed(
            Sequence(
                _base_from_expression_element,
                AnyNumberOf(Ref("JoinClauseSegment")),
            ),
        ),
    )

    def get_eventual_alias(self) -> AliasInfo:
        """Return the eventual table name referred to by this table expression.

        Returns:
            :obj:`tuple` of (:obj:`str`, :obj:`BaseSegment`, :obj:`bool`) containing
                a string representation of the alias, a reference to the
                segment containing it, and whether it's an alias.

        """
        # Get any table expressions
        tbl_expression = self.get_child("table_expression")
        if not tbl_expression:  # pragma: no cover
            _bracketed = self.get_child("bracketed")
            if _bracketed:
                tbl_expression = _bracketed.get_child("table_expression")
        # For TSQL nested, bracketed tables get the first table as reference
        if tbl_expression and not tbl_expression.get_child("object_reference"):
            _bracketed = tbl_expression.get_child("bracketed")
            if _bracketed:
                tbl_expression = _bracketed.get_child("table_expression")

        # Work out the references
        ref: Optional[ObjectReferenceSegment] = None
        if tbl_expression:
            _ref = tbl_expression.get_child("object_reference")
            if _ref:
                ref = cast(ObjectReferenceSegment, _ref)

        # Handle any aliases
        alias_expression = self.get_child("alias_expression")
        if alias_expression:
            # If it has an alias, return that
            segment = alias_expression.get_child("identifier")
            if segment:
                return AliasInfo(
                    segment.raw, segment, True, self, alias_expression, ref
                )

        # If not return the object name (or None if there isn't one)
        if ref:
            references: List = list(ref.iter_raw_references())
            # Return the last element of the reference.
            if references:
                penultimate_ref: ObjectReferenceSegment.ObjectReferencePart = (
                    references[-1]
                )
                return AliasInfo(
                    penultimate_ref.part,
                    penultimate_ref.segments[0],
                    False,
                    self,
                    None,
                    ref,
                )
        # No references or alias
        return AliasInfo(
            "",
            None,
            False,
            self,
            None,
            ref,
        )


class FromExpressionSegment(BaseSegment):
    """A from expression segment."""

    type = "from_expression"
    match_grammar: Matchable = OptionallyBracketed(
        Sequence(
            Indent,
            OneOf(
                # check first for MLTableExpression,
                # because of possible FunctionSegment in
                # MainTableExpression
                Ref("MLTableExpressionSegment"),
                Ref("FromExpressionElementSegment"),
                Bracketed(Ref("FromExpressionSegment")),
                terminators=[Sequence("ORDER", "BY"), Sequence("GROUP", "BY")],
            ),
            Dedent,
            Conditional(Indent, indented_joins=True),
            AnyNumberOf(
                Sequence(
                    OneOf(Ref("JoinClauseSegment"), Ref("JoinLikeClauseGrammar")),
                ),
                optional=True,
                terminators=[Sequence("ORDER", "BY"), Sequence("GROUP", "BY")],
            ),
            Conditional(Dedent, indented_joins=True),
        )
    )


class TableExpressionSegment(BaseSegment):
    """The main table expression e.g. within a FROM clause."""

    type = "table_expression"
    match_grammar: Matchable = OneOf(
        Ref("ValuesClauseSegment"),
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("TableReferenceSegment"),
        # Nested Selects
        Bracketed(Ref("SelectableGrammar")),
        Bracketed(Ref("MergeStatementSegment")),
    )


class WildcardIdentifierSegment(ObjectReferenceSegment):
    """Any identifier of the form a.b.*.

    This inherits iter_raw_references from the
    ObjectReferenceSegment.
    """

    type = "wildcard_identifier"
    match_grammar: Matchable = Sequence(
        # *, blah.*, blah.blah.*, etc.
        AnyNumberOf(
            OneOf(
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    Ref("ObjectReferenceDelimiterGrammar"),
                    allow_gaps=True,
                ),
                Sequence(
                    Ref("StarSegment"),
                    Ref("DotSegment"),
                ),
            )
        ),
        Ref("StarSegment"),
        allow_gaps=False,
    )

    def iter_raw_references(self):
        """Generate a list of reference strings and elements.

        Each element is a tuple of (str, segment). If some are
        split, then a segment may appear twice, but the substring
        will only appear once.
        """
        # Extract the references from those identifiers (because some may be quoted)
        for elem in self.recursive_crawl("identifier", "star"):
            yield from self._iter_reference_parts(elem)


class WildcardExpressionSegment(BaseSegment):
    """A star (*) expression for a SELECT clause.

    This is separate from the identifier to allow for
    some dialects which extend this logic to allow
    REPLACE, EXCEPT or similar clauses e.g. BigQuery.
    """

    type = "wildcard_expression"
    match_grammar: Matchable = Sequence(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardIdentifierSegment")
    )


class SelectClauseElementSegment(BaseSegment):
    """An element in the targets of a select statement."""

    type = "select_clause_element"
    # Important to split elements before parsing, otherwise debugging is really hard.

    match_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            Ref("BaseExpressionElementGrammar"),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )

    def get_alias(self) -> Optional[ColumnAliasInfo]:
        """Get info on alias within SELECT clause element."""
        alias_expression_segment = next(self.recursive_crawl("alias_expression"), None)
        if alias_expression_segment is None:
            # Return None if no alias expression is found.
            return None

        alias_identifier_segment = next(
            (s for s in alias_expression_segment.segments if s.is_type("identifier")),
            None,
        )

        if alias_identifier_segment is None:
            # Return None if no alias identifier expression is found.
            # Happened in the past due to bad syntax
            return None  # pragma: no cover

        # Get segment being aliased.
        aliased_segment = next(
            s
            for s in self.segments
            if not s.is_whitespace and not s.is_meta and s != alias_expression_segment
        )

        # Find all the columns being aliased.
        column_reference_segments = []
        if aliased_segment.is_type("column_reference"):
            column_reference_segments.append(aliased_segment)
        else:
            column_reference_segments.extend(
                aliased_segment.recursive_crawl("column_reference")
            )

        return ColumnAliasInfo(
            alias_identifier_name=alias_identifier_segment.raw,
            aliased_segment=aliased_segment,
            column_reference_segments=column_reference_segments,
        )


class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar: Matchable = OneOf(
        "DISTINCT",
        "ALL",
    )


class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement."""

    type = "select_clause"
    match_grammar: Matchable = Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
            allow_trailing=True,
        ),
        Dedent,
        terminators=[Ref("SelectClauseTerminatorGrammar")],
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
    )


class JoinClauseSegment(BaseSegment):
    """Any number of join clauses, including the `JOIN` keyword."""

    type = "join_clause"
    match_grammar: Matchable = OneOf(
        # NB These qualifiers are optional
        Sequence(
            Ref("ConditionalJoinKeywordsGrammar", optional=True),
            Ref("JoinKeywordsGrammar"),
            Indent,
            Ref("FromExpressionElementSegment"),
            AnyNumberOf(Ref("NestedJoinGrammar")),
            Dedent,
            Sequence(
                # Using nested sequence here so we only get the indents
                # if we also have content.
                Conditional(Indent, indented_using_on=True),
                # NB: this is optional
                OneOf(
                    # ON clause
                    Ref("JoinOnConditionSegment"),
                    # USING clause
                    Ref("JoinUsingConditionGrammar"),
                    # Unqualified joins *are* allowed. They just might not
                    # be a good idea.
                ),
                Conditional(Dedent, indented_using_on=True),
                optional=True,
            ),
        ),
        # Note NATURAL joins do not support Join conditions
        Sequence(
            Ref("UnconditionalJoinKeywordsGrammar"),
            Ref("JoinKeywordsGrammar"),
            Indent,
            Ref("FromExpressionElementSegment"),
            Dedent,
        ),
        # Sometimes, a natural join might already include the keyword
        Sequence(
            Ref("ExtendedNaturalJoinKeywordsGrammar"),
            Indent,
            Ref("FromExpressionElementSegment"),
            Dedent,
        ),
    )

    def get_eventual_aliases(self) -> List[Tuple[BaseSegment, AliasInfo]]:
        """Return the eventual table name referred to by this join clause."""
        buff = []

        from_expression = self.get_child("from_expression_element")
        # As per grammar above, there will always be a FromExpressionElementSegment
        assert from_expression
        alias: AliasInfo = cast(
            FromExpressionElementSegment, from_expression
        ).get_eventual_alias()
        # Only append if non-null. A None reference, may
        # indicate a generator expression or similar.
        if alias:
            buff.append((from_expression, alias))

        # In some dialects, like TSQL, join clauses can have nested join clauses
        # recurse into them - but not if part of a sub-select statement (see #3144)
        for join_clause in self.recursive_crawl(
            "join_clause", no_recursive_seg_type="select_statement"
        ):
            if join_clause is self:
                # If the starting segment itself matches the list of types we're
                # searching for, recursive_crawl() will return it. Skip that.
                continue
            aliases: List[Tuple[BaseSegment, AliasInfo]] = cast(
                JoinClauseSegment, join_clause
            ).get_eventual_aliases()
            # Only append if non-null. A None reference, may
            # indicate a generator expression or similar.
            if aliases:
                buff = buff + aliases
        return buff


class JoinOnConditionSegment(BaseSegment):
    """The `ON` condition within a `JOIN` clause."""

    type = "join_on_condition"
    match_grammar: Matchable = Sequence(
        "ON",
        Conditional(ImplicitIndent, indented_on_contents=True),
        OptionallyBracketed(Ref("ExpressionSegment")),
        Conditional(Dedent, indented_on_contents=True),
    )


ansi_dialect.add(
    # This is a hook point to allow subclassing for other dialects
    JoinLikeClauseGrammar=Nothing(),
)


class FromClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT`.

    NOTE: this is a delimited set of table expressions, with a variable
    number of optional join clauses with those table expressions. The
    delimited aspect is the higher of the two such that the following is
    valid (albeit unusual):

    ```
    SELECT *
    FROM a JOIN b, c JOIN d
    ```
    """

    type = "from_clause"
    match_grammar: Matchable = Sequence(
        "FROM",
        Delimited(
            Ref("FromExpressionSegment"),
        ),
    )

    def get_eventual_aliases(self) -> List[Tuple[BaseSegment, AliasInfo]]:
        """List the eventual aliases of this from clause.

        Comes as a list of tuples (table expr, tuple (string, segment, bool)).
        """
        buff: List[Tuple[BaseSegment, AliasInfo]] = []
        direct_table_children = []
        join_clauses = []

        for from_expression in self.get_children("from_expression"):
            direct_table_children += from_expression.get_children(
                "from_expression_element"
            )
            join_clauses += from_expression.get_children("join_clause")

        # Iterate through the potential sources of aliases
        for clause in direct_table_children:
            alias: AliasInfo = cast(
                FromExpressionElementSegment, clause
            ).get_eventual_alias()
            # Only append if non-null. A None reference, may
            # indicate a generator expression or similar.
            table_expr = (
                clause
                if clause in direct_table_children
                else clause.get_child("from_expression_element")
            )
            if alias:
                assert table_expr
                buff.append((table_expr, alias))
        for clause in join_clauses:
            aliases: List[Tuple[BaseSegment, AliasInfo]] = cast(
                JoinClauseSegment, clause
            ).get_eventual_aliases()
            # Only append if non-null. A None reference, may
            # indicate a generator expression or similar.
            if aliases:
                buff = buff + aliases
        return buff


class WhenClauseSegment(BaseSegment):
    """A 'WHEN' clause for a 'CASE' statement."""

    type = "when_clause"
    match_grammar: Matchable = Sequence(
        "WHEN",
        # NOTE: The nested sequence here is to ensure the correct
        # placement of the meta segments when templated elements
        # are present.
        # https://github.com/sqlfluff/sqlfluff/issues/3988
        Sequence(
            ImplicitIndent,
            Ref("ExpressionSegment"),
            Dedent,
        ),
        Conditional(Indent, indented_then=True),
        "THEN",
        Conditional(ImplicitIndent, indented_then_contents=True),
        Ref("ExpressionSegment"),
        Conditional(Dedent, indented_then_contents=True),
        Conditional(Dedent, indented_then=True),
    )


class ElseClauseSegment(BaseSegment):
    """An 'ELSE' clause for a 'CASE' statement."""

    type = "else_clause"
    match_grammar: Matchable = Sequence(
        "ELSE", ImplicitIndent, Ref("ExpressionSegment"), Dedent
    )


class CaseExpressionSegment(BaseSegment):
    """A `CASE WHEN` clause."""

    type = "case_expression"
    match_grammar: Matchable = OneOf(
        Sequence(
            "CASE",
            ImplicitIndent,
            AnyNumberOf(
                Ref("WhenClauseSegment"),
                reset_terminators=True,
                terminators=[Ref.keyword("ELSE"), Ref.keyword("END")],
            ),
            Ref(
                "ElseClauseSegment",
                optional=True,
                reset_terminators=True,
                terminators=[Ref.keyword("END")],
            ),
            Dedent,
            "END",
        ),
        Sequence(
            "CASE",
            Ref("ExpressionSegment"),
            ImplicitIndent,
            AnyNumberOf(
                Ref("WhenClauseSegment"),
                reset_terminators=True,
                terminators=[Ref.keyword("ELSE"), Ref.keyword("END")],
            ),
            Ref(
                "ElseClauseSegment",
                optional=True,
                reset_terminators=True,
                terminators=[Ref.keyword("END")],
            ),
            Dedent,
            "END",
        ),
        terminators=[Ref("CommaSegment"), Ref("BinaryOperatorGrammar")],
    )


ansi_dialect.add(
    # Expression_A_Grammar
    # https://www.cockroachlabs.com/docs/v20.2/sql-grammar.html#a_expr
    # The upstream grammar is defined recursively, which if implemented naively
    # will cause SQLFluff to overflow the stack from recursive function calls.
    # To work around this, the a_expr grammar is reworked a bit into sub-grammars
    # that effectively provide tail recursion.
    Expression_A_Unary_Operator_Grammar=OneOf(
        # This grammar corresponds to the unary operator portion of the initial
        # recursive block on the Cockroach Labs a_expr grammar.  It includes the
        # unary operator matching sub-block, but not the recursive call to a_expr.
        Ref(
            "SignedSegmentGrammar",
            exclude=Sequence(Ref("QualifiedNumericLiteralSegment")),
        ),
        Ref("TildeSegment"),
        Ref("NotOperatorGrammar"),
        # used in CONNECT BY clauses (EXASOL, Snowflake, Postgres...)
        "PRIOR",
    ),
    Tail_Recurse_Expression_A_Grammar=Sequence(
        # This should be used instead of a recursive call to Expression_A_Grammar
        # whenever the repeating element in Expression_A_Grammar makes a recursive
        # call to itself at the _end_.  If it's in the middle then you still need
        # to recurse into Expression_A_Grammar normally.
        AnyNumberOf(
            Ref("Expression_A_Unary_Operator_Grammar"),
            terminators=[Ref("BinaryOperatorGrammar")],
        ),
        Ref("Expression_C_Grammar"),
    ),
    Expression_A_Grammar=Sequence(
        # Grammar always starts with optional unary operator, plus c_expr.  This
        # section must always match the tail recurse grammar.
        Ref("Tail_Recurse_Expression_A_Grammar"),
        # As originally pictured in the diagram, the grammar then repeats itself
        # for any number of times with a loop.
        AnyNumberOf(
            OneOf(
                # This corresponds to the big repeating block in the diagram that
                # has like dozens and dozens of possibilities.  Some of them are
                # recursive.  If the item __ends__ with a recursive call to "a_expr",
                # use Ref("Tail_Recurse_Expression_A_Grammar") instead so that the
                # stack depth can be minimized.  If the item has a recursive call
                # in the middle of the expression, you'll need to recurse
                # Expression_A_Grammar normally.
                #
                # We need to add a lot more here...
                Sequence(
                    Sequence(
                        Ref.keyword("NOT", optional=True),
                        Ref("LikeGrammar"),
                    ),
                    Ref("Expression_A_Grammar"),
                    Sequence(
                        Ref.keyword("ESCAPE"),
                        Ref("Tail_Recurse_Expression_A_Grammar"),
                        optional=True,
                    ),
                ),
                Sequence(
                    Ref("BinaryOperatorGrammar"),
                    Ref("Tail_Recurse_Expression_A_Grammar"),
                ),
                Ref("InOperatorGrammar"),
                Sequence(
                    "IS",
                    Ref.keyword("NOT", optional=True),
                    Ref("IsClauseGrammar"),
                ),
                Ref("IsNullGrammar"),
                Ref("NotNullGrammar"),
                Ref("CollateGrammar"),
                Sequence(
                    Ref.keyword("NOT", optional=True),
                    "BETWEEN",
                    Ref("Expression_B_Grammar"),
                    "AND",
                    Ref("Tail_Recurse_Expression_A_Grammar"),
                ),
            )
        ),
    ),
    # Expression_B_Grammar: Does not directly feed into Expression_A_Grammar
    # but is used for a BETWEEN statement within Expression_A_Grammar.
    # https://www.cockroachlabs.com/docs/v20.2/sql-grammar.htm#b_expr
    #
    # We use a similar trick as seen with Expression_A_Grammar to avoid recursion
    # by using a tail recursion grammar.  See the comments for a_expr to see how
    # that works.
    Expression_B_Unary_Operator_Grammar=OneOf(
        Ref(
            "SignedSegmentGrammar",
            exclude=Sequence(Ref("QualifiedNumericLiteralSegment")),
        ),
        Ref("TildeSegment"),
    ),
    Tail_Recurse_Expression_B_Grammar=Sequence(
        # Only safe to use if the recursive call is at the END of the repeating
        # element in the main b_expr portion
        AnyNumberOf(Ref("Expression_B_Unary_Operator_Grammar")),
        Ref("Expression_C_Grammar"),
    ),
    Expression_B_Grammar=Sequence(
        # Always start with tail recursion element!
        Ref("Tail_Recurse_Expression_B_Grammar"),
        AnyNumberOf(
            OneOf(
                Sequence(
                    OneOf(
                        Ref("ArithmeticBinaryOperatorGrammar"),
                        Ref("StringBinaryOperatorGrammar"),
                        Ref("ComparisonOperatorGrammar"),
                    ),
                    Ref("Tail_Recurse_Expression_B_Grammar"),
                ),
                # TODO: Add more things from b_expr here
            ),
        ),
    ),
    # Expression_C_Grammar
    # https://www.cockroachlabs.com/docs/v20.2/sql-grammar.htm#c_expr
    Expression_C_Grammar=OneOf(
        Sequence("EXISTS", Bracketed(Ref("SelectableGrammar"))),
        # should be first priority, otherwise EXISTS() would be matched as a function
        Sequence(
            OneOf(
                Ref("Expression_D_Grammar"),
                Ref("CaseExpressionSegment"),
            ),
            AnyNumberOf(Ref("TimeZoneGrammar"), optional=True),
        ),
        Ref("ShorthandCastSegment"),
        terminators=[Ref("CommaSegment")],
    ),
    # Expression_D_Grammar
    # https://www.cockroachlabs.com/docs/v20.2/sql-grammar.htm#d_expr
    Expression_D_Grammar=Sequence(
        OneOf(
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Bracketed(
                OneOf(
                    # We're using the expression segment here rather than the grammar so
                    # that in the parsed structure we get nested elements.
                    Ref("ExpressionSegment"),
                    Ref("SelectableGrammar"),
                    Delimited(
                        Ref(
                            "ColumnReferenceSegment"
                        ),  # WHERE (a,b,c) IN (select a,b,c FROM...)
                        Ref(
                            "FunctionSegment"
                        ),  # WHERE (a, substr(b,1,3)) IN (select c,d FROM...)
                        Ref("LiteralGrammar"),  # WHERE (a, 2) IN (SELECT b, c FROM ...)
                        Ref("LocalAliasSegment"),  # WHERE (LOCAL.a, LOCAL.b) IN (...)
                    ),
                ),
                parse_mode=ParseMode.GREEDY,
            ),
            # Allow potential select statement without brackets
            Ref("SelectStatementSegment"),
            Ref("LiteralGrammar"),
            Ref("IntervalExpressionSegment"),
            Ref("TypedStructLiteralSegment"),
            Ref("ArrayExpressionSegment"),
            Ref("ColumnReferenceSegment"),
            Ref("OverlapsClauseSegment"),
            # For triggers, we allow "NEW.*" but not just "*" nor "a.b.*"
            # So can't use WildcardIdentifierSegment nor WildcardExpressionSegment
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Ref("ObjectReferenceDelimiterGrammar"),
                Ref("StarSegment"),
            ),
            Sequence(
                Ref("StructTypeSegment"),
                Bracketed(Delimited(Ref("ExpressionSegment"))),
            ),
            Sequence(
                Ref("DatatypeSegment"),
                # Don't use the full LiteralGrammar here
                # because only some of them are applicable.
                # Notably we shouldn't use QualifiedNumericLiteralSegment
                # here because it looks like an arithmetic operation.
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("BooleanLiteralGrammar"),
                    Ref("NullLiteralSegment"),
                    Ref("DateTimeLiteralGrammar"),
                ),
            ),
            Ref("LocalAliasSegment"),
            terminators=[Ref("CommaSegment")],
        ),
        Ref("AccessorGrammar", optional=True),
        allow_gaps=True,
    ),
    AccessorGrammar=AnyNumberOf(Ref("ArrayAccessorSegment")),
)


class EqualsSegment(CompositeComparisonOperatorSegment):
    """Equals operator."""

    match_grammar: Matchable = Ref("RawEqualsSegment")


class GreaterThanSegment(CompositeComparisonOperatorSegment):
    """Greater than operator."""

    match_grammar: Matchable = Ref("RawGreaterThanSegment")


class LessThanSegment(CompositeComparisonOperatorSegment):
    """Less than operator."""

    match_grammar: Matchable = Ref("RawLessThanSegment")


class GreaterThanOrEqualToSegment(CompositeComparisonOperatorSegment):
    """Greater than or equal to operator."""

    match_grammar: Matchable = Sequence(
        Ref("RawGreaterThanSegment"), Ref("RawEqualsSegment"), allow_gaps=False
    )


class LessThanOrEqualToSegment(CompositeComparisonOperatorSegment):
    """Less than or equal to operator."""

    match_grammar: Matchable = Sequence(
        Ref("RawLessThanSegment"), Ref("RawEqualsSegment"), allow_gaps=False
    )


class NotEqualToSegment(CompositeComparisonOperatorSegment):
    """Not equal to operator."""

    match_grammar: Matchable = OneOf(
        Sequence(Ref("RawNotSegment"), Ref("RawEqualsSegment"), allow_gaps=False),
        Sequence(
            Ref("RawLessThanSegment"), Ref("RawGreaterThanSegment"), allow_gaps=False
        ),
    )


class ConcatSegment(CompositeBinaryOperatorSegment):
    """Concat operator."""

    match_grammar: Matchable = Sequence(
        Ref("PipeSegment"), Ref("PipeSegment"), allow_gaps=False
    )


class BitwiseAndSegment(CompositeBinaryOperatorSegment):
    """Bitwise and operator."""

    match_grammar: Matchable = Ref("AmpersandSegment")


class BitwiseOrSegment(CompositeBinaryOperatorSegment):
    """Bitwise or operator."""

    match_grammar: Matchable = Ref("PipeSegment")


class BitwiseLShiftSegment(CompositeBinaryOperatorSegment):
    """Bitwise left-shift operator."""

    match_grammar: Matchable = Sequence(
        Ref("RawLessThanSegment"), Ref("RawLessThanSegment"), allow_gaps=False
    )


class BitwiseRShiftSegment(CompositeBinaryOperatorSegment):
    """Bitwise right-shift operator."""

    match_grammar: Matchable = Sequence(
        Ref("RawGreaterThanSegment"), Ref("RawGreaterThanSegment"), allow_gaps=False
    )


class ExpressionSegment(BaseSegment):
    """An expression, either arithmetic or boolean.

    NB: This is potentially VERY recursive and

    mostly uses the grammars above. This version
    also doesn't bound itself first, and so is potentially
    VERY SLOW. I don't really like this solution.

    We rely on elements of the expression to bound
    themselves rather than bounding at the expression
    level. Trying to bound the ExpressionSegment itself
    has been too unstable and not resilient enough to
    other bugs.
    """

    type = "expression"
    match_grammar: Matchable = Ref("Expression_A_Grammar")


class WhereClauseSegment(BaseSegment):
    """A `WHERE` clause like in `SELECT` or `INSERT`."""

    type = "where_clause"
    match_grammar: Matchable = Sequence(
        "WHERE",
        # NOTE: The indent here is implicit to allow
        # constructions like:
        #
        #    WHERE a
        #        AND b
        #
        # to be valid without forcing an indent between
        # "WHERE" and "a".
        ImplicitIndent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`."""

    type = "orderby_clause"
    match_grammar: Matchable = Sequence(
        "ORDER",
        "BY",
        Indent,
        Delimited(
            Sequence(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    # Can `ORDER BY 1`
                    Ref("NumericLiteralSegment"),
                    # Can order by an expression
                    Ref("ExpressionSegment"),
                ),
                OneOf("ASC", "DESC", optional=True),
                # NB: This isn't really ANSI, and isn't supported in Mysql, but
                # is supported in enough other dialects for it to make sense here
                # for now.
                Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
            ),
            terminators=["LIMIT", Ref("FrameClauseUnitGrammar")],
        ),
        Dedent,
    )


class RollupFunctionNameSegment(BaseSegment):
    """ROLLUP function name segment.

    Need to be able to specify this as type `function_name_identifier`
    within a `function_name` so that linting rules identify it properly.
    """

    type = "function_name"
    match_grammar: Matchable = StringParser(
        "ROLLUP",
        CodeSegment,
        type="function_name_identifier",
    )


class CubeFunctionNameSegment(BaseSegment):
    """ROLLUP function name segment.

    Need to be able to specify this as type `function_name_identifier`
    within a `function_name` so that linting rules identify it properly.
    """

    type = "function_name"
    match_grammar: Matchable = StringParser(
        "CUBE",
        CodeSegment,
        type="function_name_identifier",
    )


class GroupingSetsClauseSegment(BaseSegment):
    """`GROUPING SETS` clause within the `GROUP BY` clause."""

    type = "grouping_sets_clause"

    match_grammar = Sequence(
        "GROUPING",
        "SETS",
        Bracketed(
            Delimited(
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingExpressionList"),
            ),
        ),
    )


class GroupingExpressionList(BaseSegment):
    """A `GROUP BY` clause expression list like in `ROLLUP`."""

    type = "grouping_expression_list"

    match_grammar: Matchable = Sequence(
        Delimited(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY ROLLUP(1)`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY ROLLUP(coalesce(col, 1))`
                Ref("ExpressionSegment"),
                Bracketed(),  # Allows empty parentheses
            ),
            terminators=[Ref("GroupByClauseTerminatorGrammar")],
        ),
    )


class CubeRollupClauseSegment(BaseSegment):
    """`CUBE` / `ROLLUP` clause within the `GROUP BY` clause."""

    type = "cube_rollup_clause"
    match_grammar = Sequence(
        OneOf(Ref("CubeFunctionNameSegment"), Ref("RollupFunctionNameSegment")),
        Bracketed(
            Ref("GroupingExpressionList"),
        ),
    )


class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    type = "groupby_clause"

    match_grammar: Matchable = Sequence(
        "GROUP",
        "BY",
        Indent,
        OneOf(
            "ALL",
            Ref("CubeRollupClauseSegment"),
            # We could replace this next bit with a GroupingExpressionList
            # reference (renaming that to a more generic name), to avoid
            # repeating this bit of code, but I would rather keep it flat
            # to avoid changing regular `GROUP BY` clauses.
            Sequence(
                Delimited(
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        # Can `GROUP BY 1`
                        Ref("NumericLiteralSegment"),
                        # Can `GROUP BY coalesce(col, 1)`
                        Ref("ExpressionSegment"),
                    ),
                    terminators=[Ref("GroupByClauseTerminatorGrammar")],
                ),
            ),
        ),
        Dedent,
    )


class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`."""

    type = "having_clause"
    match_grammar: Matchable = Sequence(
        "HAVING",
        ImplicitIndent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


class LimitClauseSegment(BaseSegment):
    """A `LIMIT` clause like in `SELECT`."""

    type = "limit_clause"
    match_grammar: Matchable = Sequence(
        "LIMIT",
        Indent,
        OptionallyBracketed(
            OneOf(
                # Allow a number by itself OR
                Ref("NumericLiteralSegment"),
                # An arbitrary expression
                Ref("ExpressionSegment"),
                "ALL",
            )
        ),
        OneOf(
            Sequence(
                "OFFSET",
                OneOf(
                    # Allow a number by itself OR
                    Ref("NumericLiteralSegment"),
                    # An arbitrary expression
                    Ref("ExpressionSegment"),
                ),
            ),
            Sequence(
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
            ),
            optional=True,
        ),
        Dedent,
    )


class OverlapsClauseSegment(BaseSegment):
    """An `OVERLAPS` clause like in `SELECT."""

    type = "overlaps_clause"
    match_grammar: Matchable = Sequence(
        "OVERLAPS",
        OneOf(
            Sequence(
                Bracketed(
                    Ref("DateTimeLiteralGrammar"),
                    Ref("CommaSegment"),
                    Ref("DateTimeLiteralGrammar"),
                )
            ),
            Ref("ColumnReferenceSegment"),
        ),
    )


class NamedWindowSegment(BaseSegment):
    """A WINDOW clause."""

    type = "named_window"
    match_grammar: Matchable = Sequence(
        "WINDOW",
        Indent,
        Delimited(
            Ref("NamedWindowExpressionSegment"),
        ),
        Dedent,
    )


class FetchClauseSegment(BaseSegment):
    """A `FETCH` clause like in `SELECT."""

    type = "fetch_clause"
    match_grammar: Matchable = Sequence(
        "FETCH",
        OneOf(
            "FIRST",
            "NEXT",
        ),
        OneOf(
            Ref("NumericLiteralSegment"),
            Ref("ExpressionSegment", exclude=Ref.keyword("ROW")),
            optional=True,
        ),
        OneOf("ROW", "ROWS"),
        "ONLY",
    )


class NamedWindowExpressionSegment(BaseSegment):
    """Named window expression."""

    type = "named_window_expression"
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),  # Window name
        "AS",
        OneOf(
            Ref("SingleIdentifierGrammar"),  # Window name
            Bracketed(
                Ref("WindowSpecificationSegment"),
                parse_mode=ParseMode.GREEDY,
            ),
        ),
    )


class ValuesClauseSegment(BaseSegment):
    """A `VALUES` clause like in `INSERT`."""

    type = "values_clause"
    match_grammar: Matchable = Sequence(
        OneOf("VALUE", "VALUES"),
        Delimited(
            Sequence(
                # MySQL uses `ROW` in it's value statement.
                # Currently SQLFluff doesn't differentiate between
                # Values statement:
                # https://dev.mysql.com/doc/refman/8.0/en/values.html
                # and Values() function (used in INSERT statements):
                # https://dev.mysql.com/doc/refman/8.0/en/miscellaneous-functions.html#function_values
                # TODO: split these out in future.
                Ref.keyword("ROW", optional=True),
                Bracketed(
                    Delimited(
                        "DEFAULT",
                        Ref("LiteralGrammar"),
                        Ref("ExpressionSegment"),
                    ),
                    parse_mode=ParseMode.GREEDY,
                ),
            ),
        ),
    )


class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    type = "select_statement"

    match_grammar: Matchable = Sequence(
        Ref("SelectClauseSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("OverlapsClauseSegment", optional=True),
        Ref("NamedWindowSegment", optional=True),
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("WithDataClauseSegment"),
            Ref("OrderByClauseSegment"),
            Ref("LimitClauseSegment"),
        ],
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
    )


class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement."""

    type = "select_statement"

    # Inherit most of the parse grammar from the unordered version.
    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("FetchClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ],
        # Overwrite the terminators, because we want to remove some.
        replace_terminators=True,
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("WithDataClauseSegment"),
        ],
    )


ansi_dialect.add(
    # Things that behave like select statements
    SelectableGrammar=OneOf(
        OptionallyBracketed(Ref("WithCompoundStatementSegment")),
        OptionallyBracketed(Ref("WithCompoundNonSelectStatementSegment")),
        Ref("NonWithSelectableGrammar"),
        Bracketed(Ref("SelectableGrammar")),
    ),
    # Things that behave like select statements, which can form part of with
    # expressions.
    NonWithSelectableGrammar=OneOf(
        Ref("SetExpressionSegment"),
        OptionallyBracketed(Ref("SelectStatementSegment")),
        Ref("NonSetSelectableGrammar"),
    ),
    # Things that do not behave like select statements, which can form part of with
    # expressions.
    NonWithNonSelectableGrammar=OneOf(
        Ref("UpdateStatementSegment"),
        Ref("InsertStatementSegment"),
        Ref("DeleteStatementSegment"),
    ),
    # Things that behave like select statements, which can form part of set expressions.
    NonSetSelectableGrammar=OneOf(
        Ref("ValuesClauseSegment"),
        Ref("UnorderedSelectStatementSegment"),
        # If it's bracketed, we can have the full select statement here,
        # otherwise we can't because any order by clauses should belong
        # to the set expression.
        Bracketed(Ref("SelectStatementSegment")),
        Bracketed(Ref("WithCompoundStatementSegment")),
        Bracketed(Ref("NonSetSelectableGrammar")),
        Ref("BracketedSetExpressionGrammar"),
    ),
    # Added as part of `NonSetSelectableGrammar` where a nested `SetExpressionSegment`
    # could be used. Some dialects don't support an "ordered" set, but some may.
    BracketedSetExpressionGrammar=Bracketed(Ref("UnorderedSetExpressionSegment")),
)


class CTEColumnList(BaseSegment):
    """Bracketed column list portion of a CTE definition."""

    type = "cte_column_list"
    match_grammar = Bracketed(
        Ref("SingleIdentifierListSegment"),
    )


class CTEDefinitionSegment(BaseSegment):
    """A CTE Definition from a WITH statement.

    `tab (col1,col2) AS (SELECT a,b FROM x)`
    """

    type = "common_table_expression"
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("CTEColumnList", optional=True),
        Ref.keyword("AS", optional=True),
        Bracketed(
            # Ephemeral here to subdivide the query.
            Ref("SelectableGrammar"),
            parse_mode=ParseMode.GREEDY,
        ),
    )

    def get_identifier(self) -> IdentifierSegment:
        """Get the identifier of this CTE.

        Note: it blindly gets the first identifier it finds
        which given the structure of a CTE definition is
        usually the right one.
        """
        _identifier = self.get_child("identifier")
        # There will always be one, given the grammar above.
        assert _identifier
        return cast(IdentifierSegment, _identifier)


class WithCompoundStatementSegment(BaseSegment):
    """A `SELECT` statement preceded by a selection of `WITH` clauses.

    `WITH tab (col1,col2) AS (SELECT a,b FROM x)`
    """

    type = "with_compound_statement"
    # match grammar
    match_grammar: Matchable = Sequence(
        "WITH",
        Ref.keyword("RECURSIVE", optional=True),
        Conditional(Indent, indented_ctes=True),
        Delimited(
            Ref("CTEDefinitionSegment"),
            terminators=["SELECT"],
            allow_trailing=True,
        ),
        Conditional(Dedent, indented_ctes=True),
        Ref("NonWithSelectableGrammar"),
    )


class WithCompoundNonSelectStatementSegment(BaseSegment):
    """A `UPDATE/INSERT/DELETE` statement preceded by a selection of `WITH` clauses.

    `WITH tab (col1,col2) AS (SELECT a,b FROM x)`
    """

    type = "with_compound_statement"
    # match grammar
    match_grammar: Matchable = Sequence(
        "WITH",
        Ref.keyword("RECURSIVE", optional=True),
        Conditional(Indent, indented_ctes=True),
        Delimited(
            Ref("CTEDefinitionSegment"),
            terminators=["SELECT"],
            allow_trailing=True,
        ),
        Conditional(Dedent, indented_ctes=True),
        Ref("NonWithNonSelectableGrammar"),
    )


class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Minus, Except or Intersect."""

    type = "set_operator"
    match_grammar: Matchable = OneOf(
        Ref("UnionGrammar"),
        Sequence(
            OneOf(
                "INTERSECT",
                "EXCEPT",
            ),
            Ref.keyword("ALL", optional=True),
        ),
        "MINUS",
        exclude=Sequence("EXCEPT", Bracketed(Anything())),
    )


class UnorderedSetExpressionSegment(BaseSegment):
    """A set expression with either Union, Minus, Except or Intersect."""

    type = "set_expression"
    # match grammar
    match_grammar: Matchable = Sequence(
        Ref("NonSetSelectableGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("SetOperatorSegment"),
                Ref("NonSetSelectableGrammar"),
            ),
            min_times=1,
        ),
    )


class SetExpressionSegment(BaseSegment):
    """A set expression with either Union, Minus, Except or Intersect."""

    type = "set_expression"
    # match grammar
    match_grammar: Matchable = UnorderedSetExpressionSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ],
    )


class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement."""

    type = "insert_statement"
    match_grammar: Matchable = Sequence(
        "INSERT",
        # Maybe OVERWRITE is just snowflake?
        # (It's also Hive but that has full insert grammar implementation)
        Ref.keyword("OVERWRITE", optional=True),
        "INTO",
        Ref("TableReferenceSegment"),
        OneOf(
            # As SelectableGrammar can be bracketed too, the parse gets confused,
            # so we need slightly odd syntax here to allow those to parse (rather
            # than just add optional=True to BracketedColumnReferenceListGrammar).
            Ref("SelectableGrammar"),
            Sequence(
                Ref("BracketedColumnReferenceListGrammar"),
                Ref("SelectableGrammar"),
            ),
            # This is part of ANSI SQL since SQL-92
            Ref("DefaultValuesGrammar"),
        ),
    )


class MergeStatementSegment(BaseSegment):
    """A `MERGE` statement."""

    type = "merge_statement"

    match_grammar = Sequence(
        Ref("MergeIntoLiteralGrammar"),
        Indent,
        OneOf(
            Ref("TableReferenceSegment"),
            Ref("AliasedTableReferenceGrammar"),
        ),
        Dedent,
        "USING",
        Indent,
        OneOf(
            Ref("TableReferenceSegment"),
            Ref("AliasedTableReferenceGrammar"),
            Sequence(
                Bracketed(
                    Ref("SelectableGrammar"),
                ),
                Ref("AliasExpressionSegment", optional=True),
            ),
        ),
        Dedent,
        Conditional(Indent, indented_using_on=True),
        Ref("JoinOnConditionSegment"),
        Conditional(Dedent, indented_using_on=True),
        Ref("MergeMatchSegment"),
    )


class MergeMatchSegment(BaseSegment):
    """Contains dialect specific merge operations.

    Hookpoint for dialect specific behavior
    e.g. UpdateClause / DeleteClause, multiple MergeMatchedClauses
    """

    type = "merge_match"
    match_grammar: Matchable = AnyNumberOf(
        Ref("MergeMatchedClauseSegment"),
        Ref("MergeNotMatchedClauseSegment"),
        min_times=1,
    )


class MergeMatchedClauseSegment(BaseSegment):
    """The `WHEN MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_matched_clause"
    match_grammar: Matchable = Sequence(
        "WHEN",
        "MATCHED",
        Sequence("AND", Ref("ExpressionSegment"), optional=True),
        "THEN",
        Indent,
        OneOf(
            Ref("MergeUpdateClauseSegment"),
            Ref("MergeDeleteClauseSegment"),
        ),
        Dedent,
    )


class MergeNotMatchedClauseSegment(BaseSegment):
    """The `WHEN NOT MATCHED` clause within a `MERGE` statement."""

    type = "merge_when_not_matched_clause"
    match_grammar: Matchable = Sequence(
        "WHEN",
        "NOT",
        "MATCHED",
        Sequence("AND", Ref("ExpressionSegment"), optional=True),
        "THEN",
        Indent,
        Ref("MergeInsertClauseSegment"),
        Dedent,
    )


class MergeUpdateClauseSegment(BaseSegment):
    """`UPDATE` clause within the `MERGE` statement."""

    type = "merge_update_clause"
    match_grammar: Matchable = Sequence(
        "UPDATE",
        Indent,
        Ref("SetClauseListSegment"),
        Dedent,
    )


class MergeInsertClauseSegment(BaseSegment):
    """`INSERT` clause within the `MERGE` statement."""

    type = "merge_insert_clause"
    match_grammar: Matchable = Sequence(
        "INSERT",
        Indent,
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Dedent,
        Ref("ValuesClauseSegment", optional=True),
    )


class MergeDeleteClauseSegment(BaseSegment):
    """`DELETE` clause within the `MERGE` statement."""

    type = "merge_delete_clause"
    match_grammar: Matchable = Ref.keyword("DELETE")


class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement."""

    type = "transaction_statement"
    match_grammar: Matchable = Sequence(
        # COMMIT [ WORK ] [ AND [ NO ] CHAIN ]
        # ROLLBACK [ WORK ] [ AND [ NO ] CHAIN ]
        # BEGIN | END TRANSACTION | WORK
        # NOTE: "TO SAVEPOINT" is not yet supported
        # https://docs.snowflake.com/en/sql-reference/sql/begin.html
        # https://www.postgresql.org/docs/current/sql-end.html
        OneOf("START", "BEGIN", "COMMIT", "ROLLBACK", "END"),
        OneOf("TRANSACTION", "WORK", optional=True),
        Sequence("NAME", Ref("SingleIdentifierGrammar"), optional=True),
        Sequence("AND", Ref.keyword("NO", optional=True), "CHAIN", optional=True),
    )


class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint_segment"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar: Matchable = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),  # Constraint name
            optional=True,
        ),
        OneOf(
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
            Sequence("CHECK", Bracketed(Ref("ExpressionSegment"))),
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                Ref("ColumnConstraintDefaultGrammar"),
            ),
            Ref("PrimaryKeyGrammar"),
            Ref("UniqueKeyGrammar"),  # UNIQUE
            Ref("AutoIncrementGrammar"),
            Ref("ReferenceDefinitionGrammar"),  # REFERENCES reftable [ ( refcolumn) ]x
            Ref("CommentClauseSegment"),
            Sequence(
                "COLLATE", Ref("CollationReferenceSegment")
            ),  # https://www.sqlite.org/datatype3.html#collation
        ),
    )


class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        Ref("DatatypeSegment"),  # Column type
        Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
        AnyNumberOf(
            Ref("ColumnConstraintSegment", optional=True),
        ),
    )


class IndexColumnDefinitionSegment(BaseSegment):
    """A column definition for CREATE INDEX."""

    type = "index_column_definition"
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        OneOf("ASC", "DESC", optional=True),
    )


class TableConstraintSegment(BaseSegment):
    """A table constraint, e.g. for CREATE TABLE."""

    type = "table_constraint"

    # Later add support for CHECK constraint, others?
    # e.g. CONSTRAINT constraint_1 PRIMARY KEY(column_1)
    match_grammar: Matchable = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        OneOf(
            Sequence(  # UNIQUE ( column_name [, ... ] )
                "UNIQUE",
                Ref("BracketedColumnReferenceListGrammar"),
                # Later add support for index_parameters?
            ),
            Sequence(  # PRIMARY KEY ( column_name [, ... ] ) index_parameters
                Ref("PrimaryKeyGrammar"),
                # Columns making up PRIMARY KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                # Later add support for index_parameters?
            ),
            Sequence(  # FOREIGN KEY ( column_name [, ... ] )
                # REFERENCES reftable [ ( refcolumn [, ... ] ) ]
                Ref("ForeignKeyGrammar"),
                # Local columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                Ref(
                    "ReferenceDefinitionGrammar"
                ),  # REFERENCES reftable [ ( refcolumn) ]
            ),
        ),
    )


class TableEndClauseSegment(BaseSegment):
    """Allow for additional table endings.

    (like WITHOUT ROWID for SQLite)
    """

    type = "table_end_clause_segment"
    match_grammar: Matchable = Nothing()


class ArrayExpressionSegment(BaseSegment):
    """Expression to construct a ARRAY from a subquery.

    (Yes in BigQuery for example)

    NOTE: This differs from an array _literal_ in that it
    takes the form of an expression.
    """

    type = "array_expression"
    match_grammar: Matchable = Nothing()


class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryTransientGrammar", optional=True),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
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
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref("TableEndClauseSegment", optional=True),
    )


class CommentClauseSegment(BaseSegment):
    """A comment clause.

    e.g. COMMENT 'view/table/column description'
    """

    type = "comment_clause"
    match_grammar: Matchable = Sequence("COMMENT", Ref("QuotedLiteralSegment"))


class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement."""

    type = "create_schema_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
    )


class SetSchemaStatementSegment(BaseSegment):
    """A `SET SCHEMA` statement."""

    type = "set_schema_statement"
    match_grammar: Matchable = Sequence(
        "SET",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
    )


class DropSchemaStatementSegment(BaseSegment):
    """A `DROP SCHEMA` statement."""

    type = "drop_schema_statement"
    match_grammar: Matchable = Sequence(
        "DROP",
        "SCHEMA",
        Ref("IfExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class DropTypeStatementSegment(BaseSegment):
    """A `DROP TYPE` statement."""

    type = "drop_type_statement"
    match_grammar: Matchable = Sequence(
        "DROP",
        "TYPE",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class CreateDatabaseStatementSegment(BaseSegment):
    """A `CREATE DATABASE` statement."""

    type = "create_database_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "DATABASE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
    )


class DropDatabaseStatementSegment(BaseSegment):
    """A `DROP DATABASE` statement."""

    type = "drop_database_statement"
    match_grammar: Matchable = Sequence(
        "DROP",
        "DATABASE",
        Ref("IfExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` statement."""

    type = "create_index_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref.keyword("UNIQUE", optional=True),
        "INDEX",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence(
            Bracketed(
                Delimited(
                    Ref("IndexColumnDefinitionSegment"),
                ),
            )
        ),
    )


class AlterTableStatementSegment(BaseSegment):
    """An `ALTER TABLE` statement."""

    type = "alter_table_statement"
    # Based loosely on:
    # https://dev.mysql.com/doc/refman/8.0/en/alter-table.html
    # TODO: Flesh this out with more detail.
    match_grammar: Matchable = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        Delimited(
            Ref("AlterTableOptionsGrammar"),
        ),
    )


class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement."""

    type = "create_view_statement"
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html#create-view-statement
    # https://dev.mysql.com/doc/refman/8.0/en/create-view.html
    # https://www.postgresql.org/docs/12/sql-createview.html
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Optional list of column names
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Ref("WithNoSchemaBindingClauseSegment", optional=True),
    )


class DropTableStatementSegment(BaseSegment):
    """A `DROP TABLE` statement."""

    type = "drop_table_statement"

    match_grammar: Matchable = Sequence(
        "DROP",
        Ref("TemporaryGrammar", optional=True),
        "TABLE",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("TableReferenceSegment")),
        Ref("DropBehaviorGrammar", optional=True),
    )


class DropViewStatementSegment(BaseSegment):
    """A `DROP VIEW` statement."""

    type = "drop_view_statement"

    match_grammar: Matchable = Sequence(
        "DROP",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class DropUserStatementSegment(BaseSegment):
    """A `DROP USER` statement."""

    type = "drop_user_statement"

    match_grammar: Matchable = Sequence(
        "DROP",
        "USER",
        Ref("IfExistsGrammar", optional=True),
        Ref("RoleReferenceSegment"),
    )


class TruncateStatementSegment(BaseSegment):
    """`TRUNCATE TABLE` statement."""

    type = "truncate_table"

    match_grammar: Matchable = Sequence(
        "TRUNCATE",
        Ref.keyword("TABLE", optional=True),
        Ref("TableReferenceSegment"),
    )


class DropIndexStatementSegment(BaseSegment):
    """A `DROP INDEX` statement."""

    type = "drop_index_statement"
    # DROP INDEX <Index name> [IF EXISTS] {RESTRICT | CASCADE}
    match_grammar: Matchable = Sequence(
        "DROP",
        "INDEX",
        Ref("IfExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class AccessStatementSegment(BaseSegment):
    """A `GRANT` or `REVOKE` statement.

    In order to help reduce code duplication we decided to implement other dialect
    specific grants (like Snowflake) here too which will help with maintainability. We
    also note that this causes the grammar to be less "correct", but the benefits
    outweigh the con in our opinion.


    Grant specific information:
     * https://www.postgresql.org/docs/9.0/sql-grant.html
     * https://docs.snowflake.com/en/sql-reference/sql/grant-privilege.html

    Revoke specific information:
     * https://www.postgresql.org/docs/9.0/sql-revoke.html
     * https://docs.snowflake.com/en/sql-reference/sql/revoke-role.html
     * https://docs.snowflake.com/en/sql-reference/sql/revoke-privilege.html
     * https://docs.snowflake.com/en/sql-reference/sql/revoke-privilege-share.html
    """

    type = "access_statement"

    # Privileges that can be set on the account (specific to snowflake)
    _global_permissions = OneOf(
        Sequence(
            "CREATE",
            OneOf(
                "ROLE",
                "USER",
                "WAREHOUSE",
                "DATABASE",
                "INTEGRATION",
            ),
        ),
        Sequence("APPLY", "MASKING", "POLICY"),
        Sequence("EXECUTE", "TASK"),
        Sequence("MANAGE", "GRANTS"),
        Sequence("MONITOR", OneOf("EXECUTION", "USAGE")),
    )

    _schema_object_names = [
        "TABLE",
        "VIEW",
        "STAGE",
        "FUNCTION",
        "PROCEDURE",
        "ROUTINE",
        "SEQUENCE",
        "STREAM",
        "TASK",
    ]

    _schema_object_types = OneOf(
        *_schema_object_names,
        Sequence("MATERIALIZED", "VIEW"),
        Sequence("EXTERNAL", "TABLE"),
        Sequence("FILE", "FORMAT"),
    )

    # We reuse the object names above and simply append an `S` to the end of them to get
    # plurals
    _schema_object_types_plural = OneOf(
        *[f"{object_name}S" for object_name in _schema_object_names]
    )

    _permissions = Sequence(
        OneOf(
            Sequence(
                "CREATE",
                OneOf(
                    "SCHEMA",
                    Sequence("MASKING", "POLICY"),
                    "PIPE",
                    _schema_object_types,
                ),
            ),
            Sequence("IMPORTED", "PRIVILEGES"),
            "APPLY",
            "CONNECT",
            "CREATE",
            "DELETE",
            "EXECUTE",
            "INSERT",
            "MODIFY",
            "MONITOR",
            "OPERATE",
            "OWNERSHIP",
            "READ",
            "REFERENCE_USAGE",
            "REFERENCES",
            "SELECT",
            "TEMP",
            "TEMPORARY",
            "TRIGGER",
            "TRUNCATE",
            "UPDATE",
            "USAGE",
            "USE_ANY_ROLE",
            "WRITE",
            Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
        ),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
    )

    # All of the object types that we can grant permissions on.
    # This list will contain ansi sql objects as well as dialect specific ones.
    _objects = OneOf(
        "ACCOUNT",
        Sequence(
            OneOf(
                Sequence("RESOURCE", "MONITOR"),
                "WAREHOUSE",
                "DATABASE",
                "DOMAIN",
                "INTEGRATION",
                "LANGUAGE",
                "SCHEMA",
                "ROLE",
                "TABLESPACE",
                "TYPE",
                Sequence(
                    "FOREIGN",
                    OneOf("SERVER", Sequence("DATA", "WRAPPER")),
                ),
                Sequence("ALL", "SCHEMAS", "IN", "DATABASE"),
                Sequence("FUTURE", "SCHEMAS", "IN", "DATABASE"),
                _schema_object_types,
                Sequence("ALL", _schema_object_types_plural, "IN", "SCHEMA"),
                Sequence(
                    "FUTURE",
                    _schema_object_types_plural,
                    "IN",
                    OneOf("DATABASE", "SCHEMA"),
                ),
                optional=True,
            ),
            Delimited(
                Ref("ObjectReferenceSegment"),
                Sequence(
                    Ref("FunctionNameSegment"),
                    Ref("FunctionParameterListGrammar", optional=True),
                ),
                Ref("WildcardIdentifierSegment"),
                terminators=["TO", "FROM"],
            ),
        ),
        Sequence("LARGE", "OBJECT", Ref("NumericLiteralSegment")),
    )

    match_grammar: Matchable = OneOf(
        # Based on https://www.postgresql.org/docs/13/sql-grant.html
        # and https://docs.snowflake.com/en/sql-reference/sql/grant-privilege.html
        Sequence(
            "GRANT",
            OneOf(
                Sequence(
                    Delimited(
                        OneOf(_global_permissions, _permissions),
                        terminators=["ON"],
                    ),
                    "ON",
                    _objects,
                ),
                Sequence("ROLE", Ref("ObjectReferenceSegment")),
                Sequence("OWNERSHIP", "ON", "USER", Ref("ObjectReferenceSegment")),
                # In the case where a role is granted non-explicitly,
                # e.g. GRANT ROLE_NAME TO OTHER_ROLE_NAME
                # See https://www.postgresql.org/docs/current/sql-grant.html
                Ref("ObjectReferenceSegment"),
            ),
            "TO",
            OneOf("GROUP", "USER", "ROLE", "SHARE", optional=True),
            Delimited(
                OneOf(Ref("RoleReferenceSegment"), Ref("FunctionSegment"), "PUBLIC"),
            ),
            OneOf(
                Sequence("WITH", "GRANT", "OPTION"),
                Sequence("WITH", "ADMIN", "OPTION"),
                Sequence("COPY", "CURRENT", "GRANTS"),
                optional=True,
            ),
            Sequence(
                "GRANTED",
                "BY",
                OneOf(
                    "CURRENT_USER",
                    "SESSION_USER",
                    Ref("ObjectReferenceSegment"),
                ),
                optional=True,
            ),
        ),
        # Based on https://www.postgresql.org/docs/12/sql-revoke.html
        Sequence(
            "REVOKE",
            Sequence("GRANT", "OPTION", "FOR", optional=True),
            OneOf(
                Sequence(
                    Delimited(
                        OneOf(_global_permissions, _permissions),
                        terminators=["ON"],
                    ),
                    "ON",
                    _objects,
                ),
                Sequence("ROLE", Ref("ObjectReferenceSegment")),
                Sequence("OWNERSHIP", "ON", "USER", Ref("ObjectReferenceSegment")),
                Ref("ObjectReferenceSegment"),
            ),
            "FROM",
            OneOf("GROUP", "USER", "ROLE", "SHARE", optional=True),
            Delimited(
                Ref("ObjectReferenceSegment"),
            ),
            Ref("DropBehaviorGrammar", optional=True),
        ),
    )


class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    DELETE FROM <table name> [ WHERE <search condition> ]
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar: Matchable = Sequence(
        "DELETE",
        Ref("FromClauseSegment"),
        Ref("WhereClauseSegment", optional=True),
    )


class UpdateStatementSegment(BaseSegment):
    """An `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    """

    type = "update_statement"
    match_grammar: Matchable = Sequence(
        "UPDATE",
        Ref("TableReferenceSegment"),
        # SET is not a reserved word in all dialects (e.g. RedShift)
        # So specifically exclude as an allowed implicit alias to avoid parsing errors
        Ref("AliasExpressionSegment", exclude=Ref.keyword("SET"), optional=True),
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
    )


class SetClauseListSegment(BaseSegment):
    """SQL 1992 set clause list.

    <set clause list> ::=
              <set clause> [ { <comma> <set clause> }... ]

         <set clause> ::=
              <object column> <equals operator> <update source>

         <update source> ::=
                <value expression>
              | <null specification>
              | DEFAULT

         <object column> ::= <column name>
    """

    type = "set_clause_list"
    match_grammar: Matchable = Sequence(
        "SET",
        Indent,
        Ref("SetClauseSegment"),
        # set clause
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("SetClauseSegment"),
        ),
        Dedent,
    )


class SetClauseSegment(BaseSegment):
    """SQL 1992 set clause.

    <set clause> ::=
              <object column> <equals operator> <update source>

         <update source> ::=
                <value expression>
              | <null specification>
              | DEFAULT

         <object column> ::= <column name>
    """

    type = "set_clause"

    match_grammar: Matchable = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("EqualsSegment"),
        OneOf(
            Ref("LiteralGrammar"),
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Ref("ColumnReferenceSegment"),
            Ref("ExpressionSegment"),
            Ref("ValuesClauseSegment"),
            "DEFAULT",
        ),
    )


class CreateCastStatementSegment(BaseSegment):
    """A `CREATE CAST` statement.

    https://jakewheat.github.io/sql-overview/sql-2016-foundation-grammar.html#_11_63_user_defined_cast_definition
    """

    type = "create_cast_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        "CAST",
        Bracketed(
            Ref("DatatypeSegment"),
            "AS",
            Ref("DatatypeSegment"),
        ),
        "WITH",
        Ref.keyword("SPECIFIC", optional=True),
        OneOf(
            "ROUTINE",
            "FUNCTION",
            "PROCEDURE",
            Sequence(
                OneOf("INSTANCE", "STATIC", "CONSTRUCTOR", optional=True),
                "METHOD",
            ),
        ),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        Sequence("FOR", Ref("ObjectReferenceSegment"), optional=True),
        Sequence("AS", "ASSIGNMENT", optional=True),
    )


class DropCastStatementSegment(BaseSegment):
    """A `DROP CAST` statement.

    https://jakewheat.github.io/sql-overview/sql-2016-foundation-grammar.html#_11_64_drop_user_defined_cast_statement
    """

    type = "drop_cast_statement"

    match_grammar: Matchable = Sequence(
        "DROP",
        "CAST",
        Bracketed(
            Ref("DatatypeSegment"),
            "AS",
            Ref("DatatypeSegment"),
        ),
        Ref("DropBehaviorGrammar", optional=True),
    )


class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement."""

    type = "function_definition"
    match_grammar: Matchable = Sequence(
        "AS",
        Ref("QuotedLiteralSegment"),
        Sequence(
            "LANGUAGE",
            Ref("NakedIdentifierSegment"),
            optional=True,
        ),
    )


class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the ANSI dialect should be a "common subset" of the
    structure of the code for those dialects.
    postgres: https://www.postgresql.org/docs/9.1/sql-createfunction.html
    snowflake: https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    bigquery:
    https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    """

    type = "create_function_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


class FunctionParameterListGrammar(BaseSegment):
    """The parameters for a function ie. `(string, number)`."""

    type = "function_parameter_list"
    # Function parameter list
    match_grammar: Matchable = Bracketed(
        Delimited(
            Ref("FunctionParameterGrammar"),
            optional=True,
        ),
    )


class DropFunctionStatementSegment(BaseSegment):
    """A `DROP FUNCTION` statement."""

    type = "drop_function_statement"

    match_grammar = Sequence(
        "DROP",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
    )


class CreateModelStatementSegment(BaseSegment):
    """A BigQuery `CREATE MODEL` statement."""

    type = "create_model_statement"
    # https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-create
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "MODEL",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Sequence(
            "OPTIONS",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        OneOf(
                            # This covers many but not all the extensive list of
                            # possible 'CREATE MODEL' options.
                            Ref("LiteralGrammar"),  # Single value
                            Bracketed(
                                # E.g. input_label_cols: list of column names
                                Delimited(Ref("QuotedLiteralSegment")),
                                bracket_type="square",
                                optional=True,
                            ),
                        ),
                    ),
                )
            ),
            optional=True,
        ),
        "AS",
        Ref("SelectableGrammar"),
    )


class CreateUserStatementSegment(BaseSegment):
    """A `CREATE USER` statement.

    A very simple create user syntax which can be extended
    by other dialects.
    """

    type = "create_user_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "USER",
        Ref("RoleReferenceSegment"),
    )


class CreateRoleStatementSegment(BaseSegment):
    """A `CREATE ROLE` statement.

    A very simple create role syntax which can be extended
    by other dialects.
    """

    type = "create_role_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "ROLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("RoleReferenceSegment"),
    )


class DropRoleStatementSegment(BaseSegment):
    """A `DROP ROLE` statement with CASCADE option."""

    type = "drop_role_statement"

    match_grammar = Sequence(
        "DROP",
        "ROLE",
        Ref("IfExistsGrammar", optional=True),
        Ref("SingleIdentifierGrammar"),
    )


class DropModelStatementSegment(BaseSegment):
    """A `DROP MODEL` statement."""

    type = "drop_MODELstatement"
    # DROP MODEL <Model name> [IF EXISTS}
    # https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-drop-model
    match_grammar: Matchable = Sequence(
        "DROP",
        "MODEL",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
    )


class MLTableExpressionSegment(BaseSegment):
    """An ML table expression."""

    type = "ml_table_expression"
    # E.g. ML.WEIGHTS(MODEL `project.dataset.model`)
    match_grammar: Matchable = Sequence(
        "ML",
        Ref("DotSegment"),
        Ref("SingleIdentifierGrammar"),
        Bracketed(
            Sequence("MODEL", Ref("ObjectReferenceSegment")),
            Sequence(
                Ref("CommaSegment"),
                Bracketed(
                    Ref("SelectableGrammar"),
                ),
                optional=True,
            ),
        ),
    )


class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"
    match_grammar: Matchable = OneOf(
        Ref("SelectableGrammar"),
        Ref("MergeStatementSegment"),
        Ref("InsertStatementSegment"),
        Ref("TransactionStatementSegment"),
        Ref("DropTableStatementSegment"),
        Ref("DropViewStatementSegment"),
        Ref("CreateUserStatementSegment"),
        Ref("DropUserStatementSegment"),
        Ref("TruncateStatementSegment"),
        Ref("AccessStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("CreateRoleStatementSegment"),
        Ref("DropRoleStatementSegment"),
        Ref("AlterTableStatementSegment"),
        Ref("CreateSchemaStatementSegment"),
        Ref("SetSchemaStatementSegment"),
        Ref("DropSchemaStatementSegment"),
        Ref("DropTypeStatementSegment"),
        Ref("CreateDatabaseStatementSegment"),
        Ref("DropDatabaseStatementSegment"),
        Ref("CreateIndexStatementSegment"),
        Ref("DropIndexStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("DeleteStatementSegment"),
        Ref("UpdateStatementSegment"),
        Ref("CreateCastStatementSegment"),
        Ref("DropCastStatementSegment"),
        Ref("CreateFunctionStatementSegment"),
        Ref("DropFunctionStatementSegment"),
        Ref("CreateModelStatementSegment"),
        Ref("DropModelStatementSegment"),
        Ref("DescribeStatementSegment"),
        Ref("UseStatementSegment"),
        Ref("ExplainStatementSegment"),
        Ref("CreateSequenceStatementSegment"),
        Ref("AlterSequenceStatementSegment"),
        Ref("DropSequenceStatementSegment"),
        Ref("CreateTriggerStatementSegment"),
        Ref("DropTriggerStatementSegment"),
        terminators=[Ref("DelimiterGrammar")],
    )

    def get_table_references(self) -> Set[str]:
        """Use parsed tree to extract table references."""
        table_refs = {
            tbl_ref.raw for tbl_ref in self.recursive_crawl("table_reference")
        }
        cte_refs = {
            cast(CTEDefinitionSegment, cte_def).get_identifier().raw
            for cte_def in self.recursive_crawl("common_table_expression")
        }
        # External references are any table references which aren't
        # also cte aliases.
        return table_refs - cte_refs


class WithNoSchemaBindingClauseSegment(BaseSegment):
    """WITH NO SCHEMA BINDING clause for Redshift's Late Binding Views.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_VIEW.html
    """

    type = "with_no_schema_binding_clause"
    match_grammar: Matchable = Sequence(
        "WITH",
        "NO",
        "SCHEMA",
        "BINDING",
    )


class WithDataClauseSegment(BaseSegment):
    """WITH [NO] DATA clause for Postgres' MATERIALIZED VIEWS.

    https://www.postgresql.org/docs/9.3/sql-creatematerializedview.html
    """

    type = "with_data_clause"
    match_grammar: Matchable = Sequence("WITH", Sequence("NO", optional=True), "DATA")


class DescribeStatementSegment(BaseSegment):
    """A `Describe` statement.

    DESCRIBE <object type> <object name>
    """

    type = "describe_statement"
    match_grammar: Matchable = Sequence(
        "DESCRIBE",
        Ref("NakedIdentifierSegment"),
        Ref("ObjectReferenceSegment"),
    )


class UseStatementSegment(BaseSegment):
    """A `USE` statement."""

    type = "use_statement"
    match_grammar: Matchable = Sequence(
        "USE",
        Ref("DatabaseReferenceSegment"),
    )


class ExplainStatementSegment(BaseSegment):
    """An `Explain` statement.

    EXPLAIN explainable_stmt
    """

    type = "explain_statement"

    explainable_stmt: Matchable = OneOf(
        Ref("SelectableGrammar"),
        Ref("InsertStatementSegment"),
        Ref("UpdateStatementSegment"),
        Ref("DeleteStatementSegment"),
    )

    match_grammar: Matchable = Sequence(
        "EXPLAIN",
        explainable_stmt,
    )


class CreateSequenceOptionsSegment(BaseSegment):
    """Options for Create Sequence statement.

    https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_6015.htm
    """

    type = "create_sequence_options_segment"

    match_grammar: Matchable = OneOf(
        Sequence("INCREMENT", "BY", Ref("NumericLiteralSegment")),
        Sequence(
            "START", Ref.keyword("WITH", optional=True), Ref("NumericLiteralSegment")
        ),
        OneOf(
            Sequence("MINVALUE", Ref("NumericLiteralSegment")),
            Sequence("NO", "MINVALUE"),
        ),
        OneOf(
            Sequence("MAXVALUE", Ref("NumericLiteralSegment")),
            Sequence("NO", "MAXVALUE"),
        ),
        OneOf(Sequence("CACHE", Ref("NumericLiteralSegment")), "NOCACHE"),
        OneOf("CYCLE", "NOCYCLE"),
        Ref("OrderNoOrderGrammar"),
    )


class CreateSequenceStatementSegment(BaseSegment):
    """Create Sequence statement.

    https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_6015.htm
    """

    type = "create_sequence_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        "SEQUENCE",
        Ref("SequenceReferenceSegment"),
        AnyNumberOf(Ref("CreateSequenceOptionsSegment"), optional=True),
    )


class AlterSequenceOptionsSegment(BaseSegment):
    """Options for Alter Sequence statement.

    https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_2011.htm
    """

    type = "alter_sequence_options_segment"

    match_grammar: Matchable = OneOf(
        Sequence("INCREMENT", "BY", Ref("NumericLiteralSegment")),
        OneOf(
            Sequence("MINVALUE", Ref("NumericLiteralSegment")),
            Sequence("NO", "MINVALUE"),
        ),
        OneOf(
            Sequence("MAXVALUE", Ref("NumericLiteralSegment")),
            Sequence("NO", "MAXVALUE"),
        ),
        OneOf(Sequence("CACHE", Ref("NumericLiteralSegment")), "NOCACHE"),
        OneOf("CYCLE", "NOCYCLE"),
        Ref("OrderNoOrderGrammar"),
    )


class AlterSequenceStatementSegment(BaseSegment):
    """Alter Sequence Statement.

    https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_2011.htm
    """

    type = "alter_sequence_statement"

    match_grammar: Matchable = Sequence(
        "ALTER",
        "SEQUENCE",
        Ref("SequenceReferenceSegment"),
        AnyNumberOf(Ref("AlterSequenceOptionsSegment")),
    )


class DropSequenceStatementSegment(BaseSegment):
    """Drop Sequence Statement.

    https://docs.oracle.com/cd/E11882_01/server.112/e41084/statements_9001.htm
    """

    type = "drop_sequence_statement"

    match_grammar: Matchable = Sequence(
        "DROP", "SEQUENCE", Ref("SequenceReferenceSegment")
    )


class DatePartFunctionNameSegment(BaseSegment):
    """DATEADD function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar: Matchable = Ref("DatePartFunctionName")


class CreateTriggerStatementSegment(BaseSegment):
    """Create Trigger Statement.

    https://www.postgresql.org/docs/14/sql-createtrigger.html
    Edited as per notes in above - what doesn't match ANSI
    """

    type = "create_trigger"

    match_grammar: Matchable = Sequence(
        "CREATE",
        "TRIGGER",
        Ref("TriggerReferenceSegment"),
        OneOf("BEFORE", "AFTER", Sequence("INSTEAD", "OF"), optional=True),
        Delimited(
            "INSERT",
            "DELETE",
            Sequence(
                "UPDATE",
                "OF",
                Delimited(
                    Ref("ColumnReferenceSegment"),
                    terminators=["OR", "ON"],
                ),
            ),
            delimiter="OR",
            terminators=["ON"],
        ),
        "ON",
        Ref("TableReferenceSegment"),
        AnyNumberOf(
            Sequence(
                "REFERENCING",
                "OLD",
                "ROW",
                "AS",
                Ref("ParameterNameSegment"),
                "NEW",
                "ROW",
                "AS",
                Ref("ParameterNameSegment"),
            ),
            Sequence("FROM", Ref("TableReferenceSegment")),
            OneOf(
                Sequence("NOT", "DEFERRABLE"),
                Sequence(
                    Ref.keyword("DEFERRABLE", optional=True),
                    OneOf(
                        Sequence("INITIALLY", "IMMEDIATE"),
                        Sequence("INITIALLY", "DEFERRED"),
                    ),
                ),
            ),
            Sequence(
                "FOR", Ref.keyword("EACH", optional=True), OneOf("ROW", "STATEMENT")
            ),
            Sequence("WHEN", Bracketed(Ref("ExpressionSegment"))),
        ),
        Sequence(
            "EXECUTE",
            "PROCEDURE",
            Ref("FunctionNameIdentifierSegment"),
            Bracketed(Ref("FunctionContentsGrammar", optional=True)),
            optional=True,
        ),
    )


class DropTriggerStatementSegment(BaseSegment):
    """Drop Trigger Statement.

    Taken from specification in https://www.postgresql.org/docs/14/sql-droptrigger.html
    Edited as per notes in above - what doesn't match ANSI
    """

    type = "drop_trigger"

    match_grammar: Matchable = Sequence(
        "DROP",
        "TRIGGER",
        Ref("IfExistsGrammar", optional=True),
        Ref("TriggerReferenceSegment"),
    )


class SamplingExpressionSegment(BaseSegment):
    """A sampling expression."""

    type = "sample_expression"
    match_grammar: Matchable = Sequence(
        "TABLESAMPLE",
        OneOf("BERNOULLI", "SYSTEM"),
        Bracketed(Ref("NumericLiteralSegment")),
        Sequence(
            OneOf("REPEATABLE"),
            Bracketed(Ref("NumericLiteralSegment")),
            optional=True,
        ),
    )


class LocalAliasSegment(BaseSegment):
    """The `LOCAL.ALIAS` syntax allows to use an alias name of a column within clauses.

    A hookpoint for other dialects e.g. Exasol.
    """

    type = "local_alias_segment"
    match_grammar: Matchable = Nothing()


class PathSegment(BaseSegment):
    """A reference to a path."""

    type = "path_segment"
    match_grammar: Matchable = OneOf(
        Sequence(
            Ref("SlashSegment"),
            Delimited(
                TypedParser("word", WordSegment, type="path_segment"),
                delimiter=Ref("SlashSegment"),
                allow_gaps=False,
            ),
        ),
        Ref("QuotedLiteralSegment"),
    )
