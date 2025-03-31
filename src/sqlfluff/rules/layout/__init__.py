"""The layout plugin bundle."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule, ConfigInfo


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get additional rule config validations and descriptions."""
    return {
        "ignore_comment_lines": {
            "validation": [True, False],
            "definition": (
                "Should lines that contain only whitespace and comments"
                " be ignored when linting line lengths?"
            ),
        },
        "ignore_comment_clauses": {
            "validation": [True, False],
            "definition": (
                "Should comment clauses (e.g. column comments) be ignored"
                " when linting line lengths?"
            ),
        },
        "maximum_empty_lines_between_statements": {
            "validation": range(1000),
            "definition": (
                "The maximum number of empty lines allowed between statements. "
                "Note that currently, the gap _before_ and _after_ the semicolon "
                "is considered 'between' statements."
            ),
        },
        "maximum_empty_lines_inside_statements": {
            "validation": range(1000),
            "definition": (
                "The maximum number of empty lines allowed inside statements."
            ),
        },
        "wildcard_policy": {
            "validation": ["single", "multiple"],
            "definition": "Treatment of wildcards. Defaults to ``single``.",
        },
    }


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.layout.LT01 import Rule_LT01
    from sqlfluff.rules.layout.LT02 import Rule_LT02
    from sqlfluff.rules.layout.LT03 import Rule_LT03
    from sqlfluff.rules.layout.LT04 import Rule_LT04
    from sqlfluff.rules.layout.LT05 import Rule_LT05
    from sqlfluff.rules.layout.LT06 import Rule_LT06
    from sqlfluff.rules.layout.LT07 import Rule_LT07
    from sqlfluff.rules.layout.LT08 import Rule_LT08
    from sqlfluff.rules.layout.LT09 import Rule_LT09
    from sqlfluff.rules.layout.LT10 import Rule_LT10
    from sqlfluff.rules.layout.LT11 import Rule_LT11
    from sqlfluff.rules.layout.LT12 import Rule_LT12
    from sqlfluff.rules.layout.LT13 import Rule_LT13
    from sqlfluff.rules.layout.LT14 import Rule_LT14
    from sqlfluff.rules.layout.LT15 import Rule_LT15

    return [
        Rule_LT01,
        Rule_LT02,
        Rule_LT03,
        Rule_LT04,
        Rule_LT05,
        Rule_LT06,
        Rule_LT07,
        Rule_LT08,
        Rule_LT09,
        Rule_LT10,
        Rule_LT11,
        Rule_LT12,
        Rule_LT13,
        Rule_LT14,
        Rule_LT15,
    ]
