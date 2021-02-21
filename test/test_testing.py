"""Test the sqlfluff.testing module."""

from _pytest.outcomes import Failed
import pytest
from sqlfluff.testing.rules import (
    assert_rule_fail_in_sql,
    assert_rule_pass_in_sql,
)


def test_assert_rule_fail_in_sql_handle_parse_error():
    """Util assert_rule_fail_in_sql should handle parse errors."""
    with pytest.raises(Failed) as failed_test:
        assert_rule_fail_in_sql(code="L000", sql="select from")
    failed_test.match("Found the following parse errors in test case:")


def test_assert_rule_fail_in_sql_should_fail_queries_that_unexpectedly_pass():
    """Util assert_rule_fail_in_sql should fail tests when a query passes rules that it violates."""
    with pytest.raises(Failed) as failed_test:
        assert_rule_fail_in_sql(code="L001", sql="select 1")
    failed_test.match("No L001 failures found in query which should fail")


def test_assert_rule_pass_in_sql_should_handle_parse_error():
    """Util assert_rule_pass_in_sql should handle parse errors."""
    with pytest.raises(Failed) as failed_test:
        assert_rule_pass_in_sql(code="L001", sql="select from")
    failed_test.match("Found unparsable section:")


def test_assert_rule_pass_in_sql_should_fail_when_there_are_violations():
    """Util assert_rule_pass_in_sql should fail when there are violations."""
    with pytest.raises(Failed) as failed_test:
        assert_rule_pass_in_sql(code="L005", sql="select a , b from t")
    failed_test.match("Found L005 failures in query which should pass")
