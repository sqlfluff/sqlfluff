"""Tests specific to the postgres dialect."""
import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLParseError


@pytest.mark.parametrize(
    "raw",
    [
        """ALTER TABLE foo DROP COLUMN bar
        """,
        """CREATE USER my_user
        """,
        """TRUNCATE TABLE foo
        """,
        """EXPLAIN SELECT Id FROM Contact
        """,
        """DROP TABLE foo
        """,
        """DROP USER my_user
        """,
    ],
)
def test_non_selects_unparseable(raw: str) -> None:
    """Test that non-SELECT commands are not parseable."""
    cfg = FluffConfig(configs={"core": {"dialect": "soql"}})
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert len(result.violations) == 1
    assert isinstance(result.violations[0], SQLParseError)


def test_ignore_unreferenced_object() -> None:
    """SOQL often has an implicit relationship between objects."""
    cfg = FluffConfig(configs={"core": {"dialect": "soql"}})
    lnt = Linter(config=cfg)
    result = lnt.lint_string(
        """SELECT Account.Name FROM Contact
    """
    )
    assert result.num_violations() == 0
