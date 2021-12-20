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
from typing import Generator, List, NamedTuple, Optional, Tuple, Union

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseFileSegment,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Conditional,
    Dedent,
    Delimited,
    GreedyUntil,
    Indent,
    KeywordSegment,
    Matchable,
    NamedParser,
    NewlineSegment,
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
    WhitespaceSegment,
)
from sqlfluff.core.parser.segments.base import BracketedSegment
from sqlfluff.dialects.dialect_ansi_keywords import (
    ansi_reserved_keywords,
    ansi_unreserved_keywords,
)

ansi_dialect = Dialect("ansi", root_segment_name="FileSegment")

ansi_dialect.set_lexer_matchers(
    [
        RegexLexer("whitespace", r"[\t ]+", WhitespaceSegment),
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
                r"[\t ]+",
                WhitespaceSegment,
            ),
        ),
        RegexLexer("single_quote", r"'([^'\\]|\\.)*'", CodeSegment),
        RegexLexer("double_quote", r'"([^"\\]|\\.)*"', CodeSegment),
        RegexLexer("back_quote", r"`[^`]*`", CodeSegment),
        # See https://www.geeksforgeeks.org/postgresql-dollar-quoted-string-constants/
        RegexLexer("dollar_quote", r"\$(\w*)\$[^\1]*?\$\1\$", CodeSegment),
        # Numeric literal matches integers, decimals, and exponential formats,
        # with a positve lookahead assertion to check it is not part of a naked identifier.
        RegexLexer(
            "numeric_literal",
            r"(?>\d+(\.\d+)?|\.\d+)([eE][+-]?\d+)?(?=\b)",
            CodeSegment,
        ),
        RegexLexer("not_equal", r"!=|<>", CodeSegment),
        RegexLexer("like_operator", r"!?~~?\*?", CodeSegment),
        StringLexer("greater_than_or_equal", ">=", CodeSegment),
        StringLexer("less_than_or_equal", "<=", CodeSegment),
        RegexLexer("newline", r"\r\n|\n", NewlineSegment),
        StringLexer("casting_operator", "::", CodeSegment),
        StringLexer("concat_operator", "||", CodeSegment),
        StringLexer("equals", "=", CodeSegment),
        StringLexer("greater_than", ">", CodeSegment),
        StringLexer("less_than", "<", CodeSegment),
        StringLexer("dot", ".", CodeSegment),
        StringLexer("comma", ",", CodeSegment, segment_kwargs={"type": "comma"}),
        StringLexer("plus", "+", CodeSegment),
        StringLexer("minus", "-", CodeSegment),
        StringLexer("divide", "/", CodeSegment),
        StringLexer("percent", "%", CodeSegment),
        StringLexer("ampersand", "&", CodeSegment),
        StringLexer("vertical_bar", "|", CodeSegment),
        StringLexer("caret", "^", CodeSegment),
        StringLexer("star", "*", CodeSegment),
        StringLexer("bracket_open", "(", CodeSegment),
        StringLexer("bracket_close", ")", CodeSegment),
        StringLexer("sq_bracket_open", "[", CodeSegment),
        StringLexer("sq_bracket_close", "]", CodeSegment),
        StringLexer("crly_bracket_open", "{", CodeSegment),
        StringLexer("crly_bracket_close", "}", CodeSegment),
        StringLexer("colon", ":", CodeSegment),
        StringLexer("semicolon", ";", CodeSegment),
        RegexLexer("code", r"[0-9a-zA-Z_]+", CodeSegment),
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

# Set Keywords
ansi_dialect.sets("unreserved_keywords").update(
    [n.strip().upper() for n in ansi_unreserved_keywords.split("\n")]
)

ansi_dialect.sets("reserved_keywords").update(
    [n.strip().upper() for n in ansi_reserved_keywords.split("\n")]
)

# Bracket pairs (a set of tuples).
# (name, startref, endref, persists)
# NOTE: The `persists` value controls whether this type
# of bracket is persisted during matching to speed up other
# parts of the matching process. Round brackets are the most
# common and match the largest areas and so are sufficient.
ansi_dialect.sets("bracket_pairs").update(
    [
        ("round", "StartBracketSegment", "EndBracketSegment", True),
        ("square", "StartSquareBracketSegment", "EndSquareBracketSegment", False),
        ("curly", "StartCurlyBracketSegment", "EndCurlyBracketSegment", False),
    ]
)

# Set the value table functions. These are functions that, if they appear as
# an item in "FROM', are treated as returning a COLUMN, not a TABLE. Apparently,
# among dialects supported by SQLFluff, only BigQuery has this concept, but this
# set is defined in the ANSI dialect because:
# - It impacts core linter rules (see L020 and several other rules that subclass
#   from it) and how they interpret the contents of table_expressions
# - At least one other database (DB2) has the same value table function,
#   UNNEST(), as BigQuery. DB2 is not currently supported by SQLFluff.
ansi_dialect.sets("value_table_functions").update([])

