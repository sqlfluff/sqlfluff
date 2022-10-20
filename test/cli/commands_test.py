"""The Test file for CLI (General)."""

import configparser
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import logging
from unittest.mock import MagicMock, patch

import chardet

# Testing libraries
import pytest
import yaml
from click.testing import CliRunner

# We import the library directly here to get the version
import sqlfluff
from sqlfluff.cli.commands import (
    lint,
    version,
    rules,
    fix,
    parse,
    dialects,
    get_config,
)
from sqlfluff.core.rules import BaseRule, LintFix, LintResult
from sqlfluff.core.parser.segments.raw import CommentSegment
from sqlfluff.utils.testing.cli import invoke_assert_code

re_ansi_escape = re.compile(r"\x1b[^m]*m")


@pytest.fixture(autouse=True)
def logging_cleanup():
    """This gracefully handles logging issues at session teardown.

    Removes handlers from all loggers. Autouse applies this to all
    tests in this file (i.e. all the cli command tests), which should
    be all of the test cases where `set_logging_level` is called.

    https://github.com/sqlfluff/sqlfluff/issues/3702
    https://github.com/pytest-dev/pytest/issues/5502#issuecomment-1190557648
    """
    yield
    # NOTE: This is a teardown function so the clearup code
    # comes _after_ the yield.
    # Get only the sqlfluff loggers (which we set in set_logging_level)
    loggers = [
        logger
        for logger in logging.Logger.manager.loggerDict.values()
        if isinstance(logger, logging.Logger) and logger.name.startswith("sqlfluff")
    ]
    for logger in loggers:
        if not hasattr(logger, "handlers"):
            continue
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)


def contains_ansi_escape(s: str) -> bool:
    """Does the string contain ANSI escape codes (e.g. color)?"""
    return re_ansi_escape.search(s) is not None


expected_output = """== [test/fixtures/linter/indentation_error_simple.sql] FAIL
L:   2 | P:   4 | L003 | Expected 1 indentation, found less than 1 [compared to
                       | line 01]
L:   5 | P:  10 | L010 | Keywords must be consistently upper case.
L:   5 | P:  13 | L031 | Avoid aliases in from clauses and join conditions.
"""


def test__cli__command_directed():
    """Basic checking of lint functionality."""
    result = invoke_assert_code(
        ret_code=1,
        args=[
            lint,
            [
                "--disable-progress-bar",
                "test/fixtures/linter/indentation_error_simple.sql",
            ],
        ],
    )
    # We should get a readout of what the error was
    check_a = "L:   2 | P:   4 | L003"
    # NB: Skip the number at the end because it's configurable
    check_b = "ndentation"
    assert check_a in result.output
    assert check_b in result.output
    # Finally check the WHOLE output to make sure that unexpected newlines are not
    # added. The replace command just accounts for cross platform testing.
    assert result.output.replace("\\", "/").startswith(expected_output)


def test__cli__command_dialect():
    """Check the script raises the right exception on an unknown dialect."""
    # The dialect is unknown should be a non-zero exit code
    invoke_assert_code(
        ret_code=2,
        args=[
            lint,
            [
                "-n",
                "--dialect",
                "faslkjh",
                "test/fixtures/linter/indentation_error_simple.sql",
            ],
        ],
    )


def test__cli__command_no_dialect():
    """Check the script raises the right exception no dialect."""
    # The dialect is unknown should be a non-zero exit code
    result = invoke_assert_code(
        ret_code=2,
        args=[
            lint,
            ["-"],
        ],
        cli_input="SELECT 1",
    )
    assert "User Error" in result.stdout
    assert "No dialect was specified" in result.stdout


def test__cli__command_parse_error_dialect_explicit_warning():
    """Check parsing error raises the right warning."""
    # For any parsing error there should be a non-zero exit code
    # and a human-readable warning should be displayed.
    # Dialect specified as commandline option.
    result = invoke_assert_code(
        ret_code=1,
        args=[
            parse,
            [
                "-n",
                "--dialect",
                "postgres",
                "test/fixtures/cli/fail_many.sql",
            ],
        ],
    )
    assert (
        "WARNING: Parsing errors found and dialect is set to 'postgres'. "
        "Have you configured your dialect correctly?" in result.stdout
    )


def test__cli__command_parse_error_dialect_implicit_warning():
    """Check parsing error raises the right warning."""
    # For any parsing error there should be a non-zero exit code
    # and a human-readable warning should be displayed.
    # Dialect specified in .sqlfluff config.
    result = invoke_assert_code(
        ret_code=1,
        args=[
            # Config sets dialect to tsql
            parse,
            [
                "-n",
                "--config",
                "test/fixtures/cli/extra_configs/.sqlfluff",
                "test/fixtures/cli/fail_many.sql",
            ],
        ],
    )
    assert (
        "WARNING: Parsing errors found and dialect is set to 'tsql'. "
        "Have you configured your dialect correctly?" in result.stdout
    )


def test__cli__command_dialect_legacy():
    """Check the script raises the right exception on a legacy dialect."""
    result = invoke_assert_code(
        ret_code=2,
        args=[
            lint,
            [
                "-n",
                "--dialect",
                "exasol_fs",
                "test/fixtures/linter/indentation_error_simple.sql",
            ],
        ],
    )
    assert "Please use the 'exasol' dialect instead." in result.stdout


def test__cli__command_extra_config_fail():
    """Check the script raises the right exception non-existent extra config path."""
    result = invoke_assert_code(
        ret_code=2,
        args=[
            lint,
            [
                "--config",
                "test/fixtures/cli/extra_configs/.sqlfluffsdfdfdfsfd",
                "test/fixtures/cli/extra_config_tsql.sql",
            ],
        ],
    )
    assert (
        "Extra config 'test/fixtures/cli/extra_configs/.sqlfluffsdfdfdfsfd' does not "
        "exist." in result.stdout
    )


@pytest.mark.parametrize(
    "command",
    [
        (
            "-",
            "-n",
        ),
        (
            "-",
            "-n",
            "-v",
        ),
        (
            "-",
            "-n",
            "-vv",
        ),
        (
            "-",
            "-vv",
        ),
    ],
)
def test__cli__command_lint_stdin(command):
    """Check basic commands on a simple script using stdin.

    The subprocess command should exit without errors, as no issues should be found.
    """
    with open("test/fixtures/cli/passing_a.sql") as test_file:
        sql = test_file.read()
    invoke_assert_code(args=[lint, ("--dialect=ansi",) + command], cli_input=sql)


