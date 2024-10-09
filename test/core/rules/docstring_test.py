"""Test rules docstring."""

import re

import pytest

from sqlfluff import lint
from sqlfluff.core.plugin.host import get_plugin_manager

KEYWORD_ANTI = re.compile(r"\*\*Anti-pattern\*\*")
KEYWORD_BEST = re.compile(r"\*\*Best practice\*\*")
KEYWORD_CODE_BLOCK = re.compile(r"\n\.\. code-block:: (sql|jinja)\n")


@pytest.mark.parametrize(
    "content,min_count",
    [
        (KEYWORD_ANTI, 1),
        (KEYWORD_BEST, 1),
        (KEYWORD_CODE_BLOCK, 2),
    ],
)
def test_content_count(content, min_count):
    """Test docstring have specific content."""
    for plugin_rules in get_plugin_manager().hook.get_rules():
        for rule in plugin_rules:
            if rule._check_docstring is True:
                assert len(content.findall(rule.__doc__)) >= min_count, (
                    f"{rule.__name__} content {content} does not occur at least "
                    f"{min_count} times"
                )


def test_keyword_anti_before_best():
    """Test docstring anti pattern before best pattern."""
    for plugin_rules in get_plugin_manager().hook.get_rules():
        for rule in plugin_rules:
            if rule._check_docstring is True:
                best_match = KEYWORD_BEST.search(rule.__doc__)
                anti_match = KEYWORD_ANTI.search(rule.__doc__)
                assert best_match
                assert anti_match
                best_pos = best_match.start()
                anti_pos = anti_match.start()
                assert anti_pos < best_pos, (
                    f"{rule.__name__} keyword {KEYWORD_BEST} appears before "
                    f"{KEYWORD_ANTI}"
                )


def test_backtick_replace():
    """Test replacing docstring double backticks for lint results."""
    sql = """
    SELECT
        DISTINCT(a),
        b
    FROM foo
    """
    result = lint(sql, rules=["ST08"])
    # ST08 docstring looks like:
    # ``DISTINCT`` used with parentheses.
    # Check the double bacticks (``) get replaced by a single quote (').
    assert result[0]["description"] == "'DISTINCT' used with parentheses."
