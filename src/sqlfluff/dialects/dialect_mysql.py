"""The MySQL dialect.

For now the only change is the parsing of comments.
https://dev.mysql.com/doc/refman/8.0/en/differences-from-ansi.html
"""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import (
    AnyNumberOf,
    AnySetOf,
    Anything,
    BaseSegment,
    BinaryOperatorSegment,
    Bracketed,
    CodeSegment,
    CommentSegment,
    Dedent,
    Delimited,
    IdentifierSegment,
    Indent,
    KeywordSegment,
    LiteralSegment,
    Matchable,
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
from sqlfluff.dialects.dialect_mysql_keywords import (
    mysql_reserved_keywords,
    mysql_unreserved_keywords,
)

ansi_dialect = load_raw_dialect("ansi")
mysql_dialect = ansi_dialect.copy_as("mysql")

mysql_dialect.patch_lexer_matchers(
    [
        RegexLexer(
            "inline_comment",
            r"(-- |#)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("-- ", "#")},
        ),
        # Pattern breakdown:
        # (?s)                     DOTALL (dot matches newline)
        #     (                    group1 start
        #         '                single quote (start)
        #         (?:              non-capturing group: begin
        #             \\'          MySQL escaped single-quote
        #             |''          or ANSI escaped single-quotes
        #             |\\\\        or consecutive [escaped] backslashes
        #             |[^']        or anything besides a single-quote
        #         )*               non-capturing group: end (zero or more times)
        #         '                single quote (end of the single-quoted string)
        #         (?!')            negative lookahead: not single quote
        #     )                    group1 end
        RegexLexer(
            "single_quote",
            r"(?s)('(?:\\'|''|\\\\|[^'])*'(?!'))",
            CodeSegment,
        ),
        RegexLexer(
            "double_quote",
            r'(?s)("(?:\\"|""|\\\\|[^"])*"(?!"))',
            CodeSegment,
        ),
    ]
)

mysql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "hexadecimal_literal",
            r"([xX]'([\da-fA-F][\da-fA-F])+'|0x[\da-fA-F]+)",
            LiteralSegment,
            segment_kwargs={"type": "numeric_literal"},
        ),
        RegexLexer(
            "bit_value_literal",
            r"([bB]'[01]+'|0b[01]+)",
            LiteralSegment,
            segment_kwargs={"type": "numeric_literal"},
        ),
    ],
    before="numeric_literal",
)

# Set Keywords
# Do not clear inherited unreserved ansi keywords. Too many are needed to parse well.
# Just add MySQL unreserved keywords.
mysql_dialect.update_keywords_set_from_multiline_string(
    "unreserved_keywords", mysql_unreserved_keywords
)

mysql_dialect.sets("reserved_keywords").clear()
mysql_dialect.update_keywords_set_from_multiline_string(
    "reserved_keywords", mysql_reserved_keywords
)

# Set the datetime units
mysql_dialect.sets("datetime_units").clear()
mysql_dialect.sets("datetime_units").update(
    [
        # https://github.com/mysql/mysql-server/blob/1bfe02bdad6604d54913c62614bde57a055c8332/sql/sql_yacc.yy#L12321-L12345
        # interval:
        "DAY_HOUR",
        "DAY_MICROSECOND",
        "DAY_MINUTE",
        "DAY_SECOND",
        "HOUR_MICROSECOND",
        "HOUR_MINUTE",
        "HOUR_SECOND",
        "MINUTE_MICROSECOND",
        "MINUTE_SECOND",
        "SECOND_MICROSECOND",
        "YEAR_MONTH",
        # interval_time_stamp
        "DAY",
        "WEEK",
        "HOUR",
        "MINUTE",
        "MONTH",
        "QUARTER",
        "SECOND",
        "MICROSECOND",
        "YEAR",
    ]
)


