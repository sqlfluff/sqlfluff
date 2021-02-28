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

from typing import List, Tuple, NamedTuple, Optional

from sqlfluff.core.parser import (
    Matchable,
    BaseSegment,
    KeywordSegment,
    SymbolSegment,
    ReSegment,
    NamedSegment,
    Sequence,
    GreedyUntil,
    StartsWith,
    OneOf,
    Delimited,
    Bracketed,
    AnyNumberOf,
    Ref,
    SegmentGenerator,
    Anything,
    Indent,
    Dedent,
    Nothing,
)

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.ansi_keywords import (
    ansi_reserved_keywords,
    ansi_unreserved_keywords,
)


ansi_dialect = Dialect("ansi", root_segment_name="FileSegment")


ansi_dialect.set_lexer_struct(
    [
        # name, type, pattern, kwargs
        ("whitespace", "regex", r"[\t ]+", dict(type="whitespace")),
        (
            "inline_comment",
            "regex",
            r"(--|#)[^\n]*",
            dict(is_comment=True, type="comment", trim_start=("--", "#")),
        ),
        (
            "block_comment",
            "regex",
            r"\/\*([^\*]|\*(?!\/))*\*\/",
            dict(
                is_comment=True,
                type="comment",
                subdivide=dict(type="newline", name="newline", regex=r"\r\n|\n"),
                trim_post_subdivide=dict(
                    type="whitespace", name="whitespace", regex=r"[\t ]+"
                ),
            ),
        ),
        # Matches 0 or more characters surrounded by quotes that (aren't a quote or backslash) or a sequence of backslash followed by any character, aka an escaped character.
        ("single_quote", "regex", r"'([^'\\]|\\.)*'", dict(is_code=True)),
        ("double_quote", "regex", r'"([^"\\]|\\.)*"', dict(is_code=True)),
        ("back_quote", "regex", r"`[^`]*`", dict(is_code=True)),
        (
            "numeric_literal",
            "regex",
            r"([0-9]+(\.[0-9]+)?)|(\.[0-9]+)",
            dict(is_code=True),
        ),
        ("not_equal", "regex", r"!=|<>", dict(is_code=True)),
        ("greater_than_or_equal", "regex", r">=", dict(is_code=True)),
        ("less_than_or_equal", "regex", r"<=", dict(is_code=True)),
        ("newline", "regex", r"\r\n|\n", dict(type="newline")),
        ("casting_operator", "regex", r"::", dict(is_code=True)),
        ("concat_operator", "regex", r"\|\|", dict(is_code=True)),
        ("equals", "singleton", "=", dict(is_code=True)),
        ("greater_than", "singleton", ">", dict(is_code=True)),
        ("less_than", "singleton", "<", dict(is_code=True)),
        ("dot", "singleton", ".", dict(is_code=True)),
        ("comma", "singleton", ",", dict(is_code=True, type="comma")),
        ("plus", "singleton", "+", dict(is_code=True)),
        ("tilde", "singleton", "~", dict(is_code=True)),
        ("minus", "singleton", "-", dict(is_code=True)),
        ("divide", "singleton", "/", dict(is_code=True)),
        ("percent", "singleton", "%", dict(is_code=True)),
        ("star", "singleton", "*", dict(is_code=True)),
        ("bracket_open", "singleton", "(", dict(is_code=True)),
        ("bracket_close", "singleton", ")", dict(is_code=True)),
        ("sq_bracket_open", "singleton", "[", dict(is_code=True)),
        ("sq_bracket_close", "singleton", "]", dict(is_code=True)),
        ("crly_bracket_open", "singleton", "{", dict(is_code=True)),
        ("crly_bracket_close", "singleton", "}", dict(is_code=True)),
        ("colon", "singleton", ":", dict(is_code=True)),
        ("semicolon", "singleton", ";", dict(is_code=True)),
        ("code", "regex", r"[0-9a-zA-Z_]*", dict(is_code=True)),
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
# (name, startref, endref, definitely_bracket)
ansi_dialect.sets("bracket_pairs").update(
    [
        ("round", "StartBracketSegment", "EndBracketSegment", True),
        ("square", "StartSquareBracketSegment", "EndSquareBracketSegment", True),
        ("curly", "StartCurlyBracketSegment", "EndCurlyBracketSegment", True),
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
    SemicolonSegment=SymbolSegment.make(
        ";", name="semicolon", type="statement_terminator"
    ),
    ColonSegment=SymbolSegment.make(":", name="colon", type="colon"),
    SliceSegment=SymbolSegment.make(":", name="slice", type="slice"),
    StartBracketSegment=SymbolSegment.make(
        "(", name="start_bracket", type="start_bracket"
    ),
    EndBracketSegment=SymbolSegment.make(")", name="end_bracket", type="end_bracket"),
    StartSquareBracketSegment=SymbolSegment.make(
        "[", name="start_square_bracket", type="start_square_bracket"
    ),
    EndSquareBracketSegment=SymbolSegment.make(
        "]", name="end_square_bracket", type="end_square_bracket"
    ),
    StartCurlyBracketSegment=SymbolSegment.make(
        "{", name="start_curly_bracket", type="start_curly_bracket"
    ),
    EndCurlyBracketSegment=SymbolSegment.make(
        "}", name="end_curly_bracket", type="end_curly_bracket"
    ),
    CommaSegment=SymbolSegment.make(",", name="comma", type="comma"),
    DotSegment=SymbolSegment.make(".", name="dot", type="dot"),
    StarSegment=SymbolSegment.make("*", name="star", type="star"),
    TildeSegment=SymbolSegment.make("~", name="tilde", type="tilde"),
    CastOperatorSegment=SymbolSegment.make(
        "::", name="casting_operator", type="casting_operator"
    ),
    PlusSegment=SymbolSegment.make("+", name="plus", type="binary_operator"),
    MinusSegment=SymbolSegment.make("-", name="minus", type="binary_operator"),
    PositiveSegment=SymbolSegment.make("+", name="positive", type="sign_indicator"),
    NegativeSegment=SymbolSegment.make("-", name="negative", type="sign_indicator"),
    DivideSegment=SymbolSegment.make("/", name="divide", type="binary_operator"),
    MultiplySegment=SymbolSegment.make("*", name="multiply", type="binary_operator"),
    ModuloSegment=SymbolSegment.make("%", name="modulo", type="binary_operator"),
    ConcatSegment=SymbolSegment.make("||", name="concatenate", type="binary_operator"),
    EqualsSegment=SymbolSegment.make("=", name="equals", type="comparison_operator"),
    GreaterThanSegment=SymbolSegment.make(
        ">", name="greater_than", type="comparison_operator"
    ),
    LessThanSegment=SymbolSegment.make(
        "<", name="less_than", type="comparison_operator"
    ),
    GreaterThanOrEqualToSegment=SymbolSegment.make(
        ">=", name="greater_than_equal_to", type="comparison_operator"
    ),
    LessThanOrEqualToSegment=SymbolSegment.make(
        "<=", name="less_than_equal_to", type="comparison_operator"
    ),
    NotEqualToSegment_a=SymbolSegment.make(
        "!=", name="not_equal_to", type="comparison_operator"
    ),
    NotEqualToSegment_b=SymbolSegment.make(
        "<>", name="not_equal_to", type="comparison_operator"
    ),
    # The following functions can be called without parentheses per ANSI specification
    BareFunctionSegment=SegmentGenerator(
        lambda dialect: ReSegment.make(
            r"^(" + r"|".join(dialect.sets("bare_functions")) + r")$",
            name="bare_function",
            type="bare_function",
        )
    ),
    # The strange regex here it to make sure we don't accidentally match numeric literals. We
    # also use a regex to explicitly exclude disallowed keywords.
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: ReSegment.make(
            r"[A-Z0-9_]*[A-Z][A-Z0-9_]*",
            name="naked_identifier",
            type="identifier",
            _anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    VersionIdentifierSegment=ReSegment.make(
        r"[A-Z0-9_.]*", name="version", type="identifier"
    ),
    ParameterNameSegment=ReSegment.make(
        r"[A-Z][A-Z0-9_]*", name="parameter", type="parameter"
    ),
    FunctionNameSegment=ReSegment.make(
        r"[A-Z][A-Z0-9_]*", name="function_name", type="function_name"
    ),
    # Maybe data types should be more restrictive?
    DatatypeIdentifierSegment=ReSegment.make(
        r"[A-Z][A-Z0-9_]*", name="data_type_identifier", type="data_type_identifier"
    ),
    # Ansi Intervals
    DatetimeUnitSegment=SegmentGenerator(
        lambda dialect: ReSegment.make(
            r"^(" + r"|".join(dialect.sets("datetime_units")) + r")$",
            name="date_part",
            type="date_part",
        )
    ),
    QuotedIdentifierSegment=NamedSegment.make(
        "double_quote", name="quoted_identifier", type="identifier"
    ),
    QuotedLiteralSegment=NamedSegment.make(
        "single_quote", name="quoted_literal", type="literal"
    ),
    NumericLiteralSegment=NamedSegment.make(
        "numeric_literal", name="numeric_literal", type="literal"
    ),
    # NullSegment is defined seperately to the keyword so we can give it a different type
    NullLiteralSegment=KeywordSegment.make("null", name="null_literal", type="literal"),
    TrueSegment=KeywordSegment.make("true", name="boolean_literal", type="literal"),
    FalseSegment=KeywordSegment.make("false", name="boolean_literal", type="literal"),
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
    ),
    # hookpoint for other dialects
    # e.g. EXASOL str to date cast with DATE '2021-01-01'
    DateTimeLiteralGrammar=Nothing(),
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
    AndKeywordSegment=KeywordSegment.make("and", type="binary_operator"),
    OrKeywordSegment=KeywordSegment.make("or", type="binary_operator"),
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
    IfExistsGrammar=Sequence("IF", "EXISTS"),
    IfNotExistsGrammar=Sequence("IF", "NOT", "EXISTS"),
    LikeGrammar=OneOf("LIKE", "RLIKE", "ILIKE"),
    IsClauseGrammar=OneOf(
        "NULL",
        "NAN",
        "NOTNULL",
        "ISNULL",
        Ref("BooleanLiteralGrammar"),
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        "GROUP",
        "ORDER",
        "HAVING",
        "QUALIFY",
        "WINDOW",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
    ),
    WhereClauseTerminatorGrammar=OneOf(
        "LIMIT", "GROUP", "ORDER", "HAVING", "QUALIFY", "WINDOW"
    ),
    PrimaryKeyGrammar=Sequence("PRIMARY", "KEY"),
)


@ansi_dialect.segment()
class FileSegment(BaseSegment):
    """A segment representing a whole file or script.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    type = "file"
    # The file segment is the only one which can start or end with non-code
    can_start_end_non_code = True
    # A file can be empty!
    allow_empty = True

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    parse_grammar = Delimited(
        Ref("StatementSegment"),
        delimiter=Ref("SemicolonSegment"),
        allow_gaps=True,
        allow_trailing=True,
    )

    def get_table_references(self):
        """Use parsed tree to extract table references."""
        references = set()
        for stmt in self.get_children("statement"):
            references |= stmt.get_table_references()
        return references


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

    type = "array_literal_type"
    match_grammar = Bracketed(
        Delimited(Ref("ExpressionSegment")),
        bracket_type="square",
    )


@ansi_dialect.segment()
class DatatypeSegment(BaseSegment):
    """A data type segment."""

    type = "data_type"
    match_grammar = Sequence(
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
        delimiter=OneOf(Ref("DotSegment"), Sequence(Ref("DotSegment"))),
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
            Ref("SemicolonSegment"),
        ),
        allow_gaps=False,
    )

    @staticmethod
    def _iter_reference_parts(elem):
        """Extract the elements of a reference and yield."""
        # trim on quotes and split out any dots.
        for part in elem.raw_trimmed().split("."):
            yield part, elem

    def iter_raw_references(self):
        """Generate a list of reference strings and elements.

        Each element is a tuple of (str, segment). If some are
        split, then a segment may appear twice, but the substring
        will only appear once.
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

    def extract_reference(self, level):
        """Extract a reference of a given level.

        e.g. level 1 = the object.
        level 2 = the table
        level 3 = the schema
        etc...
        """
        refs = list(self.iter_raw_references())
        if len(refs) >= level:
            return refs[-level]
        return None


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


@ansi_dialect.segment()
class AliasedTableReferenceSegment(BaseSegment):
    """A reference to a table with an `AS` clause."""

    type = "table_reference"
    match_grammar = Sequence(
        Ref("TableReferenceSegment"), Ref("AliasExpressionSegment", optional=True)
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
            OneOf(Ref("QuotedLiteralSegment"), Ref("SingleIdentifierGrammar")),
            "IN",
            OneOf(Ref("QuotedLiteralSegment"), Ref("SingleIdentifierGrammar")),
        ),
    ),
    # Optional OVER suffix for window functions.
    # This is supported in biquery & postgres (and its derivatives)
    # and so is included here for now.
    PostFunctionGrammar=Sequence(
        Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
        Ref("OverClauseSegment"),
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
                Ref("WindowSpecificationSegment"),
            ),
        ),
    )