@pytest.mark.parametrize(
    "command",
    [
        # Test basic linting
        (
            lint,
            [
                "-n",
                "test/fixtures/cli/passing_b.sql",
                "--exclude-rules",
                "L051",
            ],
        ),
        # Original tests from test__cli__command_lint
        (lint, ["-n", "test/fixtures/cli/passing_a.sql"]),
        (lint, ["-n", "-v", "test/fixtures/cli/passing_a.sql"]),
        (lint, ["-n", "-vvvv", "test/fixtures/cli/passing_a.sql"]),
        (lint, ["-vvvv", "test/fixtures/cli/passing_a.sql"]),
        # Test basic linting with very high verbosity
        (
            lint,
            [
                "-n",
                "test/fixtures/cli/passing_b.sql",
                "-vvvvvvvvvvv",
                "--exclude-rules",
                "L051",
            ],
        ),
        # Test basic linting with specific logger.
        # Also test short rule exclusion.
        (
            lint,
            [
                "-n",
                "test/fixtures/cli/passing_b.sql",
                "-vvv",
                "--logger",
                "parser",
                "-e",
                "L051",
            ],
        ),
        # Check basic parsing
        (
            parse,
            [
                "-n",
                "test/fixtures/cli/passing_b.sql",
                "--exclude-rules",
                "L051",
            ],
        ),
        # Test basic parsing with very high verbosity
        (
            parse,
            [
                "-n",
                "test/fixtures/cli/passing_b.sql",
                "-vvvvvvvvvvv",
                "-e",
                "L051",
            ],
        ),
        # Check basic parsing, with the code only option
        (parse, ["-n", "test/fixtures/cli/passing_b.sql", "-c"]),
        # Check basic parsing, with the yaml output
        (parse, ["-n", "test/fixtures/cli/passing_b.sql", "-c", "-f", "yaml"]),
        (parse, ["-n", "test/fixtures/cli/passing_b.sql", "--format", "yaml"]),
        # Check the profiler and benching commands
        (parse, ["-n", "test/fixtures/cli/passing_b.sql", "--profiler"]),
        (parse, ["-n", "test/fixtures/cli/passing_b.sql", "--bench"]),
        (
            lint,
            [
                "-n",
                "test/fixtures/cli/passing_b.sql",
                "--bench",
                "--exclude-rules",
                "L051",
            ],
        ),
        (
            fix,
            [
                "-n",
                "test/fixtures/cli/passing_b.sql",
                "--bench",
                "--exclude-rules",
                "L051",
            ],
        ),
        # Check linting works in specifying rules
        (
            lint,
            [
                "-n",
                "--rules",
                "L001",
                "test/fixtures/linter/operator_errors.sql",
            ],
        ),
        # Check linting works in specifying multiple rules
        (
            lint,
            [
                "-n",
                "--rules",
                "L001,L002",
                "test/fixtures/linter/operator_errors.sql",
            ],
        ),
        # Check linting works with both included and excluded rules
        (
            lint,
            [
                "-n",
                "--rules",
                "L001,L006",
                "--exclude-rules",
                "L006,L031",
                "test/fixtures/linter/operator_errors.sql",
            ],
        ),
        # Check linting works with just excluded rules
        (
            lint,
            [
                "-n",
                "--exclude-rules",
                "L006,L007,L031,L039",
                "test/fixtures/linter/operator_errors.sql",
            ],
        ),
        # Check that ignoring works (also checks that unicode files parse).
        (
            lint,
            [
                "-n",
                "--exclude-rules",
                "L003,L009,L031",
                "--ignore",
                "parsing,lexing",
                "test/fixtures/linter/parse_lex_error.sql",
            ],
        ),
        # Check nofail works
        (lint, ["--nofail", "test/fixtures/linter/parse_lex_error.sql"]),
        # Check config works (sets dialect to tsql)
        (
            lint,
            [
                "--config",
                "test/fixtures/cli/extra_configs/.sqlfluff",
                "test/fixtures/cli/extra_config_tsql.sql",
            ],
        ),
        (
            lint,
            [
                "--config",
                "test/fixtures/cli/extra_configs/pyproject.toml",
                "test/fixtures/cli/extra_config_tsql.sql",
            ],
        ),
        # Check timing outputs doesn't raise exceptions
        (lint, ["test/fixtures/cli/passing_a.sql", "--persist-timing", "test.csv"]),
    ],
)
def test__cli__command_lint_parse(command):
    """Check basic commands on a more complicated script."""
    invoke_assert_code(args=command)


@pytest.mark.parametrize(
    "command, ret_code",
    [
        # Check the script doesn't raise an unexpected exception with badly formed
        # files.
        (
            (
                fix,
                [
                    "--rules",
                    "L001",
                    "test/fixtures/cli/fail_many.sql",
                    "-vvvvvvv",
                ],
                "y",
            ),
            1,
        ),
        # Fix with a suffixs
        (
            (
                fix,
                [
                    "--rules",
                    "L001",
                    "--fixed-suffix",
                    "_fix",
                    "test/fixtures/cli/fail_many.sql",
                ],
                "y",
            ),
            1,
        ),
        # Fix without specifying rules
        (
            (
                fix,
                [
                    "--fixed-suffix",
                    "_fix",
                    "test/fixtures/cli/fail_many.sql",
                ],
                "y",
            ),
            1,
        ),
        # Template syntax error in macro file
        (
            (
                lint,
                ["test/fixtures/cli/unknown_jinja_tag/test.sql", "-vvvvvvv"],
                "y",
            ),
            1,
        ),
    ],
)
def test__cli__command_lint_parse_with_retcode(command, ret_code):
    """Check commands expecting a non-zero ret code."""
    invoke_assert_code(ret_code=ret_code, args=command)


def test__cli__command_lint_warning_explicit_file_ignored():
    """Check ignoring file works when file is in an ignore directory."""
    runner = CliRunner()
    result = runner.invoke(
        lint, ["test/fixtures/linter/sqlfluffignore/path_b/query_c.sql"]
    )
    assert result.exit_code == 0
    assert (
        "Exact file path test/fixtures/linter/sqlfluffignore/path_b/query_c.sql "
        "was given but it was ignored"
    ) in result.output.strip()


def test__cli__command_lint_skip_ignore_files():
    """Check "ignore file" is skipped when --disregard-sqlfluffignores flag is set."""
    runner = CliRunner()
    result = runner.invoke(
        lint,
        [
            "test/fixtures/linter/sqlfluffignore/path_b/query_c.sql",
            "--disregard-sqlfluffignores",
        ],
    )
    assert result.exit_code == 1
    assert "L009" in result.output.strip()


