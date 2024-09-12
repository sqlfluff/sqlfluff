"""Test using sqlfluff to extract elements of queries."""

import sqlfluff
from sqlfluff.core.linter import RuleTuple


def test__api__info_dialects():
    """Basic linting of dialects."""
    dialects = sqlfluff.list_dialects()
    assert isinstance(dialects, list)
    # Turn it into a dict so we can look for items in there.
    dialect_dict = {dialect.label: dialect for dialect in dialects}
    # Check the ansi dialect works
    assert "ansi" in dialect_dict
    ansi = dialect_dict["ansi"]
    assert ansi.label == "ansi"
    assert ansi.name == "ANSI"
    assert ansi.inherits_from == "nothing"
    assert "This is the base dialect" in ansi.docstring
    # Check one other works
    assert "postgres" in dialect_dict
    postgres = dialect_dict["postgres"]
    assert postgres.label == "postgres"
    assert postgres.name == "PostgreSQL"
    assert postgres.inherits_from == "ansi"
    assert "this is often the dialect to use" in postgres.docstring


def test__api__info_rules():
    """Basic linting of dialects."""
    rules = sqlfluff.list_rules()
    assert isinstance(rules, list)
    assert (
        RuleTuple(
            code="LT01",
            name="layout.spacing",
            description="Inappropriate Spacing.",
            groups=("all", "core", "layout"),
            aliases=(
                "L001",
                "L005",
                "L006",
                "L008",
                "L023",
                "L024",
                "L039",
                "L048",
                "L071",
            ),
        )
        in rules
    )