@ansi_dialect.segment()
class WindowSpecificationSegment(BaseSegment):
    """Window specification, e.g. OVER() or named window."""

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
            Sequence(
                # a stored function could be accessed by schema identifier
                Ref("SingleIdentifierGrammar"),
                Ref("DotSegment"),
                optional=True,
            ),
            Ref("FunctionNameSegment"),
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
    )


@ansi_dialect.segment()
class PartitionClauseSegment(BaseSegment):
    """A `PARTITION BY` for window functions."""

    type = "partitionby_clause"
    match_grammar = StartsWith(
        "PARTITION",
        terminator=OneOf("ORDER", "ROWS"),
        enforce_whitespace_preceeding_terminator=True,
    )
    parse_grammar = Sequence(
        "PARTITION",
        "BY",
        Indent,
        OneOf(
            # Brackets are optional in a partition by statement
            Bracketed(Delimited(Ref("ExpressionSegment"))),
            Delimited(Ref("ExpressionSegment")),
        ),
        Dedent,
    )


@ansi_dialect.segment()
class FrameClauseSegment(BaseSegment):
    """A frame clause for window functions."""

    type = "frame_clause"
    match_grammar = StartsWith("ROWS")
    # TODO: Expand a parse statement here properly to actually
    # parse rather than assuming that it's good.
    # parse_grammar = Sequence(
    #    'ROWS',
    #    ...
    # )


