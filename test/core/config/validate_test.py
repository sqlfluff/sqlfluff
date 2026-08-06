"""Tests for the config validation routines."""

import logging

import pytest

from sqlfluff.core.config.removed import (
    REMOVED_CONFIGS,
    validate_config_dict_for_removed,
)
from sqlfluff.core.config.validate import (
    _validate_indentation_config,
    _validate_int_config,
    _validate_layout_config,
    _validate_max_parse_depth_config,
    _validate_max_parse_nodes_config,
    validate_config_dict,
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


def test__validate_configs_max_line_length_migration():
    """Test migration of the deprecated `rules:max_line_length` config.

    The replacement value is resolved from the `core` section, so the
    migrated value must land there rather than at the root of the config.
    """
    old_key = ("rules", "max_line_length")
    new_key = ("core", "max_line_length")
    # Confirm this key is still translated (guards against the test drifting).
    assert any(
        k.old_path == old_key and k.new_path == new_key for k in REMOVED_CONFIGS
    ), (
        "This test depends on this key still being removed. Update the test to "
        "one that is if this one isn't."
    )
    # NOTE: A `core` section is present, as it would be for any config loaded
    # from a file (the `[sqlfluff]` section is loaded as `core`).
    config = {"core": {"dialect": "ansi"}, "rules": {"max_line_length": 30}}
    validate_config_dict_for_removed(config, "<test>")
    assert config == {"core": {"dialect": "ansi", "max_line_length": 30}}


def test__validate_configs_max_line_length_precedence():
    """The new `max_line_length` value should win over the deprecated one."""
    config = {
        "core": {"dialect": "ansi", "max_line_length": 50},
        "rules": {"max_line_length": 30},
    }
    validate_config_dict_for_removed(config, "<test>")
    assert config == {"core": {"dialect": "ansi", "max_line_length": 50}}


def test__validate_configs_removed_new_key_display():
    """A migrated key should be quoted the way a user would write it.

    `core` is the internal name of the root `[sqlfluff]` section. In ini style
    configs a warning naming `core:max_line_length` would send people to a
    section that does not exist and leave the setting ignored, while in
    `pyproject.toml` the same setting really does live under
    `[tool.sqlfluff.core]` and the prefix must stay.
    """
    record = next(
        k for k in REMOVED_CONFIGS if k.old_path == ("rules", "max_line_length")
    )
    assert record.new_path == ("core", "max_line_length")
    assert record.formatted_new_key() == "max_line_length"
    assert record.formatted_new_key(toml=True) == "core:max_line_length"


@pytest.mark.parametrize(
    "logging_reference,expected",
    [
        (".sqlfluff", "`max_line_length`"),
        ("setup.cfg", "`max_line_length`"),
        ("/some/path/pyproject.toml", "`core:max_line_length`"),
        # Only `pyproject.toml` is loaded as toml. Any other name is read as
        # ini whatever its extension, so it takes the ini spelling.
        ("/some/path/custom.toml", "`max_line_length`"),
        ("/some/path/Pyproject.TOML", "`max_line_length`"),
        ("<config string>", "`max_line_length`"),
    ],
)
def test__validate_configs_removed_warning_is_source_aware(
    logging_reference, expected, caplog
):
    """The migration warning quotes the key for the format being read.

    An ini config takes `max_line_length` at the root of `[sqlfluff]`, but a
    `pyproject.toml` needs it under `[tool.sqlfluff.core]`, so a single
    spelling cannot be correct for both. The format is decided by filename in
    `_load_raw_file_as_dict`, so the warning has to key off the same thing.
    """
    config = records_to_nested_dict([(("rules", "max_line_length"), 800)])
    with caplog.at_level(logging.WARNING, logger="sqlfluff.config"):
        validate_config_dict_for_removed(config, logging_reference)
    assert expected in caplog.text
    # The functional migration is unaffected by how the warning is rendered.
    assert config == {"core": {"max_line_length": 800}}


@pytest.mark.parametrize(
    "old_value,expected",
    [
        # Booleans, as produced by ini configs and native toml booleans.
        (False, "forbid"),
        (True, "allow"),
        # Quoted booleans, as preserved by toml (e.g. `= "false"`). These must
        # coerce like ini values so that a quoted "false" still maps to "forbid"
        # rather than being treated as a truthy string.
        ("false", "forbid"),
        ("true", "allow"),
        ("False", "forbid"),
        ("True", "allow"),
    ],
)
def test__validate_configs_allow_implicit_indents_translation(old_value, expected):
    """Test translation of the deprecated allow_implicit_indents config."""
    old_key = ("indentation", "allow_implicit_indents")
    new_key = ("indentation", "implicit_indents")
    # Confirm this key is still translated (guards against the test drifting).
    assert any(
        k.old_path == old_key and k.new_path == new_key for k in REMOVED_CONFIGS
    ), (
        "This test depends on this key still being removed. Update the test to "
        "one that is if this one isn't."
    )
    config = records_to_nested_dict([(old_key, old_value)])
    validate_config_dict_for_removed(config, "<test>")
    assert config == {"indentation": {"implicit_indents": expected}}


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


@pytest.mark.parametrize(
    "config_dict,expected",
    [
        ({"core": {"max_parse_depth": None}}, 0),
        ({"core": {"max_parse_depth": ""}}, 0),
        ({"core": {"max_parse_depth": 0}}, 0),
        ({"core": {"max_parse_depth": 25}}, 25),
    ],
)
def test__validate_max_parse_depth_valid(config_dict, expected):
    """Test valid and normalized max_parse_depth values."""
    _validate_max_parse_depth_config(config_dict, "<test>")
    assert config_dict["core"]["max_parse_depth"] == expected


@pytest.mark.parametrize(
    "config_dict,config_warning",
    [
        (
            {"core": {"max_parse_depth": "invalid"}},
            "set an invalid value for `max_parse_depth`: 'invalid'",
        ),
        (
            {"core": {"max_parse_depth": True}},
            "set an invalid value for `max_parse_depth`: True",
        ),
        (
            {"core": {"max_parse_depth": -1}},
            "set an invalid value for `max_parse_depth`: -1",
        ),
    ],
)
def test__validate_max_parse_depth_invalid(config_dict, config_warning):
    """Test invalid max_parse_depth values are rejected."""
    with pytest.raises(SQLFluffUserError) as excinfo:
        _validate_max_parse_depth_config(config_dict, "<test>")
    assert config_warning in str(excinfo.value)


@pytest.mark.parametrize(
    "config_dict,expected",
    [
        ({"core": {"max_parse_nodes": None}}, 0),
        ({"core": {"max_parse_nodes": ""}}, 0),
        ({"core": {"max_parse_nodes": 0}}, 0),
        ({"core": {"max_parse_nodes": 2500}}, 2500),
    ],
)
def test__validate_max_parse_nodes_valid(config_dict, expected):
    """Test valid and normalized max_parse_nodes values."""
    _validate_max_parse_nodes_config(config_dict, "<test>")
    assert config_dict["core"]["max_parse_nodes"] == expected


@pytest.mark.parametrize(
    "config_dict,config_warning",
    [
        (
            {"core": {"max_parse_nodes": "invalid"}},
            "set an invalid value for `max_parse_nodes`: 'invalid'",
        ),
        (
            {"core": {"max_parse_nodes": True}},
            "set an invalid value for `max_parse_nodes`: True",
        ),
        (
            {"core": {"max_parse_nodes": -1}},
            "set an invalid value for `max_parse_nodes`: -1",
        ),
    ],
)
def test__validate_max_parse_nodes_invalid(config_dict, config_warning):
    """Test invalid max_parse_nodes values are rejected."""
    with pytest.raises(SQLFluffUserError) as excinfo:
        _validate_max_parse_nodes_config(config_dict, "<test>")
    assert config_warning in str(excinfo.value)


@pytest.mark.parametrize(
    "config_dict",
    [
        {"core": {"render_variant_limit": 1}},
        {"core": {"runaway_limit": 10}},
        {"core": {}},  # missing key should be ok
        {},  # no core section should be ok
    ],
)
def test__validate_int_config_valid(config_dict):
    """Test valid integer core config values are accepted."""
    # Should not raise for either key.
    _validate_int_config(config_dict, "render_variant_limit", 1, "<test>")
    _validate_int_config(config_dict, "runaway_limit", 1, "<test>")


@pytest.mark.parametrize(
    "config_dict,key,config_warning",
    [
        (
            {"core": {"render_variant_limit": "lots"}},
            "render_variant_limit",
            "set an invalid value for `render_variant_limit`: 'lots'",
        ),
        (
            {"core": {"render_variant_limit": True}},
            "render_variant_limit",
            "set an invalid value for `render_variant_limit`: True",
        ),
        (
            {"core": {"render_variant_limit": 0}},
            "render_variant_limit",
            "set an invalid value for `render_variant_limit`: 0",
        ),
        (
            {"core": {"runaway_limit": "lots"}},
            "runaway_limit",
            "set an invalid value for `runaway_limit`: 'lots'",
        ),
        (
            {"core": {"runaway_limit": -1}},
            "runaway_limit",
            "set an invalid value for `runaway_limit`: -1",
        ),
    ],
)
def test__validate_int_config_invalid(config_dict, key, config_warning):
    """Test invalid integer core config values are rejected."""
    with pytest.raises(SQLFluffUserError) as excinfo:
        _validate_int_config(config_dict, key, 1, "<test>")
    assert config_warning in str(excinfo.value)


@pytest.mark.parametrize(
    "config_dict,config_warning",
    [
        (
            {"core": {"render_variant_limit": "lots"}},
            "set an invalid value for `render_variant_limit`: 'lots'",
        ),
        (
            {"core": {"runaway_limit": "lots"}},
            "set an invalid value for `runaway_limit`: 'lots'",
        ),
    ],
)
def test__validate_config_dict_rejects_bad_int_limits(config_dict, config_warning):
    """A non-integer render_variant_limit/runaway_limit raises a clean error.

    Previously these flowed unchecked to numeric-use sites: a bad
    render_variant_limit crashed `sqlfluff lint` with an uncaught TypeError, and
    a bad runaway_limit was swallowed as an 'internal error' during
    `sqlfluff fix`. They should behave like their validated siblings.
    """
    with pytest.raises(SQLFluffUserError) as excinfo:
        validate_config_dict(config_dict, "<test>")
    assert config_warning in str(excinfo.value)
