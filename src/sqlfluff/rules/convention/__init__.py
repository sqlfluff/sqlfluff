"""The convention plugin bundle."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule, ConfigInfo


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get additional rule config validations and descriptions."""
    return {
        "preferred_not_equal_style": {
            "validation": ["consistent", "c_style", "ansi"],
            "definition": (
                "The style for using not equal to operator. Defaults to ``consistent``."
            ),
        },
        "select_clause_trailing_comma": {
            "validation": ["forbid", "require"],
            "definition": (
                "Should trailing commas within select clauses be required or forbidden?"
            ),
        },
        "prefer_count_1": {
            "validation": [True, False],
            "definition": ("Should count(1) be preferred over count(*) and count(0)?"),
        },
        "prefer_count_0": {
            "validation": [True, False],
            "definition": ("Should count(0) be preferred over count(*) and count(1)?"),
        },
        "multiline_newline": {
            "validation": [True, False],
            "definition": (
                "Should semi-colons be placed on a new line after multi-line "
                "statements?"
            ),
        },
        "require_final_semicolon": {
            "validation": [True, False],
            "definition": (
                "Should final semi-colons be required? "
                "(N.B. forcing trailing semi-colons is not recommended for dbt users "
                "as it can cause issues when wrapping the query within other SQL "
                "queries)."
            ),
        },
        "preferred_quoted_literal_style": {
            "validation": ["consistent", "single_quotes", "double_quotes"],
            "definition": (
                "Preferred quoting style to use for the quoted literals. If set to "
                "``consistent`` quoting style is derived from the first quoted literal "
                "in the file."
            ),
        },
        "preferred_type_casting_style": {
            "validation": ["consistent", "shorthand", "convert", "cast"],
            "definition": ("The expectation for using sql type casting"),
        },
    }


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.convention.CV01 import Rule_CV01
    from sqlfluff.rules.convention.CV02 import Rule_CV02
    from sqlfluff.rules.convention.CV03 import Rule_CV03
    from sqlfluff.rules.convention.CV04 import Rule_CV04
    from sqlfluff.rules.convention.CV05 import Rule_CV05
    from sqlfluff.rules.convention.CV06 import Rule_CV06
    from sqlfluff.rules.convention.CV07 import Rule_CV07
    from sqlfluff.rules.convention.CV08 import Rule_CV08
    from sqlfluff.rules.convention.CV09 import Rule_CV09
    from sqlfluff.rules.convention.CV10 import Rule_CV10
    from sqlfluff.rules.convention.CV11 import Rule_CV11
    from sqlfluff.rules.convention.CV12 import Rule_CV12

    return [
        Rule_CV01,
        Rule_CV02,
        Rule_CV03,
        Rule_CV04,
        Rule_CV05,
        Rule_CV06,
        Rule_CV07,
        Rule_CV08,
        Rule_CV09,
        Rule_CV10,
        Rule_CV11,
        Rule_CV12,
    ]