ansi_dialect.add(
    # This is a hook point to allow subclassing for other dialects
    PostTableExpressionGrammar=Nothing()
)


class AliasInfo(NamedTuple):
    """Details about a table alias."""

    ref_str: str  # Name given to the alias
    segment: BaseSegment  # Identifier segment containing the name
    aliased: bool
    table_expression: BaseSegment
    alias_expression: Optional[BaseSegment]


@ansi_dialect.segment()
class TableExpressionSegment(BaseSegment):
    """A table expression."""

    type = "table_expression"
    match_grammar = Sequence(
        Indent,
        Ref("PreTableFunctionKeywordsGrammar", optional=True),
        OneOf(
            Ref("MainTableExpressionSegment"),
            Bracketed(Ref("MainTableExpressionSegment")),
        ),
        Ref("AliasExpressionSegment", optional=True),
        Ref("PostTableExpressionGrammar", optional=True),
        Dedent.when(indented_joins=False),
        AnyNumberOf(
            Ref("JoinClauseSegment"), Ref("JoinLikeClauseGrammar"), optional=True
        ),
        Dedent.when(indented_joins=True),
    )

    def get_eventual_alias(self) -> Optional[AliasInfo]:
        """Return the eventual table name referred to by this table expression.

        Returns:
            :obj:`tuple` of (:obj:`str`, :obj:`BaseSegment`, :obj:`bool`) containing
                a string representation of the alias, a reference to the
                segment containing it, and whether it's an alias.

        """
        alias_expression = self.get_child("alias_expression")
        if alias_expression:
            # If it has an alias, return that
            segment = alias_expression.get_child("identifier")
            return AliasInfo(segment.raw, segment, True, self, alias_expression)

        # If not return the object name (or None if there isn't one)
        # ref = self.get_child("object_reference")
        ref = self.get_child("main_table_expression").get_child("object_reference")
        if ref:
            # Return the last element of the reference, which
            # will already be a tuple.
            penultimate_ref = list(ref.iter_raw_references())[-1]
            return AliasInfo(penultimate_ref[0], penultimate_ref[1], False, self, None)
        # No references or alias, return None
        return None


