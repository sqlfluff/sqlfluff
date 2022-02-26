"""Test rules docstring."""
import pytest

from sqlfluff import lint
from sqlfluff.core.plugin.host import get_plugin_manager
from sqlfluff.core.rules.doc_decorators import is_configurable

KEYWORD_ANTI = "    **Anti-pattern**"
KEYWORD_BEST = "    **Best practice**"
KEYWORD_CODE_BLOCK = "\n    .. code-block:: sql\n"


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
                assert rule.__doc__.count(content) >= min_count, (
                    f"{rule.__name__} content {content} does not occur at least "
                    f"{min_count} times"
                )


def test_keyword_anti_before_best():
    """Test docstring anti pattern before best pattern."""
    for plugin_rules in get_plugin_manager().hook.get_rules():
        for rule in plugin_rules:
            if rule._check_docstring is True:
                assert rule.__doc__.index(KEYWORD_ANTI) < rule.__doc__.index(
                    KEYWORD_BEST
                ), (
                    f"{rule.__name__} keyword {KEYWORD_BEST} appears before "
                    f"{KEYWORD_ANTI}"
                )


def test_config_decorator():
    """Test rules with config_keywords have the @document_configuration decorator."""
    for plugin_rules in get_plugin_manager().hook.get_rules():
        for rule in plugin_rules:
            if hasattr(rule, "config_keywords"):
                assert is_configurable(rule), (
                    f"Rule {rule.__name__} has config but is not decorated with "
                    "@document_configuration to display that config."
                )


def test_backtick_replace():
    """Test replacing docstring double backticks for lint results."""
    sql = """
    SELECT
        DISTINCT(a),
        b
    FROM foo
    """
    result = lint(sql, rules=["L015"])
    # L015 docstring looks like:
    # ``DISTINCT`` used with parentheses.
    # Check the double bacticks (``) get replaced by a single quote (').
    assert result[0]["description"] == "'DISTINCT' used with parentheses."
