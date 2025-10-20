"""Tests for the standard set of rules."""

import logging

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.linter import RuleTuple
from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, get_ruleset
from sqlfluff.core.rules.crawlers import RootOnlyCrawler, SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.core.rules.loader import get_rules_from_path
from sqlfluff.core.templaters.base import TemplatedFile
from sqlfluff.utils.testing.logging import fluff_log_catcher
from sqlfluff.utils.testing.rules import get_rule_from_set
from test.fixtures.rules.custom.L000 import Rule_L000
from test.fixtures.rules.custom.S000 import Rule_S000


class Rule_T042(BaseRule):
    """A dummy rule."""

    groups = ("all",)

    def _eval(self, context):
        pass


class Rule_T001(BaseRule):
    """A deliberately malicious rule.

    **Anti-pattern**

    Blah blah
    """

    groups = ("all",)
    crawl_behaviour = SegmentSeekerCrawler({"whitespace"})
    is_fix_compatible = True

    def _eval(self, context):
        """Stars make newlines."""
        if context.segment.is_type("whitespace"):
            return LintResult(
                anchor=context.segment,
                fixes=[
                    LintFix.replace(
                        context.segment, [WhitespaceSegment(context.segment.raw + " ")]
                    )
                ],
            )


class Rule_T002(BaseRule):
    """A rule which says all raw code segments are bad.

    This is used for testing unparsable code.
    """

    groups = ("all",)
    # Root only crawler so that the in-rule filters don't kick in.
    crawl_behaviour = RootOnlyCrawler()

    def _eval(self, context):
        """Stars make newlines."""
        violations = []
        for seg in context.segment.raw_segments:
            if seg.is_code:
                violations.append(LintResult(anchor=seg, description="TESTING"))
        return violations


class Rule_T003(BaseRule):
    """Another deliberately malicious rule.

    **Anti-pattern**

    Blah blah
    """

    groups = ("all",)
    crawl_behaviour = SegmentSeekerCrawler({"numeric_literal"})
    is_fix_compatible = True

    def _eval(self, context):
        """Triple any numeric literals."""
        return LintResult(
            anchor=context.segment,
            fixes=[
                LintFix.replace(
                    context.segment,
                    [
                        context.segment,
                        WhitespaceSegment(context.segment.raw + " "),
                        context.segment,
                        WhitespaceSegment(context.segment.raw + " "),
                        context.segment,
                    ],
                )
            ],
        )


def test__rules__user_rules():
    """Test that can safely add user rules."""
    # Set up a linter with the user rule
    linter = Linter(user_rules=[Rule_T042], dialect="ansi")
    # Make sure the new one is in there.
    assert RuleTuple("T042", "", "A dummy rule.", ("all",), ()) in linter.rule_tuples()
    # Instantiate a second linter and check it's NOT in there.
    # This tests that copying and isolation works.
    linter = Linter(dialect="ansi")
    assert not any(rule[0] == "T042" for rule in linter.rule_tuples())