@ansi_dialect.segment()
class MainTableExpressionSegment(BaseSegment):
    """The main table expression e.g. within a FROM clause."""

    type = "main_table_expression"
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
class SelectTargetElementSegment(BaseSegment):
    """An element in the targets of a select statement."""

    type = "select_target_element"
    # Important to split elements before parsing, otherwise debugging is really hard.
    match_grammar = GreedyUntil(
        "FROM",
        "LIMIT",
        Ref("CommaSegment"),
        Ref("SetOperatorSegment"),
        enforce_whitespace_preceeding_terminator=True,
    )

    parse_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            OneOf(
                Ref("LiteralGrammar"),
                Ref("BareFunctionSegment"),
                Ref("FunctionSegment"),
                Ref("IntervalExpressionSegment"),
                Ref("ColumnReferenceSegment"),
                Ref("ExpressionSegment"),
            ),
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
        terminator=OneOf("FROM", "LIMIT", Ref("SetOperatorSegment")),
        enforce_whitespace_preceeding_terminator=True,
    )

    parse_grammar = Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        Delimited(
            Ref("SelectTargetElementSegment"),
            allow_trailing=True,
        ),
        # NB: The Dedent for the indent above lives in the
        # SelectStatementSegment so that it sits in the right
        # place corresponding to the whitespace.
    )


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
        "JOIN",
        Indent,
        Sequence(
            Ref("TableExpressionSegment"),
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
        ),
        Dedent,
    )

    def get_eventual_alias(self) -> AliasInfo:
        """Return the eventual table name referred to by this join clause."""
        table_expression = self.get_child("table_expression")
        return table_expression.get_eventual_alias()