def test__cli__command_lint_ignore_local_config():
    """Test that --ignore-local_config ignores .sqlfluff file as expected."""
    runner = CliRunner()
    # First we test that not including the --ignore-local-config includes
    # .sqlfluff file, and therefore the lint doesn't raise L012
    result = runner.invoke(
        lint,
        [
            "test/fixtures/cli/ignore_local_config/ignore_local_config_test.sql",
        ],
    )
    assert result.exit_code == 0
    assert "L012" not in result.output.strip()
    # Then repeat the same lint but this time ignoring the .sqlfluff file.
    # We should see L012 raised.
    result = runner.invoke(
        lint,
        [
            "--ignore-local-config",
            "--dialect=ansi",
            "test/fixtures/cli/ignore_local_config/ignore_local_config_test.sql",
        ],
    )
    assert result.exit_code == 1
    assert "L012" in result.output.strip()


def test__cli__command_versioning():
    """Check version command."""
    # Get the package version info
    pkg_version = sqlfluff.__version__
    # Get the version info from the config file
    config = configparser.ConfigParser()
    config.read_file(open("setup.cfg"))
    config_version = config["metadata"]["version"]
    assert pkg_version == config_version
    # Get the version from the cli
    runner = CliRunner()
    result = runner.invoke(version)
    assert result.exit_code == 0
    # We need to strip to remove the newline characters
    assert result.output.strip() == pkg_version


def test__cli__command_version():
    """Just check version command for exceptions."""
    # Get the package version info
    pkg_version = sqlfluff.__version__
    runner = CliRunner()
    result = runner.invoke(version)
    assert result.exit_code == 0
    assert pkg_version in result.output
    # Check a verbose version
    result = runner.invoke(version, ["-v"])
    assert result.exit_code == 0
    assert pkg_version in result.output


def test__cli__command_rules():
    """Check rules command for exceptions."""
    invoke_assert_code(args=[rules])


def test__cli__command_dialects():
    """Check dialects command for exceptions."""
    invoke_assert_code(args=[dialects])


def generic_roundtrip_test(
    source_file,
    rulestring,
    final_exit_code=0,
    force=True,
    fix_input=None,
    fix_exit_code=0,
    input_file_encoding="utf-8",
    output_file_encoding=None,
):
    """A test for roundtrip testing, take a file buffer, lint, fix and lint.

    This is explicitly different from the linter version of this, in that
    it uses the command line rather than the direct api.
    """
    filename = "testing.sql"
    # Lets get the path of a file to use
    tempdir_path = tempfile.mkdtemp()
    filepath = os.path.join(tempdir_path, filename)
    # Open the example file and write the content to it
    with open(filepath, mode="w", encoding=input_file_encoding) as dest_file:
        for line in source_file:
            dest_file.write(line)
    status = os.stat(filepath)
    assert stat.S_ISREG(status.st_mode)
    old_mode = stat.S_IMODE(status.st_mode)
    # Check that we first detect the issue
    invoke_assert_code(
        ret_code=1,
        args=[lint, ["--dialect=ansi", "--rules", rulestring, filepath]],
    )
    # Fix the file (in force mode)
    if force:
        fix_args = ["--rules", rulestring, "-f", filepath]
    else:
        fix_args = ["--rules", rulestring, filepath]
    fix_args.append("--dialect=ansi")
    invoke_assert_code(
        ret_code=fix_exit_code, args=[fix, fix_args], cli_input=fix_input
    )
    # Now lint the file and check for exceptions
    invoke_assert_code(
        ret_code=final_exit_code,
        args=[lint, ["--dialect=ansi", "--rules", rulestring, filepath]],
    )
    # Check the output file has the correct encoding after fix
    if output_file_encoding:
        with open(filepath, mode="rb") as f:
            data = f.read()
        assert chardet.detect(data)["encoding"] == output_file_encoding
    # Also check the file mode was preserved.
    status = os.stat(filepath)
    assert stat.S_ISREG(status.st_mode)
    new_mode = stat.S_IMODE(status.st_mode)
    assert new_mode == old_mode
    shutil.rmtree(tempdir_path)


@pytest.mark.parametrize(
    "rule,fname",
    [
        ("L001", "test/fixtures/linter/indentation_errors.sql"),
        ("L008", "test/fixtures/linter/whitespace_errors.sql"),
        ("L008", "test/fixtures/linter/indentation_errors.sql"),
        # Really stretching the ability of the fixer to re-indent a file
        ("L003", "test/fixtures/linter/indentation_error_hard.sql"),
    ],
)
def test__cli__command__fix(rule, fname):
    """Test the round trip of detecting, fixing and then not detecting the rule."""
    with open(fname) as test_file:
        generic_roundtrip_test(test_file, rule)