mysql_dialect.replace(
    QuotedIdentifierSegment=TypedParser(
        "back_quote",
        IdentifierSegment,
        type="quoted_identifier",
        trim_chars=("`",),
    ),
    LiteralGrammar=ansi_dialect.get_grammar("LiteralGrammar").copy(
        insert=[
            Ref("DoubleQuotedLiteralSegment"),
            Ref("SystemVariableSegment"),
        ]
    ),
    FromClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "FromClauseTerminatorGrammar"
    ).copy(
        insert=[
            Ref("IndexHintClauseSegment"),
            Ref("SelectPartitionClauseSegment"),
            Ref("ForClauseSegment"),
            Ref("SetOperatorSegment"),
            Ref("WithNoSchemaBindingClauseSegment"),
            Ref("IntoClauseSegment"),
        ]
    ),
    WhereClauseTerminatorGrammar=ansi_dialect.get_grammar(
        "WhereClauseTerminatorGrammar"
    ).copy(
        insert=[
            Ref("IntoClauseSegment"),
        ],
    ),
    BaseExpressionElementGrammar=ansi_dialect.get_grammar(
        "BaseExpressionElementGrammar"
    ).copy(
        insert=[
            Ref("SessionVariableNameSegment"),
            Ref("LocalVariableNameSegment"),
            Ref("VariableAssignmentSegment"),
        ]
    ),
    DateTimeLiteralGrammar=Sequence(
        # MySQL does not require the keyword to be specified:
        # https://dev.mysql.com/doc/refman/8.0/en/date-and-time-literals.html
        OneOf(
            "DATE",
            "TIME",
            "TIMESTAMP",
            optional=True,
        ),
        OneOf(
            TypedParser(
                "single_quote",
                LiteralSegment,
                type="date_constructor_literal",
            ),
            Ref("NumericLiteralSegment"),
        ),
    ),
    QuotedLiteralSegment=AnyNumberOf(
        # MySQL allows whitespace-concatenated string literals (#1488).
        # Since these string literals can have comments between them,
        # we use grammar to handle this.
        TypedParser(
            "single_quote",
            LiteralSegment,
            type="quoted_literal",
        ),
        Ref("DoubleQuotedLiteralSegment"),
        min_times=1,
    ),
    UniqueKeyGrammar=Sequence(
        "UNIQUE",
        Ref.keyword("KEY", optional=True),
    ),
    # Odd syntax, but pr
    CharCharacterSetGrammar=Ref.keyword("BINARY"),
    DelimiterGrammar=OneOf(Ref("SemicolonSegment"), Ref("TildeSegment")),
    TildeSegment=StringParser("~", SymbolSegment, type="statement_terminator"),
    ParameterNameSegment=RegexParser(
        r"`?[A-Za-z0-9_]*`?", CodeSegment, type="parameter"
    ),
    SingleIdentifierGrammar=ansi_dialect.get_grammar("SingleIdentifierGrammar").copy(
        insert=[Ref("SessionVariableNameSegment")]
    ),
    AndOperatorGrammar=OneOf(
        StringParser("AND", BinaryOperatorSegment),
        StringParser("&&", BinaryOperatorSegment),
    ),
    OrOperatorGrammar=OneOf(
        StringParser("OR", BinaryOperatorSegment),
        StringParser("||", BinaryOperatorSegment),
        StringParser("XOR", BinaryOperatorSegment),
    ),
    NotOperatorGrammar=OneOf(
        StringParser("NOT", KeywordSegment, type="keyword"),
        StringParser("!", CodeSegment, type="not_operator"),
    ),
    Expression_C_Grammar=Sequence(
        Sequence(
            Ref("SessionVariableNameSegment"),
            Ref("WalrusOperatorSegment"),
            optional=True,
        ),
        ansi_dialect.get_grammar("Expression_C_Grammar"),
    ),
    ColumnConstraintDefaultGrammar=OneOf(
        Bracketed(ansi_dialect.get_grammar("ColumnConstraintDefaultGrammar")),
        ansi_dialect.get_grammar("ColumnConstraintDefaultGrammar"),
    ),
    NakedIdentifierSegment=SegmentGenerator(
        lambda dialect: RegexParser(
            r"([A-Z0-9_]*[A-Z][A-Z0-9_]*)|_",
            IdentifierSegment,
            type="naked_identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
)

mysql_dialect.add(
    DoubleQuotedLiteralSegment=TypedParser(
        "double_quote",
        LiteralSegment,
        type="quoted_literal",
        trim_chars=('"',),
    ),
    AtSignLiteralSegment=TypedParser(
        "at_sign_literal",
        LiteralSegment,
        type="at_sign_literal",
    ),
    SystemVariableSegment=RegexParser(
        r"@@(session|global)\.[A-Za-z0-9_]+",
        CodeSegment,
        type="system_variable",
    ),
    DoubleQuotedJSONPath=TypedParser(
        "double_quote",
        CodeSegment,
        type="json_path",
        trim_chars=('"',),
    ),
    SingleQuotedJSONPath=TypedParser(
        "single_quote",
        CodeSegment,
        type="json_path",
        trim_chars=("'",),
    ),
)


class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    """

    type = "alias_expression"
    match_grammar = Sequence(
        Indent,
        Ref.keyword("AS", optional=True),
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("QuotedLiteralSegment"),
        ),
        Dedent,
    )


class ColumnDefinitionSegment(BaseSegment):
    """A column definition, e.g. for CREATE TABLE or ALTER TABLE."""

    type = "column_definition"
    match_grammar = Sequence(
        Ref("SingleIdentifierGrammar"),  # Column name
        OneOf(  # Column type
            # DATETIME and TIMESTAMP take special logic
            Ref(
                "DatatypeSegment",
                exclude=OneOf("DATETIME", "TIMESTAMP"),
            ),
            Sequence(
                OneOf("DATETIME", "TIMESTAMP"),
                Bracketed(Ref("NumericLiteralSegment"), optional=True),  # Precision
                AnyNumberOf(
                    # Allow NULL/NOT NULL, DEFAULT, and ON UPDATE in any order
                    Sequence(Sequence("NOT", optional=True), "NULL", optional=True),
                    Sequence(
                        "DEFAULT",
                        OneOf(
                            Sequence(
                                OneOf("CURRENT_TIMESTAMP", "NOW"),
                                Bracketed(
                                    Ref("NumericLiteralSegment", optional=True),
                                    optional=True,
                                ),
                            ),
                            Ref("NumericLiteralSegment"),
                            Ref("QuotedLiteralSegment"),
                        ),
                        optional=True,
                    ),
                    Sequence(
                        "ON",
                        "UPDATE",
                        OneOf(
                            "CURRENT_TIMESTAMP",
                            "NOW",
                            Bracketed(
                                Ref("NumericLiteralSegment", optional=True),
                                optional=True,
                            ),
                        ),
                        optional=True,
                    ),
                    optional=True,
                ),
            ),
        ),
        Bracketed(Anything(), optional=True),  # For types like VARCHAR(100)
        AnyNumberOf(
            Ref("ColumnConstraintSegment", optional=True),
        ),
    )


class CreateTableStatementSegment(ansi.CreateTableStatementSegment):
    """Create table segment.

    https://dev.mysql.com/doc/refman/8.0/en/create-table.html
    """

    match_grammar = ansi.CreateTableStatementSegment.match_grammar.copy(
        insert=[
            AnyNumberOf(
                Sequence(
                    Ref.keyword("DEFAULT", optional=True),
                    Ref("ParameterNameSegment"),
                    Ref("EqualsSegment", optional=True),
                    OneOf(Ref("LiteralGrammar"), Ref("ParameterNameSegment")),
                ),
            ),
        ],
    )


class CreateUserStatementSegment(ansi.CreateUserStatementSegment):
    """`CREATE USER` statement.

    https://dev.mysql.com/doc/refman/8.0/en/create-user.html
    """

    match_grammar = Sequence(
        "CREATE",
        "USER",
        Ref("IfNotExistsGrammar", optional=True),
        Delimited(
            Sequence(
                Ref("RoleReferenceSegment"),
                Sequence(
                    Delimited(
                        Sequence(
                            "IDENTIFIED",
                            OneOf(
                                Sequence(
                                    "BY",
                                    OneOf(
                                        Sequence("RANDOM", "PASSWORD"),
                                        Ref("QuotedLiteralSegment"),
                                    ),
                                ),
                                Sequence(
                                    "WITH",
                                    Ref("ObjectReferenceSegment"),
                                    Sequence(
                                        OneOf(
                                            Sequence(
                                                "BY",
                                                OneOf(
                                                    Sequence("RANDOM", "PASSWORD"),
                                                    Ref("QuotedLiteralSegment"),
                                                ),
                                            ),
                                            Sequence("AS", Ref("QuotedLiteralSegment")),
                                            Sequence(
                                                "INITIAL",
                                                "AUTHENTICATION",
                                                "IDENTIFIED",
                                                OneOf(
                                                    Sequence(
                                                        "BY",
                                                        OneOf(
                                                            Sequence(
                                                                "RANDOM", "PASSWORD"
                                                            ),
                                                            Ref("QuotedLiteralSegment"),
                                                        ),
                                                    ),
                                                    Sequence(
                                                        "WITH",
                                                        Ref("ObjectReferenceSegment"),
                                                        "AS",
                                                        Ref("QuotedLiteralSegment"),
                                                    ),
                                                ),
                                            ),
                                        ),
                                        optional=True,
                                    ),
                                ),
                            ),
                        ),
                        delimiter="AND",
                    ),
                    optional=True,
                ),
            ),
        ),
        Sequence(
            "DEFAULT",
            "ROLE",
            Delimited(Ref("RoleReferenceSegment")),
            optional=True,
        ),
        Sequence(
            "REQUIRE",
            OneOf(
                "NONE",
                Delimited(
                    OneOf(
                        "SSL",
                        "X509",
                        Sequence("CIPHER", Ref("QuotedLiteralSegment")),
                        Sequence("ISSUER", Ref("QuotedLiteralSegment")),
                        Sequence("SUBJECT", Ref("QuotedLiteralSegment")),
                    ),
                    delimiter="AND",
                ),
            ),
            optional=True,
        ),
        Sequence(
            "WITH",
            AnyNumberOf(
                Sequence(
                    OneOf(
                        "MAX_QUERIES_PER_HOUR",
                        "MAX_UPDATES_PER_HOUR",
                        "MAX_CONNECTIONS_PER_HOUR",
                        "MAX_USER_CONNECTIONS",
                    ),
                    Ref("NumericLiteralSegment"),
                )
            ),
            optional=True,
        ),
        Sequence(
            AnyNumberOf(
                Sequence(
                    "PASSWORD",
                    "EXPIRE",
                    Sequence(
                        OneOf(
                            "DEFAULT",
                            "NEVER",
                            Sequence("INTERVAL", Ref("NumericLiteralSegment"), "DAY"),
                        ),
                        optional=True,
                    ),
                ),
                Sequence(
                    "PASSWORD",
                    "HISTORY",
                    OneOf("DEFAULT", Ref("NumericLiteralSegment")),
                ),
                Sequence(
                    "PASSWORD",
                    "REUSE",
                    "INTERVAL",
                    OneOf("DEFAULT", Sequence(Ref("NumericLiteralSegment"), "DAY")),
                ),
                Sequence(
                    "PASSWORD",
                    "REQUIRE",
                    "CURRENT",
                    Sequence(OneOf("DEFAULT", "OPTIONAL"), optional=True),
                ),
                Sequence("FAILED_LOGIN_ATTEMPTS", Ref("NumericLiteralSegment")),
                Sequence(
                    "PASSWORD_LOCK_TIME",
                    OneOf(Ref("NumericLiteralSegment"), "UNBOUNDED"),
                ),
            ),
            optional=True,
        ),
        Sequence("ACCOUNT", OneOf("UNLOCK", "LOCK"), optional=True),
        Sequence(
            OneOf("COMMENT", "ATTRIBUTE"),
            Ref("QuotedLiteralSegment"),
            optional=True,
        ),
    )


class UpsertClauseListSegment(BaseSegment):
    """An `ON DUPLICATE KEY UPDATE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/insert-on-duplicate.html
    """

    type = "upsert_clause_list"
    match_grammar = Sequence(
        "ON",
        "DUPLICATE",
        "KEY",
        "UPDATE",
        Delimited(Ref("SetClauseSegment")),
    )


class InsertRowAliasSegment(BaseSegment):
    """A row alias segment (used in `INSERT` statements).

    https://dev.mysql.com/doc/refman/8.0/en/insert.html
    """

    type = "insert_row_alias"
    match_grammar = Sequence(
        "AS",
        Ref("SingleIdentifierGrammar"),
        Bracketed(
            Ref("SingleIdentifierListSegment"),
            optional=True,
        ),
    )


class InsertStatementSegment(BaseSegment):
    """An `INSERT` statement.

    https://dev.mysql.com/doc/refman/8.0/en/insert.html
    """

    type = "insert_statement"
    match_grammar = Sequence(
        "INSERT",
        OneOf(
            "LOW_PRIORITY",
            "DELAYED",
            "HIGH_PRIORITY",
            optional=True,
        ),
        Ref.keyword("IGNORE", optional=True),
        Ref.keyword("INTO", optional=True),
        Ref("TableReferenceSegment"),
        Sequence(
            "PARTITION",
            Bracketed(
                Ref("SingleIdentifierListSegment"),
            ),
            optional=True,
        ),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        AnySetOf(
            OneOf(
                Ref("ValuesClauseSegment"),
                Ref("SetClauseListSegment"),
                Sequence(
                    OneOf(
                        Ref("SelectableGrammar"),
                        Sequence(
                            "TABLE",
                            Ref("TableReferenceSegment"),
                        ),
                    ),
                ),
                optional=False,
            ),
            Ref("InsertRowAliasSegment", optional=True),
            Ref("UpsertClauseListSegment", optional=True),
        ),
    )


class DeleteTargetTableSegment(BaseSegment):
    """A target table used in `DELETE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/delete.html
    """

    type = "delete_target_table"
    match_grammar = Sequence(
        Ref("TableReferenceSegment"),
        Sequence(Ref("DotSegment"), Ref("StarSegment"), optional=True),
    )


class DeleteUsingClauseSegment(BaseSegment):
    """A `USING` clause froma `DELETE` Statement`."""

    type = "using_clause"
    match_grammar = Sequence(
        "USING",
        Delimited(
            Ref("FromExpressionSegment"),
        ),
    )


class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/delete.html
    """

    type = "delete_statement"
    match_grammar = Sequence(
        "DELETE",
        Ref.keyword("LOW_PRIORITY", optional=True),
        Ref.keyword("QUICK", optional=True),
        Ref.keyword("IGNORE", optional=True),
        OneOf(
            Sequence(
                "FROM",
                Delimited(
                    Ref("DeleteTargetTableSegment"),
                    terminators=["USING"],
                ),
                Ref("DeleteUsingClauseSegment"),
                Ref("WhereClauseSegment", optional=True),
            ),
            Sequence(
                Delimited(
                    Ref("DeleteTargetTableSegment"),
                    terminators=["FROM"],
                ),
                Ref("FromClauseSegment"),
                Ref("WhereClauseSegment", optional=True),
            ),
            Sequence(
                Ref("FromClauseSegment"),
                Ref("SelectPartitionClauseSegment", optional=True),
                Ref("WhereClauseSegment", optional=True),
                Ref("OrderByClauseSegment", optional=True),
                Ref("LimitClauseSegment", optional=True),
            ),
        ),
    )


class ColumnConstraintSegment(ansi.ColumnConstraintSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    match_grammar: Matchable = OneOf(
        ansi.ColumnConstraintSegment.match_grammar,
        Sequence("CHARACTER", "SET", Ref("NakedIdentifierSegment")),
        Sequence("COLLATE", Ref("CollationReferenceSegment")),
    )


class IndexTypeGrammar(BaseSegment):
    """index_type in table_constraint."""

    type = "index_type"
    match_grammar = Sequence(
        "USING",
        OneOf("BTREE", "HASH"),
    )


class IndexOptionsSegment(BaseSegment):
    """index_option in `CREATE TABLE` and `ALTER TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/create-table.html
    https://dev.mysql.com/doc/refman/8.0/en/alter-table.html
    """

    type = "index_option"
    match_grammar = AnySetOf(
        Sequence(
            "KEY_BLOCK_SIZE",
            Ref("EqualsSegment", optional=True),
            Ref("NumericLiteralSegment"),
        ),
        Ref("IndexTypeGrammar"),
        Sequence("WITH", "PARSER", Ref("ObjectReferenceSegment")),
        Ref("CommentClauseSegment"),
        OneOf("VISIBLE", "INVISIBLE"),
        # (SECONDARY_)ENGINE_ATTRIBUTE supported in `CREATE TABLE`
        Sequence(
            "ENGINE_ATTRIBUTE",
            Ref("EqualsSegment", optional=True),
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            "SECONDARY_ENGINE_ATTRIBUTE",
            Ref("EqualsSegment", optional=True),
            Ref("QuotedLiteralSegment"),
        ),
    )


class TableConstraintSegment(BaseSegment):
    """A table constraint, e.g. for CREATE TABLE, ALTER TABLE.

    https://dev.mysql.com/doc/refman/8.0/en/create-table.html
    https://dev.mysql.com/doc/refman/8.0/en/alter-table.html
    """

    type = "table_constraint"
    # e.g. CONSTRAINT constraint_1 PRIMARY KEY(column_1)
    match_grammar = OneOf(
        Sequence(
            Sequence(  # [ CONSTRAINT <Constraint name> ]
                "CONSTRAINT",
                Ref("ObjectReferenceSegment", optional=True),
                optional=True,
            ),
            OneOf(
                # UNIQUE [INDEX | KEY] [index_name] [index_type] (key_part,...)
                # [index_option] ...
                Sequence(
                    "UNIQUE",
                    OneOf("INDEX", "KEY", optional=True),
                    Ref("IndexReferenceSegment", optional=True),
                    Ref("IndexTypeGrammar", optional=True),
                    Ref("BracketedKeyPartListGrammar"),
                    Ref("IndexOptionsSegment", optional=True),
                ),
                # PRIMARY KEY [index_type] (key_part,...) [index_option] ...
                Sequence(
                    Ref("PrimaryKeyGrammar"),
                    Ref("IndexTypeGrammar", optional=True),
                    # Columns making up PRIMARY KEY constraint
                    Ref("BracketedKeyPartListGrammar"),
                    Ref("IndexOptionsSegment", optional=True),
                ),
                # FOREIGN KEY [index_name] (col_name,...) reference_definition
                Sequence(
                    # REFERENCES reftable [ ( refcolumn [, ... ] ) ]
                    Ref("ForeignKeyGrammar"),
                    Ref("IndexReferenceSegment", optional=True),
                    # Local columns making up FOREIGN KEY constraint
                    Ref("BracketedColumnReferenceListGrammar"),
                    "REFERENCES",
                    Ref("ColumnReferenceSegment"),
                    # Foreign columns making up FOREIGN KEY constraint
                    Ref("BracketedColumnReferenceListGrammar"),
                    # Later add support for [MATCH FULL/PARTIAL/SIMPLE] ?
                    # Later add support for [ ON DELETE/UPDATE action ] ?
                    AnyNumberOf(
                        Sequence(
                            "ON",
                            OneOf("DELETE", "UPDATE"),
                            OneOf(
                                "RESTRICT",
                                "CASCADE",
                                Sequence("SET", "NULL"),
                                Sequence("NO", "ACTION"),
                                Sequence("SET", "DEFAULT"),
                            ),
                            optional=True,
                        ),
                    ),
                ),
                # CHECK (expr) [[NOT] ENFORCED]
                Sequence(
                    "CHECK",
                    Bracketed(Ref("ExpressionSegment")),
                    OneOf(
                        "ENFORCED",
                        Sequence("NOT", "ENFORCED"),
                        optional=True,
                    ),
                ),
            ),
        ),
        # {INDEX | KEY} [index_name] [index_type] (key_part,...) [index_option] ...
        Sequence(
            OneOf("INDEX", "KEY"),
            Ref("IndexReferenceSegment", optional=True),
            Ref("IndexTypeGrammar", optional=True),
            Ref("BracketedKeyPartListGrammar"),
            Ref("IndexOptionsSegment", optional=True),
        ),
        # {FULLTEXT | SPATIAL} [INDEX | KEY] [index_name] (key_part,...)
        # [index_option] ...
        Sequence(
            OneOf("FULLTEXT", "SPATIAL"),
            OneOf("INDEX", "KEY", optional=True),
            Ref("IndexReferenceSegment", optional=True),
            Ref("BracketedKeyPartListGrammar"),
            Ref("IndexOptionsSegment", optional=True),
        ),
    )


class CreateIndexStatementSegment(ansi.CreateIndexStatementSegment):
    """A `CREATE INDEX` statement.

    https://dev.mysql.com/doc/refman/8.0/en/create-index.html
    https://mariadb.com/kb/en/create-index/
    """

    match_grammar = Sequence(
        "CREATE",
        OneOf("UNIQUE", "FULLTEXT", "SPATIAL", optional=True),
        "INDEX",
        Ref("IndexReferenceSegment"),
        Ref("IndexTypeGrammar", optional=True),
        "ON",
        Ref("TableReferenceSegment"),
        Ref("BracketedKeyPartListGrammar"),
        Ref("IndexOptionsSegment", optional=True),
        AnySetOf(
            Sequence(
                "ALGORITHM",
                Ref("EqualsSegment", optional=True),
                OneOf("DEFAULT", "INPLACE", "COPY", "NOCOPY", "INSTANT"),
            ),
            Sequence(
                "LOCK",
                Ref("EqualsSegment", optional=True),
                OneOf("DEFAULT", "NONE", "SHARED", "EXCLUSIVE"),
            ),
        ),
    )


class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment.

    https://dev.mysql.com/doc/refman/8.0/en/date-and-time-functions.html#function_adddate
    """

    type = "interval_expression"
    match_grammar = Sequence(
        "INTERVAL",
        Ref("ExpressionSegment"),
        Ref("DatetimeUnitSegment"),
    )


mysql_dialect.add(
    OutputParameterSegment=StringParser(
        "OUT", SymbolSegment, type="parameter_direction"
    ),
    InputParameterSegment=StringParser("IN", SymbolSegment, type="parameter_direction"),
    InputOutputParameterSegment=StringParser(
        "INOUT", SymbolSegment, type="parameter_direction"
    ),
    ProcedureParameterGrammar=OneOf(
        Sequence(
            OneOf(
                Ref("OutputParameterSegment"),
                Ref("InputParameterSegment"),
                Ref("InputOutputParameterSegment"),
                optional=True,
            ),
            Ref("ParameterNameSegment", optional=True),
            Ref("DatatypeSegment"),
        ),
        Ref("DatatypeSegment"),
    ),
    LocalVariableNameSegment=RegexParser(
        r"`?[a-zA-Z0-9_$]*`?",
        CodeSegment,
        type="variable",
    ),
    SessionVariableNameSegment=RegexParser(
        r"[@][a-zA-Z0-9_$]*",
        CodeSegment,
        type="variable",
    ),
    WalrusOperatorSegment=StringParser(":=", SymbolSegment, type="assignment_operator"),
    VariableAssignmentSegment=Sequence(
        Ref("SessionVariableNameSegment"),
        Ref("WalrusOperatorSegment"),
        Ref("BaseExpressionElementGrammar"),
    ),
    ColumnPathOperatorSegment=StringParser(
        "->", SymbolSegment, type="column_path_operator"
    ),
    InlinePathOperatorSegment=StringParser(
        "->>", SymbolSegment, type="column_path_operator"
    ),
    BooleanDynamicSystemVariablesGrammar=OneOf(
        # Boolean dynamic system variables can be set to ON/OFF, TRUE/FALSE, or 0/1:
        # https://dev.mysql.com/doc/refman/8.0/en/dynamic-system-variables.html
        # This allows us to match ON/OFF & TRUE/FALSE as keywords and therefore apply
        # the correct capitalisation policy.
        OneOf("ON", "OFF"),
        OneOf("TRUE", "FALSE"),
    ),
    # (key_part, ...)
    # key_part: {col_name [(length)] | (expr)} [ASC | DESC]
    # https://dev.mysql.com/doc/refman/8.0/en/create-table.html
    # https://dev.mysql.com/doc/refman/8.0/en/alter-table.html
    # https://dev.mysql.com/doc/refman/8.0/en/create-index.html
    BracketedKeyPartListGrammar=Bracketed(
        Delimited(
            Sequence(
                OneOf(
                    Ref("ColumnReferenceSegment"),
                    Sequence(
                        Ref("ColumnReferenceSegment"),
                        Bracketed(Ref("NumericLiteralSegment")),
                    ),
                    Bracketed(Ref("ExpressionSegment")),
                ),
                OneOf("ASC", "DESC", optional=True),
            ),
        ),
    ),
)


mysql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "at_sign",
            r"@@?[a-zA-Z0-9_$]*(\.[a-zA-Z0-9_$]+)?",
            CodeSegment,
            segment_kwargs={"type": "at_sign_literal", "trim_chars": ("@",)},
        ),
    ],
    before="word",
)


