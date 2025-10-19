"""Tests for the config validation routines."""

import pytest

from sqlfluff.core.config.removed import (
    REMOVED_CONFIGS,
    validate_config_dict_for_removed,
)
from sqlfluff.core.config.validate import (
    _validate_layout_config,
    _validate_indentation_config,
)
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.helpers.dict import (
    iter_records_from_nested_dict,
    records_to_nested_dict,
)


def test__validate_configs_direct():
    """Test validate methods directly."""
    # Make sure there _are_ removed configs.
    assert REMOVED_CONFIGS
    # Make sure all raise an error if validated
    for k in REMOVED_CONFIGS:
        print(k)
        if k.translation_func and k.new_path:
            config = records_to_nested_dict([(k.old_path, "foo")])
            validate_config_dict_for_removed(config, "<test>")
            print(config)
            new_records = list(iter_records_from_nested_dict(config))
            # There should only be one
            assert len(new_records) == 1
            # And it should be the reassigned one
            assert new_records[0][0] == k.new_path
            # Really we should check that it's output here, but logging config
            # seems to make that hard.
        else:
            config = records_to_nested_dict([(k.old_path, "foo")])
            with pytest.raises(SQLFluffUserError) as excinfo:
                validate_config_dict_for_removed(config, "<test>")
            assert "set an outdated config" in str(excinfo.value)
            assert k.warning in str(excinfo.value)


def test__validate_configs_precedence_same_file():
    """Test _validate_configs method of FluffConfig where there's a conflict."""
    # Check with a known conflicted value
    old_key = ("rules", "LT03", "operator_new_lines")
    new_key = ("layout", "type", "binary_operator", "line_position")
    # Check it's still conflicted.
    assert any(
        k.old_path == old_key and k.new_path == new_key for k in REMOVED_CONFIGS
    ), (
        "This test depends on this key still being removed. Update the test to "
        "one that is if this one isn't."
    )
    # Test config
    config = records_to_nested_dict([(new_key, "foo"), (old_key, "foo")])
    # Before validation
    assert config == {
        "rules": {"LT03": {"operator_new_lines": "foo"}},
        "layout": {"type": {"binary_operator": {"line_position": "foo"}}},
    }
    validate_config_dict_for_removed(config, "<test>")
    # Check we only get the new key after validation
    assert config == {"layout": {"type": {"binary_operator": {"line_position": "foo"}}}}


@pytest.mark.parametrize(
    "config_dict,config_warning",
    [
        ({"layout": "foo"}, "Found value 'foo' instead of a valid layout section"),
        (
            {"layout": {"invalid": "foo"}},
            "Only sections of the form `sqlfluff:layout:type:...` are valid",
        ),
        (
            {"layout": {"type": {"foo": "bar"}}},
            "Expected a section",
        ),
        (
            {"layout": {"type": {"foo": {"bar": "baz"}}}},
            "Found the following invalid keys: {'bar'}",
        ),
        (
            {"layout": {"type": {"foo": {"spacing_before": {"a": "b"}}}}},
            "Found the an unexpected section rather than value",
        ),
    ],
)
def test__validate_layouts(config_dict, config_warning):
    """Test the layout validation checks."""
    with pytest.raises(SQLFluffUserError) as excinfo:
        _validate_layout_config(config_dict, "<test>")
    assert "set an invalid `layout` option" in str(excinfo.value)
    assert config_warning in str(excinfo.value)


@pytest.mark.parametrize(
    "config_dict,config_warning",
    [
        (
            {"indentation": {"implicit_indents": "invalid"}},
            "set an invalid value for `implicit_indents`: 'invalid'",
        ),
        (
            {"indentation": {"implicit_indents": "true"}},
            "set an invalid value for `implicit_indents`: 'true'",
        ),
        (
            {"indentation": {"implicit_indents": "REQUIRE"}},
            "set an invalid value for `implicit_indents`: 'REQUIRE'",
        ),
        (
            {"indentation": {"implicit_indents": ""}},
            "set an invalid value for `implicit_indents`: ''",
        ),
        (
            {"indentation": {"implicit_indents": 123}},
            "set an invalid value for `implicit_indents`: 123",
        ),
    ],
)
def test__validate_indentation_invalid(config_dict, config_warning):
    """Test the indentation validation checks for invalid values."""
    with pytest.raises(SQLFluffUserError) as excinfo:
        _validate_indentation_config(config_dict, "<test>")
    assert config_warning in str(excinfo.value)
    assert "Valid options are: forbid, allow, require" in str(excinfo.value)


@pytest.mark.parametrize(
    "config_dict",
    [
        {"indentation": {"implicit_indents": "forbid"}},
        {"indentation": {"implicit_indents": "allow"}},
        {"indentation": {"implicit_indents": "require"}},
        {"indentation": {}},  # missing key should be ok
        {},  # no indentation section should be ok
    ],
)
def test__validate_indentation_valid(config_dict):
    """Test the indentation validation checks for valid values."""
    # Should not raise any exception
    _validate_indentation_config(config_dict, "<test>")
