"""The Oracle dialect.

This inherits from the ansi dialect.
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
    CommentSegment,
    CompositeComparisonOperatorSegment,
    Conditional,
    Dedent,
    Delimited,
    IdentifierSegment,
    ImplicitIndent,
    Indent,
    LiteralSegment,
    Matchable,
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
    WordSegment,
)
from sqlfluff.dialects import dialect_ansi as ansi

ansi_dialect = load_raw_dialect("ansi")
oracle_dialect = ansi_dialect.copy_as(
    "oracle",
    formatted_name="Oracle",
    docstring="""The dialect for `Oracle`_ SQL. Note: this does include PL/SQL.

.. _`Oracle`: https://www.oracle.com/database/technologies/appdev/sql.html""",
)

oracle_dialect.sets("reserved_keywords").update(
    [
        "ACCESS",
        "ADD",
        "ALL",
        "ALTER",
        "AND",
        "ANY",
        "AS",
        "ASC",
        "AUDIT",
        "BETWEEN",
        "BY",
        "CHAR",
        "CHECK",
        "CLUSTER",
        "COLUMN",
        "COLUMN_VALUE",
        "COMMENT",
        "COMPRESS",
        "CONNECT",
        "CONNECT_BY_ROOT",
        "CONSTRAINT",
        "CREATE",
        "CURRENT",
        "DATE",
        "DECIMAL",
        "DEFAULT",
        "DEFINITION",
        "DELETE",
        "DELETING",
        "DESC",
        "DISABLE",
        "DISTINCT",
        "DROP",
        "ELSE",
        "ENABLE",
        "EXCLUSIVE",
        "EXISTS",
        "EXECUTE",
        "FILE",
        "FLOAT",
        "FOR",
        "FORCE",
        "FROM",
        "GRANT",
        "GROUP",
        "HAVING",
        "IDENTIFIED",
        "IMMEDIATE",
        "IN",
        "INCREMENT",
        "INDEX",
        "INDEXTYPE",
        "INITIAL",
        "INSERT",
        "INSERTING",
        "INTEGER",
        "INTERSECT",
        "INTO",
        "INVISIBLE",
        "IS",
        "LEVEL",
        "LIKE",
        "LOCK",
        "LOGGING",
        "LONG",
        "LOOP",
        "MAXEXTENTS",
        "MINUS",
        "MLSLABEL",
        "MODE",
        "MODIFY",
        "MONITORING",
        "NESTED_TABLE_ID",
        "NOAUDIT",
        "NOCOMPRESS",
        "NOLOGGING",
        "NOMONITORING",
        "NOREVERSE",
        "NOT",
        "NOWAIT",
        "NULL",
        "NUMBER",
        "OF",
        "OFFLINE",
        "ON",
        "ONLINE",
        "OPTION",
        "OR",
        "ORDER",
        "OVERFLOW",
        "PARAMETERS",
        "PCTFREE",
        "PIVOT",
        "PRIOR",
        "PRIVATE",
        "PROMPT",
        "PUBLIC",
        "RAW",
        "REBUILD",
        "RENAME",
        "RESOURCE",
        "REVOKE",
        "REVERSE",
        "ROW",
        "ROWID",
        "ROWNUM",
        "ROWS",
        "SELECT",
        "SESSION",
        "SET",
        "SHARE",
        "SIBLINGS",
        "SIZE",
        "SMALLINT",
        "START",
        "SUCCESSFUL",
        "SYNONYM",
        "SYSDATE",
        "TABLE",
        "THEN",
        "TO",
        "TRIGGER",
        "UID",
        "UNION",
        "UNIQUE",
        "UNPIVOT",
        "UNUSABLE",
        "UPDATE",
        "UPDATING",
        "USER",
        "VALIDATE",
        "VALUES",
        "VARCHAR",
        "VARCHAR2",
        "VIEW",
        "VISIBLE",
        "WHEN",
        "WHENEVER",
        "WHERE",
        "WITH",
    ]
)

oracle_dialect.sets("unreserved_keywords").update(
    [
        "ABSENT",
        "ACCESSIBLE",
        "ADMINISTER",
        "ADVISOR",
        "ANALYTIC",
        "ARCHIVE",
        "AUTHENTICATED",
        "AUTHID",
        "BECOME",
        "BODY",
        "BULK",
        "BULK_EXCEPTIONS",
        "BULK_ROWCOUNT",
        "BYTE",
        "COLLECT",
        "COMPILE",
        "COMPOUND",
        "CONSTANT",
        "CONTAINER",
        "CONTEXT",
        "CROSSEDITION",
        "CURSOR",
        "DBA_RECYCLEBIN",
        "DEBUG",
        "DELEGATE",
        "DIGEST",
        "DIMENSION",
        "DIRECTIVE",
        "DIRECTORIES",
        "DIRECTORY",
        "EDITION",
        "EDITIONABLE",
        "EDITIONING",
        "EDITIONS",
        "ELSIF",
        "EMPTY",
        "ERROR",
        "ERRORS",
        "EXEMPT",
        "EXPIRE",
        "EXTERNALLY",
        "FINE",
        "FLASHBACK",
        "FOLLOWS",
        "FORALL",
        "GLOBALLY",
        "HIERARCHY",
        "HTTP",
        "INDICES",
        "INHERITANY",
        "ISOPEN",
        "JAVA",
        "JOB",
        "KEEP",
        "LIBRARY",
        "LINK",
        "LOCKDOWN",
        "LOG",
        "LOGMINING",
        "LOOP",
        "MEASURE",
        "MINING",
        "MUTABLE",
        "NESTED",
        "NEXTVAL",
        "NOCOPY",
        "NOMAXVALUE",
        "NOMINVALUE",
        "NONEDITIONABLE",
        "NOTFOUND",
        "OID",
        "OUTLINE",
        "PACKAGE",
        "PAIRS",
        "PARALLEL_ENABLE",
        "PARENT",
        "PERSISTABLE",
        "PIPELINED",
        "PLUGGABLE",
        "POLYMORPHIC",
        "PRAGMA",
        "PRECEDES",
        "PRIVILEGE",
        "PROFILE",
        "PROGRAM",
        "PROPERTY",
        "QUERY",
        "QUOTA",
        "RAISE",
        "RECORD",
        "REDACTION",
        "REDEFINE",
        "REFRESH",
        "REJECT",
        "RELIES_ON",
        "REMOTE",
        "RESTRICTED",
        "RESULT_CACHE",
        "RESUMABLE",
        "RETURNING",
        "REUSE",
        "REVERSE",
        "REWRITE",
        "ROWTYPE",
        "SCHEDULER",
        "SHARD_ENABLE",
        "SHARED",
        "SHARING",
        "SIGN",
        "SPECIFICATION",
        "SQL_MACRO",
        "SYSGUID",
        "UNLIMITED",
        "VARRAY",
    ]
)

oracle_dialect.sets("bare_functions").clear()
oracle_dialect.sets("bare_functions").update(
    [
        "column_value",
        "current_date",
        "current_timestamp",
        "dbtimezone",
        "localtimestamp",
        "sessiontimestamp",
        "sysdate",
        "systimestamp",
    ]
)


oracle_dialect.patch_lexer_matchers(
    [
        RegexLexer("word", r"[\p{L}][\p{L}\p{N}_$#]*", WordSegment),
        RegexLexer(
            "single_quote",
            r"'([^'\\]|\\|\\.|'')*'",
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r"'((?:[^'\\]|\\|\\.|'')*)'", 1),
                "escape_replacements": [(r"''", "'")],
            },
        ),
        RegexLexer(
            "double_quote",
            r'"([^"]|"")*"',
            CodeSegment,
            segment_kwargs={
                "quoted_value": (r'"((?:[^"]|"")*)"', 1),
                "escape_replacements": [(r'""', '"')],
            },
        ),
        RegexLexer(
            "numeric_literal",
            r"(?>\d+\.\d+|\d+\.(?![\.\w])|\d+)(\.?[eE][+-]?\d+)?((?<!\.)|(?=\b))",
            LiteralSegment,
        ),
    ]
)

oracle_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "prompt_command",
            r"PROMPT([^(\r\n)])*((?=\n)|(?=\r\n))?",
            CommentSegment,
        ),
        StringLexer("at_sign", "@", CodeSegment),
    ],
    before="word",
)

oracle_dialect.insert_lexer_matchers(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [
        StringLexer("right_arrow", "=>", CodeSegment),
        StringLexer("assignment_operator", ":=", CodeSegment),
    ],
    before="equals",
)

oracle_dialect.insert_lexer_matchers(
    [
        StringLexer("power_operator", "**", CodeSegment),
    ],
    before="star",
)

