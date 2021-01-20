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

from ..parser import (
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

from .base import Dialect
from .ansi_keywords import ansi_reserved_keywords, ansi_unreserved_keywords


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
    ]
)

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
    LiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("NumericLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
        Ref("QualifiedNumericLiteralSegment"),
        # NB: Null is included in the literals, because it is a keyword which
        # can otherwise be easily mistaken for an identifier.
        Ref("NullKeywordSegment"),
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
            delimiter=Ref("CommaSegment"),
            ephemeral_name="ColumnReferenceList",
        )
    ),
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
        Delimited(Ref("ExpressionSegment"), delimiter=Ref("CommaSegment")),
        bracket_type="square",
    )


@ansi_dialect.segment()
class DatatypeSegment(BaseSegment):
    """A data type segment."""

    type = "data_type"
    match_grammar = Sequence(
        Ref("DatatypeIdentifierSegment"),
        Bracketed(
            OneOf(
                Delimited(Ref("ExpressionSegment"), delimiter=Ref("CommaSegment")),
                # The brackets might be empty for some cases...
                optional=True,
            ),
            # There may be no brackets for some data types
            optional=True,
        ),
    )


@ansi_dialect.segment()
class ObjectReferenceSegment(BaseSegment):
    """A reference to an object."""

    type = "object_reference"
    # match grammar (don't allow whitespace)
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=OneOf(Ref("DotSegment"), Sequence(Ref("DotSegment"))),
        terminator=OneOf(
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
class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias."""

    type = "column_reference"


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
class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    """

    type = "alias_expression"
    match_grammar = Sequence(
        Ref.keyword("AS", optional=True), Ref("SingleIdentifierGrammar")
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
    FunctionContentsGrammar=OneOf(
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
                Delimited(
                    Ref("FunctionContentsExpressionGrammar"),
                    delimiter=Ref("CommaSegment"),
                ),
            ),
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
        Bracketed(
            Sequence(
                Ref("PartitionClauseSegment", optional=True),
                Ref("OrderByClauseSegment", optional=True),
                Ref("FrameClauseSegment", optional=True),
                optional=True,
                ephemeral_name="OverClauseContent",
            )
        ),
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
            Bracketed(
                Delimited(Ref("ExpressionSegment"), delimiter=Ref("CommaSegment"))
            ),
            Delimited(Ref("ExpressionSegment"), delimiter=Ref("CommaSegment")),
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


@ansi_dialect.segment()
class TableExpressionSegment(BaseSegment):
    """A table expression."""

    type = "table_expression"
    match_grammar = Sequence(
        Ref("PreTableFunctionKeywordsGrammar", optional=True),
        OneOf(
            # Functions allowed here for table expressions.
            # Perhaps this should just be in a dialect, but
            # it seems sensible here for now.
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Ref("TableReferenceSegment"),
            # Nested Selects
            Bracketed(Ref("SelectableGrammar")),
            # Values clause?
        ),
        OneOf(
            Ref("PostTableExpressionGrammar"),
            Sequence(Ref("AliasExpressionSegment"), Ref("PostTableExpressionGrammar")),
            Ref("AliasExpressionSegment"),
            optional=True,
        ),
    )

    def get_eventual_alias(self):
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
            return (segment.raw, segment, True)

        # If not return the object name (or None if there isn't one)
        ref = self.get_child("object_reference")
        if ref:
            # Return the last element of the reference, which
            # will already be a tuple.
            penultimate_ref = list(ref.iter_raw_references())[-1]
            return (*penultimate_ref, False)
        # No references or alias, return None
        return None


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
            delimiter=Ref("CommaSegment"),
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
        AnyNumberOf(
            "FULL", "INNER", "LEFT", "RIGHT", "CROSS", max_times=1, optional=True
        ),
        Ref.keyword("OUTER", optional=True),
        "JOIN",
        Indent,
        Ref("TableExpressionSegment"),
        # NB: this is optional
        AnyNumberOf(
            # ON clause
            Sequence(
                "ON",
                Indent,
                OneOf(
                    Ref("ExpressionSegment"),
                    Bracketed(Ref("ExpressionSegment", ephemeral_name="JoinCondition")),
                ),
                Dedent,
            ),
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
                        delimiter=Ref("CommaSegment"),
                        ephemeral_name="UsingClauseContents",
                    )
                ),
                Dedent,
            ),
            # Unqualified joins *are* allowed. They just might not
            # be a good idea.
            min_times=0,
        ),
        Dedent,
    )

    def get_eventual_alias(self):
        """Return the eventual table name referred to by this join clause."""
        table_expression = self.get_child("table_expression")
        return table_expression.get_eventual_alias()


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
        terminator=OneOf(
            "WHERE",
            "LIMIT",
            "GROUP",
            "ORDER",
            "HAVING",
            "QUALIFY",
            Ref("SetOperatorSegment"),
        ),
        enforce_whitespace_preceeding_terminator=True,
    )
    parse_grammar = Sequence(
        "FROM",
        Indent,
        Delimited(
            OneOf(
                # Optional old school delimited joins
                Ref("TableExpressionSegment"),
                Ref("MLTableExpressionSegment"),
            ),
            delimiter=Ref("CommaSegment"),
            terminator=Ref("JoinClauseSegment"),
        ),
        # NB: The JOIN clause is *part of* the FROM clause
        # and so should be on a sub-indent of it. That isn't
        # common practice however, so for now it will be assumed
        # to be on the same level as the FROM clause. To change
        # this behaviour, set the `indented_joins` config value
        # to True.
        Dedent.when(indented_joins=False),
        AnyNumberOf(
            Ref("JoinClauseSegment"), Ref("JoinLikeClauseGrammar"), optional=True
        ),
        Dedent.when(indented_joins=True),
    )

    def get_eventual_aliases(self):
        """List the eventual aliases of this from clause.

        Comes as a list of tuples (string, segment).
        """
        buff = []
        direct_table_children = self.get_children("table_expression")
        join_clauses = self.get_children("join_clause")
        # Iterate through the potential sources of aliases
        for clause in (*direct_table_children, *join_clauses):
            ref = clause.get_eventual_alias()
            # Only append if non null. A None reference, may
            # indicate a generator expression or similar.
            if ref:
                buff.append(ref)
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
                            OneOf("LIKE", "RLIKE", "ILIKE"),
                        )
                        # We need to add a lot more here...
                    ),
                    Ref("Expression_A_Grammar"),
                    Sequence(
                        Ref.keyword("ESCAPE"),
                        Ref("Expression_A_Grammar"),
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
                                delimiter=Ref("CommaSegment"),
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
                    OneOf(
                        "NULL",
                        "NAN",
                        "NOTNULL",
                        "ISNULL",
                        # TODO: True and False might not be allowed here in some
                        # dialects (e.g. snowflake) so we should probably
                        # revisit this at some point. Perhaps abstract this clause
                        # into an "is-statement grammar", which could be overridden.
                        Ref("BooleanLiteralGrammar"),
                    ),
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
        Ref("Expression_D_Grammar"),
        Ref("CaseExpressionSegment"),
        Sequence("EXISTS", Ref("SelectStatementSegment")),
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
        terminator=OneOf("LIMIT", "GROUP", "ORDER", "HAVING", "QUALIFY"),
        enforce_whitespace_preceeding_terminator=True,
    )
    parse_grammar = Sequence("WHERE", Indent, Ref("ExpressionSegment"), Dedent)


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
            "ROWS",
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
            delimiter=Ref("CommaSegment"),
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
        terminator=OneOf("ORDER", "LIMIT", "HAVING", "QUALIFY"),
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
            delimiter=Ref("CommaSegment"),
            terminator=OneOf("ORDER", "LIMIT", "HAVING", "QUALIFY"),
        ),
        Dedent,
    )


