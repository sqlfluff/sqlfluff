"""The PostgreSQL dialect."""

from sqlfluff.core.parser import (
    OneOf,
    AnyNumberOf,
    Ref,
    Sequence,
    Bracketed,
    OptionallyBracketed,
    Anything,
    BaseSegment,
    Delimited,
    RegexLexer,
    RegexParser,
    CodeSegment,
    NamedParser,
    SymbolSegment,
    StartsWith,
    CommentSegment,
    Dedent,
    SegmentGenerator,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects.dialect_postgres_keywords import (
    postgres_keywords,
    get_keywords,
    postgres_postgis_datatype_keywords,
)

ansi_dialect = load_raw_dialect("ansi")

postgres_dialect = ansi_dialect.copy_as("postgres")

postgres_dialect.insert_lexer_matchers(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [
        # Explanation for the regex
        # - (?s) Switch - .* includes newline characters
        # - U& - must start with U&
        # - (('')+?(?!')|('.*?(?<!')(?:'')*'(?!')))
        #    ('')+?                                 Any non-zero number of pairs of single quotes -
        #          (?!')                            that are not then followed by a single quote
        #               |                           OR
        #                ('.*?(?<!')(?:'')*'(?!'))
        #                 '.*?                      A single quote followed by anything (non-greedy)
        #                     (?<!')(?:'')*         Any even number of single quotes, including zero
        #                                  '(?!')   Followed by a single quote, which is not followed by a single quote
        # - (\s*UESCAPE\s*'[^0-9A-Fa-f'+\-\s)]')?
        #    \s*UESCAPE\s*                          Whitespace, followed by UESCAPE, followed by whitespace
        #                 '[^0-9A-Fa-f'+\-\s)]'     Any character that isn't A-F, a-f, 0-9, +-, or whitespace, in quotes
        #                                       ?   This last block is optional
        RegexLexer(
            "unicode_single_quote",
            r"(?s)U&(('')+?(?!')|('.*?(?<!')(?:'')*'(?!')))(\s*UESCAPE\s*'[^0-9A-Fa-f'+\-\s)]')?",
            CodeSegment,
        ),
        # This is similar to the Unicode regex, the key differences being:
        # - E - must start with E
        # - The final quote character must be preceded by:
        # (?<!\\)(?:\\\\)*(?<!')(?:'')     An even/zero number of \ followed by an even/zero number of '
        # OR
        # (?<!\\)(?:\\\\)*\\(?<!')(?:'')*' An odd number of \ followed by an odd number of '
        # There is no UESCAPE block
        RegexLexer(
            "escaped_single_quote",
            r"(?s)E(('')+?(?!')|'.*?((?<!\\)(?:\\\\)*(?<!')(?:'')*|(?<!\\)(?:\\\\)*\\(?<!')(?:'')*')'(?!'))",
            CodeSegment,
        ),
        # Double quote Unicode string cannot be empty, and have no single quote escapes
        RegexLexer(
            "unicode_double_quote",
            r'(?s)U&".+?"(\s*UESCAPE\s*\'[^0-9A-Fa-f\'+\-\s)]\')?',
            CodeSegment,
        ),
        RegexLexer(
            "json_operator",
            r"->>|#>>|->|#>|@>|<@|\?\||\?|\?&|#-",
            CodeSegment,
        ),
    ],
    before="not_equal",
)

postgres_dialect.insert_lexer_matchers(
    [
        # Explanation for the regex
        # \\([^(\\\r\n)])+((\\\\)|(?=\n)|(?=\r\n))?
        # \\                                        Starts with backslash
        #   ([^\\\r\n])+                            Anything that is not a newline or a backslash
        #                 (
        #                  (\\\\)                   Double backslash
        #                        |                  OR
        #                         (?=\n)            The next character is a newline
        #                               |           OR
        #                                (?=\r\n)   The next 2 characters are a carriage return and a newline
        #                                        )
        #                                         ? The previous clause is optional
        RegexLexer(
            # For now we'll just treat meta syntax like comments and so just ignore them.
            # In future we may want to enhance this to actually parse them to ensure they are
            # valid meta commands.
            "meta_command",
            r"\\([^\\\r\n])+((\\\\)|(?=\n)|(?=\r\n))?",
            CommentSegment,
        )
    ],
    before="code",  # Final thing to search for - as psql specific
)

postgres_dialect.patch_lexer_matchers(
    [
        # Patching comments to remove hash comments
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--")},
        ),
        # In Postgres, the only escape character is ' for single quote strings
        RegexLexer(
            "single_quote", r"(?s)('')+?(?!')|('.*?(?<!')(?:'')*'(?!'))", CodeSegment
        ),
        # In Postgres, there is no escape character for double quote strings
        RegexLexer("double_quote", r'(?s)".+?"', CodeSegment),
        RegexLexer("code", r"[0-9a-zA-Z_]+[0-9a-zA-Z_$]*", CodeSegment),
    ]
)

postgres_dialect.sets("reserved_keywords").update(
    get_keywords(postgres_keywords, "reserved")
)
postgres_dialect.sets("unreserved_keywords").update(
    get_keywords(postgres_keywords, "non-reserved")
)
postgres_dialect.sets("reserved_keywords").difference_update(
    get_keywords(postgres_keywords, "not-keyword")
)

postgres_dialect.sets("unreserved_keywords").difference_update(
    get_keywords(postgres_keywords, "not-keyword")
)

# Add datetime units
postgres_dialect.sets("datetime_units").update(
    [
        "CENTURY",
        "DECADE",
        "DOW",
        "DOY",
        "EPOCH",
        "ISODOW",
        "ISOYEAR",
        "MICROSECONDS",
        "MILLENNIUM",
        "MILLISECONDS",
        "TIMEZONE",
        "TIMEZONE_HOUR",
        "TIMEZONE_MINUTE",
    ]
)

postgres_dialect.add(
    JsonOperatorSegment=NamedParser(
        "json_operator", SymbolSegment, name="json_operator", type="binary_operator"
    ),
    DollarQuotedLiteralSegment=NamedParser(
        "dollar_quote", CodeSegment, name="dollar_quoted_literal", type="literal"
    ),
    SimpleGeometryGrammar=AnyNumberOf(Ref("NumericLiteralSegment")),
)

postgres_dialect.replace(
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment_a"),
        Ref("NotEqualToSegment_b"),
        Ref("LikeOperatorSegment"),
        Sequence("IS", "DISTINCT", "FROM"),
        Sequence("IS", "NOT", "DISTINCT", "FROM"),
    ),
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            # Can’t begin with $, must only contain digits, letters, underscore it $ but can’t be all digits.
            r"([A-Z_]+|[0-9]+[A-Z_$])[A-Z0-9_$]*",
            CodeSegment,
            name="naked_identifier",
            type="identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    ParameterNameSegment=RegexParser(
        r"[A-Z_][A-Z0-9_$]*", CodeSegment, name="parameter", type="parameter"
    ),
    QuotedLiteralSegment=OneOf(
        NamedParser("single_quote", CodeSegment, name="quoted_literal", type="literal"),
        NamedParser(
            "unicode_single_quote", CodeSegment, name="quoted_literal", type="literal"
        ),
        NamedParser(
            "escaped_single_quote", CodeSegment, name="quoted_literal", type="literal"
        ),
    ),
    QuotedIdentifierSegment=OneOf(
        NamedParser(
            "double_quote", CodeSegment, name="quoted_identifier", type="identifier"
        ),
        NamedParser(
            "unicode_double_quote", CodeSegment, name="quoted_literal", type="literal"
        ),
    ),
    PostFunctionGrammar=OneOf(
        Ref("WithinGroupClauseSegment"),
        Ref("OverClauseSegment"),
        # Filter clause supported by both Postgres and SQLite
        Ref("FilterClauseGrammar"),
    ),
    BinaryOperatorGrammar=OneOf(
        Ref("ArithmeticBinaryOperatorGrammar"),
        Ref("StringBinaryOperatorGrammar"),
        Ref("BooleanBinaryOperatorGrammar"),
        Ref("ComparisonOperatorGrammar"),
        # Add JSON operators
        Ref("JsonOperatorSegment"),
    ),
    FunctionParameterGrammar=Sequence(
        OneOf("IN", "OUT", "INOUT", "VARIADIC", optional=True),
        OneOf(
            Ref("DatatypeSegment"),
            Sequence(Ref("ParameterNameSegment"), Ref("DatatypeSegment")),
        ),
        Sequence(
            OneOf("DEFAULT", Ref("EqualsSegment")), Ref("LiteralGrammar"), optional=True
        ),
    ),
    FrameClauseUnitGrammar=OneOf("RANGE", "ROWS", "GROUPS"),
    # In Postgres, column references may be followed by a time zone cast in all cases.
    # For more information, see https://www.postgresql.org/docs/11/functions-datetime.html
    ColumnReferenceSegment=Sequence(
        ansi_dialect.get_segment("ColumnReferenceSegment"),
        Ref("ArrayAccessorSegment", optional=True),
        Ref("TimeZoneGrammar", optional=True),
    ),
    # Postgres supports the non-standard ISNULL and NONNULL comparison operators. See
    # https://www.postgresql.org/docs/14/functions-comparison.html
    IsNullGrammar=Ref.keyword("ISNULL"),
    NotNullGrammar=Ref.keyword("NOTNULL"),
    JoinKeywords=Sequence("JOIN", Sequence("LATERAL", optional=True)),
    SelectClauseElementTerminatorGrammar=OneOf(
        "INTO",
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        Ref("CommaSegment"),
        Ref("SetOperatorSegment"),
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
        Ref("PsqlVariableGrammar"),
        Sequence(Ref("SimpleArrayTypeGrammar"), Ref("ArrayLiteralSegment")),
    ),
    SimpleArrayTypeGrammar=Ref.keyword("ARRAY"),
)


@postgres_dialect.segment()
class PsqlVariableGrammar(BaseSegment):
    """PSQl Variables :thing, :'thing', :"thing"."""

    type = "psql_variable"

    match_grammar = Sequence(
        OptionallyBracketed(
            Ref("ColonSegment"),
            OneOf(
                Ref("ParameterNameSegment"),
                Ref("QuotedLiteralSegment"),
                Ref("QuotedIdentifierSegment"),
            ),
        )
    )