ansi_dialect.add(
    # Real segments
    DelimiterSegment=Ref("SemicolonSegment"),
    SemicolonSegment=StringParser(
        ";", SymbolSegment, name="semicolon", type="statement_terminator"
    ),
    ColonSegment=StringParser(":", SymbolSegment, name="colon", type="colon"),
    SliceSegment=StringParser(":", SymbolSegment, name="slice", type="slice"),
    StartBracketSegment=StringParser(
        "(", SymbolSegment, name="start_bracket", type="start_bracket"
    ),
    EndBracketSegment=StringParser(
        ")", SymbolSegment, name="end_bracket", type="end_bracket"
    ),
    StartSquareBracketSegment=StringParser(
        "[", SymbolSegment, name="start_square_bracket", type="start_square_bracket"
    ),
    EndSquareBracketSegment=StringParser(
        "]", SymbolSegment, name="end_square_bracket", type="end_square_bracket"
    ),
    StartCurlyBracketSegment=StringParser(
        "{", SymbolSegment, name="start_curly_bracket", type="start_curly_bracket"
    ),
    EndCurlyBracketSegment=StringParser(
        "}", SymbolSegment, name="end_curly_bracket", type="end_curly_bracket"
    ),
    CommaSegment=StringParser(",", SymbolSegment, name="comma", type="comma"),
    DotSegment=StringParser(".", SymbolSegment, name="dot", type="dot"),
    StarSegment=StringParser("*", SymbolSegment, name="star", type="star"),
    TildeSegment=StringParser("~", SymbolSegment, name="tilde", type="tilde"),
    CastOperatorSegment=StringParser(
        "::", SymbolSegment, name="casting_operator", type="casting_operator"
    ),
    PlusSegment=StringParser("+", SymbolSegment, name="plus", type="binary_operator"),
    MinusSegment=StringParser("-", SymbolSegment, name="minus", type="binary_operator"),
    PositiveSegment=StringParser(
        "+", SymbolSegment, name="positive", type="sign_indicator"
    ),
    NegativeSegment=StringParser(
        "-", SymbolSegment, name="negative", type="sign_indicator"
    ),
    DivideSegment=StringParser(
        "/", SymbolSegment, name="divide", type="binary_operator"
    ),
    MultiplySegment=StringParser(
        "*", SymbolSegment, name="multiply", type="binary_operator"
    ),
    ModuloSegment=StringParser(
        "%", SymbolSegment, name="modulo", type="binary_operator"
    ),
    SlashSegment=StringParser("/", SymbolSegment, name="slash", type="slash"),
    ConcatSegment=StringParser(
        "||", SymbolSegment, name="concatenate", type="binary_operator"
    ),
    BitwiseAndSegment=StringParser(
        "&", SymbolSegment, name="binary_and", type="binary_operator"
    ),
    BitwiseOrSegment=StringParser(
        "|", SymbolSegment, name="binary_or", type="binary_operator"
    ),
    BitwiseXorSegment=StringParser(
        "^", SymbolSegment, name="binary_xor", type="binary_operator"
    ),
    EqualsSegment=StringParser(
        "=", SymbolSegment, name="equals", type="comparison_operator"
    ),
    LikeOperatorSegment=NamedParser(
        "like_operator", SymbolSegment, name="like_operator", type="comparison_operator"
    ),
    GreaterThanSegment=StringParser(
        ">", SymbolSegment, name="greater_than", type="comparison_operator"
    ),
    LessThanSegment=StringParser(
        "<", SymbolSegment, name="less_than", type="comparison_operator"
    ),
    GreaterThanOrEqualToSegment=StringParser(
        ">=", SymbolSegment, name="greater_than_equal_to", type="comparison_operator"
    ),
    LessThanOrEqualToSegment=StringParser(
        "<=", SymbolSegment, name="less_than_equal_to", type="comparison_operator"
    ),
    NotEqualToSegment_a=StringParser(
        "!=", SymbolSegment, name="not_equal_to", type="comparison_operator"
    ),
    NotEqualToSegment_b=StringParser(
        "<>", SymbolSegment, name="not_equal_to", type="comparison_operator"
    ),
    # The following functions can be called without parentheses per ANSI specification
    BareFunctionSegment=SegmentGenerator(
        lambda dialect: RegexParser(
            r"^(" + r"|".join(dialect.sets("bare_functions")) + r")$",
            CodeSegment,
            name="bare_function",
            type="bare_function",
        )
    ),
    # The strange regex here it to make sure we don't accidentally match numeric literals. We
    # also use a regex to explicitly exclude disallowed keywords.
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z0-9_]*[A-Z][A-Z0-9_]*",
            CodeSegment,
            name="naked_identifier",
            type="identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    VersionIdentifierSegment=RegexParser(
        r"[A-Z0-9_.]*", CodeSegment, name="version", type="identifier"
    ),
    ParameterNameSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*", CodeSegment, name="parameter", type="parameter"
    ),
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*",
        CodeSegment,
        name="function_name_identifier",
        type="function_name_identifier",
    ),
    # Maybe data types should be more restrictive?
    DatatypeIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z][A-Z0-9_]*",
            CodeSegment,
            name="data_type_identifier",
            type="data_type_identifier",
            anti_template=r"^(NOT)$",  # TODO - this is a stopgap until we implement explicit data types
        ),
    ),
    # Ansi Intervals
    DatetimeUnitSegment=SegmentGenerator(
        lambda dialect: RegexParser(
            r"^(" + r"|".join(dialect.sets("datetime_units")) + r")$",
            CodeSegment,
            name="date_part",
            type="date_part",
        )
    ),
    QuotedIdentifierSegment=NamedParser(
        "double_quote", CodeSegment, name="quoted_identifier", type="identifier"
    ),
    QuotedLiteralSegment=NamedParser(
        "single_quote", CodeSegment, name="quoted_literal", type="literal"
    ),
    NumericLiteralSegment=NamedParser(
        "numeric_literal", CodeSegment, name="numeric_literal", type="literal"
    ),
    # NullSegment is defined seperately to the keyword so we can give it a different type
    NullLiteralSegment=StringParser(
        "null", KeywordSegment, name="null_literal", type="literal"
    ),
    TrueSegment=StringParser(
        "true", KeywordSegment, name="boolean_literal", type="literal"
    ),
    FalseSegment=StringParser(
        "false", KeywordSegment, name="boolean_literal", type="literal"
    ),
    # We use a GRAMMAR here not a Segment. Otherwise we get an unnecessary layer
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"), Ref("QuotedIdentifierSegment")
    ),
    BooleanLiteralGrammar=OneOf(Ref("TrueSegment"), Ref("FalseSegment")),
    # We specifically define a group of arithmetic operators to make it easier to override this
    # if some dialects have different available operators
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
    StringBinaryOperatorGrammar=OneOf(Ref("ConcatSegment")),
    BooleanBinaryOperatorGrammar=OneOf(
        Ref("AndKeywordSegment"), Ref("OrKeywordSegment")
    ),
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment_a"),
        Ref("NotEqualToSegment_b"),
        Ref("LikeOperatorSegment"),
    ),
    # hookpoint for other dialects
    # e.g. EXASOL str to date cast with DATE '2021-01-01'
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "TIME", "TIMESTAMP", "INTERVAL"), Ref("QuotedLiteralSegment")
    ),
    LiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("NumericLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
        Ref("QualifiedNumericLiteralSegment"),
        # NB: Null is included in the literals, because it is a keyword which
        # can otherwise be easily mistaken for an identifier.
        Ref("NullLiteralSegment"),
        Ref("DateTimeLiteralGrammar"),
    ),
    AndKeywordSegment=StringParser("and", KeywordSegment, type="binary_operator"),
    OrKeywordSegment=StringParser("or", KeywordSegment, type="binary_operator"),
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
            ephemeral_name="ColumnReferenceList",
        )
    ),
    OrReplaceGrammar=Sequence("OR", "REPLACE"),
    TemporaryTransientGrammar=OneOf("TRANSIENT", Ref("TemporaryGrammar")),
    TemporaryGrammar=OneOf("TEMP", "TEMPORARY"),
    IfExistsGrammar=Sequence("IF", "EXISTS"),
    IfNotExistsGrammar=Sequence("IF", "NOT", "EXISTS"),
    LikeGrammar=OneOf("LIKE", "RLIKE", "ILIKE"),
    IsClauseGrammar=OneOf(
        "NULL",
        "NAN",
        Ref("BooleanLiteralGrammar"),
    ),
    SelectClauseSegmentGrammar=Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
            allow_trailing=True,
        ),
        # NB: The Dedent for the indent above lives in the
        # SelectStatementSegment so that it sits in the right
        # place corresponding to the whitespace.
    ),
    SelectClauseElementTerminatorGrammar=OneOf(
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        Ref("CommaSegment"),
        Ref("SetOperatorSegment"),
    ),
    # Define these as grammars to allow child dialects to enable them (since they are non-standard
    # keywords)
    IsNullGrammar=Nothing(),
    NotNullGrammar=Nothing(),
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
    ),
    WhereClauseTerminatorGrammar=OneOf(
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "QUALIFY",
        "WINDOW",
        "OVERLAPS",
    ),
    PrimaryKeyGrammar=Sequence("PRIMARY", "KEY"),
    ForeignKeyGrammar=Sequence("FOREIGN", "KEY"),
    # Odd syntax, but prevents eager parameters being confused for data types
    FunctionParameterGrammar=OneOf(
        Sequence(
            Ref("ParameterNameSegment", optional=True),
            OneOf(Sequence("ANY", "TYPE"), Ref("DatatypeSegment")),
        ),
        OneOf(Sequence("ANY", "TYPE"), Ref("DatatypeSegment")),
    ),
    # This is a placeholder for other dialects.
    SimpleArrayTypeGrammar=Nothing(),
    BaseExpressionElementGrammar=OneOf(
        Ref("LiteralGrammar"),
        Ref("BareFunctionSegment"),
        Ref("IntervalExpressionSegment"),
        Ref("FunctionSegment"),
        Ref("ColumnReferenceSegment"),
        Ref("ExpressionSegment"),
    ),
    FilterClauseGrammar=Sequence(
        "FILTER", Bracketed(Sequence("WHERE", Ref("ExpressionSegment")))
    ),
    FrameClauseUnitGrammar=OneOf("ROWS", "RANGE"),
    # It's as a sequence to allow to parametrize that in Postgres dialect with LATERAL
    JoinKeywords=Sequence("JOIN"),
    TableConstraintReferenceOptionGrammar=OneOf(
        "RESTRICT",
        "CASCADE",
        Sequence("SET", "NULL"),
        Sequence("NO", "ACTION"),
        Sequence("SET", "DEFAULT"),
    ),
)


@ansi_dialect.segment()
class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    parse_grammar = Delimited(
        Ref("StatementSegment"),
        delimiter=AnyNumberOf(Ref("DelimiterSegment"), min_times=1),
        allow_gaps=True,
        allow_trailing=True,
    )


@ansi_dialect.segment()
class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment."""

    type = "interval_expression"
    match_grammar = Sequence(
        "INTERVAL",
        OneOf(
            # The Numeric Version
            Sequence(
                Ref("NumericLiteralSegment"),
                OneOf(Ref("QuotedLiteralSegment"), Ref("DatetimeUnitSegment")),
            ),
            # The String version
            Ref("QuotedLiteralSegment"),
        ),
    )


@ansi_dialect.segment()
class ArrayLiteralSegment(BaseSegment):
    """An array literal segment."""

    type = "array_literal"
    match_grammar = Bracketed(
        Delimited(Ref("ExpressionSegment"), optional=True),
        bracket_type="square",
    )


@ansi_dialect.segment()
class DatatypeSegment(BaseSegment):
    """A data type segment.

    Supports timestamp with(out) time zone. Doesn't currently support intervals.
    """

    type = "data_type"
    match_grammar = OneOf(
        Sequence(
            OneOf("time", "timestamp"),
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
                    # Some dialects allow optional qualification of data types with schemas
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
            Bracketed(
                OneOf(
                    Delimited(Ref("ExpressionSegment")),
                    # The brackets might be empty for some cases...
                    optional=True,
                ),
                # There may be no brackets for some data types
                optional=True,
            ),
            Ref("CharCharacterSetSegment", optional=True),
        ),
    )


# hookpoint
ansi_dialect.add(CharCharacterSetSegment=Nothing())


@ansi_dialect.segment()
class ObjectReferenceSegment(BaseSegment):
    """A reference to an object."""

    type = "object_reference"
    # match grammar (don't allow whitespace)
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
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

    def is_qualified(self):
        """Return if there is more than one element to the reference."""
        return len(list(self.iter_raw_references())) > 1

    def qualification(self):
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

    @staticmethod
    def _level_to_int(level: Union[ObjectReferenceLevel, int]) -> int:
        # If it's an ObjectReferenceLevel, get the value. Otherwise, assume it's
        # an int.
        level = getattr(level, "value", level)
        assert isinstance(level, int)
        return level


@ansi_dialect.segment()
class TableReferenceSegment(ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias."""

    type = "table_reference"


