"""Tests for the standard set of rules."""
import os
import os.path
from pathlib import Path

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig
from sqlfluff.utils.testing.rules import assert_rule_raises_violations_in_file
from test.fixtures.dbt.templater import (  # noqa
    DBT_FLUFF_CONFIG,
    dbt_templater,
    project_dir,
)


@pytest.mark.parametrize(
    "rule,path,violations",
    [
        # Group By
        ("AM01", "models/my_new_project/select_distinct_group_by.sql", [(1, 8)]),
        # Multiple trailing newline
        ("LT12", "models/my_new_project/multiple_trailing_newline.sql", [(3, 1)]),
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


def test__rules__fix_utf8(project_dir):  # noqa
    """Verify that non-ASCII characters are preserved by 'fix'."""
    rule = "CP01"
    path = "models/my_new_project/utf8/test.sql"
    lntr = Linter(
        config=FluffConfig(configs=DBT_FLUFF_CONFIG, overrides=dict(rules=rule))
    )
    lnt = lntr.lint_path(os.path.join(project_dir, path), fix=True)
    # Check that we did actually find issues.
    # NOTE: This test is mostly useful to distinguish between whether there's
    # a problem with the rule - or a problem with the file.
    violations_dict = lnt.violation_dict()
    print("Violations Dict: ", violations_dict)
    qual_path = os.path.normpath(Path(project_dir) / path)
    assert qual_path in violations_dict, f"{path} not in violations dict."
    assert violations_dict[qual_path], f"No issues found for {qual_path}."
    lnt.persist_changes(fixed_file_suffix="FIXED")
    # TODO: Check contents of file:
    # ./plugins/sqlfluff-templater-dbt/test/fixtures/dbt/dbt_project/models/
    # my_new_project/utf8/testFIXED.sql
    # Against a git file, similar to the autofix tests
    fixed_path = Path(project_dir) / "models/my_new_project/utf8/testFIXED.sql"
    cmp_filepath = Path(project_dir) / "models/my_new_project/utf8/test.sql.fixed"
    fixed_buff = fixed_path.read_text("utf8")
    comp_buff = cmp_filepath.read_text("utf8")

    # Assert that we fixed as expected
    assert fixed_buff == comp_buff
    os.unlink(fixed_path)


def test__rules__order_by(project_dir):  # noqa
    """Verify that rule AM03 works with dbt."""
    rule = "AM03"
    path = "models/my_new_project/AM03_test.sql"
    lntr = Linter(
        config=FluffConfig(configs=DBT_FLUFF_CONFIG, overrides=dict(rules=rule))
    )
    lnt = lntr.lint_path(os.path.join(project_dir, path))

    violations = lnt.check_tuples()
    assert len(violations) == 0
