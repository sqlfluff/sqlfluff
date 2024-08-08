"""Tests for the configuration routines."""

import logging
import os
import sys
from contextlib import contextmanager
from unittest.mock import call, patch

import appdirs
import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.config import (
    REMOVED_CONFIGS,
    ConfigLoader,
)
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.templaters import (
    JinjaTemplater,
    PlaceholderTemplater,
    PythonTemplater,
    RawTemplater,
)
from sqlfluff.utils.testing.logging import fluff_log_catcher

config_a = {
    "core": {"testing_val": "foobar", "testing_int": 4, "dialect": "mysql"},
    "bar": {"foo": "barbar"},
}

config_b = {
    "core": {"rules": "LT03", "dialect": "ansi"},
    "layout": {
        "type": {"comma": {"line_position": "trailing", "spacing_before": "touch"}}
    },
}

config_c = {
    "core": {"rules": "LT03", "dialect": "ansi"},
    # NOTE:
    # - NOT_A_RULE doesn't match anything.
    # - L001 is an alias, but no longer a rule.
    # - layout is a group and but doesn't match any individual rule.
    "rules": {
        "NOT_A_RULE": {"foo": "bar"},
        "L001": {"foo": "bar"},
        "layout": {"foo": "bar"},
    },
}


@pytest.fixture
def mock_xdg_home(monkeypatch):
    """Sets the XDG_CONFIG_HOME variable."""
    monkeypatch.setenv("XDG_CONFIG_HOME", "~/.config/my/special/path")


def test__config__load_file_dir():
    """Test loading config from a directory path."""
    c = ConfigLoader()
    cfg = c.load_config_at_path(
        os.path.join("test", "fixtures", "config", "inheritance_a")
    )
    assert cfg == config_a


def test__config__load_from_string():
    """Test loading config from a string."""
    c = ConfigLoader()
    # Load a string
    with open(
        os.path.join("test", "fixtures", "config", "inheritance_a", ".sqlfluff")
    ) as f:
        config_string = f.read()
    cfg = c.load_config_string(config_string)
    assert cfg == config_a


def test__config__from_strings():
    """Test loading config from multiple strings."""
    strings = [
        "[sqlfluff]\ndialect=mysql\ntesting_val=foobar",
        "[sqlfluff]\ndialect=postgres\ntesting_val2=bar",
        "[sqlfluff]\ndialect=mysql\ntesting_val=foo",
    ]
    cfg = FluffConfig.from_strings(*strings)
    assert cfg.get("dialect") == "mysql"
    assert cfg.get("testing_val2") == "bar"
    assert cfg.get("testing_val") == "foo"


def test__config__load_file_f():
    """Test loading config from a file path."""
    c = ConfigLoader()
    cfg = c.load_config_at_path(
        os.path.join("test", "fixtures", "config", "inheritance_a", "testing.sql")
    )
    assert cfg == config_a