@ansi_dialect.segment()
class SchemaReferenceSegment(ObjectReferenceSegment):
    """A reference to a schema."""

    type = "schema_reference"


@ansi_dialect.segment()
class DatabaseReferenceSegment(ObjectReferenceSegment):
    """A reference to a database."""

    type = "database_reference"


@ansi_dialect.segment()
class IndexReferenceSegment(ObjectReferenceSegment):
    """A reference to an index."""

    type = "index_reference"


@ansi_dialect.segment()
class ExtensionReferenceSegment(ObjectReferenceSegment):
    """A reference to an extension."""

    type = "extension_reference"


@ansi_dialect.segment()
class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias."""

    type = "column_reference"


@ansi_dialect.segment()
class SequenceReferenceSegment(ObjectReferenceSegment):
    """A reference to a sequence."""

    type = "sequence_reference"


@ansi_dialect.segment()
class TriggerReferenceSegment(ObjectReferenceSegment):
    """A reference to a trigger."""

    type = "trigger_reference"


@ansi_dialect.segment()
class SingleIdentifierListSegment(BaseSegment):
    """A comma delimited list of identifiers."""

    type = "identifier_list"
    match_grammar = Delimited(Ref("SingleIdentifierGrammar"))


@ansi_dialect.segment()
class ArrayAccessorSegment(BaseSegment):
    """An array accessor e.g. [3:4]."""

    type = "array_accessor"
    match_grammar = Bracketed(
        Delimited(
            OneOf(Ref("NumericLiteralSegment"), Ref("ExpressionSegment")),
            delimiter=Ref("SliceSegment"),
            ephemeral_name="ArrayAccessorContent",
        ),
        bracket_type="square",
    )


@ansi_dialect.segment()
class AliasedObjectReferenceSegment(BaseSegment):
    """A reference to an object with an `AS` clause."""

    type = "object_reference"
    match_grammar = Sequence(
        Ref("ObjectReferenceSegment"), Ref("AliasExpressionSegment")
    )


ansi_dialect.add(
    # This is a hook point to allow subclassing for other dialects
    AliasedTableReferenceGrammar=Sequence(
        Ref("TableReferenceSegment"), Ref("AliasExpressionSegment")
    )
)


@ansi_dialect.segment()
class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    """

    type = "alias_expression"
    match_grammar = Sequence(
        Ref.keyword("AS", optional=True),
        OneOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                # Column alias in VALUES clause
                Bracketed(Ref("SingleIdentifierListSegment"), optional=True),
            ),
            Ref("QuotedLiteralSegment"),
        ),
    )


@ansi_dialect.segment()
class ShorthandCastSegment(BaseSegment):
    """A casting operation using '::'."""

    type = "cast_expression"
    match_grammar = Sequence(
        Ref("CastOperatorSegment"), Ref("DatatypeSegment"), allow_gaps=False
    )


@ansi_dialect.segment()
class QualifiedNumericLiteralSegment(BaseSegment):
    """A numeric literal with a + or - sign preceding.

    The qualified numeric literal is a compound of a raw
    literal and a plus/minus sign. We do it this way rather
    than at the lexing step because the lexer doesn't deal
    well with ambiguity.
    """

    type = "numeric_literal"
    match_grammar = Sequence(
        OneOf(Ref("PlusSegment"), Ref("MinusSegment")),
        Ref("NumericLiteralSegment"),
        allow_gaps=False,
    )


ansi_dialect.add(
    # FunctionContentsExpressionGrammar intended as a hook to override
    # in other dialects.
    FunctionContentsExpressionGrammar=Ref("ExpressionSegment"),
    FunctionContentsGrammar=AnyNumberOf(
        Ref("ExpressionSegment"),
        # A Cast-like function
        Sequence(Ref("ExpressionSegment"), "AS", Ref("DatatypeSegment")),
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
            "OrderByClauseSegment"
        ),  # used by string_agg (postgres), group_concat (exasol), listagg (snowflake)...
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
        Sequence(OneOf("IGNORE", "RESPECT"), "NULLS"),
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


@ansi_dialect.segment()
class OverClauseSegment(BaseSegment):
    """An OVER clause for window functions."""

    type = "over_clause"
    match_grammar = Sequence(
        "OVER",
        OneOf(
            Ref("SingleIdentifierGrammar"),  # Window name
            Bracketed(
                Ref("WindowSpecificationSegment", optional=True),
            ),
        ),
    )


@ansi_dialect.segment()
class WindowSpecificationSegment(BaseSegment):
    """Window specification within OVER(...)."""

    type = "window_specification"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar", optional=True),  # "Base" window name
        Ref("PartitionClauseSegment", optional=True),
        Ref("OrderByClauseSegment", optional=True),
        Ref("FrameClauseSegment", optional=True),
        optional=True,
        ephemeral_name="OverClauseContent",
    )


@ansi_dialect.segment()
class FunctionNameSegment(BaseSegment):
    """Function name, including any prefix bits, e.g. project or schema."""

    type = "function_name"
    match_grammar = Sequence(
        # Project name, schema identifier, etc.
        AnyNumberOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Ref("DotSegment"),
            ),
        ),
        # Base function name
        OneOf(
            Ref("FunctionNameIdentifierSegment"),
            Ref("QuotedIdentifierSegment"),
        ),
        allow_gaps=False,
    )


@ansi_dialect.segment()
class DatePartClause(BaseSegment):
    """DatePart clause for use within DATEADD() or related functions."""

    type = "date_part"

    match_grammar = OneOf(
        "DAY",
        "DAYOFYEAR",
        "HOUR",
        "MINUTE",
        "MONTH",
        "QUARTER",
        "SECOND",
        "WEEK",
        "WEEKDAY",
        "YEAR",
    )