oracle_dialect.add(
    SequenceNextValGrammar=Sequence(
        Ref("NakedIdentifierSegment"),
        Ref("DotSegment"),
        "NEXTVAL",
        allow_gaps=False,
    ),
    AtSignSegment=StringParser("@", SymbolSegment, type="at_sign"),
    RightArrowSegment=StringParser("=>", SymbolSegment, type="right_arrow"),
    AssignmentOperatorSegment=StringParser(
        ":=", SymbolSegment, type="assignment_operator"
    ),
    PowerOperatorSegment=StringParser("**", SymbolSegment, type="binary_operator"),
    ModOperatorSegment=StringParser("MOD", WordSegment, type="binary_operator"),
    OnCommitGrammar=Sequence(
        "ON",
        "COMMIT",
        OneOf(
            Sequence(OneOf("DROP", "PRESERVE"), Ref.keyword("DEFINITION")),
            Sequence(OneOf("DELETE", "PRESERVE"), Ref.keyword("ROWS")),
        ),
    ),
    ConnectByRootGrammar=Sequence("CONNECT_BY_ROOT", Ref("NakedIdentifierSegment")),
    PlusJoinSegment=Bracketed(
        StringParser("+", SymbolSegment, type="plus_join_symbol")
    ),
    PlusJoinGrammar=OneOf(
        Sequence(
            OneOf(Ref("ColumnReferenceSegment"), Ref("FunctionSegment")),
            Ref("EqualsSegment"),
            Ref("ColumnReferenceSegment"),
            Ref("PlusJoinSegment"),
        ),
        Sequence(
            Ref("ColumnReferenceSegment"),
            Ref("PlusJoinSegment"),
            Ref("EqualsSegment"),
            OneOf(Ref("ColumnReferenceSegment"), Ref("FunctionSegment")),
        ),
    ),
    IntervalUnitsGrammar=OneOf("YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND"),
    TriggerCorrelationReferenceSegment=Ref("TriggerCorrelationReferenceSegment"),
    PivotForInGrammar=Sequence(
        "FOR",
        OptionallyBracketed(Delimited(Ref("ColumnReferenceSegment"))),
        "IN",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("Expression_D_Grammar"),
                    Ref("AliasExpressionSegment", optional=True),
                )
            )
        ),
    ),
    UnpivotNullsGrammar=Sequence(OneOf("INCLUDE", "EXCLUDE"), "NULLS"),
    StatementAndDelimiterGrammar=Sequence(
        Ref("StatementSegment"),
        Ref("DelimiterGrammar", optional=True),
    ),
    OneOrMoreStatementsGrammar=AnyNumberOf(
        Ref("StatementAndDelimiterGrammar"),
        min_times=1,
    ),
    TimingPointGrammar=Sequence(
        OneOf("BEFORE", "AFTER", Sequence("INSTEAD", "OF")),
        OneOf("STATEMENT", Sequence("EACH", "ROW")),
    ),
    SharingClauseGrammar=Sequence("SHARING", OneOf("METADATA", "NONE"), optional=True),
    DefaultCollationClauseGrammar=Sequence(
        "DEFAULT", "COLLATION", Ref("NakedIdentifierSegment"), optional=True
    ),
    InvokerRightsClauseGrammar=Sequence("AUTHID", OneOf("CURRENT_USER", "DEFINER")),
    AccessibleByClauseGrammar=Sequence(
        "ACCESSIBLE",
        "BY",
        Delimited(
            Bracketed(
                Sequence(
                    OneOf(
                        "FUNCTION",
                        "PROCEDURE",
                        "PACKAGE",
                        "TRIGGER",
                        "TYPE",
                        optional=True,
                    ),
                    Ref("FunctionNameSegment"),
                )
            )
        ),
    ),
    DmlGrammar=OneOf(
        "DELETE",
        "INSERT",
        Sequence(
            "UPDATE",
            Sequence("OF", Delimited(Ref("ColumnReferenceSegment")), optional=True),
        ),
    ),
    IterationBoundsGrammar=OneOf(
        Ref("NumericLiteralSegment"),
        Ref("SingleIdentifierGrammar"),
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            Ref("SingleIdentifierGrammar"),
        ),
    ),
    IterationSteppedControlGrammar=Sequence(
        Ref("IterationBoundsGrammar"),
        Ref("DotSegment"),
        Ref("DotSegment"),
        Ref("IterationBoundsGrammar"),
        Sequence("BY", "STEP", optional=True),
    ),
    ParallelEnableClauseGrammar=Sequence(
        "PARALLEL_ENABLE",
        Sequence(
            Bracketed(
                "PARTITION",
                Ref("SingleIdentifierGrammar"),
                "BY",
                OneOf(
                    "ANY",
                    Sequence(
                        OneOf("HASH", "RANGE"),
                        Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                        Sequence(
                            OneOf("ORDER", "CLUSTER"),
                            Ref("ExpressionSegment"),
                            "BY",
                            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
                            optional=True,
                        ),
                    ),
                    Sequence("VALUE", Bracketed(Ref("ColumnReferenceSegment"))),
                ),
            ),
            optional=True,
        ),
    ),
    ResultCacheClauseGrammar=Sequence(
        "RESULT_CACHE",
        Sequence(
            "RELIES_ON",
            Bracketed(Delimited(Ref("SingleIdentifierGrammar"))),
            optional=True,
        ),
    ),
    PipelinedClauseGrammar=Sequence(
        "PIPELINED",
        OneOf(
            Sequence("USING", Ref("ObjectReferenceSegment"), optional=True),
            Sequence(
                OneOf("ROW", "TABLE"),
                "POLYMORPHIC",
                Sequence("USING", Ref("ObjectReferenceSegment"), optional=True),
            ),
        ),
    ),
    ElementSpecificationGrammar=Sequence(
        AnyNumberOf(
            Sequence(
                Ref.keyword("NOT"),
                OneOf("OVERRIDING", "FINAL", "INSTANTIABLE"),
            ),
            optional=True,
        ),
        AnyNumberOf(
            Sequence(
                OneOf("MEMBER", "STATIC"),
                OneOf(
                    Ref("CreateFunctionStatementSegment"),
                    Ref("CreateProcedureStatementSegment"),
                ),
            )
        ),
    ),
    ImplicitCursorAttributesGrammar=Sequence(
        Ref("SingleIdentifierGrammar"),
        Ref("ModuloSegment"),
        OneOf(
            "ISOPEN",
            "FOUND",
            "NOTFOUND",
            "ROWCOUNT",
            "BULK_ROWCOUNT",
            "BULK_EXCEPTIONS",
        ),
    ),
    ObjectTypeAndSubtypeDefGrammar=Sequence(
        OneOf("OBJECT", Sequence("UNDER", Ref("ObjectReferenceSegment"))),
        Bracketed(
            Delimited(
                OneOf(
                    Sequence(
                        Ref("SingleIdentifierGrammar"),
                        Ref("DatatypeSegment"),
                    ),
                    Ref("ElementSpecificationGrammar"),
                )
            ),
            optional=True,
        ),
        AnyNumberOf(
            Sequence(
                Ref.keyword("NOT", optional=True),
                OneOf("FINAL", "INSTANTIABLE", "PERSISTABLE"),
            ),
            optional=True,
        ),
    ),
    VarrayAndNestedTypeSpecGrammar=Sequence(
        OneOf(
            Sequence(
                OneOf(
                    "VARRAY",
                    Sequence(Ref.keyword("VARYING", optional=True), "ARRAY"),
                ),
                Bracketed(Ref("NumericLiteralSegment")),
            ),
            "TABLE",
        ),
        "OF",
        OneOf(
            Sequence(
                Ref("StartBracketSegment", optional=True),
                Ref("DatatypeSegment"),
                Sequence("NOT", "NULL", optional=True),
                Ref("EndBracketSegment", optional=True),
            ),
            Sequence(
                Bracketed(
                    Sequence(
                        Ref("DatatypeSegment"),
                        Sequence("NOT", "NULL", optional=True),
                    )
                ),
                Ref.keyword("NOT", optional=True),
                Ref.keyword("PERSISTABLE", optional=True),
            ),
        ),
    ),
    ForUpdateGrammar=Sequence(
        "FOR", "UPDATE", Sequence("OF", Ref("TableReferenceSegment"), optional=True)
    ),
    CompileClauseGrammar=Sequence(
        "COMPILE",
        Ref.keyword("DEBUG", optional=True),
        OneOf("PACKAGE", "SPECIFICATION", "BODY", optional=True),
        Delimited(
            Ref("ParameterNameSegment"),
            Ref("EqualsSegment"),
            Ref("NakedIdentifierSegment"),
            optional=True,
        ),
        Sequence("REUSE", "SETTINGS", optional=True),
    ),
    IdentityClauseGrammar=Sequence(
        "GENERATED",
        OneOf(
            "ALWAYS",
            Sequence(
                "BY",
                "DEFAULT",
                Sequence(
                    "ON",
                    "NULL",
                    Sequence(
                        "FOR",
                        "INSERT",
                        OneOf("ONLY", Sequence("AND", "UPDATE")),
                        optional=True,
                    ),
                    optional=True,
                ),
            ),
            optional=True,
        ),
        "AS",
        "IDENTITY",
        Bracketed(Ref("IdentityOptionsGrammar"), optional=True),
    ),
    IdentityOptionsGrammar=AnyNumberOf(
        Sequence(
            OneOf(
                Sequence("START", "WITH"),
                Sequence("INCREMENT", "BY"),
                "MAXVALUE",
                "MINVALUE",
                "CACHE",
            ),
            Ref("NumericLiteralSegment"),
            Sequence("LIMIT", "VALUE", optional=True),
        ),
        "NOMAXVALUE",
        "NOMINVALUE",
        "CYCLE",
        "NOCYCLE",
        "NOCACHE",
        "ORDER",
        "NOORDER",
    ),
    SizeClauseGrammar=Sequence(
        Ref("NumericLiteralSegment"),
        RegexParser(r"[KMGTPE]?", LiteralSegment, type="size_prefix"),
    ),
    TriggerPredicatesGrammar=OneOf(
        "INSERTING",
        Sequence("UPDATING", Bracketed(Ref("QuotedLiteralSegment"), optional=True)),
        "DELETING",
    ),
    JSONObjectContentSegment=Sequence(
        OneOf(Ref("StarSegment"), Delimited(Ref("JSONEntrySegment")), optional=True),
        Ref("JSONOnNullClause", optional=True),
        Ref("JSONReturningClause", optional=True),
        Ref.keyword("STRICT", optional=True),
        Sequence("WITH", "UNIQUE", "KEYS", optional=True),
    ),
    JSONEntrySegment=OneOf(
        Sequence(
            Ref("JSONRegularEntrySegment"),
            Sequence("FORMAT", "JSON", optional=True),
        ),
        Ref("WildcardIdentifierSegment"),
    ),
    JSONRegularEntrySegment=Sequence(
        OneOf(
            Sequence(
                Ref.keyword("KEY", optional=True),
                Ref("QuotedLiteralSegment"),
                "VALUE",
                Ref("ExpressionSegment"),
            ),
            Sequence(
                Ref("ExpressionSegment"),
                Sequence(Ref("ColonSegment"), Ref("ExpressionSegment"), optional=True),
            ),
            Ref("ColumnReferenceSegment"),
        )
    ),
    JSONOnNullClause=Sequence(OneOf("NULL", "ABSENT"), "ON", "NULL"),
    JSONReturningClause=Sequence(
        "RETURNING",
        OneOf(
            Sequence(
                "VARCHAR",
                Bracketed(
                    Sequence(
                        Ref("NumericLiteralSegment"),
                        OneOf("BYTE", "CHAR", optional=True),
                    ),
                    optional=True,
                ),
                Sequence("WITH", "TYPENAME", optional=True),
            ),
            Sequence(
                OneOf("CLOB", "BLOB"), Ref("SingleIdentifierGrammar", optional=True)
            ),
            "JSON",
        ),
    ),
    DBLinkAuthenticationGrammar=OneOf(
        Sequence(
            "AUTHENTICATED",
            "BY",
            Ref("RoleReferenceSegment"),
            "IDENTIFIED",
            "BY",
            Ref("SingleIdentifierGrammar"),
        ),
        Sequence("WITH", "CREDENTIAL"),
    ),
    BatchDelimiterGrammar=Ref("SlashBufferExecutorSegment"),
)

