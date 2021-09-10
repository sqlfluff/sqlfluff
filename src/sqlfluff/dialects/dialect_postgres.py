"""The PostgreSQL dialect."""

from sqlfluff.core.parser import (
    OneOf,
    AnyNumberOf,
    Ref,
    Sequence,
    Bracketed,
    Anything,
    BaseSegment,
    Delimited,
    RegexLexer,
    CodeSegment,
    NamedParser,
    SymbolSegment,
    StartsWith,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects.postgres_keywords import postgres_keywords, get_keywords

ansi_dialect = load_raw_dialect("ansi")

postgres_dialect = ansi_dialect.copy_as("postgres")

postgres_dialect.insert_lexer_matchers(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [
        RegexLexer(
            "json_operator",
            r"->>|#>>|->|#>|@>|<@|\?\||\?|\?&|#-",
            CodeSegment,
        )
    ],
    before="not_equal",
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

# Add the EPOCH datetime unit
postgres_dialect.sets("datetime_units").update(["EPOCH"])

postgres_dialect.add(
    JsonOperatorSegment=NamedParser(
        "json_operator", SymbolSegment, name="json_operator", type="binary_operator"
    ),
    DollarQuotedLiteralSegment=NamedParser(
        "dollar_quote", CodeSegment, name="dollar_quoted_literal", type="literal"
    ),
)

postgres_dialect.replace(
    PostFunctionGrammar=OneOf(
        Ref("WithinGroupClauseSegment"),
        Sequence(
            Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
            Ref("OverClauseSegment"),
        ),
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
                Ref("DatatypeSegment"),
            ),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
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
                    Sequence("DETACH", "PARTITION", Ref("ParameterNameSegment")),
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
                Sequence("SET", "DEFAULT", Ref("ExpressionSegment")),
                Sequence("DROP", "DEFAULT"),
                Sequence(OneOf("SET", "DROP", optional=True), "NOT", "NULL"),
                Sequence("DROP", "EXPRESSION", Sequence("IF", "EXISTS", optional=True)),
                Sequence(
                    "ADD",
                    "GENERATED",
                    OneOf("ALWAYS", Sequence("BY", "DEFAULT")),
                    "AS",
                    "IDENTITY",
                    # TODO Optional Sequence options here
                ),
                Sequence(
                    OneOf(
                        Sequence(
                            "SET",
                            "GENERATED",
                            OneOf("ALWAYS", Sequence("BY", "DEFAULT")),
                        ),
                        # TODO SET sequence_option
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
                        Ref("LiteralGrammer"),
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
            OneOf(Ref("ParameterNameSegment"), "CURRENT_USER", "SESSION_USER"),
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
class LikeOptionSegment(BaseSegment):
    """Like Option Segment.

    As specified in https://www.postgresql.org/docs/13/sql-createtable.html
    """

    type = "like_option"

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


@postgres_dialect.segment()
class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more.

    This matches the definition in https://www.postgresql.org/docs/13/sql-altertable.html
    """

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
                # TODO Add optional sequence options
            ),
            "UNIQUE",
            Ref("PrimaryKeyGrammar"),
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar", optional=True),
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

    type = "table_constraint_definition"

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


# Adding PostgreSQL specific statements
@postgres_dialect.segment(replace=True)
class StatementSegment(BaseSegment):
    """A generic segment, to any of its child subsegments."""

    type = "statement"

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("AlterDefaultPrivilegesStatementSegment"),
            Ref("CommentOnStatementSegment"),
        ],
    )

    match_grammar = ansi_dialect.get_segment("StatementSegment").match_grammar.copy()
