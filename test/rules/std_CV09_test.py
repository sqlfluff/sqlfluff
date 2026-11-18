"""Tests the python routines within CV09."""

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.rules import LintResult
from sqlfluff.rules.convention.CV09 import Rule_CV09


# NOTE: The rules below keep CV09's name, so that they're given CV09's configuration.
class Rule_T009(Rule_CV09):
    """A rule based on CV09, which flags every keyword whatever is blocked."""

    aliases = ()

    def _eval(self, context):
        if context.segment.is_type("keyword"):
            return LintResult(anchor=context.segment, description="Keyword.")


class Rule_T010(Rule_CV09):
    """A rule based on CV09, which sets what it blocks in code, not in config."""

    aliases = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocked_words = "deprecated_table"


@pytest.mark.parametrize(
    "rule_class,expected",
    [
        # Its own _eval() flags every keyword.
        (Rule_T009, ["Keyword.", "Keyword."]),
        # It sets its blocked words in its own __init__(), after CV09's.
        (Rule_T010, ["Use of blocked word 'deprecated_table'."]),
    ],
)
def test__rules__std_CV09_subclass_sees_every_segment(rule_class, expected) -> None:
    """A subclass is given every raw segment, even with nothing blocked in config.

    With nothing blocked CV09 itself can't flag anything, so it doesn't crawl
    the file. A subclass can flag segments whatever the config says, either by
    replacing `_eval()` or by setting its own blocked words.
    """
    linter = Linter(user_rules=[rule_class], dialect="ansi", rules=[rule_class.code])
    result = linter.lint_string("SELECT a FROM deprecated_table\n")
    assert [v.desc() for v in result.get_violations()] == expected


def test__rules__std_CV09_raised() -> None:
    """CV09 is raised for use of blocked words with correct error message."""
    sql = "SELECT MYOLDFUNCTION(col1) FROM deprecated_table;\n"
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    cfg.set_value(
        config_path=["rules", "convention.blocked_words", "blocked_words"],
        val="myoldfunction,deprecated_table",
    )
    linter = Linter(config=cfg)
    result_records = linter.lint_string_wrapped(sql).as_records()
    result = result_records[0]["violations"]

    assert len(result) == 2
    assert result[0]["description"] == "Use of blocked word 'MYOLDFUNCTION'."
    assert result[1]["description"] == "Use of blocked word 'deprecated_table'."