oracle_dialect.replace(
    ColumnConstraintDefaultGrammar=OneOf(
        ansi_dialect.get_grammar("ColumnConstraintDefaultGrammar"),
        Ref("SequenceNextValGrammar"),
    ),
    # https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/DROP-TABLE.html
    DropBehaviorGrammar=Sequence(
        Sequence(
            "CASCADE",
            "CONSTRAINTS",
            optional=True,
        ),
        Ref.keyword("PURGE", optional=True),
        optional=True,
    ),
    NakedIdentifierSegment=SegmentGenerator(
        lambda dialect: RegexParser(
            r"[\p{L}\p{N}_]*[\p{L}][\p{L}\p{N}_#$]*",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^("
            + r"|".join(sorted(dialect.sets("reserved_keywords")))
            + r")$",
            casefold=str.upper,
        )
    ),
    PostFunctionGrammar=AnyNumberOf(
        Ref("WithinGroupClauseSegment"),
        Ref("FilterClauseGrammar"),
        Ref("OverClauseSegment", optional=True),
    ),
    FunctionContentsExpressionGrammar=OneOf(
        Ref("ExpressionSegment"),
        Ref("NamedArgumentSegment"),
    ),
    FunctionContentsGrammar=ansi_dialect.get_grammar("FunctionContentsGrammar").copy(
        insert=[Ref("ListaggOverflowClauseSegment"), Ref("JSONObjectContentSegment")]
    ),
    TemporaryGrammar=Sequence(
        OneOf("GLOBAL", "PRIVATE"),
        Ref.keyword("TEMPORARY"),
        optional=True,
    ),
    ParameterNameSegment=RegexParser(
        r'[A-Z_][A-Z0-9_$]*|"[^"]*"', CodeSegment, type="parameter"
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("TriggerCorrelationReferenceSegment"),
            Ref("SqlplusVariableGrammar"),
            Ref.keyword("LEVEL"),
            Ref.keyword("ROWNUM"),
            Ref.keyword("ANY"),
        ],
        before=Ref("ArrayLiteralSegment"),
    ),
    BaseExpressionElementGrammar=ansi_dialect.get_grammar(
        "BaseExpressionElementGrammar"
    ).copy(
        insert=[
            Ref("ConnectByRootGrammar"),
            Ref("SqlplusSubstitutionVariableSegment"),
        ]
    ),
    Expression_D_Grammar=Sequence(
        OneOf(
            Ref("PlusJoinGrammar"),
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Ref("TriggerCorrelationReferenceSegment"),
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
            Ref("SqlplusSubstitutionVariableSegment"),
            Ref("ImplicitCursorAttributesGrammar"),
            Sequence(
                Ref("ObjectReferenceSegment"),
                Bracketed(
                    OneOf(
                        Ref("ObjectReferenceSegment"),
                        Ref("SingleQuotedIdentifierSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                    optional=True,
                ),
                Ref("DotSegment", optional=True),
            ),
            terminators=[Ref("CommaSegment")],
        ),
        Ref("AccessorGrammar", optional=True),
        allow_gaps=True,
    ),
    DateTimeLiteralGrammar=Sequence(
        OneOf("DATE", "TIME", "TIMESTAMP", "INTERVAL"),
        TypedParser("single_quote", LiteralSegment, type="date_constructor_literal"),
        Sequence(
            Ref("IntervalUnitsGrammar"),
            Sequence("TO", Ref("IntervalUnitsGrammar"), optional=True),
        ),
    ),
    PreTableFunctionKeywordsGrammar=OneOf("LATERAL"),
    ConditionalCrossJoinKeywordsGrammar=Nothing(),
    UnconditionalCrossJoinKeywordsGrammar=Ref.keyword("CROSS"),
    SingleIdentifierGrammar=ansi_dialect.get_grammar("SingleIdentifierGrammar").copy(
        insert=[
            Ref("SqlplusSubstitutionVariableSegment"),
        ]
    ),
    SequenceMinValueGrammar=OneOf(
        Sequence("MINVALUE", Ref("NumericLiteralSegment")),
        "NOMINVALUE",
    ),
    SequenceMaxValueGrammar=OneOf(
        Sequence("MAXVALUE", Ref("NumericLiteralSegment")),
        "NOMAXVALUE",
    ),
    FunctionParameterGrammar=Sequence(
        Ref("ParameterNameSegment"),
        OneOf(
            Sequence(
                Ref.keyword("IN", optional=True),
                OneOf(
                    Ref("DatatypeSegment"),
                    Ref("ColumnTypeReferenceSegment"),
                    Ref("RowTypeReferenceSegment"),
                ),
                Sequence(
                    OneOf(Ref("AssignmentOperatorSegment"), "DEFAULT"),
                    Ref("ExpressionSegment"),
                    optional=True,
                ),
            ),
            Sequence(
                Ref.keyword("IN", optional=True),
                "OUT",
                Ref.keyword("NOCOPY", optional=True),
                OneOf(
                    Ref("DatatypeSegment"),
                    Ref("ColumnTypeReferenceSegment"),
                    Ref("RowTypeReferenceSegment"),
                ),
            ),
        ),
    ),
    ArithmeticBinaryOperatorGrammar=ansi_dialect.get_grammar(
        "ArithmeticBinaryOperatorGrammar"
    ).copy(
        insert=[
            Ref("ModOperatorSegment"),
            Ref("PowerOperatorSegment"),
        ]
    ),
    SelectClauseTerminatorGrammar=OneOf(
        "BULK",
        "INTO",
        "FROM",
        "WHERE",
        Sequence("ORDER", "BY"),
        "LIMIT",
        "OVERLAPS",
        Ref("SetOperatorSegment"),
        "FETCH",
    ),
)


class AlterIndexStatementSegment(BaseSegment):
    """An `ALTER INDEX` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-INDEX.html
    If possible, please keep the order below the same as Oracle's doc:
    """

    type = "alter_index_statement"
    match_grammar: Matchable = Sequence(
        "ALTER",
        "INDEX",
        Ref("IndexReferenceSegment"),
        OneOf(
            Sequence(
                "REBUILD",
                OneOf(
                    "REVERSE",
                    "NOREVERSE",
                    optional=True,
                ),
            ),
            Sequence("MONITORING", "USAGE"),
            Sequence("NOMONITORING", "USAGE"),
            Sequence("PARAMETERS", Bracketed(Ref("QuotedLiteralSegment"))),
            Sequence("RENAME", "TO", Ref("IndexReferenceSegment")),
            "COMPILE",
            "LOGGING",
            "NOLOGGING",
            "ENABLE",
            "DISABLE",
            "UNUSABLE",
            "INVISIBLE",
            "VISIBLE",
        ),
    )


class AlterTableStatementSegment(ansi.AlterTableStatementSegment):
    """An `ALTER TABLE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html
    If possible, please keep the order below the same as Oracle's doc:
    """

    match_grammar: Matchable = Sequence(
        "ALTER",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # @TODO all stuff inside this "Delimited" is not validated for Oracle
            Delimited(
                OneOf(
                    # Table options
                    Sequence(
                        Ref("ParameterNameSegment"),
                        Ref("EqualsSegment", optional=True),
                        OneOf(Ref("LiteralGrammar"), Ref("NakedIdentifierSegment")),
                    ),
                ),
            ),
            Ref("AlterTablePropertiesSegment"),
            Ref("AlterTableColumnClausesSegment"),
            Ref("AlterTableConstraintClauses"),
        ),
    )


class AlterTablePropertiesSegment(BaseSegment):
    """ALTER TABLE `alter_table_properties` per defined in Oracle's grammar.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html

    If possible, please match the order of this sequence with what's defined in
    Oracle's alter_table_properties grammar.
    """

    type = "alter_table_properties"

    # TODO: There are many more alter_table_properties to implement
    match_grammar = OneOf(
        # Rename
        Sequence(
            "RENAME",
            "TO",
            Ref("TableReferenceSegment"),
        ),
    )


class AlterTableColumnClausesSegment(BaseSegment):
    """ALTER TABLE `column_clauses` per defined in Oracle's grammar.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html

    If possible, please match the order of this sequence with what's defined in
    Oracle's column_clauses grammar.
    """

    type = "alter_table_column_clauses"

    match_grammar = OneOf(
        # add_column_clause
        # modify_column_clause
        Sequence(
            OneOf(
                "ADD",
                "MODIFY",
            ),
            OneOf(
                Ref("ColumnDefinitionSegment"),
                Bracketed(Delimited(Ref("ColumnDefinitionSegment"))),
            ),
        ),
        # drop_column_clause
        # @TODO: extend drop_column_clause
        Sequence(
            "DROP",
            OneOf(
                Sequence("COLUMN", Ref("ColumnReferenceSegment")),
                Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            ),
        ),
        # @TODO: add_period_clause
        # @TODO: drop_period_clause
        # rename_column_clause
        Sequence(
            "RENAME",
            "COLUMN",
            Ref("ColumnReferenceSegment"),
            "TO",
            Ref("ColumnReferenceSegment"),
        ),
        # @TODO: modify_collection_retrieval
        # @TODO: modify_LOB_storage_clause
        # @TODO: alter_varray_col_properties
    )


class AlterTableConstraintClauses(BaseSegment):
    """ALTER TABLE `constraint_clauses` per defined in Oracle's grammar.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/ALTER-TABLE.html

    If possible, please match the order of this sequence with what's defined in
    Oracle's constraint_clauses grammar.
    """

    type = "alter_table_constraint_clauses"

    match_grammar = OneOf(
        Sequence(
            "ADD",
            Ref("TableConstraintSegment"),
        ),
        # @TODO MODIFY
        # @TODO DROP
        # drop_constraint_clause
        Sequence(
            "DROP",
            OneOf(
                Sequence(
                    "PRIMARY",
                    "KEY",
                ),
                Sequence(
                    "UNIQUE",
                    Bracketed(Ref("ColumnReferenceSegment")),
                ),
                Sequence("CONSTRAINT", Ref("ObjectReferenceSegment")),
            ),
            Ref.keyword("CASCADE", optional=True),
            Sequence(
                OneOf(
                    "KEEP",
                    "DROP",
                ),
                "INDEX",
                optional=True,
            ),
            Ref.keyword("ONLINE", optional=True),
        ),
        Sequence(
            "RENAME",
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),
            "TO",
            Ref("ObjectReferenceSegment"),
        ),
    )


class ExecuteFileSegment(BaseSegment):
    """A reference to an indextype."""

    type = "execute_file_statement"

    match_grammar = Sequence(
        OneOf(
            Sequence(
                Ref("AtSignSegment"),
                Ref("AtSignSegment", optional=True),
            ),
            "START",
        ),
        # Probably should have a better file definition but this will do for now
        AnyNumberOf(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            Ref("SlashSegment"),
        ),
    )


class IndexTypeReferenceSegment(BaseSegment):
    """A reference to an indextype."""

    type = "indextype_reference"

    match_grammar = ansi.ObjectReferenceSegment.match_grammar.copy()


# Adding Oracle specific statements.
class StatementSegment(ansi.StatementSegment):
    """A generic segment, to any of its child subsegments.

    Override ANSI to allow exclusion of ExecuteFileSegment.
    """

    type = "statement"

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("CommentStatementSegment"),
            Ref("CreateProcedureStatementSegment"),
            Ref("DropProcedureStatementSegment"),
            Ref("AlterFunctionStatementSegment"),
            Ref("CreateTypeStatementSegment"),
            Ref("CreateTypeBodyStatementSegment"),
            Ref("CreatePackageStatementSegment"),
            Ref("DropPackageStatementSegment"),
            Ref("AlterPackageStatementSegment"),
            Ref("AlterTriggerStatementSegment"),
            Ref("BeginEndSegment"),
            Ref("AssignmentStatementSegment"),
            Ref("RecordTypeDefinitionSegment"),
            Ref("DeclareCursorVariableSegment"),
            Ref("ExecuteImmediateSegment"),
            Ref("FunctionSegment"),
            Ref("IfExpressionStatement"),
            Ref("CaseExpressionSegment"),
            Ref("NullStatementSegment"),
            Ref("ForLoopStatementSegment"),
            Ref("WhileLoopStatementSegment"),
            Ref("LoopStatementSegment"),
            Ref("ForAllStatementSegment"),
            Ref("OpenStatementSegment"),
            Ref("CloseStatementSegment"),
            Ref("OpenForStatementSegment"),
            Ref("FetchStatementSegment"),
            Ref("ExitStatementSegment"),
            Ref("ContinueStatementSegment"),
            Ref("RaiseStatementSegment"),
            Ref("ReturnStatementSegment"),
            Ref("AlterIndexStatementSegment"),
            Ref("CreateDatabaseLinkStatementSegment"),
            Ref("DropDatabaseLinkStatementSegment"),
            Ref("AlterDatabaseLinkStatementSegment"),
            Ref("CreateSynonymStatementSegment"),
            Ref("DropSynonymStatementSegment"),
            Ref("AlterSynonymStatementSegment"),
        ],
    )


class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    We override default as Oracle allows concept of several
    batches of commands separated by '/' as well as usual
    semicolon-separated statement lines and ExecuteFileSegment.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    match_grammar = Sequence(
        AnyNumberOf(
            Ref("BatchSegment"),
            Ref("ExecuteFileSegment"),
        ),
    )


class BatchSegment(BaseSegment):
    """A segment representing a '/' batch within a file or script."""

    type = "batch"
    match_grammar = OneOf(
        Sequence(
            Delimited(
                Ref("StatementSegment"),
                delimiter=AnyNumberOf(Ref("DelimiterGrammar"), min_times=1),
                allow_gaps=True,
                allow_trailing=True,
            ),
            Ref("BatchDelimiterGrammar", optional=True),
        ),
        Ref("BatchDelimiterGrammar"),
    )


class SlashBufferExecutorSegment(BaseSegment):
    """A `/` standalone, functioning as a batch delimiter for SQL*Plus."""

    type = "slash_buffer_executor"
    match_grammar = Ref("SlashSegment")


class CommentStatementSegment(BaseSegment):
    """A `Comment` statement.

    COMMENT [text]
    https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_4009.htm
    """

    type = "comment_statement"

    match_grammar = Sequence(
        "COMMENT",
        "ON",
        Sequence(
            OneOf(
                Sequence(
                    "TABLE",
                    Ref("TableReferenceSegment"),
                ),
                Sequence(
                    "COLUMN",
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    "OPERATOR",
                    Ref("ObjectReferenceSegment"),
                ),
                Sequence(
                    "INDEXTYPE",
                    Ref("IndexTypeReferenceSegment"),
                ),
                Sequence(
                    "MATERIALIZED",
                    "VIEW",
                    Ref("TableReferenceSegment"),
                ),
            ),
            Sequence("IS", OneOf(Ref("QuotedLiteralSegment"), "NULL")),
        ),
    )


