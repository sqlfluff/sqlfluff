"""Tests for the standard set of rules."""
import pytest

from sqlfluff.core import Linter
from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix
from sqlfluff.core.rules import get_ruleset
from sqlfluff.core.rules.doc_decorators import document_configuration
from sqlfluff.core.config import FluffConfig
from sqlfluff.testing.rules import (
    assert_rule_raises_violations_in_file,
    get_rule_from_set,
)

from test.fixtures.dbt.templater import (  # noqa
    DBT_FLUFF_CONFIG,
    in_dbt_project_dir,
    dbt_templater,
)
from test.fixtures.rules.L000 import Rule_L000
from test.fixtures.rules.S000 import Rule_S000
from sqlfluff.core.rules.std import get_rules_from_path


class Rule_T042(BaseRule):
    """A dummy rule."""

    def _eval(self, segment, raw_stack, **kwargs):
        pass


class Rule_T001(BaseRule):
    """A deliberately malicious rule."""

    def _eval(self, segment, raw_stack, **kwargs):
        """Stars make newlines."""
        if segment.is_type("star"):
            return LintResult(
                anchor=segment,
                fixes=[
                    LintFix("create", segment, self.make_newline(segment.pos_marker))
                ],
            )


def test__rules__user_rules():
    """Test that can safely add user rules."""
    # Set up a linter with the user rule
    linter = Linter(user_rules=[Rule_T042])
    # Make sure the new one is in there.
    assert ("T042", "A dummy rule.") in linter.rule_tuples()
    # Instantiate a second linter and check it's NOT in there.
    # This tests that copying and isolation works.
    linter = Linter()
    assert not any(rule[0] == "T042" for rule in linter.rule_tuples())


def test__rules__runaway_fail_catch():
    """Test that we catch runaway rules."""
    runaway_limit = 5
    my_query = "SELECT * FROM foo"
    # Set up the config to only use the rule we are testing.
    cfg = FluffConfig(overrides={"rules": "T001", "runaway_limit": runaway_limit})
    # Lint it using the current config (while in fix mode)
    linter = Linter(config=cfg, user_rules=[Rule_T001])
    # In theory this step should result in an infinite
    # loop, but the loop limit should catch it.
    linted = linter.lint_string(my_query, fix=True)
    # We should have a lot of newlines in there.
    # The number should equal the runaway limit
    assert linted.tree.raw.count("\n") == runaway_limit


@pytest.mark.parametrize(
    "rule,path,violations",
    [
        ("L001", "test/fixtures/linter/indentation_errors.sql", [(4, 24)]),
        ("L002", "test/fixtures/linter/indentation_errors.sql", [(3, 1), (4, 1)]),
        (
            "L003",
            "test/fixtures/linter/indentation_errors.sql",
            [(2, 4), (3, 4), (4, 6)],
        ),
        (
            "L004",
            "test/fixtures/linter/indentation_errors.sql",
            [(3, 1), (4, 1), (5, 1)],
        ),
        # Check we get comma (with leading space/newline) whitespace errors
        # NB The newline before the comma, should report on the comma, not the newline for clarity.
        ("L005", "test/fixtures/linter/whitespace_errors.sql", [(2, 9)]),
        ("L019", "test/fixtures/linter/whitespace_errors.sql", [(4, 1)]),
        # Check we get comma (with incorrect trailing space) whitespace errors,
        # but also no false positives on line 4 or 5.
        ("L008", "test/fixtures/linter/whitespace_errors.sql", [(3, 12)]),
        # Check we get operator whitespace errors and it works with brackets
        (
            "L006",
            "test/fixtures/linter/operator_errors.sql",
            [(3, 8), (4, 10), (7, 6), (7, 7), (7, 9), (7, 10), (7, 12), (7, 13)],
        ),
        ("L007", "test/fixtures/linter/operator_errors.sql", [(5, 9)]),
        # Check we DO get a violation on line 2 but NOT on line 3
        (
            "L006",
            "test/fixtures/linter/operator_errors_negative.sql",
            [(2, 6), (2, 9), (5, 6), (5, 7)],
        ),
        # Hard indentation errors
        (
            "L003",
            "test/fixtures/linter/indentation_error_hard.sql",
            [(2, 4), (6, 5), (9, 13), (14, 14), (19, 5), (20, 6)],
        ),
        # Check bracket handling with closing brackets and contained indents works.
        ("L003", "test/fixtures/linter/indentation_error_contained.sql", []),
        # Check we handle block comments as expect. Github #236
        (
            "L016",
            "test/fixtures/linter/block_comment_errors.sql",
            [(1, 121), (2, 99), (4, 88)],
        ),
        ("L016", "test/fixtures/linter/block_comment_errors_2.sql", [(1, 85), (2, 86)]),
        # Column references
        ("L027", "test/fixtures/linter/column_references.sql", [(1, 8)]),
        ("L027", "test/fixtures/linter/column_references_bare_function.sql", []),
        ("L026", "test/fixtures/linter/column_references.sql", [(1, 11)]),
        ("L025", "test/fixtures/linter/column_references.sql", [(2, 11)]),
        # Distinct and Group by
        ("L021", "test/fixtures/linter/select_distinct_group_by.sql", [(1, 8)]),
        # Make sure that ignoring works as expected
        ("L006", "test/fixtures/linter/operator_errors_ignore.sql", [(10, 8), (10, 9)]),
        (
            "L031",
            "test/fixtures/linter/aliases_in_join_error.sql",
            [(6, 15), (7, 19), (8, 16)],
        ),
    ],
)
def test__rules__std_file(rule, path, violations):
    """Test the linter finds the given errors in (and only in) the right places."""
    assert_rule_raises_violations_in_file(
        rule=rule,
        fpath=path,
        violations=violations,
        fluff_config=FluffConfig(overrides=dict(rules=rule)),
    )


