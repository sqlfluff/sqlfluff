"""Documenting and validating rule configuration.

Provide a mapping with all configuration options, with information
on valid inputs and definitions.

This mapping is used to validate rule config inputs, as well
as document rule configuration.
"""

STANDARD_CONFIG_INFO_DICT = {
    "tab_space_size": {
        "validation": range(100),
        "definition": (
            "The number of spaces to consider equal to one tab. "
            "Used in the fixing step of this rule"
        ),
    },
    "max_line_length": {
        "validation": range(1000),
        "definition": (
            "The maximum length of a line to allow without " "raising a violation"
        ),
    },
    "indent_unit": {
        "validation": ["space", "tab"],
        "definition": "Whether to use tabs or spaces to add new indents",
    },
    "comma_style": {
        "validation": ["leading", "trailing"],
        "definition": "The comma style to to enforce",
    },
    "allow_scalar": {
        "validation": [True, False],
        "definition": (
            "Whether or not to allow a single element in the "
            " select clause to be without an alias"
        ),
    },
    "single_table_references": {
        "validation": ["consistent", "qualified", "unqualified"],
        "definition": "The expectation for references in single-table select",
    },
    "only_aliases": {
        "validation": [True, False],
        "definition": (
            "Whether or not to flags violations for only alias expressions "
            "or all unquoted identifiers"
        ),
    },
    "capitalisation_policy": {
        "validation": ["consistent", "upper", "lower", "capitalise"],
        "definition": "The capitalisation policy to enforce",
    },
    "lint_templated_tokens": {
        "validation": [True, False],
        "definition": (
            "Should lines starting with a templating placeholder"
            " such as `{{blah}}` have their indentation linted."
        ),
    },
}