# need to ignore type due to mypy rules on type variables
# see https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
# for details
class TableReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias.

    Extended from ANSI to allow Database Link syntax using AtSignSegment
    """

    type = "table_reference"
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=OneOf(
            Ref("DotSegment"),
            Sequence(Ref("DotSegment"), Ref("DotSegment")),
            Ref("AtSignSegment"),
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
    )


class CreateViewStatementSegment(ansi.CreateViewStatementSegment):
    """A `CREATE VIEW` statement."""

    type = "create_view_statement"
    # https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/CREATE-VIEW.html
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence(Ref.keyword("NO", optional=True), "FORCE", optional=True),
        OneOf(
            "EDITIONING",
            Sequence("EDITIONABLE", Ref.keyword("EDITIONING", optional=True)),
            "NONEDITIONABLE",
            optional=True,
        ),
        Ref.keyword("MATERIALIZED", optional=True),
        "VIEW",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TableReferenceSegment"),
        # Optional list of column names
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Ref("WithNoSchemaBindingClauseSegment", optional=True),
    )


class WithinGroupClauseSegment(BaseSegment):
    """An WITHIN GROUP clause for window functions."""

    type = "withingroup_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(Ref("OrderByClauseSegment", optional=False)),
    )


class ListaggOverflowClauseSegment(BaseSegment):
    """ON OVERFLOW clause of listagg function."""

    type = "listagg_overflow_clause"
    match_grammar = Sequence(
        "ON",
        "OVERFLOW",
        OneOf(
            "ERROR",
            Sequence(
                "TRUNCATE",
                Ref("SingleQuotedIdentifierSegment", optional=True),
                OneOf("WITH", "WITHOUT", optional=True),
                Ref.keyword("COUNT", optional=True),
            ),
        ),
    )


class NamedArgumentSegment(BaseSegment):
    """Named argument to a function.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/plsql-subprograms.html
    """

    type = "named_argument"
    match_grammar = Sequence(
        Ref("NakedIdentifierSegment"),
        Ref("RightArrowSegment"),
        Ref("ExpressionSegment"),
    )


class CreateTableStatementSegment(BaseSegment):
    """A CREATE TABLE statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/CREATE-TABLE.html
    https://oracle-base.com/articles/misc/temporary-tables
    https://oracle-base.com/articles/18c/private-temporary-tables-18c
    """

    type = "create_table_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Ref("TemporaryGrammar", optional=True),
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
                Ref("OnCommitGrammar", optional=True),
            ),
            # Create AS syntax:
            Sequence(
                Ref("OnCommitGrammar", optional=True),
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref("TableEndClauseSegment", optional=True),
    )


class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        OneOf(
            AnyNumberOf(
                Sequence(
                    Ref("ColumnConstraintSegment"),
                    OneOf("ENABLE", "DISABLE", optional=True),
                )
            ),
            Sequence(
                Ref("DatatypeSegment"),  # Column type
                # For types like VARCHAR(100), VARCHAR(100 BYTE), VARCHAR (100 CHAR)
                Bracketed(
                    Sequence(
                        Anything(),
                        OneOf(
                            "BYTE",
                            "CHAR",
                            optional=True,
                        ),
                    ),
                    optional=True,
                ),
                AnyNumberOf(
                    Sequence(
                        Ref("ColumnConstraintSegment"),
                        OneOf("ENABLE", "DISABLE", optional=True),
                    )
                ),
                Ref("IdentityClauseGrammar", optional=True),
            ),
        ),
    )


class SqlplusVariableGrammar(BaseSegment):
    """SQLPlus Bind Variables :thing.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqpug/using-substitution-variables-sqlplus.html
    """

    type = "sqlplus_variable"

    match_grammar = Sequence(
        OptionallyBracketed(
            Ref("ColonSegment"),
            Ref("ParameterNameSegment"),
            Sequence(Ref("DotSegment"), Ref("ParameterNameSegment"), optional=True),
        )
    )


class ConnectByClauseSegment(BaseSegment):
    """`CONNECT BY` clause used in Hierarchical Queries.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/Hierarchical-Queries.html
    """

    type = "connectby_clause"

    match_grammar: Matchable = Sequence(
        "CONNECT",
        "BY",
        Ref.keyword("NOCYCLE", optional=True),
        Ref("ExpressionSegment"),
    )


class StartWithClauseSegment(BaseSegment):
    """`START WITH` clause used in Hierarchical Queries.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/Hierarchical-Queries.html
    """

    type = "startwith_clause"

    match_grammar: Matchable = Sequence(
        "START",
        "WITH",
        Ref("ExpressionSegment"),
    )


class HierarchicalQueryClauseSegment(BaseSegment):
    """Hierarchical Query.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/Hierarchical-Queries.html
    """

    type = "hierarchical_query_clause"

    match_grammar: Matchable = OneOf(
        Sequence(
            Ref("ConnectByClauseSegment"),
            Ref("StartWithClauseSegment", optional=True),
        ),
        Sequence(
            Ref("StartWithClauseSegment"),
            Ref("ConnectByClauseSegment"),
        ),
    )


class OrderByClauseSegment(ansi.OrderByClauseSegment):
    """A `ORDER BY` clause like in `SELECT`."""

    match_grammar: Matchable = ansi.OrderByClauseSegment.match_grammar.copy(
        insert=[Ref.keyword("SIBLINGS", optional=True)], before=Ref("ByKeywordSegment")
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    match_grammar = ansi.UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("HierarchicalQueryClauseSegment", optional=True),
            Ref("PivotSegment", optional=True),
            Ref("UnpivotSegment", optional=True),
        ],
        before=Ref("GroupByClauseSegment", optional=True),
        terminators=[
            Ref("HierarchicalQueryClauseSegment"),
            Ref("PivotSegment", optional=True),
            Ref("UnpivotSegment", optional=True),
            "LOG",
        ],
    ).copy(
        insert=[
            OneOf(
                Ref("IntoClauseSegment"),
                Ref("BulkCollectIntoClauseSegment"),
                optional=True,
            ),
        ],
        before=Ref("FromClauseSegment", optional=True),
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """A `SELECT` statement."""

    match_grammar: Matchable = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("IntoClauseSegment", optional=True),
            Ref("ForUpdateGrammar", optional=True),
            Ref("OrderByClauseSegment", optional=True),
            Ref("FetchClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
            Ref("ForUpdateGrammar", optional=True),
        ],
        replace_terminators=True,
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("WithDataClauseSegment"),
            "LOG",
        ],
    )


class GreaterThanOrEqualToSegment(CompositeComparisonOperatorSegment):
    """Allow spaces between operators."""

    match_grammar = OneOf(
        Sequence(
            Ref("RawGreaterThanSegment"),
            Ref("RawEqualsSegment"),
        ),
        Sequence(
            Ref("RawNotSegment"),
            Ref("RawLessThanSegment"),
        ),
    )


class LessThanOrEqualToSegment(CompositeComparisonOperatorSegment):
    """Allow spaces between operators."""

    match_grammar = OneOf(
        Sequence(
            Ref("RawLessThanSegment"),
            Ref("RawEqualsSegment"),
        ),
        Sequence(
            Ref("RawNotSegment"),
            Ref("RawGreaterThanSegment"),
        ),
    )


class NotEqualToSegment(CompositeComparisonOperatorSegment):
    """Allow spaces between operators."""

    match_grammar = OneOf(
        Sequence(Ref("RawNotSegment"), Ref("RawEqualsSegment")),
        Sequence(Ref("RawLessThanSegment"), Ref("RawGreaterThanSegment")),
    )


class PivotSegment(BaseSegment):
    """Pivot clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/SELECT.html
    """

    type = "pivot_clause"

    match_grammar: Matchable = Sequence(
        "PIVOT",
        Ref.keyword("XML", optional=True),
        Bracketed(
            Delimited(
                Sequence(
                    Ref("FunctionSegment"), Ref("AliasExpressionSegment", optional=True)
                )
            ),
            Ref("PivotForInGrammar"),
        ),
    )


class TriggerCorrelationNameSegment(BaseSegment):
    """A correlation name like OLD, NEW, or PARENT."""

    type = "trigger_correlation_name"
    match_grammar = OneOf("OLD", "NEW", "PARENT")


class TriggerCorrelationReferenceSegment(BaseSegment):
    """A segment to represent pseudorecords like :NEW, :OLD, and :PARENT."""

    type = "bind_variable"

    match_grammar = Sequence(
        Ref("ColonDelimiterSegment"),
        Ref("TriggerCorrelationNameSegment"),
        Sequence(
            Ref("DotSegment"),
            Ref("SingleIdentifierGrammar"),
            optional=True,
        ),
        allow_gaps=False,
    )


class UnpivotSegment(BaseSegment):
    """Unpivot clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/SELECT.html
    """

    type = "unpivot_clause"

    match_grammar: Matchable = Sequence(
        "UNPIVOT",
        Ref("UnpivotNullsGrammar", optional=True),
        Bracketed(
            OptionallyBracketed(Delimited(Ref("ColumnReferenceSegment"))),
            Ref("PivotForInGrammar"),
        ),
    )


class ObjectReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to an object."""

    # Allow whitespace
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=Ref("ObjectReferenceDelimiterGrammar"),
        terminators=[Ref("ObjectReferenceTerminatorGrammar")],
        allow_gaps=True,
    )


class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias."""

    type = "column_reference"


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
        Delimited(
            OneOf(
                Ref("FunctionNameIdentifierSegment"),
                Ref("QuotedIdentifierSegment"),
                terminators=[Ref("BracketedSegment")],
            ),
            delimiter=Ref("AtSignSegment"),
        ),
        allow_gaps=False,
    )


class SqlplusSubstitutionVariableSegment(BaseSegment):
    """SQLPlus Substitution Variables &thing.

    https://docs.oracle.com/en/database/oracle/oracle-database/21/sqpug/using-substitution-variables-sqlplus.html
    """

    type = "sqlplus_variable"

    match_grammar = Sequence(
        Ref("AmpersandSegment"),
        Ref("AmpersandSegment", optional=True),
        Ref("SingleIdentifierGrammar"),
    )


class JsonTableColumnDefinitionSegment(BaseSegment):
    """A column definition in a JSON_TABLE COLUMNS clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/JSON_TABLE.html
    """

    type = "json_table_column_definition"
    match_grammar: Matchable = OneOf(
        # FOR ORDINALITY: col_name FOR ORDINALITY
        Sequence(
            Ref("SingleIdentifierGrammar"),
            "FOR",
            "ORDINALITY",
        ),
        # NESTED [PATH] path_expr COLUMNS(...)
        Sequence(
            "NESTED",
            Ref.keyword("PATH", optional=True),
            Ref("QuotedLiteralSegment"),
            Ref("JsonTableColumnsClauseSegment"),
        ),
        # Regular column: col_name type [FORMAT JSON] [PATH path_expr] [error_handling]
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DatatypeSegment"),
            Sequence("FORMAT", "JSON", optional=True),
            Sequence(
                "PATH",
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            AnyNumberOf(
                Sequence(
                    OneOf(
                        "NULL",
                        "ERROR",
                        Sequence("DEFAULT", Ref("ExpressionSegment")),
                    ),
                    "ON",
                    OneOf("EMPTY", "ERROR"),
                ),
            ),
        ),
    )


class JsonTableColumnsClauseSegment(BaseSegment):
    """The COLUMNS clause in a JSON_TABLE function.

    https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/JSON_TABLE.html
    """

    type = "json_table_columns_clause"
    match_grammar: Matchable = Sequence(
        "COLUMNS",
        Bracketed(
            Delimited(
                Ref("JsonTableColumnDefinitionSegment"),
            ),
        ),
    )


class JsonTableFunctionContentsSegment(BaseSegment):
    """JSON_TABLE function contents.

    https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/JSON_TABLE.html
    """

    type = "function_contents"
    match_grammar: Matchable = Bracketed(
        Ref("ExpressionSegment"),
        Ref("CommaSegment"),
        Ref("QuotedLiteralSegment"),
        AnyNumberOf(
            Sequence(
                OneOf("NULL", "ERROR"),
                "ON",
                "ERROR",
            ),
        ),
        Ref("JsonTableColumnsClauseSegment"),
    )


class JsonTableFunctionNameSegment(BaseSegment):
    """JSON_TABLE function name segment.

    Need to specify as type function_name so that linting rules identify it properly.
    """

    type = "function_name"
    match_grammar: Matchable = StringParser(
        "JSON_TABLE", WordSegment, type="function_name_identifier"
    )


class FunctionSegment(ansi.FunctionSegment):
    """A scalar or aggregate function with Oracle-specific JSON_TABLE support."""

    match_grammar = ansi.FunctionSegment.match_grammar.copy(
        insert=[
            Sequence(
                Ref("JsonTableFunctionNameSegment"),
                Ref("JsonTableFunctionContentsSegment"),
            ),
        ],
        at=0,
    )


class TableExpressionSegment(ansi.TableExpressionSegment):
    """The main table expression e.g. within a FROM clause."""

    match_grammar = ansi.TableExpressionSegment.match_grammar.copy(
        insert=[
            Ref("SqlplusSubstitutionVariableSegment"),
        ]
    )


class TableConstraintSegment(ansi.TableConstraintSegment):
    """A table constraint, e.g. for CREATE TABLE.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/ALTER-TABLE.html
    """

    type = "table_constraint"

    # Later add support for CHECK constraint, others?
    # e.g. CONSTRAINT constraint_1 PRIMARY KEY(column_1)
    match_grammar: Matchable = Sequence(
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


class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement."""

    type = "transaction_statement"
    match_grammar: Matchable = Sequence(
        OneOf("START", "COMMIT", "ROLLBACK"),
        OneOf("TRANSACTION", "WORK", optional=True),
        Sequence("NAME", Ref("SingleIdentifierGrammar"), optional=True),
        Sequence("AND", Ref.keyword("NO", optional=True), "CHAIN", optional=True),
    )


