"""Tests for the configuration routines."""

import os
import sys
from contextlib import contextmanager
from unittest.mock import call, patch

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

    # Get the config path as though we are on macOS.
    resolved_path = _get_user_config_dir_path("darwin")
    # Because we're mocking the path_exists function to say the XDG
    # config path doesn't exist, we expect the resolved path to be the
    # macOS specific default one.
    assert resolved_path == os.path.expanduser("~/Library/Application Support/sqlfluff")
    # At this stage, the function should have checked the default sqlfluff
    # config path and the XDG config path to see if either of them exist first.
    mock_path_exists.assert_has_calls(
        [
            call(os.path.expanduser("~/.config/sqlfluff")),
            call(xdg_config_path),
        ]
    )
    # Making a call to load the appdir config should trigger a check of the
    # default config path, the XDG config path and the macOS specific one.
    mock_path_exists.reset_mock()
    _load_user_appdir_config()
    mock_path_exists.assert_has_calls(
        [
            call(os.path.expanduser("~/.config/sqlfluff")),
            call(xdg_config_path),
            call(os.path.expanduser("~/Library/Application Support/sqlfluff")),
        ]
    )


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