mysql_dialect.insert_lexer_matchers(
    [
        StringLexer("double_ampersand", "&&", CodeSegment),
    ],
    before="ampersand",
)


mysql_dialect.insert_lexer_matchers(
    [
        StringLexer("double_vertical_bar", "||", CodeSegment),
    ],
    before="vertical_bar",
)


mysql_dialect.insert_lexer_matchers(
    [
        StringLexer("walrus_operator", ":=", CodeSegment),
    ],
    before="equals",
)


mysql_dialect.insert_lexer_matchers(
    [
        StringLexer("inline_path_operator", "->>", CodeSegment),
        StringLexer("column_path_operator", "->", CodeSegment),
    ],
    before="greater_than",
)


class RoleReferenceSegment(ansi.RoleReferenceSegment):
    """A reference to an account, role, or user.

    https://dev.mysql.com/doc/refman/8.0/en/account-names.html
    https://dev.mysql.com/doc/refman/8.0/en/role-names.html
    """

    match_grammar: Matchable = OneOf(
        Sequence(
            OneOf(
                Ref("NakedIdentifierSegment"),
                Ref("QuotedIdentifierSegment"),
                Ref("SingleQuotedIdentifierSegment"),
                Ref("DoubleQuotedLiteralSegment"),
            ),
            Sequence(
                Ref("AtSignLiteralSegment"),
                OneOf(
                    Ref("NakedIdentifierSegment"),
                    Ref("QuotedIdentifierSegment"),
                    Ref("SingleQuotedIdentifierSegment"),
                    Ref("DoubleQuotedLiteralSegment"),
                ),
                optional=True,
                allow_gaps=False,
            ),
            allow_gaps=True,
        ),
        "CURRENT_USER",
    )


