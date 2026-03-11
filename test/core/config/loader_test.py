"""Tests for the configuration routines."""

import os
import re
import sys
from contextlib import contextmanager
from unittest.mock import call, patch

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.config import (
    clear_config_caches,
    load_config_at_path,
    load_config_file,
    load_config_string,
    load_config_up_to_path,
)
from sqlfluff.core.config.loader import (
    _get_user_config_dir_path,
    _load_user_appdir_config,
)
from sqlfluff.core.config.toml import _format_toml_parse_error
from sqlfluff.core.errors import SQLFluffUserError

# tomllib is only in the stdlib from 3.11+
if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

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


def test__config__load_file_missing_extra():
    """Test loading config from a file path if extra path is not found."""
    with pytest.raises(SQLFluffUserError):
        load_config_up_to_path(
            os.path.join("test", "fixtures", "config", "inheritance_a", "testing.sql"),
            extra_config_path="non/existent/path",
        )


def test__config__load_nested():
    """Test nested overwrite and order of precedence of config files."""
    cfg = load_config_up_to_path(
        os.path.join(
            "test", "fixtures", "config", "inheritance_a", "nested", "blah.sql"
        ),
        extra_config_path=os.path.join(
            "test",
            "fixtures",
            "config",
            "inheritance_a",
            "extra",
            "this_can_have_any_name.cfg",
        ),
    )
    assert cfg == {
        "core": {
            # Outer .sqlfluff defines dialect & testing_val and not overridden.
            "dialect": "mysql",
            "testing_val": "foobar",
            # tesing_int is defined in many. Inner pyproject.toml takes precedence.
            "testing_int": 1,
            # testing_bar is defined only in setup.cfg
            "testing_bar": 7.698,
        },
        # bar is defined in a few, but the extra_config takes precedence.
        "bar": {"foo": "foobarextra"},
        # fnarr is defined in a few. Inner tox.ini takes precedence.
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
@pytest.mark.parametrize(
    "sys_platform,xdg_exists,default_exists,resolved_config_path,paths_checked",
    [
        # On linux, if the default path exists, it should be the only path we check
        # and the chosen config path.
        ("linux", True, True, "~/.config/sqlfluff", ["~/.config/sqlfluff"]),
        # On linux, if the default path doesn't exist, then (because for this
        # test case we set XDG_CONFIG_HOME) it will check the default path
        # but then on finding it to not exist it will then try the XDG path.
        # In this case, neither actually exist and so what matters is that both
        # are either checked or used - rather than one in particular being the
        # end result.
        (
            "linux",
            False,
            False,
            "~/.config/my/special/path/sqlfluff",
            ["~/.config/sqlfluff"],
        ),
        # On MacOS, if the default config path and the XDG path don't exist, then
        # we should resolve config to the default MacOS config path.
        (
            "darwin",
            False,
            False,
            "~/Library/Application Support/sqlfluff",
            ["~/.config/sqlfluff", "~/.config/my/special/path/sqlfluff"],
        ),
        # However, if XDG_CONFIG_HOME is set, and the path exists then that should
        # be resolved _ahead of_ the default MacOS config path (as demonstrated
        # by us not checking the presence of that path in the process).
        # https://github.com/sqlfluff/sqlfluff/issues/889
        (
            "darwin",
            True,
            False,
            "~/.config/my/special/path/sqlfluff",
            ["~/.config/sqlfluff", "~/.config/my/special/path/sqlfluff"],
        ),
    ],
)
def test__config__get_user_config_dir_path(
    mock_listdir,
    mock_path_exists,
    mock_xdg_home,
    sys_platform,
    xdg_exists,
    default_exists,
    resolved_config_path,
    paths_checked,
):
    """Test loading config from user appdir."""
    xdg_home = os.environ.get("XDG_CONFIG_HOME")
    assert xdg_home, "XDG HOME should be set by the mock. Something has gone wrong."
    xdg_config_path = xdg_home + "/sqlfluff"

    def path_exists(check_path):
        """Patch for os.path.exists which depends on test parameters.

        Returns:
            True, unless `default_exists` is `False` and the path passed to
            the function is the default config path, or unless `xdg_exists`
            is `False` and the path passed is the XDG config path.
        """
        resolved_path = os.path.expanduser(check_path)
        if (
            resolved_path == os.path.expanduser("~/.config/sqlfluff")
            and not default_exists
        ):
            return False
        if resolved_path == os.path.expanduser(xdg_config_path) and not xdg_exists:
            return False
        return True

    mock_path_exists.side_effect = path_exists

    # Get the config path as though we are on macOS.
    resolved_path = _get_user_config_dir_path(sys_platform)
    assert os.path.expanduser(resolved_path) == os.path.expanduser(resolved_config_path)
    mock_path_exists.assert_has_calls(
        [call(os.path.expanduser(path)) for path in paths_checked]
    )


@patch("os.path.exists")
@patch("sqlfluff.core.config.loader.load_config_at_path")
def test__config__load_user_appdir_config(mock_load_config, mock_path_exists):
    """Test _load_user_appdir_config.

    NOTE: We mock `load_config_at_path()` so we can be really focussed with this test
    and also not need to actually interact with local home directories.
    """
    mock_load_config.side_effect = lambda x: {}
    mock_path_exists.side_effect = lambda x: True
    _load_user_appdir_config()
    # It will check that the default config path exists...
    mock_path_exists.assert_has_calls([call(os.path.expanduser("~/.config/sqlfluff"))])
    # ...and assuming it does, it will try and load config files at that path.
    mock_load_config.assert_has_calls([call(os.path.expanduser("~/.config/sqlfluff"))])


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


def test__config__load_toml_invalid_syntax(tmp_path):
    """Invalid TOML should raise a SQLFluff user error with location info."""
    pyproject_path = tmp_path / "pyproject.toml"
    invalid_toml = '[tool.sqlfluff.core]\ndialect = "ansi"\nrules = [1,,2]\n'
    pyproject_path.write_text(invalid_toml, encoding="utf-8")

    try:
        with pytest.raises(SQLFluffUserError) as exc_info:
            load_config_file(str(tmp_path), "pyproject.toml")
    finally:
        clear_config_caches()
        pyproject_path.unlink(missing_ok=True)

    try:
        tomllib.loads(invalid_toml)
    except tomllib.TOMLDecodeError as err:
        expected_line = getattr(err, "lineno", None)
        expected_column = getattr(err, "colno", None)
        if expected_line is None or expected_column is None:
            location_match = re.search(
                r"at line (?P<line>\d+), column (?P<column>\d+)",
                str(err),
            )
            if location_match:
                expected_line = int(location_match.group("line"))
                expected_column = int(location_match.group("column"))
    else:  # pragma: no cover
        raise AssertionError("Expected invalid TOML to fail parsing.")

    assert expected_line is not None
    assert expected_column is not None

    message = str(exc_info.value)
    assert str(pyproject_path).replace("\\", "/") in message.replace("\\", "/")
    assert "Failed to parse TOML config file" in message
    assert "Invalid" in message
    assert f"line {expected_line}" in message
    assert f"column {expected_column}" in message
    assert "UTF-8 BOM" not in message


def test__config__load_toml_utf8_bom_hint(tmp_path):
    """A UTF-8 BOM should surface a targeted configuration hint."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(
        '\ufeff[tool.sqlfluff.core]\ndialect = "ansi"\n',
        encoding="utf-8",
    )

    try:
        with pytest.raises(SQLFluffUserError) as exc_info:
            load_config_file(str(tmp_path), "pyproject.toml")
    finally:
        clear_config_caches()
        pyproject_path.unlink(missing_ok=True)

    message = str(exc_info.value)
    assert str(pyproject_path).replace("\\", "/") in message.replace("\\", "/")
    assert "UTF-8 BOM" in message
    assert "UTF-8 without BOM" in message
    assert "line 1" in message
    assert "column 1" in message


def test__config__format_toml_parse_error_regex_location() -> None:
    """Regex fallback should extract location from the raw decode message."""

    class _DummyTomlError(Exception):
        def __str__(self) -> str:
            return "Invalid value (at line 3, column 12)"

    message = _format_toml_parse_error(
        "pyproject.toml",
        "[tool.sqlfluff.core]\nrules=[1,,2]\n",
        _DummyTomlError(),  # type: ignore[arg-type]
    )
    assert "Invalid value" in message
    assert "line 3" in message
    assert "column 12" in message


def test__config__format_toml_parse_error_line_only_location() -> None:
    """Line-only location should still be included in parse error output."""

    class _DummyTomlError(Exception):
        msg = "Invalid value"
        lineno = 7
        colno = None

        def __str__(self) -> str:
            return self.msg

    message = _format_toml_parse_error(
        "pyproject.toml",
        "[tool.sqlfluff.core]\n",
        _DummyTomlError(),  # type: ignore[arg-type]
    )
    assert "Invalid value" in message
    assert "line 7" in message
    assert "column" not in message
