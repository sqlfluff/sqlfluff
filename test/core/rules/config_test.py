"""Tests for the standard set of rules."""
import pytest

from sqlfluff.core import Linter
from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix
from sqlfluff.core.rules import get_ruleset
from sqlfluff.core.rules.doc_decorators import document_configuration
from sqlfluff.core.config import FluffConfig
from sqlfluff.core.parser import NewlineSegment
from sqlfluff.testing.rules import get_rule_from_set

from test.fixtures.rules.custom.L000 import Rule_L000
from test.fixtures.rules.custom.S000 import Rule_S000
from sqlfluff.core.rules.loader import get_rules_from_path


class Rule_T042(BaseRule):
    """A dummy rule."""

    def _eval(self, context):
        pass


class Rule_T001(BaseRule):
    """A deliberately malicious rule."""

    def _eval(self, context):
        """Stars make newlines."""
        if context.segment.is_type("star"):
            return LintResult(
                anchor=context.segment,
                fixes=[LintFix.create_before(context.segment, [NewlineSegment()])],
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

        config_keywords = ["comma_style"]

    assert "comma_style" in RuleWithConfig.__doc__

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
    assert (
        get_rules_from_path(
            rules_path="test/fixtures/rules/custom/*.py",
            base_module="test.fixtures.rules.custom",
        )
        == [Rule_L000, Rule_S000]
    )

    with pytest.raises(AttributeError) as e:
        get_rules_from_path(
            rules_path="test/fixtures/rules/custom/bad_rule_name/*.py",
            base_module="test.fixtures.rules.custom.bad_rule_name",
        )

    e.match("Rule classes must be named in the format of")


def test_rule_set_return_informative_error_when_rule_not_registered():
    """Assert that a rule that throws an exception on _eval returns it as a validation."""
    cfg = FluffConfig()
    with pytest.raises(ValueError) as e:
        get_rule_from_set("L000", config=cfg)

    e.match("'L000' not in")
