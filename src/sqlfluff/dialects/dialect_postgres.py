"""The PostgreSQL dialect."""

from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    Indent,
    Matchable,
    TypedParser,
    NewlineSegment,
    OneOf,
    OptionallyBracketed,
    Ref,
    RegexLexer,
    RegexParser,
    SegmentGenerator,
    Sequence,
    SymbolSegment,
    StartsWith,
)
from sqlfluff.core.parser.segments.base import BracketedSegment

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser.grammar.anyof import AnySetOf
from sqlfluff.core.parser.lexer import StringLexer
from sqlfluff.dialects.dialect_postgres_keywords import (
    postgres_keywords,
    get_keywords,
    postgres_postgis_datatype_keywords,
)

from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")

postgres_dialect = ansi_dialect.copy_as("postgres")

postgres_dialect.insert_lexer_matchers(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [
        # Explanation for the regex
        # - (?s) Switch - .* includes newline characters
        # - U& - must start with U&
        # - (('')+?(?!')|('.*?(?<!')(?:'')*'(?!')))
        #    ('')+?                                 Any non-zero number of pairs of
        #                                           single quotes -
        #          (?!')                            that are not then followed by a
        #                                           single quote
        #               |                           OR
        #                ('.*?(?<!')(?:'')*'(?!'))
        #                 '.*?                      A single quote followed by anything
        #                                           (non-greedy)
        #                     (?<!')(?:'')*         Any even number of single quotes,
        #                                           including zero
        #                                  '(?!')   Followed by a single quote, which is
        #                                           not followed by a single quote
        # - (\s*UESCAPE\s*'[^0-9A-Fa-f'+\-\s)]')?
        #    \s*UESCAPE\s*                          Whitespace, followed by UESCAPE,
        #                                           followed by whitespace
        #                 '[^0-9A-Fa-f'+\-\s)]'     Any character that isn't A-F, a-f,
        #                                           0-9, +-, or whitespace, in quotes
        #                                       ?   This last block is optional
        RegexLexer(
            "unicode_single_quote",
            r"(?s)U&(('')+?(?!')|('.*?(?<!')(?:'')*'(?!')))(\s*UESCAPE\s*'"
            r"[^0-9A-Fa-f'+\-\s)]')?",
            CodeSegment,
            segment_kwargs={"type": "unicode_single_quote"},
        ),
        # This is similar to the Unicode regex, the key differences being:
        # - E - must start with E
        # - The final quote character must be preceded by:
        # (?<!\\)(?:\\\\)*(?<!')(?:'')     An even/zero number of \ followed by an
        # even/zero number of '
        # OR
        # (?<!\\)(?:\\\\)*\\(?<!')(?:'')*' An odd number of \ followed by an odd number
        # of '
        # There is no UESCAPE block
        RegexLexer(
            "escaped_single_quote",
            r"(?s)E(('')+?(?!')|'.*?((?<!\\)(?:\\\\)*(?<!')(?:'')*|(?<!\\)(?:\\\\)*\\"
            r"(?<!')(?:'')*')'(?!'))",
            CodeSegment,
            segment_kwargs={"type": "escaped_single_quote"},
        ),
        # Double quote Unicode string cannot be empty, and have no single quote escapes
        RegexLexer(
            "unicode_double_quote",
            r'(?s)U&".+?"(\s*UESCAPE\s*\'[^0-9A-Fa-f\'+\-\s)]\')?',
            CodeSegment,
            segment_kwargs={"type": "unicode_double_quote"},
        ),
        RegexLexer(
            "json_operator",
            r"->>|#>>|->|#>|@>|<@|\?\||\?|\?&|#-",
            SymbolSegment,
            segment_kwargs={"type": "json_operator"},
        ),
        StringLexer("at", "@", CodeSegment),
    ],
    before="like_operator",
)

postgres_dialect.insert_lexer_matchers(
    [
        # Explanation for the regex
        # \\([^(\\\r\n)])+((\\\\)|(?=\n)|(?=\r\n))?
        # \\                                        Starts with backslash
        #   ([^\\\r\n])+                            Anything that is not a newline or a
        #                                           backslash
        #                 (
        #                  (\\\\)                   Double backslash
        #                        |                  OR
        #                         (?=\n)            The next character is a newline
        #                               |           OR
        #                                (?=\r\n)   The next 2 characters are a carriage
        #                                           return and a newline
        #                                        )
        #                                         ? The previous clause is optional
        RegexLexer(
            # For now we'll just treat meta syntax like comments and so just ignore
            # them. In future we may want to enhance this to actually parse them to
            # ensure they are valid meta commands.
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
            segment_kwargs={"trim_start": ("--"), "type": "inline_comment"},
        ),
        # In Postgres, the only escape character is ' for single quote strings
        RegexLexer(
            "single_quote",
            r"(?s)('')+?(?!')|('.*?(?<!')(?:'')*'(?!'))",
            CodeSegment,
            segment_kwargs={"type": "single_quote"},
        ),
        # In Postgres, there is no escape character for double quote strings
        RegexLexer(
            "double_quote",
            r'(?s)".+?"',
            CodeSegment,
            segment_kwargs={"type": "double_quote"},
        ),
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

# Set the bare functions
postgres_dialect.sets("bare_functions").update(
    ["CURRENT_TIMESTAMP", "CURRENT_TIME", "CURRENT_DATE", "LOCALTIME", "LOCALTIMESTAMP"]
)

# Postgres doesn't have a dateadd function
# Also according to https://www.postgresql.org/docs/14/functions-datetime.html
# It quotes dateparts. So don't need this.
postgres_dialect.sets("date_part_function_name").clear()

# In Postgres, UNNEST() returns a "value table", similar to BigQuery
postgres_dialect.sets("value_table_functions").update(["UNNEST", "GENERATE_SERIES"])

postgres_dialect.add(
    JsonOperatorSegment=TypedParser(
        "json_operator", SymbolSegment, type="binary_operator"
    ),
    SimpleGeometryGrammar=AnyNumberOf(Ref("NumericLiteralSegment")),
    # N.B. this MultilineConcatenateDelimiterGrammar is only created
    # to parse multiline-concatenated string literals
    # and shouldn't be used in other contexts.
    # In general let the parser handle newlines and whitespace.
    MultilineConcatenateNewline=TypedParser(
        "newline",
        NewlineSegment,
        type="newline",
    ),
    MultilineConcatenateDelimiterGrammar=AnyNumberOf(
        Ref("MultilineConcatenateNewline"), min_times=1, allow_gaps=False
    ),
    # Add a Full equivalent which also allow keywords
    NakedIdentifierFullSegment=RegexParser(
        r"[A-Z_][A-Z0-9_]*",
        ansi.IdentifierSegment,
        type="naked_identifier_all",
    ),
    SingleIdentifierFullGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("NakedIdentifierFullSegment"),
    ),
    CascadeRestrictGrammar=OneOf("CASCADE", "RESTRICT"),
)

postgres_dialect.replace(
    LikeGrammar=OneOf("LIKE", "ILIKE", Sequence("SIMILAR", "TO")),
    StringBinaryOperatorGrammar=OneOf(Ref("ConcatSegment"), "COLLATE"),
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment"),
        Ref("LikeOperatorSegment"),
        Sequence("IS", "DISTINCT", "FROM"),
        Sequence("IS", "NOT", "DISTINCT", "FROM"),
        Ref("OverlapSegment"),
        Ref("NotExtendRightSegment"),
        Ref("NotExtendLeftSegment"),
        Ref("AdjacentSegment"),
    ),
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            # Can’t begin with $, must only contain digits, letters, underscore it $ but
            # can’t be all digits.
            r"([A-Z_]+|[0-9]+[A-Z_$])[A-Z0-9_$]*",
            ansi.IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    ParameterNameSegment=RegexParser(
        r'[A-Z_][A-Z0-9_$]*|"[^"]*"', CodeSegment, type="parameter"
    ),
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z_][A-Z0-9_$]*",
        CodeSegment,
        type="function_name_identifier",
    ),
    QuotedLiteralSegment=OneOf(
        # Postgres allows newline-concatenated string literals (#1488).
        # Since these string literals can have comments between them,
        # we use grammar to handle this.
        # Note we CANNOT use Delimited as it's greedy and swallows the
        # last Newline - see #2495
        Sequence(
            TypedParser(
                "single_quote",
                ansi.LiteralSegment,
                type="quoted_literal",
            ),
            AnyNumberOf(
                Ref("MultilineConcatenateDelimiterGrammar"),
                TypedParser(
                    "single_quote",
                    ansi.LiteralSegment,
                    type="quoted_literal",
                ),
            ),
        ),
        Delimited(
            TypedParser(
                "unicode_single_quote",
                ansi.LiteralSegment,
                type="quoted_literal",
            ),
            AnyNumberOf(
                Ref("MultilineConcatenateDelimiterGrammar"),
                TypedParser(
                    "unicode_single_quote",
                    ansi.LiteralSegment,
                    type="quoted_literal",
                ),
            ),
        ),
        Delimited(
            TypedParser(
                "escaped_single_quote",
                ansi.LiteralSegment,
                type="quoted_literal",
            ),
            AnyNumberOf(
                Ref("MultilineConcatenateDelimiterGrammar"),
                TypedParser(
                    "escaped_single_quote",
                    ansi.LiteralSegment,
                    type="quoted_literal",
                ),
            ),
        ),
        Delimited(
            TypedParser(
                "dollar_quote",
                ansi.LiteralSegment,
                type="quoted_literal",
            ),
            AnyNumberOf(
                Ref("MultilineConcatenateDelimiterGrammar"),
                TypedParser(
                    "dollar_quote",
                    ansi.LiteralSegment,
                    type="quoted_literal",
                ),
            ),
        ),
    ),
    QuotedIdentifierSegment=OneOf(
        TypedParser("double_quote", ansi.IdentifierSegment, type="quoted_identifier"),
        TypedParser("unicode_double_quote", ansi.LiteralSegment, type="quoted_literal"),
    ),
    PostFunctionGrammar=AnyNumberOf(
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
            OneOf("DEFAULT", Ref("EqualsSegment")),
            Ref("ExpressionSegment"),
            optional=True,
        ),
    ),
    FrameClauseUnitGrammar=OneOf("RANGE", "ROWS", "GROUPS"),
    # Postgres supports the non-standard ISNULL and NONNULL comparison operators. See
    # https://www.postgresql.org/docs/14/functions-comparison.html
    IsNullGrammar=Ref.keyword("ISNULL"),
    NotNullGrammar=Ref.keyword("NOTNULL"),
    JoinKeywordsGrammar=Sequence("JOIN", Sequence("LATERAL", optional=True)),
    SelectClauseElementTerminatorGrammar=OneOf(
        "INTO",
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        Ref("CommaSegment"),
        Ref("SetOperatorSegment"),
    ),
    SelectClauseSegmentGrammar=Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
            # In Postgres you don't need an element so make it optional
            optional=True,
            allow_trailing=True,
        ),
        # NB: The Dedent for the indent above lives in the
        # SelectStatementSegment so that it sits in the right
        # place corresponding to the whitespace.
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("PsqlVariableGrammar"),
        ],
        before=Ref("ArrayLiteralSegment"),
    ),
    SimpleArrayTypeGrammar=Ref.keyword("ARRAY"),
    WhereClauseTerminatorGrammar=OneOf(
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "QUALIFY",
        "WINDOW",
        "OVERLAPS",
        "RETURNING",
        Sequence("ON", "CONFLICT"),
    ),
    OrderByClauseTerminators=OneOf(
        "LIMIT",
        "HAVING",
        "QUALIFY",
        # For window functions
        "WINDOW",
        Ref("FrameClauseUnitGrammar"),
        "SEPARATOR",
        Sequence("WITH", "DATA"),
    ),
    Accessor_Grammar=AnyNumberOf(
        Ref("ArrayAccessorSegment"),
        # Add in semi structured expressions
        Ref("SemiStructuredAccessorSegment"),
    ),
)