def test__config__load_nested():
    """Test nested overwrite and order of precedence of config files."""
    c = ConfigLoader()
    cfg = c.load_config_up_to_path(
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
    c = ConfigLoader()
    with change_dir(
        os.path.join("test", "fixtures", "config", "inheritance_a", "nested")
    ):
        cfg = c.load_config_up_to_path("blah.sql")
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


def test__config__iter_config_elems_from_dict():
    """Test nested overwrite and order of precedence of config files."""
    c = ConfigLoader._iter_config_elems_from_dict(
        {"a": {"b": {"c": 123, "d": 456}, "f": 6}}
    )
    assert list(c) == [
        (("a", "b", "c"), 123),
        (("a", "b", "d"), 456),
        (("a", "f"), 6),
    ]


def test__config__load_toml():
    """Test loading config from a pyproject.toml file."""
    c = ConfigLoader()
    cfg = c.load_config_file(
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
    c = ConfigLoader()
    cfg = c.load_config_file(
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


def test__config__find_sqlfluffignore_in_same_directory():
    """Test find ignore file in the same directory as sql file."""
    ignore_files = ConfigLoader.find_ignore_config_files(
        path="test/fixtures/linter/sqlfluffignore/path_b/query_b.sql",
        working_path="test/fixtures/linter/sqlfluffignore/",
    )
    assert ignore_files == {
        os.path.abspath("test/fixtures/linter/sqlfluffignore/path_b/.sqlfluffignore"),
        os.path.abspath("test/fixtures/linter/sqlfluffignore/.sqlfluffignore"),
    }


def test__config__nested_config_tests():
    """Test linting with overridden config in nested paths.

    This looks like a linter test but it's actually a config
    test.
    """
    lntr = Linter(
        # Exclude CP02 in overrides (similar to cli --exclude-rules)
        config=FluffConfig(overrides=dict(exclude_rules="CP02", dialect="ansi"))
    )
    lnt = lntr.lint_path("test/fixtures/config/inheritance_b")
    violations = lnt.check_tuples(by_path=True)
    for k in violations:
        if k.endswith("nested\\example.sql"):
            # CP01 is enabled in the .sqlfluff file and not excluded.
            assert ("CP01", 1, 4) in violations[k]
            # LT02 is enabled in the .sqlfluff file and not excluded.
            assert ("LT02", 1, 1) in violations[k]
            # CP02 is enabled in the .sqlfluff file but excluded by the
            # override above.
            assert "CP02" not in [c[0] for c in violations[k]]
        elif k.endswith("inheritance_b\\example.sql"):
            # CP01 is enabled because while disabled in the tox.ini file,
            # the exclude-rules option is overridden by the override above
            # which effectively sets the exclude to CP02 and in effect
            # re-enables CP01.
            # This may seem counter-intuitive but is in line with current
            # documentation on how to use `rules` and `exclude-rules`.
            # https://docs.sqlfluff.com/en/latest/perma/rule_disabling.html
            assert ("CP01", 1, 4) in violations[k]
            # CP02 is disabled because of the override above.
            assert "CP02" not in [c[0] for c in violations[k]]
            # LT02 is disabled because it is not in the `rules` of tox.ini
            assert "LT02" not in [c[0] for c in violations[k]]


@patch("os.path.exists")
@patch("os.listdir")
@pytest.mark.skipif(sys.platform == "win32", reason="Not applicable on Windows")
def test__config__load_user_appdir_config(
    mock_listdir, mock_path_exists, mock_xdg_home
):
    """Test loading config from user appdir."""
    xdg_config_path = os.environ.get("XDG_CONFIG_HOME") + "/sqlfluff"

    def path_exists(x):
        if x == os.path.expanduser("~/.config/sqlfluff"):
            return False
        if x == xdg_config_path:
            return False
        else:
            return True

    mock_path_exists.side_effect = path_exists

    c = ConfigLoader()

    with patch.object(appdirs, attribute="system", new="darwin"):
        resolved_path = c._get_user_config_dir_path()
        c.load_user_appdir_config()
    assert resolved_path == os.path.expanduser("~/Library/Application Support/sqlfluff")

    mock_path_exists.assert_has_calls(
        [
            call(xdg_config_path),
            call(os.path.expanduser("~/Library/Application Support/sqlfluff")),
        ]
    )


def test__config__templater_selection():
    """Test template selection by name."""
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    assert cfg.get_templater().__class__ is JinjaTemplater
    assert cfg.get_templater("raw").__class__ is RawTemplater
    assert cfg.get_templater("python").__class__ is PythonTemplater
    assert cfg.get_templater("jinja").__class__ is JinjaTemplater
    assert cfg.get_templater("placeholder").__class__ is PlaceholderTemplater

    with pytest.raises(ValueError):
        cfg.get_templater("afefhlsakufe")


def test__config__glob_exclude_config_tests():
    """Test linting with a glob pattern in exclude_rules.

    This looks like a linter test but it's actually a config
    test.
    """
    lntr = Linter(config=FluffConfig.from_path("test/fixtures/config/glob_exclude"))
    lnt = lntr.lint_path("test/fixtures/config/glob_exclude/test.sql")
    violations = lnt.check_tuples(by_path=True)
    for k in violations:
        assert ("AM04", 12, 1) in violations[k]
        assert "RF02" not in [c[0] for c in violations[k]]
        assert "LT13" not in [c[0] for c in violations[k]]
        assert "AM05" not in [c[0] for c in violations[k]]
        assert "CV06" not in [c[0] for c in violations[k]]


def test__config__glob_include_config_tests():
    """Test linting with a glob pattern in rules.

    This looks like a linter test but it's actually a config
    test.
    """
    lntr = Linter(config=FluffConfig.from_path("test/fixtures/config/glob_include"))
    lnt = lntr.lint_path("test/fixtures/config/glob_include/test.sql")
    violations = lnt.check_tuples(by_path=True)
    for k in violations:
        assert ("LT13", 1, 1) in violations[k]
        assert ("AM05", 14, 1) in violations[k]
        assert ("CV06", 14, 9) in violations[k]
        assert ("RF02", 12, 8) in violations[k]
        assert "AM04" not in [c[0] for c in violations[k]]


def test__config__rules_set_to_none():
    """Test linting when rules are set to 'None'.

    Ensure that all rules are still run.
    """
    lntr = Linter(
        config=FluffConfig.from_path("test/fixtures/config/rules_set_to_none")
    )
    lnt = lntr.lint_path("test/fixtures/config/rules_set_to_none/test.sql")
    violations = lnt.check_tuples(by_path=True)
    for k in violations:
        assert ("LT13", 1, 1) in violations[k]
        assert ("AM04", 12, 1) in violations[k]
        assert ("CP01", 12, 10) in violations[k]


def test__config__rules_group_with_exclude():
    """Test linting when a rules group is selected and rules are excluded."""
    lntr = Linter(
        config=FluffConfig.from_path("test/fixtures/config/rules_group_with_exclude")
    )
    lnt = lntr.lint_path("test/fixtures/config/rules_group_with_exclude/test.sql")
    violations = lnt.check_tuples(by_path=True)
    for k in violations:
        assert ("CP01", 15, 1) in violations[k]
        assert "LT04" not in [c[0] for c in violations[k]]


def test__config__get_section():
    """Test FluffConfig.get_section method."""
    cfg = FluffConfig(config_b)

    assert cfg.get_section("core").get("rules", None) == "LT03"
    assert cfg.get_section(["layout", "type", "comma"]) == {
        "line_position": "trailing",
        "spacing_before": "touch",
    }
    assert cfg.get_section("non_existent") is None


def test__config__get():
    """Test FluffConfig.get method."""
    cfg = FluffConfig(config_b)

    assert cfg.get("rules") == "LT03"
    assert cfg.get("rulez") is None
    assert cfg.get("rulez", section="core", default=123) == 123
    assert (
        cfg.get("line_position", section=["layout", "type", "comma"], default=None)
        == "trailing"
    )
    assert (
        cfg.get("line_position", section=["layout", "type", "ASDFSDG007"], default=None)
        is None
    )


def test__config__from_kwargs():
    """Test from_kwargs method of FluffConfig."""
    # Instantiate config object.
    cfg = FluffConfig.from_kwargs(
        dialect="snowflake",
        rules=["LT01", "LT02"],
        exclude_rules=["CP01", "AL01"],
    )

    # Verify we can later retrieve the config values.
    assert cfg.get("dialect") == "snowflake"
    assert cfg.get("rules") == "LT01,LT02"
    assert cfg.get("exclude_rules") == "CP01,AL01"


def test__config__from_string():
    """Test from_string method of FluffConfig."""
    with open(
        os.path.join("test", "fixtures", "config", "inheritance_a", ".sqlfluff")
    ) as f:
        config_string = f.read()
    cfg = FluffConfig.from_string(config_string)
    # Verify we can later retrieve the config values.
    assert cfg.get("testing_val") == "foobar"
    assert cfg.get("dialect") == "mysql"


def test__config_missing_dialect():
    """Verify an exception is thrown if no dialect was specified."""
    with pytest.raises(SQLFluffUserError) as e:
        FluffConfig.from_kwargs()
    assert "must configure a dialect" in str(e.value)


def test__config__validate_configs_direct():
    """Test _validate_configs method of ConfigLoader directly."""
    # Make sure there _are_ removed configs.
    assert REMOVED_CONFIGS
    # Make sure all raise an error if validated
    for k in REMOVED_CONFIGS:
        print(k)
        if k.translation_func and k.new_path:
            res = ConfigLoader._validate_configs([(k.old_path, "foo")], "<test>")
            print(res)
            # Check that it's reassigned.
            assert not any(elem[0] == k.old_path for elem in res)
            assert any(elem[0] == k.new_path for elem in res)
            # Really we should check that it's output here, but logging config
            # seems to make that hard.
        else:
            with pytest.raises(SQLFluffUserError) as excinfo:
                ConfigLoader._validate_configs([(k.old_path, "foo")], "<test>")
            assert "set an outdated config" in str(excinfo.value)
            assert k.warning in str(excinfo.value)


def test__config__validate_configs_indirect():
    """Test _validate_configs method of FluffConfig indirectly."""
    # Instantiate config object.
    with pytest.raises(SQLFluffUserError):
        FluffConfig(
            configs={
                "core": {"dialect": "ansi"},
                # This is a known removed value.
                "rules": {"L003": {"lint_templated_tokens": True}},
            }
        )


@pytest.mark.parametrize(
    "raw_sql",
    [
        (
            # "types" not "type"
            "-- sqlfluff:layout:types:comma:line_position:leading\n"
            "SELECT 1"
        ),
        (
            # Unsupported layout config length
            "-- sqlfluff:layout:foo\n"
            "SELECT 1"
        ),
        (
            # Unsupported layout config length
            "-- sqlfluff:layout:type:comma:bar\n"
            "SELECT 1"
        ),
        (
            # Unsupported layout config key ("foo")
            "-- sqlfluff:layout:type:comma:foo:bar\n"
            "SELECT 1"
        ),
        (
            # Unsupported layout config key ("foo") [no space]
            "--sqlfluff:layout:type:comma:foo:bar\n"
            "SELECT 1"
        ),
    ],
)
def test__config__validate_configs_inline_layout(raw_sql):
    """Test _validate_configs method of FluffConfig when used on a file.

    This test covers both the validation of inline config
    directives but also the validation of layout configs.
    """
    # Instantiate config object.
    cfg = FluffConfig(configs={"core": {"dialect": "ansi"}})

    # Try to process an invalid inline config. Make sure we get an error.
    with pytest.raises(SQLFluffUserError):
        cfg.process_raw_file_for_config(raw_sql, "test.sql")


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
    test_config = [(new_key, "foo"), (old_key, "foo")]
    assert len(test_config) == 2
    res = ConfigLoader._validate_configs(test_config, "<test>")
    assert len(res) == 1
    # Check that the old key isn't there.
    assert not any(k == old_key for k, _ in res)


def test__config__toml_list_config():
    """Test Parsing TOML list of values."""
    c = ConfigLoader()
    loaded_config = c.load_config_file(
        os.path.join("test", "fixtures", "config", "toml"),
        "pyproject.toml",
    )
    loaded_config["core"]["dialect"] = "ansi"
    cfg = FluffConfig(loaded_config)

    # Verify we can later retrieve the config values.
    assert cfg.get("dialect") == "ansi"
    assert cfg.get("rules") == ["LT03", "LT09"]


def test__config__warn_unknown_rule():
    """Test warnings when rules are unknown."""
    lntr = Linter(config=FluffConfig(config_c))

    with fluff_log_catcher(logging.WARNING, "sqlfluff.rules") as caplog:
        lntr.get_rulepack()

    # Check we get a warning on the unrecognised rule.
    assert (
        "Rule configuration contain a section for unexpected rule 'NOT_A_RULE'."
    ) in caplog.text
    # Check we get a warning for the deprecated rule.
    assert (
        "Rule configuration contain a section for unexpected rule 'L001'."
    ) in caplog.text
    # Check we get a hint for the matched rule.
    assert "match for rule LT01 with name 'layout.spacing'" in caplog.text
    # Check we get a warning for the group name.
    assert (
        "Rule configuration contain a section for unexpected rule 'layout'."
    ) in caplog.text
    # Check we get a hint for the matched rule group.
    # NOTE: We don't check the set explicitly because we can't assume ordering.
    assert ("The reference was found as a match for multiple rules: {") in caplog.text
    assert ("LT01") in caplog.text
    assert ("LT02") in caplog.text


def test__process_inline_config():
    """Test the processing of inline in-file configuration directives."""
    cfg = FluffConfig(config_b)
    assert cfg.get("rules") == "LT03"

    cfg.process_inline_config("-- sqlfluff:rules:LT02", "test.sql")
    assert cfg.get("rules") == "LT02"

    assert cfg.get("tab_space_size", section="indentation") == 4
    cfg.process_inline_config("-- sqlfluff:indentation:tab_space_size:20", "test.sql")
    assert cfg.get("tab_space_size", section="indentation") == 20

    assert cfg.get("dialect") == "ansi"
    assert cfg.get("dialect_obj").name == "ansi"
    cfg.process_inline_config("-- sqlfluff:dialect:postgres", "test.sql")
    assert cfg.get("dialect") == "postgres"
    assert cfg.get("dialect_obj").name == "postgres"

    assert cfg.get("rulez") is None
    cfg.process_inline_config("-- sqlfluff:rulez:LT06", "test.sql")
    assert cfg.get("rulez") == "LT06"

    # Check that Windows paths don't get mangled
    cfg.process_inline_config("-- sqlfluff:jinja:my_path:c:\\foo", "test.sql")
    assert cfg.get("my_path", section="jinja") == "c:\\foo"