@ansi_dialect.segment()
class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    type = "function"
    match_grammar = OneOf(
        Sequence(
            Sequence(
                Ref("DatePartFunctionNameSegment"),
                Bracketed(
                    Delimited(
                        Ref("DatePartClause"),
                        Ref(
                            "FunctionContentsGrammar",
                            # The brackets might be empty for some functions...
                            optional=True,
                            ephemeral_name="FunctionContentsGrammar",
                        ),
                    )
                ),
            )
        ),
        Sequence(
            Sequence(
                AnyNumberOf(
                    Ref("FunctionNameSegment"),
                    max_times=1,
                    min_times=1,
                    exclude=Ref("DatePartFunctionNameSegment"),
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
            Ref("PostFunctionGrammar", optional=True),
        ),
    )


@ansi_dialect.segment()
class PartitionClauseSegment(BaseSegment):
    """A `PARTITION BY` for window functions."""

    type = "partitionby_clause"
    match_grammar = StartsWith(
        "PARTITION",
        terminator=OneOf("ORDER", Ref("FrameClauseUnitGrammar")),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "PARTITION",
        "BY",
        Indent,
        # Brackets are optional in a partition by statement
        OptionallyBracketed(Delimited(Ref("ExpressionSegment"))),
        Dedent,
    )


@ansi_dialect.segment()
class FrameClauseSegment(BaseSegment):
    """A frame clause for window functions.

    As specified in https://docs.oracle.com/cd/E17952_01/mysql-8.0-en/window-functions-frames.html
    """

    type = "frame_clause"

    _frame_extent = OneOf(
        Sequence("CURRENT", "ROW"),
        Sequence(
            OneOf(Ref("NumericLiteralSegment"), "UNBOUNDED"),
            OneOf("PRECEDING", "FOLLOWING"),
        ),
    )

    match_grammar = Sequence(
        Ref("FrameClauseUnitGrammar"),
        OneOf(_frame_extent, Sequence("BETWEEN", _frame_extent, "AND", _frame_extent)),
    )


ansi_dialect.add(
    # This is a hook point to allow subclassing for other dialects
    PostTableExpressionGrammar=Nothing()
)


@ansi_dialect.segment()
class FromExpressionElementSegment(BaseSegment):
    """A table expression."""

    type = "from_expression_element"
    match_grammar = Sequence(
        Ref("PreTableFunctionKeywordsGrammar", optional=True),
        OptionallyBracketed(Ref("TableExpressionSegment")),
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#flattening_arrays
        Sequence("WITH", "OFFSET", optional=True),
        OneOf(
            Sequence(Ref("AliasExpressionSegment"), Ref("SamplingExpressionSegment")),
            Ref("SamplingExpressionSegment"),
            Ref("AliasExpressionSegment"),
            optional=True,
        ),
        Ref("PostTableExpressionGrammar", optional=True),
    )

    def get_eventual_alias(self) -> Optional[AliasInfo]:
        """Return the eventual table name referred to by this table expression.

        Returns:
            :obj:`tuple` of (:obj:`str`, :obj:`BaseSegment`, :obj:`bool`) containing
                a string representation of the alias, a reference to the
                segment containing it, and whether it's an alias.

        """
        alias_expression = self.get_child("alias_expression")
        tbl_expression = self.get_child("table_expression")
        if not tbl_expression:  # pragma: no cover
            tbl_expression = self.get_child("bracketed").get_child("table_expression")
        ref = tbl_expression.get_child("object_reference")
        if alias_expression:
            # If it has an alias, return that
            segment = alias_expression.get_child("identifier")
            return AliasInfo(segment.raw, segment, True, self, alias_expression, ref)

        # If not return the object name (or None if there isn't one)
        # ref = self.get_child("object_reference")
        if ref:
            # Return the last element of the reference.
            penultimate_ref: ObjectReferenceSegment.ObjectReferencePart = list(
                ref.iter_raw_references()
            )[-1]
            return AliasInfo(
                penultimate_ref.part,
                penultimate_ref.segments[0],
                False,
                self,
                None,
                ref,
            )
        # No references or alias, return None
        return None


@ansi_dialect.segment()
class FromExpressionSegment(BaseSegment):
    """A from expression segment."""

    type = "from_expression"
    match_grammar = Sequence(
        Indent,
        OneOf(
            # check first for MLTableExpression, because of possible FunctionSegment in MainTableExpression
            Ref("MLTableExpressionSegment"),
            Ref("FromExpressionElementSegment"),
        ),
        Conditional(Dedent, indented_joins=False),
        AnyNumberOf(
            Ref("JoinClauseSegment"), Ref("JoinLikeClauseGrammar"), optional=True
        ),
        Conditional(Dedent, indented_joins=True),
    )


@ansi_dialect.segment()
class TableExpressionSegment(BaseSegment):
    """The main table expression e.g. within a FROM clause."""

    type = "table_expression"
    match_grammar = OneOf(
        Ref("BareFunctionSegment"),
        Ref("FunctionSegment"),
        Ref("TableReferenceSegment"),
        # Nested Selects
        Bracketed(Ref("SelectableGrammar")),
        # Values clause?
    )


@ansi_dialect.segment()
class WildcardIdentifierSegment(ObjectReferenceSegment):
    """Any identifier of the form a.b.*.

    This inherits iter_raw_references from the
    ObjectReferenceSegment.
    """

    type = "wildcard_identifier"
    match_grammar = Sequence(
        # *, blah.*, blah.blah.*, etc.
        AnyNumberOf(
            Sequence(Ref("SingleIdentifierGrammar"), Ref("DotSegment"), allow_gaps=True)
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


@ansi_dialect.segment()
class WildcardExpressionSegment(BaseSegment):
    """A star (*) expression for a SELECT clause.

    This is separate from the identifier to allow for
    some dialects which extend this logic to allow
    REPLACE, EXCEPT or similar clauses e.g. BigQuery.
    """

    type = "wildcard_expression"
    match_grammar = Sequence(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardIdentifierSegment")
    )


@ansi_dialect.segment()
class SelectClauseElementSegment(BaseSegment):
    """An element in the targets of a select statement."""

    type = "select_clause_element"
    # Important to split elements before parsing, otherwise debugging is really hard.
    match_grammar = GreedyUntil(
        Ref("SelectClauseElementTerminatorGrammar"),
        enforce_whitespace_preceding_terminator=True,
    )

    parse_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            Ref("BaseExpressionElementGrammar"),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )


@ansi_dialect.segment()
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = OneOf(
        "DISTINCT",
        "ALL",
    )


@ansi_dialect.segment()
class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement."""

    type = "select_clause"
    match_grammar = StartsWith(
        Sequence("SELECT", Ref("WildcardExpressionSegment", optional=True)),
        terminator=OneOf(
            "FROM",
            "WHERE",
            Sequence("ORDER", "BY"),
            "LIMIT",
            "OVERLAPS",
            Ref("SetOperatorSegment"),
        ),
        enforce_whitespace_preceding_terminator=True,
    )

    parse_grammar = Ref("SelectClauseSegmentGrammar")


@ansi_dialect.segment()
class JoinClauseSegment(BaseSegment):
    """Any number of join clauses, including the `JOIN` keyword."""

    type = "join_clause"
    match_grammar = Sequence(
        # NB These qualifiers are optional
        # TODO: Allow nested joins like:
        # ....FROM S1.T1 t1 LEFT JOIN ( S2.T2 t2 JOIN S3.T3 t3 ON t2.col1=t3.col1) ON tab1.col1 = tab2.col1
        OneOf(
            "CROSS",
            "INNER",
            Sequence(
                OneOf(
                    "FULL",
                    "LEFT",
                    "RIGHT",
                ),
                Ref.keyword("OUTER", optional=True),
            ),
            optional=True,
        ),
        Ref("JoinKeywords"),
        Indent,
        Sequence(
            Ref("FromExpressionElementSegment"),
            Conditional(Dedent, indented_using_on=False),
            # NB: this is optional
            OneOf(
                # ON clause
                Ref("JoinOnConditionSegment"),
                # USING clause
                Sequence(
                    "USING",
                    Indent,
                    Bracketed(
                        # NB: We don't use BracketedColumnReferenceListGrammar
                        # here because we're just using SingleIdentifierGrammar,
                        # rather than ObjectReferenceSegment or ColumnReferenceSegment.
                        # This is a) so that we don't lint it as a reference and
                        # b) because the column will probably be returned anyway
                        # during parsing.
                        Delimited(
                            Ref("SingleIdentifierGrammar"),
                            ephemeral_name="UsingClauseContents",
                        )
                    ),
                    Dedent,
                ),
                # Unqualified joins *are* allowed. They just might not
                # be a good idea.
                optional=True,
            ),
            Conditional(Indent, indented_using_on=False),
        ),
        Dedent,
    )

    def get_eventual_alias(self) -> AliasInfo:
        """Return the eventual table name referred to by this join clause."""
        from_expression_element = self.get_child("from_expression_element")
        return from_expression_element.get_eventual_alias()


@ansi_dialect.segment()
class JoinOnConditionSegment(BaseSegment):
    """The `ON` condition within a `JOIN` clause."""

    type = "join_on_condition"
    match_grammar = Sequence(
        "ON",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


ansi_dialect.add(
    # This is a hook point to allow subclassing for other dialects
    JoinLikeClauseGrammar=Nothing(),
)


@ansi_dialect.segment()
class FromClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT`.

    NOTE: this is a delimited set of table expressions, with a variable
    number of optional join clauses with those table expressions. The
    delmited aspect is the higher of the two such that the following is
    valid (albeit unusual):

    ```
    SELECT *
    FROM a JOIN b, c JOIN d
    ```
    """

    type = "from_clause"
    match_grammar = StartsWith(
        "FROM",
        terminator=Ref("FromClauseTerminatorGrammar"),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "FROM",
        Delimited(
            Ref("FromExpressionSegment"),
        ),
    )

    def get_eventual_aliases(self) -> List[Tuple[BaseSegment, AliasInfo]]:
        """List the eventual aliases of this from clause.

        Comes as a list of tuples (table expr, tuple (string, segment, bool)).
        """
        buff = []
        direct_table_children = []
        join_clauses = []

        for from_expression in self.get_children("from_expression"):
            direct_table_children += from_expression.get_children(
                "from_expression_element"
            )
            join_clauses += from_expression.get_children("join_clause")

        # Iterate through the potential sources of aliases
        for clause in (*direct_table_children, *join_clauses):
            ref: AliasInfo = clause.get_eventual_alias()
            # Only append if non null. A None reference, may
            # indicate a generator expression or similar.
            table_expr = (
                clause
                if clause in direct_table_children
                else clause.get_child("from_expression_element")
            )
            if ref:
                buff.append((table_expr, ref))
        return buff


@ansi_dialect.segment()
class CaseExpressionSegment(BaseSegment):
    """A `CASE WHEN` clause."""

    type = "case_expression"
    match_grammar = OneOf(
        Sequence(
            "CASE",
            Indent,
            AnyNumberOf(
                Sequence(
                    "WHEN",
                    Indent,
                    Ref("ExpressionSegment"),
                    "THEN",
                    Ref("ExpressionSegment"),
                    Dedent,
                )
            ),
            Sequence("ELSE", Indent, Ref("ExpressionSegment"), Dedent, optional=True),
            Dedent,
            "END",
        ),
        Sequence(
            "CASE",
            OneOf(Ref("ExpressionSegment")),
            Indent,
            AnyNumberOf(
                Sequence(
                    "WHEN",
                    Indent,
                    Ref("ExpressionSegment"),
                    "THEN",
                    Ref("ExpressionSegment"),
                    Dedent,
                )
            ),
            Sequence("ELSE", Indent, Ref("ExpressionSegment"), Dedent, optional=True),
            Dedent,
            "END",
        ),
    )


ansi_dialect.add(
    # Expression_A_Grammar https://www.cockroachlabs.com/docs/v20.2/sql-grammar.html#a_expr
    Expression_A_Grammar=Sequence(
        OneOf(
            Ref("Expression_C_Grammar"),
            Sequence(
                OneOf(
                    Ref("PositiveSegment"),
                    Ref("NegativeSegment"),
                    # Ref('TildeSegment'),
                    "NOT",
                    "PRIOR",  # used in CONNECT BY clauses (EXASOL, Snowflake, Postgres...)
                ),
                Ref("Expression_C_Grammar"),
            ),
        ),
        AnyNumberOf(
            OneOf(
                Sequence(
                    OneOf(
                        Sequence(
                            Ref.keyword("NOT", optional=True),
                            Ref("LikeGrammar"),
                        ),
                        Sequence(
                            Ref("BinaryOperatorGrammar"),
                            Ref.keyword("NOT", optional=True),
                        ),
                        # We need to add a lot more here...
                    ),
                    Ref("Expression_C_Grammar"),
                    Sequence(
                        Ref.keyword("ESCAPE"),
                        Ref("Expression_C_Grammar"),
                        optional=True,
                    ),
                ),
                Sequence(
                    Ref.keyword("NOT", optional=True),
                    "IN",
                    Bracketed(
                        OneOf(
                            Delimited(
                                Ref("Expression_A_Grammar"),
                            ),
                            Ref("SelectableGrammar"),
                            ephemeral_name="InExpression",
                        )
                    ),
                ),
                Sequence(
                    Ref.keyword("NOT", optional=True),
                    "IN",
                    Ref("FunctionSegment"),  # E.g. UNNEST()
                ),
                Sequence(
                    "IS",
                    Ref.keyword("NOT", optional=True),
                    Ref("IsClauseGrammar"),
                ),
                Ref("IsNullGrammar"),
                Ref("NotNullGrammar"),
                Sequence(
                    # e.g. NOT EXISTS, but other expressions could be met as
                    # well by inverting the condition with the NOT operator
                    "NOT",
                    Ref("Expression_C_Grammar"),
                ),
                Sequence(
                    Ref.keyword("NOT", optional=True),
                    "BETWEEN",
                    # In a between expression, we're restricted to arithmetic operations
                    # because if we look for all binary operators then we would match AND
                    # as both an operator and also as the delimiter within the BETWEEN
                    # expression.
                    Ref("Expression_C_Grammar"),
                    AnyNumberOf(
                        Sequence(
                            Ref("ArithmeticBinaryOperatorGrammar"),
                            Ref("Expression_C_Grammar"),
                        )
                    ),
                    "AND",
                    Ref("Expression_C_Grammar"),
                    AnyNumberOf(
                        Sequence(
                            Ref("ArithmeticBinaryOperatorGrammar"),
                            Ref("Expression_C_Grammar"),
                        )
                    ),
                ),
            )
        ),
    ),
    # CockroachDB defines Expression_B_Grammar. The SQLFluff implementation of
    # expression parsing pulls that logic into Expression_A_Grammar and so there's
    # currently no need to define Expression_B.
    # https://www.cockroachlabs.com/docs/v20.2/sql-grammar.htm#b_expr
    #
    # Expression_C_Grammar https://www.cockroachlabs.com/docs/v20.2/sql-grammar.htm#c_expr
    Expression_C_Grammar=OneOf(
        Sequence(
            "EXISTS", Bracketed(Ref("SelectStatementSegment"))
        ),  # should be first priority, otherwise EXISTS() would be matched as a function
        Sequence(
            OneOf(
                Ref("Expression_D_Grammar"),
                Ref("CaseExpressionSegment"),
            ),
            AnyNumberOf(Ref("ShorthandCastSegment")),
        ),
    ),
    # Expression_D_Grammar https://www.cockroachlabs.com/docs/v20.2/sql-grammar.htm#d_expr
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
                    ),
                    ephemeral_name="BracketedExpression",
                ),
            ),
            # Allow potential select statement without brackets
            Ref("SelectStatementSegment"),
            Ref("LiteralGrammar"),
            Ref("IntervalExpressionSegment"),
            Ref("ColumnReferenceSegment"),
            Sequence(
                Ref("SimpleArrayTypeGrammar", optional=True), Ref("ArrayLiteralSegment")
            ),
            Sequence(
                Ref("DatatypeSegment"),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("BooleanLiteralGrammar"),
                    Ref("NullLiteralSegment"),
                    Ref("DateTimeLiteralGrammar"),
                ),
            ),
        ),
        Ref("Accessor_Grammar", optional=True),
        allow_gaps=True,
    ),
    Accessor_Grammar=AnyNumberOf(Ref("ArrayAccessorSegment")),
)


