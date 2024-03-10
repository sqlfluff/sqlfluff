"""The PostgreSQL dialect."""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    Anything,
    BaseSegment,
    Bracketed,
    BracketedSegment,
    CodeSegment,
    CommentSegment,
    CompositeComparisonOperatorSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    LiteralSegment,
    Matchable,
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
    StringParser,
    SymbolSegment,
    TypedParser,
    WhitespaceSegment,
    WordSegment,
)
from sqlfluff.core.parser.grammar.anyof import AnySetOf
from sqlfluff.core.parser.lexer import StringLexer
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_postgres_keywords import (
    get_keywords,
    postgres_keywords,
    postgres_postgis_datatype_keywords,
)

ansi_dialect = load_raw_dialect("ansi")

postgres_dialect = ansi_dialect.copy_as("postgres")

postgres_dialect.insert_lexer_matchers(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [
        StringLexer("right_arrow", "=>", CodeSegment),
    ],
    before="equals",
)

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
            SymbolSegment,
        ),
        StringLexer("at", "@", CodeSegment),
        # https://www.postgresql.org/docs/current/sql-syntax-lexical.html
        RegexLexer(
            "bit_string_literal",
            # binary (e.g. b'1001') or hex (e.g. X'1FF')
            r"[bBxX]'[0-9a-fA-F]*'",
            CodeSegment,
        ),
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
        ),
        RegexLexer(
            # pg_stat_statements which is an official postgres extension used for
            # storing the query logs replaces the actual literals used in the
            # query with $n where n is integer value. This grammar is for parsing
            # those literals.
            # ref: https://www.postgresql.org/docs/current/pgstatstatements.html
            "dollar_numeric_literal",
            r"\$\d+",
            LiteralSegment,
        ),
    ],
    before="word",  # Final thing to search for - as psql specific
)

postgres_dialect.insert_lexer_matchers(
    [
        StringLexer("walrus_operator", ":=", CodeSegment),
    ],
    before="equals",
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
            "single_quote",
            r"(?s)('')+?(?!')|('.*?(?<!')(?:'')*'(?!'))",
            CodeSegment,
        ),
        # In Postgres, there is no escape character for double quote strings
        RegexLexer(
            "double_quote",
            r'(?s)".+?"',
            CodeSegment,
        ),
        # Patching block comments to account for nested blocks.
        # N.B. this syntax is only possible via the non-standard-library
        # (but still backwards compatible) `regex` package.
        # https://pypi.org/project/regex/
        # Pattern breakdown:
        # /\*                    Match opening slash.
        #   (?>                  Atomic grouping
        #                        (https://www.regular-expressions.info/atomic.html).
        #       [^*/]+           Non forward-slash or asterisk characters.
        #       |\*(?!\/)        Negative lookahead assertion to match
        #                        asterisks not followed by a forward-slash.
        #       |/[^*]           Match lone forward-slashes not followed by an asterisk.
        #   )*                   Match any number of the atomic group contents.
        #   (?>
        #       (?R)             Recursively match the block comment pattern
        #                        to match nested block comments.
        #       (?>
        #           [^*/]+
        #           |\*(?!\/)
        #           |/[^*]
        #       )*
        #   )*
        # \*/                    Match closing slash.
        RegexLexer(
            "block_comment",
            r"/\*(?>[^*/]+|\*(?!\/)|/[^*])*(?>(?R)(?>[^*/]+|\*(?!\/)|/[^*])*)*\*/",
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
        RegexLexer("word", r"[a-zA-Z_][0-9a-zA-Z_$]*", WordSegment),
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
    NakedIdentifierFullSegment=TypedParser(
        "word",
        IdentifierSegment,
        type="naked_identifier_all",
    ),
    PropertiesNakedIdentifierSegment=TypedParser(  # allows reserved keywords
        "word",
        CodeSegment,
        type="properties_naked_identifier",
    ),
    SingleIdentifierFullGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("NakedIdentifierFullSegment"),
    ),
    DefinitionArgumentValueGrammar=OneOf(
        # This comes from def_arg:
        # https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L6331
        # TODO: this list is incomplete
        Ref("LiteralGrammar"),
        # This is a gross simplification of the grammar, which seems overly
        # permissive for the actual use cases here.  Grammar says this matches
        # reserved keywords.  Plus also unreserved keywords and IDENT:  func_type -->
        #     Typename --> SimpleTypename --> GenericType --> type_function_name -->
        #     { unreserved_keyword | type_func_name_keyword | IDENT }
        # We'll just match any normal code/keyword string here to keep it simple.
        Ref("PropertiesNakedIdentifierSegment"),
    ),
    CascadeRestrictGrammar=OneOf("CASCADE", "RESTRICT"),
    ExtendedTableReferenceGrammar=OneOf(
        Ref("TableReferenceSegment"),
        Sequence("ONLY", OptionallyBracketed(Ref("TableReferenceSegment"))),
        Sequence(Ref("TableReferenceSegment"), Ref("StarSegment")),
    ),
    RightArrowSegment=StringParser("=>", SymbolSegment, type="right_arrow"),
    OnKeywordAsIdentifierSegment=StringParser(
        "ON", IdentifierSegment, type="naked_identifier"
    ),
    DollarNumericLiteralSegment=TypedParser(
        "dollar_numeric_literal", LiteralSegment, type="dollar_numeric_literal"
    ),
    ForeignDataWrapperGrammar=Sequence("FOREIGN", "DATA", "WRAPPER"),
    OptionsListGrammar=Sequence(
        Delimited(Ref("NakedIdentifierFullSegment"), Ref("QuotedLiteralSegment"))
    ),
    OptionsGrammar=Sequence(
        "OPTIONS", Bracketed(AnyNumberOf(Ref("OptionsListGrammar")))
    ),
    CreateUserMappingGrammar=Sequence("CREATE", "USER", "MAPPING"),
    SessionInformationUserFunctionsGrammar=OneOf(
        "USER", "CURRENT_ROLE", "CURRENT_USER", "SESSION_USER"
    ),
    ImportForeignSchemaGrammar=Sequence("IMPORT", "FOREIGN", "SCHEMA"),
    CreateForeignTableGrammar=Sequence("CREATE", "FOREIGN", "TABLE"),
    IntervalUnitsGrammar=OneOf("YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND"),
    WalrusOperatorSegment=StringParser(":=", SymbolSegment, type="assignment_operator"),
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
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    Expression_C_Grammar=Sequence(
        Ref("WalrusOperatorSegment", optional=True),
        ansi_dialect.get_grammar("Expression_C_Grammar"),
    ),
    ParameterNameSegment=RegexParser(
        r'[A-Z_][A-Z0-9_$]*|"[^"]*"', CodeSegment, type="parameter"
    ),
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z_][A-Z0-9_$]*",
        CodeSegment,
        type="function_name_identifier",
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("ExpressionSegment"),
        Ref("NamedArgumentSegment"),
    ),
    FunctionContentsGrammar=AnyNumberOf(
        Ref("ExpressionSegment"),
        OptionallyBracketed(Ref("SetExpressionSegment")),
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
        # https://www.postgresql.org/docs/current/functions-string.html
        Sequence(
            OneOf(Ref("DatetimeUnitSegment"), Ref("ExpressionSegment")),
            AnySetOf(
                Sequence("FROM", Ref("ExpressionSegment")),
                Sequence("FOR", Ref("ExpressionSegment")),
                optional=True,
            ),
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
    QuotedLiteralSegment=OneOf(
        # Postgres allows newline-concatenated string literals (#1488).
        # Since these string literals can have comments between them,
        # we use grammar to handle this.
        # Note we CANNOT use Delimited as it's greedy and swallows the
        # last Newline - see #2495
        Sequence(
            TypedParser(
                "single_quote",
                LiteralSegment,
                type="quoted_literal",
            ),
            AnyNumberOf(
                Ref("MultilineConcatenateDelimiterGrammar"),
                TypedParser(
                    "single_quote",
                    LiteralSegment,
                    type="quoted_literal",
                ),
            ),
        ),
        Sequence(
            TypedParser(
                "bit_string_literal",
                LiteralSegment,
                type="quoted_literal",
            ),
            AnyNumberOf(
                Ref("MultilineConcatenateDelimiterGrammar"),
                TypedParser(
                    "bit_string_literal",
                    LiteralSegment,
                    type="quoted_literal",
                ),
            ),
        ),
        Delimited(
            TypedParser(
                "unicode_single_quote",
                LiteralSegment,
                type="quoted_literal",
            ),
            AnyNumberOf(
                Ref("MultilineConcatenateDelimiterGrammar"),
                TypedParser(
                    "unicode_single_quote",
                    LiteralSegment,
                    type="quoted_literal",
                ),
            ),
        ),
        Delimited(
            TypedParser(
                "escaped_single_quote",
                LiteralSegment,
                type="quoted_literal",
            ),
            AnyNumberOf(
                Ref("MultilineConcatenateDelimiterGrammar"),
                TypedParser(
                    "escaped_single_quote",
                    LiteralSegment,
                    type="quoted_literal",
                ),
            ),
        ),
        Delimited(
            TypedParser(
                "dollar_quote",
                LiteralSegment,
                type="quoted_literal",
            ),
            AnyNumberOf(
                Ref("MultilineConcatenateDelimiterGrammar"),
                TypedParser(
                    "dollar_quote",
                    LiteralSegment,
                    type="quoted_literal",
                ),
            ),
        ),
    ),
    QuotedIdentifierSegment=OneOf(
        TypedParser("double_quote", IdentifierSegment, type="quoted_identifier"),
        TypedParser("unicode_double_quote", LiteralSegment, type="quoted_literal"),
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
            OneOf("DEFAULT", Ref("EqualsSegment"), Ref("WalrusOperatorSegment")),
            Ref("ExpressionSegment"),
            optional=True,
        ),
    ),
    FrameClauseUnitGrammar=OneOf("RANGE", "ROWS", "GROUPS"),
    # Postgres supports the non-standard ISNULL and NONNULL comparison operators. See
    # https://www.postgresql.org/docs/14/functions-comparison.html
    IsNullGrammar=Ref.keyword("ISNULL"),
    NotNullGrammar=Ref.keyword("NOTNULL"),
    PreTableFunctionKeywordsGrammar=OneOf("LATERAL"),
    ConditionalCrossJoinKeywordsGrammar=Nothing(),
    UnconditionalCrossJoinKeywordsGrammar=Ref.keyword("CROSS"),
    SelectClauseTerminatorGrammar=OneOf(
        "INTO",
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        Ref("CommaSegment"),
        Ref("SetOperatorSegment"),
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("DollarNumericLiteralSegment"),
            Ref("PsqlVariableGrammar"),
        ],
        before=Ref("ArrayLiteralSegment"),
    ),
    FromClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "FromClauseTerminatorGrammar"
    ).copy(
        insert=[Ref("ForClauseSegment")],
    ),
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
        Ref("ForClauseSegment"),
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
        Ref("ForClauseSegment"),
    ),
    AccessorGrammar=AnyNumberOf(
        Ref("ArrayAccessorSegment"),
        # Add in semi structured expressions
        Ref("SemiStructuredAccessorSegment"),
    ),
    # PostgreSQL supports the non-standard "RETURNING" keyword, and therefore the
    # INSERT/UPDATE/DELETE statements can also be used in subqueries.
    NonWithSelectableGrammar=OneOf(
        Ref("SetExpressionSegment"),
        OptionallyBracketed(Ref("SelectStatementSegment")),
        Ref("NonSetSelectableGrammar"),
        # moved from NonWithNonSelectableGrammar:
        Ref("UpdateStatementSegment"),
        Ref("InsertStatementSegment"),
        Ref("DeleteStatementSegment"),
    ),
    NonWithNonSelectableGrammar=OneOf(),
    # https://www.postgresql.org/docs/current/functions-datetime.html
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "TIME", "TIMESTAMP", "INTERVAL"),
        TypedParser("single_quote", LiteralSegment, type="date_constructor_literal"),
        Sequence(
            Ref("IntervalUnitsGrammar"),
            Sequence("TO", Ref("IntervalUnitsGrammar"), optional=True),
        ),
    ),
    BracketedSetExpressionGrammar=Bracketed(Ref("SetExpressionSegment")),
    ReferentialActionGrammar=OneOf(
        "CASCADE",
        Sequence(
            "SET",
            OneOf("DEFAULT", "NULL"),
            Bracketed(
                Delimited(Ref("ColumnReferenceSegment")),
                optional=True,
            ),
        ),
        "RESTRICT",
        Sequence("NO", "ACTION"),
    ),
)


