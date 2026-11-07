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
    "cfg_content",
    [
        # Missing "]" on the section header.
        "[sqlfluff\ndialect = ansi\n",
        # A line which is not a key/value pair.
        "[sqlfluff]\ndialect = ansi\nthis is not valid\n",
        # The same option given twice in one section.
        "[sqlfluff]\ndialect = ansi\ndialect = postgres\n",
    ],
)
def test__config__ini_invalid_syntax_raises_user_error(cfg_content):
    """Invalid INI syntax raises a user error instead of a configparser error.

    https://github.com/sqlfluff/sqlfluff/issues/9067
    """
    with pytest.raises(SQLFluffUserError) as exc_info:
        load_ini_string(cfg_content)

    assert "Failed to parse INI config" in str(exc_info.value)


def test__config__ini_invalid_syntax_includes_filepath():
    """The user error identifies the config file which failed to parse."""
    cfg_path = "/tmp/project/.sqlfluff"
    with pytest.raises(SQLFluffUserError) as exc_info:
        load_ini_string("[sqlfluff\n", cfg_path)

    message = str(exc_info.value)
    assert f"Failed to parse INI config file {cfg_path}" in message