@postgres_dialect.segment()
class TimeZoneGrammar(BaseSegment):
    """Literal Date Time with optional casting to Time Zone."""

    type = "time_zone_grammar"
    match_grammar = AnyNumberOf(
        Sequence("AT", "TIME", "ZONE", Ref("QuotedLiteralSegment")),
    )


@postgres_dialect.segment(replace=True)
class ArrayAccessorSegment(BaseSegment):
    """Overwrites Array Accessor in ANSI to allow n many consecutive brackets."""

    type = "array_accessor"

    match_grammar = Sequence(
        AnyNumberOf(
            Bracketed(
                Sequence(
                    OneOf(
                        Ref("QualifiedNumericLiteralSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                    Sequence(
                        Ref("SliceSegment"),
                        OneOf(
                            Ref("QualifiedNumericLiteralSegment"),
                            Ref("NumericLiteralSegment"),
                        ),
                        optional=True,
                    ),
                    optional=True,
                ),
                bracket_type="square",
            )
        )
    )


@postgres_dialect.segment()
class SimpleArrayContentsGrammar(BaseSegment):
    """This Grammar is Literals in Square Brackets, comma delimited."""

    type = "simple_array_contents_grammar"

    match_grammar = Bracketed(Delimited(Ref("LiteralGrammar")), bracket_type="square")


@postgres_dialect.segment(replace=True)
class ArrayLiteralSegment(BaseSegment):
    """Overwrites ANSI to allow for nested Arrays."""

    type = "array_contents_grammar"

    match_grammar = Sequence(
        OneOf(
            Ref("SimpleArrayContentsGrammar"),
            Bracketed(Delimited(Ref("ArrayLiteralSegment")), bracket_type="square"),
        )
    )


@postgres_dialect.segment()
class DateTimeTypeIdentifier(BaseSegment):
    """Date Time Type."""

    type = "datetime_type_identifier"
    match_grammar = OneOf(
        "DATE",
        Sequence(
            OneOf("TIME", "TIMESTAMP"),
            Bracketed(Ref("NumericLiteralSegment"), optional=True),
            Sequence(OneOf("WITH", "WITHOUT"), "TIME", "ZONE", optional=True),
        ),
        Sequence("TIMESTAMPTZ", Bracketed(Ref("NumericLiteralSegment"), optional=True)),
        "INTERVAL",
    )


@postgres_dialect.segment(replace=True)
class DateTimeLiteralGrammar(BaseSegment):
    """Literal Date Time with optional casting to Time Zone."""

    type = "datetime_literal"
    match_grammar = Sequence(
        Ref("DateTimeTypeIdentifier"),
        Ref("QuotedLiteralSegment"),
        Ref("TimeZoneGrammar", optional=True),
    )


@postgres_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment.

    Supports timestamp with(out) time zone. Doesn't currently support intervals.
    """

    type = "data_type"
    match_grammar = OneOf(
        Ref("WellKnownTextGeometrySegment"),
        Sequence(
            Ref("DateTimeTypeIdentifier"),
            Ref("TimeZoneGrammar", optional=True),
        ),
        Sequence(
            OneOf(
                Sequence("DOUBLE", "PRECISION"),
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
                    OneOf(
                        Ref("ArrayAccessorSegment"),
                        Sequence(
                            Ref("SimpleArrayTypeGrammar"), Ref("ArrayLiteralSegment")
                        ),
                        optional=True,
                    ),
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


@postgres_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the ANSI dialect should be a "common subset" of the
    structure of the code for those dialects.
    postgres: https://www.postgresql.org/docs/13/sql-createfunction.html
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
            OneOf(
                Sequence(
                    "TABLE",
                    Bracketed(
                        Delimited(
                            OneOf(
                                Ref("DatatypeSegment"),
                                Sequence(
                                    Ref("ParameterNameSegment"), Ref("DatatypeSegment")
                                ),
                            ),
                            delimiter=Ref("CommaSegment"),
                        )
                    ),
                    optional=True,
                ),
                Sequence(
                    "SETOF",
                    Ref("DatatypeSegment"),
                ),
                Ref("DatatypeSegment"),
            ),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


@postgres_dialect.segment()
class DropFunctionStatementSegment(BaseSegment):
    """A `DROP FUNCTION` statement.

    As per the specification: https://www.postgresql.org/docs/14/sql-dropfunction.html
    """

    type = "drop_function_statement"

    match_grammar = Sequence(
        "DROP",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Delimited(
            Sequence(
                Ref("FunctionNameSegment"),
                Ref("FunctionParameterListGrammar", optional=True),
            )
        ),
        OneOf("CASCADE", "RESTRICT", optional=True),
    )


@postgres_dialect.segment()
class AlterFunctionStatementSegment(BaseSegment):
    """A `ALTER FUNCTION` statement.

    As per the specification: https://www.postgresql.org/docs/14/sql-alterfunction.html
    """

    type = "alter_function_statement"

    match_grammar = StartsWith(Sequence("ALTER", "FUNCTION"))

    parse_grammar = Sequence(
        "ALTER",
        "FUNCTION",
        Delimited(
            Sequence(
                Ref("FunctionNameSegment"),
                Ref("FunctionParameterListGrammar", optional=True),
            )
        ),
        OneOf(
            Ref("AlterFunctionActionSegment", optional=True),
            Sequence("RENAME", "TO", Ref("FunctionNameSegment")),
            Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
            Sequence(
                "OWNER",
                "TO",
                OneOf(
                    OneOf(Ref("ParameterNameSegment"), Ref("QuotedIdentifierSegment")),
                    "CURRENT_ROLE",
                    "CURRENT_USER",
                    "SESSION_USER",
                ),
            ),
            Sequence(
                Ref.keyword("NO", optional=True),
                "DEPENDS",
                "ON",
                "EXTENSION",
            ),
        ),
    )


@postgres_dialect.segment()
class AlterFunctionActionSegment(BaseSegment):
    """Alter Function Action Segment.

    Matches the definition of action in https://www.postgresql.org/docs/14/sql-alterfunction.html
    """

    type = "alter_function_action_segment"

    match_grammar = Sequence(
        OneOf(
            OneOf(
                Sequence("CALLED", "ON", "NULL", "INPUT"),
                Sequence("RETURNS", "NULL", "ON", "NULL", "INPUT"),
                "STRICT",
            ),
            OneOf("IMMUTABLE", "STABLE", "VOLATILE"),
            Sequence(Ref.keyword("NOT", optional=True), "LEAKPROOF"),
            Sequence(
                Ref.keyword("EXTERNAL", optional=True),
                "SECURITY",
                OneOf("DEFINER", "INVOKER"),
            ),
            Sequence("PARALLEL", OneOf("UNSAFE", "RESTRICTED", "SAFE")),
            Sequence("COST", Ref("NumericLiteralSegment")),
            Sequence("ROWS", Ref("NumericLiteralSegment")),
            Sequence("SUPPORT", Ref("ParameterNameSegment")),
            Sequence(
                "SET",
                Ref("ParameterNameSegment"),
                OneOf(
                    Sequence(
                        OneOf("TO", Ref("EqualsSegment")),
                        OneOf(
                            Ref("LiteralGrammar"),
                            Ref("NakedIdentifierSegment"),
                            "DEFAULT",
                        ),
                    ),
                    Sequence("FROM", "CURRENT"),
                ),
            ),
            Sequence("RESET", OneOf("ALL", Ref("ParameterNameSegment"))),
        ),
        Ref.keyword("RESTRICT", optional=True),
    )


@postgres_dialect.segment()
class WellKnownTextGeometrySegment(BaseSegment):
    """A Data Type Segment to identify Well Known Text Geometric Data Types.

    As specified in https://postgis.net/stuff/postgis-3.1.pdf

    This approach is to maximise 'accepted code' for the parser, rather than be overly restrictive.
    """

    type = "wkt_geometry_type"

    _geometry_type_keywords = [x[0] for x in postgres_postgis_datatype_keywords]

    match_grammar = OneOf(
        Sequence(
            OneOf(*_geometry_type_keywords),
            Bracketed(
                Delimited(
                    OptionallyBracketed(Delimited(Ref("SimpleGeometryGrammar"))),
                    # 2D Arrays of coordinates - to specify surfaces
                    Bracketed(
                        Delimited(Bracketed(Delimited(Ref("SimpleGeometryGrammar"))))
                    ),
                    Ref("WellKnownTextGeometrySegment"),
                )
            ),
        ),
        Sequence(
            OneOf("GEOMETRY", "GEOGRAPHY"),
            Bracketed(
                Sequence(
                    OneOf(*_geometry_type_keywords, "GEOMETRY", "GEOGRAPHY"),
                    Ref("CommaSegment"),
                    Ref("NumericLiteralSegment"),
                )
            ),
        ),
    )


@postgres_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement.

    Options supported as defined in https://www.postgresql.org/docs/13/sql-createfunction.html
    """

    match_grammar = Sequence(
        AnyNumberOf(
            Sequence("LANGUAGE", Ref("ParameterNameSegment")),
            Sequence("TRANSFORM", "FOR", "TYPE", Ref("ParameterNameSegment")),
            Ref.keyword("WINDOW"),
            OneOf("IMMUTABLE", "STABLE", "VOLATILE"),
            Sequence(Ref.keyword("NOT", optional=True), "LEAKPROOF"),
            OneOf(
                Sequence("CALLED", "ON", "NULL", "INPUT"),
                Sequence("RETURNS", "NULL", "ON", "NULL", "INPUT"),
                "STRICT",
            ),
            Sequence(
                Ref.keyword("EXTERNAL", optional=True),
                "SECURITY",
                OneOf("INVOKER", "DEFINER"),
            ),
            Sequence("PARALLEL", OneOf("UNSAFE", "RESTRICTED", "SAFE")),
            Sequence("COST", Ref("NumericLiteralSegment")),
            Sequence("ROWS", Ref("NumericLiteralSegment")),
            Sequence("SUPPORT", Ref("ParameterNameSegment")),
            Sequence(
                "SET",
                Ref("ParameterNameSegment"),
                OneOf(
                    Sequence(
                        OneOf("TO", Ref("EqualsSegment")),
                        Delimited(
                            OneOf(
                                Ref("ParameterNameSegment"),
                                Ref("LiteralGrammar"),
                            ),
                            delimiter=Ref("CommaSegment"),
                        ),
                    ),
                    Sequence("FROM", "CURRENT"),
                ),
            ),
            Sequence(
                "AS",
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("DollarQuotedLiteralSegment"),
                    Sequence(
                        Ref("QuotedLiteralSegment"),
                        Ref("CommaSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
        ),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(Ref("ParameterNameSegment"), delimiter=Ref("CommaSegment"))
            ),
            optional=True,
        ),
    )


@postgres_dialect.segment()
class IntoClauseSegment(BaseSegment):
    """Into Clause Segment.

    As specified in https://www.postgresql.org/docs/14/sql-selectinto.html
    """

    type = "into_clause"

    match_grammar = Sequence(
        "INTO",
        OneOf("TEMPORARY", "TEMP", "UNLOGGED", optional=True),
        Ref.keyword("TABLE", optional=True),
        Ref("TableReferenceSegment"),
    )


@postgres_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(BaseSegment):
    """Overrides ANSI Statement, to allow for SELECT INTO statements."""

    type = "select_statement"

    match_grammar = ansi_dialect.get_segment(
        "UnorderedSelectStatementSegment"
    ).match_grammar.copy()

    parse_grammar = Sequence(
        Ref("SelectClauseSegment"),
        # Dedent for the indent in the select clause.
        # It's here so that it can come AFTER any whitespace.
        Dedent,
        Ref("IntoClauseSegment", optional=True),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
        Ref("OverlapsClauseSegment", optional=True),
    )


@postgres_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """Overrides ANSI as the parse grammar copy needs to be reapplied."""

    type = "select_statement"

    match_grammar = ansi_dialect.get_segment(
        "SelectStatementSegment"
    ).match_grammar.copy()

    parse_grammar = postgres_dialect.get_segment(
        "UnorderedSelectStatementSegment"
    ).parse_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ]
    )


