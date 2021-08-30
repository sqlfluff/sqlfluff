"""Test rules docstring"""
import pytest

from sqlfluff.core.plugin.host import get_plugin_manager

KEYWORD_ANTI = "\n    | **Anti-pattern**"
KEYWORD_BEST = "\n    | **Best practice**"
KEYWORD_CODE_BLOCK = "\n    .. code-block:: sql\n"


@pytest.mark.parametrize(
    "content,count",
    [
        (KEYWORD_ANTI, 1),
        (KEYWORD_BEST, 1),
        (KEYWORD_CODE_BLOCK, 2),
    ]
)
def test_content_count(content, count):
    """Test docstring have specific content"""
    for plugin_rules in get_plugin_manager().hook.get_rules():
        for rule in plugin_rules:
            if rule._check_docstring is True:
                assert rule.__doc__.count(content) == count, \
                    f"{rule.__name__} do not occurrences content {content} with {count} times"


def test_keyword_anti_before_best():
    """Test docstring anti pattern before best pattern"""
    for plugin_rules in get_plugin_manager().hook.get_rules():
        for rule in plugin_rules:
            if rule._check_docstring is True:
                assert rule.__doc__.index(KEYWORD_ANTI) < rule.__doc__.index(KEYWORD_BEST), \
                    f"{rule.__name__} keyword {KEYWORD_BEST} appear before {KEYWORD_ANTI}"