# Inherit from the ANSI ObjectReferenceSegment this way so we can inherit
# other segment types from it.
class ObjectReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an object."""

    pass


class OverlapSegment(ansi.CompositeComparisonOperatorSegment):
    """Overlaps range operator."""

    match_grammar = Sequence(
        Ref("AmpersandSegment"), Ref("AmpersandSegment"), allow_gaps=False
    )


class NotExtendRightSegment(ansi.CompositeComparisonOperatorSegment):
    """Not extend right range operator."""

    match_grammar = Sequence(
        Ref("AmpersandSegment"), Ref("RawGreaterThanSegment"), allow_gaps=False
    )


class NotExtendLeftSegment(ansi.CompositeComparisonOperatorSegment):
    """Not extend left range operator."""

    match_grammar = Sequence(
        Ref("AmpersandSegment"), Ref("RawLessThanSegment"), allow_gaps=False
    )


class AdjacentSegment(ansi.CompositeComparisonOperatorSegment):
    """Adjacent range operator."""

    match_grammar = Sequence(
        Ref("MinusSegment"), Ref("PipeSegment"), Ref("MinusSegment"), allow_gaps=False
    )


class PsqlVariableGrammar(BaseSegment):
    """PSQl Variables :thing, :'thing', :"thing"."""

    type = "psql_variable"

    match_grammar = Sequence(
        OptionallyBracketed(
            Ref("ColonSegment"),
            OneOf(
                Ref("ParameterNameSegment"),
                Ref("QuotedLiteralSegment"),
            ),
        )
    )


class ArrayAccessorSegment(ansi.ArrayAccessorSegment):
    """Overwrites Array Accessor in ANSI to allow n many consecutive brackets.

    Postgres can also have array access like python [:2] or [2:] so
    numbers on either side of the slice segment are optional.
    """

    match_grammar = Sequence(
        AnyNumberOf(
            Bracketed(
                Sequence(
                    OneOf(
                        OneOf(
                            Ref("QualifiedNumericLiteralSegment"),
                            Ref("NumericLiteralSegment"),
                        ),
                        Sequence(
                            OneOf(
                                Ref("QualifiedNumericLiteralSegment"),
                                Ref("NumericLiteralSegment"),
                                optional=True,
                            ),
                            Ref("SliceSegment"),
                            OneOf(
                                Ref("QualifiedNumericLiteralSegment"),
                                Ref("NumericLiteralSegment"),
                            ),
                        ),
                        Sequence(
                            OneOf(
                                Ref("QualifiedNumericLiteralSegment"),
                                Ref("NumericLiteralSegment"),
                            ),
                            Ref("SliceSegment"),
                            OneOf(
                                Ref("QualifiedNumericLiteralSegment"),
                                Ref("NumericLiteralSegment"),
                                optional=True,
                            ),
                        ),
                    ),
                ),
                bracket_type="square",
            )
        )
    )


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
        Sequence(
            OneOf("INTERVAL", "TIMETZ", "TIMESTAMPTZ"),
            Bracketed(Ref("NumericLiteralSegment"), optional=True),
        ),
    )


class DateTimeLiteralGrammar(BaseSegment):
    """Literal Date Time."""

    type = "datetime_literal"
    match_grammar = Sequence(
        Ref("DateTimeTypeIdentifier"),
        Ref("QuotedLiteralSegment"),
    )


class DatatypeSegment(ansi.DatatypeSegment):
    """A data type segment.

    Supports timestamp with(out) time zone. Doesn't currently support intervals.
    """

    match_grammar = Sequence(
        # Some dialects allow optional qualification of data types with schemas
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            allow_gaps=False,
            optional=True,
        ),
        OneOf(
            Ref("WellKnownTextGeometrySegment"),
            Ref("DateTimeTypeIdentifier"),
            Sequence(
                OneOf(
                    # numeric types
                    "SMALLINT",
                    "INTEGER",
                    "INT",
                    "INT2",
                    "INT4",
                    "INT8",
                    "BIGINT",
                    "FLOAT4",
                    "FLOAT8",
                    "REAL",
                    Sequence("DOUBLE", "PRECISION"),
                    "SMALLSERIAL",
                    "SERIAL",
                    "SERIAL2",
                    "SERIAL4",
                    "SERIAL8",
                    "BIGSERIAL",
                    # numeric types [(precision)]
                    Sequence(
                        OneOf("FLOAT"),
                        Bracketed(Ref("NumericLiteralSegment"), optional=True),
                    ),
                    # numeric types [precision ["," scale])]
                    Sequence(
                        OneOf("DECIMAL", "NUMERIC"),
                        Bracketed(
                            Delimited(Ref("NumericLiteralSegment")),
                            optional=True,
                        ),
                    ),
                    # monetary type
                    "MONEY",
                    # character types
                    OneOf(
                        Sequence(
                            OneOf(
                                "CHAR",
                                "CHARACTER",
                                Sequence("CHARACTER", "VARYING"),
                                "VARCHAR",
                            ),
                            Bracketed(Ref("NumericLiteralSegment"), optional=True),
                        ),
                        "TEXT",
                    ),
                    # binary type
                    "BYTEA",
                    # boolean types
                    OneOf("BOOLEAN", "BOOL"),
                    # geometric types
                    OneOf("POINT", "LINE", "LSEG", "BOX", "PATH", "POLYGON", "CIRCLE"),
                    # network address types
                    OneOf("CIDR", "INET", "MACADDR", "MACADDR8"),
                    # text search types
                    OneOf("TSVECTOR", "TSQUERY"),
                    # bit string types
                    Sequence(
                        "BIT",
                        OneOf("VARYING", optional=True),
                        Bracketed(
                            Ref("NumericLiteralSegment"),
                            optional=True,
                        ),
                    ),
                    # uuid type
                    "UUID",
                    # xml type
                    "XML",
                    # json types
                    OneOf("JSON", "JSONB"),
                    # range types
                    "INT4RANGE",
                    "INT8RANGE",
                    "NUMRANGE",
                    "TSRANGE",
                    "TSTZRANGE",
                    "DATERANGE",
                    # pg_lsn type
                    "PG_LSN",
                ),
            ),
            # user defined data types
            Ref("DatatypeIdentifierSegment"),
        ),
        # array types
        OneOf(
            AnyNumberOf(
                Bracketed(
                    Ref("ExpressionSegment", optional=True), bracket_type="square"
                )
            ),
            Ref("SimpleArrayTypeGrammar"),
            Sequence(Ref("SimpleArrayTypeGrammar"), Ref("ArrayLiteralSegment")),
            optional=True,
        ),
    )


class CreateFunctionStatementSegment(ansi.CreateFunctionStatementSegment):
    """A `CREATE FUNCTION` statement.

    This version in the ANSI dialect should be a "common subset" of the
    structure of the code for those dialects.
    postgres: https://www.postgresql.org/docs/13/sql-createfunction.html
    """

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        Ref("TemporaryGrammar", optional=True),
        "FUNCTION",
        Ref("IfNotExistsGrammar", optional=True),
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
                                    Ref("ColumnReferenceSegment"),
                                    Ref("DatatypeSegment"),
                                ),
                            ),
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
        Ref("DropBehaviorGrammar", optional=True),
    )


class AlterFunctionStatementSegment(BaseSegment):
    """A `ALTER FUNCTION` statement.

    As per the specification: https://www.postgresql.org/docs/14/sql-alterfunction.html
    """

    type = "alter_function_statement"

    match_grammar = Sequence(
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
                Ref("ExtensionReferenceSegment"),
            ),
        ),
    )


class AlterFunctionActionSegment(BaseSegment):
    """Alter Function Action Segment.

    https://www.postgresql.org/docs/14/sql-alterfunction.html
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