@pytest.mark.parametrize(
    "rules, exclude_rules, resulting_codes",
    [
        # NB: We don't check the "select nothing" case, because not setting
        # the rules setting just means "select everything".
        # ("", "", set()),
        # 1: Select by code.
        # NOTE: T012 uses T011 as it's name but that should be ignored
        # because of the conflict.
        ("T010", "", {"T010"}),
        ("T010,T011", "", {"T010", "T011"}),
        ("T010,T011", "T011", {"T010"}),
        # 2: Select by name
        # NOTE: T012 uses "fake_other" as it's group but that should be ignored
        # because of the conflict.
        ("fake_basic", "", {"T010"}),
        ("fake_other", "", {"T011"}),
        ("fake_basic,fake_other", "", {"T010", "T011"}),
        # 3: Select by group
        # NOTE: T010 uses "foo" as it's alias but that should be ignored
        # because of the conflict.
        ("test", "", {"T010", "T011"}),
        ("foo", "", {"T011", "T012"}),
        ("test,foo", "", {"T010", "T011", "T012"}),
        ("test", "foo", {"T010"}),
        # 3: Select by alias
        ("fb1", "", {"T010"}),
        ("fb2", "", {"T011"}),
    ],
)
def test__rules__rule_selection(rules, exclude_rules, resulting_codes):
    """Test that rule selection works by various means."""

    class Rule_T010(BaseRule):
        """Fake Basic Rule."""

        groups = ("all", "test")
        name = "fake_basic"
        aliases = ("fb1", "foo")  # NB: Foo is a group on another rule.
        crawl_behaviour = RootOnlyCrawler()

        def _eval(self, **kwargs):
            pass

    class Rule_T011(Rule_T010):
        """Fake Basic Rule.

        NOTE: We inherit crawl behaviour and _eval from above.
        """

        groups = ("all", "test", "foo")
        name = "fake_other"
        aliases = ("fb2",)

    class Rule_T012(Rule_T010):
        """Fake Basic Rule.

        NOTE: We inherit crawl behaviour and _eval from above.
        """

        # NB: "fake_other" is the name of another rule.
        groups = ("all", "foo", "fake_other")
        # No aliases, Name collides with the alias of another rule.
        name = "fake_again"
        aliases = ()

    cfg = FluffConfig(
        overrides={"rules": rules, "exclude_rules": exclude_rules, "dialect": "ansi"}
    )
    linter = Linter(config=cfg, user_rules=[Rule_T010, Rule_T011, Rule_T012])
    # Get the set of selected codes:
    selected_codes = set(tpl[0] for tpl in linter.rule_tuples())
    # Check selected rules
    assert selected_codes == resulting_codes


def test__rules__filter_unparsable():
    """Test that rules that handle their own crawling respect unparsable."""
    # Set up a linter with the user rule
    linter = Linter(user_rules=[Rule_T002], dialect="ansi", rules=["T002"])
    # Lint a simple parsable file and check we do get issues
    # It's parsable, so we should get issues.
    res = linter.lint_string("SELECT 1")
    assert any(v.rule_code() == "T002" for v in res.violations)
    # Lint an unparsable file. Check we don't get any violations.
    # It's not parsable so we shouldn't get issues.
    res = linter.lint_string("asd asdf sdfg")
    assert not any(v.rule_code() == "T002" for v in res.violations)


def test__rules__result_unparsable():
    """Test that the linter won't allow rules which make the file unparsable."""
    # Set up a linter with the user rule
    linter = Linter(user_rules=[Rule_T003], dialect="ansi", rules=["T003"])
    # Lint a simple parsable file and check we do get issues
    # It's parsable, so we should get issues.
    raw_sql = "SELECT 1 FROM a"
    with fluff_log_catcher(logging.WARNING, "sqlfluff") as caplog:
        res = linter.lint_string(raw_sql, fix=True)
    # Check we got the warning.
    assert "would result in an unparsable file" in caplog.text
    # Check we get the violation.
    assert any(v.rule_code() == "T003" for v in res.violations)
    # The resulting file should be _the same_ because it would have resulted
    # in an unparsable file if applied.
    assert res.tree.raw == raw_sql