class OverlapSegment(CompositeComparisonOperatorSegment):
    """Overlaps range operator."""

    match_grammar = Sequence(
        Ref("AmpersandSegment"), Ref("AmpersandSegment"), allow_gaps=False
    )


class NotExtendRightSegment(CompositeComparisonOperatorSegment):
    """Not extend right range operator."""

    match_grammar = Sequence(
        Ref("AmpersandSegment"), Ref("RawGreaterThanSegment"), allow_gaps=False
    )


class NotExtendLeftSegment(CompositeComparisonOperatorSegment):
    """Not extend left range operator."""

    match_grammar = Sequence(
        Ref("AmpersandSegment"), Ref("RawLessThanSegment"), allow_gaps=False
    )


class AdjacentSegment(CompositeComparisonOperatorSegment):
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

    match_grammar = Bracketed(
        OneOf(
            # These three are for a single element access: [n]
            Ref("QualifiedNumericLiteralSegment"),
            Ref("NumericLiteralSegment"),
            Ref("ExpressionSegment"),
            # This is for slice access: [n:m], [:m], [n:], and [:]
            Sequence(
                OneOf(
                    Ref("QualifiedNumericLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
                Ref("SliceSegment"),
                OneOf(
                    Ref("QualifiedNumericLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
            ),
        ),
        bracket_type="square",
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
        Ref("DateTimeTypeIdentifier", optional=True),
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
                        Ref("BracketedArguments", optional=True),
                    ),
                    # numeric types [precision ["," scale])]
                    Sequence(
                        OneOf("DECIMAL", "NUMERIC"),
                        Ref("BracketedArguments", optional=True),
                    ),
                    # monetary type
                    "MONEY",
                    # character types
                    OneOf(
                        Sequence(
                            OneOf(
                                "BPCHAR",
                                "CHAR",
                                # CHAR VARYING is not documented, but it's
                                # in the real grammar:
                                # https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L14262
                                Sequence("CHAR", "VARYING"),
                                "CHARACTER",
                                Sequence("CHARACTER", "VARYING"),
                                "VARCHAR",
                            ),
                            Ref("BracketedArguments", optional=True),
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
                        Ref("BracketedArguments", optional=True),
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
            Ref("ArrayTypeSegment"),
            Ref("SizedArrayTypeSegment"),
            optional=True,
        ),
    )


class ArrayTypeSegment(ansi.ArrayTypeSegment):
    """Prefix for array literals specifying the type."""

    type = "array_type"
    match_grammar = Ref.keyword("ARRAY")


class IndexAccessMethodSegment(BaseSegment):
    """Index access method (e.g. `USING gist`)."""

    type = "index_access_method"
    match_grammar = Ref("SingleIdentifierGrammar")


class OperatorClassReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an operator class."""

    type = "operator_class_reference"


class DefinitionParameterSegment(BaseSegment):
    """A single definition parameter.

    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L6320
    """

    type = "definition_parameter"
    match_grammar: Matchable = Sequence(
        Ref("PropertiesNakedIdentifierSegment"),
        Sequence(
            Ref("EqualsSegment"),
            # could also contain ParameterNameSegment:
            Ref("DefinitionArgumentValueGrammar"),
            optional=True,
        ),
    )


class DefinitionParametersSegment(BaseSegment):
    """List of definition parameters.

    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L6313
    """

    type = "definition_parameters"
    match_grammar: Matchable = Bracketed(
        Delimited(
            Ref("DefinitionParameterSegment"),
        )
    )


class CreateCastStatementSegment(ansi.CreateCastStatementSegment):
    """A `CREATE CAST` statement.

    https://www.postgresql.org/docs/15/sql-createcast.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L8951
    """

    match_grammar: Matchable = Sequence(
        "CREATE",
        "CAST",
        Bracketed(
            Ref("DatatypeSegment"),
            "AS",
            Ref("DatatypeSegment"),
        ),
        OneOf(
            Sequence(
                "WITH",
                "FUNCTION",
                Ref("FunctionNameSegment"),
                Ref("FunctionParameterListGrammar", optional=True),
            ),
            Sequence("WITHOUT", "FUNCTION"),
            Sequence("WITH", "INOUT"),
        ),
        OneOf(
            Sequence("AS", "ASSIGNMENT", optional=True),
            Sequence("AS", "IMPLICIT", optional=True),
            optional=True,
        ),
    )


class DropCastStatementSegment(ansi.DropCastStatementSegment):
    """A `DROP CAST` statement.

    https://www.postgresql.org/docs/15/sql-dropcast.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L8995
    """

    match_grammar: Matchable = Sequence(
        "DROP",
        "CAST",
        Ref("IfExistsGrammar", optional=True),
        Bracketed(
            Ref("DatatypeSegment"),
            "AS",
            Ref("DatatypeSegment"),
        ),
        Ref("DropBehaviorGrammar", optional=True),
    )


class DropAggregateStatementSegment(BaseSegment):
    """A `DROP AGGREGATE` statement.

    https://www.postgresql.org/docs/15/sql-dropaggregate.html
    """

    type = "drop_aggregate_statement"
    match_grammar: Matchable = Sequence(
        "DROP",
        "AGGREGATE",
        Ref("IfExistsGrammar", optional=True),
        Delimited(
            Sequence(
                Ref("ObjectReferenceSegment"),
                OneOf(
                    Ref("FunctionParameterListGrammar"),
                    # TODO: Is this too permissive?
                    Anything(),
                    Ref("StarSegment"),
                ),
            ),
        ),
        Ref("DropBehaviorGrammar", optional=True),
    )


class CreateAggregateStatementSegment(BaseSegment):
    """A `CREATE AGGREGATE` statement.

    https://www.postgresql.org/docs/16/sql-createaggregate.html
    """

    type = "create_aggregate_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "AGGREGATE",
        Ref("ObjectReferenceSegment"),
        Bracketed(
            # TODO: Is this too permissive?
            Anything(),
        ),
        Ref("FunctionParameterListGrammar"),
    )


class RelationOptionSegment(BaseSegment):
    """Relation option element from reloptions.

    It is very similar to DefinitionParameterSegment except that it allows qualified
    names (e.g. namespace.attr = 5).

    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L3016-L3035
    """

    type = "relation_option"
    match_grammar: Matchable = Sequence(
        Ref("PropertiesNakedIdentifierSegment"),
        Sequence(
            Ref("DotSegment"),
            Ref("PropertiesNakedIdentifierSegment"),
            optional=True,
        ),
        Sequence(
            Ref("EqualsSegment"),
            # could also contain ParameterNameSegment:
            Ref("DefinitionArgumentValueGrammar"),
            optional=True,
        ),
    )


class RelationOptionsSegment(BaseSegment):
    """List of relation options.

    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L3003-L3014
    """

    type = "relation_options"
    match_grammar: Matchable = Bracketed(
        Delimited(
            Ref("RelationOptionSegment"),
        )
    )


class CreateFunctionStatementSegment(ansi.CreateFunctionStatementSegment):
    """A `CREATE FUNCTION` statement.

    This version in the ANSI dialect should be a "common subset" of the
    structure of the code for those dialects.
    postgres: https://www.postgresql.org/docs/13/sql-createfunction.html
    """

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
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
                Ref("ObjectReferenceSegment"),
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
        Ref("OrReplaceGrammar", optional=True),
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
            Sequence(
                "RETURN",
                Ref("ExpressionSegment"),
            ),
            Sequence(
                "BEGIN",
                "ATOMIC",
                AnyNumberOf(
                    Sequence(
                        Ref("InsertStatementSegment"),
                        Ref("SemicolonSegment"),
                    ),
                    Sequence(
                        Ref("UpdateStatementSegment"),
                        Ref("SemicolonSegment"),
                    ),
                    Sequence(
                        Ref("SelectStatementSegment"),
                        Ref("SemicolonSegment"),
                    ),
                ),
                "END",
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


class ForClauseSegment(BaseSegment):
    """`FOR ...` clause in `SELECT` statements.

    As specified in
    https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE.
    """

    type = "for_clause"

    match_grammar = Sequence(
        "FOR",
        OneOf(
            "UPDATE",
            Sequence("NO", "KEY", "UPDATE"),
            "SHARE",
            Sequence("KEY", "SHARE"),
        ),
        Sequence(
            "OF",
            Delimited(
                Ref("TableReferenceSegment"),
            ),
            optional=True,
        ),
        OneOf(
            "NOWAIT",
            Sequence("SKIP", "LOCKED"),
            optional=True,
        ),
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """Overrides ANSI Statement, to allow for SELECT INTO statements."""

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("IntoClauseSegment", optional=True),
        ],
        before=Ref("FromClauseSegment", optional=True),
        terminators=[
            Sequence("WITH", Ref.keyword("NO", optional=True), "DATA"),
            Sequence("ON", "CONFLICT"),
            Ref.keyword("RETURNING"),
            Ref("WithCheckOptionSegment"),
        ],
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """Overrides ANSI as the parse grammar copy needs to be reapplied."""

    # Inherit most of the parse grammar from the unordered version.
    match_grammar: Matchable = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
        ]
    ).copy(
        insert=[Ref("ForClauseSegment", optional=True)],
        before=Ref("LimitClauseSegment", optional=True),
        # Overwrite the terminators, because we want to remove some.
        replace_terminators=True,
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("WithDataClauseSegment"),
            Sequence("ON", "CONFLICT"),
            Ref.keyword("RETURNING"),
            Ref("WithCheckOptionSegment"),
        ],
    )


class SelectClauseSegment(ansi.SelectClauseSegment):
    """Overrides ANSI to allow INTO as a terminator."""

    match_grammar = Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        Delimited(
            Ref("SelectClauseElementSegment"),
            # In Postgres you don't need an element so make it optional
            optional=True,
            allow_trailing=True,
        ),
        Dedent,
        terminators=[
            "INTO",
            "FROM",
            "WHERE",
            Sequence("ORDER", "BY"),
            "LIMIT",
            "OVERLAPS",
            Ref("SetOperatorSegment"),
            Sequence("WITH", Ref.keyword("NO", optional=True), "DATA"),
            Ref("WithCheckOptionSegment"),
        ],
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
    )


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


class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`."""

    type = "groupby_clause"
    match_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        Delimited(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                Ref("CubeRollupClauseSegment"),
                Ref("GroupingSetsClauseSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
                Bracketed(),  # Allows empty parentheses
            ),
            terminators=[
                Sequence("ORDER", "BY"),
                "LIMIT",
                "HAVING",
                "QUALIFY",
                "WINDOW",
                Ref("SetOperatorSegment"),
            ],
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
        OneOf(
            # role_specification
            Sequence(
                OneOf(
                    "CURRENT_ROLE",
                    "CURRENT_USER",
                    "SESSION_USER",
                    Ref("RoleReferenceSegment"),
                ),
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
                    Sequence(
                        Ref.keyword("ENCRYPTED", optional=True),
                        "PASSWORD",
                        OneOf(Ref("QuotedLiteralSegment"), "NULL"),
                    ),
                    Sequence("VALID", "UNTIL", Ref("QuotedLiteralSegment")),
                ),
            ),
            # name only
            Sequence(
                Ref("RoleReferenceSegment"),
                Sequence("RENAME", "TO", Ref("RoleReferenceSegment")),
            ),
            # role_specification | all
            Sequence(
                OneOf(
                    "CURRENT_ROLE",
                    "CURRENT_USER",
                    "SESSION_USER",
                    "ALL",
                    Ref("RoleReferenceSegment"),
                ),
                Sequence(
                    "IN",
                    "DATABASE",
                    Ref("DatabaseReferenceSegment"),
                    optional=True,
                ),
                OneOf(
                    Sequence(
                        "SET",
                        Ref("ParameterNameSegment"),
                        OneOf(
                            Sequence(
                                OneOf("TO", Ref("EqualsSegment")),
                                OneOf(
                                    "DEFAULT",
                                    Delimited(
                                        Ref("LiteralGrammar"),
                                        Ref("NakedIdentifierSegment"),
                                        # https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L1810-L1815
                                        Ref("OnKeywordAsIdentifierSegment"),
                                    ),
                                ),
                            ),
                            Sequence(
                                "FROM",
                                "CURRENT",
                            ),
                        ),
                    ),
                    Sequence("RESET", OneOf(Ref("ParameterNameSegment"), "ALL")),
                ),
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


class CreateSchemaStatementSegment(ansi.CreateSchemaStatementSegment):
    """A `CREATE SCHEMA` statement.

    https://www.postgresql.org/docs/15/sql-createschema.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L1493
    """

    match_grammar: Matchable = Sequence(
        "CREATE",
        "SCHEMA",
        Ref("IfNotExistsGrammar", optional=True),
        OneOf(
            Sequence(
                # schema name defaults to role if not provided
                Ref("SchemaReferenceSegment", optional=True),
                "AUTHORIZATION",
                Ref("RoleReferenceSegment"),
            ),
            Ref("SchemaReferenceSegment"),
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
                                    # A single COLLATE segment can come before or
                                    # after constraint segments
                                    OneOf(
                                        Ref("ColumnConstraintSegment"),
                                        Sequence(
                                            "COLLATE",
                                            Ref("CollationReferenceSegment"),
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
                        optional=True,
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
                                        Ref("CollationReferenceSegment"),
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
                Sequence("WITH", Ref("RelationOptionsSegment")),
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
            Bracketed(
                Delimited(Ref("ColumnReferenceSegment")),
                optional=True,
            ),
            Sequence("USING", Ref("ParameterNameSegment"), optional=True),
            OneOf(
                Sequence(
                    "WITH",
                    Bracketed(
                        Delimited(
                            Sequence(
                                Ref("ParameterNameSegment"),
                                Sequence(
                                    Ref("EqualsSegment"),
                                    OneOf(
                                        Ref("LiteralGrammar"),
                                        Ref("NakedIdentifierSegment"),
                                    ),
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
            Sequence("COLLATE", Ref("CollationReferenceSegment"), optional=True),
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
                    Sequence(
                        "COLLATE", Ref("CollationReferenceSegment"), optional=True
                    ),
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
                Sequence("SET", Ref("RelationOptionsSegment")),
                # Documentation says you can only provide keys in RESET options, but the
                # actual grammar lets you pass in values too.
                Sequence("RESET", Ref("RelationOptionsSegment")),
                Sequence(
                    "SET", "STORAGE", OneOf("PLAIN", "EXTERNAL", "EXTENDED", "MAIN")
                ),
            ),
        ),
        Sequence("ADD", Ref("TableConstraintSegment")),
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
        Sequence("SET", Ref("RelationOptionsSegment")),
        # Documentation says you can only provide keys in RESET options, but the
        # actual grammar lets you pass in values too.
        Sequence("RESET", Ref("RelationOptionsSegment")),
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


class VersionIdentifierSegment(BaseSegment):
    """A reference to an version."""

    type = "version_identifier"
    # match grammar (don't allow whitespace)
    match_grammar: Matchable = OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("NakedIdentifierSegment"),
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
        Ref("DropBehaviorGrammar", optional=True),
    )


class AlterExtensionStatementSegment(BaseSegment):
    """An `ALTER EXTENSION` statement.

    https://www.postgresql.org/docs/16/sql-alterextension.html
    """

    type = "alter_extension_statement"
    match_grammar: Matchable = Sequence(
        "ALTER",
        "EXTENSION",
        Ref("ExtensionReferenceSegment"),
        OneOf(
            Sequence(
                "UPDATE",
                Sequence(
                    "TO",
                    Ref("LiteralGrammar"),
                    optional=True,
                ),
            ),
            Sequence(
                "SET",
                "SCHEMA",
                OneOf(Ref("SchemaReferenceSegment"), "CURRENT_SCHEMA"),
            ),
            Sequence(
                OneOf(
                    "ADD",
                    "DROP",
                ),
                OneOf(
                    Sequence(
                        OneOf(
                            Sequence("ACCESS", "METHOD"),
                            "COLLATION",
                            "CONVERSION",
                            "DOMAIN",
                            Sequence("EVENT", "TRIGGER"),
                            Sequence("FOREIGN", "DATA", "WRAPPER"),
                            Sequence("FOREIGN", "TABLE"),
                            Sequence(
                                Ref.keyword("PROCEDURAL", optional=True),
                                "LANGUAGE",
                            ),
                            "SCHEMA",
                            "SEQUENCE",
                            "SERVER",
                            Sequence(
                                "TEXT",
                                "SEARCH",
                                OneOf(
                                    "CONFIGURATION",
                                    "DICTIONARY",
                                    "PARSER",
                                    "TEMPLATE",
                                ),
                            ),
                            "TYPE",
                        ),
                        Ref("ObjectReferenceSegment"),
                    ),
                    Sequence(
                        OneOf(
                            Sequence("MATERIALIZED", "VIEW"),
                            "TABLE",
                            "VIEW",
                        ),
                        Ref("TableReferenceSegment"),
                    ),
                    Sequence(
                        "AGGREGATE",
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
                        OneOf(
                            "FUNCTION",
                            "PROCEDURE",
                            "ROUTINE",
                        ),
                        Delimited(
                            Sequence(
                                Ref("FunctionNameSegment"),
                                Ref("FunctionParameterListGrammar", optional=True),
                            ),
                        ),
                    ),
                    Sequence(
                        "OPERATOR",
                        OneOf(
                            Sequence(
                                Ref("ObjectReferenceSegment"),
                                Bracketed(
                                    Delimited(
                                        Ref("DatatypeSegment"),
                                        Ref("CommaSegment"),
                                        Ref("DatatypeSegment"),
                                    ),
                                ),
                            ),
                            Sequence(
                                OneOf("CLASS", "FAMILY"),
                                Ref("ObjectReferenceSegment"),
                                "USING",
                                Ref("IndexAccessMethodSegment"),
                            ),
                        ),
                    ),
                    Sequence("TRANSFORM", "FOR", "TYPE", Ref("ParameterNameSegment")),
                ),
            ),
        ),
    )


class PublicationReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to a publication."""

    type = "publication_reference"
    match_grammar: Matchable = Ref("SingleIdentifierGrammar")


class PublicationTableSegment(BaseSegment):
    """Specification for a single table object in a publication."""

    type = "publication_table"
    match_grammar: Matchable = Sequence(
        Ref("ExtendedTableReferenceGrammar"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Sequence("WHERE", Bracketed(Ref("ExpressionSegment")), optional=True),
    )


class PublicationObjectsSegment(BaseSegment):
    """Specification for one or more objects in a publication.

    Unlike the underlying PG grammar which has one object per PublicationObjSpec and
    so requires one to track the previous object type if it's a "continuation object
    type", this grammar groups together the continuation objects, e.g.
    "TABLE a, b, TABLE c, d" results in two segments: one containing references
    "a, b", and the other contianing "c, d".

    https://www.postgresql.org/docs/15/sql-createpublication.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L10435-L10530
    """

    type = "publication_objects"
    match_grammar: Matchable = OneOf(
        Sequence(
            "TABLE",
            Delimited(
                Ref("PublicationTableSegment"),
                terminators=[Sequence(Ref("CommaSegment"), OneOf("TABLE", "TABLES"))],
            ),
        ),
        Sequence(
            "TABLES",
            "IN",
            "SCHEMA",
            Delimited(
                OneOf(Ref("SchemaReferenceSegment"), "CURRENT_SCHEMA"),
                terminators=[Sequence(Ref("CommaSegment"), OneOf("TABLE", "TABLES"))],
            ),
        ),
    )


class CreatePublicationStatementSegment(BaseSegment):
    """A `CREATE PUBLICATION` statement.

    https://www.postgresql.org/docs/15/sql-createpublication.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L10390-L10530
    """

    type = "create_publication_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "PUBLICATION",
        Ref("PublicationReferenceSegment"),
        OneOf(
            Sequence("FOR", "ALL", "TABLES"),
            Sequence("FOR", Delimited(Ref("PublicationObjectsSegment"))),
            optional=True,
        ),
        Sequence(
            "WITH",
            Ref("DefinitionParametersSegment"),
            optional=True,
        ),
    )


class AlterPublicationStatementSegment(BaseSegment):
    """A `ALTER PUBLICATION` statement.

    https://www.postgresql.org/docs/15/sql-alterpublication.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L10549
    """

    type = "alter_publication_statement"
    match_grammar: Matchable = Sequence(
        "ALTER",
        "PUBLICATION",
        Ref("PublicationReferenceSegment"),
        OneOf(
            Sequence("SET", Ref("DefinitionParametersSegment")),
            Sequence("ADD", Delimited(Ref("PublicationObjectsSegment"))),
            Sequence("SET", Delimited(Ref("PublicationObjectsSegment"))),
            Sequence("DROP", Delimited(Ref("PublicationObjectsSegment"))),
            Sequence("RENAME", "TO", Ref("PublicationReferenceSegment")),
            Sequence(
                "OWNER",
                "TO",
                OneOf(
                    "CURRENT_ROLE",
                    "CURRENT_USER",
                    "SESSION_USER",
                    # must come last; CURRENT_USER isn't reserved:
                    Ref("RoleReferenceSegment"),
                ),
            ),
        ),
    )


class DropPublicationStatementSegment(BaseSegment):
    """A `DROP PUBLICATION` statement.

    https://www.postgresql.org/docs/15/sql-droppublication.html
    """

    type = "drop_publication_statement"
    match_grammar: Matchable = Sequence(
        "DROP",
        "PUBLICATION",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("PublicationReferenceSegment")),
        Ref("DropBehaviorGrammar", optional=True),
    )


class CreateMaterializedViewStatementSegment(BaseSegment):
    """A `CREATE MATERIALIZED VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-creatematerializedview.html
    """

    type = "create_materialized_view_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        "MATERIALIZED",
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Sequence("USING", Ref("ParameterNameSegment"), optional=True),
        Sequence("WITH", Ref("RelationOptionsSegment"), optional=True),
        Sequence("TABLESPACE", Ref("TablespaceReferenceSegment"), optional=True),
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


class WithCheckOptionSegment(BaseSegment):
    """WITH [ CASCADED | LOCAL ] CHECK OPTION for Postgres' CREATE VIEWS.

    https://www.postgresql.org/docs/14/sql-createview.html
    """

    type = "with_check_option"
    match_grammar: Matchable = Sequence(
        "WITH", OneOf("CASCADED", "LOCAL"), "CHECK", "OPTION"
    )


class AlterPolicyStatementSegment(BaseSegment):
    """An ALTER POLICY statement.

    As specified in https://www.postgresql.org/docs/current/sql-alterpolicy.html
    """

    type = "alter_policy_statement"

    match_grammar = Sequence(
        "ALTER",
        "POLICY",
        Ref("ObjectReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence("RENAME", "TO", Ref("ObjectReferenceSegment")),
            AnySetOf(
                Sequence(
                    "TO",
                    Delimited(
                        OneOf(
                            Ref("RoleReferenceSegment"),
                            "PUBLIC",
                            "CURRENT_ROLE",
                            "CURRENT_USER",
                            "SESSION_USER",
                        )
                    ),
                ),
                Sequence("USING", Bracketed(Ref("ExpressionSegment"))),
                Sequence(
                    "WITH",
                    "CHECK",
                    Bracketed(Ref("ExpressionSegment")),
                ),
                min_times=1,
            ),
        ),
    )


class CreateViewStatementSegment(BaseSegment):
    """An `Create VIEW` statement.

    As specified in https://www.postgresql.org/docs/14/sql-createview.html
    """

    type = "create_view_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryGrammar", optional=True),
        Ref.keyword("RECURSIVE", optional=True),
        "VIEW",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        Sequence("WITH", Ref("RelationOptionsSegment"), optional=True),
        "AS",
        OneOf(
            OptionallyBracketed(Ref("SelectableGrammar")),
            Ref("ValuesClauseSegment"),
        ),
        Ref("WithCheckOptionSegment", optional=True),
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


class DropViewStatementSegment(ansi.DropViewStatementSegment):
    """A `DROP VIEW` statement.

    https://www.postgresql.org/docs/15/sql-dropview.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L6698-L6719
    """

    match_grammar: Matchable = Sequence(
        "DROP",
        "VIEW",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("TableReferenceSegment")),
        Ref("DropBehaviorGrammar", optional=True),
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


class VacuumStatementSegment(BaseSegment):
    """A `VACUUM` statement.

    https://www.postgresql.org/docs/15/sql-vacuum.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L11658
    """

    type = "vacuum_statement"
    match_grammar = Sequence(
        "VACUUM",
        OneOf(
            Sequence(
                Ref.keyword("FULL", optional=True),
                Ref.keyword("FREEZE", optional=True),
                Ref.keyword("VERBOSE", optional=True),
                OneOf("ANALYZE", "ANALYSE", optional=True),
            ),
            Bracketed(
                Delimited(
                    Sequence(
                        OneOf(
                            "FULL",
                            "FREEZE",
                            "VERBOSE",
                            "ANALYZE",
                            "ANALYSE",
                            "DISABLE_PAGE_SKIPPING",
                            "SKIP_LOCKED",
                            "INDEX_CLEANUP",
                            "PROCESS_TOAST",
                            "TRUNCATE",
                            "PARALLEL",
                        ),
                        OneOf(
                            Ref("LiteralGrammar"),
                            Ref("NakedIdentifierSegment"),
                            # https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L1810-L1815
                            Ref("OnKeywordAsIdentifierSegment"),
                            optional=True,
                        ),
                    ),
                ),
            ),
            optional=True,
        ),
        Delimited(
            Sequence(
                Ref("TableReferenceSegment"),
                Ref("BracketedColumnReferenceListGrammar", optional=True),
            ),
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
                    Ref("ShorthandCastSegment"),
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    Ref("BareFunctionSegment"),
                    Ref("ExpressionSegment"),
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
            Sequence(
                "UNIQUE",
                Sequence(
                    "NULLS",
                    Ref.keyword("NOT", optional=True),
                    "DISTINCT",
                    optional=True,
                ),
                Sequence("WITH", Ref("DefinitionParametersSegment"), optional=True),
                Sequence(
                    "USING",
                    "INDEX",
                    "TABLESPACE",
                    Ref("TablespaceReferenceSegment"),
                    optional=True,
                ),
            ),
            Sequence(
                "PRIMARY",
                "KEY",
                Sequence("WITH", Ref("DefinitionParametersSegment"), optional=True),
                Sequence(
                    "USING",
                    "INDEX",
                    "TABLESPACE",
                    Ref("TablespaceReferenceSegment"),
                    optional=True,
                ),
            ),
            Ref("ReferenceDefinitionGrammar"),  # REFERENCES reftable [ ( refcolumn) ]
        ),
        OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE"), optional=True),
        OneOf(
            Sequence("INITIALLY", "DEFERRED"),
            Sequence("INITIALLY", "IMMEDIATE"),
            optional=True,
        ),
    )


class ForeignTableColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """A column option for a foreign table.

    Each CREATE FOREIGN TABLE column can have 0 or more.

    https://www.postgresql.org/docs/16/sql-createforeigntable.html
    """

    match_grammar = Sequence(
        # [ CONSTRAINT constraint_name ]
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        OneOf(
            # NOT NULL | NULL
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),
            # CHECK ( expression ) [ NO INHERIT ]
            Sequence(
                "CHECK",
                Bracketed(Ref("ExpressionSegment")),
                Sequence("NO", "INHERIT", optional=True),
            ),
            # DEFAULT default_expr
            Sequence(
                "DEFAULT",
                OneOf(
                    Ref("ShorthandCastSegment"),
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    Ref("BareFunctionSegment"),
                    Ref("ExpressionSegment"),
                ),
            ),
            # GENERATED ALWAYS AS ( generation_expr ) STORED
            Sequence("GENERATED", "ALWAYS", "AS", Ref("ExpressionSegment"), "STORED"),
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
                Sequence(
                    "NULLS",
                    Ref.keyword("NOT", optional=True),
                    "DISTINCT",
                    optional=True,
                ),
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
                Sequence("USING", Ref("IndexAccessMethodSegment"), optional=True),
                Bracketed(Delimited(Ref("ExclusionConstraintElementSegment"))),
                Ref("IndexParametersSegment", optional=True),
                Sequence("WHERE", Bracketed(Ref("ExpressionSegment")), optional=True),
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
        ),
        AnyNumberOf(
            OneOf("DEFERRABLE", Sequence("NOT", "DEFERRABLE")),
            OneOf(
                Sequence("INITIALLY", "DEFERRED"), Sequence("INITIALLY", "IMMEDIATE")
            ),
            Sequence("NOT", "VALID"),
            Sequence("NO", "INHERIT"),
        ),
    )


class ForeignTableTableConstraintSegment(ansi.TableConstraintSegment):
    """A table constraint on a foreign table, e.g. for CREATE FOREIGN TABLE.

    As specified in https://www.postgresql.org/docs/16/sql-createforeigntable.html
    """

    match_grammar = Sequence(
        # [ CONSTRAINT constraint_name ]
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            optional=True,
        ),
        # CHECK ( expression ) [ NO INHERIT ]
        Sequence(
            "CHECK",
            Bracketed(Ref("ExpressionSegment")),
            Sequence("NO", "INHERIT", optional=True),
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
        Sequence("WITH", Ref("DefinitionParametersSegment"), optional=True),
        Sequence(
            "USING",
            "INDEX",
            "TABLESPACE",
            Ref("TablespaceReferenceSegment"),
            optional=True,
        ),
    )


class IndexElementOptionsSegment(BaseSegment):
    """Index element options segment.

    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L8057
    """

    type = "index_element_options"

    match_grammar = Sequence(
        Sequence("COLLATE", Ref("CollationReferenceSegment"), optional=True),
        Sequence(
            Ref(
                "OperatorClassReferenceSegment",
                exclude=Sequence("NULLS", OneOf("FIRST", "LAST")),
            ),
            Ref("RelationOptionsSegment", optional=True),  # args for opclass
            optional=True,
        ),
        OneOf("ASC", "DESC", optional=True),
        Sequence("NULLS", OneOf("FIRST", "LAST"), optional=True),
    )


class IndexElementSegment(BaseSegment):
    """Index element segment.

    As found in https://www.postgresql.org/docs/15/sql-altertable.html.
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L8089
    """

    type = "index_element"
    match_grammar = Sequence(
        OneOf(
            Ref("ColumnReferenceSegment"),
            # TODO: This is still not perfect.  This corresponds to
            # func_expr_windowless in the grammar and we don't currently
            # implement everything it provides.
            Ref("FunctionSegment"),
            Bracketed(Ref("ExpressionSegment")),
        ),
        Ref("IndexElementOptionsSegment", optional=True),
    )


class ExclusionConstraintElementSegment(BaseSegment):
    """Exclusion constraint element segment.

    As found in https://www.postgresql.org/docs/15/sql-altertable.html.
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L4277
    """

    type = "exclusion_constraint_element"
    match_grammar = Sequence(
        Ref("IndexElementSegment"),
        "WITH",
        Ref("ComparisonOperatorGrammar"),
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
                terminators=["IN", "GRANT", "REVOKE"],
            ),
            optional=True,
        ),
        Sequence(
            "IN",
            "SCHEMA",
            Delimited(
                Ref("SchemaReferenceSegment"),
                terminators=["GRANT", "REVOKE"],
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
            terminators=["ON"],
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
            terminators=["WITH"],
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
            terminators=["RESTRICT", "CASCADE"],
        ),
        Ref("DropBehaviorGrammar", optional=True),
    )


class DropOwnedStatementSegment(BaseSegment):
    """A `DROP OWNED` statement.

    https://www.postgresql.org/docs/15/sql-drop-owned.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L6667
    """

    type = "drop_owned_statement"

    match_grammar = Sequence(
        "DROP",
        "OWNED",
        "BY",
        Delimited(
            OneOf(
                "CURRENT_ROLE",
                "CURRENT_USER",
                "SESSION_USER",
                # must come last; CURRENT_USER isn't reserved:
                Ref("RoleReferenceSegment"),
            ),
        ),
        Ref("DropBehaviorGrammar", optional=True),
    )


class ReassignOwnedStatementSegment(BaseSegment):
    """A `REASSIGN OWNED` statement.

    https://www.postgresql.org/docs/15/sql-reassign-owned.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L6678
    """

    type = "reassign_owned_statement"

    match_grammar = Sequence(
        "REASSIGN",
        "OWNED",
        "BY",
        Delimited(
            OneOf(
                "CURRENT_ROLE",
                "CURRENT_USER",
                "SESSION_USER",
                # must come last; CURRENT_USER isn't reserved:
                Ref("RoleReferenceSegment"),
            ),
        ),
        "TO",
        OneOf(
            "CURRENT_ROLE",
            "CURRENT_USER",
            "SESSION_USER",
            # must come last; CURRENT_USER isn't reserved:
            Ref("RoleReferenceSegment"),
        ),
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
        "INDEX",
        Ref.keyword("CONCURRENTLY", optional=True),
        Sequence(
            Ref("IfNotExistsGrammar", optional=True),
            Ref("IndexReferenceSegment"),
            optional=True,
        ),
        "ON",
        Ref.keyword("ONLY", optional=True),
        Ref("TableReferenceSegment"),
        Sequence("USING", Ref("IndexAccessMethodSegment"), optional=True),
        Bracketed(Delimited(Ref("IndexElementSegment"))),
        Sequence(
            "INCLUDE", Bracketed(Delimited(Ref("IndexElementSegment"))), optional=True
        ),
        Sequence("NULLS", Ref.keyword("NOT", optional=True), "DISTINCT", optional=True),
        Sequence("WITH", Ref("RelationOptionsSegment"), optional=True),
        Sequence("TABLESPACE", Ref("TablespaceReferenceSegment"), optional=True),
        Sequence("WHERE", Ref("ExpressionSegment"), optional=True),
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


class DropIndexStatementSegment(ansi.DropIndexStatementSegment):
    """A `DROP INDEX` statement.

    https://www.postgresql.org/docs/15/sql-dropindex.html
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L6698-L6719
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L6808-L6829
    """

    match_grammar: Matchable = Sequence(
        "DROP",
        "INDEX",
        Ref.keyword("CONCURRENTLY", optional=True),
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("IndexReferenceSegment")),
        Ref("DropBehaviorGrammar", optional=True),
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


class StatisticsReferenceSegment(ansi.ObjectReferenceSegment):
    """Statics Reference."""

    type = "statistics_reference"


class CreateStatisticsStatementSegment(BaseSegment):
    """Create Statistics Segment.

    As specified in https://www.postgresql.org/docs/16/sql-createstatistics.html
    """

    type = "create_statistics_statement"

    match_grammar = Sequence(
        "CREATE",
        "STATISTICS",
        Sequence(
            Ref("IfNotExistsGrammar", optional=True),
            Ref("StatisticsReferenceSegment"),
            optional=True,
        ),
        Bracketed(
            Delimited(
                "DEPENDENCIES",
                "MCV",
                "NDISTINCT",
            ),
            optional=True,
        ),
        "ON",
        Delimited(
            Ref("ColumnReferenceSegment"),
            Ref("ExpressionSegment"),
        ),
        "FROM",
        Ref("TableReferenceSegment"),
    )


class AlterStatisticsStatementSegment(BaseSegment):
    """Alter Statistics Segment.

    As specified in https://www.postgresql.org/docs/16/sql-alterstatistics.html
    """

    type = "alter_statistics_statement"

    match_grammar = Sequence(
        "ALTER",
        "STATISTICS",
        Ref("StatisticsReferenceSegment"),
        OneOf(
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
                "RENAME",
                "TO",
                Ref("StatisticsReferenceSegment"),
            ),
            Sequence(
                "SET",
                OneOf(
                    Sequence(
                        "SCHEMA",
                        Ref("SchemaReferenceSegment"),
                    ),
                    Sequence(
                        "STATISTICS",
                        Ref("NumericLiteralSegment"),
                    ),
                ),
            ),
        ),
    )


class DropStatisticsStatementSegment(BaseSegment):
    """Alter Statistics Segment.

    As specified in https://www.postgresql.org/docs/16/sql-dropstatistics.html
    """

    type = "drop_statistics_statement"

    match_grammar = Sequence(
        "DROP",
        "STATISTICS",
        Ref("IfExistsGrammar", optional=True),
        Delimited(Ref("StatisticsReferenceSegment")),
        OneOf(
            "CASCADE",
            "RESTRICT",
            optional=True,
        ),
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

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("AlterDefaultPrivilegesStatementSegment"),
            Ref("DropOwnedStatementSegment"),
            Ref("ReassignOwnedStatementSegment"),
            Ref("CommentOnStatementSegment"),
            Ref("AnalyzeStatementSegment"),
            Ref("CreateTableAsStatementSegment"),
            Ref("AlterTriggerStatementSegment"),
            Ref("SetStatementSegment"),
            Ref("AlterPolicyStatementSegment"),
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
            Ref("VacuumStatementSegment"),
            Ref("AlterFunctionStatementSegment"),
            Ref("CreateViewStatementSegment"),
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
            Ref("AlterExtensionStatementSegment"),
            Ref("CreatePublicationStatementSegment"),
            Ref("AlterPublicationStatementSegment"),
            Ref("DropPublicationStatementSegment"),
            Ref("CreateTypeStatementSegment"),
            Ref("AlterTypeStatementSegment"),
            Ref("AlterSchemaStatementSegment"),
            Ref("LockTableStatementSegment"),
            Ref("ClusterStatementSegment"),
            Ref("CreateCollationStatementSegment"),
            Ref("CallStoredProcedureSegment"),
            Ref("CreateServerStatementSegment"),
            Ref("CreateUserMappingStatementSegment"),
            Ref("ImportForeignSchemaStatementSegment"),
            Ref("CreateForeignTableStatementSegment"),
            Ref("DropAggregateStatementSegment"),
            Ref("CreateAggregateStatementSegment"),
            Ref("CreateStatisticsStatementSegment"),
            Ref("AlterStatisticsStatementSegment"),
            Ref("DropStatisticsStatementSegment"),
        ],
    )


class CreateTriggerStatementSegment(ansi.CreateTriggerStatementSegment):
    """Create Trigger Statement.

    As Specified in https://www.postgresql.org/docs/14/sql-createtrigger.html
    """

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
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
                        terminators=["OR", "ON"],
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
        Indent,
        "AS",
        Ref("SingleIdentifierGrammar"),
        Dedent,
    )


class OperationClassReferenceSegment(ansi.ObjectReferenceSegment):
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
                            Ref("FunctionSegment"),
                        ),
                        Sequence(
                            "COLLATE",
                            Ref("CollationReferenceSegment"),
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
    Also: https://www.postgresql.org/docs/15/sql-set-role.html (still a VariableSetStmt)
    https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L1584
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
                    "DEFAULT",
                    Delimited(
                        Ref("LiteralGrammar"),
                        Ref("NakedIdentifierSegment"),
                        # https://github.com/postgres/postgres/blob/4380c2509d51febad34e1fac0cfaeb98aaa716c5/src/backend/parser/gram.y#L1810-L1815
                        Ref("OnKeywordAsIdentifierSegment"),
                    ),
                ),
            ),
            Sequence(
                "TIME", "ZONE", OneOf(Ref("QuotedLiteralSegment"), "LOCAL", "DEFAULT")
            ),
            Sequence("SCHEMA", Ref("QuotedLiteralSegment")),
            Sequence("ROLE", OneOf("NONE", Ref("RoleReferenceSegment"))),
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
        Sequence("COLLATE", Ref("CollationReferenceSegment"), optional=True),
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
    Also, RESET ROLE from: https://www.postgresql.org/docs/15/sql-set-role.html
    """

    type = "reset_statement"
    match_grammar = Sequence(
        "RESET",
        OneOf("ALL", "ROLE", Ref("ParameterNameSegment")),
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
        Sequence(Ref.keyword("NOT", optional=True), "MATERIALIZED", optional=True),
        Bracketed(
            Ref("SelectableGrammar"),
            parse_mode=ParseMode.GREEDY,
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
                ),
                parse_mode=ParseMode.GREEDY,
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
                    OneOf(
                        # Potentially a bracketed SELECT
                        Ref("SelectableGrammar"),
                        # Or a delimited list of literals
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
                    Sequence(
                        Ref("ExpressionSegment"),
                        Ref("AliasExpressionSegment", optional=True),
                    ),
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

    https://www.postgresql.org/docs/current/sql-altertype.html
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
                "VALUE",
                Ref("QuotedLiteralSegment"),
                "TO",
                Ref("QuotedLiteralSegment"),
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
                        Ref("CollationReferenceSegment"),
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
                        Ref("CollationReferenceSegment"),
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


class ClusterStatementSegment(BaseSegment):
    """A `CLUSTER` statement.

    https://www.postgresql.org/docs/current/sql-cluster.html
    """

    type = "cluster_statement"
    match_grammar = Sequence(
        "CLUSTER",
        Ref.keyword("VERBOSE", optional=True),
        OneOf(
            Sequence(
                Ref("TableReferenceSegment"),
                Sequence("USING", Ref("IndexReferenceSegment"), optional=True),
            ),
            Sequence(Ref("IndexReferenceSegment"), "ON", Ref("TableReferenceSegment")),
            optional=True,
        ),
    )


class ColumnReferenceSegment(ansi.ObjectReferenceSegment):
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
                    Ref("JoinLikeClauseGrammar"),
                    BracketedSegment,
                ],
                allow_gaps=False,
            ),
            allow_gaps=False,
            optional=True,
        ),
        allow_gaps=False,
    )


class NamedArgumentSegment(BaseSegment):
    """Named argument to a function.

    https://www.postgresql.org/docs/current/sql-syntax-calling-funcs.html#SQL-SYNTAX-CALLING-FUNCS-NAMED
    """

    type = "named_argument"
    match_grammar = Sequence(
        Ref("NakedIdentifierSegment"),
        Ref("RightArrowSegment"),
        Ref("ExpressionSegment"),
    )


class TableExpressionSegment(ansi.TableExpressionSegment):
    """The main table expression e.g. within a FROM clause.

    Override from ANSI to allow optional WITH ORDINALITY clause
    """

    match_grammar: Matchable = OneOf(
        Ref("ValuesClauseSegment"),
        Ref("BareFunctionSegment"),
        Sequence(
            Ref("FunctionSegment"),
            Sequence("WITH", "ORDINALITY", optional=True),
        ),
        Ref("TableReferenceSegment"),
        # Nested Selects
        Bracketed(Ref("SelectableGrammar")),
        Bracketed(Ref("MergeStatementSegment")),
    )


class ServerReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to a server."""

    type = "server_reference"


class CreateServerStatementSegment(BaseSegment):
    """Create server statement.

    https://www.postgresql.org/docs/15/sql-createserver.html
    """

    type = "create_server_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        "SERVER",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ServerReferenceSegment"),
        Sequence("TYPE", Ref("QuotedLiteralSegment"), optional=True),
        Sequence("VERSION", Ref("VersionIdentifierSegment"), optional=True),
        Ref("ForeignDataWrapperGrammar"),
        Ref("ObjectReferenceSegment"),
        Ref("OptionsGrammar", optional=True),
    )


class CreateUserMappingStatementSegment(BaseSegment):
    """Create user mapping statement.

    https://www.postgresql.org/docs/15/sql-createusermapping.html
    """

    type = "create_user_mapping_statement"

    match_grammar: Matchable = Sequence(
        Ref("CreateUserMappingGrammar"),
        Ref("IfNotExistsGrammar", optional=True),
        "FOR",
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("SessionInformationUserFunctionsGrammar"),
            "PUBLIC",
        ),
        "SERVER",
        Ref("ServerReferenceSegment"),
        Ref("OptionsGrammar", optional=True),
    )


class ImportForeignSchemaStatementSegment(BaseSegment):
    """Import foreign schema statement.

    https://www.postgresql.org/docs/15/sql-importforeignschema.html
    """

    type = "import_foreign_schema_statement"

    match_grammar: Matchable = Sequence(
        Ref("ImportForeignSchemaGrammar"),
        Ref("SchemaReferenceSegment"),
        Sequence(
            OneOf(Sequence("LIMIT", "TO"), "EXCEPT"),
            Bracketed(Delimited(Ref("NakedIdentifierFullSegment"))),
            optional=True,
        ),
        "FROM",
        "SERVER",
        Ref("ServerReferenceSegment"),
        "INTO",
        Ref("SchemaReferenceSegment"),
        Ref("OptionsGrammar", optional=True),
    )


class CreateForeignTableStatementSegment(BaseSegment):
    """Create foreign table statement.

    https://www.postgresql.org/docs/current/sql-createforeigntable.html
    """

    type = "create_foreign_table_statement"

    match_grammar: Matchable = OneOf(
        Sequence(
            Ref("CreateForeignTableGrammar"),
            Ref("IfNotExistsGrammar", optional=True),
            Ref("TableReferenceSegment"),
            Bracketed(
                Delimited(
                    OneOf(
                        Sequence(
                            Ref("ColumnReferenceSegment"),
                            Ref("DatatypeSegment"),
                            Ref("OptionsGrammar", optional=True),
                            Sequence(
                                "COLLATE",
                                Ref("CollationReferenceSegment"),
                                optional=True,
                            ),
                            AnyNumberOf(Ref("ForeignTableColumnConstraintSegment")),
                        ),
                        Ref("ForeignTableTableConstraintSegment"),
                    ),
                ),
                optional=True,
            ),
            Sequence(
                "INHERITS",
                Bracketed(Delimited(Ref("TableReferenceSegment"))),
                optional=True,
            ),
            Sequence(
                "SERVER",
                Ref("ServerReferenceSegment"),
            ),
            Ref("OptionsGrammar", optional=True),
        ),
        Sequence(
            Ref("CreateForeignTableGrammar"),
            Ref("IfNotExistsGrammar", optional=True),
            Ref("TableReferenceSegment"),
            Sequence(
                "PARTITION",
                "OF",
                Ref("TableReferenceSegment"),
                Bracketed(
                    Delimited(
                        OneOf(
                            Sequence(
                                Ref("ColumnReferenceSegment"),
                                Sequence("WITH", "OPTIONS", optional=True),
                                AnyNumberOf(Ref("ForeignTableColumnConstraintSegment")),
                            ),
                            Ref("ForeignTableTableConstraintSegment"),
                        )
                    ),
                    optional=True,
                ),
                OneOf(
                    Sequence("FOR", "VALUES", Ref("PartitionBoundSpecSegment")),
                    "DEFAULT",
                ),
            ),
            Sequence(
                "SERVER",
                Ref("ServerReferenceSegment"),
            ),
            Ref("OptionsGrammar", optional=True),
        ),
    )


class OverlapsClauseSegment(ansi.OverlapsClauseSegment):
    """An `OVERLAPS` clause.

    https://www.postgresql.org/docs/current/functions-datetime.html
    """

    match_grammar: Matchable = Sequence(
        OneOf(
            Sequence(
                Bracketed(
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        Ref("DateTimeLiteralGrammar"),
                        Ref("ShorthandCastSegment"),
                    ),
                    Ref("CommaSegment"),
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        Ref("DateTimeLiteralGrammar"),
                        Ref("ShorthandCastSegment"),
                    ),
                )
            ),
            Ref("ColumnReferenceSegment"),
        ),
        "OVERLAPS",
        OneOf(
            Sequence(
                Bracketed(
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        Ref("DateTimeLiteralGrammar"),
                        Ref("ShorthandCastSegment"),
                    ),
                    Ref("CommaSegment"),
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        Ref("DateTimeLiteralGrammar"),
                        Ref("ShorthandCastSegment"),
                    ),
                )
            ),
            Ref("ColumnReferenceSegment"),
        ),
    )
