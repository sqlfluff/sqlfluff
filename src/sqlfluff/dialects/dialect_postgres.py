"""The PostgreSQL dialect."""

from sqlfluff.core.parser import (
    OneOf,
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
)

from sqlfluff.core.dialects import load_raw_dialect

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


# https://www.postgresql.org/docs/current/sql-keywords-appendix.html
# SPACE has special status in some SQL dialects, but not Postgres.
postgres_dialect.sets("unreserved_keywords").remove("SPACE")
# Reserve WITHIN (required for the WithinGroupClauseSegment)
postgres_dialect.sets("unreserved_keywords").remove("WITHIN")
postgres_dialect.sets("unreserved_keywords").update(
    [
        "WITHIN",
        "ANALYZE",
        "VERBOSE",
        "COSTS",
        "BUFFERS",
        "FORMAT",
        "XML",
    ]
)
postgres_dialect.sets("reserved_keywords").add("WITHIN")
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
)


@postgres_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement."""

    match_grammar = Sequence(
        "AS",
        OneOf(Ref("QuotedLiteralSegment"), Ref("DollarQuotedLiteralSegment")),
        Sequence(
            "LANGUAGE",
            # Not really a parameter, but best fit for now.
            Ref("ParameterNameSegment"),
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