@ansi_dialect.segment()
class BitwiseLShiftSegment(BaseSegment):
    """Bitwise left-shift operator."""

    type = "binary_operator"
    match_grammar = Sequence(
        Ref("LessThanSegment"), Ref("LessThanSegment"), allow_gaps=False
    )


@ansi_dialect.segment()
class BitwiseRShiftSegment(BaseSegment):
    """Bitwise right-shift operator."""

    type = "binary_operator"
    match_grammar = Sequence(
        Ref("GreaterThanSegment"), Ref("GreaterThanSegment"), allow_gaps=False
    )


@ansi_dialect.segment()
class ExpressionSegment(BaseSegment):
    """A expression, either arithmetic or boolean.

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
    match_grammar = Ref("Expression_A_Grammar")


@ansi_dialect.segment()
class WhereClauseSegment(BaseSegment):
    """A `WHERE` clause like in `SELECT` or `INSERT`."""

    type = "where_clause"
    match_grammar = StartsWith(
        "WHERE",
        terminator=Ref("WhereClauseTerminatorGrammar"),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "WHERE",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@ansi_dialect.segment()
class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`."""

    type = "orderby_clause"
    match_grammar = StartsWith(
        Sequence("ORDER", "BY"),
        terminator=OneOf(
            "LIMIT",
            "HAVING",
            "QUALIFY",
            # For window functions
            "WINDOW",
            Ref("FrameClauseUnitGrammar"),
            "SEPARATOR",
        ),
    )
    parse_grammar = Sequence(
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
            terminator=OneOf(Ref.keyword("LIMIT"), Ref("FrameClauseUnitGrammar")),
        ),
        Dedent,
    )


@ansi_dialect.segment()
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    type = "groupby_clause"
    match_grammar = StartsWith(
        Sequence("GROUP", "BY"),
        terminator=OneOf("ORDER", "LIMIT", "HAVING", "QUALIFY", "WINDOW"),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        Delimited(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
            ),
            terminator=OneOf("ORDER", "LIMIT", "HAVING", "QUALIFY", "WINDOW"),
        ),
        Dedent,
    )