@postgres_dialect.segment(replace=True)
class SelectClauseSegment(BaseSegment):
    """Overrides ANSI to allow INTO as a terminator."""

    type = "select_clause"
    match_grammar = StartsWith(
        Sequence("SELECT", Ref("WildcardExpressionSegment", optional=True)),
        terminator=OneOf(
            "INTO",
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


@postgres_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = OneOf(
        Sequence("DISTINCT", Sequence("ON", Bracketed(Anything()), optional=True)),
        "ALL",
    )

    parse_grammar = OneOf(
        Sequence(
            "DISTINCT",
            Sequence(
                "ON",
                Bracketed(
                    Delimited(Ref("ExpressionSegment"), delimiter=Ref("CommaSegment"))
                ),
                optional=True,
            ),
        ),
        "ALL",
    )


@postgres_dialect.segment()
class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions.

    https://www.postgresql.org/docs/current/functions-aggregate.html.
    """

    type = "withingroup_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Anything(optional=True)),
    )

    parse_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Ref("OrderByClauseSegment", optional=True)),
    )


@postgres_dialect.segment(replace=True)
class CreateRoleStatementSegment(BaseSegment):
    """A `CREATE ROLE` statement.

    As per:
    https://www.postgresql.org/docs/current/sql-createrole.html
    """

    type = "create_role_statement"
    match_grammar = ansi_dialect.get_segment(
        "CreateRoleStatementSegment"
    ).match_grammar.copy(
        insert=[
            Sequence(
                Ref.keyword("WITH", optional=True),
                # Very permissive for now. Anything can go here.
                Anything(),
            )
        ],
    )


@postgres_dialect.segment(replace=True)
class ExplainStatementSegment(ansi_dialect.get_segment("ExplainStatementSegment")):  # type: ignore
    """An `Explain` statement.

    EXPLAIN [ ( option [, ...] ) ] statement
    EXPLAIN [ ANALYZE ] [ VERBOSE ] statement

    https://www.postgresql.org/docs/9.1/sql-explain.html
    """

    parse_grammar = Sequence(
        "EXPLAIN",
        OneOf(
            Sequence(
                Ref.keyword("ANALYZE", optional=True),
                Ref.keyword("VERBOSE", optional=True),
            ),
            Bracketed(
                Delimited(Ref("ExplainOptionSegment"), delimiter=Ref("CommaSegment"))
            ),
            optional=True,
        ),
        ansi_dialect.get_segment("ExplainStatementSegment").explainable_stmt,
    )


@postgres_dialect.segment()
class ExplainOptionSegment(BaseSegment):
    """An `Explain` statement option.

    ANALYZE [ boolean ]
    VERBOSE [ boolean ]
    COSTS [ boolean ]
    BUFFERS [ boolean ]
    FORMAT { TEXT | XML | JSON | YAML }

    https://www.postgresql.org/docs/9.1/sql-explain.html
    """

    type = "explain_option"

    flag_segment = Sequence(
        OneOf("ANALYZE", "VERBOSE", "COSTS", "BUFFERS"),
        OneOf(Ref("TrueSegment"), Ref("FalseSegment"), optional=True),
    )

    match_grammar = OneOf(
        flag_segment,
        Sequence(
            "FORMAT",
            OneOf("TEXT", "XML", "JSON", "YAML"),
        ),
    )


@postgres_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement.

    As specified in https://www.postgresql.org/docs/13/sql-createtable.html
    """

    type = "create_table_statement"

    match_grammar = Sequence(
        "CREATE",
        OneOf(
            Sequence(
                OneOf("GLOBAL", "LOCAL", optional=True),
                Ref("TemporaryGrammar", optional=True),
            ),
            "UNLOGGED",
            optional=True,
        ),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Sequence(
                                Ref("ColumnReferenceSegment"),
                                Ref("DatatypeSegment"),
                                Sequence(
                                    "COLLATE",
                                    Ref("QuotedLiteralSegment"),
                                    optional=True,
                                ),
                                AnyNumberOf(
                                    Ref("ColumnConstraintSegment", optional=True)
                                ),
                            ),
                            Ref("TableConstraintSegment"),
                            Sequence(
                                "LIKE",
                                Ref("TableReferenceSegment"),
                                AnyNumberOf(Ref("LikeOptionSegment"), optional=True),
                            ),
                        ),
                    )
                ),
                Sequence(
                    "INHERITS",
                    Bracketed(
                        Delimited(
                            Ref("TableReferenceSegment"), delimiter=Ref("CommaSegment")
                        )
                    ),
                    optional=True,
                ),
            ),
            # Create OF syntax:
            Sequence(
                "OF",
                Ref("ParameterNameSegment"),
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            Sequence("WITH", "OPTIONS", optional=True),
                            AnyNumberOf(Ref("ColumnConstraintSegment")),
                        ),
                        Ref("TableConstraintSegment"),
                        delimiter=Ref("CommaSegment"),
                    ),
                    optional=True,
                ),
            ),
            # Create PARTITION OF syntax
            Sequence(
                "PARTITION",
                "OF",
                Ref("TableReferenceSegment"),
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            Sequence("WITH", "OPTIONS", optional=True),
                            AnyNumberOf(Ref("ColumnConstraintSegment")),
                        ),
                        Ref("TableConstraintSegment"),
                        delimiter=Ref("CommaSegment"),
                    ),
                    optional=True,
                ),
                OneOf(
                    Sequence("FOR", "VALUES", Ref("PartitionBoundSpecSegment")),
                    "DEFAULT",
                ),
            ),
        ),
        AnyNumberOf(
            Sequence(
                "PARTITION",
                "BY",
                OneOf("RANGE", "LIST", "HASH"),
                Bracketed(
                    AnyNumberOf(
                        Delimited(
                            Sequence(
                                OneOf(
                                    Ref("ColumnReferenceSegment"),
                                    Ref("FunctionSegment"),
                                ),
                                AnyNumberOf(
                                    Sequence(
                                        "COLLATE",
                                        Ref("QuotedLiteralSegment"),
                                        optional=True,
                                    ),
                                    Ref("ParameterNameSegment", optional=True),
                                ),
                            ),
                            delimiter=Ref("CommaSegment"),
                        )
                    )
                ),
            ),
            Sequence("USING", Ref("ParameterNameSegment")),
            OneOf(
                Sequence(
                    "WITH",
                    Bracketed(
                        AnyNumberOf(
                            Sequence(
                                Ref("ParameterNameSegment"),
                                Sequence(
                                    Ref("EqualsSegment"),
                                    Ref("LiteralGrammar"),
                                    optional=True,
                                ),
                            )
                        )
                    ),
                ),
                Sequence("WITHOUT", "OIDS"),
            ),
            Sequence(
                "ON",
                "COMMIT",
                OneOf(Sequence("PRESERVE", "ROWS"), Sequence("DELETE", "ROWS"), "DROP"),
            ),
            Sequence("TABLESPACE", Ref("TableReferenceSegment")),
        ),
    )


@postgres_dialect.segment()
class CreateTableAsStatementSegment(BaseSegment):
    """A `CREATE TABLE AS` statement.

    As specified in https://www.postgresql.org/docs/13/sql-createtableas.html
    """

    type = "create_table_as_statement"

    match_grammar = Sequence(
        "CREATE",
        OneOf(
            Sequence(
                OneOf("GLOBAL", "LOCAL", optional=True),
                Ref("TemporaryGrammar"),
            ),
            "UNLOGGED",
            optional=True,
        ),
        "TABLE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        AnyNumberOf(
            Sequence(
                Bracketed(
                    Delimited(Ref("ColumnReferenceSegment")),
                ),
                optional=True,
            ),
            Sequence("USING", Ref("ParameterNameSegment"), optional=True),
            OneOf(
                Sequence(
                    "WITH",
                    Bracketed(
                        AnyNumberOf(
                            Sequence(
                                Ref("ParameterNameSegment"),
                                Sequence(
                                    Ref("EqualsSegment"),
                                    Ref("LiteralGrammar"),
                                    optional=True,
                                ),
                            )
                        )
                    ),
                ),
                Sequence("WITHOUT", "OIDS"),
                optional=True,
            ),
            Sequence(
                "ON",
                "COMMIT",
                OneOf(Sequence("PRESERVE", "ROWS"), Sequence("DELETE", "ROWS"), "DROP"),
                optional=True,
            ),
            Sequence("TABLESPACE", Ref("ParameterNameSegment"), optional=True),
        ),
        "AS",
        OneOf(
            OptionallyBracketed(Ref("SelectableGrammar")),
            OptionallyBracketed(Sequence("TABLE", Ref("TableReferenceSegment"))),
            Ref("ValuesClauseSegment"),
            OptionallyBracketed(Sequence("EXECUTE", Ref("FunctionSegment"))),
        ),
        Ref("WithDataClauseSegment", optional=True),
    )


