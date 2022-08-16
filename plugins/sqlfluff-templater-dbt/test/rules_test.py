"""Tests for the standard set of rules."""
import pytest
import os

from sqlfluff.core.config import FluffConfig
from sqlfluff.utils.testing.rules import assert_rule_raises_violations_in_file

from test.fixtures.dbt.templater import (  # noqa
    DBT_FLUFF_CONFIG,
    project_dir,
    dbt_templater,
)


@pytest.mark.parametrize(
    "rule,path,violations",
    [
        # Group By
        ("L021", "models/my_new_project/select_distinct_group_by.sql", [(1, 8)]),
        # Multiple trailing newline
        ("L009", "models/my_new_project/multiple_trailing_newline.sql", [(3, 1)]),
    ],
)
def test__rules__std_file_dbt(rule, path, violations, project_dir):  # noqa
    """Test linter finds the given errors in (and only in) the right places (DBT)."""
    assert_rule_raises_violations_in_file(
        rule=rule,
        fpath=os.path.join(project_dir, path),
        violations=violations,
        fluff_config=FluffConfig(configs=DBT_FLUFF_CONFIG, overrides=dict(rules=rule)),
    )