@ansi_dialect.segment()
class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`."""

    type = "having_clause"
    match_grammar = StartsWith(
        "HAVING",
        terminator=OneOf("ORDER", "LIMIT", "QUALIFY", "WINDOW"),
        enforce_whitespace_preceding_terminator=True,
    )
    parse_grammar = Sequence(
        "HAVING",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@ansi_dialect.segment()
class LimitClauseSegment(BaseSegment):
    """A `LIMIT` clause like in `SELECT`."""

    type = "limit_clause"
    match_grammar = Sequence(
        "LIMIT",
        Indent,
        OneOf(
            Ref("NumericLiteralSegment"),
            Sequence(
                Ref("NumericLiteralSegment"), "OFFSET", Ref("NumericLiteralSegment")
            ),
            Sequence(
                Ref("NumericLiteralSegment"),
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
            ),
        ),
        Dedent,
    )


@ansi_dialect.segment()
class OverlapsClauseSegment(BaseSegment):
    """An `OVERLAPS` clause like in `SELECT."""

    type = "overlaps_clause"
    match_grammar = StartsWith(
        "OVERLAPS",
    )
    parse_grammar = Sequence(
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


@ansi_dialect.segment()
class NamedWindowSegment(BaseSegment):
    """A WINDOW clause."""

    type = "named_window"
    match_grammar = Sequence(
        "WINDOW",
        Delimited(
            Ref("NamedWindowExpressionSegment"),
        ),
    )


@ansi_dialect.segment()
class NamedWindowExpressionSegment(BaseSegment):
    """Named window expression."""

    type = "named_window_expression"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),  # Window name
        "AS",
        Bracketed(
            Ref("WindowSpecificationSegment"),
        ),
    )


@ansi_dialect.segment()
class ValuesClauseSegment(BaseSegment):
    """A `VALUES` clause like in `INSERT`."""

    type = "values_clause"
    match_grammar = Sequence(
        OneOf("VALUE", "VALUES"),
        Delimited(
            Bracketed(
                Delimited(
                    Ref("LiteralGrammar"),
                    Ref("IntervalExpressionSegment"),
                    Ref("FunctionSegment"),
                    Ref("BareFunctionSegment"),
                    "DEFAULT",  # not in `FROM` clause, rule?
                    ephemeral_name="ValuesClauseElements",
                )
            ),
        ),
        Ref("AliasExpressionSegment", optional=True),
    )


@ansi_dialect.segment()
class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    type = "select_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith(
        # NB: In bigquery, the select clause may include an EXCEPT, which
        # will also match the set operator, but by starting with the whole
        # select clause rather than just the SELECT keyword, we mitigate that
        # here.
        Ref("SelectClauseSegment"),
        terminator=OneOf(
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("WithDataClauseSegment"),
            Ref("OrderByClauseSegment"),
            Ref("LimitClauseSegment"),
            Ref("NamedWindowSegment"),
        ),
        enforce_whitespace_preceding_terminator=True,
    )

    parse_grammar = Sequence(
        Ref("SelectClauseSegment"),
        # Dedent for the indent in the select clause.
        # It's here so that it can come AFTER any whitespace.
        Dedent,
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("OverlapsClauseSegment", optional=True),
    )


@ansi_dialect.segment()
class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement."""

    type = "select_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith(
        # NB: In bigquery, the select clause may include an EXCEPT, which
        # will also match the set operator, but by starting with the whole
        # select clause rather than just the SELECT keyword, we mitigate that
        # here.
        Ref("SelectClauseSegment"),
        terminator=OneOf(
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("WithDataClauseSegment"),
        ),
        enforce_whitespace_preceding_terminator=True,
    )

    # Inherit most of the parse grammar from the original.
    parse_grammar = UnorderedSelectStatementSegment.parse_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ]
    )


ansi_dialect.add(
    # Things that behave like select statements
    SelectableGrammar=OneOf(
        Ref("WithCompoundStatementSegment"), Ref("NonWithSelectableGrammar")
    ),
    # Things that behave like select statements, which can form part of with expressions.
    NonWithSelectableGrammar=OneOf(
        Ref("SetExpressionSegment"),
        OptionallyBracketed(Ref("SelectStatementSegment")),
        Ref("NonSetSelectableGrammar"),
    ),
    # Things that do not behave like select statements, which can form part of with expressions.
    NonWithNonSelectableGrammar=OneOf(
        Ref("UpdateStatementSegment"),
        Ref("InsertStatementSegment"),
    ),
    # Things that behave like select statements, which can form part of set expressions.
    NonSetSelectableGrammar=OneOf(
        Ref("ValuesClauseSegment"),
        Ref("UnorderedSelectStatementSegment"),
        # If it's bracketed, we can have the full select statment here,
        # otherwise we can't because any order by clauses should belong
        # to the set expression.
        Bracketed(Ref("SelectStatementSegment")),
    ),
)


@ansi_dialect.segment()
class CTEDefinitionSegment(BaseSegment):
    """A CTE Definition from a WITH statement.

    `tab (col1,col2) AS (SELECT a,b FROM x)`
    """

    type = "common_table_expression"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),
        Bracketed(
            Ref("SingleIdentifierListSegment"),
            optional=True,
        ),
        "AS",
        Bracketed(
            # Ephemeral here to subdivide the query.
            Ref("SelectableGrammar", ephemeral_name="SelectableGrammar")
        ),
    )

    def get_identifier(self) -> BaseSegment:
        """Gets the identifier of this CTE.

        Note: it blindly get the first identifier it finds
        which given the structure of a CTE definition is
        usually the right one.
        """
        return self.get_child("identifier")


@ansi_dialect.segment()
class WithCompoundStatementSegment(BaseSegment):
    """A `SELECT` statement preceded by a selection of `WITH` clauses.

    `WITH tab (col1,col2) AS (SELECT a,b FROM x)`
    """

    type = "with_compound_statement"
    # match grammar
    match_grammar = StartsWith("WITH")
    parse_grammar = Sequence(
        "WITH",
        Ref.keyword("RECURSIVE", optional=True),
        Delimited(
            Ref("CTEDefinitionSegment"),
            terminator=Ref.keyword("SELECT"),
        ),
        OneOf(
            Ref("NonWithSelectableGrammar"),
            Ref("NonWithNonSelectableGrammar"),
        ),
    )


@ansi_dialect.segment()
class SetOperatorSegment(BaseSegment):
    """A set operator such as Union, Minus, Except or Intersect."""

    type = "set_operator"
    match_grammar = OneOf(
        Sequence("UNION", OneOf("DISTINCT", "ALL", optional=True)),
        "INTERSECT",
        "EXCEPT",
        "MINUS",
        exclude=Sequence("EXCEPT", Bracketed(Anything())),
    )


@ansi_dialect.segment()
class SetExpressionSegment(BaseSegment):
    """A set expression with either Union, Minus, Except or Intersect."""

    type = "set_expression"
    # match grammar
    match_grammar = Sequence(
        Ref("NonSetSelectableGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("SetOperatorSegment"),
                Ref("NonSetSelectableGrammar"),
            ),
            min_times=1,
        ),
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
        Ref("NamedWindowSegment", optional=True),
    )


@ansi_dialect.segment()
class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement."""

    type = "insert_statement"
    match_grammar = StartsWith("INSERT")
    parse_grammar = Sequence(
        "INSERT",
        # Maybe OVERWRITE is just snowflake?
        # (It's also Hive but that has full insert grammar implementation)
        Ref.keyword("OVERWRITE", optional=True),
        "INTO",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Ref("SelectableGrammar"),
    )


@ansi_dialect.segment()
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement."""

    type = "transaction_statement"
    match_grammar = Sequence(
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


@ansi_dialect.segment()
class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint_segment"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
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
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    # ?? Ref('IntervalExpressionSegment')
                ),
            ),
            Ref("PrimaryKeyGrammar"),
            "UNIQUE",  # UNIQUE
            "AUTO_INCREMENT",  # AUTO_INCREMENT (MySQL)
            "UNSIGNED",  # UNSIGNED (MySQL)
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar", optional=True),
            ),
            Ref("CommentClauseSegment"),
        ),
    )


@ansi_dialect.segment()
class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        Ref("DatatypeSegment"),  # Column type
        Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
        AnyNumberOf(
            Ref("ColumnConstraintSegment", optional=True),
        ),
    )


@ansi_dialect.segment()
class IndexColumnDefinitionSegment(BaseSegment):
    """A column definition for CREATE INDEX."""

    type = "index_column_definition"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        OneOf("ASC", "DESC", optional=True),
    )


@ansi_dialect.segment()
class TableConstraintSegment(BaseSegment):
    """A table constraint, e.g. for CREATE TABLE."""

    type = "table_constraint_segment"

    # Later add support for CHECK constraint, others?
    # e.g. CONSTRAINT constraint_1 PRIMARY KEY(column_1)
    match_grammar = Sequence(
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
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                # Later add support for [MATCH FULL/PARTIAL/SIMPLE] ?
                AnyNumberOf(
                    # ON DELETE clause, e.g. ON DELETE NO ACTION
                    Sequence(
                        "ON",
                        "DELETE",
                        Ref("TableConstraintReferenceOptionGrammar"),
                    ),
                    # ON UPDATE clause, e.g. ON UPDATE SET NULL
                    Sequence(
                        "ON",
                        "UPDATE",
                        Ref("TableConstraintReferenceOptionGrammar"),
                    ),
                ),
            ),
        ),
    )


@ansi_dialect.segment()
class TableEndClauseSegment(BaseSegment):
    """Allow for additional table endings.

    (like WITHOUT ROWID for SQLite)
    """

    type = "table_end_clause_segment"
    match_grammar = Nothing()


@ansi_dialect.segment()
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
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


@ansi_dialect.segment()
class CommentClauseSegment(BaseSegment):
    """A comment clause.

    e.g. COMMENT 'view/table/column description'
    """

    type = "comment_clause"
    match_grammar = Sequence("COMMENT", Ref("QuotedLiteralSegment"))


@ansi_dialect.segment()
class CreateSchemaStatementSegment(BaseSegment):
    """A `CREATE SCHEMA` statement."""

    type = "create_schema_statement"
    match_grammar = Sequence(
        "CREATE",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
    )


@ansi_dialect.segment()
class SetSchemaStatementSegment(BaseSegment):
    """A `SET SCHEMA` statement."""

    type = "set_schema_statement"
    match_grammar = Sequence(
        "SET",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
    )


