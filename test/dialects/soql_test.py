"""Tests specific to the soql dialect."""

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLParseError


@pytest.mark.parametrize(
    "raw",
    [
        "ALTER TABLE foo DROP COLUMN bar\n",
        "CREATE USER my_user\n",
        "TRUNCATE TABLE foo\n",
        "EXPLAIN SELECT Id FROM Contact\n",
        "DROP TABLE foo\n",
        "DROP USER my_user\n",
    ],
)
def test_non_selects_unparseable(raw: str) -> None:
    """Test that non-SELECT commands are not parseable."""
    cfg = FluffConfig(configs={"core": {"dialect": "soql"}})
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert len(result.violations) == 1
    assert isinstance(result.violations[0], SQLParseError)
