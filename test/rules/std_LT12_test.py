"""Tests for rule LT12 (layout.end_of_file) on an empty file.

An empty file has no content to terminate, so LT12 shouldn't ask for a trailing
newline. If it does, LT13 removes that newline as a leading one, and successive
`fix` runs flip the file between empty and a single newline forever.
"""

import pytest

from sqlfluff.core import FluffConfig, Linter


@pytest.mark.parametrize("templater", ["raw", "jinja"])
def test_rules_LT12_empty_file_no_violation(templater):
    """An empty file has nothing to terminate."""
    linter = Linter(
        config=FluffConfig(
            overrides={"dialect": "ansi", "rules": "LT12", "templater": templater}
        )
    )
    result = linter.lint_string("", fix=True)
    assert not result.get_violations()
    assert result.fix_string()[0] == ""


def test_rules_LT12_LT13_empty_file_fix_is_stable():
    """LT12 and LT13 must agree on the result for an empty file."""
    linter = Linter(
        config=FluffConfig(
            overrides={"dialect": "ansi", "rules": "LT12,LT13", "templater": "raw"}
        )
    )
    first = linter.lint_string("", fix=True).fix_string()[0]
    second = linter.lint_string(first, fix=True).fix_string()[0]
    assert first == second == ""
