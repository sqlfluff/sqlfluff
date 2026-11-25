"""DuckDB dialect-specific lexer tests."""

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.parser import Lexer


@pytest.mark.parametrize(
    "raw,res",
    [
        # A `#` followed by a number is a column index.
        ("#1", [("#1", "column_index")]),
        ("#1 # 2", [("#1", "column_index"), ("#", "hash"), ("2", "numeric_literal")]),
        # Otherwise it's an operator, and `##` always is.
        ("a # b", [("a", "word"), ("#", "hash"), ("b", "word")]),
        ("a ##1", [("a", "word"), ("##", "hash"), ("1", "numeric_literal")]),
    ],
)
def test_hash_lexing(raw: str, res: list[tuple[str, str]]) -> None:
    """`#` starts a column index when a number follows it."""
    tokens, violations = Lexer(config=FluffConfig(overrides={"dialect": "duckdb"})).lex(
        raw
    )
    assert not violations
    assert [(token.raw, token.get_type()) for token in tokens if token.is_code] == res
