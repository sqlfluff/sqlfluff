"""Test the sqlfluff.utils.testing module."""

import pytest
from _pytest.outcomes import Failed, Skipped

from sqlfluff.utils.testing.rules import (
    RuleTestCase,
    assert_rule_fail_in_sql,
    assert_rule_pass_in_sql,
)


def test_assert_rule_fail_in_sql_handle_parse_error():
    """Util assert_rule_fail_in_sql should handle parse errors."""
    with pytest.raises(Failed) as failed_test:
        assert_rule_fail_in_sql(code="L000", sql="select from")
    failed_test.match("Found the following parse errors in test case:")


def test_assert_rule_fail_in_sql_should_fail_queries_that_unexpectedly_pass():
    """Util assert_rule_fail_in_sql should fail if no failure."""
    with pytest.raises(Failed) as failed_test:
        assert_rule_fail_in_sql(code="LT01", sql="select 1")
    failed_test.match("No LT01 failures found in query which should fail")


def test_assert_rule_pass_in_sql_should_handle_parse_error():
    """Util assert_rule_pass_in_sql should handle parse errors."""
    with pytest.raises(Failed) as failed_test:
        assert_rule_pass_in_sql(code="LT01", sql="select from")
    failed_test.match("Found unparsable section:")


def test_assert_rule_pass_in_sql_should_fail_when_there_are_violations():
    """Util assert_rule_pass_in_sql should fail when there are violations."""
    with pytest.raises(Failed) as failed_test:
        assert_rule_pass_in_sql(code="LT01", sql="select a , b from t")
    failed_test.match("Found LT01 failures in query which should pass")


def test_rules_test_case_skipped_when_test_case_skipped():
    """Test functionality of the `RuleTestCase` skip attribute."""
    rule_test_case = RuleTestCase(rule="CP01", skip="Skip this one for now")
    with pytest.raises(Skipped) as skipped_test:
        rule_test_case.evaluate()
    skipped_test.match("Skip this one for now")


def test_rules_test_case_has_variable_introspection(test_verbosity_level):
    """Make sure the helper gives variable introspection information on failure."""
    rule_test_case = RuleTestCase(
        rule="LT02",
        fail_str="""
            select
                a,
                    b
            from table
        """,
        # extra comma on purpose
        fix_str="""
            select
                a,
                b,
            from table
        """,
    )
    with pytest.raises(AssertionError) as skipped_test:
        rule_test_case.evaluate()
    if test_verbosity_level >= 2:
        # Enough to check that a query diff is displayed
        skipped_test.match("select")
