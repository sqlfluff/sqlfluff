"""The references plugin bundle."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule, ConfigInfo


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get additional rule config validations and descriptions."""
    return {
        "subqueries_ignore_external_references": {
            "validation": [True, False],
            "definition": "If ``True``, parent query references are not included as "
            "potentially ambiguous in subqueries. Defaults to ``False``.",
        },
        "single_table_references": {
            "validation": ["consistent", "qualified", "unqualified"],
            "definition": "The expectation for references in single-table select.",
        },
        "unquoted_identifiers_policy": {
            "validation": ["all", "aliases", "column_aliases", "table_aliases"],
            "definition": "Types of unquoted identifiers to flag violations for.",
        },
        "quoted_identifiers_policy": {
            "validation": ["all", "aliases", "column_aliases", "table_aliases", "none"],
            "definition": "Types of quoted identifiers to flag violations for.",
        },
        "allow_space_in_identifier": {
            "validation": [True, False],
            "definition": ("Should spaces in identifiers be allowed?"),
        },
        "additional_allowed_characters": {
            "definition": (
                "Optional list of extra allowed characters, "
                "in addition to alphanumerics (A-Z, a-z, 0-9) and underscores."
            ),
        },
        "prefer_quoted_identifiers": {
            "validation": [True, False],
            "definition": (
                "If ``True``, requires every identifier to be quoted. "
                "Defaults to ``False``."
            ),
        },
        "prefer_quoted_keywords": {
            "validation": [True, False],
            "definition": (
                "If ``True``, requires every keyword used as an identifier to be "
                "quoted. Defaults to ``False``."
            ),
        },
    }


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.references.RF01 import Rule_RF01
    from sqlfluff.rules.references.RF02 import Rule_RF02
    from sqlfluff.rules.references.RF03 import Rule_RF03
    from sqlfluff.rules.references.RF04 import Rule_RF04
    from sqlfluff.rules.references.RF05 import Rule_RF05
    from sqlfluff.rules.references.RF06 import Rule_RF06

    return [Rule_RF01, Rule_RF02, Rule_RF03, Rule_RF04, Rule_RF05, Rule_RF06]