@pytest.mark.parametrize(
    "sql,fix_args,fixed,exit_code",
    [
        (
            # - One lint error: "where" is lower case
            # - Not fixable because of parse error, hence error exit
            """
            SELECT my_col
            FROM my_schema.my_table
            where processdate ! 3
            """,
            ["--force", "--fixed-suffix", "FIXED", "--rules", "L010"],
            None,
            1,
        ),
        (
            # - One lint error: "where" is lower case
            # - Not fixable because of templater error, hence error exit
            """
            SELECT my_col
            FROM my_schema.my_table
            where processdate {{ condition }}
            """,
            # Test the short versions of the options.
            ["--force", "-x", "FIXED", "-r", "L010"],
            None,
            1,
        ),
        (
            # - One lint error: "where" is lower case
            # - Not fixable because of parse error (even though "noqa"), hence
            #   error exit
            """
            SELECT my_col
            FROM my_schema.my_table
            where processdate ! 3  -- noqa: PRS
            """,
            # Test the short versions of the options.
            ["--force", "-x", "FIXED", "-r", "L010"],
            None,
            1,
        ),
        (
            # - No lint errors
            # - Parse error not suppressed, hence error exit
            """
            SELECT my_col
            FROM my_schema.my_table
            WHERE processdate ! 3
            """,
            ["--force", "--fixed-suffix", "FIXED", "--rules", "L010"],
            None,
            1,
        ),
        (
            # - No lint errors
            # - Parse error suppressed, hence success exit
            """
            SELECT my_col
            FROM my_schema.my_table
            WHERE processdate ! 3  --noqa: PRS
            """,
            ["--force", "--fixed-suffix", "FIXED", "--rules", "L010"],
            None,
            0,
        ),
        (
            # - One lint error: "where" is lower case
            # - Parse error not suppressed
            # - "--FIX-EVEN-UNPARSABLE", hence fix anyway & success exit
            """
            SELECT my_col
            FROM my_schema.my_table
            where processdate ! 3
            """,
            [
                "--force",
                "--fixed-suffix",
                "FIXED",
                "--rules",
                "L010",
                "--FIX-EVEN-UNPARSABLE",
            ],
            """
            SELECT my_col
            FROM my_schema.my_table
            WHERE processdate ! 3
            """,
            0,
        ),
        (
            # Two files:
            # File #1:
            #   - One lint error: "where" is lower case
            #   - Not fixable because of parse error
            # File #2:
            #   - One lint error: "where" is lower case
            #   - No parse error, thus fixable
            # Should fix the second file but not the first, and exit with an
            # error.
            [
                """
                SELECT my_col
                FROM my_schema.my_table
                where processdate ! 3
                """,
                """SELECT my_col
                FROM my_schema.my_table
                where processdate != 3""",
            ],
            ["--force", "--fixed-suffix", "FIXED", "--rules", "L010"],
            [
                None,
                """SELECT my_col
                FROM my_schema.my_table
                WHERE processdate != 3""",
            ],
            1,
        ),
    ],
    ids=[
        "1_lint_error_1_unsuppressed_parse_error",
        "1_lint_error_1_unsuppressed_templating_error",
        "1_lint_error_1_suppressed_parse_error",
        "0_lint_errors_1_unsuppressed_parse_error",
        "0_lint_errors_1_suppressed_parse_error",
        "1_lint_error_1_unsuppressed_parse_error_FIX_EVEN_UNPARSABLE",
        "2_files_with_lint_errors_1_unsuppressed_parse_error",
    ],
)
def test__cli__fix_error_handling_behavior(sql, fix_args, fixed, exit_code, tmpdir):
    """Tests how "fix" behaves wrt parse errors, exit code, etc."""
    if not isinstance(sql, list):
        sql = [sql]
    if not isinstance(fixed, list):
        fixed = [fixed]
    assert len(sql) == len(fixed)
    tmp_path = pathlib.Path(str(tmpdir))
    for idx, this_sql in enumerate(sql):
        filepath = tmp_path / f"testing{idx+1}.sql"
        filepath.write_text(textwrap.dedent(this_sql))
    with tmpdir.as_cwd():
        with pytest.raises(SystemExit) as e:
            fix(
                fix_args
                + [
                    "-f",
                    # Use the short dialect option
                    "-d",
                    "ansi",
                ]
            )
        assert exit_code == e.value.code
    for idx, this_fixed in enumerate(fixed):
        fixed_path = tmp_path / f"testing{idx+1}FIXED.sql"
        if this_fixed is not None:
            assert textwrap.dedent(this_fixed) == fixed_path.read_text()
        else:
            # A None value indicates "sqlfluff fix" should have skipped any
            # fixes for this file. To confirm this, we verify that the output
            # file WAS NOT EVEN CREATED.
            assert not fixed_path.is_file()


@pytest.mark.parametrize(
    "method,fix_even_unparsable",
    [
        ("command-line", False),
        ("command-line", True),
        ("config-file", False),
        ("config-file", True),
    ],
)
def test_cli_fix_even_unparsable(
    method: str, fix_even_unparsable: bool, monkeypatch, tmpdir
):
    """Test the fix_even_unparsable option works from cmd line and config."""
    sql_filename = "fix_even_unparsable.sql"
    sql_path = str(tmpdir / sql_filename)
    with open(sql_path, "w") as f:
        print(
            """SELECT my_col
FROM my_schema.my_table
where processdate ! 3
""",
            file=f,
        )
    options = [
        "--dialect",
        "ansi",
        "-f",
        "--fixed-suffix=FIXED",
        sql_path,
    ]
    if method == "command-line":
        if fix_even_unparsable:
            options.append("--FIX-EVEN-UNPARSABLE")
    else:
        assert method == "config-file"
        with open(str(tmpdir / ".sqlfluff"), "w") as f:
            print(
                f"[sqlfluff]\nfix_even_unparsable = {fix_even_unparsable}",
                file=f,
            )
    # TRICKY: Switch current directory to the one with the SQL file. Otherwise,
    # the setting doesn't work. That's because SQLFluff reads it in
    # sqlfluff.cli.commands.fix(), prior to reading any file-specific settings
    # (down in sqlfluff.core.linter.Linter._load_raw_file_and_config()).
    monkeypatch.chdir(str(tmpdir))
    invoke_assert_code(
        ret_code=0 if fix_even_unparsable else 1,
        args=[
            fix,
            options,
        ],
    )
    fixed_path = str(tmpdir / "fix_even_unparsableFIXED.sql")
    if fix_even_unparsable:
        with open(fixed_path, "r") as f:
            fixed_sql = f.read()
            assert (
                fixed_sql
                == """SELECT my_col
FROM my_schema.my_table
WHERE processdate ! 3
"""
            )
    else:
        assert not os.path.isfile(fixed_path)


_old_eval = BaseRule._eval
_fix_counter = 0


def _mock_eval(rule, context):
    # For test__cli__fix_loop_limit_behavior, we mock BaseRule.crawl(),
    # replacing it with this function. This function generates an infinite
    # sequence of fixes without ever repeating the same fix. This causes the
    # linter to hit the loop limit, allowing us to test that behavior.
    if context.segment.is_type("comment") and "Comment" in context.segment.raw:
        global _fix_counter
        _fix_counter += 1
        fix = LintFix.replace(
            context.segment, [CommentSegment(f"-- Comment {_fix_counter}")]
        )
        return LintResult(context.segment, fixes=[fix])
    else:
        return _old_eval(rule, context)


@pytest.mark.parametrize(
    "sql, exit_code",
    [
        ("-- Comment A\nSELECT 1 FROM foo", 1),
        ("-- noqa: disable=all\n-- Comment A\nSELECT 1 FROM foo", 0),
    ],
)
@patch("sqlfluff.rules.L001.Rule_L001._eval", _mock_eval)
def test__cli__fix_loop_limit_behavior(sql, exit_code, tmpdir):
    """Tests how "fix" behaves when the loop limit is exceeded."""
    fix_args = ["--force", "--fixed-suffix", "FIXED", "--rules", "L001"]
    tmp_path = pathlib.Path(str(tmpdir))
    filepath = tmp_path / "testing.sql"
    filepath.write_text(textwrap.dedent(sql))
    with tmpdir.as_cwd():
        with pytest.raises(SystemExit) as e:
            fix(
                fix_args
                + [
                    "-f",
                    "--dialect=ansi",
                ]
            )
        assert exit_code == e.value.code
    # In both parametrized test cases, no output file should have been
    # created.
    # - Case #1: Hitting the loop limit is an error
    # - Case #2: "noqa" suppressed all lint errors, thus no fixes applied
    fixed_path = tmp_path / "testingFIXED.sql"
    assert not fixed_path.is_file()