@ansi_dialect.segment()
class JoinOnConditionSegment(BaseSegment):
    """The `ON` condition within a `JOIN` clause."""

    type = "join_on_condition"
    match_grammar = Sequence(
        "ON",
        Indent,
        OneOf(
            Ref("ExpressionSegment"),
            Bracketed(Ref("ExpressionSegment", ephemeral_name="JoinCondition")),
        ),
        Dedent,
    )


ansi_dialect.add(
    # This is a hook point to allow subclassing for other dialects
    JoinLikeClauseGrammar=Nothing(),
)


@ansi_dialect.segment()
class FromClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT`."""

    type = "from_clause"
    match_grammar = StartsWith(
        "FROM",
        terminator=Ref("FromClauseTerminatorGrammar"),
        enforce_whitespace_preceeding_terminator=True,
    )
    parse_grammar = Sequence(
        "FROM",
        Delimited(
            OneOf(
                # check first for MLTableExpression, because of possible FunctionSegment in MainTableExpression
                Ref("MLTableExpressionSegment"),
                Ref("TableExpressionSegment"),
            ),
        ),
    )

    def get_eventual_aliases(self) -> List[Tuple[BaseSegment, AliasInfo]]:
        """List the eventual aliases of this from clause.

        Comes as a list of tuples (table expr, tuple (string, segment, bool)).
        """
        buff = []
        direct_table_children = self.get_children("table_expression")
        join_clauses = [
            join_clause
            for child in direct_table_children
            for join_clause in child.get_children("join_clause")
        ]
        # Iterate through the potential sources of aliases
        for clause in (*direct_table_children, *join_clauses):
            ref: AliasInfo = clause.get_eventual_alias()
            # Only append if non null. A None reference, may
            # indicate a generator expression or similar.
            table_expr = (
                clause
                if clause in direct_table_children
                else clause.get_child("table_expression")
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
                Ref("Expression_A_Grammar"),
            ),
        ),
        AnyNumberOf(
            OneOf(
                Sequence(
                    OneOf(
                        Ref("BinaryOperatorGrammar"),
                        Sequence(
                            Ref.keyword("NOT", optional=True),
                            Ref("LikeGrammar"),
                        )
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
                                Ref("LiteralGrammar"),
                                Ref("IntervalExpressionSegment"),
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
    # Expression_B_Grammar https://www.cockroachlabs.com/docs/v20.2/sql-grammar.htm#b_expr
    Expression_B_Grammar=None,  # TODO
    # Expression_C_Grammar https://www.cockroachlabs.com/docs/v20.2/sql-grammar.htm#c_expr
    Expression_C_Grammar=OneOf(
        Sequence(
            "EXISTS", Bracketed(Ref("SelectStatementSegment"))
        ),  # should be first priority, otherwise EXISTS() would be matched as a function
        Ref("Expression_D_Grammar"),
        Ref("CaseExpressionSegment"),
    ),
    # Expression_D_Grammar https://www.cockroachlabs.com/docs/v20.2/sql-grammar.htm#d_expr
    Expression_D_Grammar=Sequence(
        OneOf(
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Bracketed(
                OneOf(
                    Ref("Expression_A_Grammar"),
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
            Ref("ArrayLiteralSegment"),
        ),
        Ref("Accessor_Grammar", optional=True),
        Ref("ShorthandCastSegment", optional=True),
        allow_gaps=True,
    ),
    Accessor_Grammar=AnyNumberOf(Ref("ArrayAccessorSegment")),
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
        enforce_whitespace_preceeding_terminator=True,
    )
    parse_grammar = Sequence(
        "WHERE",
        Indent,
        OneOf(
            Bracketed(
                # expression could be in brackets
                Ref("ExpressionSegment"),
            ),
            Ref("ExpressionSegment"),
        ),
        Dedent,
    )


@ansi_dialect.segment()
class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`."""

    type = "orderby_clause"
    match_grammar = StartsWith(
        "ORDER",
        terminator=OneOf(
            "LIMIT",
            "HAVING",
            "QUALIFY",
            # For window functions
            "WINDOW",
            "ROWS",
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
            terminator=Ref.keyword("LIMIT"),
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
        enforce_whitespace_preceeding_terminator=True,
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
        enforce_whitespace_preceeding_terminator=True,
    )
    parse_grammar = Sequence(
        "HAVING",
        Indent,
        OneOf(
            Bracketed(
                Ref("ExpressionSegment"),
            ),
            Ref("ExpressionSegment"),
        ),
        Dedent,
    )


@ansi_dialect.segment()
class LimitClauseSegment(BaseSegment):
    """A `LIMIT` clause like in `SELECT`."""

    type = "limit_clause"
    match_grammar = Sequence(
        "LIMIT",
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
                    "DEFAULT",  # not in `FROM` clause, rule?
                    ephemeral_name="ValuesClauseElements",
                )
            ),
        ),
        Ref("AliasExpressionSegment", optional=True),
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
            Ref("SetOperatorSegment"), Ref("WithNoSchemaBindingClauseSegment")
        ),
        enforce_whitespace_preceeding_terminator=True,
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
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
        Ref("NamedWindowSegment", optional=True),
    )


ansi_dialect.add(
    # Things that behave like select statements
    SelectableGrammar=OneOf(
        Ref("WithCompoundStatementSegment"), Ref("NonWithSelectableGrammar")
    ),
    # Things that behave like select statements, which can form part of with expressions.
    NonWithSelectableGrammar=OneOf(
        Ref("SetExpressionSegment"), Ref("NonSetSelectableGrammar")
    ),
    # Things that behave like select statements, which can form part of set expressions.
    NonSetSelectableGrammar=OneOf(
        Ref("SelectStatementSegment"),
        Ref("ValuesClauseSegment"),
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
        Delimited(
            Ref("CTEDefinitionSegment"),
            terminator=Ref.keyword("SELECT"),
        ),
        Ref("NonWithSelectableGrammar"),
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
    )


@ansi_dialect.segment()
class InsertStatementSegment(BaseSegment):
    """A `INSERT` statement."""

    type = "insert_statement"
    match_grammar = StartsWith("INSERT")
    parse_grammar = Sequence(
        "INSERT",
        Ref.keyword("OVERWRITE", optional=True),  # Maybe this is just snowflake?
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Ref("SelectableGrammar"),
    )


@ansi_dialect.segment()
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT` or `ROLLBACK` statement."""

    type = "transaction_statement"
    match_grammar = OneOf(
        # COMMIT [ WORK ] [ AND [ NO ] CHAIN ]
        Sequence(
            "COMMIT",
            Ref.keyword("WORK", optional=True),
            Sequence("AND", Ref.keyword("NO", optional=True), "CHAIN", optional=True),
        ),
        # NOTE: "TO SAVEPOINT" is not yet supported
        # ROLLBACK [ WORK ] [ AND [ NO ] CHAIN ]
        Sequence(
            "ROLLBACK",
            Ref.keyword("WORK", optional=True),
            Sequence("AND", Ref.keyword("NO", optional=True), "CHAIN", optional=True),
        ),
    )