def test__rules__unparsable_does_not_crash():
    """Test that rules don't crash when generating fixes on unparsable sections.

    This is a regression test for a bug where _choose_anchor_segment would
    crash with an AssertionError when trying to find a path to segments in
    unparsable sections. The fix should be gracefully skipped instead.

    Specifically tests LT02, LT05, and LT09 which have _adjust_anchors=True
    and were triggering this crash on T-SQL queries with reserved keywords
    used as identifiers when the line is also too long.
    """
    # Set up a linter with rules that have _adjust_anchors=True
    linter = Linter(dialect="tsql", rules=["LT09", "LT02", "LT05"])

    # This SQL has 'cursor' which is a reserved keyword in T-SQL, causing
    # an unparsable section when used as a column name without quotes.
    # The line is also long to trigger LT05 which has _adjust_anchors=True.
    sql_with_unparsable = (
        "SELECT\n"
        "  Race, cursor, Cha, Authority, Points, Gold, Bind, PX, PZ, PY, "
        "col2, col3, col4, col5,col6\n"
        "FROM USERDATA"
    )

    # This should NOT crash, even though rules try to generate fixes on
    # segments that end up in unparsable sections. Before the fix, this
    # would crash with: AssertionError: No path found from <FileSegment>
    # to <WordSegment: 'col6'>!
    res = linter.lint_string(sql_with_unparsable, fix=True)

    # We should get parsing errors (PRS violations) for the unparsable content
    parsing_errors = [v for v in res.violations if v.rule_code() == "PRS"]
    assert len(parsing_errors) > 0


@pytest.mark.parametrize(
    "sql_query, check_tuples",
    [
        (
            "SELECT * FROM foo",
            # Even though there's a runaway fix, we should still
            # find each issue once and not duplicates of them.
            [
                ("T001", 1, 7),
                ("T001", 1, 9),
                ("T001", 1, 14),
            ],
        ),
        # If the errors are disabled, they shouldn't come through.
        ("-- noqa: disable=all\nSELECT * FROM foo", []),
    ],
)
def test__rules__runaway_fail_catch(sql_query, check_tuples):
    """Test that we catch runaway rules."""
    runaway_limit = 5
    # Set up the config to only use the rule we are testing.
    cfg = FluffConfig(
        overrides={"rules": "T001", "runaway_limit": runaway_limit, "dialect": "ansi"}
    )
    # Lint it using the current config (while in fix mode)
    linter = Linter(config=cfg, user_rules=[Rule_T001])
    # In theory this step should result in an infinite
    # loop, but the loop limit should catch it.
    result = linter.lint_string(sql_query, fix=True)
    # When the linter hits the runaway limit, it returns the original SQL tree.
    assert result.tree.raw == sql_query
    # Check the issues found.
    assert result.check_tuples() == check_tuples


def test_rules_cannot_be_instantiated_without_declared_configs():
    """Ensure that new rules must be instantiated with config values."""

    class Rule_NewRule_ZZ99(BaseRule):
        """Testing Rule."""

        config_keywords = ["case_sensitive"]

    new_rule = Rule_NewRule_ZZ99(code="L000", description="", case_sensitive=False)
    assert new_rule.case_sensitive is False
    # Error is thrown since "case_sensitive" is defined in class,
    # but not upon instantiation
    with pytest.raises(ValueError):
        new_rule = Rule_NewRule_ZZ99(code="L000", description="")


def test_rules_legacy_doc_decorators(caplog):
    """Ensure that the deprecated decorators can still be imported but do nothing."""
    with fluff_log_catcher(logging.WARNING, "sqlfluff") as caplog:

        @document_fix_compatible
        @document_groups
        @document_configuration
        class Rule_NewRule_ZZ99(BaseRule):
            """Untouched Text."""

            pass

    # Check they didn't do anything to the docstring.
    assert Rule_NewRule_ZZ99.__doc__ == """Untouched Text."""
    # Check there are warnings.
    print("Records:")
    for record in caplog.records:
        print(record)
    assert "uses the @document_fix_compatible decorator" in caplog.text
    assert "uses the @document_groups decorator" in caplog.text
    assert "uses the @document_configuration decorator" in caplog.text


def test_rules_configs_are_dynamically_documented():
    """Ensure that rule configurations are added to the class docstring."""

    class RuleWithConfig_ZZ99(BaseRule):
        """A new rule with configuration."""

        config_keywords = ["unquoted_identifiers_policy"]

    print(f"RuleWithConfig_ZZ99.__doc__: {RuleWithConfig_ZZ99.__doc__!r}")
    assert "unquoted_identifiers_policy" in RuleWithConfig_ZZ99.__doc__

    class RuleWithoutConfig_ZZ99(BaseRule):
        """A new rule without configuration."""

        pass

    print(f"RuleWithoutConfig_ZZ99.__doc__: {RuleWithoutConfig_ZZ99.__doc__!r}")
    assert "Configuration" not in RuleWithoutConfig_ZZ99.__doc__