@postgres_dialect.segment(replace=True)
class AlterTableStatementSegment(BaseSegment):
    """An `ALTER TABLE` statement.

    Matches the definition in https://www.postgresql.org/docs/13/sql-altertable.html
    """

    type = "alter_table_statement"

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        OneOf(
            Sequence(
                Sequence("IF", "EXISTS", optional=True),
                Ref.keyword("ONLY", optional=True),
                Ref("TableReferenceSegment"),
                Ref("StarSegment", optional=True),
                OneOf(
                    Delimited(
                        Ref("AlterTableActionSegment"), delimiter=Ref("CommaSegment")
                    ),
                    Sequence(
                        "RENAME",
                        Ref.keyword("COLUMN", optional=True),
                        Ref("ColumnReferenceSegment"),
                        "TO",
                        Ref("ColumnReferenceSegment"),
                    ),
                    Sequence(
                        "RENAME",
                        "CONSTRAINT",
                        Ref("ParameterNameSegment"),
                        "TO",
                        Ref("ParameterNameSegment"),
                    ),
                ),
            ),
            Sequence(
                Sequence("IF", "EXISTS", optional=True),
                Ref("TableReferenceSegment"),
                OneOf(
                    Sequence("RENAME", "TO", Ref("TableReferenceSegment")),
                    Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
                    Sequence(
                        "ATTACH",
                        "PARTITION",
                        Ref("ParameterNameSegment"),
                        OneOf(
                            Sequence("FOR", "VALUES", Ref("PartitionBoundSpecSegment")),
                            "DEFAULT",
                        ),
                    ),
                    Sequence(
                        "DETACH",
                        "PARTITION",
                        Ref("ParameterNameSegment"),
                        Ref.keyword("CONCURRENTLY", optional=True),
                        Ref.keyword("FINALIZE", optional=True),
                    ),
                ),
            ),
            Sequence(
                "ALL",
                "IN",
                "TABLESPACE",
                Ref("ParameterNameSegment"),
                Sequence(
                    "OWNED",
                    "BY",
                    Delimited(
                        Ref("ObjectReferenceSegment"), delimiter=Ref("CommaSegment")
                    ),
                    optional=True,
                ),
                "SET",
                "TABLESPACE",
                Ref("ParameterNameSegment"),
                Ref.keyword("NOWAIT", optional=True),
            ),
        ),
    )


@postgres_dialect.segment()
class AlterTableActionSegment(BaseSegment):
    """Alter Table Action Segment.

    Matches the definition of action in https://www.postgresql.org/docs/13/sql-altertable.html
    """

    type = "alter_table_action_segment"

    match_grammar = OneOf(
        Sequence(
            "ADD",
            Ref.keyword("COLUMN", optional=True),
            Sequence("IF", "NOT", "EXISTS", optional=True),
            Ref("ColumnReferenceSegment"),
            Ref("DatatypeSegment"),
            Sequence("COLLATE", Ref("QuotedLiteralSegment"), optional=True),
            AnyNumberOf(Ref("ColumnConstraintSegment")),
        ),
        Sequence(
            "DROP",
            Ref.keyword("COLUMN", optional=True),
            Sequence("IF", "EXISTS", optional=True),
            Ref("ColumnReferenceSegment"),
            OneOf("RESTRICT", "CASCADE", optional=True),
        ),
        Sequence(
            "ALTER",
            Ref.keyword("COLUMN", optional=True),
            Ref("ColumnReferenceSegment"),
            OneOf(
                Sequence(
                    Sequence("SET", "DATA", optional=True),
                    "TYPE",
                    Ref("DatatypeSegment"),
                    Sequence("COLLATE", Ref("QuotedLiteralSegment"), optional=True),
                    Sequence("USING", OneOf(Ref("ExpressionSegment")), optional=True),
                ),
                Sequence(
                    "SET",
                    "DEFAULT",
                    OneOf(
                        OneOf(
                            Ref("LiteralGrammar"),
                            Ref("FunctionSegment"),
                            Ref("BareFunctionSegment"),
                            Ref("ExpressionSegment"),
                        )
                    ),
                ),
                Sequence("DROP", "DEFAULT"),
                Sequence(OneOf("SET", "DROP", optional=True), "NOT", "NULL"),
                Sequence("DROP", "EXPRESSION", Sequence("IF", "EXISTS", optional=True)),
                Sequence(
                    "ADD",
                    "GENERATED",
                    OneOf("ALWAYS", Sequence("BY", "DEFAULT")),
                    "AS",
                    "IDENTITY",
                    Bracketed(
                        AnyNumberOf(Ref("AlterSequenceOptionsSegment")), optional=True
                    ),
                ),
                Sequence(
                    OneOf(
                        Sequence(
                            "SET",
                            "GENERATED",
                            OneOf("ALWAYS", Sequence("BY", "DEFAULT")),
                        ),
                        Sequence("SET", Ref("AlterSequenceOptionsSegment")),
                        Sequence(
                            "RESTART", Sequence("WITH", Ref("NumericLiteralSegment"))
                        ),
                    )
                ),
                Sequence("DROP", "IDENTITY", Sequence("IF", "EXISTS", optional=True)),
                Sequence("SET", "STATISTICS", Ref("NumericLiteralSegment")),
                Sequence(
                    "SET",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("ParameterNameSegment"),
                                Ref("EqualsSegment"),
                                Ref("LiteralGrammar"),
                            ),
                            delimiter=Ref("CommaSegment"),
                        )
                    ),
                ),
                Sequence(
                    "RESET",
                    Bracketed(
                        Delimited(
                            Ref("ParameterNameSegment"), delimiter=Ref("CommaSegment")
                        )
                    ),
                ),
                Sequence(
                    "SET", "STORAGE", OneOf("PLAIN", "EXTERNAL", "EXTENDED", "MAIN")
                ),
            ),
        ),
        Sequence(
            "ADD",
            Ref("TableConstraintSegment"),
            Sequence("NOT", "VALID", optional=True),
        ),
        Sequence("ADD", Ref("TableConstraintUsingIndexSegment")),
        Sequence(
            "ALTER",
            "CONSTRAINT",
            Ref("ParameterNameSegment"),
            OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
            OneOf(
                Sequence("INITIALLY", "DEFERRED"),
                Sequence("INITIALLY", "IMMEDIATE"),
                optional=True,
            ),
        ),
        Sequence("VALIDATE", "CONSTRAINT", Ref("ParameterNameSegment")),
        Sequence(
            "DROP",
            "CONSTRAINT",
            Sequence("IF", "EXISTS", optional=True),
            Ref("ParameterNameSegment"),
            OneOf("RESTRICT", "CASCADE", optional=True),
        ),
        Sequence(
            OneOf("ENABLE", "DISABLE"),
            "TRIGGER",
            OneOf(Ref("ParameterNameSegment"), "ALL", "USER"),
        ),
        Sequence(
            "ENABLE", OneOf("REPLICA", "ALWAYS"), "TRIGGER", Ref("ParameterNameSegment")
        ),
        Sequence(
            OneOf(
                "ENABLE",
                "DISABLE",
                Sequence("ENABLE", "REPLICA"),
                Sequence("ENABLE", "RULE"),
            ),
            "RULE",
            Ref("ParameterNameSegment"),
        ),
        Sequence(
            OneOf("DISABLE", "ENABLE", "FORCE", Sequence("NO", "FORCE")),
            "ROW",
            "LEVEL",
            "SECURITY",
        ),
        Sequence("CLUSTER", "ON", Ref("ParameterNameSegment")),
        Sequence("SET", "WITHOUT", OneOf("CLUSTER", "OIDS")),
        Sequence("SET", "TABLESPACE", Ref("ParameterNameSegment")),
        Sequence("SET", OneOf("LOGGED", "UNLOGGED")),
        Sequence(
            "SET",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        Ref("LiteralGrammar"),
                    ),
                    delimiter=Ref("CommaSegment"),
                )
            ),
        ),
        Sequence(
            "RESET",
            Bracketed(
                Delimited(Ref("ParameterNameSegment"), delimiter=Ref("CommaSegment"))
            ),
        ),
        Sequence(
            Ref.keyword("NO", optional=True), "INHERIT", Ref("TableReferenceSegment")
        ),
        Sequence("OF", Ref("ParameterNameSegment")),
        Sequence("NOT", "OF"),
        Sequence(
            "OWNER",
            "TO",
            OneOf(
                OneOf(Ref("ParameterNameSegment"), Ref("QuotedIdentifierSegment")),
                "CURRENT_ROLE",
                "CURRENT_USER",
                "SESSION_USER",
            ),
        ),
        Sequence(
            "REPLICA",
            "IDENTITY",
            OneOf(
                "DEFAULT",
                Sequence("USING", "INDEX", Ref("ParameterNameSegment")),
                "FULL",
                "NOTHING",
            ),
        ),
    )


@postgres_dialect.segment()
class CreateMaterializedViewStatementSegment(BaseSegment):
    """A `CREATE MATERIALIZED VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-creatematerializedview.html
    """

    type = "create_materialized_view_statement"

    match_grammar = StartsWith(Sequence("CREATE", "MATERIALIZED", "VIEW"))

    parse_grammar = Sequence(
        "CREATE",
        "MATERIALIZED",
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        AnyNumberOf(
            Sequence("USING", Ref("ParameterNameSegment"), optional=True),
            Sequence("TABLESPACE", Ref("ParameterNameSegment"), optional=True),
            Sequence(
                "WITH",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ParameterNameSegment"),
                            Sequence(
                                Ref("EqualsSegment"),
                                Ref("LiteralGrammar"),
                                optional=True,
                            ),
                        ),
                    )
                ),
            ),
        ),
        "AS",
        OneOf(
            OptionallyBracketed(Ref("SelectableGrammar")),
            OptionallyBracketed(Sequence("TABLE", Ref("TableReferenceSegment"))),
            Ref("ValuesClauseSegment"),
            OptionallyBracketed(Sequence("EXECUTE", Ref("FunctionSegment"))),
        ),
        Ref("WithDataClauseSegment", optional=True),
    )


