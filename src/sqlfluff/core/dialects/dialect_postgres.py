"""The PostgreSQL dialect."""

from sqlfluff.core.parser import (
    OneOf,
    Ref,
    Sequence,
    Bracketed,
    Anything,
    BaseSegment,
    NamedSegment,
    Delimited,
)

from sqlfluff.core.dialects.dialect_ansi import ansi_dialect

# At the moment this is just a placeholder. Unique syntax to be added later.
postgres_dialect = ansi_dialect.copy_as("postgres")


postgres_dialect.insert_lexer_struct(
    # JSON Operators: https://www.postgresql.org/docs/9.5/functions-json.html
    [
        (
            "json_operator",
            "regex",
            r"->>|#>>|->|#>|@>|<@|\?\||\?|\?&|#-",
            dict(is_code=True),
        )
    ],
    before="not_equal",
)


# Reserve WITHIN (required for the WithinGroupClauseSegment)
postgres_dialect.sets("unreserved_keywords").remove("WITHIN")
postgres_dialect.sets("reserved_keywords").add("WITHIN")
# Add the EPOCH datetime unit
postgres_dialect.sets("datetime_units").update(["EPOCH"])


postgres_dialect.add(
    JsonOperatorSegment=NamedSegment.make(
        "json_operator", name="json_operator", type="binary_operator"
    ),
)


postgres_dialect.replace(
    PostFunctionGrammar=OneOf(
        Ref("WithinGroupClauseSegment"),
        Sequence(
            Sequence(OneOf("IGNORE", "RESPECT"), "NULLS", optional=True),
            Ref("OverClauseSegment"),
        ),
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
