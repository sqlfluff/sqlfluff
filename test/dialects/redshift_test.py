"""Redshift dialect-specific parser rejection and lexer tests.

Positive/valid-SQL cases belong in the SQL/YAML parse fixtures under
test/fixtures/dialects/redshift/ per project convention.
"""

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import Lexer


def _violations(sql: str) -> list:
    """Return all parse errors, including unparsable nodes in the tree."""
    parsed = Linter(dialect="redshift").parse_string(sql)
    violations: list = list(parsed.violations)
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "SELECT *, a, EXCLUDE x FROM tbl;",
            id="comma_before_unbracketed_exclude",
        ),
        pytest.param(
            "SELECT col1, EXCLUDE col2 FROM tbl;",
            id="comma_before_unbracketed_exclude_no_star",
        ),
        pytest.param(
            "SELECT col1, EXCLUDE (col2) FROM tbl;",
            id="comma_before_bracketed_exclude",
        ),
    ],
)
def test_select_exclude_rejects_comma_before_clause(sql: str) -> None:
    """A comma before SELECT EXCLUDE must not parse as a select item."""
    assert _violations(sql), f"Expected violations but got none for:\n{sql}"


@pytest.mark.parametrize(
    "raw,res",
    [
        # A `#` followed by a name is a temporary table.
        ("#temp_table", [("#temp_table", "word")]),
        ("#t # 1", [("#t", "word"), ("#", "hash"), ("1", "numeric_literal")]),
        # Otherwise it's an operator, and `##` always is.
        ("a # b", [("a", "word"), ("#", "hash"), ("b", "word")]),
        ("a ## b", [("a", "word"), ("##", "hash"), ("b", "word")]),
        ("a ##b", [("a", "word"), ("##", "hash"), ("b", "word")]),
        ("a ##1", [("a", "word"), ("##", "hash"), ("1", "numeric_literal")]),
    ],
)
def test_hash_lexing(raw: str, res: list[tuple[str, str]]) -> None:
    """`#` starts a temporary table name when a name follows it."""
    tokens, violations = Lexer(
        config=FluffConfig(overrides={"dialect": "redshift"})
    ).lex(raw)
    assert not violations
    assert [(token.raw, token.get_type()) for token in tokens if token.is_code] == res