@postgres_dialect.segment()
class AlterMaterializedViewStatementSegment(BaseSegment):
    """A `ALTER MATERIALIZED VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-altermaterializedview.html
    """

    type = "alter_materialized_view_statement"

    match_grammar = StartsWith(Sequence("ALTER", "MATERIALIZED", "VIEW"))

    parse_grammar = Sequence(
        "ALTER",
        "MATERIALIZED",
        "VIEW",
        OneOf(
            Sequence(
                Sequence("IF", "EXISTS", optional=True),
                Ref("TableReferenceSegment"),
                OneOf(
                    Delimited(Ref("AlterMaterializedViewActionSegment")),
                    Sequence(
                        "RENAME",
                        Sequence("COLUMN", optional=True),
                        Ref("ColumnReferenceSegment"),
                        "TO",
                        Ref("ColumnReferenceSegment"),
                    ),
                    Sequence("RENAME", "TO", Ref("TableReferenceSegment")),
                    Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
                ),
            ),
            Sequence(
                Ref("TableReferenceSegment"),
                Ref.keyword("NO", optional=True),
                "DEPENDS",
                "ON",
                "EXTENSION",
                Ref("ParameterNameSegment"),
            ),
            Sequence(
                "ALL",
                "IN",
                "TABLESPACE",
                Ref("TableReferenceSegment"),
                Sequence(
                    "OWNED",
                    "BY",
                    Delimited(Ref("ObjectReferenceSegment")),
                    optional=True,
                ),
                "SET",
                "TABLESPACE",
                Ref("ParameterNameSegment"),
                Sequence("NOWAIT", optional=True),
            ),
        ),
    )


@postgres_dialect.segment()
class AlterMaterializedViewActionSegment(BaseSegment):
    """Alter Materialized View Action Segment.

    Matches the definition of action in https://www.postgresql.org/docs/14/sql-altermaterializedview.html
    """

    type = "alter_materialized_view_action_segment"

    match_grammar = OneOf(
        Sequence(
            "ALTER",
            Ref.keyword("COLUMN", optional=True),
            Ref("ColumnReferenceSegment"),
            OneOf(
                Sequence("SET", "STATISTICS", Ref("NumericLiteralSegment")),
                Sequence(
                    "SET",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("ParameterNameSegment"),
                                Ref("EqualsSegment"),
                                Ref("LiteralGrammar"),
                            ),
                        )
                    ),
                ),
                Sequence(
                    "RESET",
                    Bracketed(Delimited(Ref("ParameterNameSegment"))),
                ),
                Sequence(
                    "SET", "STORAGE", OneOf("PLAIN", "EXTERNAL", "EXTENDED", "MAIN")
                ),
                Sequence("SET", "COMPRESSION", Ref("ParameterNameSegment")),
            ),
        ),
        Sequence("CLUSTER", "ON", Ref("ParameterNameSegment")),
        Sequence("SET", "WITHOUT", "CLUSTER"),
        Sequence(
            "SET",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Sequence(
                            Ref("EqualsSegment"), Ref("LiteralGrammar"), optional=True
                        ),
                    )
                )
            ),
        ),
        Sequence(
            "RESET",
            Bracketed(Delimited(Ref("ParameterNameSegment"))),
        ),
        Sequence(
            "OWNER",
            "TO",
            OneOf(
                Ref("ObjectReferenceSegment"),
                "CURRENT_ROLE",
                "CURRENT_USER",
                "SESSION_USER",
            ),
        ),
    )


@postgres_dialect.segment()
class RefreshMaterializedViewStatementSegment(BaseSegment):
    """A `REFRESH MATERIALIZED VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-refreshmaterializedview.html
    """

    type = "refresh_materialized_view_statement"

    match_grammar = StartsWith(Sequence("REFRESH", "MATERIALIZED", "VIEW"))

    parse_grammar = Sequence(
        "REFRESH",
        "MATERIALIZED",
        "VIEW",
        Ref.keyword("CONCURRENTLY", optional=True),
        Ref("TableReferenceSegment"),
        Ref("WithDataClauseSegment", optional=True),
    )


@postgres_dialect.segment()
class DropMaterializedViewStatementSegment(BaseSegment):
    """A `DROP MATERIALIZED VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-dropmaterializedview.html
    """

    type = "drop_materialized_view_statement"

    match_grammar = StartsWith(Sequence("DROP", "MATERIALIZED", "VIEW"))

    parse_grammar = Sequence(
        "DROP",
        "MATERIALIZED",
        "VIEW",
        Sequence("IF", "EXISTS", optional=True),
        Delimited(Ref("TableReferenceSegment")),
        OneOf("CASCADE", "RESTRICT", optional=True),
    )


@postgres_dialect.segment()
class AlterViewStatementSegment(BaseSegment):
    """An `ALTER VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-alterview.html
    """

    type = "alter_view_statement"

    match_grammar = StartsWith(Sequence("ALTER", "VIEW"))

    parse_grammar = Sequence(
        "ALTER",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "ALTER",
                Ref.keyword("COLUMN", optional=True),
                Ref("ColumnReferenceSegment"),
                OneOf(
                    Sequence(
                        "SET",
                        "DEFAULT",
                        OneOf(
                            Ref("LiteralGrammar"),
                            Ref("FunctionSegment"),
                            Ref("BareFunctionSegment"),
                            Ref("ExpressionSegment"),
                        ),
                    ),
                    Sequence("DROP", "DEFAULT"),
                ),
            ),
            Sequence(
                "OWNER",
                "TO",
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    "CURRENT_ROLE",
                    "CURRENT_USER",
                    "SESSION_USER",
                ),
            ),
            Sequence(
                "RENAME",
                Ref.keyword("COLUMN", optional=True),
                Ref("ColumnReferenceSegment"),
                "TO",
                Ref("ColumnReferenceSegment"),
            ),
            Sequence("RENAME", "TO", Ref("TableReferenceSegment")),
            Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
            Sequence(
                "SET",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ParameterNameSegment"),
                            Sequence(
                                Ref("EqualsSegment"),
                                Ref("LiteralGrammar"),
                                optional=True,
                            ),
                        )
                    )
                ),
            ),
            Sequence(
                "RESET",
                Bracketed(Delimited(Ref("ParameterNameSegment"))),
            ),
        ),
    )