# Test case disabled because there isn't a good example of where to test this.
# This *should* test the case where a rule DOES have a proposed fix, but for
# some reason when we try to apply it, there's a failure.
# @pytest.mark.parametrize('rule,fname', [
#     # NB: L004 currently has no fix routine.
#     ('L004', 'test/fixtures/linter/indentation_errors.sql')
# ])
# def test__cli__command__fix_fail(rule, fname):
#     """Test the round trip of detecting, fixing and then still detecting the rule."""
#     with open(fname, mode='r') as test_file:
#         generic_roundtrip_test(test_file, rule, fix_exit_code=1, final_exit_code=65)


@pytest.mark.parametrize(
    "stdin,rules,stdout",
    [
        ("select * from t", "L003", "select * from t"),  # no change
        (
            " select * from t",
            "L003",
            "select * from t",
        ),  # fix preceding whitespace
        # L031 fix aliases in joins
        (
            "SELECT u.id, c.first_name, c.last_name, COUNT(o.user_id) "
            "FROM users as u JOIN customers as c on u.id = c.user_id JOIN orders as o "
            "on u.id = o.user_id;",
            "L031",
            "SELECT users.id, customers.first_name, customers.last_name, "
            "COUNT(orders.user_id) "
            "FROM users JOIN customers on users.id = customers.user_id JOIN orders on "
            "users.id = orders.user_id;",
        ),
    ],
)
def test__cli__command_fix_stdin(stdin, rules, stdout):
    """Check stdin input for fix works."""
    result = invoke_assert_code(
        args=[
            fix,
            ("-", "--rules", rules, "--disable-progress-bar", "--dialect=ansi"),
        ],
        cli_input=stdin,
    )
    assert result.output == stdout


def test__cli__command_fix_stdin_logging_to_stderr(monkeypatch):
    """Check that logging goes to stderr when stdin is passed to fix."""
    perfect_sql = "select col from table"

    class MockLinter(sqlfluff.core.Linter):
        @classmethod
        def lint_fix_parsed(cls, *args, **kwargs):
            cls._warn_unfixable("<FAKE CODE>")
            return super().lint_fix_parsed(*args, **kwargs)

    monkeypatch.setattr(sqlfluff.cli.commands, "Linter", MockLinter)
    result = invoke_assert_code(
        args=[fix, ("-", "--rules=L003", "--dialect=ansi")],
        cli_input=perfect_sql,
        mix_stderr=False,
    )

    assert result.stdout == perfect_sql
    assert "<FAKE CODE>" in result.stderr


def test__cli__command_fix_stdin_safety():
    """Check edge cases regarding safety when fixing stdin."""
    perfect_sql = "select col from table"

    # just prints the very same thing
    result = invoke_assert_code(
        args=[fix, ("-", "--disable-progress-bar", "--dialect=ansi")],
        cli_input=perfect_sql,
    )
    assert result.output.strip() == perfect_sql


@pytest.mark.parametrize(
    "sql,exit_code,params,output_contains",
    [
        (
            "create TABLE {{ params.dsfsdfds }}.t (a int)",
            1,
            "-v",
            "Fix aborted due to unparsable template variables.",
        ),  # template error
        ("create TABLE a.t (a int)", 0, "", ""),  # fixable error
        ("create table a.t (a int)", 0, "", ""),  # perfection
        (
            "select col from a join b using (c)",
            1,
            "-v",
            "Unfixable violations detected.",
        ),  # unfixable error (using)
    ],
)
def test__cli__command_fix_stdin_error_exit_code(
    sql, exit_code, params, output_contains
):
    """Check that the CLI fails nicely if fixing a templated stdin."""
    if exit_code == 0:
        invoke_assert_code(
            args=[fix, ("--dialect=ansi", "-")],
            cli_input=sql,
        )
    else:
        with pytest.raises(SystemExit) as exc_info:
            invoke_assert_code(
                args=[fix, (params, "--dialect=ansi", "-")],
                cli_input=sql,
                output_contains=output_contains,
            )
        assert exc_info.value.args[0] == exit_code


@pytest.mark.parametrize(
    "rule,fname,prompt,exit_code,fix_exit_code",
    [
        ("L001", "test/fixtures/linter/indentation_errors.sql", "y", 0, 0),
        ("L001", "test/fixtures/linter/indentation_errors.sql", "n", 1, 1),
    ],
)
def test__cli__command__fix_no_force(rule, fname, prompt, exit_code, fix_exit_code):
    """Round trip test, using the prompts."""
    with open(fname) as test_file:
        generic_roundtrip_test(
            test_file,
            rule,
            force=False,
            final_exit_code=exit_code,
            fix_input=prompt,
            fix_exit_code=fix_exit_code,
        )


@pytest.mark.parametrize("serialize", ["yaml", "json"])
@pytest.mark.parametrize("write_file", [None, "outfile"])
def test__cli__command_parse_serialize_from_stdin(serialize, write_file, tmp_path):
    """Check that the parser serialized output option is working.

    This tests both output to stdout and output to file.

    Not going to test for the content of the output as that is subject to change.
    """
    cmd_args = ("-", "--format", serialize, "--dialect=ansi")

    if write_file:
        target_file = os.path.join(tmp_path, write_file + "." + serialize)
        cmd_args += ("--write-output", target_file)

    result = invoke_assert_code(
        args=[parse, cmd_args],
        cli_input="select * from tbl",
    )

    if write_file:
        with open(target_file, "r") as payload_file:
            result_payload = payload_file.read()
    else:
        result_payload = result.output

    if serialize == "json":
        result = json.loads(result_payload)
    elif serialize == "yaml":
        result = yaml.safe_load(result_payload)
    else:
        raise Exception
    result = result[0]  # only one file
    assert result["filepath"] == "stdin"


@pytest.mark.parametrize("serialize", ["yaml", "json"])
@pytest.mark.parametrize(
    "sql,expected,exit_code",
    [
        ("select * from tbl", [], 0),  # empty list if no violations
        (
            "SElect * from tbl",
            [
                {
                    "filepath": "stdin",
                    "violations": [
                        {
                            "code": "L010",
                            "line_no": 1,
                            "line_pos": 1,
                            "description": "Keywords must be consistently upper case.",
                        },
                        {
                            "code": "L010",
                            "line_no": 1,
                            "line_pos": 10,
                            "description": "Keywords must be consistently upper case.",
                        },
                    ],
                }
            ],
            1,
        ),
    ],
)
def test__cli__command_lint_serialize_from_stdin(serialize, sql, expected, exit_code):
    """Check an explicit serialized return value for a single error."""
    result = invoke_assert_code(
        args=[
            lint,
            (
                "-",
                "--rules",
                "L010",
                "--format",
                serialize,
                "--disable-progress-bar",
                "--dialect=ansi",
            ),
        ],
        cli_input=sql,
        ret_code=exit_code,
    )

    if serialize == "json":
        assert json.loads(result.output) == expected
    elif serialize == "yaml":
        assert yaml.safe_load(result.output) == expected
    else:
        raise Exception


