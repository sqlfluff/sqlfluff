"""The Db2 dialect.

https://www.ibm.com/docs/en/i/7.4?topic=overview-db2-i
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    BaseSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
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
    WordSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi
from sqlfluff.dialects.dialect_db2_keywords import UNRESERVED_KEYWORDS

ansi_dialect = load_raw_dialect("ansi")

db2_dialect = ansi_dialect.copy_as("db2")
db2_dialect.sets("reserved_keywords").remove("NATURAL")
db2_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)


db2_dialect.replace(
    # Db2 allows # in field names, and doesn't use it as a comment
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z0-9_#]*[A-Z#][A-Z0-9_#]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("ExpressionSegment"),
        Ref("NamedArgumentSegment"),
    ),
    ConditionalCrossJoinKeywordsGrammar=Nothing(),
    NaturalJoinKeywordsGrammar=Nothing(),
    UnconditionalCrossJoinKeywordsGrammar=Ref.keyword("CROSS"),
    PreTableFunctionKeywordsGrammar=OneOf("LATERAL"),
    PostFunctionGrammar=OneOf(
        Ref("OverClauseSegment"),
        Ref("WithinGroupClauseSegment"),
    ),
    FromClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "FromClauseTerminatorGrammar"
    ).copy(
        insert=[Ref.keyword("OFFSET")],
    ),
    WhereClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "WhereClauseTerminatorGrammar"
    ).copy(
        insert=[Ref.keyword("OFFSET")],
    ),
    GroupByClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "GroupByClauseTerminatorGrammar"
    ).copy(
        insert=[Ref.keyword("OFFSET")],
    ),
    HavingClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "HavingClauseTerminatorGrammar"
    ).copy(
        insert=[Ref.keyword("OFFSET")],
    ),
    OrderByClauseTerminators=ansi_dialect.get_grammar("OrderByClauseTerminators").copy(
        insert=[Ref.keyword("OFFSET")],
    ),
    Expression_C_Grammar=OneOf(
        Sequence("EXISTS", Bracketed(Ref("SelectableGrammar"))),
        # should be first priority, otherwise EXISTS() would be matched as a function
        Sequence(
            OneOf(
                Ref("Expression_D_Grammar"),
                Ref("CaseExpressionSegment"),
            ),
            AnyNumberOf(Ref("TimeZoneGrammar")),
        ),
        Ref("ShorthandCastSegment"),
        Ref("LabeledDurationGrammar"),
    ),
    BracketedSetExpressionGrammar=Bracketed(Ref("SetExpressionSegment")),
)


db2_dialect.insert_lexer_matchers(
    [
        StringLexer("right_arrow", "=>", CodeSegment),
    ],
    before="equals",
)

db2_dialect.patch_lexer_matchers(
    [
        # Patching comments to remove hash comments
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--")},
        ),
        # In Db2, the only escape character is ' for single quote strings
        RegexLexer(
            "single_quote",
            r"(?s)('')+?(?!')|('.*?(?<!')(?:'')*'(?!'))",
            CodeSegment,
        ),
        # In Db2, there is no escape character for double quote strings
        RegexLexer(
            "double_quote",
            r'(?s)".+?"',
            CodeSegment,
        ),
        # In Db2, a field could have a # pound/hash sign
        RegexLexer("word", r"[0-9a-zA-Z_#]+", WordSegment),
    ]
)

db2_dialect.add(
    RightArrowSegment=StringParser("=>", SymbolSegment, type="right_arrow"),
    # https://www.ibm.com/docs/en/db2/11.5?topic=expressions-datetime-operations-durations
    LabeledDurationGrammar=Sequence(
        OneOf(
            Ref("LiteralGrammar"),
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Ref("ColumnReferenceSegment"),
            Ref("Expression_D_Grammar"),
        ),
        OneOf(
            "DAY",
            "DAYS",
            "HOUR",
            "HOURS",
            "MICROSECOND",
            "MICROSECONDS",
            "MINUTE",
            "MINUTES",
            "MONTH",
            "MONTHS",
            "SECOND",
            "SECONDS",
            "YEAR",
            "YEARS",
        ),
    ),
    # https://www.ibm.com/docs/en/db2/11.5?topic=elements-special-registers
    SpecialRegisterGrammar=OneOf(
        "CURRENT_DATE",
        "CURRENT_PATH",
        "CURRENT_SCHEMA",
        "CURRENT_SERVER",
        "CURRENT_TIME",
        "CURRENT_TIMESTAMP",
        "CURRENT_TIMEZONE",
        "CURRENT_USER",
        "SESSION_USER",
        "SYSTEM_USER",
        "USER",
        Sequence(
            "CURRENT",
            OneOf(
                "CLIENT_ACCTNG",
                "CLIENT_APPLNAME",
                "CLIENT_USERID",
                "CLIENT_WRKSTNNAME",
                "DATE",
                "DBPARTITIONNUM",
                Sequence("DECFLOAT", "ROUNDING", "MODE"),
                Sequence("DEFAULT", "TRANSFORM", "GROUP"),
                "DEGREE",
                Sequence("EXPLAIN", OneOf("MODE", "SNAPSHOT")),
                Sequence("FEDERATED", "ASYNCHRONY"),
                Sequence("IMPLICIT", "XMLPARSE", "OPTION"),
                "ISOLATION",
                Sequence("LOCALE", OneOf("LC_MESSAGES", "LC_TIME")),
                Sequence("LOCK", "TIMEOUT"),
                Sequence("MAINTAINED", "TABLE", "TYPES", "FOR", "OPTIMIZATION"),
                Sequence("MDC", "ROLLOUT", "MODE"),
                "MEMBER",
                Sequence("OPTIMIZATION", "PROFILE"),
                Sequence("PACKAGE", "PATH"),
                "PATH",
                Sequence("QUERY", "OPTIMIZATION"),
                Sequence("REFRESH", "AGE"),
                "SCHEMA",
                "SERVER",
                "SQL_CCFLAGS",
                Sequence("TEMPORAL", OneOf("BUSINESS_TIME", "SYSTEM_TIME")),
                "TIME",
                "TIMESTAMP",
                "TIMEZONE",
                "USER",
            ),
        ),
    ),
)


class BareFunctionSegment(BaseSegment):
    """A function that can be called without parenthesis per ANSI specification.

    DB2 extends this to include `special registers`.
    """

    type = "bare_function"
    match_grammar = Ref("SpecialRegisterGrammar")


class CallStoredProcedureSegment(BaseSegment):
    """This is a CALL statement used to execute a stored procedure.

    https://www.ibm.com/docs/en/db2/11.5?topic=statements-call
    """

    type = "call_segment"

    match_grammar = Sequence(
        "CALL",
        OneOf(
            Ref("FunctionSegment"),
            # Call without parenthesis
            Ref("FunctionNameSegment", reset_terminators=True),
        ),
    )


class CopyOptionsSegment(BaseSegment):
    """Copy-options when using like or as for creating a table.

    https://www.ibm.com/docs/en/db2/11.5?topic=statements-create-table#sdx-synid_frag-copy-options
    """

    type = "copy_options"

    match_grammar = AnySetOf(
        Sequence(
            OneOf("INCLUDING", "EXCLUDING"),
            Ref.keyword("COLUMN", optional=True),
            "DEFAULTS",
        ),
        Sequence(
            OneOf("INCLUDING", "EXCLUDING"),
            "IDENTITY",
            Sequence(
                "COLUMN",
                "ATTRIBUTES",
                optional=True,
            ),
        ),
    )


class DeclareGlobalTempTableSegment(BaseSegment):
    """DECLARE GLOBAL TEMPORARY TABLE statement.

    https://www.ibm.com/docs/en/db2/11.5?topic=statements-declare-global-temporary-table
    """

    type = "declare_temp_table"

    match_grammar = Sequence(
        "DECLARE",
        "GLOBAL",
        "TEMPORARY",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        Ref("ColumnDefinitionSegment"),
                    ),
                )
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
                Ref("WithDataClauseSegment"),
                Ref("CopyOptionsSegment", optional=True),
            ),
            # Create like syntax
            Sequence(
                "LIKE",
                Ref("TableReferenceSegment"),
                Ref("CopyOptionsSegment", optional=True),
            ),
        ),
        AnySetOf(
            Sequence(
                "ORGANIZE",
                "BY",
                OneOf("ROW", "COLUMN"),
            ),
            OneOf(
                Sequence(
                    "ON",
                    "COMMIT",
                    OneOf("DELETE", "PRESERVE"),
                    "ROWS",
                ),
            ),
            OneOf(
                "LOGGED",
                Sequence(
                    "NOT",
                    "LOGGED",
                    Sequence(
                        "ON",
                        "ROLLBACK",
                        OneOf("DELETE", "PRESERVE"),
                        "ROWS",
                        optional=True,
                    ),
                ),
            ),
            Sequence(
                "WITH",
                "REPLACE",
            ),
            Sequence(
                "IN",
                Ref("TablespaceReferenceSegment"),
            ),
            Ref("DeclareDistributionClauseSegment"),
        ),
    )


class DeclareDistributionClauseSegment(BaseSegment):
    """Distribution clause in declaring table creation.

    https://www.ibm.com/docs/en/db2/11.5?topic=statements-declare-global-temporary-table#sdx-synid_frag-distribution-clause
    """

    type = "distribution_clause"
    match_grammar = Sequence(
        "DISTRIBUTE",
        OneOf("BY", "ON"),
        OneOf(
            Sequence(
                Ref.keyword("HASH", optional=True),
                Bracketed(
                    Delimited(
                        Ref("ColumnReferenceSegment"),
                    ),
                ),
            ),
            "RANDOM",
        ),
    )


class NamedArgumentSegment(BaseSegment):
    """Named argument to a function.

    https://www.ibm.com/docs/en/db2/11.5?topic=statements-call
    """

    type = "named_argument"
    match_grammar = Sequence(
        Ref("NakedIdentifierSegment"),
        Ref("RightArrowSegment"),
        Ref("ExpressionSegment"),
    )


class OffsetClauseSegment(BaseSegment):
    """OFFSET clause in as SELECT statement."""

    type = "offset_clause"

    match_grammar = Sequence(
        "OFFSET",
        OneOf(
            Ref("NumericLiteralSegment"),
            Ref("ExpressionSegment"),
        ),
        OneOf("ROW", "ROWS"),
    )


class LimitClauseSegment(BaseSegment):
    """A `LIMIT` clause like in `SELECT`."""

    type = "limit_clause"
    match_grammar = OneOf(
        Sequence(
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
        ),
        Sequence(
            Ref("OffsetClauseSegment", optional=True),
            Ref("FetchClauseSegment", optional=True),
        ),
    )


class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions."""

    type = "withingroup_clause"

    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(
            Ref("OrderByClauseSegment", optional=True), parse_mode=ParseMode.GREEDY
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """An element in the targets of a select statement."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CallStoredProcedureSegment"),
            Ref("DeclareGlobalTempTableSegment"),
        ]
    )


class ValuesClauseSegment(ansi.ValuesClauseSegment):
    """A `VALUES` clause like in `INSERT` or as a standalone statement.

    https://www.ibm.com/docs/en/db2/11.5?topic=queries-fullselect#sdx-synid_frag-values-clause
    """

    type = "values_clause"
    match_grammar = Sequence(
        "VALUES",
        Delimited(
            Bracketed(
                Delimited(
                    "DEFAULT",
                    Ref("ExpressionSegment"),
                ),
                parse_mode=ParseMode.GREEDY,
            ),
            "DEFAULT",
            Ref("ExpressionSegment"),
        ),
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
    )