@ansi_dialect.segment()
class ColumnOptionSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint"
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
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                Ref("LiteralGrammar"),
                # ?? Ref('IntervalExpressionSegment')
            ),
            Ref("PrimaryKeyGrammar"),
            "UNIQUE",  # UNIQUE
            "AUTO_INCREMENT",  # AUTO_INCREMENT (MySQL)
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar", optional=True),
            ),
            Sequence(  # [COMMENT 'string'] (MySQL)
                "COMMENT",
                Ref("QuotedLiteralSegment"),
            ),
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
            Ref("ColumnOptionSegment", optional=True),
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

    type = "table_constraint_definition"
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
                "FOREIGN",
                "KEY",
                # Local columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                # Later add support for [MATCH FULL/PARTIAL/SIMPLE] ?
                # Later add support for [ ON DELETE/UPDATE action ] ?
            ),
        ),
    )


@ansi_dialect.segment()
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    # https://crate.io/docs/sql-99/en/latest/chapters/18.html
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
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
                Sequence(  # [COMMENT 'string'] (MySQL)
                    "COMMENT", Ref("QuotedLiteralSegment"), optional=True
                ),
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                Ref("SelectableGrammar"),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
    )


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
        ),
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf("RESTRICT", Ref.keyword("CASCADE", optional=True), optional=True),
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

    In order to help reduce code duplication we decided to implement other dialect specific grants (like snowflake)
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
            "MODIFY",
            "USE_ANY_ROLE",
            "USAGE",
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "TRUNCATE",
            "REFERENCES",
            "READ",
            "WRITE",
            "MONITOR",
            "OPERATE",
            "APPLY",
            "OWNERSHIP",
            "REFERENCE_USAGE",
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
                "INTEGRATION",
                "SCHEMA",
                "ROLE",
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
            Ref("ObjectReferenceSegment"),
            Ref("FunctionParameterGrammar", optional=True),
        ),
    )

    match_grammar = OneOf(
        # Based on https://www.postgresql.org/docs/12/sql-grant.html
        # and https://docs.snowflake.com/en/sql-reference/sql/grant-privilege.html
        Sequence(
            "GRANT",
            OneOf(
                Sequence(
                    Delimited(
                        OneOf(_global_permissions, _permissions),
                        delimiter=Ref("CommaSegment"),
                    ),
                    "ON",
                    _objects,
                ),
                Sequence("ROLE", Ref("ObjectReferenceSegment")),
            ),
            "TO",
            OneOf("GROUP", "USER", "ROLE", "SHARE", optional=True),
            OneOf(
                Ref("ObjectReferenceSegment"),
                "PUBLIC",
            ),
            OneOf(
                Sequence("WITH", "GRANT", "OPTION"),
                Sequence("COPY", "CURRENT", "GRANTS"),
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
                    ),
                    "ON",
                    _objects,
                ),
                Sequence("ROLE", Ref("ObjectReferenceSegment")),
            ),
            "FROM",
            OneOf("GROUP", "USER", "ROLE", "SHARE", optional=True),
            Ref("ObjectReferenceSegment"),
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
    """A `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    """

    type = "update_statement"
    match_grammar = StartsWith("UPDATE")
    parse_grammar = Sequence(
        "UPDATE",
        Ref("TableReferenceSegment"),
        Ref("SetClauseListSegment"),
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
            "DEFAULT",
        ),
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
        OneOf("TEMPORARY", "TEMP", optional=True),
        "FUNCTION",
        Anything(),
    )

    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        OneOf("TEMPORARY", "TEMP", optional=True),
        "FUNCTION",
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