@postgres_dialect.segment(replace=True)
class CreateDatabaseStatementSegment(BaseSegment):
    """A `CREATE DATABASE` statement.

    As specified in https://www.postgresql.org/docs/14/sql-createdatabase.html
    """

    type = "create_database_statement"

    match_grammar = StartsWith(Sequence("CREATE", "DATABASE"))

    parse_grammar = Sequence(
        "CREATE",
        "DATABASE",
        Ref("DatabaseReferenceSegment"),
        Ref.keyword("WITH", optional=True),
        AnyNumberOf(
            Sequence(
                "OWNER",
                Ref("EqualsSegment", optional=True),
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "TEMPLATE",
                Ref("EqualsSegment", optional=True),
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "ENCODING",
                Ref("EqualsSegment", optional=True),
                OneOf(Ref("QuotedLiteralSegment"), "DEFAULT"),
            ),
            OneOf(
                # LOCALE This is a shortcut for setting LC_COLLATE and LC_CTYPE at once.
                # If you specify this, you cannot specify either of those parameters.
                Sequence(
                    "LOCALE",
                    Ref("EqualsSegment", optional=True),
                    Ref("QuotedLiteralSegment"),
                ),
                AnyNumberOf(
                    Sequence(
                        "LC_COLLATE",
                        Ref("EqualsSegment", optional=True),
                        Ref("QuotedLiteralSegment"),
                    ),
                    Sequence(
                        "LC_CTYPE",
                        Ref("EqualsSegment", optional=True),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            Sequence(
                "TABLESPACE",
                Ref("EqualsSegment", optional=True),
                Ref("ParameterNameSegment"),
            ),
            Sequence(
                "ALLOW_CONNECTIONS",
                Ref("EqualsSegment", optional=True),
                Ref("BooleanLiteralGrammar"),
            ),
            Sequence(
                "CONNECTION",
                "LIMIT",
                Ref("EqualsSegment", optional=True),
                Ref("NumericLiteralSegment"),
            ),
            Sequence(
                "IS_TEMPLATE",
                Ref("EqualsSegment", optional=True),
                Ref("BooleanLiteralGrammar"),
            ),
        ),
    )


@postgres_dialect.segment()
class AlterDatabaseStatementSegment(BaseSegment):
    """A `ALTER DATABASE` statement.

    As specified in https://www.postgresql.org/docs/14/sql-alterdatabase.html
    """

    type = "alter_database_statement"

    match_grammar = StartsWith(Sequence("ALTER", "DATABASE"))

    parse_grammar = Sequence(
        "ALTER",
        "DATABASE",
        Ref("DatabaseReferenceSegment"),
        OneOf(
            Sequence(
                Ref.keyword("WITH", optional=True),
                AnyNumberOf(
                    Sequence("ALLOW_CONNECTIONS", Ref("BooleanLiteralGrammar")),
                    Sequence(
                        "CONNECTION",
                        "LIMIT",
                        Ref("NumericLiteralSegment"),
                    ),
                    Sequence("IS_TEMPLATE", Ref("BooleanLiteralGrammar")),
                    min_times=1,
                ),
            ),
            Sequence("RENAME", "TO", Ref("DatabaseReferenceSegment")),
            Sequence(
                "OWNER",
                "TO",
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    "CURRENT_ROLE",
                    "CURRENT_USER",
                    "SESSION_USER",
                ),
            ),
            Sequence("SET", "TABLESPACE", Ref("ParameterNameSegment")),
            Sequence(
                "SET",
                Ref("ParameterNameSegment"),
                OneOf(
                    Sequence(
                        OneOf("TO", Ref("EqualsSegment")),
                        OneOf("DEFAULT", Ref("LiteralGrammar")),
                    ),
                    Sequence("FROM", "CURRENT"),
                ),
            ),
            Sequence("RESET", OneOf("ALL", Ref("ParameterNameSegment"))),
            optional=True,
        ),
    )


@postgres_dialect.segment()
class DropDatabaseStatementSegment(BaseSegment):
    """A `DROP DATABASE` statement.

    As specified in https://www.postgresql.org/docs/14/sql-dropdatabase.html
    """

    type = "drop_database_statement"

    match_grammar = StartsWith(Sequence("DROP", "DATABASE"))

    parse_grammar = Sequence(
        "DROP",
        "DATABASE",
        Sequence("IF", "EXISTS", optional=True),
        Ref("DatabaseReferenceSegment"),
        Sequence(
            Ref.keyword("WITH", optional=True),
            Bracketed("FORCE"),
            optional=True,
        ),
    )


@postgres_dialect.segment()
class LikeOptionSegment(BaseSegment):
    """Like Option Segment.

    As specified in https://www.postgresql.org/docs/13/sql-createtable.html
    """

    type = "like_option_segment"

    match_grammar = Sequence(
        OneOf("INCLUDING", "EXCLUDING"),
        OneOf(
            "COMMENTS",
            "CONSTRAINTS",
            "DEFAULTS",
            "GENERATED",
            "IDENTITY",
            "INDEXES",
            "STATISTICS",
            "STORAGE",
            "ALL",
        ),
    )


@postgres_dialect.segment(replace=True)
class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more.

    This matches the definition in https://www.postgresql.org/docs/13/sql-altertable.html
    """

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
            Sequence(
                "CHECK",
                Bracketed(Ref("ExpressionSegment")),
                Sequence("NO", "INHERIT", optional=True),
            ),
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    Ref("BareFunctionSegment"),
                    Ref("ExpressionSegment")
                    # ?? Ref('IntervalExpressionSegment')
                ),
            ),
            Sequence("GENERATED", "ALWAYS", "AS", Ref("ExpressionSegment"), "STORED"),
            Sequence(
                "GENERATED",
                OneOf("ALWAYS", Sequence("BY", "DEFAULT")),
                "AS",
                "IDENTITY",
                Bracketed(
                    AnyNumberOf(Ref("AlterSequenceOptionsSegment")), optional=True
                ),
            ),
            "UNIQUE",
            Ref("PrimaryKeyGrammar"),
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                Sequence(
                    "ON",
                    OneOf("DELETE", "UPDATE"),
                    Ref("ReferentialActionSegment"),
                    optional=True,
                ),
            ),
        ),
        OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
        OneOf(
            Sequence("INITIALLY", "DEFERRED"),
            Sequence("INITIALLY", "IMMEDIATE"),
            optional=True,
        ),
    )


@postgres_dialect.segment()
class PartitionBoundSpecSegment(BaseSegment):
    """partition_bound_spec as per https://www.postgresql.org/docs/13/sql-altertable.html."""

    match_grammar = OneOf(
        Sequence(
            "IN",
            Bracketed(
                Delimited(Ref("ExpressionSegment"), delimiter=Ref("CommaSegment"))
            ),
        ),
        Sequence(
            "FROM",
            Bracketed(
                Delimited(
                    OneOf(Ref("ExpressionSegment"), "MINVALUE", "MAXVALUE"),
                    delimiter=Ref("CommaSegment"),
                )
            ),
            "TO",
            Bracketed(
                Delimited(
                    OneOf(Ref("ExpressionSegment"), "MINVALUE", "MAXVALUE"),
                    delimiter=Ref("CommaSegment"),
                )
            ),
        ),
        Sequence(
            "WITH",
            Bracketed(
                Sequence(
                    "MODULUS",
                    Ref("NumericLiteralSegment"),
                    Ref("CommaSegment"),
                    "REMAINDER",
                    Ref("NumericLiteralSegment"),
                )
            ),
        ),
    )


@postgres_dialect.segment(replace=True)
class TableConstraintSegment(BaseSegment):
    """A table constraint, e.g. for CREATE TABLE.

    As specified in https://www.postgresql.org/docs/13/sql-altertable.html
    """

    type = "table_constraint_segment"

    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        OneOf(
            Sequence(
                "CHECK",
                Bracketed(Ref("ExpressionSegment")),
                Sequence("NO", "INHERIT", optional=True),
            ),
            Sequence(  # UNIQUE ( column_name [, ... ] )
                "UNIQUE",
                Ref("BracketedColumnReferenceListGrammar"),
                Ref("IndexParametersSegment", optional=True),
            ),
            Sequence(  # PRIMARY KEY ( column_name [, ... ] ) index_parameters
                Ref("PrimaryKeyGrammar"),
                # Columns making up PRIMARY KEY constraint
                Ref("BracketedColumnReferenceListGrammar"),
                Ref("IndexParametersSegment", optional=True),
            ),
            Sequence(
                "EXCLUDE",
                Sequence("USING", Ref("FunctionSegment"), optional=True),
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ExcludeElementSegment"),
                            "WITH",
                            Ref("ComparisonOperatorGrammar"),
                        )
                    )
                ),
                Ref("IndexParametersSegment", optional=True),
                Sequence("WHERE", Ref("ExpressionSegment")),
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
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                Sequence("MATCH", OneOf("FULL", "PARTIAL", "SIMPLE"), optional=True),
                Sequence(
                    "ON", "DELETE", Ref("ReferentialActionSegment"), optional=True
                ),
                Sequence(
                    "ON", "UPDATE", Ref("ReferentialActionSegment"), optional=True
                ),
            ),
            OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
            OneOf(
                Sequence("INITIALLY", "DEFERRED"),
                Sequence("INITIALLY", "IMMEDIATE"),
                optional=True,
            ),
        ),
    )


@postgres_dialect.segment()
class TableConstraintUsingIndexSegment(BaseSegment):
    """table_constraint_using_index as specified in https://www.postgresql.org/docs/13/sql-altertable.html."""

    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        Sequence(
            OneOf("UNIQUE", Sequence("PRIMARY", "KEY")),
            "USING",
            "INDEX",
            Ref("ParameterNameSegment"),
        ),
        OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
        OneOf(
            Sequence("INITIALLY", "DEFERRED"),
            Sequence("INITIALLY", "IMMEDIATE"),
            optional=True,
        ),
    )


@postgres_dialect.segment()
class IndexParametersSegment(BaseSegment):
    """index_parameters as specified in https://www.postgresql.org/docs/13/sql-altertable.html."""

    type = "index_parameters"

    match_grammar = Sequence(
        Sequence("INCLUDE", Ref("BracketedColumnReferenceListGrammar"), optional=True),
        Sequence(
            "WITH",
            Bracketed(
                Delimited(
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment"),
                        Ref("LiteralGrammar"),
                    ),
                    delimiter=Ref("CommaSegment"),
                )
            ),
            optional=True,
        ),
        Sequence(
            "USING", "INDEX", "TABLESPACE", Ref("ParameterNameSegment"), optional=True
        ),
    )


@postgres_dialect.segment()
class ReferentialActionSegment(BaseSegment):
    """Foreign Key constraints.

    As found in https://www.postgresql.org/docs/13/infoschema-referential-constraints.html
    """

    type = "referential_action"

    match_grammar = OneOf(
        "CASCADE",
        Sequence("SET", "NULL"),
        Sequence("SET", "DEFAULT"),
        "RESTRICT",
        Sequence("NO", "ACTION"),
    )


@postgres_dialect.segment()
class ExcludeElementSegment(BaseSegment):
    """exclude_element segment as found in https://www.postgresql.org/docs/13/sql-altertable.html."""

    match_grammar = Sequence(
        OneOf(Ref("ColumnReferenceSegment"), Bracketed(Ref("ExpressionSegment"))),
        Ref("ParameterNameSegment", optional=True),
        OneOf("ASC", "DESC", optional=True),
        Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
    )


@postgres_dialect.segment()
class AlterDefaultPrivilegesStatementSegment(BaseSegment):
    """`ALTER DEFAULT PRIVILEGES` statement.

    ```
    ALTER DEFAULT PRIVILEGES
    [ FOR { ROLE | USER } target_role [, ...] ]
    [ IN SCHEMA schema_name [, ...] ]
    abbreviated_grant_or_revoke
    ```

    https://www.postgresql.org/docs/13/sql-alterdefaultprivileges.html
    """

    type = "alter_default_privileges_statement"
    match_grammar = Sequence(
        "ALTER",
        "DEFAULT",
        "PRIVILEGES",
        Sequence(
            "FOR",
            OneOf("ROLE", "USER"),
            Delimited(
                Ref("ObjectReferenceSegment"),
                terminator=OneOf("IN", "GRANT", "REVOKE"),
            ),
            optional=True,
        ),
        Sequence(
            "IN",
            "SCHEMA",
            Delimited(
                Ref("SchemaReferenceSegment"),
                terminator=OneOf("GRANT", "REVOKE"),
            ),
            optional=True,
        ),
        OneOf(
            Ref("AlterDefaultPrivilegesGrantSegment"),
            Ref("AlterDefaultPrivilegesRevokeSegment"),
        ),
    )


@postgres_dialect.segment()
class AlterDefaultPrivilegesObjectPrivilegesSegment(BaseSegment):
    """`ALTER DEFAULT PRIVILEGES` object privileges.

    https://www.postgresql.org/docs/13/sql-alterdefaultprivileges.html
    """

    type = "alter_default_privileges_object_privilege"
    match_grammar = OneOf(
        Sequence("ALL", Ref.keyword("PRIVILEGES", optional=True)),
        Delimited(
            "CREATE",
            "DELETE",
            "EXECUTE",
            "INSERT",
            "REFERENCES",
            "SELECT",
            "TRIGGER",
            "TRUNCATE",
            "UPDATE",
            "USAGE",
            terminator="ON",
        ),
    )


@postgres_dialect.segment()
class AlterDefaultPrivilegesSchemaObjectsSegment(BaseSegment):
    """`ALTER DEFAULT PRIVILEGES` schema object types.

    https://www.postgresql.org/docs/13/sql-alterdefaultprivileges.html
    """

    type = "alter_default_privileges_schema_object"
    match_grammar = OneOf(
        "TABLES",
        "FUNCTIONS",
        "ROUTINES",
        "SEQUENCES",
        "TYPES",
        "SCHEMAS",
    )


@postgres_dialect.segment()
class AlterDefaultPrivilegesToFromRolesSegment(BaseSegment):
    """The segment after `TO` / `FROM`  in `ALTER DEFAULT PRIVILEGES`.

    `{ [ GROUP ] role_name | PUBLIC } [, ...]`

    https://www.postgresql.org/docs/13/sql-alterdefaultprivileges.html
    """

    type = "alter_default_privileges_to_from_roles"
    match_grammar = OneOf(
        Sequence(
            Ref.keyword("GROUP", optional=True),
            Ref("ObjectReferenceSegment"),
        ),
        "PUBLIC",
    )