@pytest.mark.parametrize(
    "command",
    [
        [lint, ("this_file_does_not_exist.sql")],
        [fix, ("this_file_does_not_exist.sql")],
    ],
)
def test__cli__command_fail_nice_not_found(command):
    """Check commands fail as expected when then don't find files."""
    result = invoke_assert_code(args=command, ret_code=2)
    assert "could not be accessed" in result.output


@patch("click.utils.should_strip_ansi")
@patch("sys.stdout.isatty")
def test__cli__command_lint_nocolor(isatty, should_strip_ansi, capsys, tmpdir):
    """Test the --nocolor option prevents color output."""
    # Patch these two functions to make it think every output stream is a TTY.
    # In spite of this, the output should not contain ANSI color codes because
    # we specify "--nocolor" below.
    isatty.return_value = True
    should_strip_ansi.return_value = False
    fpath = "test/fixtures/linter/indentation_errors.sql"
    output_file = str(tmpdir / "result.txt")
    cmd_args = [
        "--verbose",
        "--nocolor",
        "--dialect",
        "ansi",
        "--disable-progress-bar",
        fpath,
        "--write-output",
        output_file,
    ]
    with pytest.raises(SystemExit):
        lint(cmd_args)
    out = capsys.readouterr()[0]
    assert not contains_ansi_escape(out)
    with open(output_file, "r") as f:
        file_contents = f.read()
    assert not contains_ansi_escape(file_contents)


@pytest.mark.parametrize(
    "serialize",
    ["human", "yaml", "json", "github-annotation", "github-annotation-native"],
)
@pytest.mark.parametrize("write_file", [None, "outfile"])
def test__cli__command_lint_serialize_multiple_files(serialize, write_file, tmp_path):
    """Test the output output formats for multiple files.

    This tests runs both stdout checking and file checking.
    """
    fpath = "test/fixtures/linter/indentation_errors.sql"

    cmd_args = (
        fpath,
        fpath,
        "--format",
        serialize,
        "--disable-progress-bar",
    )

    if write_file:
        ext = {
            "human": ".txt",
            "yaml": ".yaml",
        }
        target_file = os.path.join(tmp_path, write_file + ext.get(serialize, ".json"))
        cmd_args += ("--write-output", target_file)

    # note the file is in here twice. two files = two payloads.
    result = invoke_assert_code(
        args=[lint, cmd_args],
        ret_code=1,
    )

    if write_file:
        with open(target_file, "r") as payload_file:
            result_payload = payload_file.read()
    else:
        result_payload = result.output

    if serialize == "human":
        assert len(result_payload.split("\n")) == 33 if write_file else 32
    elif serialize == "json":
        result = json.loads(result_payload)
        assert len(result) == 2
    elif serialize == "yaml":
        result = yaml.safe_load(result_payload)
        assert len(result) == 2
    elif serialize == "github-annotation":
        result = json.loads(result_payload)
        filepaths = {r["file"] for r in result}
        assert len(filepaths) == 1
    elif serialize == "github-annotation-native":
        result = result_payload.split("\n")
        # SQLFluff produces trailing newline
        if result[-1] == "":
            del result[-1]
        assert len(result) == 24
    else:
        raise Exception


def test__cli__command_lint_serialize_github_annotation():
    """Test format of github-annotation output."""
    fpath = "test/fixtures/linter/identifier_capitalisation.sql"
    result = invoke_assert_code(
        args=[
            lint,
            (
                fpath,
                "--format",
                "github-annotation",
                "--annotation-level",
                "warning",
                "--disable-progress-bar",
            ),
        ],
        ret_code=1,
    )
    result = json.loads(result.output)
    assert result == [
        {
            "annotation_level": "warning",
            # Normalise paths to control for OS variance
            "file": os.path.normpath(
                "test/fixtures/linter/identifier_capitalisation.sql"
            ),
            "line": 1,
            "message": "L036: Select targets should be on a new line unless there is "
            "only one select target.",
            "start_column": 1,
            "end_column": 1,
            "title": "SQLFluff",
        },
        {
            "annotation_level": "warning",
            # Normalise paths to control for OS variance
            "file": os.path.normpath(
                "test/fixtures/linter/identifier_capitalisation.sql"
            ),
            "line": 2,
            "message": "L027: Unqualified reference 'foo' found in select with more "
            "than one referenced table/view.",
            "start_column": 5,
            "end_column": 5,
            "title": "SQLFluff",
        },
        {
            "annotation_level": "warning",
            # Normalise paths to control for OS variance
            "file": os.path.normpath(
                "test/fixtures/linter/identifier_capitalisation.sql"
            ),
            "line": 3,
            "message": "L012: Implicit/explicit aliasing of columns.",
            "start_column": 5,
            "end_column": 5,
            "title": "SQLFluff",
        },
        {
            "annotation_level": "warning",
            # Normalise paths to control for OS variance
            "file": os.path.normpath(
                "test/fixtures/linter/identifier_capitalisation.sql"
            ),
            "line": 3,
            "message": "L014: Unquoted identifiers must be consistently lower case.",
            "start_column": 5,
            "end_column": 5,
            "title": "SQLFluff",
        },
        {
            "annotation_level": "warning",
            # Normalise paths to control for OS variance
            "file": os.path.normpath(
                "test/fixtures/linter/identifier_capitalisation.sql"
            ),
            "line": 4,
            "message": "L010: Keywords must be consistently lower case.",
            "start_column": 1,
            "end_column": 1,
            "title": "SQLFluff",
        },
        {
            "annotation_level": "warning",
            # Normalise paths to control for OS variance
            "file": os.path.normpath(
                "test/fixtures/linter/identifier_capitalisation.sql"
            ),
            "line": 4,
            "message": "L014: Unquoted identifiers must be consistently lower case.",
            "start_column": 12,
            "end_column": 12,
            "title": "SQLFluff",
        },
        {
            "annotation_level": "warning",
            # Normalise paths to control for OS variance
            "file": os.path.normpath(
                "test/fixtures/linter/identifier_capitalisation.sql"
            ),
            "line": 4,
            "message": "L014: Unquoted identifiers must be consistently lower case.",
            "start_column": 18,
            "end_column": 18,
            "title": "SQLFluff",
        },
    ]