@ansi_dialect.segment()
class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`."""

    type = "having_clause"
    match_grammar = StartsWith(
        "HAVING",
        terminator=OneOf("ORDER", "LIMIT", "QUALIFY"),
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
                    delimiter=Ref("CommaSegment"),
                    ephemeral_name="ValuesClauseElements",
                )
            ),
            delimiter=Ref("CommaSegment"),
        ),
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
        terminator=Ref("SetOperatorSegment"),
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
        Ref("SelectStatementSegment"), Ref("ValuesClauseSegment")
    ),
)


@ansi_dialect.segment()
class WithCompoundStatementSegment(BaseSegment):
    """A `SELECT` statement preceded by a selection of `WITH` clauses."""

    type = "with_compound_statement"
    # match grammar
    match_grammar = StartsWith("WITH")
    parse_grammar = Sequence(
        "WITH",
        Delimited(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                "AS",
                Bracketed(
                    # Checkpoint here to subdivide the query.
                    Ref("SelectableGrammar", ephemeral_name="SelectableGrammar")
                ),
            ),
            delimiter=Ref("CommaSegment"),
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
            Sequence(Ref("SetOperatorSegment"), Ref("NonSetSelectableGrammar")),
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
            Sequence(  # PRIMARY KEY
                "PRIMARY",
                "KEY",
            ),
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
                "PRIMARY",
                "KEY",
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
        Sequence("OR", "REPLACE", optional=True),
        "TABLE",
        Sequence("IF", "NOT", "EXISTS", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("ColumnDefinitionSegment"),
                            Ref("TableConstraintSegment"),
                        ),
                        delimiter=Ref("CommaSegment"),
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
            delimiter=Ref("CommaSegment"),
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
        Sequence("OR", "REPLACE", optional=True),
        "VIEW",
        Ref("TableReferenceSegment"),
        # Optional list of column names
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        Ref("SelectableGrammar"),
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
        Sequence("IF", "EXISTS", optional=True),
        Ref("TableReferenceSegment"),
        OneOf("RESTRICT", Ref.keyword("CASCADE", optional=True), optional=True),
    )


@ansi_dialect.segment()
class AccessStatementSegment(BaseSegment):
    """A `GRANT` or `REVOKE` statement."""

    type = "access_statement"
    # Based on https://www.postgresql.org/docs/12/sql-grant.html
    match_grammar = OneOf(
        Sequence(
            "GRANT",
            Delimited(  # List of permission types
                Sequence(
                    OneOf(  # Permission type
                        Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
                        "SELECT",
                        "UPDATE",
                        "INSERT",
                    ),
                    # Optional list of column names
                    Ref("BracketedColumnReferenceListGrammar", optional=True),
                ),
                delimiter=Ref("CommaSegment"),
            ),
            "ON",
            OneOf(
                Sequence(
                    Ref.keyword("TABLE", optional=True),
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "ALL",
                    "TABLES",
                    "IN",
                    "SCHEMA",
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            "TO",
            OneOf("GROUP", "USER", "ROLE", optional=True),
            OneOf(
                Ref("ObjectReferenceSegment"),
                "PUBLIC",
            ),
            Sequence("WITH", "GRANT", "OPTION", optional=True),
        ),
        # Based on https://www.postgresql.org/docs/12/sql-revoke.html
        Sequence(
            "REVOKE",
            Delimited(  # List of permission types
                Sequence(
                    Sequence("GRANT", "OPTION", "FOR", optional=True),
                    OneOf(  # Permission type
                        Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
                        "SELECT",
                        "UPDATE",
                        "INSERT",
                    ),
                    # Optional list of column names
                    Ref("BracketedColumnReferenceListGrammar", optional=True),
                ),
                delimiter=Ref("CommaSegment"),
            ),
            "ON",
            OneOf(
                Sequence(
                    Ref.keyword("TABLE", optional=True),
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "ALL",
                    "TABLES",
                    "IN",
                    "SCHEMA",
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            "FROM",
            OneOf("GROUP", "USER", "ROLE", optional=True),
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

    type = "delete_statement"
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
                Delimited(Ref("SetClauseSegment"), delimiter=Ref("CommaSegment")),
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
            "NULL",
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
        # Function parameter list
        Bracketed(
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
        ),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


@ansi_dialect.segment()
class CreateModelStatementSegment(BaseSegment):
    """A BigQuery `CREATE MODEL` statement."""

    type = "create_model_statement"
    # https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-create
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        "MODEL",
        Sequence("IF", "NOT", "EXISTS", optional=True),
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
                                Delimited(
                                    Ref("QuotedLiteralSegment"),
                                    delimiter=Ref("CommaSegment"),
                                ),
                                bracket_type="square",
                                optional=True,
                            ),
                        ),
                    ),
                    delimiter=Ref("CommaSegment"),
                )
            ),
            optional=True,
        ),
        "AS",
        Ref("SelectableGrammar"),
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
        Sequence("IF", "EXISTS", optional=True),
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
        Ref("AlterTableStatementSegment"),
        Ref("CreateViewStatementSegment"),
        Ref("DeleteStatementSegment"),
        Ref("UpdateStatementSegment"),
        Ref("CreateFunctionStatementSegment"),
        Ref("CreateModelStatementSegment"),
        Ref("DropModelStatementSegment"),
    )
