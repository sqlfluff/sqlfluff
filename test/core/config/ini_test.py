"""Tests for INI config file parsing."""

import pytest

from sqlfluff.core.config.ini import load_ini_string
from sqlfluff.core.errors import SQLFluffUserError


def test__config__ini_dotted_keys_nested_structure():
    """Test that dotted keys create nested dictionary structures.

    Regression test for issue #7318.
    """
    config_string = """
[sqlfluff:templater:jinja:context]
namespace.projectname=test
namespace.env=prep
other.nested.key=value
simple_key=simple_value
"""

    result = load_ini_string(config_string)

    # Check that dotted keys created nested structures
    assert result == {
        "templater": {
            "jinja": {
                "context": {
                    "namespace": {
                        "projectname": "test",
                        "env": "prep",
                    },
                    "other": {
                        "nested": {
                            "key": "value",
                        },
                    },
                    "simple_key": "simple_value",
                },
            },
        },
    }


def test__config__ini_dotted_keys_type_coercion():
    """Test that dotted keys work correctly with type coercion."""
    config_string = """
[sqlfluff:templater:jinja:context]
namespace.count=42
namespace.ratio=3.14
namespace.enabled=true
namespace.disabled=false
namespace.nullable=none
"""

    result = load_ini_string(config_string)

    assert result == {
        "templater": {
            "jinja": {
                "context": {
                    "namespace": {
                        "count": 42,
                        "ratio": 3.14,
                        "enabled": True,
                        "disabled": False,
                        "nullable": None,
                    },
                },
            },
        },
    }


def test__config__ini_simple_keys_without_dots():
    """Test that simple keys without dots continue to work as expected."""
    config_string = """
[sqlfluff]
dialect = bigquery
max_line_length = 80

[sqlfluff:rules]
tab_space_size = 4
"""

    result = load_ini_string(config_string)

    assert result == {
        "core": {
            "dialect": "bigquery",
            "max_line_length": 80,
        },
        "rules": {
            "tab_space_size": 4,
        },
    }


def test__config__ini_dotted_keys_all_sections():
    """Test that dotted key splitting applies to all sections."""
    config_string = """
[sqlfluff:rules]
some.nested.config = value
"""

    result = load_ini_string(config_string)

    assert result == {
        "rules": {
            "some": {
                "nested": {
                    "config": "value",
                },
            },
        },
    }


@pytest.mark.parametrize(
    "config_string, expected_snippet",
    [
        (
            "[sqlfluff\ndialect = ansi\n",
            "File contains no section headers",
        ),
        (
            "[sqlfluff]\ndialect = ansi\nnot a key val\n",
            "Source contains parsing errors",
        ),
        (
            "[sqlfluff]\ndialect = ansi\ndialect = postgres\n",
            "already exists",
        ),
    ],
)
def test__config__ini_syntax_error(config_string, expected_snippet):
    """Test that invalid INI config syntax raises SQLFluffUserError."""
    with pytest.raises(SQLFluffUserError) as exc_info:
        load_ini_string(config_string, filename=".sqlfluff")

    error_msg = str(exc_info.value)
    assert "Failed to parse INI config file .sqlfluff" in error_msg
    assert expected_snippet in error_msg


def test__config__ini_syntax_error_no_filename():
    """Test that invalid INI config without filename raises SQLFluffUserError."""
    with pytest.raises(SQLFluffUserError) as exc_info:
        load_ini_string("[sqlfluff\ndialect = ansi\n")

    error_msg = str(exc_info.value)
    assert "Failed to parse INI config file:" in error_msg
    assert "File contains no section headers" in error_msg