class AlterProcedureActionSegment(BaseSegment):
    """Alter Procedure Action Segment.

    https://www.postgresql.org/docs/14/sql-alterprocedure.html
    """

    type = "alter_procedure_action_segment"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                Ref.keyword("EXTERNAL", optional=True),
                "SECURITY",
                OneOf("DEFINER", "INVOKER"),
            ),
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


class AlterProcedureStatementSegment(BaseSegment):
    """An `ALTER PROCEDURE` statement.

    https://www.postgresql.org/docs/14/sql-alterprocedure.html
    """

    type = "alter_procedure_statement"

    match_grammar = Sequence(
        "ALTER",
        "PROCEDURE",
        Delimited(
            Sequence(
                Ref("FunctionNameSegment"),
                Ref("FunctionParameterListGrammar", optional=True),
            )
        ),
        OneOf(
            Ref("AlterProcedureActionSegment", optional=True),
            Sequence("RENAME", "TO", Ref("FunctionNameSegment")),
            Sequence("SET", "SCHEMA", Ref("SchemaReferenceSegment")),
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
                        ),
                    ),
                    Sequence("FROM", "CURRENT"),
                ),
            ),
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
                Ref("ExtensionReferenceSegment"),
            ),
        ),
    )


class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE PROCEDURE` statement.

    https://www.postgresql.org/docs/14/sql-createprocedure.html

    TODO: Just a basic statement for now, without full syntax.
    based on CreateFunctionStatementSegment without a return type.
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        "PROCEDURE",
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar"),
        Ref("FunctionDefinitionGrammar"),
    )


class DropProcedureStatementSegment(BaseSegment):
    """A `DROP PROCEDURE` statement.

    https://www.postgresql.org/docs/11/sql-dropprocedure.html
    """

    type = "drop_procedure_statement"

    match_grammar = Sequence(
        "DROP",
        "PROCEDURE",
        Ref("IfExistsGrammar", optional=True),
        Delimited(
            Sequence(
                Ref("FunctionNameSegment"),
                Ref("FunctionParameterListGrammar", optional=True),
            ),
        ),
        OneOf(
            "CASCADE",
            "RESTRICT",
            optional=True,
        ),
    )


class WellKnownTextGeometrySegment(BaseSegment):
    """A Data Type Segment to identify Well Known Text Geometric Data Types.

    As specified in https://postgis.net/stuff/postgis-3.1.pdf

    This approach is to maximise 'accepted code' for the parser, rather than be overly
    restrictive.
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


class FunctionDefinitionGrammar(ansi.FunctionDefinitionGrammar):
    """This is the body of a `CREATE FUNCTION AS` statement.

    https://www.postgresql.org/docs/13/sql-createfunction.html
    """

    match_grammar = Sequence(
        AnyNumberOf(
            Ref("LanguageClauseSegment"),
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
                        ),
                    ),
                    Sequence("FROM", "CURRENT"),
                ),
            ),
            Sequence(
                "AS",
                OneOf(
                    Ref("QuotedLiteralSegment"),
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
            Bracketed(Delimited(Ref("ParameterNameSegment"))),
            optional=True,
        ),
    )


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


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """Overrides ANSI Statement, to allow for SELECT INTO statements."""

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy()
    match_grammar.terminator = match_grammar.terminator.copy(  # type: ignore
        insert=[
            Sequence("ON", "CONFLICT"),
        ],
    )
    parse_grammar = ansi.UnorderedSelectStatementSegment.parse_grammar.copy(
        insert=[
            Ref("IntoClauseSegment", optional=True),
        ],
        before=Ref("FromClauseSegment", optional=True),
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """Overrides ANSI as the parse grammar copy needs to be reapplied."""

    match_grammar = ansi.SelectStatementSegment.match_grammar.copy()
    match_grammar.terminator = match_grammar.terminator.copy(  # type: ignore
        insert=[
            Sequence("ON", "CONFLICT"),
        ],
    )
    parse_grammar = UnorderedSelectStatementSegment.parse_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ]
    )


class SelectClauseSegment(ansi.SelectClauseSegment):
    """Overrides ANSI to allow INTO as a terminator."""

    match_grammar = StartsWith(
        "SELECT",
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
    parse_grammar = ansi.SelectClauseSegment.parse_grammar


class SelectClauseModifierSegment(ansi.SelectClauseModifierSegment):
    """Things that come after SELECT but before the columns."""

    match_grammar = OneOf(
        Sequence(
            "DISTINCT",
            Sequence(
                "ON",
                Bracketed(Delimited(Ref("ExpressionSegment"))),
                optional=True,
            ),
        ),
        "ALL",
    )


class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions.

    https://www.postgresql.org/docs/current/functions-aggregate.html.
    """

    type = "withingroup_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Ref("OrderByClauseSegment", optional=True)),
    )


class CubeRollupClauseSegment(BaseSegment):
    """`CUBE` / `ROLLUP` clause within the `GROUP BY` clause.

    https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS
    """

    type = "cube_rollup_clause"
    match_grammar = StartsWith(
        OneOf("CUBE", "ROLLUP"),
        terminator=OneOf(
            "HAVING",
            "QUALIFY",
            Sequence("ORDER", "BY"),
            "LIMIT",
            "WINDOW",
            Ref("SetOperatorSegment"),
        ),
    )
    parse_grammar = Sequence(
        OneOf("CUBE", "ROLLUP"),
        Bracketed(
            Ref("GroupingExpressionList"),
        ),
    )


class GroupingSetsClauseSegment(BaseSegment):
    """`GROUPING SETS` clause within the `GROUP BY` clause.

    https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS
    """

    type = "grouping_sets_clause"
    match_grammar = StartsWith(
        Sequence("GROUPING", "SETS"),
        terminator=OneOf(
            "HAVING",
            "QUALIFY",
            Sequence("ORDER", "BY"),
            "LIMIT",
            "WINDOW",
            Ref("SetOperatorSegment"),
        ),
    )
    parse_grammar = Sequence(
        "GROUPING",
        "SETS",
        Bracketed(
            Delimited(
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingExpressionList"),
            )
        ),
    )


class GroupingExpressionList(BaseSegment):
    """Grouping expression list within `CUBE` / `ROLLUP` `GROUPING SETS`."""

    type = "grouping_expression_list"
    match_grammar = Delimited(
        OneOf(
            Bracketed(Delimited(Ref("ExpressionSegment"))),
            Ref("ExpressionSegment"),
            Bracketed(),  # Allows empty parentheses
        )
    )


class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    type = "groupby_clause"
    match_grammar = StartsWith(
        Sequence("GROUP", "BY"),
        terminator=OneOf(
            Sequence("ORDER", "BY"),
            "LIMIT",
            "HAVING",
            "QUALIFY",
            "WINDOW",
            Ref("SetOperatorSegment"),
        ),
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
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingSetsClauseSegment"),
                Bracketed(),  # Allows empty parentheses
            ),
            terminator=OneOf(
                Sequence("ORDER", "BY"),
                "LIMIT",
                "HAVING",
                "QUALIFY",
                "WINDOW",
                Ref("SetOperatorSegment"),
            ),
        ),
        Dedent,
    )


class CreateRoleStatementSegment(ansi.CreateRoleStatementSegment):
    """A `CREATE ROLE` statement.

    As per:
    https://www.postgresql.org/docs/current/sql-createrole.html
    """

    type = "create_role_statement"

    match_grammar = Sequence(
        "CREATE",
        OneOf("ROLE", "USER"),
        Ref("RoleReferenceSegment"),
        Sequence(
            Ref.keyword("WITH", optional=True),
            AnySetOf(
                OneOf("SUPERUSER", "NOSUPERUSER"),
                OneOf("CREATEDB", "NOCREATEDB"),
                OneOf("CREATEROLE", "NOCREATEROLE"),
                OneOf("INHERIT", "NOINHERIT"),
                OneOf("LOGIN", "NOLOGIN"),
                OneOf("REPLICATION", "NOREPLICATION"),
                OneOf("BYPASSRLS", "NOBYPASSRLS"),
                Sequence("CONNECTION", "LIMIT", Ref("NumericLiteralSegment")),
                Sequence("PASSWORD", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
                Sequence("VALID", "UNTIL", Ref("QuotedLiteralSegment")),
                Sequence("IN", "ROLE", Ref("RoleReferenceSegment")),
                Sequence("IN", "GROUP", Ref("RoleReferenceSegment")),
                Sequence("ROLE", Ref("RoleReferenceSegment")),
                Sequence("ADMIN", Ref("RoleReferenceSegment")),
                Sequence("USER", Ref("RoleReferenceSegment")),
                Sequence("SYSID", Ref("NumericLiteralSegment")),
            ),
            optional=True,
        ),
    )


class AlterRoleStatementSegment(BaseSegment):
    """An `ALTER ROLE` statement.

    As per:
    https://www.postgresql.org/docs/current/sql-alterrole.html
    """

    type = "alter_role_statement"

    match_grammar = Sequence(
        "ALTER",
        OneOf("ROLE", "USER"),
        OneOf(Ref("RoleReferenceSegment"), "ALL"),
        OneOf(
            Sequence(
                Ref.keyword("WITH", optional=True),
                AnySetOf(
                    OneOf("SUPERUSER", "NOSUPERUSER"),
                    OneOf("CREATEDB", "NOCREATEDB"),
                    OneOf("CREATEROLE", "NOCREATEROLE"),
                    OneOf("INHERIT", "NOINHERIT"),
                    OneOf("LOGIN", "NOLOGIN"),
                    OneOf("REPLICATION", "NOREPLICATION"),
                    OneOf("BYPASSRLS", "NOBYPASSRLS"),
                    Sequence("CONNECTION", "LIMIT", Ref("NumericLiteralSegment")),
                    Sequence("PASSWORD", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
                    Sequence("VALID", "UNTIL", Ref("QuotedLiteralSegment")),
                ),
                optional=True,
            ),
            Sequence("RENAME", "TO", Ref("RoleReferenceSegment"), optional=True),
            Sequence(
                Sequence(
                    "IN",
                    "DATABASE",
                    Ref("ObjectReferenceSegment"),
                    optional=True,
                ),
                OneOf(
                    Sequence(
                        "SET",
                        Ref("ObjectReferenceSegment"),
                        OneOf(
                            Sequence(
                                OneOf("TO", Ref("EqualsSegment")),
                                OneOf(
                                    Ref("QuotedLiteralSegment"),
                                    "DEFAULT",
                                    "ON",
                                    "OFF",
                                ),
                            ),
                            Sequence(
                                "FROM",
                                "CURRENT",
                            ),
                        ),
                    ),
                    Sequence("RESET", OneOf(Ref("QuotedLiteralSegment"), "ALL")),
                ),
                optional=True,
            ),
        ),
    )


class ExplainStatementSegment(ansi.ExplainStatementSegment):
    """An `Explain` statement.

    EXPLAIN [ ( option [, ...] ) ] statement
    EXPLAIN [ ANALYZE ] [ VERBOSE ] statement

    https://www.postgresql.org/docs/14/sql-explain.html
    """

    match_grammar = Sequence(
        "EXPLAIN",
        OneOf(
            Sequence(
                OneOf(
                    "ANALYZE",
                    "ANALYSE",
                    optional=True,
                ),
                Ref.keyword("VERBOSE", optional=True),
            ),
            Bracketed(Delimited(Ref("ExplainOptionSegment"))),
            optional=True,
        ),
        ansi.ExplainStatementSegment.explainable_stmt,
    )


class ExplainOptionSegment(BaseSegment):
    """An `Explain` statement option.

    ANALYZE [ boolean ]
    VERBOSE [ boolean ]
    COSTS [ boolean ]
    SETTINGS [ boolean ]
    BUFFERS [ boolean ]
    WAL [ boolean ]
    TIMING [ boolean ]
    SUMMARY [ boolean ]
    FORMAT { TEXT | XML | JSON | YAML }

    https://www.postgresql.org/docs/14/sql-explain.html
    """

    type = "explain_option"

    match_grammar = OneOf(
        Sequence(
            OneOf(
                "ANALYZE",
                "ANALYSE",
                "VERBOSE",
                "COSTS",
                "SETTINGS",
                "BUFFERS",
                "WAL",
                "TIMING",
                "SUMMARY",
            ),
            Ref("BooleanLiteralGrammar", optional=True),
        ),
        Sequence(
            "FORMAT",
            OneOf("TEXT", "XML", "JSON", "YAML"),
        ),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """A `CREATE TABLE` statement.

    As specified in https://www.postgresql.org/docs/13/sql-createtable.html
    """

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
                                AnyNumberOf(
                                    # A single COLLATE segment can come before or after
                                    # constraint segments
                                    OneOf(
                                        Ref("ColumnConstraintSegment"),
                                        Sequence(
                                            "COLLATE",
                                            Ref("ObjectReferenceSegment"),
                                        ),
                                    ),
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
                    Bracketed(Delimited(Ref("TableReferenceSegment"))),
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
            Sequence("TABLESPACE", Ref("TablespaceReferenceSegment")),
        ),
    )


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
            Sequence("TABLESPACE", Ref("TablespaceReferenceSegment"), optional=True),
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


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """An `ALTER TABLE` statement.

    Matches the definition in https://www.postgresql.org/docs/13/sql-altertable.html
    """

    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        OneOf(
            Sequence(
                Ref("IfExistsGrammar", optional=True),
                Ref.keyword("ONLY", optional=True),
                Ref("TableReferenceSegment"),
                Ref("StarSegment", optional=True),
                OneOf(
                    Delimited(Ref("AlterTableActionSegment")),
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
                Ref("IfExistsGrammar", optional=True),
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
                Ref("TablespaceReferenceSegment"),
                Sequence(
                    "OWNED",
                    "BY",
                    Delimited(Ref("ObjectReferenceSegment")),
                    optional=True,
                ),
                "SET",
                "TABLESPACE",
                Ref("TablespaceReferenceSegment"),
                Ref.keyword("NOWAIT", optional=True),
            ),
        ),
    )


class AlterTableActionSegment(BaseSegment):
    """Alter Table Action Segment.

    https://www.postgresql.org/docs/13/sql-altertable.html
    """

    type = "alter_table_action_segment"

    match_grammar = OneOf(
        Sequence(
            "ADD",
            Ref.keyword("COLUMN", optional=True),
            Ref("IfNotExistsGrammar", optional=True),
            Ref("ColumnReferenceSegment"),
            Ref("DatatypeSegment"),
            Sequence("COLLATE", Ref("QuotedLiteralSegment"), optional=True),
            AnyNumberOf(Ref("ColumnConstraintSegment")),
        ),
        Sequence(
            "DROP",
            Ref.keyword("COLUMN", optional=True),
            Ref("IfExistsGrammar", optional=True),
            Ref("ColumnReferenceSegment"),
            Ref("DropBehaviorGrammar", optional=True),
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
                Sequence("DROP", "EXPRESSION", Ref("IfExistsGrammar", optional=True)),
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
                Sequence(
                    "DROP",
                    "IDENTITY",
                    Ref("IfExistsGrammar", optional=True),
                ),
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
            Ref("IfExistsGrammar", optional=True),
            Ref("ParameterNameSegment"),
            Ref("DropBehaviorGrammar", optional=True),
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
        Sequence("SET", "TABLESPACE", Ref("TablespaceReferenceSegment")),
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
                )
            ),
        ),
        Sequence(
            "RESET",
            Bracketed(Delimited(Ref("ParameterNameSegment"))),
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
                Ref("ParameterNameSegment"),
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
                Sequence("USING", "INDEX", Ref("IndexReferenceSegment")),
                "FULL",
                "NOTHING",
            ),
        ),
    )


class CreateExtensionStatementSegment(BaseSegment):
    """A `CREATE EXTENSION` statement.

    https://www.postgresql.org/docs/9.1/sql-createextension.html
    """

    type = "create_extension_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "EXTENSION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ExtensionReferenceSegment"),
        Ref.keyword("WITH", optional=True),
        Sequence("SCHEMA", Ref("SchemaReferenceSegment"), optional=True),
        Sequence("VERSION", Ref("VersionIdentifierSegment"), optional=True),
        Sequence("FROM", Ref("VersionIdentifierSegment"), optional=True),
    )


class DropExtensionStatementSegment(BaseSegment):
    """A `DROP EXTENSION` statement.

    https://www.postgresql.org/docs/14/sql-dropextension.html
    """

    type = "drop_extension_statement"
    match_grammar: Matchable = Sequence(
        "DROP",
        "EXTENSION",
        Ref("IfExistsGrammar", optional=True),
        Ref("ExtensionReferenceSegment"),
        Ref("CascadeRestrictGrammar", optional=True),
    )


class CreateMaterializedViewStatementSegment(BaseSegment):
    """A `CREATE MATERIALIZED VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-creatematerializedview.html
    """

    type = "create_materialized_view_statement"

    match_grammar = Sequence(
        "CREATE",
        "MATERIALIZED",
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        AnyNumberOf(
            Sequence("USING", Ref("ParameterNameSegment"), optional=True),
            Sequence("TABLESPACE", Ref("TablespaceReferenceSegment"), optional=True),
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


class AlterMaterializedViewStatementSegment(BaseSegment):
    """A `ALTER MATERIALIZED VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-altermaterializedview.html
    """

    type = "alter_materialized_view_statement"

    match_grammar = Sequence(
        "ALTER",
        "MATERIALIZED",
        "VIEW",
        OneOf(
            Sequence(
                Ref("IfExistsGrammar", optional=True),
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
                Ref("ExtensionReferenceSegment"),
            ),
            Sequence(
                "ALL",
                "IN",
                "TABLESPACE",
                Ref("TablespaceReferenceSegment"),
                Sequence(
                    "OWNED",
                    "BY",
                    Delimited(Ref("ObjectReferenceSegment")),
                    optional=True,
                ),
                "SET",
                "TABLESPACE",
                Ref("TablespaceReferenceSegment"),
                Sequence("NOWAIT", optional=True),
            ),
        ),
    )


class AlterMaterializedViewActionSegment(BaseSegment):
    """Alter Materialized View Action Segment.

    https://www.postgresql.org/docs/14/sql-altermaterializedview.html
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


class RefreshMaterializedViewStatementSegment(BaseSegment):
    """A `REFRESH MATERIALIZED VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-refreshmaterializedview.html
    """

    type = "refresh_materialized_view_statement"

    match_grammar = Sequence(
        "REFRESH",
        "MATERIALIZED",
        "VIEW",
        Ref.keyword("CONCURRENTLY", optional=True),
        Ref("TableReferenceSegment"),
        Ref("WithDataClauseSegment", optional=True),
    )


class DropMaterializedViewStatementSegment(BaseSegment):
    """A `DROP MATERIALIZED VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-dropmaterializedview.html
    """

    type = "drop_materialized_view_statement"

    match_grammar = Sequence(
        "DROP",
        "MATERIALIZED",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("TableReferenceSegment")),
        Ref("DropBehaviorGrammar", optional=True),
    )


class AlterViewStatementSegment(BaseSegment):
    """An `ALTER VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-alterview.html
    """

    type = "alter_view_statement"

    match_grammar = Sequence(
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


class CreateDatabaseStatementSegment(ansi.CreateDatabaseStatementSegment):
    """A `CREATE DATABASE` statement.

    As specified in https://www.postgresql.org/docs/14/sql-createdatabase.html
    """

    match_grammar = Sequence(
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
                OneOf(Ref("TablespaceReferenceSegment"), "DEFAULT"),
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


class AlterDatabaseStatementSegment(BaseSegment):
    """A `ALTER DATABASE` statement.

    As specified in https://www.postgresql.org/docs/14/sql-alterdatabase.html
    """

    type = "alter_database_statement"

    match_grammar = Sequence(
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
            Sequence("SET", "TABLESPACE", Ref("TablespaceReferenceSegment")),
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


class DropDatabaseStatementSegment(ansi.DropDatabaseStatementSegment):
    """A `DROP DATABASE` statement.

    As specified in https://www.postgresql.org/docs/14/sql-dropdatabase.html
    """

    match_grammar = Sequence(
        "DROP",
        "DATABASE",
        Ref("IfExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        Sequence(
            Ref.keyword("WITH", optional=True),
            Bracketed("FORCE"),
            optional=True,
        ),
    )


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


class ColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """A column option; each CREATE TABLE column can have 0 or more.

    https://www.postgresql.org/docs/13/sql-altertable.html
    """

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
            Ref("ReferenceDefinitionGrammar"),  # REFERENCES reftable [ ( refcolumn) ]
        ),
        OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
        OneOf(
            Sequence("INITIALLY", "DEFERRED"),
            Sequence("INITIALLY", "IMMEDIATE"),
            optional=True,
        ),
    )


class PartitionBoundSpecSegment(BaseSegment):
    """Partition bound spec.

    As per https://www.postgresql.org/docs/13/sql-altertable.html.
    """

    type = "partition_bound_spec"
    match_grammar = OneOf(
        Sequence(
            "IN",
            Bracketed(Delimited(Ref("ExpressionSegment"))),
        ),
        Sequence(
            "FROM",
            Bracketed(
                Delimited(
                    OneOf(Ref("ExpressionSegment"), "MINVALUE", "MAXVALUE"),
                )
            ),
            "TO",
            Bracketed(
                Delimited(
                    OneOf(Ref("ExpressionSegment"), "MINVALUE", "MAXVALUE"),
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


class TableConstraintSegment(ansi.TableConstraintSegment):
    """A table constraint, e.g. for CREATE TABLE.

    As specified in https://www.postgresql.org/docs/13/sql-altertable.html
    """

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
                Ref(
                    "ReferenceDefinitionGrammar"
                ),  # REFERENCES reftable [ ( refcolumn) ]
            ),
            OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
            OneOf(
                Sequence("INITIALLY", "DEFERRED"),
                Sequence("INITIALLY", "IMMEDIATE"),
                optional=True,
            ),
        ),
    )


class TableConstraintUsingIndexSegment(BaseSegment):
    """table_constraint_using_index.

    As specified in: https://www.postgresql.org/docs/13/sql-altertable.html.
    """

    type = "table_constraint"
    match_grammar = Sequence(
        Sequence(  # [ CONSTRAINT <Constraint name> ]
            "CONSTRAINT", Ref("ObjectReferenceSegment"), optional=True
        ),
        Sequence(
            OneOf("UNIQUE", Ref("PrimaryKeyGrammar")),
            "USING",
            "INDEX",
            Ref("IndexReferenceSegment"),
        ),
        OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
        OneOf(
            Sequence("INITIALLY", "DEFERRED"),
            Sequence("INITIALLY", "IMMEDIATE"),
            optional=True,
        ),
    )


class IndexParametersSegment(BaseSegment):
    """index_parameters.

    As specified in https://www.postgresql.org/docs/13/sql-altertable.html.
    """

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
                )
            ),
            optional=True,
        ),
        Sequence(
            "USING",
            "INDEX",
            "TABLESPACE",
            Ref("TablespaceReferenceSegment"),
            optional=True,
        ),
    )


class ReferentialActionSegment(BaseSegment):
    """Foreign Key constraints.

    https://www.postgresql.org/docs/13/infoschema-referential-constraints.html
    """

    type = "referential_action"

    match_grammar = OneOf(
        "CASCADE",
        Sequence("SET", "NULL"),
        Sequence("SET", "DEFAULT"),
        "RESTRICT",
        Sequence("NO", "ACTION"),
    )


class ExcludeElementSegment(BaseSegment):
    """Exclude element segment.

    As found in https://www.postgresql.org/docs/13/sql-altertable.html.
    """

    match_grammar = Sequence(
        OneOf(Ref("ColumnReferenceSegment"), Bracketed(Ref("ExpressionSegment"))),
        Ref("ParameterNameSegment", optional=True),
        OneOf("ASC", "DESC", optional=True),
        Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
    )


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


class AlterDefaultPrivilegesToFromRolesSegment(BaseSegment):
    """The segment after `TO` / `FROM`  in `ALTER DEFAULT PRIVILEGES`.

    `{ [ GROUP ] role_name | PUBLIC } [, ...]`

    https://www.postgresql.org/docs/13/sql-alterdefaultprivileges.html
    """

    type = "alter_default_privileges_to_from_roles"
    match_grammar = OneOf(
        Sequence(
            Ref.keyword("GROUP", optional=True),
            Ref("RoleReferenceSegment"),
        ),
        "PUBLIC",
    )


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
        Ref("DropBehaviorGrammar", optional=True),
    )


class CommentOnStatementSegment(BaseSegment):
    """`COMMENT ON` statement.

    https://www.postgresql.org/docs/13/sql-comment.html
    """

    type = "comment_clause"

    match_grammar = Sequence(
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
                    Sequence(Ref("FunctionParameterListGrammar"), optional=True),
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
                            optional=True,
                        ),
                        optional=True,
                    ),
                ),
            ),
            Sequence("IS", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
        ),
    )


class CreateIndexStatementSegment(ansi.CreateIndexStatementSegment):
    """A `CREATE INDEX` statement.

    As specified in https://www.postgresql.org/docs/13/sql-createindex.html
    """

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
                                    ),
                                ),
                            ),
                            OneOf("ASC", "DESC"),
                            OneOf(
                                Sequence("NULLS", "FIRST"), Sequence("NULLS", "LAST")
                            ),
                        ),
                    ),
                )
            ),
        ),
        AnyNumberOf(
            Sequence(
                "INCLUDE",
                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
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
                    )
                ),
            ),
            Sequence("TABLESPACE", Ref("TableReferenceSegment")),
            Sequence("WHERE", Ref("ExpressionSegment")),
        ),
    )


class AlterIndexStatementSegment(BaseSegment):
    """An ALTER INDEX segment.

    As per https://www.postgresql.org/docs/14/sql-alterindex.html
    """

    type = "alter_index_statement"

    match_grammar = Sequence(
        "ALTER",
        "INDEX",
        OneOf(
            Sequence(
                Ref("IfExistsGrammar", optional=True),
                Ref("IndexReferenceSegment"),
                OneOf(
                    Sequence("RENAME", "TO", Ref("IndexReferenceSegment")),
                    Sequence("SET", "TABLESPACE", Ref("TablespaceReferenceSegment")),
                    Sequence("ATTACH", "PARTITION", Ref("IndexReferenceSegment")),
                    Sequence(
                        Ref.keyword("NO", optional=True),
                        "DEPENDS",
                        "ON",
                        "EXTENSION",
                        Ref("ExtensionReferenceSegment"),
                    ),
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
                        "RESET", Bracketed(Delimited(Ref("ParameterNameSegment")))
                    ),
                    Sequence(
                        "ALTER",
                        Ref.keyword("COLUMN", optional=True),
                        Ref("NumericLiteralSegment"),
                        "SET",
                        "STATISTICS",
                        Ref("NumericLiteralSegment"),
                    ),
                ),
            ),
            Sequence(
                "ALL",
                "IN",
                "TABLESPACE",
                Ref("TablespaceReferenceSegment"),
                Sequence(
                    "OWNED", "BY", Delimited(Ref("RoleReferenceSegment")), optional=True
                ),
                "SET",
                "TABLESPACE",
                Ref("TablespaceReferenceSegment"),
                Ref.keyword("NOWAIT", optional=True),
            ),
        ),
    )


class ReindexStatementSegment(BaseSegment):
    """A Reindex Statement Segment.

    As per https://www.postgresql.org/docs/14/sql-reindex.html
    """

    type = "reindex_statement_segment"

    match_grammar = Sequence(
        "REINDEX",
        Bracketed(
            Delimited(
                Sequence("CONCURRENTLY", Ref("BooleanLiteralGrammar", optional=True)),
                Sequence(
                    "TABLESPACE",
                    Ref("TablespaceReferenceSegment"),
                ),
                Sequence("VERBOSE", Ref("BooleanLiteralGrammar", optional=True)),
            ),
            optional=True,
        ),
        OneOf(
            Sequence(
                "INDEX",
                Ref.keyword("CONCURRENTLY", optional=True),
                Ref("IndexReferenceSegment"),
            ),
            Sequence(
                "TABLE",
                Ref.keyword("CONCURRENTLY", optional=True),
                Ref("TableReferenceSegment"),
            ),
            Sequence(
                "SCHEMA",
                Ref.keyword("CONCURRENTLY", optional=True),
                Ref("SchemaReferenceSegment"),
            ),
            Sequence(
                OneOf("DATABASE", "SYSTEM"),
                Ref.keyword("CONCURRENTLY", optional=True),
                Ref("DatabaseReferenceSegment"),
            ),
        ),
    )


class FrameClauseSegment(ansi.FrameClauseSegment):
    """A frame clause for window functions.

    As specified in https://www.postgresql.org/docs/13/sql-expressions.html
    """

    _frame_extent = ansi.FrameClauseSegment._frame_extent

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


class CreateSequenceOptionsSegment(ansi.CreateSequenceOptionsSegment):
    """Options for Create Sequence statement.

    As specified in https://www.postgresql.org/docs/13/sql-createsequence.html
    """

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


class AlterSequenceOptionsSegment(ansi.AlterSequenceOptionsSegment):
    """Dialect-specific options for ALTER SEQUENCE statement.

    As specified in https://www.postgresql.org/docs/13/sql-altersequence.html
    """

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


class AlterSequenceStatementSegment(ansi.AlterSequenceStatementSegment):
    """Alter Sequence Statement.

    As specified in https://www.postgresql.org/docs/13/sql-altersequence.html
    """

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


class DropSequenceStatementSegment(ansi.DropSequenceStatementSegment):
    """Drop Sequence Statement.

    As specified in https://www.postgresql.org/docs/13/sql-dropsequence.html
    """

    match_grammar = Sequence(
        "DROP",
        "SEQUENCE",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("SequenceReferenceSegment")),
        Ref("DropBehaviorGrammar", optional=True),
    )


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
class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments."""

    match_grammar = ansi.StatementSegment.match_grammar
    parse_grammar = ansi.StatementSegment.parse_grammar.copy(
        insert=[
            Ref("AlterDefaultPrivilegesStatementSegment"),
            Ref("CommentOnStatementSegment"),
            Ref("AnalyzeStatementSegment"),
            Ref("CreateTableAsStatementSegment"),
            Ref("AlterTriggerStatementSegment"),
            Ref("SetStatementSegment"),
            Ref("CreatePolicyStatementSegment"),
            Ref("DropPolicyStatementSegment"),
            Ref("CreateDomainStatementSegment"),
            Ref("AlterDomainStatementSegment"),
            Ref("DropDomainStatementSegment"),
            Ref("CreateMaterializedViewStatementSegment"),
            Ref("AlterMaterializedViewStatementSegment"),
            Ref("DropMaterializedViewStatementSegment"),
            Ref("RefreshMaterializedViewStatementSegment"),
            Ref("AlterDatabaseStatementSegment"),
            Ref("DropDatabaseStatementSegment"),
            Ref("AlterFunctionStatementSegment"),
            Ref("AlterViewStatementSegment"),
            Ref("ListenStatementSegment"),
            Ref("NotifyStatementSegment"),
            Ref("UnlistenStatementSegment"),
            Ref("LoadStatementSegment"),
            Ref("ResetStatementSegment"),
            Ref("DiscardStatementSegment"),
            Ref("AlterProcedureStatementSegment"),
            Ref("CreateProcedureStatementSegment"),
            Ref("DropProcedureStatementSegment"),
            Ref("CopyStatementSegment"),
            Ref("DoStatementSegment"),
            Ref("AlterIndexStatementSegment"),
            Ref("ReindexStatementSegment"),
            Ref("AlterRoleStatementSegment"),
            Ref("CreateExtensionStatementSegment"),
            Ref("DropExtensionStatementSegment"),
            Ref("CreateTypeStatementSegment"),
            Ref("AlterTypeStatementSegment"),
            Ref("AlterSchemaStatementSegment"),
            Ref("LockTableStatementSegment"),
            Ref("CreateCollationStatementSegment"),
            Ref("CallStoredProcedureSegment"),
        ],
    )