class DeclareStatement(BaseSegment):
    """DECLARE statement.

    https://dev.mysql.com/doc/refman/8.0/en/declare-local-variable.html
    https://dev.mysql.com/doc/refman/8.0/en/declare-handler.html
    https://dev.mysql.com/doc/refman/8.0/en/declare-condition.html
    https://dev.mysql.com/doc/refman/8.0/en/declare-cursor.html
    """

    type = "declare_statement"

    match_grammar = OneOf(
        Sequence(
            "DECLARE",
            Ref("NakedIdentifierSegment"),
            "CURSOR",
            "FOR",
            Ref("StatementSegment"),
        ),
        Sequence(
            "DECLARE",
            OneOf("CONTINUE", "EXIT", "UNDO"),
            "HANDLER",
            "FOR",
            OneOf(
                "SQLEXCEPTION",
                "SQLWARNING",
                Sequence("NOT", "FOUND"),
                Sequence(
                    "SQLSTATE",
                    Ref.keyword("VALUE", optional=True),
                    Ref("QuotedLiteralSegment"),
                ),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("NakedIdentifierSegment"),
                ),
            ),
            Sequence(Ref("StatementSegment")),
        ),
        Sequence(
            "DECLARE",
            Ref("NakedIdentifierSegment"),
            "CONDITION",
            "FOR",
            OneOf(Ref("QuotedLiteralSegment"), Ref("NumericLiteralSegment")),
        ),
        Sequence(
            "DECLARE",
            Ref("LocalVariableNameSegment"),
            Ref("DatatypeSegment"),
            Sequence(
                Ref.keyword("DEFAULT"),
                OneOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("FunctionSegment"),
                ),
                optional=True,
            ),
        ),
    )


class StatementSegment(ansi.StatementSegment):
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi.StatementSegment.match_grammar.copy(
        insert=[
            Ref("DelimiterStatement"),
            Ref("CreateProcedureStatementSegment"),
            Ref("DeclareStatement"),
            Ref("SetAssignmentStatementSegment"),
            Ref("IfExpressionStatement"),
            Ref("WhileStatementSegment"),
            Ref("IterateStatementSegment"),
            Ref("RepeatStatementSegment"),
            Ref("LoopStatementSegment"),
            Ref("CallStoredProcedureSegment"),
            Ref("PrepareSegment"),
            Ref("ExecuteSegment"),
            Ref("DeallocateSegment"),
            Ref("GetDiagnosticsSegment"),
            Ref("ResignalSegment"),
            Ref("CursorOpenCloseSegment"),
            Ref("CursorFetchSegment"),
            Ref("DropProcedureStatementSegment"),
            Ref("AlterTableStatementSegment"),
            Ref("AlterViewStatementSegment"),
            Ref("CreateViewStatementSegment"),
            Ref("RenameTableStatementSegment"),
            Ref("ResetMasterStatementSegment"),
            Ref("PurgeBinaryLogsStatementSegment"),
            Ref("HelpStatementSegment"),
            Ref("CheckTableStatementSegment"),
            Ref("ChecksumTableStatementSegment"),
            Ref("AnalyzeTableStatementSegment"),
            Ref("RepairTableStatementSegment"),
            Ref("OptimizeTableStatementSegment"),
            Ref("UpsertClauseListSegment"),
            Ref("InsertRowAliasSegment"),
            Ref("FlushStatementSegment"),
            Ref("LoadDataSegment"),
            Ref("ReplaceSegment"),
            Ref("AlterDatabaseStatementSegment"),
            Ref("ReturnStatementSegment"),
            Ref("SetNamesStatementSegment"),
        ],
        remove=[
            # handle CREATE SCHEMA in CreateDatabaseStatementSegment
            Ref("CreateSchemaStatementSegment"),
        ],
    )


class DelimiterStatement(BaseSegment):
    """DELIMITER statement."""

    type = "delimiter_statement"

    match_grammar = Ref.keyword("DELIMITER")


class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE PROCEDURE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/create-procedure.html
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("DefinerSegment", optional=True),
        "PROCEDURE",
        Ref("FunctionNameSegment"),
        Ref("ProcedureParameterListGrammar", optional=True),
        Ref("CommentClauseSegment", optional=True),
        Ref("CharacteristicStatement", optional=True),
        Ref("FunctionDefinitionGrammar"),
    )


