# flake8: noqa
"""Tests for L001."""
from .std_test import rules__test_helper


test_cases = {
    "pass": [],
    "fail": [
        {
            "query":
"""
SELECT 1     
""",
            "fixed":
"""
SELECT 1
""",
            "configs": None
        }
    ],
}


def test__rule_L001():
    rules__test_helper("L001", test_cases)