def test__cli__command_lint_serialize_github_annotation_native():
    """Test format of github-annotation output."""
    fpath = "test/fixtures/linter/identifier_capitalisation.sql"
    # Normalise paths to control for OS variance
    fpath_normalised = os.path.normpath(fpath)

    result = invoke_assert_code(
        args=[
            lint,
            (
                fpath,
                "--format",
                "github-annotation-native",
                "--annotation-level",
                "error",
                "--disable-progress-bar",
            ),
        ],
        ret_code=1,
    )

    assert result.output == "\n".join(
        [
            f"::error title=SQLFluff,file={fpath_normalised},line=1,col=1::"
            "L036: Select targets should be on a new line unless there is only one "
            "select target.",
            f"::error title=SQLFluff,file={fpath_normalised},line=2,col=5::"
            "L027: Unqualified reference 'foo' found in select with more than one "
            "referenced table/view.",
            f"::error title=SQLFluff,file={fpath_normalised},line=3,col=5::"
            "L012: Implicit/explicit aliasing of columns.",
            f"::error title=SQLFluff,file={fpath_normalised},line=3,col=5::"
            "L014: Unquoted identifiers must be consistently lower case.",
            f"::error title=SQLFluff,file={fpath_normalised},line=4,col=1::"
            "L010: Keywords must be consistently lower case.",
            f"::error title=SQLFluff,file={fpath_normalised},line=4,col=12::"
            "L014: Unquoted identifiers must be consistently lower case.",
            f"::error title=SQLFluff,file={fpath_normalised},line=4,col=18::"
            "L014: Unquoted identifiers must be consistently lower case.",
            "",  # SQLFluff produces trailing newline
        ]
    )


@pytest.mark.parametrize("serialize", ["github-annotation", "github-annotation-native"])
def test__cli__command_lint_serialize_annotation_level_error_failure_equivalent(
    serialize,
):
    """Test format of github-annotation output."""
    fpath = "test/fixtures/linter/identifier_capitalisation.sql"
    result_error = invoke_assert_code(
        args=[
            lint,
            (
                fpath,
                "--format",
                serialize,
                "--annotation-level",
                "error",
                "--disable-progress-bar",
            ),
        ],
        ret_code=1,
    )

    result_failure = invoke_assert_code(
        args=[
            lint,
            (
                fpath,
                "--format",
                serialize,
                "--annotation-level",
                "failure",
                "--disable-progress-bar",
            ),
        ],
        ret_code=1,
    )

    assert result_error.output == result_failure.output


def test___main___help():
    """Test that the CLI can be access via __main__."""
    # nonzero exit is good enough
    subprocess.check_output(
        [sys.executable, "-m", "sqlfluff", "--help"], env=os.environ
    )


@pytest.mark.parametrize(
    "encoding_in,encoding_out",
    [
        ("utf-8", "ascii"),  # chardet will detect ascii as a subset of utf-8
        ("utf-8-sig", "UTF-8-SIG"),
        ("utf-32", "UTF-32"),
    ],
)
def test_encoding(encoding_in, encoding_out):
    """Check the encoding of the test file remains the same after fix is applied."""
    with open("test/fixtures/linter/indentation_errors.sql", "r") as testfile:
        generic_roundtrip_test(
            testfile,
            "L001",
            input_file_encoding=encoding_in,
            output_file_encoding=encoding_out,
        )


@pytest.mark.parametrize(
    "encoding,method,expect_success",
    [
        ("utf-8", "command-line", False),
        ("utf-8-SIG", "command-line", True),
        ("utf-8", "config-file", False),
        ("utf-8-SIG", "config-file", True),
    ],
)
def test_cli_encoding(encoding, method, expect_success, tmpdir):
    """Try loading a utf-8-SIG encoded file using the correct encoding via the cli."""
    sql_path = "test/fixtures/cli/encoding_test.sql"
    if method == "command-line":
        options = [sql_path, "--encoding", encoding]
    else:
        assert method == "config-file"
        with open(str(tmpdir / ".sqlfluff"), "w") as f:
            print(f"[sqlfluff]\ndialect=ansi\nencoding = {encoding}", file=f)
        shutil.copy(sql_path, tmpdir)
        options = [str(tmpdir / "encoding_test.sql")]
    result = invoke_assert_code(
        ret_code=1,
        args=[
            lint,
            options,
        ],
    )
    raw_output = repr(result.output)

    # Incorrect encoding raises parsing and lexer errors.
    success1 = r"L:   1 | P:   1 |  LXR |" not in raw_output
    success2 = r"L:   1 | P:   1 |  PRS |" not in raw_output
    assert success1 == expect_success
    assert success2 == expect_success


def test_cli_no_disable_noqa_flag():
    """Test that unset --disable_noqa flag respects inline noqa comments."""
    invoke_assert_code(
        ret_code=0,
        args=[
            lint,
            ["test/fixtures/cli/disable_noqa_test.sql"],
        ],
    )


def test_cli_disable_noqa_flag():
    """Test that --disable_noqa flag ignores inline noqa comments."""
    result = invoke_assert_code(
        ret_code=1,
        args=[
            lint,
            [
                "test/fixtures/cli/disable_noqa_test.sql",
                "--disable-noqa",
            ],
        ],
    )
    raw_output = repr(result.output)

    # Linting error is raised even though it is inline ignored.
    assert r"L:   5 | P:  11 | L010 |" in raw_output


def test_cli_get_default_config():
    """`nocolor` and `verbose` values loaded from config if not specified via CLI."""
    config = get_config(
        "test/fixtures/config/toml/pyproject.toml",
        True,
        nocolor=None,
        verbose=None,
        require_dialect=False,
    )
    assert config.get("nocolor") is True
    assert config.get("verbose") == 2


