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


@pytest.mark.parametrize(
    "source",
    [
        "SELECT 1\n{% if false %}x{% endif %}",
        "SELECT 1\n{{ '' }}",
        "SELECT 1{% if false %}x{% endif %}",
    ],
)
def test_rules_LT12_trailing_empty_template_still_needs_newline(source):
    """A trailing block that renders to nothing doesn't make the file empty."""
    linter = Linter(
        config=FluffConfig(
            overrides={"dialect": "ansi", "rules": "LT12", "templater": "jinja"}
        )
    )
    result = linter.lint_string(source, fix=True)
    assert [v.rule_code() for v in result.get_violations()] == ["LT12"]
    assert result.fix_string()[0].endswith("\n")


def test_rules_LT12_empty_file_default_rules_fix_is_stable():
    """With every rule enabled, `fix` leaves an empty file empty."""
    linter = Linter(
        config=FluffConfig(overrides={"dialect": "ansi", "templater": "raw"})
    )
    first = linter.lint_string("", fix=True).fix_string()[0]
    second = linter.lint_string(first, fix=True).fix_string()[0]
    assert first == second == ""