@postgres_dialect.segment()
class AlterDefaultPrivilegesGrantSegment(BaseSegment):
    """`GRANT` for `ALTER DEFAULT PRIVILEGES`.

    https://www.postgresql.org/docs/13/sql-alterdefaultprivileges.html
    """

    type = "alter_default_privileges_grant"
    match_grammar = Sequence(
        "GRANT",
        Ref("AlterDefaultPrivilegesObjectPrivilegesSegment"),
        "ON",
        Ref("AlterDefaultPrivilegesSchemaObjectsSegment"),
        "TO",
        Delimited(
            Ref("AlterDefaultPrivilegesToFromRolesSegment"),
            terminator="WITH",
        ),
        Sequence("WITH", "GRANT", "OPTION", optional=True),
    )


@postgres_dialect.segment()
class AlterDefaultPrivilegesRevokeSegment(BaseSegment):
    """`REVOKE` for `ALTER DEFAULT PRIVILEGES`.

    https://www.postgresql.org/docs/13/sql-alterdefaultprivileges.html
    """

    type = "alter_default_privileges_revoke"
    match_grammar = Sequence(
        "REVOKE",
        Sequence("GRANT", "OPTION", "FOR", optional=True),
        Ref("AlterDefaultPrivilegesObjectPrivilegesSegment"),
        "ON",
        Ref("AlterDefaultPrivilegesSchemaObjectsSegment"),
        "FROM",
        Delimited(
            Ref("AlterDefaultPrivilegesToFromRolesSegment"),
            terminator=OneOf("RESTRICT", "CASCADE"),
        ),
        OneOf("RESTRICT", "CASCADE", optional=True),
    )