@patch(
    "sqlfluff.core.linter.linter.progress_bar_configuration",
    disable_progress_bar=False,
)
class TestProgressBars:
    """Progress bars test cases.

    The tqdm package, used for handling progress bars, is able to tell when it is used
    in a not tty terminal (when `disable` is set to None). In such cases, it just does
    not render anything. To suppress that for testing purposes, we need to set
    implicitly that we don't want to disable it.
    Probably it would be better - cleaner - just to patch `isatty` at some point,
    but I didn't find a way how to do that properly.
    """

    def test_cli_lint_disabled_progress_bar(
        self, mock_disable_progress_bar: MagicMock
    ) -> None:
        """When progress bar is disabled, nothing should be printed into output."""
        result = invoke_assert_code(
            args=[
                lint,
                [
                    "--disable-progress-bar",
                    "test/fixtures/linter/passing.sql",
                ],
            ],
        )
        raw_output = repr(result.output)

        assert "\rpath test/fixtures/linter/passing.sql:" not in raw_output
        assert "\rparsing: 0it" not in raw_output
        assert "\r\rlint by rules:" not in raw_output

    def test_cli_lint_disabled_progress_bar_deprecated_option(
        self, mock_disable_progress_bar: MagicMock
    ) -> None:
        """Same as above but checks additionally if deprecation warning is printed."""
        result = invoke_assert_code(
            args=[
                lint,
                [
                    "--disable_progress_bar",
                    "test/fixtures/linter/passing.sql",
                ],
            ],
        )
        raw_output = repr(result.output)

        assert "\rpath test/fixtures/linter/passing.sql:" not in raw_output
        assert "\rparsing: 0it" not in raw_output
        assert "\r\rlint by rules:" not in raw_output
        assert (
            "DeprecationWarning: The option '--disable_progress_bar' is deprecated, "
            "use '--disable-progress-bar'"
        ) in raw_output

    def test_cli_lint_enabled_progress_bar(
        self, mock_disable_progress_bar: MagicMock
    ) -> None:
        """When progress bar is enabled, there should be some tracks in output."""
        result = invoke_assert_code(
            args=[
                lint,
                [
                    "test/fixtures/linter/passing.sql",
                ],
            ],
        )
        raw_output = repr(result.output)

        assert r"\rlint by rules:" in raw_output
        assert r"\rrule L001:" in raw_output
        assert r"\rrule L049:" in raw_output

    def test_cli_lint_enabled_progress_bar_multiple_paths(
        self, mock_disable_progress_bar: MagicMock
    ) -> None:
        """When progress bar is enabled, there should be some tracks in output."""
        result = invoke_assert_code(
            ret_code=1,
            args=[
                lint,
                [
                    "test/fixtures/linter/passing.sql",
                    "test/fixtures/linter/indentation_errors.sql",
                ],
            ],
        )
        raw_output = repr(result.output)

        assert r"\rpath test/fixtures/linter/passing.sql:" in raw_output
        assert r"\rpath test/fixtures/linter/indentation_errors.sql:" in raw_output
        assert r"\rlint by rules:" in raw_output
        assert r"\rrule L001:" in raw_output
        assert r"\rrule L049:" in raw_output

    def test_cli_lint_enabled_progress_bar_multiple_files(
        self, mock_disable_progress_bar: MagicMock
    ) -> None:
        """When progress bar is enabled, there should be some tracks in output."""
        result = invoke_assert_code(
            args=[
                lint,
                [
                    "test/fixtures/linter/multiple_files",
                ],
            ],
        )
        raw_output = repr(result.output)

        assert r"\rfile passing.1.sql:" in raw_output
        assert r"\rfile passing.2.sql:" in raw_output
        assert r"\rfile passing.3.sql:" in raw_output
        assert r"\rlint by rules:" in raw_output
        assert r"\rrule L001:" in raw_output
        assert r"\rrule L049:" in raw_output


multiple_expected_output = """==== finding fixable violations ====
== [test/fixtures/linter/multiple_sql_errors.sql] FAIL
L:  12 | P:   1 | L003 | Expected 1 indentation, found 0 [compared to line 10]
==== fixing violations ====
1 fixable linting violations found
Are you sure you wish to attempt to fix these? [Y/n] ...
Invalid input, please enter 'Y' or 'N'
Aborting...
  [4 unfixable linting violations found]
"""


def test__cli__fix_multiple_errors_no_show_errors():
    """Basic checking of lint functionality."""
    result = invoke_assert_code(
        ret_code=1,
        args=[
            fix,
            [
                "--disable-progress-bar",
                "test/fixtures/linter/multiple_sql_errors.sql",
            ],
        ],
    )
    # We should get a readout of what the error was
    check_a = "4 unfixable linting violations found"
    assert check_a in result.output
    # Finally check the WHOLE output to make sure that unexpected newlines are not
    # added. The replace command just accounts for cross platform testing.
    assert result.output.replace("\\", "/").startswith(multiple_expected_output)


def test__cli__fix_multiple_errors_show_errors():
    """Basic checking of lint functionality."""
    result = invoke_assert_code(
        ret_code=1,
        args=[
            fix,
            [
                "--disable-progress-bar",
                "--show-lint-violations",
                "test/fixtures/linter/multiple_sql_errors.sql",
            ],
        ],
    )
    # We should get a readout of what the error was
    check_a = "4 unfixable linting violations found"
    assert check_a in result.output
    # Finally check the WHOLE output to make sure that unexpected newlines are not
    # added. The replace command just accounts for cross platform testing.
    assert (
        "L:  12 | P:   1 | L003 | Expected 1 indentation, found 0 [compared to line 10]"
        in result.output
    )
    assert (
        "L:  36 | P:   9 | L027 | Unqualified reference 'package_id' found in "
        "select with more than" in result.output
    )
    assert (
        "L:  45 | P:  17 | L027 | Unqualified reference 'owner_type' found in "
        "select with more than" in result.output
    )
    assert (
        "L:  45 | P:  50 | L027 | Unqualified reference 'app_key' found in "
        "select with more than one" in result.output
    )
    assert (
        "L:  42 | P:  45 | L027 | Unqualified reference 'owner_id' found in "
        "select with more than" in result.output
    )


def test__cli__multiple_files__fix_multiple_errors_show_errors():
    """Basic check of lint ensures with multiple files, filenames are listed."""
    sql_path = "test/fixtures/linter/multiple_sql_errors.sql"
    indent_path = "test/fixtures/linter/indentation_errors.sql"
    result = invoke_assert_code(
        ret_code=1,
        args=[
            fix,
            [
                "--disable-progress-bar",
                "--show-lint-violations",
                sql_path,
                indent_path,
            ],
        ],
    )

    unfixable_error_msg = "==== lint for unfixable violations ===="
    assert unfixable_error_msg in result.output

    indent_pass_msg = f"== [{os.path.normpath(indent_path)}] PASS"
    multi_fail_msg = f"== [{os.path.normpath(sql_path)}] FAIL"

    unfix_err_log = result.output[result.output.index(unfixable_error_msg) :]
    assert indent_pass_msg in unfix_err_log
    assert multi_fail_msg in unfix_err_log

    # Assert that they are sorted in alphabetical order
    assert unfix_err_log.index(indent_pass_msg) < unfix_err_log.index(multi_fail_msg)