@ansi_dialect.segment()
class FunctionParameterGrammar(BaseSegment):
    """The parameters for a function ie. `(string, number)`."""

    # Function parameter list
    match_grammar = Bracketed(
        Delimited(
            # Odd syntax, but prevents eager parameters being confused for data types
            OneOf(
                Sequence(
                    Ref("ParameterNameSegment", optional=True),
                    OneOf(Sequence("ANY", "TYPE"), Ref("DatatypeSegment")),
                ),
                OneOf(Sequence("ANY", "TYPE"), Ref("DatatypeSegment")),
            ),
            delimiter=Ref("CommaSegment"),
        )
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
    match_grammar = GreedyUntil(Ref("SemicolonSegment"))

    parse_grammar = OneOf(
        Ref("SelectableGrammar"),
        Ref("InsertStatementSegment"),
        Ref("TransactionStatementSegment"),
        Ref("DropStatementSegment"),
        Ref("AccessStatementSegment"),
        Ref("CreateTableStatementSegment"),
        Ref("CreateTypeStatementSegment"),
        Ref("AlterTableStatementSegment"),
        Ref("CreateSchemaStatementSegment"),
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
    )

    def get_table_references(self):
        """Use parsed tree to extract table references."""
        table_refs = set(
            tbl_ref.raw for tbl_ref in self.recursive_crawl("table_reference")
        )
        cte_refs = set(
            cte_def.get_identifier().raw
            for cte_def in self.recursive_crawl("common_table_expression")
        )
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