def test_rules_name_validation():
    """Ensure that rule names are validated."""
    with pytest.raises(SQLFluffUserError) as exc_info:

        class RuleWithoutBadName_ZZ99(BaseRule):
            """A new rule without configuration."""

            name = "MY-KEBAB-CASE-NAME"

    assert "Tried to define rule with unexpected name" in exc_info.value.args[0]
    assert "MY-KEBAB-CASE-NAME" in exc_info.value.args[0]


def test_rule_exception_is_caught_to_validation():
    """Assert that a rule that throws an exception returns it as a validation."""
    std_rule_set = get_ruleset()

    @std_rule_set.register
    class Rule_T000(BaseRule):
        """Rule that throws an exception."""

        groups = ("all",)
        crawl_behaviour = RootOnlyCrawler()

        def _eval(self, segment, parent_stack, **kwargs):
            raise Exception("Catch me or I'll deny any linting results from you")

    linter = Linter(
        config=FluffConfig(overrides=dict(rules="T000", dialect="ansi")),
        user_rules=[Rule_T000],
    )

    assert linter.lint_string("select 1").check_tuples() == [("T000", 1, 1)]


def test_rule_must_belong_to_all_group():
    """Assert correct 'groups' config for rule."""
    std_rule_set = get_ruleset()

    with pytest.raises(AssertionError):

        @std_rule_set.register
        class Rule_T000(BaseRule):
            """Badly configured rule, no groups attribute."""

            def _eval(self, **kwargs):
                pass

    with pytest.raises(AssertionError):

        @std_rule_set.register
        class Rule_T001(BaseRule):
            """Badly configured rule, no 'all' group."""

            groups = ()

            def _eval(self, **kwargs):
                pass


def test_std_rule_import_fail_bad_naming():
    """Check that rule import from file works."""
    assert get_rules_from_path(
        rules_path="test/fixtures/rules/custom/*.py",
        base_module="test.fixtures.rules.custom",
    ) == [Rule_L000, Rule_S000]

    with pytest.raises(AttributeError) as e:
        get_rules_from_path(
            rules_path="test/fixtures/rules/custom/bad_rule_name/*.py",
            base_module="test.fixtures.rules.custom.bad_rule_name",
        )

    e.match("Rule classes must be named in the format of")


def test_rule_set_return_informative_error_when_rule_not_registered():
    """Assert that a rule that throws an exception returns it as a validation."""
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    with pytest.raises(ValueError) as e:
        get_rule_from_set("L000", config=cfg)

    e.match("'L000' not in")


seg = WhitespaceSegment(
    pos_marker=PositionMarker(
        slice(0, 1), slice(0, 1), TemplatedFile(" ", fname="<str>")
    )
)


@pytest.mark.parametrize(
    "lint_result, expected",
    [
        (LintResult(), "LintResult(<empty>)"),
        (LintResult(seg), "LintResult(<WhitespaceSegment: ([L:  1, P:  1]) ' '>)"),
        (
            LintResult(seg, description="foo"),
            "LintResult(foo: <WhitespaceSegment: ([L:  1, P:  1]) ' '>)",
        ),
        (
            LintResult(
                seg,
                description="foo",
                fixes=[
                    LintFix("create_before", seg, edit=[seg]),
                    LintFix("create_after", seg, edit=[seg]),
                ],
            ),
            "LintResult(foo: <WhitespaceSegment: ([L:  1, P:  1]) ' '>+2F)",
        ),
    ],
)
def test_rules__lint_result_repr(lint_result, expected):
    """Test that repr(LintResult) works as expected."""
    assert repr(lint_result) == expected
