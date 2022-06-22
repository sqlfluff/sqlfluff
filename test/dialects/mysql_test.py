"""Tests specific to the mysql dialect."""

import pytest
from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize(
    "raw",
    [
        "insert into foo (bar, bazz) value (1, 2) "
        "on duplicate key update bar = 3, bazz = 4;",
        "insert into foo (bar, bazz) value (1, 2) "
        "on duplicate key update bar = values(bar), bazz = values(bazz);",
        "insert into foo (bar, bazz) values (1, 2) "
        "on duplicate key update bar = 3, bazz = 4;",
        "insert into foo (bar, bazz) values (1, 2) "
        "on duplicate key update bar = values(bar), bazz = values(bazz);",
    ],
)
def test_insert_on_duplicate_key(raw: str) -> None:
    """Test the INSERT ... ON DUPLICATE KEY UPDATE keyword(s) for mysql."""
    # Don't test for new lines or capitalisation
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "L009,L016,L036", "dialect": "mysql"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0
