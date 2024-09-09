"""Tests for the configuration routines."""

import os
import sys
from contextlib import contextmanager
from unittest.mock import call, patch

import appdirs
import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.config import (
    load_config_at_path,
    load_config_file,
    load_config_string,
    load_config_up_to_path,
)
from sqlfluff.core.config.loader import (
    _get_user_config_dir_path,
    _load_user_appdir_config,
)
from sqlfluff.core.config.removed import (
    REMOVED_CONFIGS,
    validate_config_dict_for_removed,
)
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.helpers.dict import (
    iter_records_from_nested_dict,
    records_to_nested_dict,
)

config_a = {
    "core": {"testing_val": "foobar", "testing_int": 4, "dialect": "mysql"},
    "bar": {"foo": "barbar"},
}


@pytest.fixture
def mock_xdg_home(monkeypatch):
    """Sets the XDG_CONFIG_HOME variable."""
    monkeypatch.setenv("XDG_CONFIG_HOME", "~/.config/my/special/path")


def test__config__load_file_dir():
    """Test loading config from a directory path."""
    cfg = load_config_at_path(
        os.path.join("test", "fixtures", "config", "inheritance_a")
    )
    assert cfg == config_a


def test__config__load_from_string():
    """Test loading config from a string."""
    # Load a string
    with open(
        os.path.join("test", "fixtures", "config", "inheritance_a", ".sqlfluff")
    ) as f:
        config_string = f.read()
    cfg = load_config_string(config_string)
    assert cfg == config_a


def test__config__load_file_f():
    """Test loading config from a file path."""
    cfg = load_config_at_path(
        os.path.join("test", "fixtures", "config", "inheritance_a", "testing.sql")
    )
    assert cfg == config_a


def test__config__load_nested():
    """Test nested overwrite and order of precedence of config files."""
    cfg = load_config_up_to_path(
        os.path.join(
            "test", "fixtures", "config", "inheritance_a", "nested", "blah.sql"
        )
    )
    assert cfg == {
        "core": {
            "dialect": "mysql",
            "testing_val": "foobar",
            "testing_int": 1,
            "testing_bar": 7.698,
        },
        "bar": {"foo": "foobar"},
        "fnarr": {"fnarr": {"foo": "foobar"}},
    }


@contextmanager
def change_dir(path):
    """Set the current working directory to `path` for the duration of the context."""
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Seems test is not executed under home directory on Windows",
)
def test__config__load_parent():
    """Test that config is loaded from parent directory of current working directory."""
    with change_dir(
        os.path.join("test", "fixtures", "config", "inheritance_a", "nested")
    ):
        cfg = load_config_up_to_path("blah.sql")
    assert cfg == {
        "core": {
            "dialect": "mysql",
            "testing_val": "foobar",
            "testing_int": 1,
            "testing_bar": 7.698,
        },
        "bar": {"foo": "foobar"},
        "fnarr": {"fnarr": {"foo": "foobar"}},
    }


def test__config__load_toml():
    """Test loading config from a pyproject.toml file."""
    cfg = load_config_file(
        os.path.join("test", "fixtures", "config", "toml"),
        "pyproject.toml",
    )
    assert cfg == {
        "core": {
            "nocolor": True,
            "verbose": 2,
            "testing_int": 5,
            "testing_bar": 7.698,
            "testing_bool": False,
            "testing_arr": ["a", "b", "c"],
            "rules": ["LT03", "LT09"],
            "testing_inline_table": {"x": 1},
        },
        "bar": {"foo": "foobar"},
        "fnarr": {"fnarr": {"foo": "foobar"}},
        "rules": {"capitalisation.keywords": {"capitalisation_policy": "upper"}},
    }


def test__config__load_placeholder_cfg():
    """Test loading a sqlfluff configuration file for placeholder templater."""
    cfg = load_config_file(
        os.path.join("test", "fixtures", "config", "placeholder"),
        ".sqlfluff-placeholder",
    )
    assert cfg == {
        "core": {
            "testing_val": "foobar",
            "testing_int": 4,
        },
        "bar": {"foo": "barbar"},
        "templater": {
            "placeholder": {
                "param_style": "flyway_var",
                "flyway:database": "test_db",
            }
        },
    }


@patch("os.path.exists")
@patch("os.listdir")
@pytest.mark.skipif(sys.platform == "win32", reason="Not applicable on Windows")
def test__config__load_user_appdir_config(
    mock_listdir, mock_path_exists, mock_xdg_home
):
    """Test loading config from user appdir."""
    xdg_home = os.environ.get("XDG_CONFIG_HOME")
    assert xdg_home, "XDG HOME should be set by the mock. Something has gone wrong."
    xdg_config_path = xdg_home + "/sqlfluff"

    def path_exists(x):
        if x == os.path.expanduser("~/.config/sqlfluff"):
            return False
        if x == xdg_config_path:
            return False
        else:
            return True

    mock_path_exists.side_effect = path_exists

    with patch.object(appdirs, attribute="system", new="darwin"):
        resolved_path = _get_user_config_dir_path()
        _load_user_appdir_config()
    assert resolved_path == os.path.expanduser("~/Library/Application Support/sqlfluff")

    mock_path_exists.assert_has_calls(
        [
            call(xdg_config_path),
            call(os.path.expanduser("~/Library/Application Support/sqlfluff")),
        ]
    )


def test__config__validate_configs_direct():
    """Test _validate_configs method of ConfigLoader directly."""
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


def test__config__validate_configs_precedence_same_file():
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


def test__config__toml_list_config():
    """Test Parsing TOML list of values."""
    loaded_config = load_config_file(
        os.path.join("test", "fixtures", "config", "toml"),
        "pyproject.toml",
    )
    loaded_config["core"]["dialect"] = "ansi"
    cfg = FluffConfig(loaded_config)

    # Verify we can later retrieve the config values.
    assert cfg.get("dialect") == "ansi"
    assert cfg.get("rules") == ["LT03", "LT09"]
