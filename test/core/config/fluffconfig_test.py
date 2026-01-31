"""Tests for the configuration routines."""

import logging
import os

import pytest

import sqlfluff
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.templaters import (
    JinjaTemplater,
    PlaceholderTemplater,
    PythonTemplater,
    RawTemplater,
)
from sqlfluff.utils.testing.logging import fluff_log_catcher

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
    violations = lnt.check_tuples_by_path()
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


@pytest.mark.parametrize(
    "templater_name,templater_class,raises_error",
    [
        ("raw", RawTemplater, False),
        ("jinja", JinjaTemplater, False),
        ("python", PythonTemplater, False),
        ("placeholder", PlaceholderTemplater, False),
        ("afefhlsakufe", None, True),
        ("", None, True),
    ],
)
def test__config__templater_selection(templater_name, templater_class, raises_error):
    """Test template selection by name."""
    if raises_error:
        with pytest.raises(SQLFluffUserError):
            FluffConfig(overrides={"dialect": "ansi", "templater": templater_name})
    else:
        cfg = FluffConfig(overrides={"dialect": "ansi", "templater": templater_name})
        assert cfg.get_templater().__class__ is templater_class
        assert cfg._configs["core"]["templater_obj"].__class__ is templater_class


def test__config__glob_exclude_config_tests():
    """Test linting with a glob pattern in exclude_rules.

    This looks like a linter test but it's actually a config
    test.
    """
    lntr = Linter(config=FluffConfig.from_path("test/fixtures/config/glob_exclude"))
    lnt = lntr.lint_path("test/fixtures/config/glob_exclude/test.sql")
    violations = lnt.check_tuples_by_path()
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
    violations = lnt.check_tuples_by_path()
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
    violations = lnt.check_tuples_by_path()
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
    violations = lnt.check_tuples_by_path()
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
            "-- sqlfluff:layout:types:comma:line_position:leading\nSELECT 1"
        ),
        (
            # Unsupported layout config length
            "-- sqlfluff:layout:foo:bar\nSELECT 1"
        ),
        (
            # Unsupported layout config length
            "-- sqlfluff:layout:type:comma:bar\nSELECT 1"
        ),
        (
            # Unsupported layout config key ("foo")
            "-- sqlfluff:layout:type:comma:foo:bar\nSELECT 1"
        ),
        (
            # Unsupported layout config key ("foo") [no space]
            "--sqlfluff:layout:type:comma:foo:bar\nSELECT 1"
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

    # Check that JSON objects are not mangled
    cfg.process_inline_config('-- sqlfluff:jinja:my_dict:{"k":"v"}', "test.sql")
    assert cfg.get("my_dict", section="jinja") == '{"k":"v"}'

    # Check that JSON arrays are not mangled
    cfg.process_inline_config('-- sqlfluff:jinja:my_dict:[{"k":"v"}]', "test.sql")
    assert cfg.get("my_dict", section="jinja") == '[{"k":"v"}]'


@pytest.mark.parametrize(
    "raw_sql",
    [
        (
            "-- sqlfluff:max_line_length:25\n"
            "-- sqlfluff:rules:LT05,LT06\n"
            "-- sqlfluff:exclude_rules:LT01,LT02\n"
            "SELECT 1"
        )
    ],
)
def test__process_raw_file_for_config(raw_sql):
    """Test the processing of a file inline directives."""
    cfg = FluffConfig(config_b)

    # verify initial attributes based on the preloaded configuration
    assert cfg.get("max_line_length") == 80
    assert cfg.get("rules") == "LT03"
    assert cfg.get("exclude_rules") is None

    # internal list attributes should have corresponding exploded list values
    assert cfg.get("rule_allowlist") == ["LT03"]
    assert cfg.get("rule_denylist") == []

    cfg.process_raw_file_for_config(raw_sql, "test.sql")

    # verify overrides based on the file inline directives
    assert cfg.get("max_line_length") == 25
    assert cfg.get("rules") == "LT05,LT06"
    assert cfg.get("exclude_rules") == "LT01,LT02"

    # internal list attributes should have overridden exploded list values
    assert cfg.get("rule_allowlist") == ["LT05", "LT06"]
    assert cfg.get("rule_denylist") == ["LT01", "LT02"]


def test__api__immutable_config():
    """Tests that a config is not mutated when parsing."""
    config = FluffConfig.from_path(
        "test/fixtures/api/config_path_test/extra_configs/.sqlfluff"
    )
    assert config.get("dialect") == "ansi"
    sqlfluff.parse(
        "-- sqlfluff:dialect: postgres\nSELECT * FROM table1\n", config=config
    )
    assert config.get("dialect") == "ansi"


def test__config__comma_separated_path_keys_glob_support(tmp_path):
    """Test that comma-separated path keys support glob patterns."""
    # Set up test directory structure
    macros_dir = tmp_path / "macros"
    macros_dir.mkdir()
    (macros_dir / "macro1.sql").touch()
    (macros_dir / "macro2.sql").touch()
    (macros_dir / "other.txt").touch()

    subdir = macros_dir / "subdirectory"
    subdir.mkdir()
    (subdir / "macro3.sql").touch()

    # Create config file with glob patterns
    config_file = tmp_path / ".sqlfluff"
    config_file.write_text(
        "[sqlfluff]\n"
        "dialect = ansi\n"
        "[sqlfluff:templater:jinja]\n"
        "load_macros_from_path = macros/*.sql, macros/subdirectory/*.sql\n"
        "loader_search_path = macros/*\n"
    )

    # Load config and verify glob expansion
    config = FluffConfig.from_path(str(config_file))

    # Check that globs are expanded to actual file paths
    load_macros_from_path = config.get(
        "load_macros_from_path", section="templater:jinja"
    )
    loader_search_path = config.get("loader_search_path", section="templater:jinja")

    # load_macros_from_path should contain the expanded paths
    expanded_macros = load_macros_from_path.split(",")
    expanded_macros = [path.strip() for path in expanded_macros]

    # Should match the SQL files but not other.txt
    assert len(expanded_macros) == 3
    assert any("macro1.sql" in path for path in expanded_macros)
    assert any("macro2.sql" in path for path in expanded_macros)
    assert any("macro3.sql" in path for path in expanded_macros)
    assert not any("other.txt" in path for path in expanded_macros)

    # loader_search_path should contain expanded directories and files
    expanded_search = loader_search_path.split(",")
    expanded_search = [path.strip() for path in expanded_search]

    # Should match all files in macros directory
    assert len(expanded_search) == 4  # 3 files + 1 subdirectory
    assert any("macro1.sql" in path for path in expanded_search)
    assert any("macro2.sql" in path for path in expanded_search)
    assert any("other.txt" in path for path in expanded_search)
    assert any("subdirectory" in path for path in expanded_search)


def test__config__comma_separated_path_keys_exact_match(tmp_path):
    """Test that comma-separated path keys still work with exact file matches."""
    # Set up test directory structure
    macros_dir = tmp_path / "macros"
    macros_dir.mkdir()
    specific_file = macros_dir / "specific_macro.sql"
    specific_file.touch()

    # Create config file with exact file path
    config_file = tmp_path / ".sqlfluff"
    config_file.write_text(
        "[sqlfluff]\n"
        "dialect = ansi\n"
        "[sqlfluff:templater:jinja]\n"
        "load_macros_from_path = macros/specific_macro.sql\n"
    )

    # Load config and verify exact path resolution
    config = FluffConfig.from_path(str(config_file))

    load_macros_from_path = config.get(
        "load_macros_from_path", section="templater:jinja"
    )

    # Should contain exactly one path - the resolved specific file
    assert "specific_macro.sql" in load_macros_from_path
    # Should not be comma-separated since only one match
    assert "," not in load_macros_from_path


def test__config__comma_separated_path_keys_no_matches(tmp_path):
    """Test behavior when glob patterns don't match any files."""
    # Set up test directory with no matching files
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    # Create config file with pattern that won't match anything
    config_file = tmp_path / ".sqlfluff"
    config_file.write_text(
        "[sqlfluff]\n"
        "dialect = ansi\n"
        "[sqlfluff:templater:jinja]\n"
        "load_macros_from_path = empty/*.sql, nonexistent/*.sql\n"
    )

    # Load config and verify empty result handling
    config = FluffConfig.from_path(str(config_file))

    load_macros_from_path = config.get(
        "load_macros_from_path", section="templater:jinja"
    )

    # Should be empty since no files match the glob patterns
    assert load_macros_from_path == ""