@ansi_dialect.segment()
class DropSchemaStatementSegment(BaseSegment):
    """A `DROP SCHEMA` statement."""

    type = "drop_schema_statement"
    match_grammar = Sequence(
        "DROP",
        "SCHEMA",
        Ref("IfExistsGrammar", optional=True),
        Ref("SchemaReferenceSegment"),
        OneOf("RESTRICT", "CASCADE", optional=True),
    )


@ansi_dialect.segment()
class DropTypeStatementSegment(BaseSegment):
    """A `DROP TYPE` statement."""

    type = "drop_type_statement"
    match_grammar = Sequence(
        "DROP",
        "TYPE",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf("RESTRICT", "CASCADE", optional=True),
    )


@ansi_dialect.segment()
class CreateDatabaseStatementSegment(BaseSegment):
    """A `CREATE DATABASE` statement."""

    type = "create_database_statement"
    match_grammar = Sequence(
        "CREATE",
        "DATABASE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
    )


@ansi_dialect.segment()
class CreateExtensionStatementSegment(BaseSegment):
    """A `CREATE EXTENSION` statement.

    https://www.postgresql.org/docs/9.1/sql-createextension.html
    """

    type = "create_extension_statement"
    match_grammar = Sequence(
        "CREATE",
        "EXTENSION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ExtensionReferenceSegment"),
        Ref.keyword("WITH", optional=True),
        Sequence("SCHEMA", Ref("SchemaReferenceSegment"), optional=True),
        Sequence("VERSION", Ref("VersionIdentifierSegment"), optional=True),
        Sequence("FROM", Ref("VersionIdentifierSegment"), optional=True),
    )


@ansi_dialect.segment()
class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` statement."""

    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
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


@ansi_dialect.segment()
class AlterTableStatementSegment(BaseSegment):
    """An `ALTER TABLE` statement."""

    type = "alter_table_statement"
    # Based loosely on:
    # https://dev.mysql.com/doc/refman/8.0/en/alter-table.html
    # TODO: Flesh this out with more detail.
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        Delimited(
            OneOf(
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
                        Sequence(
                            OneOf("FIRST", "AFTER"), Ref("ColumnReferenceSegment")
                        ),
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
        ),
    )


@ansi_dialect.segment()
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement."""

    type = "create_view_statement"
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html#create-view-statement
    # https://dev.mysql.com/doc/refman/8.0/en/create-view.html
    # https://www.postgresql.org/docs/12/sql-createview.html
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "VIEW",
        Ref("TableReferenceSegment"),
        # Optional list of column names
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        Ref("SelectableGrammar"),
        Ref("WithNoSchemaBindingClauseSegment", optional=True),
    )


@ansi_dialect.segment()
class DropStatementSegment(BaseSegment):
    """A `DROP` statement."""

    type = "drop_statement"
    # DROP {TABLE | VIEW} <Table name> [IF EXISTS} {RESTRICT | CASCADE}
    match_grammar = Sequence(
        "DROP",
        OneOf(
            "TABLE",
            "VIEW",
            "USER",
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf("RESTRICT", Ref.keyword("CASCADE", optional=True), optional=True),
    )


@ansi_dialect.segment()
class TruncateStatementSegment(BaseSegment):
    """`TRUNCATE TABLE` statement."""

    type = "truncate_table"

    match_grammar = Sequence(
        "TRUNCATE",
        Ref.keyword("TABLE", optional=True),
        Ref("TableReferenceSegment"),
    )


@ansi_dialect.segment()
class DropIndexStatementSegment(BaseSegment):
    """A `DROP INDEX` statement."""

    type = "drop_statement"
    # DROP INDEX <Index name> [CONCURRENTLY] [IF EXISTS] {RESTRICT | CASCADE}
    match_grammar = Sequence(
        "DROP",
        "INDEX",
        Ref.keyword("CONCURRENTLY", optional=True),
        Ref("IfExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        OneOf("RESTRICT", Ref.keyword("CASCADE", optional=True), optional=True),
    )


@ansi_dialect.segment()
class AccessStatementSegment(BaseSegment):
    """A `GRANT` or `REVOKE` statement.

    In order to help reduce code duplication we decided to implement other dialect specific grants (like Snowflake)
    here too which will help with maintainability. We also note that this causes the grammar to be less "correct",
    but the benefits outweigh the con in our opinion.


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

    # We reuse the object names above and simply append an `S` to the end of them to get plurals
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
            Delimited(Ref("ObjectReferenceSegment"), terminator=OneOf("TO", "FROM")),
            Ref("FunctionParameterListGrammar", optional=True),
        ),
        Sequence("LARGE", "OBJECT", Ref("NumericLiteralSegment")),
    )

    match_grammar = OneOf(
        # Based on https://www.postgresql.org/docs/13/sql-grant.html
        # and https://docs.snowflake.com/en/sql-reference/sql/grant-privilege.html
        Sequence(
            "GRANT",
            OneOf(
                Sequence(
                    Delimited(
                        OneOf(_global_permissions, _permissions),
                        delimiter=Ref("CommaSegment"),
                        terminator="ON",
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
                OneOf(Ref("ObjectReferenceSegment"), Ref("FunctionSegment"), "PUBLIC"),
                delimiter=Ref("CommaSegment"),
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
                        delimiter=Ref("CommaSegment"),
                        terminator="ON",
                    ),
                    "ON",
                    _objects,
                ),
                Sequence("ROLE", Ref("ObjectReferenceSegment")),
                Sequence("OWNERSHIP", "ON", "USER", Ref("ObjectReferenceSegment")),
            ),
            "FROM",
            OneOf("GROUP", "USER", "ROLE", "SHARE", optional=True),
            Delimited(
                Ref("ObjectReferenceSegment"),
                delimiter=Ref("CommaSegment"),
            ),
            OneOf("RESTRICT", Ref.keyword("CASCADE", optional=True), optional=True),
        ),
    )


@ansi_dialect.segment()
class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    DELETE FROM <table name> [ WHERE <search condition> ]
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith("DELETE")
    parse_grammar = Sequence(
        "DELETE",
        Ref("FromClauseSegment"),
        Ref("WhereClauseSegment", optional=True),
    )


@ansi_dialect.segment()
class UpdateStatementSegment(BaseSegment):
    """An `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    """

    type = "update_statement"
    match_grammar = StartsWith("UPDATE")
    parse_grammar = Sequence(
        "UPDATE",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
    )


@ansi_dialect.segment()
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
    match_grammar = Sequence(
        "SET",
        Indent,
        OneOf(
            Ref("SetClauseSegment"),
            # set clause
            AnyNumberOf(
                Delimited(Ref("SetClauseSegment")),
            ),
        ),
        Dedent,
    )


@ansi_dialect.segment()
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

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("EqualsSegment"),
        OneOf(
            Ref("LiteralGrammar"),
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Ref("ColumnReferenceSegment"),
            Ref("ExpressionSegment"),
            "DEFAULT",
        ),
        AnyNumberOf(Ref("ShorthandCastSegment")),
    )


@ansi_dialect.segment()
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement."""

    match_grammar = Sequence(
        "AS",
        Ref("QuotedLiteralSegment"),
        Sequence(
            "LANGUAGE",
            # Not really a parameter, but best fit for now.
            Ref("ParameterNameSegment"),
            optional=True,
        ),
    )


@ansi_dialect.segment()
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the ANSI dialect should be a "common subset" of the
    structure of the code for those dialects.
    postgres: https://www.postgresql.org/docs/9.1/sql-createfunction.html
    snowflake: https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    bigquery: https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",
        Anything(),
    )

    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


@ansi_dialect.segment()
class FunctionParameterListGrammar(BaseSegment):
    """The parameters for a function ie. `(string, number)`."""

    # Function parameter list
    match_grammar = Bracketed(
        Delimited(
            Ref("FunctionParameterGrammar"),
            delimiter=Ref("CommaSegment"),
            optional=True,
        ),
    )