class CreateTriggerStatementSegment(ansi.CreateTriggerStatementSegment):
    """Create Trigger Statement.

    As Specified in https://www.postgresql.org/docs/14/sql-createtrigger.html
    """

    match_grammar = Sequence(
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
            Ref("FunctionSegment"),
        ),
    )


class AlterTriggerStatementSegment(BaseSegment):
    """Alter Trigger Statement.

    As Specified in https://www.postgresql.org/docs/14/sql-altertrigger.html
    """

    type = "alter_trigger"

    match_grammar = Sequence(
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
                Ref("ExtensionReferenceSegment"),
            ),
        ),
    )


class DropTriggerStatementSegment(ansi.DropTriggerStatementSegment):
    """Drop Trigger Statement.

    As Specified in https://www.postgresql.org/docs/14/sql-droptrigger.html
    """

    match_grammar = Sequence(
        "DROP",
        "TRIGGER",
        Ref("IfExistsGrammar", optional=True),
        Ref("TriggerReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class AliasExpressionSegment(ansi.AliasExpressionSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    """

    match_grammar = Sequence(
        Ref.keyword("AS", optional=True),
        OneOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                Bracketed(Ref("SingleIdentifierListSegment"), optional=True),
            ),
            Sequence(
                Ref("SingleIdentifierGrammar", optional=True),
                Bracketed(
                    Delimited(
                        Sequence(Ref("ParameterNameSegment"), Ref("DatatypeSegment"))
                    )
                ),
            ),
        ),
    )


class AsAliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    This is used in `InsertStatementSegment` in Postgres
    since the `AS` is not optional in this context.

    N.B. We keep as a separate segment since the `alias_expression`
    type is required for rules to interpret the alias.
    """

    type = "alias_expression"
    match_grammar = Sequence(
        "AS",
        Ref("SingleIdentifierGrammar"),
    )


class OperationClassReferenceSegment(ObjectReferenceSegment):
    """A reference to an operation class."""

    type = "operation_class_reference"


class ConflictActionSegment(BaseSegment):
    """A Conflict Action Statement used within an INSERT statement.

    As specified in https://www.postgresql.org/docs/14/sql-insert.html
    """

    type = "conflict_action"

    match_grammar = Sequence(
        "DO",
        OneOf(
            "NOTHING",
            Sequence(
                "UPDATE",
                "SET",
                Delimited(
                    OneOf(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            Ref("EqualsSegment"),
                            OneOf(Ref("ExpressionSegment"), "DEFAULT"),
                        ),
                        Sequence(
                            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                            Ref("EqualsSegment"),
                            Ref.keyword("ROW", optional=True),
                            Bracketed(
                                Delimited(OneOf(Ref("ExpressionSegment"), "DEFAULT"))
                            ),
                        ),
                        Sequence(
                            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                            Ref("EqualsSegment"),
                            Bracketed(Ref("SelectableGrammar")),
                        ),
                    )
                ),
                Sequence("WHERE", Ref("ExpressionSegment"), optional=True),
            ),
        ),
    )


class ConflictTargetSegment(BaseSegment):
    """A Conflict Target Statement used within an INSERT statement.

    As specified in https://www.postgresql.org/docs/14/sql-insert.html
    """

    type = "conflict_target"

    match_grammar = OneOf(
        Sequence(
            Bracketed(
                Delimited(
                    Sequence(
                        OneOf(
                            Ref("ColumnReferenceSegment"),
                            Bracketed(Ref("ExpressionSegment")),
                        ),
                        Sequence(
                            "COLLATE",
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                        Ref("OperationClassReferenceSegment", optional=True),
                    )
                )
            ),
            Sequence("WHERE", Ref("ExpressionSegment"), optional=True),
        ),
        Sequence("ON", "CONSTRAINT", Ref("ParameterNameSegment")),
    )


class InsertStatementSegment(ansi.InsertStatementSegment):
    """An `INSERT` statement.

    https://www.postgresql.org/docs/14/sql-insert.html
    """

    match_grammar = Sequence(
        "INSERT",
        "INTO",
        Ref("TableReferenceSegment"),
        Ref("AsAliasExpressionSegment", optional=True),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Sequence("OVERRIDING", OneOf("SYSTEM", "USER"), "VALUE", optional=True),
        OneOf(
            Sequence("DEFAULT", "VALUES"),
            Ref("SelectableGrammar"),
        ),
        Sequence(
            "ON",
            "CONFLICT",
            Ref("ConflictTargetSegment", optional=True),
            Ref("ConflictActionSegment"),
            optional=True,
        ),
        Sequence(
            "RETURNING",
            OneOf(
                Ref("StarSegment"),
                Delimited(
                    Sequence(
                        Ref("ExpressionSegment"),
                        Ref("AsAliasExpressionSegment", optional=True),
                    ),
                ),
            ),
            optional=True,
        ),
    )


class DropTypeStatementSegment(ansi.DropTypeStatementSegment):
    """Drop Type Statement.

    As specified in https://www.postgresql.org/docs/14/sql-droptype.html
    """

    match_grammar = Sequence(
        "DROP",
        "TYPE",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("DatatypeSegment")),
        Ref("DropBehaviorGrammar", optional=True),
    )


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


class CreatePolicyStatementSegment(BaseSegment):
    """A `CREATE POLICY` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-createpolicy.html
    """

    type = "create_policy_statement"
    match_grammar = Sequence(
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


class CallStoredProcedureSegment(BaseSegment):
    """This is a CALL statement used to execute a stored procedure.

    https://www.postgresql.org/docs/14/sql-call.html
    """

    type = "call_statement"

    match_grammar = Sequence(
        "CALL",
        Ref("FunctionSegment"),
    )


class CreateDomainStatementSegment(BaseSegment):
    """A `CREATE Domain` statement.

    As Specified in https://www.postgresql.org/docs/current/sql-createdomain.html
    """

    type = "create_domain_statement"
    match_grammar = Sequence(
        "CREATE",
        "DOMAIN",
        Ref("ObjectReferenceSegment"),
        Sequence("AS", optional=True),
        Ref("DatatypeSegment"),
        Sequence("COLLATE", Ref("ObjectReferenceSegment"), optional=True),
        Sequence("DEFAULT", Ref("ExpressionSegment"), optional=True),
        AnyNumberOf(
            Sequence(
                Sequence(
                    "CONSTRAINT",
                    Ref("ObjectReferenceSegment"),
                    optional=True,
                ),
                OneOf(
                    Sequence(Ref.keyword("NOT", optional=True), "NULL"),
                    Sequence("CHECK", Ref("ExpressionSegment")),
                ),
            ),
        ),
    )


class AlterDomainStatementSegment(BaseSegment):
    """An `ALTER DOMAIN` statement.

    As Specified in https://www.postgresql.org/docs/current/sql-alterdomain.html
    """

    type = "alter_domain_statement"
    match_grammar: Matchable = Sequence(
        "ALTER",
        "DOMAIN",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(
                "SET",
                "DEFAULT",
                Ref("ExpressionSegment"),
            ),
            Sequence(
                "DROP",
                "DEFAULT",
            ),
            Sequence(OneOf("SET", "DROP"), "NOT", "NULL"),
            Sequence(
                "ADD",
                Sequence(
                    "CONSTRAINT",
                    Ref("ObjectReferenceSegment"),
                    optional=True,
                ),
                OneOf(
                    Sequence(Ref.keyword("NOT", optional=True), "NULL"),
                    Sequence("CHECK", Ref("ExpressionSegment")),
                ),
                Sequence("NOT", "VALID", optional=True),
            ),
            Sequence(
                "DROP",
                "CONSTRAINT",
                Ref("IfExistsGrammar", optional=True),
                Ref("ObjectReferenceSegment"),
                OneOf("RESTRICT", "CASCADE", optional=True),
            ),
            Sequence(
                "RENAME",
                "CONSTRAINT",
                Ref("ObjectReferenceSegment"),
                "TO",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "VALIDATE",
                "CONSTRAINT",
                Ref("ObjectReferenceSegment"),
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
                "TO",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "SET",
                "SCHEMA",
                Ref("ObjectReferenceSegment"),
            ),
        ),
    )


class DropDomainStatementSegment(BaseSegment):
    """Drop Domain Statement.

    As Specified in https://www.postgresql.org/docs/current/sql-dropdomain.html
    """

    type = "drop_domain_statement"
    match_grammar = Sequence(
        "DROP",
        "DOMAIN",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("ObjectReferenceSegment")),
        Ref("DropBehaviorGrammar", optional=True),
    )


class DropPolicyStatementSegment(BaseSegment):
    """A `DROP POLICY` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-droppolicy.html
    """

    type = "drop_policy_statement"
    match_grammar = Sequence(
        "DROP",
        "POLICY",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Ref("DropBehaviorGrammar", optional=True),
    )


class LoadStatementSegment(BaseSegment):
    """A `LOAD` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-load.html
    """

    type = "load_statement"
    match_grammar = Sequence(
        "LOAD",
        Ref("QuotedLiteralSegment"),
    )


class ResetStatementSegment(BaseSegment):
    """A `RESET` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-reset.html
    """

    type = "reset_statement"
    match_grammar = Sequence(
        "RESET",
        OneOf("ALL", Ref("ParameterNameSegment")),
    )


class DiscardStatementSegment(BaseSegment):
    """A `DISCARD` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-discard.html
    """

    type = "discard_statement"
    match_grammar = Sequence(
        "DISCARD",
        OneOf(
            "ALL",
            "PLANS",
            "SEQUENCES",
            "TEMPORARY",
            "TEMP",
        ),
    )


class ListenStatementSegment(BaseSegment):
    """A `LISTEN` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-listen.html
    """

    type = "listen_statement"
    match_grammar = Sequence("LISTEN", Ref("SingleIdentifierGrammar"))


class NotifyStatementSegment(BaseSegment):
    """A `NOTIFY` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-notify.html
    """

    type = "notify_statement"
    match_grammar = Sequence(
        "NOTIFY",
        Ref("SingleIdentifierGrammar"),
        Sequence(
            Ref("CommaSegment"),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


class UnlistenStatementSegment(BaseSegment):
    """A `UNLISTEN` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-unlisten.html
    """

    type = "unlisten_statement"
    match_grammar = Sequence(
        "UNLISTEN",
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("StarSegment"),
        ),
    )


class TruncateStatementSegment(ansi.TruncateStatementSegment):
    """`TRUNCATE TABLE` statement.

    https://www.postgresql.org/docs/14/sql-truncate.html
    """

    match_grammar = Sequence(
        "TRUNCATE",
        Ref.keyword("TABLE", optional=True),
        Delimited(
            OneOf(
                Sequence(
                    Ref.keyword("ONLY", optional=True),
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    Ref("TableReferenceSegment"),
                    Ref("StarSegment", optional=True),
                ),
            ),
        ),
        Sequence(
            OneOf("RESTART", "CONTINUE"),
            "IDENTITY",
            optional=True,
        ),
        Ref(
            "DropBehaviorGrammar",
            optional=True,
        ),
    )


class CopyStatementSegment(BaseSegment):
    """A `COPY` statement.

    As Specified in https://www.postgresql.org/docs/14/sql-copy.html
    """

    type = "copy_statement"

    _target_subset = OneOf(
        Ref("QuotedLiteralSegment"), Sequence("PROGRAM", Ref("QuotedLiteralSegment"))
    )

    _table_definition = Sequence(
        Ref("TableReferenceSegment"),
        Bracketed(Delimited(Ref("ColumnReferenceSegment")), optional=True),
    )

    _option = Sequence(
        Ref.keyword("WITH", optional=True),
        Bracketed(
            Delimited(
                AnySetOf(
                    Sequence("FORMAT", Ref("SingleIdentifierGrammar")),
                    Sequence("FREEZE", Ref("BooleanLiteralGrammar", optional=True)),
                    Sequence("DELIMITER", Ref("QuotedLiteralSegment")),
                    Sequence("NULL", Ref("QuotedLiteralSegment")),
                    Sequence("HEADER", Ref("BooleanLiteralGrammar", optional=True)),
                    Sequence("QUOTE", Ref("QuotedLiteralSegment")),
                    Sequence("ESCAPE", Ref("QuotedLiteralSegment")),
                    Sequence(
                        "FORCE_QUOTE",
                        OneOf(
                            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                            Ref("StarSegment"),
                        ),
                    ),
                    Sequence(
                        "FORCE_NOT_NULL",
                        Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    ),
                    Sequence(
                        "FORCE_NULL",
                        Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                    ),
                    Sequence("ENCODING", Ref("QuotedLiteralSegment")),
                )
            )
        ),
        optional=True,
    )

    match_grammar = Sequence(
        "COPY",
        OneOf(
            Sequence(
                _table_definition,
                "FROM",
                OneOf(
                    _target_subset,
                    Sequence("STDIN"),
                ),
                _option,
                Sequence("WHERE", Ref("ExpressionSegment"), optional=True),
            ),
            Sequence(
                OneOf(
                    _table_definition, Bracketed(Ref("UnorderedSelectStatementSegment"))
                ),
                "TO",
                OneOf(
                    _target_subset,
                    Sequence("STDOUT"),
                ),
                _option,
            ),
        ),
    )


class LanguageClauseSegment(BaseSegment):
    """Clause specifying language used for executing anonymous code blocks."""

    type = "language_clause"

    match_grammar = Sequence(
        "LANGUAGE",
        OneOf(Ref("NakedIdentifierSegment"), Ref("SingleQuotedIdentifierSegment")),
    )


class DoStatementSegment(BaseSegment):
    """A `DO` statement for executing anonymous code blocks.

    As specified in https://www.postgresql.org/docs/14/sql-do.html
    """

    type = "do_statement"

    match_grammar = Sequence(
        "DO",
        OneOf(
            Sequence(
                Ref("LanguageClauseSegment", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                Ref("QuotedLiteralSegment"),
                Ref("LanguageClauseSegment", optional=True),
            ),
        ),
    )


class CTEDefinitionSegment(ansi.CTEDefinitionSegment):
    """A CTE Definition from a WITH statement.

    https://www.postgresql.org/docs/14/queries-with.html

    TODO: Data-Modifying Statements (INSERT, UPDATE, DELETE) in WITH
    """

    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("CTEColumnList", optional=True),
        "AS",
        Sequence("NOT", "MATERIALIZED", optional=True),
        Bracketed(
            # Ephemeral here to subdivide the query.
            Ref("SelectableGrammar", ephemeral_name="SelectableGrammar")
        ),
        OneOf(
            Sequence(
                "SEARCH",
                OneOf(
                    "BREADTH",
                    "DEPTH",
                ),
                "FIRST",
                "BY",
                Ref("ColumnReferenceSegment"),
                "SET",
                Ref("ColumnReferenceSegment"),
            ),
            Sequence(
                "CYCLE",
                Ref("ColumnReferenceSegment"),
                "SET",
                Ref("ColumnReferenceSegment"),
                "USING",
                Ref("ColumnReferenceSegment"),
            ),
            optional=True,
        ),
    )


class ValuesClauseSegment(ansi.ValuesClauseSegment):
    """A `VALUES` clause within in `WITH` or `SELECT`."""

    match_grammar = Sequence(
        "VALUES",
        Delimited(
            Bracketed(
                Delimited(
                    Ref("ExpressionSegment"),
                    # DEFAULT keyword used in
                    # INSERT INTO statement.
                    "DEFAULT",
                    ephemeral_name="ValuesClauseElements",
                )
            ),
        ),
        Ref("AliasExpressionSegment", optional=True),
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
    )


class DeleteStatementSegment(ansi.DeleteStatementSegment):
    """A `DELETE` statement.

    https://www.postgresql.org/docs/14/sql-delete.html
    """

    match_grammar = Sequence(
        "DELETE",
        "FROM",
        Ref.keyword("ONLY", optional=True),
        Ref("TableReferenceSegment"),
        Ref("StarSegment", optional=True),
        Ref("AliasExpressionSegment", optional=True),
        Sequence(
            "USING",
            Indent,
            Delimited(
                Sequence(
                    Ref("TableExpressionSegment"),
                    Ref("AliasExpressionSegment", optional=True),
                ),
            ),
            Dedent,
            optional=True,
        ),
        OneOf(
            Sequence("WHERE", "CURRENT", "OF", Ref("ObjectReferenceSegment")),
            Ref("WhereClauseSegment"),
            optional=True,
        ),
        Sequence(
            "RETURNING",
            OneOf(
                Ref("StarSegment"),
                Delimited(
                    Sequence(
                        Ref("ExpressionSegment"),
                        Ref("AliasExpressionSegment", optional=True),
                    ),
                ),
            ),
            optional=True,
        ),
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
        OneOf(
            Sequence(
                Ref("ColumnReferenceSegment"),
                Ref("ArrayAccessorSegment", optional=True),
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
            ),
            Sequence(
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                ),
                Ref("EqualsSegment"),
                Bracketed(
                    Delimited(
                        Sequence(
                            OneOf(
                                Ref("LiteralGrammar"),
                                Ref("BareFunctionSegment"),
                                Ref("FunctionSegment"),
                                Ref("ColumnReferenceSegment"),
                                Ref("ExpressionSegment"),
                                "DEFAULT",
                            ),
                            AnyNumberOf(Ref("ShorthandCastSegment")),
                        ),
                    ),
                ),
            ),
        ),
    )


class UpdateStatementSegment(BaseSegment):
    """An `Update` statement.

    https://www.postgresql.org/docs/current/sql-update.html
    """

    type = "update_statement"
    match_grammar: Matchable = Sequence(
        # TODO add [ WITH [ RECURSIVE ] with_query [, ...] ]
        "UPDATE",
        Ref.keyword("ONLY", optional=True),
        Ref("TableReferenceSegment"),
        # SET is not a reserved word in all dialects (e.g. RedShift)
        # So specifically exclude as an allowed implicit alias to avoid parsing errors
        Ref("AliasExpressionSegment", exclude=Ref.keyword("SET"), optional=True),
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        OneOf(
            Sequence("WHERE", "CURRENT", "OF", Ref("ObjectReferenceSegment")),
            Ref("WhereClauseSegment"),
            optional=True,
        ),
        Sequence(
            "RETURNING",
            OneOf(
                Ref("StarSegment"),
                Delimited(
                    Ref("ExpressionSegment"),
                    Ref("AliasExpressionSegment", optional=True),
                ),
            ),
            optional=True,
        ),
    )


class CreateTypeStatementSegment(BaseSegment):
    """A `CREATE TYPE` statement.

    https://www.postgresql.org/docs/current/sql-createtype.html
    """

    type = "create_type_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "TYPE",
        Ref("ObjectReferenceSegment"),
        Sequence("AS", OneOf("ENUM", "RANGE", optional=True), optional=True),
        Bracketed(Delimited(Anything(), optional=True), optional=True),
    )


class AlterTypeStatementSegment(BaseSegment):
    """An `ALTER TYPE` statement.

    https://www.postgresql.org/docs/current/sql-createtype.html
    """

    type = "alter_type_statement"
    match_grammar: Matchable = Sequence(
        "ALTER",
        "TYPE",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Sequence(
                "OWNER",
                "TO",
                OneOf(
                    "CURRENT_USER",
                    "SESSION_USER",
                    "CURRENT_ROLE",
                    Ref("ObjectReferenceSegment"),
                ),
            ),
            Sequence(
                "RENAME",
                "TO",
                Ref("ObjectReferenceSegment"),
            ),
            Sequence(
                "SET",
                "SCHEMA",
                Ref("SchemaReferenceSegment"),
            ),
            Delimited(
                Sequence(
                    "ADD",
                    "ATTRIBUTE",
                    Ref("ColumnReferenceSegment"),
                    Ref("DatatypeSegment"),
                    Sequence(
                        "COLLATE",
                        Ref("QuotedLiteralSegment"),
                        optional=True,
                    ),
                    Ref("CascadeRestrictGrammar", optional=True),
                ),
                Sequence(
                    "ALTER",
                    "ATTRIBUTE",
                    Ref("ColumnReferenceSegment"),
                    Sequence("SET", "DATA", optional=True),
                    "TYPE",
                    Ref("DatatypeSegment"),
                    Sequence(
                        "COLLATE",
                        Ref("QuotedLiteralSegment"),
                        optional=True,
                    ),
                    Ref("CascadeRestrictGrammar", optional=True),
                ),
                Sequence(
                    "DROP",
                    "ATTRIBUTE",
                    Ref("IfExistsGrammar", optional=True),
                    Ref("ColumnReferenceSegment"),
                    Ref("CascadeRestrictGrammar", optional=True),
                ),
                Sequence(
                    "RENAME",
                    "ATTRIBUTE",
                    Ref("ColumnReferenceSegment"),
                    "TO",
                    Ref("ColumnReferenceSegment"),
                    Ref("CascadeRestrictGrammar", optional=True),
                ),
            ),
            Sequence(
                "ADD",
                "VALUE",
                Ref("IfNotExistsGrammar", optional=True),
                Ref("QuotedLiteralSegment"),
                Sequence(
                    OneOf("BEFORE", "AFTER"), Ref("QuotedLiteralSegment"), optional=True
                ),
            ),
        ),
    )


class CreateCollationStatementSegment(BaseSegment):
    """A `CREATE COLLATION` statement.

    https://www.postgresql.org/docs/current/sql-createcollation.html
    """

    type = "create_collation_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "COLLATION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf(
            Bracketed(
                Delimited(
                    Sequence(
                        "LOCALE",
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                    Sequence(
                        "LC_COLLATE",
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                    Sequence(
                        "LC_CTYPE",
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                    Sequence(
                        "PROVIDER",
                        Ref("EqualsSegment"),
                        OneOf("ICU", "LIBC"),
                    ),
                    Sequence(
                        "DETERMINISTIC",
                        Ref("EqualsSegment"),
                        Ref("BooleanLiteralGrammar"),
                    ),
                    Sequence(
                        "VERSION",
                        Ref("EqualsSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                )
            ),
            Sequence(
                "FROM",
                Ref("ObjectReferenceSegment"),
            ),
        ),
    )


class AlterSchemaStatementSegment(BaseSegment):
    """An `ALTER SCHEMA` statement.

    https://www.postgresql.org/docs/current/sql-alterschema.html
    """

    type = "alter_schema_statement"
    match_grammar = Sequence(
        "ALTER",
        "SCHEMA",
        Ref("SchemaReferenceSegment"),
        OneOf(
            Sequence(
                "RENAME",
                "TO",
                Ref("SchemaReferenceSegment"),
            ),
            Sequence(
                "OWNER",
                "TO",
                Ref("RoleReferenceSegment"),
            ),
        ),
    )


class LockTableStatementSegment(BaseSegment):
    """An `LOCK TABLE` statement.

    https://www.postgresql.org/docs/14/sql-lock.html
    """

    type = "lock_table_statement"
    match_grammar: Matchable = Sequence(
        "LOCK",
        Ref.keyword("TABLE", optional=True),
        Ref.keyword("ONLY", optional=True),
        OneOf(
            Delimited(
                Ref("TableReferenceSegment"),
            ),
            Ref("StarSegment"),
        ),
        Sequence(
            "IN",
            OneOf(
                Sequence("ACCESS", "SHARE"),
                Sequence("ROW", "SHARE"),
                Sequence("ROW", "EXCLUSIVE"),
                Sequence("SHARE", "UPDATE", "EXCLUSIVE"),
                "SHARE",
                Sequence("SHARE", "ROW", "EXCLUSIVE"),
                "EXCLUSIVE",
                Sequence("ACCESS", "EXCLUSIVE"),
            ),
            "MODE",
            optional=True,
        ),
        Ref.keyword("NOWAIT", optional=True),
    )


class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias.

    We override this for Postgres to allow keywords in fully qualified column
    names (using Full segments), similar to how this is done in BigQuery.
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
                    Ref("JoinLikeClauseGrammar"),
                    BracketedSegment,
                ),
                allow_gaps=False,
            ),
            allow_gaps=False,
            optional=True,
        ),
        allow_gaps=False,
    )
