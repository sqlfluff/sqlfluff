"""Tests specific to the postgres dialect."""
import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize(
    "raw",
    [
        "ALTER TABLE foo DROP COLUMN bar",
        "CREATE USER my_user",
        "TRUNCATE TABLE foo",
        "EXPLAIN SELECT Id FROM Contact",
        "DROP TABLE foo",
        "DROP USER my_user",
    ],
)
def test_non_selects_unparseable(raw: str) -> None:
    """Test that non-SELECT commands are not parseable."""
    cfg = FluffConfig(configs={"core": {"dialect": "soql"}})
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() > 0
