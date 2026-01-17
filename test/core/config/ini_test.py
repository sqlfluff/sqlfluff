"""Tests for INI config file parsing."""

from sqlfluff.core.config.ini import load_ini_string


def test__config__ini_dotted_keys_create_nested_structure():
    """Test that dotted keys in INI files create nested dictionary structures."""
    # Test case for issue #7318: dotted notation should create nested structures
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


def test__config__ini_dotted_keys_with_types():
    """Test that dotted keys work with type coercion."""
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


def test__config__ini_non_context_sections_unchanged():
    """Test that non-context sections still work normally."""
    config_string = """
[sqlfluff]
dialect = bigquery
max_line_length = 80

[sqlfluff:rules]
tab_space_size = 4
"""

    result = load_ini_string(config_string)

    # Non-context sections should work as before (no dot splitting)
    assert result == {
        "core": {
            "dialect": "bigquery",
            "max_line_length": 80,
        },
        "rules": {
            "tab_space_size": 4,
        },
    }
