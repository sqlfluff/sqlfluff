"""Documenting and validating rule configuration.

Provide a mapping with all configuration options, with information
on valid inputs and definitions.

This mapping is used to validate rule config inputs, as well
as document rule configuration.
"""

from typing import Any, Dict

from sqlfluff.core.plugin.host import get_plugin_manager

STANDARD_CONFIG_INFO_DICT: Dict[str, Dict[str, Any]] = {
    "tab_space_size": {
        "validation": range(100),
        "definition": (
            "The number of spaces to consider equal to one tab. "
            "Used in the fixing step of this rule."
        ),
    },
    "indent_unit": {
        "validation": ["space", "tab"],
        "definition": "Whether to use tabs or spaces to add new indents.",
    },
    "hanging_indents": {
        "validation": [True, False],
        "definition": (
            "Whether hanging indents will be considered when evaluating the "
            "indentation of a file."
        ),
    },
    "allow_scalar": {
        "validation": [True, False],
        "definition": (
            "Whether or not to allow a single element in the "
            " select clause to be without an alias."
        ),
    },
    "single_table_references": {
        "validation": ["consistent", "qualified", "unqualified"],
        "definition": "The expectation for references in single-table select.",
    },
    "force_enable": {
        "validation": [True, False],
        "definition": (
            "Run this rule even for dialects where this rule is disabled by default."
        ),
    },
    "unquoted_identifiers_policy": {
        "validation": ["all", "aliases", "column_aliases"],
        "definition": "Types of unquoted identifiers to flag violations for.",
    },
    "quoted_identifiers_policy": {
        "validation": ["all", "aliases", "column_aliases", "none"],
        "definition": "Types of quoted identifiers to flag violations for.",
    },
    "capitalisation_policy": {
        "validation": ["consistent", "upper", "lower", "capitalise"],
        "definition": "The capitalisation policy to enforce.",
    },
    "extended_capitalisation_policy": {
        "validation": ["consistent", "upper", "lower", "pascal", "capitalise"],
        "definition": (
            "The capitalisation policy to enforce, extended with PascalCase. "
            "This is separate from ``capitalisation_policy`` as it should not be "
            "applied to keywords."
        ),
    },
    "select_clause_trailing_comma": {
        "validation": ["forbid", "require"],
        "definition": (
            "Should trailing commas within select clauses be required or forbidden?"
        ),
    },
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
    "ignore_words": {
        "definition": ("Comma separated list of words to ignore from rule"),
    },
    "ignore_words_regex": {
        "definition": (
            "Words to ignore from rule if they are a partial match for the regular "
            "expression. To ignore only full matches you can use ``^`` (beginning "
            "of text) and ``$`` (end of text). Due to regular expression operator "
            "precedence, it is good practice to use parentheses around everything "
            "between ``^`` and ``$``."
        ),
    },
    "forbid_subquery_in": {
        "validation": ["join", "from", "both"],
        "definition": "Which clauses should be linted for subqueries?",
    },
    "prefer_count_1": {
        "validation": [True, False],
        "definition": ("Should count(1) be preferred over count(*) and count(0)?"),
    },
    "prefer_count_0": {
        "validation": [True, False],
        "definition": ("Should count(0) be preferred over count(*) and count(1)?"),
    },
    "operator_new_lines": {
        "validation": ["before", "after"],
        "definition": ("Should operator be placed before or after newlines?"),
    },
    "aliasing": {
        "validation": ["implicit", "explicit"],
        "definition": (
            "Should alias have an explicit AS or is implicit aliasing required?"
        ),
    },
    "fully_qualify_join_types": {
        "validation": ["inner", "outer", "both"],
        "definition": ("Which types of JOIN clauses should be fully qualified?"),
    },
    "multiline_newline": {
        "validation": [True, False],
        "definition": (
            "Should semi-colons be placed on a new line after multi-line statements?"
        ),
    },
    "require_final_semicolon": {
        "validation": [True, False],
        "definition": (
            "Should final semi-colons be required? "
            "(N.B. forcing trailing semi-colons is not recommended for dbt users "
            "as it can cause issues when wrapping the query within other SQL queries)."
        ),
    },
    "group_by_and_order_by_style": {
        "validation": ["consistent", "implicit", "explicit"],
        "definition": (
            "The expectation for using explicit column name references "
            "or implicit positional references."
        ),
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
            "If ``True``, requires every keyword used as an identifier to be quoted. "
            "Defaults to ``False``."
        ),
    },
    "blocked_words": {
        "definition": (
            "Optional, comma-separated list of blocked words which should not be used "
            "in statements."
        ),
    },
    "blocked_regex": {
        "definition": (
            "Optional, regex of blocked pattern which should not be used in statements."
        ),
    },
    "match_source": {
        "definition": (
            "Optional, also match regex of blocked pattern before applying templating"
        ),
    },
    "preferred_quoted_literal_style": {
        "validation": ["consistent", "single_quotes", "double_quotes"],
        "definition": (
            "Preferred quoting style to use for the quoted literals. If set to "
            "``consistent`` quoting style is derived from the first quoted literal"
            "in the file."
        ),
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
    "wildcard_policy": {
        "validation": ["single", "multiple"],
        "definition": "Treatment of wildcards. Defaults to ``single``.",
    },
    "preferred_type_casting_style": {
        "validation": ["consistent", "shorthand", "convert", "cast"],
        "definition": ("The expectation for using sql type casting"),
    },
    "preferred_first_table_in_join_clause": {
        "validation": ["earlier", "later"],
        "definition": (
            "Which table to list first when joining two tables. "
            "Defaults to ``earlier``."
        ),
    },
    "preferred_not_equal_style": {
        "validation": ["consistent", "c_style", "ansi"],
        "definition": (
            "The style for using not equal to operator. Defaults to ``consistent``."
        ),
    },
}


def get_config_info() -> Dict[str, Any]:
    """Get the config from core sqlfluff and sqlfluff plugins and merges them."""
    plugin_manager = get_plugin_manager()
    configs_info = plugin_manager.hook.get_configs_info()
    return {
        k: v for config_info_dict in configs_info for k, v in config_info_dict.items()
    }