@pytest.mark.dbt
@pytest.mark.parametrize(
    "rule,path,violations",
    [
        # Group By
        ("L021", "models/my_new_project/select_distinct_group_by.sql", [(1, 8)]),
    ],
)
def test__rules__std_file_dbt(rule, path, violations, in_dbt_project_dir):  # noqa
    """Test the linter finds the given errors in (and only in) the right places (DBT)."""
    assert_rule_raises_violations_in_file(
        rule=rule,
        fpath=path,
        violations=violations,
        fluff_config=FluffConfig(configs=DBT_FLUFF_CONFIG, overrides=dict(rules=rule)),
    )


def test__rules__std_L003_process_raw_stack(generate_test_segments):
    """Test the _process_raw_stack function.

    Note: This test probably needs expanding. It doesn't
    really check enough of the full functionality.

    """
    cfg = FluffConfig()
    r = get_rule_from_set("L003", config=cfg)
    test_stack = generate_test_segments(["bar", "\n", "     ", "foo", "baar", " \t "])
    res = r._process_raw_stack(test_stack)
    print(res)
    assert sorted(res.keys()) == [1, 2]
    assert res[2]["indent_size"] == 5


@pytest.mark.parametrize(
    "rule_config_dict",
    [
        {"tab_space_size": "blah"},
        {"max_line_length": "blah"},
        {"indent_unit": "blah"},
        {"comma_style": "blah"},
        {"allow_scalar": "blah"},
        {"single_table_references": "blah"},
        {"only_aliases": "blah"},
        {"L010": {"capitalisation_policy": "blah"}},
        {"L014": {"capitalisation_policy": "blah"}},
        {"L030": {"capitalisation_policy": "blah"}},
    ],
)
def test_improper_configs_are_rejected(rule_config_dict):
    """Ensure that unsupported configs raise a ValueError."""
    config = FluffConfig(configs={"rules": rule_config_dict})
    with pytest.raises(ValueError):
        get_ruleset().get_rulelist(config)


def test_rules_cannot_be_instantiated_without_declared_configs():
    """Ensure that new rules must be instantiated with config values."""

    class NewRule(BaseRule):
        config_keywords = ["comma_style"]

    new_rule = NewRule(code="L000", description="", comma_style="trailing")
    assert new_rule.comma_style == "trailing"
    # Error is thrown since "comma_style" is defined in class,
    # but not upon instantiation
    with pytest.raises(ValueError):
        new_rule = NewRule(code="L000", description="")


def test_rules_configs_are_dynamically_documented():
    """Ensure that rule configurations are added to the class docstring."""

    @document_configuration
    class RuleWithConfig(BaseRule):
        """A new rule with configuration."""

        config_keywords = ["comma_style", "only_aliases"]

    assert "comma_style" in RuleWithConfig.__doc__
    assert "only_aliases" in RuleWithConfig.__doc__

    @document_configuration
    class RuleWithoutConfig(BaseRule):
        """A new rule without configuration."""

        pass

    assert "Configuration" not in RuleWithoutConfig.__doc__


def test_rule_exception_is_caught_to_validation():
    """Assert that a rule that throws an exception on _eval returns it as a validation."""
    std_rule_set = get_ruleset()

    @std_rule_set.register
    class Rule_T000(BaseRule):
        """Rule that throws an exception."""

        def _eval(self, segment, parent_stack, **kwargs):
            raise Exception("Catch me or I'll deny any linting results from you")

    linter = Linter(
        config=FluffConfig(overrides=dict(rules="T000")),
        user_rules=[Rule_T000],
    )

    assert linter.lint_string("select 1").check_tuples() == [("T000", 1, 1)]


def test_std_rule_import_fail_bad_naming():
    """Check that rule import from file works."""
    assert get_rules_from_path(
        rules_path="test/fixtures/rules/*.py", base_module="test.fixtures.rules"
    ) == [Rule_L000, Rule_S000]

    with pytest.raises(AttributeError) as e:
        get_rules_from_path(
            rules_path="test/fixtures/rules/bad_rule_name/*.py",
            base_module="test.fixtures.rules.bad_rule_name",
        )

    e.match("Rule classes must be named in the format of")


def test_rule_set_return_informative_error_when_rule_not_registered():
    """Assert that a rule that throws an exception on _eval returns it as a validation."""
    cfg = FluffConfig()
    with pytest.raises(ValueError) as e:
        get_rule_from_set("L000", config=cfg)

    e.match("'L000' not in")