@ansi_dialect.segment()
class CreateModelStatementSegment(BaseSegment):
    """A BigQuery `CREATE MODEL` statement."""

    type = "create_model_statement"
    # https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-create
    match_grammar = Sequence(
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


@ansi_dialect.segment()
class CreateTypeStatementSegment(BaseSegment):
    """A `CREATE TYPE` statement.

    This is based around the Postgres syntax.
    https://www.postgresql.org/docs/current/sql-createtype.html

    Note: This is relatively permissive currently
    and does not lint the syntax strictly, to allow
    for some deviation between dialects.
    """

    type = "create_type_statement"
    match_grammar = Sequence(
        "CREATE",
        "TYPE",
        Ref("ObjectReferenceSegment"),
        Sequence("AS", OneOf("ENUM", "RANGE", optional=True), optional=True),
        Bracketed(Delimited(Anything()), optional=True),
    )


@ansi_dialect.segment()
class CreateRoleStatementSegment(BaseSegment):
    """A `CREATE ROLE` statement.

    A very simple create role syntax which can be extended
    by other dialects.
    """

    type = "create_role_statement"
    match_grammar = Sequence(
        "CREATE",
        "ROLE",
        Ref("ObjectReferenceSegment"),
    )


@ansi_dialect.segment()
class DropModelStatementSegment(BaseSegment):
    """A `DROP MODEL` statement."""

    type = "drop_MODELstatement"
    # DROP MODEL <Model name> [IF EXISTS}
    # https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-drop-model
    match_grammar = Sequence(
        "DROP",
        "MODEL",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
    )


@ansi_dialect.segment()
class MLTableExpressionSegment(BaseSegment):
    """An ML table expression."""

    type = "ml_table_expression"
    # E.g. ML.WEIGHTS(MODEL `project.dataset.model`)
    match_grammar = Sequence(
        "ML",
        Ref("DotSegment"),
        Ref("SingleIdentifierGrammar"),
        Bracketed(
            Sequence("MODEL", Ref("ObjectReferenceSegment")),
            OneOf(
                Sequence(
                    Ref("CommaSegment"),
                    Bracketed(
                        Ref("SelectableGrammar"),
                    ),
                ),
                optional=True,
            ),
        ),
    )


@ansi_dialect.segment()
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"
    match_grammar = GreedyUntil(Ref("DelimiterSegment"))

    parse_grammar = OneOf(
        Ref("SelectableGrammar"),
        Ref("InsertStatementSegment"),
        Ref("TransactionStatementSegment"),
        Ref("DropStatementSegment"),
        Ref("TruncateStatementSegment"),
        Ref("AccessStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("CreateTypeStatementSegment"),
        Ref("CreateRoleStatementSegment"),
        Ref("AlterTableStatementSegment"),
        Ref("CreateSchemaStatementSegment"),
        Ref("SetSchemaStatementSegment"),
        Ref("DropSchemaStatementSegment"),
        Ref("DropTypeStatementSegment"),
        Ref("CreateDatabaseStatementSegment"),
        Ref("CreateExtensionStatementSegment"),
        Ref("CreateIndexStatementSegment"),
        Ref("DropIndexStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("DeleteStatementSegment"),
        Ref("UpdateStatementSegment"),
        Ref("CreateFunctionStatementSegment"),
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
    )

    def get_table_references(self):
        """Use parsed tree to extract table references."""
        table_refs = {
            tbl_ref.raw for tbl_ref in self.recursive_crawl("table_reference")
        }
        cte_refs = {
            cte_def.get_identifier().raw
            for cte_def in self.recursive_crawl("common_table_expression")
        }
        # External references are any table references which aren't
        # also cte aliases.
        return table_refs - cte_refs


@ansi_dialect.segment()
class WithNoSchemaBindingClauseSegment(BaseSegment):
    """WITH NO SCHEMA BINDING clause for Redshift's Late Binding Views.

    https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_VIEW.html
    """

    type = "with_no_schema_binding_clause"
    match_grammar = Sequence(
        "WITH",
        "NO",
        "SCHEMA",
        "BINDING",
    )


@ansi_dialect.segment()
class WithDataClauseSegment(BaseSegment):
    """WITH [NO] DATA clause for Postgres' MATERIALIZED VIEWS.

    https://www.postgresql.org/docs/9.3/sql-creatematerializedview.html
    """

    type = "with_data_clause"
    match_grammar = Sequence("WITH", Sequence("NO", optional=True), "DATA")


@ansi_dialect.segment()
class DescribeStatementSegment(BaseSegment):
    """A `Describe` statement.

    DESCRIBE <object type> <object name>
    """

    type = "describe_statement"
    match_grammar = StartsWith("DESCRIBE")

    parse_grammar = Sequence(
        "DESCRIBE",
        Ref("NakedIdentifierSegment"),
        Ref("ObjectReferenceSegment"),
    )


@ansi_dialect.segment()
class UseStatementSegment(BaseSegment):
    """A `USE` statement.

    USE [ ROLE ] <name>

    USE [ WAREHOUSE ] <name>

    USE [ DATABASE ] <name>

    USE [ SCHEMA ] [<db_name>.]<name>
    """

    type = "use_statement"
    match_grammar = StartsWith("USE")

    parse_grammar = Sequence(
        "USE",
        OneOf("ROLE", "WAREHOUSE", "DATABASE", "SCHEMA", optional=True),
        Ref("ObjectReferenceSegment"),
    )


@ansi_dialect.segment()
class ExplainStatementSegment(BaseSegment):
    """An `Explain` statement.

    EXPLAIN explainable_stmt
    """

    type = "explain_statement"

    explainable_stmt = OneOf(
        Ref("SelectableGrammar"),
        Ref("InsertStatementSegment"),
        Ref("UpdateStatementSegment"),
        Ref("DeleteStatementSegment"),
    )

    match_grammar = StartsWith("EXPLAIN")

    parse_grammar = Sequence(
        "EXPLAIN",
        explainable_stmt,
    )


@ansi_dialect.segment()
class CreateSequenceOptionsSegment(BaseSegment):
    """Options for Create Sequence statement.

    As specified in https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_6015.htm
    """

    type = "create_sequence_options_segment"

    match_grammar = OneOf(
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
        OneOf("ORDER", "NOORDER"),
    )


@ansi_dialect.segment()
class CreateSequenceStatementSegment(BaseSegment):
    """Create Sequence statement.

    As specified in https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_6015.htm
    """

    type = "create_sequence_statement"

    match_grammar = Sequence(
        "CREATE",
        "SEQUENCE",
        Ref("SequenceReferenceSegment"),
        AnyNumberOf(Ref("CreateSequenceOptionsSegment"), optional=True),
    )


@ansi_dialect.segment()
class AlterSequenceOptionsSegment(BaseSegment):
    """Options for Alter Sequence statement.

    As specified in https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_2011.htm
    """

    type = "alter_sequence_options_segment"

    match_grammar = OneOf(
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
        OneOf("ORDER", "NOORDER"),
    )


@ansi_dialect.segment()
class AlterSequenceStatementSegment(BaseSegment):
    """Alter Sequence Statement.

    As specified in https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_2011.htm
    """

    type = "alter_sequence_statement"

    match_grammar = Sequence(
        "ALTER",
        "SEQUENCE",
        Ref("SequenceReferenceSegment"),
        AnyNumberOf(Ref("AlterSequenceOptionsSegment")),
    )


@ansi_dialect.segment()
class DropSequenceStatementSegment(BaseSegment):
    """Drop Sequence Statement.

    As specified in https://docs.oracle.com/cd/E11882_01/server.112/e41084/statements_9001.htm
    """

    type = "drop_sequence_statement"

    match_grammar = Sequence("DROP", "SEQUENCE", Ref("SequenceReferenceSegment"))


@ansi_dialect.segment()
class DatePartFunctionNameSegment(BaseSegment):
    """DATEADD function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("DATEADD")


@ansi_dialect.segment()
class CreateTriggerStatementSegment(BaseSegment):
    """Create Trigger Statement.

    Taken from specification in https://www.postgresql.org/docs/14/sql-createtrigger.html
    Edited as per notes in above - what doesn't match ANSI
    """

    type = "create_trigger"

    match_grammar = Sequence("CREATE", "TRIGGER", Anything())

    parse_grammar = Sequence(
        "CREATE",
        "TRIGGER",
        Ref("TriggerReferenceSegment"),
        OneOf("BEFORE", "AFTER", Sequence("INSTEAD", "OF")),
        Delimited(
            "INSERT",
            "DELETE",
            Sequence(
                "UPDATE",
                "OF",
                Delimited(
                    Ref("ColumnReferenceSegment"),
                    terminator=OneOf("OR", "ON"),
                ),
            ),
            delimiter="OR",
            terminator="ON",
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
        ),
    )


@ansi_dialect.segment()
class DropTriggerStatementSegment(BaseSegment):
    """Drop Trigger Statement.

    Taken from specification in https://www.postgresql.org/docs/14/sql-droptrigger.html
    Edited as per notes in above - what doesn't match ANSI
    """

    type = "drop_trigger"

    match_grammar = Sequence("DROP", "TRIGGER", Ref("TriggerReferenceSegment"))


@ansi_dialect.segment()
class SamplingExpressionSegment(BaseSegment):
    """A sampling expression."""

    type = "sample_expression"
    match_grammar = Sequence(
        "TABLESAMPLE",
        OneOf("BERNOULLI", "SYSTEM"),
        Bracketed(Ref("NumericLiteralSegment")),
        Sequence(
            OneOf("REPEATABLE"),
            Bracketed(Ref("NumericLiteralSegment")),
            optional=True,
        ),
    )