class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE OR ALTER PROCEDURE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-PROCEDURE-statement.html
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        Ref.keyword("CREATE", optional=True),
        Sequence("OR", "REPLACE", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        "PROCEDURE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        Ref("SharingClauseGrammar", optional=True),
        AnyNumberOf(
            Ref("DefaultCollationClauseGrammar"),
            Ref("InvokerRightsClauseGrammar"),
            Ref("AccessibleByClauseGrammar"),
            optional=True,
        ),
        OneOf("IS", "AS", optional=True),
        AnyNumberOf(Ref("DeclareSegment"), optional=True),
        Ref("BeginEndSegment", optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class DropProcedureStatementSegment(BaseSegment):
    """A `DROP PROCEDURE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/DROP-PROCEDURE-statement.html
    """

    type = "drop_procedure_statement"

    match_grammar = Sequence(
        "DROP",
        "PROCEDURE",
        Ref("FunctionNameSegment"),
    )


class DeclareSegment(BaseSegment):
    """A declaration segment in PL/SQL.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/block.html
    """

    type = "declare_segment"

    match_grammar = Sequence(
        Ref.keyword("DECLARE", optional=True),
        Indent,
        AnyNumberOf(
            Delimited(
                OneOf(
                    Sequence(
                        OneOf(
                            Sequence(
                                Ref("SingleIdentifierGrammar"),
                                Ref.keyword("CONSTANT", optional=True),
                                OneOf(
                                    Ref("DatatypeSegment"),
                                    Ref("ColumnTypeReferenceSegment"),
                                    Ref("RowTypeReferenceSegment"),
                                ),
                            ),
                            Sequence(
                                "PRAGMA",
                                Ref("FunctionSegment"),
                            ),
                            Ref("CollectionTypeDefinitionSegment"),
                            Ref("RecordTypeDefinitionSegment"),
                            Ref("RefCursorTypeDefinitionSegment"),
                        ),
                        Sequence("NOT", "NULL", optional=True),
                        Sequence(
                            OneOf(
                                Ref("AssignmentOperatorSegment"),
                                "DEFAULT",
                            ),
                            Ref("ExpressionSegment"),
                            optional=True,
                        ),
                        Ref("DelimiterGrammar"),
                    ),
                    Ref("CreateProcedureStatementSegment"),
                    Ref("CreateFunctionStatementSegment"),
                    Ref("DeclareCursorVariableSegment"),
                ),
                delimiter=Ref("DelimiterGrammar"),
                terminators=["BEGIN", "END"],
            ),
            min_times=1,
        ),
        Dedent,
    )


class ColumnTypeReferenceSegment(BaseSegment):
    """A column type reference segment (e.g. `table_name.column_name%type`).

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/TYPE-attribute.html
    """

    type = "column_type_reference"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"), Ref("ModuloSegment"), "TYPE"
    )


class RowTypeReferenceSegment(BaseSegment):
    """A column type reference segment (e.g. `table_name%rowtype`).

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/ROWTYPE-attribute.html
    """

    type = "row_type_reference"

    match_grammar = Sequence(
        Ref("TableReferenceSegment"), Ref("ModuloSegment"), "ROWTYPE"
    )


class CollectionTypeDefinitionSegment(BaseSegment):
    """A collection type definition.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/collection-variable.html
    """

    type = "collection_type"

    match_grammar = Sequence(
        "TYPE",
        Ref("SingleIdentifierGrammar"),
        "IS",
        Sequence("TABLE", "OF", optional=True),
        OneOf(
            Ref("DatatypeSegment"),
            Ref("ColumnTypeReferenceSegment"),
            Ref("RowTypeReferenceSegment"),
        ),
        Sequence("OF", Ref("DatatypeSegment"), optional=True),
        Sequence("NOT", "NULL", optional=True),
        Sequence("INDEX", "BY", Ref("DatatypeSegment"), optional=True),
    )


class RecordTypeDefinitionSegment(BaseSegment):
    """A `RECORD` type definition.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/record-variable-declaration.html
    """

    type = "record_type"

    match_grammar = Sequence(
        "TYPE",
        Ref("SingleIdentifierGrammar"),
        "IS",
        "RECORD",
        Bracketed(
            Delimited(
                Sequence(
                    Ref("SingleIdentifierGrammar"),
                    OneOf(Ref("DatatypeSegment"), Ref("ColumnTypeReferenceSegment")),
                    Sequence(
                        Sequence("NOT", "NULL", optional=True),
                        OneOf(
                            Ref("AssignmentOperatorSegment"),
                            "DEFAULT",
                        ),
                        Ref("ExpressionSegment"),
                        optional=True,
                    ),
                )
            )
        ),
    )


class RefCursorTypeDefinitionSegment(BaseSegment):
    """A `REF CURSOR TYPE` declaration.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/cursor-variable-declaration.html
    """

    type = "ref_cursor_type"

    match_grammar = Sequence(
        "TYPE",
        Ref("SingleIdentifierGrammar"),
        "IS",
        "REF",
        "CURSOR",
        Sequence(
            "RETURN",
            OneOf(
                Ref("RowTypeReferenceSegment"),
                Ref("ColumnTypeReferenceSegment"),
                Ref("ObjectReferenceSegment"),
            ),
            optional=True,
        ),
    )


class DeclareCursorVariableSegment(BaseSegment):
    """A `CURSOR` declaration.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/explicit-cursor-declaration-and-definition.html
    """

    type = "cursor_variable"

    match_grammar = Sequence(
        "CURSOR",
        Ref("SingleIdentifierGrammar"),
        Ref("FunctionParameterListGrammar", optional=True),
        Sequence(
            "RETURN",
            OneOf(
                Ref("ColumnTypeReferenceSegment"),
                Ref("RowTypeReferenceSegment"),
                Ref("DatatypeSegment"),
            ),
            optional=True,
        ),
        Sequence("IS", Indent, Ref("SelectStatementSegment"), Dedent, optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class ExecuteImmediateSegment(BaseSegment):
    """An `EXECUTE IMMEDIATE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/EXECUTE-IMMEDIATE-statement.html
    """

    type = "execute_immediate_statement"

    match_grammar = Sequence(
        "EXECUTE",
        "IMMEDIATE",
        Indent,
        Ref("ExpressionSegment"),
        OneOf(
            Ref("IntoClauseSegment"),
            Ref("BulkCollectIntoClauseSegment"),
            optional=True,
        ),
        Sequence(
            "USING",
            Delimited(
                Sequence(
                    OneOf("IN", "OUT", Sequence("IN", "OUT"), optional=True),
                    Ref("ExpressionSegment"),
                ),
            ),
            optional=True,
        ),
        Sequence(
            OneOf("RETURNING", "RETURN"),
            OneOf(
                Ref("IntoClauseSegment"),
                Ref("BulkCollectIntoClauseSegment"),
            ),
            optional=True,
        ),
        Dedent,
    )


class BeginEndSegment(BaseSegment):
    """A `BEGIN/END` block.

    Encloses multiple statements into a single statement object.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/block.html
    """

    _when_clause = Sequence(
        "WHEN",
        OneOf(
            "OTHERS",
            Sequence(
                Ref("SingleIdentifierGrammar"),
                AnyNumberOf(
                    Sequence(
                        "OR",
                        Ref("SingleIdentifierGrammar"),
                    )
                ),
            ),
        ),
        "THEN",
        Indent,
        Ref("OneOrMoreStatementsGrammar"),
        Dedent,
    )

    type = "begin_end_block"
    match_grammar = Sequence(
        Ref("DeclareSegment", optional=True),
        "BEGIN",
        Indent,
        Ref("OneOrMoreStatementsGrammar"),
        Sequence(
            "EXCEPTION",
            Indent,
            # Using AnyNumberOf with min_times=1 is not greedy enough to grab multiple
            # exceptions here. So define it once, then have AnyNumberOf after.
            _when_clause,
            AnyNumberOf(_when_clause),
            Dedent,
            optional=True,
        ),
        Dedent,
        "END",
        Ref("ObjectReferenceSegment", optional=True),
    )


class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE OR ALTER FUNCTION` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-FUNCTION-statement.html
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        Ref.keyword("CREATE", optional=True),
        Sequence("OR", "REPLACE", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        "FUNCTION",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        "RETURN",
        Ref("DatatypeSegment"),
        Ref("SharingClauseGrammar", optional=True),
        AnyNumberOf(
            Ref("DefaultCollationClauseGrammar"),
            Ref("InvokerRightsClauseGrammar"),
            Ref("AccessibleByClauseGrammar"),
            "DETERMINISTIC",
            "SHARD_ENABLE",
            Ref("ParallelEnableClauseGrammar"),
            Ref("ResultCacheClauseGrammar"),
            Sequence("AGGREGATE", "USING", Ref("ObjectReferenceSegment")),
            Ref("PipelinedClauseGrammar"),
            Sequence(
                "SQL_MACRO",
                Bracketed(
                    Sequence("TYPE", Ref("RightArrowSegment")),
                    OneOf("SCALAR", "TABLE"),
                    optional=True,
                ),
            ),
            optional=True,
        ),
        OneOf("IS", "AS", optional=True),
        AnyNumberOf(Ref("DeclareSegment"), optional=True),
        Ref("BeginEndSegment", optional=True),
        Ref("DelimiterGrammar", optional=True),
    )


class AlterFunctionStatementSegment(BaseSegment):
    """An `ALTER FUNCTION` or `ALTER PROCEDURE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/ALTER-FUNCTION-statement.html
    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/ALTER-PROCEDURE-statement.html
    """

    type = "alter_function_statement"

    match_grammar = Sequence(
        "ALTER",
        OneOf("FUNCTION", "PROCEDURE"),
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        OneOf(
            Ref("CompileClauseGrammar"),
            "EDITIONABLE",
            "NONEDITIONABLE",
        ),
    )


class CreateTypeStatementSegment(BaseSegment):
    """A `CREATE TYPE` declaration.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-TYPE-statement.html
    """

    type = "create_type_statement"

    match_grammar = Sequence(
        Ref.keyword("CREATE", optional=True),
        Sequence("OR", "REPLACE", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        "TYPE",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TypeReferenceSegment"),
        Ref.keyword("FORCE", optional=True),
        Sequence(
            "OID",
            Ref("SingleQuotedIdentifierSegment"),
            Ref("ObjectReferenceSegment"),
            Ref("SingleQuotedIdentifierSegment"),
            optional=True,
        ),
        Ref("SharingClauseGrammar", optional=True),
        Ref("DefaultCollationClauseGrammar", optional=True),
        AnyNumberOf(
            Ref("InvokerRightsClauseGrammar"),
            Ref("AccessibleByClauseGrammar"),
            optional=True,
        ),
        OneOf("IS", "AS", optional=True),
        OneOf(
            Ref("ObjectTypeAndSubtypeDefGrammar"),
            Ref("VarrayAndNestedTypeSpecGrammar"),
        ),
    )


class TypeReferenceSegment(ObjectReferenceSegment):
    """A reference to a type."""

    type = "type_reference"


class CreateTypeBodyStatementSegment(BaseSegment):
    """A `CREATE TYPE BODY` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-TYPE-BODY-statement.html
    """

    type = "create_type_body_statement"

    match_grammar = Sequence(
        Ref.keyword("CREATE", optional=True),
        Sequence("OR", "REPLACE", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        "TYPE",
        "BODY",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TypeReferenceSegment"),
        Ref("SharingClauseGrammar", optional=True),
        OneOf("IS", "AS"),
        Indent,
        Ref("ElementSpecificationGrammar"),
        Dedent,
        "END",
    )


class DropTypeStatementSegment(ansi.DropTypeStatementSegment):
    """A `DROP TYPE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/DROP-TYPE-statement.html
    """

    type = "drop_type_statement"

    match_grammar: Matchable = ansi.DropTypeStatementSegment.match_grammar.copy(
        insert=[Ref.keyword("BODY", optional=True)],
        before=Ref("IfExistsGrammar", optional=True),
    ).copy(
        insert=[OneOf("FORCE", "VALIDATE", optional=True)],
        before=Ref("DropBehaviorGrammar", optional=True),
    )


class CreatePackageStatementSegment(BaseSegment):
    """A `CREATE PACKAGE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-PACKAGE-statement.html
    """

    type = "create_package_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        "PACKAGE",
        Ref.keyword("BODY", optional=True),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("PackageReferenceSegment"),
        Ref("SharingClauseGrammar", optional=True),
        AnyNumberOf(
            Ref("DefaultCollationClauseGrammar"),
            Ref("InvokerRightsClauseGrammar"),
            Ref("AccessibleByClauseGrammar"),
            optional=True,
        ),
        OneOf("IS", "AS"),
        Ref("DeclareSegment"),
        "END",
        Ref("PackageReferenceSegment", optional=True),
    )


class PackageReferenceSegment(ObjectReferenceSegment):
    """A reference to a package."""

    type = "package_reference"


class AlterPackageStatementSegment(BaseSegment):
    """An `ALTER PACKAGE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/ALTER-PACKAGE-statement.html
    """

    type = "alter_package_statement"

    match_grammar = Sequence(
        "ALTER",
        "PACKAGE",
        Ref("IfExistsGrammar", optional=True),
        Ref("PackageReferenceSegment"),
        OneOf(Ref("CompileClauseGrammar"), "EDITIONABLE", "NONEDITIONABLE"),
    )


class DropPackageStatementSegment(BaseSegment):
    """A `DROP PACKAGE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/DROP-PACKAGE-statement.html
    """

    type = "drop_package_statement"

    match_grammar = Sequence(
        "DROP",
        "PACKAGE",
        Ref.keyword("BODY", optional=True),
        Ref("IfExistsGrammar", optional=True),
        Ref("PackageReferenceSegment"),
    )


class CreateTriggerStatementSegment(ansi.CreateTriggerStatementSegment):
    """Create Trigger Statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-TRIGGER-statement.html
    """

    type = "create_trigger_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        Sequence("OR", "REPLACE", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        "TRIGGER",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TriggerReferenceSegment"),
        Ref("SharingClauseGrammar", optional=True),
        Ref("DefaultCollationClauseGrammar", optional=True),
        Sequence(
            OneOf(OneOf("BEFORE", "AFTER"), Sequence("INSTEAD", "OF"), "FOR"),
            Ref("DmlEventClauseSegment"),
        ),
        Ref("ReferencingClauseSegment", optional=True),
        Sequence("FOR", "EACH", "ROW", optional=True),
        Sequence(
            OneOf("FORWARD", "REVERSE", optional=True), "CROSSEDITION", optional=True
        ),
        Sequence(
            OneOf("FOLLOWS", "PRECEDES"),
            Delimited(Ref("TriggerReferenceSegment")),
            optional=True,
        ),
        OneOf("ENABLE", "DISABLE", optional=True),
        Sequence("WHEN", Bracketed(Ref("ExpressionSegment")), optional=True),
        OneOf(Ref("CompoundTriggerBlock"), Ref("OneOrMoreStatementsGrammar")),
        Ref.keyword("END", optional=True),
        Ref("TriggerReferenceSegment", optional=True),
    )


class DmlEventClauseSegment(BaseSegment):
    """DML event clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-TRIGGER-statement.html
    """

    type = "dml_event_clause"

    match_grammar: Matchable = Sequence(
        Ref("DmlGrammar"),
        AnyNumberOf(
            Sequence(
                "OR",
                Ref("DmlGrammar"),
            )
        ),
        "ON",
        Sequence("NESTED", "TABLE", Ref("ColumnReferenceSegment"), "OF", optional=True),
        Ref("TableReferenceSegment"),
    )


class ReferencingClauseSegment(BaseSegment):
    """`REFERENCING` clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-TRIGGER-statement.html
    """

    type = "referencing_clause"

    match_grammar: Matchable = Sequence(
        "REFERENCING",
        AnyNumberOf(
            Sequence(
                Ref("TriggerCorrelationNameSegment"),
                Ref.keyword("AS", optional=True),
                Ref("NakedIdentifierSegment"),
            )
        ),
    )


class CompoundTriggerBlock(BaseSegment):
    """A compound trigger block.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-TRIGGER-statement.html
    """

    type = "compound_trigger_statement"

    match_grammar: Matchable = Sequence(
        "COMPOUND",
        "TRIGGER",
        Ref("DeclareSegment", optional=True),
        AnyNumberOf(Ref("TimingPointSectionSegment")),
    )


class TimingPointSectionSegment(BaseSegment):
    """A timing point section.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CREATE-TRIGGER-statement.html
    """

    type = "timing_point_section"

    match_grammar: Matchable = Sequence(
        Ref("TimingPointGrammar"),
        "IS",
        "BEGIN",
        Ref("OneOrMoreStatementsGrammar"),
        Sequence("END", Ref("TimingPointGrammar")),
        Ref("DelimiterGrammar"),
    )


class AlterTriggerStatementSegment(BaseSegment):
    """An `ALTER TRIGGER` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/ALTER-TRIGGER-statement.html
    """

    type = "alter_trigger_statement"

    match_grammar = Sequence(
        "ALTER",
        "TRIGGER",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
        OneOf(
            Ref("CompileClauseGrammar"),
            "ENABLE",
            "DISABLE",
            Sequence("RENAME", "TO", Ref("FunctionNameSegment")),
            "EDITIONABLE",
            "NONEDITIONABLE",
        ),
    )


class AssignmentStatementSegment(BaseSegment):
    """A assignment segment in PL/SQL.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/assignment-statement.html
    """

    type = "assignment_segment_statement"

    match_grammar = Sequence(
        AnyNumberOf(
            Ref("ObjectReferenceSegment"),
            Bracketed(
                OneOf(
                    Ref("ObjectReferenceSegment"),
                    Ref("SingleQuotedIdentifierSegment"),
                    Ref("NumericLiteralSegment"),
                ),
                optional=True,
            ),
            Ref("DotSegment", optional=True),
            OneOf(
                Ref("TriggerCorrelationReferenceSegment"),
                Ref("SqlplusVariableGrammar"),
            ),
            optional=True,
        ),
        OneOf(Ref("AssignmentOperatorSegment"), "DEFAULT"),
        Ref("ExpressionSegment"),
    )


class IfExpressionStatement(BaseSegment):
    """IF-ELSE statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/IF-statement.html
    """

    type = "if_then_statement"

    match_grammar = Sequence(
        Ref("IfClauseSegment"),
        Indent,
        Ref("OneOrMoreStatementsGrammar"),
        Dedent,
        AnyNumberOf(
            Sequence(
                "ELSIF",
                OneOf(
                    Ref("ExpressionSegment"),
                    Ref("TriggerPredicatesGrammar"),
                ),
                "THEN",
                Indent,
                Ref("OneOrMoreStatementsGrammar"),
                Dedent,
            ),
        ),
        Sequence(
            "ELSE",
            Indent,
            Ref("OneOrMoreStatementsGrammar"),
            Dedent,
            optional=True,
        ),
        "END",
        "IF",
    )


class IfClauseSegment(BaseSegment):
    """IF clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/IF-statement.html
    """

    type = "if_clause"

    match_grammar = Sequence(
        "IF",
        OneOf(
            Ref("ExpressionSegment"),
            Ref("TriggerPredicatesGrammar"),
        ),
        "THEN",
    )


class CaseExpressionSegment(BaseSegment):
    """A `CASE WHEN` clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/CASE-Expressions.html
    """

    type = "case_expression"
    match_grammar: Matchable = OneOf(
        Sequence(
            "CASE",
            ImplicitIndent,
            AnyNumberOf(
                Ref("WhenClauseSegment", terminators=[Ref.keyword("WHEN")]),
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
            ImplicitIndent,
            AnyNumberOf(
                Ref("WhenClauseSegment", terminators=[Ref.keyword("WHEN")]),
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
            Ref.keyword("CASE", optional=True),
            Ref("SingleIdentifierGrammar", optional=True),
        ),
        Sequence(
            "CASE",
            OneOf(
                Ref("ExpressionSegment"),
                Ref("TriggerPredicatesGrammar"),
            ),
            ImplicitIndent,
            AnyNumberOf(
                Ref("WhenClauseSegment", terminators=[Ref.keyword("WHEN")]),
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
            Ref.keyword("CASE", optional=True),
            Ref("SingleIdentifierGrammar", optional=True),
        ),
        terminators=[
            Ref("ComparisonOperatorGrammar"),
            Ref("CommaSegment"),
            Ref("BinaryOperatorGrammar"),
        ],
    )


class WhenClauseSegment(BaseSegment):
    """A 'WHEN' clause for a 'CASE' statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/CASE-Expressions.html
    """

    type = "when_clause"
    match_grammar: Matchable = Sequence(
        "WHEN",
        # NOTE: The nested sequence here is to ensure the correct
        # placement of the meta segments when templated elements
        # are present.
        # https://github.com/sqlfluff/sqlfluff/issues/3988
        Sequence(
            ImplicitIndent,
            OneOf(
                Ref("ExpressionSegment"),
                Ref("TriggerPredicatesGrammar"),
            ),
            Dedent,
        ),
        Conditional(Indent, indented_then=True),
        "THEN",
        Conditional(ImplicitIndent, indented_then_contents=True),
        OneOf(Ref("ExpressionSegment"), Ref("OneOrMoreStatementsGrammar")),
        Conditional(Dedent, indented_then_contents=True),
        Conditional(Dedent, indented_then=True),
    )


class ElseClauseSegment(BaseSegment):
    """An 'ELSE' clause for a 'CASE' statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/CASE-Expressions.html
    """

    type = "else_clause"
    match_grammar: Matchable = Sequence(
        "ELSE",
        ImplicitIndent,
        OneOf(Ref("ExpressionSegment"), Ref("OneOrMoreStatementsGrammar")),
        Dedent,
    )


class NullStatementSegment(BaseSegment):
    """A `NULL` statement inside a block."""

    type = "null_statement"

    match_grammar = Sequence("NULL")


class MergeUpdateClauseSegment(BaseSegment):
    """`UPDATE` clause within the `MERGE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/MERGE.html
    """

    type = "merge_update_clause"

    match_grammar: Matchable = Sequence(
        "UPDATE",
        Indent,
        Ref("SetClauseListSegment"),
        Dedent,
        Ref("WhereClauseSegment", optional=True),
        Ref("ReturningClauseSegment", optional=True),
    )


class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/INSERT.html
    """

    type = "insert_statement"

    _insert_into_clause = Sequence(
        "INTO",
        OneOf(
            Ref("TableReferenceSegment"),
            Bracketed(Ref("SelectStatementSegment")),
        ),
        Ref("AliasExpressionSegment", optional=True),
        Bracketed(Delimited(Ref("ColumnReferenceSegment")), optional=True),
    )

    _insert_set_or_values_clause = (
        Sequence(
            OneOf(
                Ref("ValuesClauseSegment"),
                Sequence("SET", Delimited(Ref("SetClauseSegment"))),
            ),
            Ref("ReturningClauseSegment", optional=True),
            optional=True,
        ),
    )

    _error_logging_clause = Sequence(
        "LOG",
        "ERRORS",
        Sequence("INTO", Ref("TableReferenceSegment"), optional=True),
        Bracketed(Ref("ExpressionSegment"), optional=True),
        Sequence(
            "REJECT",
            "LIMIT",
            OneOf(Ref("NumericLiteralSegment"), "UNLIMITED"),
            optional=True,
        ),
        optional=True,
    )

    _by_name_position_subquery_clause = Sequence(
        Sequence("BY", OneOf("NAME", "POSITION"), optional=True),
        Ref("SelectableGrammar"),
    )

    match_grammar: Matchable = Sequence(
        "INSERT",
        OneOf(
            Sequence(
                _insert_into_clause,
                OneOf(*_insert_set_or_values_clause, _by_name_position_subquery_clause),
                _error_logging_clause,
            ),
            Sequence(
                "ALL",
                AnyNumberOf(
                    Sequence(
                        _insert_into_clause,
                        *_insert_set_or_values_clause,
                        _error_logging_clause,
                    ),
                    min_times=1,
                ),
                _by_name_position_subquery_clause,
            ),
        ),
    )


class ForLoopStatementSegment(BaseSegment):
    """A `FOR LOOP` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/FOR-LOOP-statement.html
    """

    type = "for_loop_statement"

    match_grammar: Matchable = Sequence(
        "FOR",
        Delimited(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                OneOf("MUTABLE", "IMMUTABLE", optional=True),
            )
        ),
        "IN",
        Delimited(
            Sequence(
                Ref.keyword("REVERSE", optional=True),
                OneOf(
                    Ref("IterationSteppedControlGrammar"),
                    Sequence(
                        Ref.keyword("REPEAT", optional=True), Ref("ExpressionSegment")
                    ),
                    Sequence(
                        OneOf("VALUES", "INDICES", "PAIRS"),
                        "OF",
                        Ref("SingleIdentifierGrammar"),
                    ),
                    Bracketed(Ref("SelectStatementSegment")),
                ),
                Sequence("WHILE", Ref("ExpressionSegment"), optional=True),
                Sequence("WHEN", Ref("ExpressionSegment"), optional=True),
            )
        ),
        Ref("LoopStatementSegment"),
    )


class WhileLoopStatementSegment(BaseSegment):
    """A `WHILE LOOP` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/WHILE-LOOP-statement.html
    """

    type = "while_loop_statement"

    match_grammar: Matchable = Sequence(
        "WHILE",
        Ref("ExpressionSegment"),
        Ref("LoopStatementSegment"),
    )


class LoopStatementSegment(BaseSegment):
    """A `LOOP` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/loop-statements.html
    """

    type = "loop_statement"

    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar", optional=True),
        "LOOP",
        Indent,
        Ref("OneOrMoreStatementsGrammar"),
        Dedent,
        "END",
        "LOOP",
        Ref("SingleIdentifierGrammar", optional=True),
    )


class ForAllStatementSegment(BaseSegment):
    """A `FORALL` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/FORALL-statement.html
    """

    type = "forall_statement"

    match_grammar = Sequence(
        "FORALL",
        Ref("NakedIdentifierSegment"),
        "IN",
        OneOf(
            Ref("IterationSteppedControlGrammar"),
            Sequence("VALUES", "OF", Ref("SingleIdentifierGrammar")),
        ),
        Sequence("SAVE", "EXCEPTIONS", optional=True),
        OneOf(
            Ref("DeleteStatementSegment"),
            Ref("InsertStatementSegment"),
            Ref("SelectStatementSegment"),
            Ref("UpdateStatementSegment"),
        ),
    )


class OpenStatementSegment(BaseSegment):
    """An `OPEN` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/OPEN-statement.html
    """

    type = "open_statement"

    match_grammar = Sequence(
        "OPEN",
        Ref("SingleIdentifierGrammar"),
        Ref("FunctionContentsSegment", optional=True),
    )


class CloseStatementSegment(BaseSegment):
    """A `CLOSE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CLOSE-statement.html
    """

    type = "close_statement"

    match_grammar = Sequence(
        "CLOSE",
        OneOf(Ref("SingleIdentifierGrammar"), Ref("SqlplusVariableGrammar")),
    )


class OpenForStatementSegment(BaseSegment):
    """An `OPEN FOR` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/OPEN-FOR-statement.html
    """

    type = "open_for_statement"

    match_grammar = Sequence(
        "OPEN",
        OneOf(Ref("SingleIdentifierGrammar"), Ref("SqlplusVariableGrammar")),
        "FOR",
        OneOf(
            Ref("SingleQuotedIdentifierSegment"),
            Ref("SelectStatementSegment"),
            Ref("SingleIdentifierGrammar"),
        ),
        Sequence(
            "USING",
            Delimited(
                Sequence(
                    OneOf("IN", "OUT", Sequence("IN", "OUT"), optional=True),
                    OneOf(
                        Ref("SingleIdentifierGrammar"),
                        Ref("SingleQuotedIdentifierSegment"),
                    ),
                ),
                optional=True,
            ),
            optional=True,
        ),
    )


class FetchStatementSegment(BaseSegment):
    """A `FETCH` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/FETCH-statement.html
    """

    type = "fetch_statement"

    match_grammar = Sequence(
        "FETCH",
        OneOf(Ref("SingleIdentifierGrammar"), Ref("SqlplusVariableGrammar")),
        OneOf(
            Ref("IntoClauseSegment"),
            Sequence(
                Ref("BulkCollectIntoClauseSegment"),
                Sequence(
                    "LIMIT",
                    OneOf(Ref("NumericLiteralSegment"), Ref("SingleIdentifierGrammar")),
                    optional=True,
                ),
            ),
        ),
    )


class IntoClauseSegment(BaseSegment):
    """Into Clause Segment.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/RETURNING-INTO-clause.html
    """

    type = "into_clause"

    match_grammar = Sequence(
        "INTO",
        Delimited(OneOf(Ref("SingleIdentifierGrammar"), Ref("SqlplusVariableGrammar"))),
    )


class BulkCollectIntoClauseSegment(BaseSegment):
    """A `BULK COLLECT INTO` Clause Segment.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/RETURNING-INTO-clause.html
    """

    type = "bulk_collect_into_clause"

    match_grammar = Sequence(
        "BULK",
        "COLLECT",
        "INTO",
        ImplicitIndent,
        Delimited(OneOf(Ref("SingleIdentifierGrammar"), Ref("SqlplusVariableGrammar"))),
        Dedent,
    )


class ExitStatementSegment(BaseSegment):
    """An `EXIT` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/EXIT-statement.html
    """

    type = "exit_statement"

    match_grammar = Sequence(
        "EXIT",
        Ref("SingleIdentifierGrammar", optional=True),
        Sequence("WHEN", Ref("ExpressionSegment"), optional=True),
    )


class ContinueStatementSegment(BaseSegment):
    """A `CONTINUE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/CONTINUE-statement.html
    """

    type = "continue_statement"

    match_grammar = Sequence(
        "CONTINUE",
        Ref("SingleIdentifierGrammar", optional=True),
        Sequence("WHEN", Ref("ExpressionSegment"), optional=True),
    )


class RaiseStatementSegment(BaseSegment):
    """A `RAISE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/RAISE-statement.html
    """

    type = "raise_statement"

    match_grammar = Sequence(
        "RAISE",
        Ref("SingleIdentifierGrammar", optional=True),
    )


class ReturnStatementSegment(BaseSegment):
    """A RETURN statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/RETURN-statement.html
    """

    type = "return_statement"

    match_grammar = Sequence(
        "RETURN",
        Ref("ExpressionSegment", optional=True),
    )


class CreateUserStatementSegment(BaseSegment):
    """A `CREATE USER` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/CREATE-USER.html
    """

    type = "create_user_statement"
    match_grammar: Matchable = Sequence(
        "CREATE",
        "USER",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("RoleReferenceSegment"),
        OneOf(
            Sequence(
                "IDENTIFIED",
                OneOf(
                    Sequence(
                        "BY",
                        Ref("SingleIdentifierGrammar"),
                        Sequence(
                            Ref.keyword("HTTP", optional=True),
                            "DIGEST",
                            OneOf("ENABLE", "DISABLE"),
                            optional=True,
                        ),
                    ),
                    Sequence(
                        OneOf("EXTERNALLY", "GLOBALLY"),
                        Sequence(
                            "AS",
                            OneOf(
                                Ref("QuotedIdentifierSegment"),
                                Ref("SingleQuotedIdentifierSegment"),
                            ),
                            optional=True,
                        ),
                    ),
                ),
            ),
            Sequence("NO", "AUTHENTICATION"),
        ),
        AnyNumberOf(
            Ref("DefaultCollationClauseGrammar"),
            Sequence(
                OneOf(
                    Sequence("DEFAULT", "TABLESPACE"),
                    Sequence(
                        Ref.keyword("LOCAL", optional=True), "TEMPORARY", "TABLESPACE"
                    ),
                    Sequence(
                        "QUOTA", OneOf(Ref("SizeClauseGrammar"), "UNLIMITED"), "ON"
                    ),
                    "PROFILE",
                ),
                Ref("ObjectReferenceSegment"),
            ),
            Sequence("PASSWORD", "EXPIRE"),
            Sequence("ACCOUNT", OneOf("LOCK", "UNLOCK")),
            Sequence("ENABLE", "EDITIONS"),
            Sequence("CONTAINER", Ref("EqualsSegment"), OneOf("CURRENT", "ALL")),
            Sequence("READ", OneOf("ONLY", "WRITE")),
        ),
    )


class ReturningClauseSegment(BaseSegment):
    """A `RETURNING` clause.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/lnpls/RETURNING-INTO-clause.html
    """

    type = "returning_clause"

    match_grammar: Matchable = Sequence(
        OneOf("RETURNING", "RETURN"),
        Delimited(
            Sequence(
                OneOf("OLD", "NEW", optional=True),
                OneOf(Ref("SingleIdentifierGrammar"), Ref("ExpressionSegment")),
            ),
        ),
        OneOf(Ref("IntoClauseSegment"), Ref("BulkCollectIntoClauseSegment")),
    )


class UpdateStatementSegment(ansi.UpdateStatementSegment):
    """An `Update` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/UPDATE.html
    """

    match_grammar: Matchable = ansi.UpdateStatementSegment.match_grammar.copy(
        insert=[Ref("ReturningClauseSegment", optional=True)]
    )


class DeleteStatementSegment(ansi.DeleteStatementSegment):
    """A `DELETE` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/DELETE.html
    """

    match_grammar: Matchable = ansi.DeleteStatementSegment.match_grammar.copy(
        insert=[Ref("ReturningClauseSegment", optional=True)]
    )


class DatabaseLinkReferenceSegment(ansi.ObjectReferenceSegment):
    """A reference to a database link."""

    type = "database_link_reference"
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"), delimiter=Ref("DotSegment")
    )


class CreateDatabaseLinkStatementSegment(BaseSegment):
    """A `CREATE DATABASE LINK` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/CREATE-DATABASE-LINK.html
    """

    type = "create_database_link_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref.keyword("SHARED", optional=True),
        Ref.keyword("PUBLIC", optional=True),
        "DATABASE",
        "LINK",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("DatabaseLinkReferenceSegment"),
        Sequence(
            OneOf(
                Sequence(
                    "CONNECT",
                    OneOf(
                        Sequence(
                            "TO",
                            OneOf(
                                "CURRENT_USER",
                                Sequence(
                                    Ref("RoleReferenceSegment"),
                                    "IDENTIFIED",
                                    "BY",
                                    Ref("SingleIdentifierGrammar"),
                                    Ref("DBLinkAuthenticationGrammar", optional=True),
                                ),
                            ),
                        ),
                        Sequence("WITH", Ref("SingleIdentifierGrammar")),
                    ),
                ),
                Ref("DBLinkAuthenticationGrammar"),
            ),
            optional=True,
        ),
        Sequence("USING", Ref("SingleQuotedIdentifierSegment"), optional=True),
    )


class DropDatabaseLinkStatementSegment(BaseSegment):
    """A `DROP DATABASE LINK` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/DROP-DATABASE-LINK.html
    """

    type = "drop_database_link_statement"

    match_grammar: Matchable = Sequence(
        "DROP",
        Ref.keyword("PUBLIC", optional=True),
        "DATABASE",
        "LINK",
        Ref("IfExistsGrammar", optional=True),
        Ref("DatabaseLinkReferenceSegment"),
    )


class AlterDatabaseLinkStatementSegment(BaseSegment):
    """An `ALTER DATABASE LINK` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/ALTER-DATABASE-LINK.html
    """

    type = "alter_database_link_statement"

    match_grammar: Matchable = Sequence(
        "ALTER",
        Ref.keyword("SHARED", optional=True),
        Ref.keyword("PUBLIC", optional=True),
        "DATABASE",
        "LINK",
        Ref("IfExistsGrammar", optional=True),
        Ref("DatabaseLinkReferenceSegment"),
        OneOf(
            Sequence(
                "CONNECT",
                OneOf(
                    Sequence(
                        "TO",
                        Ref("RoleReferenceSegment"),
                        "IDENTIFIED",
                        "BY",
                        Ref("SingleIdentifierGrammar"),
                        Ref("DBLinkAuthenticationGrammar", optional=True),
                    ),
                    Sequence("WITH", Ref("SingleIdentifierGrammar")),
                ),
            ),
            Ref("DBLinkAuthenticationGrammar"),
        ),
    )


class CreateSynonymStatementSegment(BaseSegment):
    """A `CREATE SYNONYM` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/CREATE-SYNONYM.html
    """

    type = "create_synonym_statement"

    match_grammar: Matchable = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        OneOf("EDITIONABLE", "NONEDITIONABLE", optional=True),
        Ref.keyword("PUBLIC", optional=True),
        "SYNONYM",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref("SharingClauseGrammar", optional=True),
        "FOR",
        Ref("ObjectReferenceSegment"),
        Sequence(
            Ref("AtSignSegment"), Ref("DatabaseLinkReferenceSegment"), optional=True
        ),
    )


class DropSynonymStatementSegment(BaseSegment):
    """A `DROP SYNONYM` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/DROP-SYNONYM.html
    """

    type = "drop_synonym_statement"

    match_grammar: Matchable = Sequence(
        "DROP",
        Ref.keyword("PUBLIC", optional=True),
        "SYNONYM",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        Ref.keyword("FORCE", optional=True),
    )


class AlterSynonymStatementSegment(BaseSegment):
    """An `ALTER SYNONYM` statement.

    https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/ALTER-SYNONYM.html
    """

    type = "alter_synonym_statement"

    match_grammar: Matchable = Sequence(
        "ALTER",
        Ref.keyword("PUBLIC", optional=True),
        "SYNONYM",
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
        OneOf("EDITIONABLE", "NONEDITIONABLE", "COMPILE"),
    )


class AccessPermissionSegment(ansi.AccessPermissionSegment):
    """An access permission."""

    match_grammar: Matchable = OneOf(
        "ADMINISTER",
        "ADVISOR",
        "ALL",
        "ALTER",
        "ANALYZE",
        "AUDIT",
        "BACKUP",
        Sequence("BECOME", "USER"),
        Sequence("CHANGE", "NOTIFICATION"),
        "COMMENT",
        "CREATE",
        "DEBUG",
        "DELETE",
        "DROP",
        Sequence("ENABLE", "DIAGNOSTICS"),
        "EXECUTE",
        "EXEMPT",
        Sequence(
            "FLASHBACK",
            Ref.keyword("ARCHIVE", optional=True),
            Ref.keyword("ADMINISTER", optional=True),
        ),
        "FORCE",
        "GRANT",
        "INDEX",
        "INHERIT",
        "INSERT",
        "KEEP",
        "LOCK",
        "LOGMINING",
        "MANAGE",
        "MERGE",
        Sequence("ON", "COMMIT", "REFRESH"),
        "PURGE",
        Sequence(Ref.keyword("GLOBAL", optional=True), "QUERY", "REWRITE"),
        "READ",
        "REDEFINE",
        "REFERENCES",
        "RESTRICTED",
        "RESUMABLE",
        "SELECT",
        "SET",
        "SIGN",
        Sequence("TABLE", "RETENTION"),
        "TRANSLATE",
        "UNDER",
        "UNLIMITED",
        "UPDATE",
        "USE",
        "WRITE",
    )


class AccessPermissionsSegment(ansi.AccessPermissionsSegment):
    """An access permission set."""

    match_grammar: Matchable = Delimited(
        Sequence(
            Ref("AccessPermissionSegment"),
            OneOf("ANY", "PUBLIC", optional=True),
            Ref("AccessObjectSegment", optional=True),
        ),
        Ref("RoleReferenceSegment"),
        Sequence(
            Ref("AccessPermissionSegment"),
            OneOf("ANY", "PUBLIC", optional=True),
            Ref("AccessObjectSegment", optional=True),
            Bracketed(Delimited(Ref("ColumnReferenceSegment")), optional=True),
        ),
    )


class AccessObjectSegment(ansi.AccessObjectSegment):
    """An access object."""

    match_grammar: Matchable = OneOf(
        Sequence("ACCESS", "POLICY"),
        Sequence("ANALYTIC", "VIEW"),
        Sequence("ATTRIBUTE", "DIMENSION"),
        "CLASS",
        "CLUSTER",
        Sequence("CONNECT", "SESSION"),
        "CONTAINER",
        "CONTEXT",
        Sequence(
            "CUBE", OneOf("DIMENSION", Sequence("BUILD", "PROCESS"), optional=True)
        ),
        Sequence("DATABASE", OneOf("LINK", "TRIGGER", optional=True)),
        Sequence("DATE", "TIME"),
        "DBA_RECYCLEBIN",
        "DICTIONARY",
        "DIMENSION",
        "DIRECTIVE",
        "DIRECTORY",
        "DOMAIN",
        "EDITION",
        Sequence("FINE", "GRAINED", "AUDIT", "POLICY"),
        "HIERARCHY",
        "INDEX",
        "INDEXTYPE",
        Sequence(
            Ref.keyword("EXTERNAL", optional=True),
            "JOB",
            Ref.keyword("RESOURCE", optional=True),
        ),
        Sequence("KEY", "MANAGEMENT"),
        "LIBRARY",
        Sequence("LOCKDOWN", "PROFILE"),
        Sequence("MATERIALIZED", "VIEW"),
        Sequence("MEASURE", "FOLDER"),
        Sequence("MINING", "MODEL"),
        Sequence("OBJECT", Ref.keyword("PRIVILEGE", optional=True)),
        "OPERATOR",
        "OUTLINE",
        Sequence("LOCKDOWN", "PROFILE"),
        Sequence("PLUGGABLE", "DATABASE"),
        "PRIVILEGE",
        "PRIVILEGES",
        "PROCEDURE",
        "PROFILE",
        "PROGRAM",
        Sequence("PROPERTY", "GRAPH"),
        Sequence("REDACTION", "POLICY"),
        Sequence(Ref.keyword("REMOTE", optional=True), "PRIVILEGES"),
        Sequence("RESOURCE", "COST"),
        "ROLE",
        Sequence("ROLLBACK", "SEGMENT"),
        Sequence("ROW", "LEVEL", "SECURITY", "POLICY"),
        "SCHEDULER",
        "SEQUENCE",
        "SESSION",
        Sequence(
            "SQL",
            OneOf(
                "FIREWALL",
                Sequence("MANAGEMENT", "OBJECT"),
                "PROFILE",
                Sequence("TRANSLATION", "PROFILE"),
                Sequence("TUNING", "SET"),
                optional=True,
            ),
        ),
        "SYNONYM",
        "SYSGUID",
        "SYSTEM",
        "TABLE",
        "TABLESPACE",
        "TRANSACTION",
        "TRIGGER",
        "TYPE",
        "USER",
        "VIEW",
    )


class AccessTargetSegment(ansi.AccessTargetSegment):
    """An access target."""

    match_grammar: Matchable = OneOf(
        Sequence(
            OneOf("FUNCTION", "PROCEDURE", "PACKAGE"),
            Sequence(Ref("SchemaReferenceSegment"), Ref("DotSegment"), optional=True),
            Ref("FunctionNameSegment"),
        ),
        Delimited(
            Sequence(
                Sequence(
                    Ref("SchemaReferenceSegment"), Ref("DotSegment"), optional=True
                ),
                Ref("ObjectReferenceSegment"),
            ),
        ),
        Delimited(Ref("RoleReferenceSegment"), "PUBLIC"),
    )


class GrantStatementSegment(ansi.GrantStatementSegment):
    """A `GRANT` statement."""

    match_grammar: Matchable = Sequence(
        "GRANT",
        OneOf(
            Sequence(
                OneOf(
                    Sequence(
                        Ref("AccessPermissionsSegment"),
                        Sequence(
                            "ON", "SCHEMA", Ref("SchemaReferenceSegment"), optional=True
                        ),
                        "TO",
                        OneOf(
                            Ref("AccessTargetSegment"),
                            Sequence(
                                Ref("AccessTargetSegment"),
                                "IDENTIFIED",
                                "BY",
                                Delimited(Ref("SingleIdentifierGrammar")),
                            ),
                        ),
                        Sequence(
                            "WITH", OneOf("ADMIN", "DELEGATE"), "OPTION", optional=True
                        ),
                    ),
                    Sequence(
                        Ref("AccessPermissionsSegment"),
                        "ON",
                        Sequence(
                            OneOf(
                                "USER",
                                "DIRECTORY",
                                "EDITION",
                                Sequence("MINING", "MODEL"),
                                Sequence("JAVA", OneOf("SOURCE", "RESOURCE")),
                                Sequence("SQL", "TRANSLATION", "PROFILE"),
                                optional=True,
                            ),
                            Delimited(
                                Sequence(
                                    Sequence(
                                        Ref("SchemaReferenceSegment"),
                                        Ref("DotSegment"),
                                        optional=True,
                                    ),
                                    Ref("ObjectReferenceSegment"),
                                ),
                            ),
                        ),
                        "TO",
                        Ref("AccessTargetSegment"),
                        Sequence("WITH", "HIERARCHY", "OPTION", optional=True),
                        Sequence("WITH", "GRANT", "OPTION", optional=True),
                        OneOf(
                            Sequence("CASCADE", "CONSTRAINTS"), "FORCE", optional=True
                        ),
                    ),
                ),
                Sequence(
                    "CONTAINER",
                    Ref("EqualsSegment"),
                    OneOf("CURRENT", "ALL"),
                    optional=True,
                ),
            ),
            Sequence(
                Ref("AccessPermissionsSegment"),
                "TO",
                Ref("AccessTargetSegment"),
            ),
        ),
    )


class RevokeStatementSegment(ansi.RevokeStatementSegment):
    """A `REVOKE` statement."""

    match_grammar: Matchable = Sequence(
        "REVOKE",
        OneOf(
            Sequence(
                OneOf(
                    Sequence(
                        Ref("AccessPermissionsSegment"),
                        Sequence(
                            "ON", "SCHEMA", Ref("SchemaReferenceSegment"), optional=True
                        ),
                        "FROM",
                        OneOf(
                            Ref("AccessTargetSegment"),
                            Sequence(
                                Ref("AccessTargetSegment"),
                                "IDENTIFIED",
                                "BY",
                                Delimited(Ref("SingleIdentifierGrammar")),
                            ),
                        ),
                    ),
                    Sequence(
                        Ref("AccessPermissionsSegment"),
                        "ON",
                        Sequence(
                            OneOf(
                                "USER",
                                "DIRECTORY",
                                "EDITION",
                                Sequence("MINING", "MODEL"),
                                Sequence("JAVA", OneOf("SOURCE", "RESOURCE")),
                                Sequence("SQL", "TRANSLATION", "PROFILE"),
                                optional=True,
                            ),
                            Delimited(
                                Sequence(
                                    Sequence(
                                        Ref("SchemaReferenceSegment"),
                                        Ref("DotSegment"),
                                        optional=True,
                                    ),
                                    Ref("ObjectReferenceSegment"),
                                ),
                            ),
                        ),
                        "FROM",
                        Ref("AccessTargetSegment"),
                        OneOf(
                            Sequence("CASCADE", "CONSTRAINTS"), "FORCE", optional=True
                        ),
                    ),
                ),
                Sequence(
                    "CONTAINER",
                    Ref("EqualsSegment"),
                    OneOf("CURRENT", "ALL"),
                    optional=True,
                ),
            ),
            Sequence(
                Delimited(Ref("RoleReferenceSegment")),
                "FROM",
                Ref("AccessTargetSegment"),
            ),
        ),
    )


class ValuesClauseSegment(BaseSegment):
    """A `VALUES` clause like in `INSERT`."""

    type = "values_clause"

    match_grammar: Matchable = Sequence(
        OneOf("VALUE", "VALUES"),
        OptionallyBracketed(
            Delimited(
                "DEFAULT",
                Ref("LiteralGrammar"),
                Ref("ExpressionSegment"),
            ),
        ),
    )