@postgres_dialect.segment()
class CommentOnStatementSegment(BaseSegment):
    """`COMMENT ON` statement.

    https://www.postgresql.org/docs/13/sql-comment.html
    """

    type = "comment_on_statement"

    match_grammar = StartsWith(Sequence("COMMENT", "ON"))
    parse_grammar = Sequence(
        "COMMENT",
        "ON",
        Sequence(
            OneOf(
                Sequence(
                    OneOf(
                        "TABLE",
                        # TODO: Create a ViewReferenceSegment
                        "VIEW",
                    ),
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "CAST",
                    Bracketed(
                        Sequence(
                            Ref("ObjectReferenceSegment"),
                            "AS",
                            Ref("ObjectReferenceSegment"),
                        ),
                    ),
                ),
                Sequence(
                    "COLUMN",
                    # TODO: Does this correctly emit a Table Reference?
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    "CONSTRAINT",
                    Ref("ObjectReferenceSegment"),
                    Sequence(
                        "ON",
                        Ref.keyword("DOMAIN", optional=True),
                        Ref("ObjectReferenceSegment"),
                    ),
                ),
                Sequence(
                    "DATABASE",
                    Ref("DatabaseReferenceSegment"),
                ),
                Sequence(
                    "EXTENSION",
                    Ref("ExtensionReferenceSegment"),
                ),
                Sequence(
                    "FUNCTION",
                    Ref("FunctionNameSegment"),
                    Ref("FunctionParameterListGrammar"),
                ),
                Sequence(
                    "INDEX",
                    Ref("IndexReferenceSegment"),
                ),
                Sequence(
                    "SCHEMA",
                    Ref("SchemaReferenceSegment"),
                ),
                # TODO: Split out individual items if they have references
                Sequence(
                    OneOf(
                        "COLLATION",
                        "CONVERSION",
                        "DOMAIN",
                        "LANGUAGE",
                        "POLICY",
                        "PUBLICATION",
                        "ROLE",
                        "RULE",
                        "SEQUENCE",
                        "SERVER",
                        "STATISTICS",
                        "SUBSCRIPTION",
                        "TABLESPACE",
                        "TRIGGER",
                        "TYPE",
                        Sequence("ACCESS", "METHOD"),
                        Sequence("EVENT", "TRIGGER"),
                        Sequence("FOREIGN", "DATA", "WRAPPER"),
                        Sequence("FOREIGN", "TABLE"),
                        Sequence("MATERIALIZED", "VIEW"),
                        Sequence("TEXT", "SEARCH", "CONFIGURATION"),
                        Sequence("TEXT", "SEARCH", "DICTIONARY"),
                        Sequence("TEXT", "SEARCH", "PARSER"),
                        Sequence("TEXT", "SEARCH", "TEMPLATE"),
                    ),
                    Ref("ObjectReferenceSegment"),
                    Sequence("ON", Ref("ObjectReferenceSegment"), optional=True),
                ),
                Sequence(
                    OneOf(
                        "AGGREGATE",
                        "PROCEDURE",
                        "ROUTINE",
                    ),
                    Ref("ObjectReferenceSegment"),
                    Bracketed(
                        Sequence(
                            # TODO: Is this too permissive?
                            Anything(),
                        ),
                    ),
                ),
            ),
            Sequence("IS", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
        ),
    )


@postgres_dialect.segment(replace=True)
class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` statement.

    As specified in https://www.postgresql.org/docs/13/sql-createindex.html
    """

    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref.keyword("UNIQUE", optional=True),
        Ref("OrReplaceGrammar", optional=True),
        "INDEX",
        Ref.keyword("CONCURRENTLY", optional=True),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment", optional=True),
        "ON",
        Ref.keyword("ONLY", optional=True),
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence("USING", Ref("FunctionSegment"), optional=True),
            Bracketed(
                Delimited(
                    Sequence(
                        OneOf(
                            Ref("ColumnReferenceSegment"),
                            OptionallyBracketed(Ref("FunctionSegment")),
                            Bracketed(Ref("ExpressionSegment")),
                        ),
                        AnyNumberOf(
                            Sequence(
                                "COLLATE",
                                OneOf(
                                    Ref("LiteralGrammar"),
                                    Ref("QuotedIdentifierSegment"),
                                ),
                            ),
                            Sequence(
                                Ref("ParameterNameSegment"),
                                Bracketed(
                                    Delimited(
                                        Sequence(
                                            Ref("ParameterNameSegment"),
                                            Ref("EqualsSegment"),
                                            OneOf(
                                                Ref("LiteralGrammar"),
                                                Ref("QuotedIdentifierSegment"),
                                            ),
                                        ),
                                        delimiter=Ref("CommaSegment"),
                                    ),
                                ),
                            ),
                            OneOf("ASC", "DESC"),
                            OneOf(
                                Sequence("NULLS", "FIRST"), Sequence("NULLS", "LAST")
                            ),
                        ),
                    ),
                    delimiter=Ref("CommaSegment"),
                )
            ),
        ),
        AnyNumberOf(
            Sequence(
                "INCLUDE",
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"), delimiter=Ref("CommaSegment")
                    )
                ),
            ),
            Sequence(
                "WITH",
                Bracketed(
                    Delimited(
                        Sequence(
                            Ref("ParameterNameSegment"),
                            Ref("EqualsSegment"),
                            Ref("LiteralGrammar"),
                        ),
                        delimiter=Ref("CommaSegment"),
                    )
                ),
            ),
            Sequence("TABLESPACE", Ref("TableReferenceSegment")),
            Sequence("WHERE", Ref("ExpressionSegment")),
        ),
    )


@postgres_dialect.segment(replace=True)
class FrameClauseSegment(BaseSegment):
    """A frame clause for window functions.

    As specified in https://www.postgresql.org/docs/13/sql-expressions.html
    """

    type = "frame_clause"

    _frame_extent = OneOf(
        Sequence("CURRENT", "ROW"),
        Sequence(
            OneOf(Ref("NumericLiteralSegment"), "UNBOUNDED"),
            OneOf("PRECEDING", "FOLLOWING"),
        ),
    )

    _frame_exclusion = Sequence(
        "EXCLUDE",
        OneOf(Sequence("CURRENT", "ROW"), "GROUP", "TIES", Sequence("NO", "OTHERS")),
        optional=True,
    )

    match_grammar = Sequence(
        Ref("FrameClauseUnitGrammar"),
        OneOf(_frame_extent, Sequence("BETWEEN", _frame_extent, "AND", _frame_extent)),
        _frame_exclusion,
    )


@postgres_dialect.segment(replace=True)
class CreateSequenceOptionsSegment(BaseSegment):
    """Options for Create Sequence statement.

    As specified in https://www.postgresql.org/docs/13/sql-createsequence.html
    """

    type = "create_sequence_options_segment"

    match_grammar = OneOf(
        Sequence("AS", Ref("DatatypeSegment")),
        Sequence(
            "INCREMENT", Ref.keyword("BY", optional=True), Ref("NumericLiteralSegment")
        ),
        OneOf(
            Sequence("MINVALUE", Ref("NumericLiteralSegment")),
            Sequence("NO", "MINVALUE"),
        ),
        OneOf(
            Sequence("MAXVALUE", Ref("NumericLiteralSegment")),
            Sequence("NO", "MAXVALUE"),
        ),
        Sequence(
            "START", Ref.keyword("WITH", optional=True), Ref("NumericLiteralSegment")
        ),
        Sequence("CACHE", Ref("NumericLiteralSegment")),
        OneOf("CYCLE", Sequence("NO", "CYCLE")),
        Sequence("OWNED", "BY", OneOf("NONE", Ref("ColumnReferenceSegment"))),
    )


@postgres_dialect.segment(replace=True)
class CreateSequenceStatementSegment(BaseSegment):
    """Create Sequence Statement.

    As specified in https://www.postgresql.org/docs/13/sql-createsequence.html
    """

    type = "create_sequence_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("TemporaryGrammar", optional=True),
        "SEQUENCE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("SequenceReferenceSegment"),
        AnyNumberOf(Ref("CreateSequenceOptionsSegment"), optional=True),
    )


@postgres_dialect.segment(replace=True)
class AlterSequenceOptionsSegment(BaseSegment):
    """Dialect-specific options for ALTER SEQUENCE statement.

    As specified in https://www.postgresql.org/docs/13/sql-altersequence.html
    """

    type = "alter_sequence_options_segment"

    match_grammar = OneOf(
        Sequence("AS", Ref("DatatypeSegment")),
        Sequence(
            "INCREMENT", Ref.keyword("BY", optional=True), Ref("NumericLiteralSegment")
        ),
        OneOf(
            Sequence("MINVALUE", Ref("NumericLiteralSegment")),
            Sequence("NO", "MINVALUE"),
        ),
        OneOf(
            Sequence("MAXVALUE", Ref("NumericLiteralSegment")),
            Sequence("NO", "MAXVALUE"),
        ),
        # N.B. The SEQUENCE NAME keywords are undocumented but are produced
        # by the pg_dump utility. See discussion in issue #1857.
        Sequence("SEQUENCE", "NAME", Ref("SequenceReferenceSegment")),
        Sequence(
            "START", Ref.keyword("WITH", optional=True), Ref("NumericLiteralSegment")
        ),
        Sequence(
            "RESTART", Ref.keyword("WITH", optional=True), Ref("NumericLiteralSegment")
        ),
        Sequence("CACHE", Ref("NumericLiteralSegment")),
        Sequence(Ref.keyword("NO", optional=True), "CYCLE"),
        Sequence("OWNED", "BY", OneOf("NONE", Ref("ColumnReferenceSegment"))),
    )


@postgres_dialect.segment(replace=True)
class AlterSequenceStatementSegment(BaseSegment):
    """Alter Sequence Statement.

    As specified in https://www.postgresql.org/docs/13/sql-altersequence.html
    """

    type = "alter_sequence_statement"

    match_grammar = Sequence(
        "ALTER",
        "SEQUENCE",
        Ref("IfExistsGrammar", optional=True),
        Ref("SequenceReferenceSegment"),
        OneOf(
            AnyNumberOf(Ref("AlterSequenceOptionsSegment", optional=True)),
            Sequence(
                "OWNER",
                "TO",
                OneOf(Ref("ParameterNameSegment"), "CURRENT_USER", "SESSION_USER"),
            ),
            Sequence("RENAME", "TO", Ref("SequenceReferenceSegment")),
            Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
        ),
    )


@postgres_dialect.segment(replace=True)
class DropSequenceStatementSegment(BaseSegment):
    """Drop Sequence Statement.

    As specified in https://www.postgresql.org/docs/13/sql-dropsequence.html
    """

    type = "drop_sequence_statement"

    match_grammar = Sequence(
        "DROP",
        "SEQUENCE",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("SequenceReferenceSegment")),
        OneOf("CASCADE", "RESTRICT", optional=True),
    )


@postgres_dialect.segment()
class AnalyzeStatementSegment(BaseSegment):
    """Analyze Statement Segment.

    As specified in https://www.postgresql.org/docs/13/sql-analyze.html
    """

    type = "analyze_statement"

    _option = Sequence(
        OneOf("VERBOSE", "SKIP_LOCKED"), Ref("BooleanLiteralGrammar", optional=True)
    )

    _tables_and_columns = Sequence(
        Ref("TableReferenceSegment"),
        Bracketed(Delimited(Ref("ColumnReferenceSegment")), optional=True),
    )

    match_grammar = Sequence(
        OneOf("ANALYZE", "ANALYSE"),
        OneOf(Bracketed(Delimited(_option)), "VERBOSE", optional=True),
        Delimited(_tables_and_columns, optional=True),
    )


# Adding PostgreSQL specific statements
@postgres_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("AlterDefaultPrivilegesStatementSegment"),
            Ref("CommentOnStatementSegment"),
            Ref("AnalyzeStatementSegment"),
            Ref("CreateTableAsStatementSegment"),
            Ref("AlterTriggerStatementSegment"),
            Ref("SetStatementSegment"),
            Ref("DropFunctionStatementSegment"),
            Ref("CreatePolicyStatementSegment"),
            Ref("DropPolicyStatementSegment"),
            Ref("CreateMaterializedViewStatementSegment"),
            Ref("AlterMaterializedViewStatementSegment"),
            Ref("DropMaterializedViewStatementSegment"),
            Ref("RefreshMaterializedViewStatementSegment"),
            Ref("AlterDatabaseStatementSegment"),
            Ref("DropDatabaseStatementSegment"),
            Ref("AlterFunctionStatementSegment"),
            Ref("AlterViewStatementSegment"),
        ],
    )

    match_grammar = ansi_dialect.get_segment("StatementSegment").match_grammar.copy()


@postgres_dialect.segment(replace=True)
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


@postgres_dialect.segment(replace=True)
class CreateTriggerStatementSegment(BaseSegment):
    """Create Trigger Statement.

    As Specified in https://www.postgresql.org/docs/14/sql-createtrigger.html
    """

    type = "create_trigger"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref.keyword("CONSTRAINT", optional=True),
        "TRIGGER",
        Anything(),
    )

    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref.keyword("CONSTRAINT", optional=True),
        "TRIGGER",
        Ref("TriggerReferenceSegment"),
        OneOf("BEFORE", "AFTER", Sequence("INSTEAD", "OF")),
        Delimited(
            "INSERT",
            "DELETE",
            "TRUNCATE",
            Sequence(
                "UPDATE",
                Sequence(
                    "OF",
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                        terminator=OneOf("OR", "ON"),
                    ),
                    optional=True,
                ),
            ),
            delimiter="OR",
        ),
        "ON",
        Ref("TableReferenceSegment"),
        AnyNumberOf(
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
                "REFERENCING",
                OneOf("OLD", "NEW"),
                "TABLE",
                "AS",
                Ref("TableReferenceSegment"),
                Sequence(
                    OneOf("OLD", "NEW"),
                    "TABLE",
                    "AS",
                    Ref("TableReferenceSegment"),
                    optional=True,
                ),
            ),
            Sequence(
                "FOR", Ref.keyword("EACH", optional=True), OneOf("ROW", "STATEMENT")
            ),
            Sequence("WHEN", Bracketed(Ref("ExpressionSegment"))),
        ),
        Sequence(
            "EXECUTE",
            OneOf("FUNCTION", "PROCEDURE"),
            Ref("FunctionNameIdentifierSegment"),
            Bracketed(Ref("FunctionContentsGrammar", optional=True)),
        ),
    )


@postgres_dialect.segment()
class AlterTriggerStatementSegment(BaseSegment):
    """Alter Trigger Statement.

    As Specified in https://www.postgresql.org/docs/14/sql-altertrigger.html
    """

    type = "alter_trigger"

    match_grammar = Sequence("ALTER", "TRIGGER", Anything())

    parse_grammar = Sequence(
        "ALTER",
        "TRIGGER",
        Ref("TriggerReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("TriggerReferenceSegment")),
            Sequence(
                Ref.keyword("NO", optional=True),
                "DEPENDS",
                "ON",
                "EXTENSION",
                Ref("ParameterNameSegment"),
            ),
        ),
    )


@postgres_dialect.segment(replace=True)
class DropTriggerStatementSegment(BaseSegment):
    """Drop Trigger Statement.

    As Specified in https://www.postgresql.org/docs/14/sql-droptrigger.html
    """

    type = "drop_trigger"

    match_grammar = Sequence("DROP", "TRIGGER", Anything())

    parse_grammar = Sequence(
        "DROP",
        "TRIGGER",
        Sequence("IF", "EXISTS", optional=True),
        Ref("TriggerReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        OneOf("CASCADE", "RESTRICT", optional=True),
    )


@postgres_dialect.segment(replace=True)
class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-insert.html
    N.B. This is not a complete implementation of the documentation above.
    TODO: Implement complete postgres insert statement structure.
    """

    type = "insert_statement"
    match_grammar = StartsWith("INSERT")
    parse_grammar = Sequence(
        "INSERT",
        "INTO",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Sequence("OVERRIDING", OneOf("SYSTEM", "USER"), "VALUE", optional=True),
        Ref("SelectableGrammar"),
    )


@postgres_dialect.segment(replace=True)
class DropTypeStatementSegment(BaseSegment):
    """Drop Type Statement.

    As specified in https://www.postgresql.org/docs/14/sql-droptype.html
    """

    type = "drop_type_statement"

    match_grammar = Sequence(
        "DROP",
        "TYPE",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("DatatypeSegment")),
        OneOf("CASCADE", "RESTRICT", optional=True),
    )


@postgres_dialect.segment()
class SetStatementSegment(BaseSegment):
    """Set Statement.

    As specified in https://www.postgresql.org/docs/14/sql-set.html
    """

    type = "set_statement"

    match_grammar = Sequence(
        "SET",
        OneOf("SESSION", "LOCAL", optional=True),
        OneOf(
            Sequence(
                Ref("ParameterNameSegment"),
                OneOf("TO", Ref("EqualsSegment")),
                OneOf(
                    Delimited(Ref("LiteralGrammar"), Ref("NakedIdentifierSegment")),
                    "DEFAULT",
                ),
            ),
            Sequence(
                "TIME", "ZONE", OneOf(Ref("QuotedLiteralSegment"), "LOCAL", "DEFAULT")
            ),
        ),
    )


@postgres_dialect.segment()
class CreatePolicyStatementSegment(BaseSegment):
    """A `CREATE POLICY` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-createpolicy.html
    """

    type = "create_policy_statement"
    match_grammar = StartsWith(Sequence("CREATE", "POLICY"))
    parse_grammar = Sequence(
        "CREATE",
        "POLICY",
        Ref("ObjectReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence("AS", OneOf("PERMISSIVE", "RESTRICTIVE"), optional=True),
        Sequence(
            "FOR", OneOf("ALL", "SELECT", "INSERT", "UPDATE", "DELETE"), optional=True
        ),
        Sequence(
            "TO",
            Delimited(
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    "PUBLIC",
                    "CURRENT_ROLE",
                    "CURRENT_USER",
                    "SESSION_USER",
                )
            ),
            optional=True,
        ),
        Sequence("USING", Bracketed(Ref("ExpressionSegment")), optional=True),
        Sequence("WITH", "CHECK", Bracketed(Ref("ExpressionSegment")), optional=True),
    )


@postgres_dialect.segment()
class DropPolicyStatementSegment(BaseSegment):
    """A `DROP POLICY` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-droppolicy.html
    """

    type = "drop_policy_statement"
    match_grammar = StartsWith(Sequence("DROP", "POLICY"))
    parse_grammar = Sequence(
        "DROP",
        "POLICY",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        OneOf("CASCADE", "RESTRICT", optional=True),
    )