class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION` statement."""

    type = "function_definition"
    match_grammar = Ref("TransactionStatementSegment")


class CharacteristicStatement(BaseSegment):
    """A Characteristics statement for functions/procedures."""

    type = "characteristic_statement"

    match_grammar = Sequence(
        OneOf("DETERMINISTIC", Sequence("NOT", "DETERMINISTIC")),
        Sequence("LANGUAGE", "SQL", optional=True),
        OneOf(
            Sequence("CONTAINS", "SQL", optional=True),
            Sequence("NO", "SQL", optional=True),
            Sequence("READS", "SQL", "DATA", optional=True),
            Sequence("MODIFIES", "SQL", "DATA", optional=True),
            optional=True,
        ),
        Sequence("SQL", "SECURITY", OneOf("DEFINER", "INVOKER"), optional=True),
    )


class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    https://dev.mysql.com/doc/refman/8.0/en/create-procedure.html
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("DefinerSegment", optional=True),
        "FUNCTION",
        Ref("FunctionNameSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        Sequence(
            "RETURNS",
            Ref("DatatypeSegment"),
        ),
        Ref("CommentClauseSegment", optional=True),
        Ref("CharacteristicStatement"),
        Ref("FunctionDefinitionGrammar"),
    )


class AlterTableStatementSegment(BaseSegment):
    """An `ALTER TABLE .. ALTER COLUMN` statement.

    Overriding ANSI to add `CHANGE COLUMN` and `DROP COLUMN` support.

    https://dev.mysql.com/doc/refman/8.0/en/alter-table.html
    https://mariadb.com/kb/en/alter-table/

    """

    type = "alter_table_statement"
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
                # Add column
                Sequence(
                    "ADD",
                    Ref.keyword("COLUMN", optional=True),
                    Ref("IfNotExistsGrammar", optional=True),
                    Ref("ColumnDefinitionSegment"),
                    OneOf(
                        "FIRST",
                        Sequence("AFTER", Ref("ColumnReferenceSegment")),
                        # Bracketed Version of the same
                        Ref("BracketedColumnReferenceListGrammar"),
                        optional=True,
                    ),
                ),
                Sequence(
                    "MODIFY",
                    Ref.keyword("COLUMN", optional=True),
                    Ref("ColumnDefinitionSegment"),
                    OneOf(
                        "FIRST",
                        Sequence("AFTER", Ref("ColumnReferenceSegment")),
                        # Bracketed Version of the same
                        Ref("BracketedColumnReferenceListGrammar"),
                        optional=True,
                    ),
                ),
                # Add constraint
                Sequence(
                    "ADD",
                    Ref("TableConstraintSegment"),
                ),
                # Change column
                Sequence(
                    "CHANGE",
                    Ref.keyword("COLUMN", optional=True),
                    Ref("ColumnReferenceSegment"),
                    Ref("ColumnDefinitionSegment"),
                    OneOf(
                        Sequence(
                            OneOf(
                                "FIRST",
                                Sequence("AFTER", Ref("ColumnReferenceSegment")),
                            ),
                        ),
                        optional=True,
                    ),
                ),
                # Drop column
                Sequence(
                    "DROP",
                    OneOf(
                        Sequence(
                            Ref.keyword("COLUMN", optional=True),
                            Ref("ColumnReferenceSegment"),
                        ),
                        Sequence(
                            OneOf("INDEX", "KEY", optional=True),
                            Ref("IndexReferenceSegment"),
                        ),
                        Ref("PrimaryKeyGrammar"),
                        Sequence(
                            Ref("ForeignKeyGrammar"),
                            Ref("ObjectReferenceSegment"),
                        ),
                        Sequence(
                            OneOf("CHECK", "CONSTRAINT"),
                            Ref("ObjectReferenceSegment"),
                        ),
                    ),
                ),
                # Alter constraint
                Sequence(
                    "ALTER",
                    OneOf("CHECK", "CONSTRAINT"),
                    Ref("ObjectReferenceSegment"),
                    OneOf(
                        "ENFORCED",
                        Sequence("NOT", "ENFORCED"),
                    ),
                ),
                # Alter index
                Sequence(
                    "ALTER",
                    "INDEX",
                    Ref("IndexReferenceSegment"),
                    OneOf("VISIBLE", "INVISIBLE"),
                ),
                # Rename
                Sequence(
                    "RENAME",
                    OneOf(
                        # Rename table
                        Sequence(
                            OneOf("AS", "TO", optional=True),
                            Ref("TableReferenceSegment"),
                        ),
                        # Rename index
                        Sequence(
                            OneOf("INDEX", "KEY"),
                            Ref("IndexReferenceSegment"),
                            "TO",
                            Ref("IndexReferenceSegment"),
                        ),
                        # Rename column
                        Sequence(
                            "COLUMN",
                            Ref("ColumnReferenceSegment"),
                            "TO",
                            Ref("ColumnReferenceSegment"),
                        ),
                    ),
                ),
                # Enable/Disable updating nonunique indexes
                Sequence(
                    OneOf("DISABLE", "ENABLE"),
                    "KEYS",
                ),
            ),
        ),
    )


class WithCheckOptionSegment(BaseSegment):
    """WITH [CASCADED | LOCAL] CHECK OPTION for CREATE/ALTER View Syntax.

    As specified in https://dev.mysql.com/doc/refman/8.0/en/alter-view.html
    """

    type = "with_check_options"

    match_grammar: Matchable = Sequence(
        "WITH",
        OneOf("CASCADED", "LOCAL", optional=True),
        "CHECK",
        "OPTION",
    )


class AlterViewStatementSegment(BaseSegment):
    """An `ALTER VIEW .. AS ..` statement.

    As specified in https://dev.mysql.com/doc/refman/8.0/en/alter-view.html
    """

    type = "alter_view_statement"

    match_grammar = Sequence(
        "ALTER",
        Sequence(
            "ALGORITHM",
            Ref("EqualsSegment"),
            OneOf("UNDEFINED", "MERGE", "TEMPTABLE"),
            optional=True,
        ),
        Ref("DefinerSegment", optional=True),
        Sequence("SQL", "SECURITY", OneOf("DEFINER", "INVOKER"), optional=True),
        "VIEW",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        OptionallyBracketed(
            OneOf(
                Ref("SelectStatementSegment"),
                Ref("SetExpressionSegment"),
            )
        ),
        Ref("WithCheckOptionSegment", optional=True),
    )


class CreateViewStatementSegment(BaseSegment):
    """An `CREATE VIEW .. AS ..` statement.

    As specified in https://dev.mysql.com/doc/refman/8.0/en/create-view.html
    """

    type = "create_view_statement"

    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence(
            "ALGORITHM",
            Ref("EqualsSegment"),
            OneOf("UNDEFINED", "MERGE", "TEMPTABLE"),
            optional=True,
        ),
        Ref("DefinerSegment", optional=True),
        Sequence("SQL", "SECURITY", OneOf("DEFINER", "INVOKER"), optional=True),
        "VIEW",
        Ref("TableReferenceSegment"),
        Ref("BracketedColumnReferenceListGrammar", optional=True),
        "AS",
        OptionallyBracketed(
            OneOf(
                Ref("SelectStatementSegment"),
                Ref("SetExpressionSegment"),
            )
        ),
        Ref("WithCheckOptionSegment", optional=True),
    )


class ProcedureParameterListGrammar(BaseSegment):
    """The parameters for a procedure ie. `(in/out/inout name datatype)`."""

    type = "procedure_parameter_list"
    match_grammar = Bracketed(
        Delimited(
            Ref("ProcedureParameterGrammar"),
            optional=True,
        ),
    )


class SetAssignmentStatementSegment(BaseSegment):
    """A `SET` statement.

    https://dev.mysql.com/doc/refman/8.0/en/set-variable.html
    """

    type = "set_statement"

    match_grammar = Sequence(
        "SET",
        Delimited(
            Sequence(
                OneOf(
                    Ref("SessionVariableNameSegment"), Ref("LocalVariableNameSegment")
                ),
                OneOf(
                    Ref("EqualsSegment"),
                    Ref("WalrusOperatorSegment"),
                ),
                AnyNumberOf(
                    Ref("QuotedLiteralSegment"),
                    Ref("DoubleQuotedLiteralSegment"),
                    Ref("SessionVariableNameSegment"),
                    # Match boolean keywords before local variables.
                    Ref("BooleanDynamicSystemVariablesGrammar"),
                    Ref("LocalVariableNameSegment"),
                    Ref("FunctionSegment"),
                    Ref("ArithmeticBinaryOperatorGrammar"),
                    Ref("ExpressionSegment"),
                ),
            ),
        ),
    )


class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement.

    https://dev.mysql.com/doc/refman/8.0/en/commit.html
    https://dev.mysql.com/doc/refman/8.0/en/begin-end.html
    """

    type = "transaction_statement"

    match_grammar = OneOf(
        Sequence("START", "TRANSACTION"),
        Sequence(
            Sequence(
                Ref("SingleIdentifierGrammar"), Ref("ColonSegment"), optional=True
            ),
            Sequence(
                "BEGIN",
                Ref.keyword("WORK", optional=True),
                Ref("StatementSegment"),
            ),
        ),
        Sequence(
            "LEAVE",
            Ref("SingleIdentifierGrammar", optional=True),
        ),
        Sequence(
            "COMMIT",
            Ref.keyword("WORK", optional=True),
            Sequence("AND", Ref.keyword("NO", optional=True), "CHAIN", optional=True),
        ),
        Sequence(
            "ROLLBACK",
            Ref.keyword("WORK", optional=True),
        ),
        Sequence(
            "END",
            Ref("SingleIdentifierGrammar", optional=True),
        ),
    )


class IfExpressionStatement(BaseSegment):
    """IF-THEN-ELSE-ELSEIF-END IF statement.

    https://dev.mysql.com/doc/refman/8.0/en/if.html
    """

    type = "if_then_statement"

    match_grammar = AnyNumberOf(
        Sequence(
            "IF",
            Ref("ExpressionSegment"),
            "THEN",
            Ref("StatementSegment"),
        ),
        Sequence(
            "ELSEIF",
            Ref("ExpressionSegment"),
            "THEN",
            Ref("StatementSegment"),
        ),
        Sequence("ELSE", Ref("StatementSegment"), optional=True),
        Sequence("END", "IF"),
    )


class DefinerSegment(BaseSegment):
    """This is the body of a `CREATE FUNCTION` and `CREATE TRIGGER` statements."""

    type = "definer_segment"

    match_grammar = Sequence(
        "DEFINER",
        Ref("EqualsSegment"),
        Ref("RoleReferenceSegment"),
    )


class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = Sequence(
        OneOf("DISTINCT", "ALL", "DISTINCTROW", optional=True),
        Ref.keyword("HIGH_PRIORITY", optional=True),
        Ref.keyword("STRAIGHT_JOIN", optional=True),
        Ref.keyword("SQL_SMALL_RESULT", optional=True),
        Ref.keyword("SQL_BIG_RESULT", optional=True),
        Ref.keyword("SQL_BUFFER_RESULT", optional=True),
        Ref.keyword("SQL_CACHE", optional=True),
        Ref.keyword("SQL_NO_CACHE", optional=True),
        Ref.keyword("SQL_CALC_FOUND_ROWS", optional=True),
        optional=True,
    )


class IntoClauseSegment(BaseSegment):
    """This is an `INTO` clause for assigning variables in a select statement.

    https://dev.mysql.com/doc/refman/5.7/en/load-data.html
    https://dev.mysql.com/doc/refman/5.7/en/select-into.html
    """

    type = "into_clause"

    match_grammar = Sequence(
        "INTO",
        OneOf(
            Delimited(
                AnyNumberOf(
                    Ref("SessionVariableNameSegment"),
                    Ref("LocalVariableNameSegment"),
                ),
                Sequence("DUMPFILE", Ref("QuotedLiteralSegment")),
                Sequence(
                    "OUTFILE",
                    Ref("QuotedLiteralSegment"),
                    Sequence(
                        "CHARACTER", "SET", Ref("NakedIdentifierSegment"), optional=True
                    ),
                    Sequence(
                        OneOf("FIELDS", "COLUMNS"),
                        Sequence(
                            "TERMINATED",
                            "BY",
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                        Sequence(
                            Ref.keyword("OPTIONALLY", optional=True),
                            "ENCLOSED",
                            "BY",
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                        Sequence(
                            "ESCAPED", "BY", Ref("QuotedLiteralSegment"), optional=True
                        ),
                        optional=True,
                    ),
                    Sequence(
                        "LINES",
                        Sequence(
                            "STARTING", "BY", Ref("QuotedLiteralSegment"), optional=True
                        ),
                        Sequence(
                            "TERMINATED",
                            "BY",
                            Ref("QuotedLiteralSegment"),
                            optional=True,
                        ),
                        optional=True,
                    ),
                ),
            ),
        ),
        parse_mode=ParseMode.GREEDY_ONCE_STARTED,
        terminators=[Ref("SelectClauseTerminatorGrammar")],
    )


class UnorderedSelectStatementSegment(ansi.UnorderedSelectStatementSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    This is designed for use in the context of set operations,
    for other use cases, we should use the main
    SelectStatementSegment.
    """

    type = "select_statement"

    match_grammar = (
        ansi.UnorderedSelectStatementSegment.match_grammar.copy(
            insert=[Ref("IntoClauseSegment", optional=True)],
            before=Ref("FromClauseSegment", optional=True),
        )
        .copy(insert=[Ref("ForClauseSegment", optional=True)])
        .copy(
            insert=[Ref("IndexHintClauseSegment", optional=True)],
            before=Ref("WhereClauseSegment", optional=True),
        )
        .copy(
            insert=[Ref("SelectPartitionClauseSegment", optional=True)],
            before=Ref("WhereClauseSegment", optional=True),
            terminators=[
                Ref("IntoClauseSegment"),
                Ref("ForClauseSegment"),
                Ref("IndexHintClauseSegment"),
                Ref("SelectPartitionClauseSegment"),
                Ref("UpsertClauseListSegment"),
            ],
        )
    )


class SelectClauseSegment(ansi.SelectClauseSegment):
    """A group of elements in a select target statement."""

    match_grammar = ansi.SelectClauseSegment.match_grammar.copy(
        terminators=[Ref("IntoKeywordSegment")],
    )


class SelectStatementSegment(ansi.SelectStatementSegment):
    """A `SELECT` statement.

    https://dev.mysql.com/doc/refman/5.7/en/select.html
    """

    # Inherit most of the parse grammar from the original.
    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("LimitClauseSegment", optional=True),
            Ref("NamedWindowSegment", optional=True),
            Ref("IntoClauseSegment", optional=True),
        ],
        terminators=[
            Ref("SetOperatorSegment"),
            Ref("UpsertClauseListSegment"),
            Ref("WithCheckOptionSegment"),
        ],
        # Overwrite the terminators, because we want to remove some from the
        # expression above.
        replace_terminators=True,
    )


class ForClauseSegment(BaseSegment):
    """This is the body of a `FOR` clause."""

    type = "for_clause"

    match_grammar = OneOf(
        Sequence(
            Sequence(
                "FOR",
                OneOf("UPDATE", "SHARE"),
            ),
            Sequence("OF", Delimited(Ref("NakedIdentifierSegment")), optional=True),
            OneOf("NOWAIT", Sequence("SKIP", "LOCKED"), optional=True),
        ),
        Sequence("LOCK", "IN", "SHARE", "MODE"),
        optional=True,
    )


class IndexHintClauseSegment(BaseSegment):
    """This is the body of an index hint clause."""

    type = "index_hint_clause"

    match_grammar = Sequence(
        OneOf("USE", "IGNORE", "FORCE"),
        OneOf("INDEX", "KEY"),
        Sequence(
            "FOR",
            OneOf(
                "JOIN", Sequence("ORDER", "BY"), Sequence("GROUP", "BY"), optional=True
            ),
            optional=True,
        ),
        Bracketed(Ref("ObjectReferenceSegment")),
        Ref("JoinOnConditionSegment", optional=True),
    )


class CallStoredProcedureSegment(BaseSegment):
    """This is a CALL statement used to execute a stored procedure.

    https://dev.mysql.com/doc/refman/8.0/en/call.html
    """

    type = "call_segment"

    match_grammar = Sequence(
        "CALL",
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("QuotedIdentifierSegment"),
        ),
        Bracketed(
            AnyNumberOf(
                Delimited(
                    Ref("QuotedLiteralSegment"),
                    Ref("NumericLiteralSegment"),
                    Ref("DoubleQuotedLiteralSegment"),
                    Ref("SessionVariableNameSegment"),
                    Ref("LocalVariableNameSegment"),
                    Ref("FunctionSegment"),
                ),
            ),
        ),
    )


class SelectPartitionClauseSegment(BaseSegment):
    """This is the body of a partition clause."""

    type = "partition_clause"

    match_grammar = Sequence(
        "PARTITION",
        Bracketed(Delimited(Ref("ObjectReferenceSegment"))),
    )


class WhileStatementSegment(BaseSegment):
    """A `WHILE-DO-END WHILE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/while.html
    """

    type = "while_statement"

    match_grammar = OneOf(
        Sequence(
            Sequence(
                Ref("SingleIdentifierGrammar"), Ref("ColonSegment"), optional=True
            ),
            Sequence(
                "WHILE",
                Ref("ExpressionSegment"),
                "DO",
                AnyNumberOf(
                    Ref("StatementSegment"),
                ),
            ),
        ),
        Sequence(
            "END",
            "WHILE",
            Ref("SingleIdentifierGrammar", optional=True),
        ),
    )


class PrepareSegment(BaseSegment):
    """This is the body of a `PREPARE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/prepare.html
    """

    type = "prepare_segment"

    match_grammar = Sequence(
        "PREPARE",
        Ref("NakedIdentifierSegment"),
        "FROM",
        OneOf(
            Ref("QuotedLiteralSegment"),
            Ref("SessionVariableNameSegment"),
            Ref("LocalVariableNameSegment"),
        ),
    )


class GetDiagnosticsSegment(BaseSegment):
    """This is the body of a `GET DIAGNOSTICS` statement.

    https://dev.mysql.com/doc/refman/8.0/en/get-diagnostics.html
    """

    type = "get_diagnostics_segment"

    match_grammar = Sequence(
        "GET",
        Sequence("CURRENT", "STACKED", optional=True),
        "DIAGNOSTICS",
        Delimited(
            Sequence(
                OneOf(
                    Ref("SessionVariableNameSegment"), Ref("LocalVariableNameSegment")
                ),
                Ref("EqualsSegment"),
                OneOf("NUMBER", "ROW_COUNT"),
            ),
            optional=True,
        ),
        "CONDITION",
        OneOf(
            Ref("SessionVariableNameSegment"),
            Ref("LocalVariableNameSegment"),
            Ref("NumericLiteralSegment"),
        ),
        Delimited(
            Sequence(
                OneOf(
                    Ref("SessionVariableNameSegment"), Ref("LocalVariableNameSegment")
                ),
                Ref("EqualsSegment"),
                OneOf(
                    "CLASS_ORIGIN",
                    "SUBCLASS_ORIGIN",
                    "RETURNED_SQLSTATE",
                    "MESSAGE_TEXT",
                    "MYSQL_ERRNO",
                    "CONSTRAINT_CATALOG",
                    "CONSTRAINT_SCHEMA",
                    "CONSTRAINT_NAME",
                    "CATALOG_NAME",
                    "SCHEMA_NAME",
                    "TABLE_NAME",
                    "COLUMN_NAME",
                    "CURSOR_NAME",
                ),
            ),
            optional=True,
        ),
    )


class LoopStatementSegment(BaseSegment):
    """A `LOOP` statement.

    https://dev.mysql.com/doc/refman/8.0/en/loop.html
    """

    type = "loop_statement"

    match_grammar = OneOf(
        Sequence(
            Sequence(
                Ref("SingleIdentifierGrammar"), Ref("ColonSegment"), optional=True
            ),
            "LOOP",
            Delimited(
                Ref("StatementSegment"),
            ),
        ),
        Sequence(
            "END",
            "LOOP",
            Ref("SingleIdentifierGrammar", optional=True),
        ),
    )


class CursorOpenCloseSegment(BaseSegment):
    """This is a CLOSE or Open statement.

    https://dev.mysql.com/doc/refman/8.0/en/close.html
    https://dev.mysql.com/doc/refman/8.0/en/open.html
    """

    type = "cursor_open_close_segment"

    match_grammar = Sequence(
        OneOf("CLOSE", "OPEN"),
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Ref("QuotedIdentifierSegment"),
        ),
    )


class IterateStatementSegment(BaseSegment):
    """A `ITERATE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/iterate.html
    """

    type = "iterate_statement"

    match_grammar = Sequence(
        "ITERATE",
        Ref("SingleIdentifierGrammar"),
    )


class ExecuteSegment(BaseSegment):
    """This is the body of a `EXECUTE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/execute.html
    """

    type = "execute_segment"

    match_grammar = Sequence(
        "EXECUTE",
        Ref("NakedIdentifierSegment"),
        Sequence("USING", Delimited(Ref("SessionVariableNameSegment")), optional=True),
    )


class RepeatStatementSegment(BaseSegment):
    """A `REPEAT-UNTIL` statement.

    https://dev.mysql.com/doc/refman/8.0/en/repeat.html
    """

    type = "repeat_statement"

    match_grammar = OneOf(
        Sequence(
            Sequence(
                Ref("SingleIdentifierGrammar"), Ref("ColonSegment"), optional=True
            ),
            "REPEAT",
            AnyNumberOf(
                Ref("StatementSegment"),
            ),
        ),
        Sequence(
            "UNTIL",
            Ref("ExpressionSegment"),
            Sequence(
                "END",
                "REPEAT",
                Ref("SingleIdentifierGrammar", optional=True),
            ),
        ),
    )


class DeallocateSegment(BaseSegment):
    """This is the body of a `DEALLOCATE/DROP` statement.

    https://dev.mysql.com/doc/refman/8.0/en/deallocate-prepare.html
    """

    type = "deallocate_segment"

    match_grammar = Sequence(
        Sequence(OneOf("DEALLOCATE", "DROP"), "PREPARE"),
        Ref("NakedIdentifierSegment"),
    )


class ResignalSegment(BaseSegment):
    """This is the body of a `RESIGNAL` statement.

    https://dev.mysql.com/doc/refman/8.0/en/resignal.html
    """

    type = "resignal_segment"

    match_grammar = Sequence(
        OneOf("SIGNAL", "RESIGNAL"),
        OneOf(
            Sequence(
                "SQLSTATE",
                Ref.keyword("VALUE", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
            Ref("NakedIdentifierSegment"),
            optional=True,
        ),
        Sequence(
            "SET",
            Delimited(
                Sequence(
                    OneOf(
                        "CLASS_ORIGIN",
                        "SUBCLASS_ORIGIN",
                        "RETURNED_SQLSTATE",
                        "MESSAGE_TEXT",
                        "MYSQL_ERRNO",
                        "CONSTRAINT_CATALOG",
                        "CONSTRAINT_SCHEMA",
                        "CONSTRAINT_NAME",
                        "CATALOG_NAME",
                        "SCHEMA_NAME",
                        "TABLE_NAME",
                        "COLUMN_NAME",
                        "CURSOR_NAME",
                    ),
                    Ref("EqualsSegment"),
                    OneOf(
                        Ref("SessionVariableNameSegment"),
                        Ref("LocalVariableNameSegment"),
                        Ref("QuotedLiteralSegment"),
                    ),
                ),
            ),
            optional=True,
        ),
    )


class CursorFetchSegment(BaseSegment):
    """This is a FETCH statement.

    https://dev.mysql.com/doc/refman/8.0/en/fetch.html
    """

    type = "cursor_fetch_segment"

    match_grammar = Sequence(
        "FETCH",
        Sequence(Ref.keyword("NEXT", optional=True), "FROM", optional=True),
        Ref("NakedIdentifierSegment"),
        "INTO",
        Delimited(
            Ref("SessionVariableNameSegment"),
            Ref("LocalVariableNameSegment"),
        ),
    )


class DropIndexStatementSegment(ansi.DropIndexStatementSegment):
    """A `DROP INDEX` statement.

    https://dev.mysql.com/doc/refman/8.0/en/drop-index.html
    """

    # DROP INDEX <Index name> ON <table_name>
    # [ALGORITHM [=] {DEFAULT | INPLACE | COPY} | LOCK [=] {DEFAULT | NONE | SHARED |
    # EXCLUSIVE}]
    match_grammar = Sequence(
        "DROP",
        "INDEX",
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        OneOf(
            Sequence(
                "ALGORITHM",
                Ref("EqualsSegment", optional=True),
                OneOf("DEFAULT", "INPLACE", "COPY"),
            ),
            Sequence(
                "LOCK",
                Ref("EqualsSegment", optional=True),
                OneOf("DEFAULT", "NONE", "SHARED", "EXCLUSIVE"),
            ),
            optional=True,
        ),
    )


class DropProcedureStatementSegment(BaseSegment):
    """A `DROP` statement that addresses stored procedures and functions.

    https://dev.mysql.com/doc/refman/8.0/en/drop-procedure.html
    """

    type = "drop_procedure_statement"

    # DROP {PROCEDURE | FUNCTION} [IF EXISTS] sp_name
    match_grammar = Sequence(
        "DROP",
        OneOf("PROCEDURE", "FUNCTION"),
        Ref("IfExistsGrammar", optional=True),
        Ref("ObjectReferenceSegment"),
    )


class DropFunctionStatementSegment(BaseSegment):
    """A `DROP` statement that addresses loadable functions.

    https://dev.mysql.com/doc/refman/8.0/en/drop-function-loadable.html
    """

    type = "drop_function_statement"

    # DROP FUNCTION [IF EXISTS] function_name
    match_grammar = Sequence(
        "DROP",
        "FUNCTION",
        Ref("IfExistsGrammar", optional=True),
        Ref("FunctionNameSegment"),
    )


class RenameTableStatementSegment(BaseSegment):
    """A `RENAME TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/rename-table.html
    """

    type = "rename_table_statement"
    match_grammar = Sequence(
        "RENAME",
        "TABLE",
        Delimited(
            Sequence(
                Ref("TableReferenceSegment"),
                "TO",
                Ref("TableReferenceSegment"),
            ),
        ),
    )


class ResetMasterStatementSegment(BaseSegment):
    """A `RESET MASTER` statement.

    https://dev.mysql.com/doc/refman/8.0/en/reset-master.html
    """

    type = "reset_master_statement"
    match_grammar = Sequence(
        "RESET",
        "MASTER",
        Sequence("TO", Ref("NumericLiteralSegment"), optional=True),
    )


class PurgeBinaryLogsStatementSegment(BaseSegment):
    """A `PURGE BINARY LOGS` statement.

    https://dev.mysql.com/doc/refman/8.0/en/purge-binary-logs.html
    """

    type = "purge_binary_logs_statement"
    match_grammar = Sequence(
        "PURGE",
        OneOf(
            "BINARY",
            "MASTER",
        ),
        "LOGS",
        OneOf(
            Sequence(
                "TO",
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "BEFORE",
                OneOf(
                    Ref("ExpressionSegment"),
                ),
            ),
        ),
    )


class HelpStatementSegment(BaseSegment):
    """A `HELP` statement.

    https://dev.mysql.com/doc/refman/8.0/en/help.html
    """

    type = "help_statement"
    match_grammar = Sequence(
        "HELP",
        Ref("QuotedLiteralSegment"),
    )


class CheckTableStatementSegment(BaseSegment):
    """A `CHECK TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/check-table.html
    """

    type = "check_table_statement"
    match_grammar = Sequence(
        "CHECK",
        "TABLE",
        Delimited(
            Ref("TableReferenceSegment"),
        ),
        AnyNumberOf(
            Sequence("FOR", "UPGRADE"),
            "QUICK",
            "FAST",
            "MEDIUM",
            "EXTENDED",
            "CHANGED",
            min_times=1,
        ),
    )


class ChecksumTableStatementSegment(BaseSegment):
    """A `CHECKSUM TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/checksum-table.html
    """

    type = "checksum_table_statement"
    match_grammar = Sequence(
        "CHECKSUM",
        "TABLE",
        Delimited(
            Ref("TableReferenceSegment"),
        ),
        OneOf(
            "QUICK",
            "EXTENDED",
        ),
    )


class AnalyzeTableStatementSegment(BaseSegment):
    """An `ANALYZE TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/analyze-table.html
    """

    type = "analyze_table_statement"
    match_grammar = Sequence(
        "ANALYZE",
        OneOf(
            "NO_WRITE_TO_BINLOG",
            "LOCAL",
            optional=True,
        ),
        "TABLE",
        OneOf(
            Sequence(
                Delimited(
                    Ref("TableReferenceSegment"),
                ),
            ),
            Sequence(
                Ref("TableReferenceSegment"),
                "UPDATE",
                "HISTOGRAM",
                "ON",
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
                Sequence(
                    "WITH",
                    Ref("NumericLiteralSegment"),
                    "BUCKETS",
                    optional=True,
                ),
            ),
            Sequence(
                Ref("TableReferenceSegment"),
                "DROP",
                "HISTOGRAM",
                "ON",
                Delimited(
                    Ref("ColumnReferenceSegment"),
                ),
            ),
        ),
    )


class RepairTableStatementSegment(BaseSegment):
    """A `REPAIR TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/repair-table.html
    """

    type = "repair_table_statement"
    match_grammar = Sequence(
        "REPAIR",
        OneOf(
            "NO_WRITE_TO_BINLOG",
            "LOCAL",
            optional=True,
        ),
        "TABLE",
        Delimited(
            Ref("TableReferenceSegment"),
        ),
        AnyNumberOf(
            "QUICK",
            "EXTENDED",
            "USE_FRM",
        ),
    )


class OptimizeTableStatementSegment(BaseSegment):
    """An `OPTIMIZE TABLE` statement.

    https://dev.mysql.com/doc/refman/8.0/en/optimize-table.html
    """

    type = "optimize_table_statement"
    match_grammar = Sequence(
        "OPTIMIZE",
        OneOf(
            "NO_WRITE_TO_BINLOG",
            "LOCAL",
            optional=True,
        ),
        "TABLE",
        Delimited(
            Ref("TableReferenceSegment"),
        ),
    )


class UpdateStatementSegment(BaseSegment):
    """An `Update` statement.

    As per https://dev.mysql.com/doc/refman/8.0/en/update.html
    """

    type = "update_statement"
    match_grammar: Matchable = Sequence(
        "UPDATE",
        Ref.keyword("LOW_PRIORITY", optional=True),
        Ref.keyword("IGNORE", optional=True),
        Delimited(Ref("TableReferenceSegment"), Ref("FromExpressionSegment")),
        Ref("SetClauseListSegment"),
        Ref("WhereClauseSegment", optional=True),
        Ref("OrderByClauseSegment", optional=True),
        Ref("LimitClauseSegment", optional=True),
    )


class FlushStatementSegment(BaseSegment):
    """A `Flush` statement.

    As per https://dev.mysql.com/doc/refman/8.0/en/flush.html
    """

    type = "flush_statement"
    match_grammar: Matchable = Sequence(
        "FLUSH",
        OneOf(
            "NO_WRITE_TO_BINLOG",
            "LOCAL",
            optional=True,
        ),
        OneOf(
            Delimited(
                Sequence("BINARY", "LOGS"),
                Sequence("ENGINE", "LOGS"),
                Sequence("ERROR", "LOGS"),
                Sequence("GENERAL", "LOGS"),
                "HOSTS",
                "LOGS",
                "PRIVILEGES",
                "OPTIMIZER_COSTS",
                Sequence(
                    "RELAY",
                    "LOGS",
                    Sequence(
                        "FOR", "CHANNEL", Ref("ObjectReferenceSegment"), optional=True
                    ),
                ),
                Sequence("SLOW", "LOGS"),
                "STATUS",
                "USER_RESOURCES",
            ),
            Sequence(
                "TABLES",
                Sequence(
                    Delimited(Ref("TableReferenceSegment"), terminators=["WITH"]),
                    optional=True,
                ),
                Sequence("WITH", "READ", "LOCK", optional=True),
            ),
            Sequence(
                "TABLES",
                Sequence(
                    Delimited(Ref("TableReferenceSegment"), terminators=["FOR"]),
                    optional=False,
                ),
                Sequence("FOR", "EXPORT", optional=True),
            ),
        ),
    )


class LoadDataSegment(BaseSegment):
    """A `LOAD DATA` statement.

    As per https://dev.mysql.com/doc/refman/8.0/en/load-data.html
    """

    type = "load_data_statement"

    match_grammar = Sequence(
        "LOAD",
        "DATA",
        OneOf("LOW_PRIORITY", "CONCURRENT", optional=True),
        Sequence("LOCAL", optional=True),
        "INFILE",
        Ref("QuotedLiteralSegment"),
        OneOf("REPLACE", "IGNORE", optional=True),
        "INTO",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("SelectPartitionClauseSegment", optional=True),
        Sequence("CHARACTER", "SET", Ref("NakedIdentifierSegment"), optional=True),
        Sequence(
            OneOf("FIELDS", "COLUMNS"),
            Sequence("TERMINATED", "BY", Ref("QuotedLiteralSegment"), optional=True),
            Sequence(
                Sequence("OPTIONALLY", optional=True),
                "ENCLOSED",
                "BY",
                Ref("QuotedLiteralSegment"),
                optional=True,
            ),
            Sequence("ESCAPED", "BY", Ref("QuotedLiteralSegment"), optional=True),
            optional=True,
        ),
        Sequence(
            "LINES",
            Sequence("STARTING", "BY", Ref("QuotedLiteralSegment"), optional=True),
            Sequence("TERMINATED", "BY", Ref("QuotedLiteralSegment"), optional=True),
            optional=True,
        ),
        Sequence(
            "IGNORE",
            Ref("NumericLiteralSegment"),
            OneOf("LINES", "ROWS"),
            optional=True,
        ),
        Sequence(
            Bracketed(Delimited(Ref("ColumnReferenceSegment"))),
            optional=True,
        ),
        Sequence(
            "SET",
            Ref("Expression_B_Grammar"),
            optional=True,
        ),
    )


class ReplaceSegment(BaseSegment):
    """A `REPLACE` statement.

    As per https://dev.mysql.com/doc/refman/8.0/en/replace.html
    """

    type = "replace_statement"

    match_grammar = Sequence(
        "REPLACE",
        OneOf("LOW_PRIORITY", "DELAYED", optional=True),
        Sequence("INTO", optional=True),
        Ref("TableReferenceSegment"),
        Ref("SelectPartitionClauseSegment", optional=True),
        OneOf(
            Sequence(
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                Ref("ValuesClauseSegment"),
            ),
            Ref("SetClauseListSegment"),
            Sequence(
                Ref("BracketedColumnReferenceListGrammar", optional=True),
                OneOf(
                    Ref("SelectableGrammar"),
                    Sequence(
                        "TABLE",
                        Ref("TableReferenceSegment"),
                    ),
                ),
            ),
        ),
    )


class CreateTriggerStatementSegment(ansi.CreateTriggerStatementSegment):
    """Create Trigger Statement.

    As Specified in https://dev.mysql.com/doc/refman/8.0/en/create-trigger.html
    """

    # "DEFINED = user", optional
    match_grammar = Sequence(
        "CREATE",
        Ref("DefinerSegment", optional=True),
        "TRIGGER",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("TriggerReferenceSegment"),
        OneOf("BEFORE", "AFTER"),
        OneOf("INSERT", "UPDATE", "DELETE"),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence("FOR", "EACH", "ROW"),
        Sequence(
            OneOf("FOLLOWS", "PRECEDES"), Ref("SingleIdentifierGrammar"), optional=True
        ),
        OneOf(
            Ref("StatementSegment"),
            Sequence("BEGIN", Ref("StatementSegment"), "END"),
        ),
    )


class DropTriggerStatementSegment(ansi.DropTriggerStatementSegment):
    """A `DROP TRIGGER` Statement.

    As per https://dev.mysql.com/doc/refman/8.0/en/drop-trigger.html
    """

    match_grammar = Sequence(
        "DROP",
        "TRIGGER",
        Ref("IfExistsGrammar", optional=True),
        Ref("TriggerReferenceSegment"),
    )


class ColumnReferenceSegment(ansi.ColumnReferenceSegment):
    """A reference to column, field or alias.

    Also allows `column->path` and `column->>path` for JSON values.
    https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_json-column-path
    """

    match_grammar = ansi.ColumnReferenceSegment.match_grammar.copy(
        insert=[
            Sequence(
                ansi.ColumnReferenceSegment.match_grammar.copy(),
                OneOf(
                    Ref("ColumnPathOperatorSegment"),
                    Ref("InlinePathOperatorSegment"),
                ),
                OneOf(
                    Ref("DoubleQuotedJSONPath"),
                    Ref("SingleQuotedJSONPath"),
                ),
            ),
        ]
    )


class CreateDatabaseStatementSegment(ansi.CreateDatabaseStatementSegment):
    """A `CREATE DATABASE` statement.

    As specified in https://dev.mysql.com/doc/refman/8.0/en/create-database.html
    """

    match_grammar: Matchable = Sequence(
        "CREATE",
        OneOf("DATABASE", "SCHEMA"),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("DatabaseReferenceSegment"),
        AnyNumberOf(Ref("CreateOptionSegment")),
    )


class CreateOptionSegment(BaseSegment):
    """A database characteristic.

    As specified in https://dev.mysql.com/doc/refman/8.0/en/create-database.html
    """

    type = "create_option_segment"
    match_grammar = Sequence(
        Ref.keyword("DEFAULT", optional=True),
        OneOf(
            Sequence(
                "CHARACTER",
                "SET",
                Ref("EqualsSegment", optional=True),
                Ref("NakedIdentifierSegment"),
            ),
            Sequence(
                "COLLATE",
                Ref("EqualsSegment", optional=True),
                Ref("CollationReferenceSegment"),
            ),
            Sequence(
                "ENCRYPTION",
                Ref("EqualsSegment", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
        ),
    )


class AlterDatabaseStatementSegment(BaseSegment):
    """A `ALTER DATABASE` statement.

    As specified in https://dev.mysql.com/doc/refman/8.0/en/alter-database.html
    """

    type = "alter_database_statement"
    match_grammar: Matchable = Sequence(
        "ALTER",
        OneOf("DATABASE", "SCHEMA"),
        Ref("DatabaseReferenceSegment", optional=True),
        AnyNumberOf(Ref("AlterOptionSegment")),
    )


class AlterOptionSegment(BaseSegment):
    """A database characteristic.

    As specified in https://dev.mysql.com/doc/refman/8.0/en/alter-database.html
    """

    type = "alter_option_segment"
    match_grammar = Sequence(
        OneOf(
            Sequence(
                Ref.keyword("DEFAULT", optional=True),
                "CHARACTER",
                "SET",
                Ref("EqualsSegment", optional=True),
                Ref("NakedIdentifierSegment"),
            ),
            Sequence(
                Ref.keyword("DEFAULT", optional=True),
                "COLLATE",
                Ref("EqualsSegment", optional=True),
                Ref("CollationReferenceSegment"),
            ),
            Sequence(
                Ref.keyword("DEFAULT", optional=True),
                "ENCRYPTION",
                Ref("EqualsSegment", optional=True),
                Ref("QuotedLiteralSegment"),
            ),
            Sequence(
                "READ",
                "ONLY",
                Ref("EqualsSegment", optional=True),
                OneOf("DEFAULT", Ref("NumericLiteralSegment")),
            ),
        ),
    )


class ReturnStatementSegment(BaseSegment):
    """A RETURN statement.

    As specified in https://dev.mysql.com/doc/refman/8.0/en/return.html
    """

    type = "return_statement"
    match_grammar = Sequence(
        "RETURN",
        Ref("ExpressionSegment"),
    )


class SetNamesStatementSegment(BaseSegment):
    """A `SET NAMES` statement.

    As specified in https://dev.mysql.com/doc/refman/8.0/en/set-names.html
    """

    type = "set_names_statement"
    match_grammar: Matchable = Sequence(
        "SET",
        "NAMES",
        OneOf("DEFAULT", Ref("QuotedLiteralSegment"), Ref("NakedIdentifierSegment")),
        Sequence("COLLATE", Ref("CollationReferenceSegment"), optional=True),
    )
