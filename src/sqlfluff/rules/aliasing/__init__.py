"""The aliasing plugin bundle."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule, ConfigInfo


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get additional rule config validations and descriptions."""
    return {
        "aliasing": {
            "validation": ["implicit", "explicit"],
            "definition": (
                "Should alias have an explicit AS or is implicit aliasing required?"
            ),
        },
        "allow_scalar": {
            "validation": [True, False],
            "definition": (
                "Whether or not to allow a single element in the "
                " select clause to be without an alias."
            ),
        },
        "alias_case_check": {
            "validation": [
                "dialect",
                "case_insensitive",
                "quoted_cs_naked_upper",
                "quoted_cs_naked_lower",
                "case_sensitive",
            ],
            "definition": "How to handle comparison casefolding in an alias.",
        },
        "min_alias_length": {
            "validation": range(1000),
            "definition": (
                "The minimum length of an alias to allow without raising a violation."
            ),
        },
        "max_alias_length": {
            "validation": range(1000),
            "definition": (
                "The maximum length of an alias to allow without raising a violation."
            ),
        },
    }


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.aliasing.AL01 import Rule_AL01
    from sqlfluff.rules.aliasing.AL02 import Rule_AL02
    from sqlfluff.rules.aliasing.AL03 import Rule_AL03
    from sqlfluff.rules.aliasing.AL04 import Rule_AL04
    from sqlfluff.rules.aliasing.AL05 import Rule_AL05
    from sqlfluff.rules.aliasing.AL06 import Rule_AL06
    from sqlfluff.rules.aliasing.AL07 import Rule_AL07
    from sqlfluff.rules.aliasing.AL08 import Rule_AL08
    from sqlfluff.rules.aliasing.AL09 import Rule_AL09

    return [
        Rule_AL01,
        Rule_AL02,
        Rule_AL03,
        Rule_AL04,
        Rule_AL05,
        Rule_AL06,
        Rule_AL07,
        Rule_AL08,
        Rule_AL09,
    ]
