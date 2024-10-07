"""Tests for the standard set of rules."""

import os
import os.path
from pathlib import Path

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig
from sqlfluff.utils.testing.rules import assert_rule_raises_violations_in_file


@pytest.mark.parametrize(
    "rule,path,violations",
    [
        # Group By
        ("AM01", "models/my_new_project/select_distinct_group_by.sql", [(1, 8)]),
        # Multiple trailing newline
        ("LT12", "models/my_new_project/multiple_trailing_newline.sql", [(3, 1)]),
    ],
)
def test__rules__std_file_dbt(rule, path, violations, project_dir, dbt_fluff_config):  # noqa
    """Test linter finds the given errors in (and only in) the right places (DBT)."""
    assert_rule_raises_violations_in_file(
        rule=rule,
        fpath=os.path.join(project_dir, path),
        violations=violations,
        fluff_config=FluffConfig(configs=dbt_fluff_config, overrides=dict(rules=rule)),
    )


def test__rules__fix_utf8(project_dir, dbt_fluff_config):  # noqa
    """Verify that non-ASCII characters are preserved by 'fix'."""
    rule = "CP01"
    path = "models/my_new_project/utf8/test.sql"
    linter = Linter(
        config=FluffConfig(configs=dbt_fluff_config, overrides=dict(rules=rule))
    )
    result = linter.lint_path(os.path.join(project_dir, path), fix=True)
    # Check that we did actually find issues.
    # NOTE: This test is mostly useful to distinguish between whether there's
    # a problem with the rule - or a problem with the file.
    record_map = {record["filepath"]: record for record in result.as_records()}
    print("Result Map: ", record_map)
    qual_path = os.path.normpath(Path(project_dir) / path)
    assert qual_path in record_map, f"{path} not in result."
    assert record_map[qual_path]["violations"], f"No issues found for {qual_path}."
    result.persist_changes(fixed_file_suffix="FIXED")
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


def test__rules__order_by(project_dir, dbt_fluff_config):  # noqa
    """Verify that rule AM03 works with dbt."""
    rule = "AM03"
    path = "models/my_new_project/AM03_test.sql"
    lntr = Linter(
        config=FluffConfig(configs=dbt_fluff_config, overrides=dict(rules=rule))
    )
    lnt = lntr.lint_path(os.path.join(project_dir, path))

    violations = lnt.check_tuples()
    assert len(violations) == 0


def test__rules__indent_oscillate(project_dir, dbt_fluff_config):  # noqa
    """Verify that we don't get oscillations with LT02 and dbt."""
    # This *should* be the wrong format
    path_1 = "models/my_new_project/indent_loop_4.sql"
    # This *should* be the correct format
    path_2 = "models/my_new_project/indent_loop_8.sql"
    # Get the content of the latter
    with open(os.path.join(project_dir, path_2), "r") as f:
        path_2_content = f.read()
    linter = Linter(
        config=FluffConfig(configs=dbt_fluff_config, overrides={"rules": "LT02"})
    )
    # Check the wrong one first (path_1)
    linted_dir = linter.lint_path(os.path.join(project_dir, path_1), fix=True)
    linted_file = linted_dir.files[0]
    assert linted_file.check_tuples() == [("LT02", 6, 1)]
    fixed_file_1, _ = linted_file.fix_string()
    assert (
        fixed_file_1 == path_2_content
    ), "indent_loop_4.sql should match indent_loop_8.sql post fix"
    # Check the correct one second, we shouldn't get any issues.
    # NOTE: This also checks that the fixed version of the first one wouldn't
    # change again.
    linted_dir = linter.lint_path(os.path.join(project_dir, path_2), fix=True)
    linted_file = linted_dir.files[0]
    assert linted_file.check_tuples() == []  # Should find no issues.
