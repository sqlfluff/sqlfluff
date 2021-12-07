"""The Test file for CLI (General)."""

import configparser
import tempfile
import os
import shutil
import json
from unittest.mock import MagicMock, patch

import oyaml as yaml
import subprocess
import chardet
import sys

# Testing libraries
import pytest
from click.testing import CliRunner

# We import the library directly here to get the version
import sqlfluff
from sqlfluff.cli.commands import lint, version, rules, fix, parse, dialects


def invoke_assert_code(
    ret_code=0,
    args=None,
    kwargs=None,
    cli_input=None,
    mix_stderr=True,
    output_contains="",
):
    """Invoke a command and check return code."""
    args = args or []
    kwargs = kwargs or {}
    if cli_input:
        kwargs["input"] = cli_input
    runner = CliRunner(mix_stderr=mix_stderr)
    result = runner.invoke(*args, **kwargs)
    # Output the CLI code for debugging
    print(result.output)
    # Check return codes
    if output_contains != "":
        assert output_contains in result.output
    if ret_code == 0:
        if result.exception:
            raise result.exception
    assert ret_code == result.exit_code
    return result


expected_output = """== [test/fixtures/linter/indentation_error_simple.sql] FAIL
L:   2 | P:   4 | L003 | Indentation not hanging or a multiple of 4 spaces
L:   5 | P:  10 | L010 | Keywords must be consistently upper case.
L:   5 | P:  13 | L031 | Avoid aliases in from clauses and join conditions.
"""


def test__cli__command_directed():
    """Basic checking of lint functionality."""
    result = invoke_assert_code(
        ret_code=65,
        args=[
            lint,
            [
                "--disable_progress_bar",
                "test/fixtures/linter/indentation_error_simple.sql",
            ],
        ],
    )
    # We should get a readout of what the error was
    check_a = "L:   2 | P:   4 | L003"
    # NB: Skip the number at the end because it's configurable
    check_b = "Indentation"
    assert check_a in result.output
    assert check_b in result.output
    # Finally check the WHOLE output to make sure that unexpected newlines are not added.
    # The replace command just accounts for cross platform testing.
    assert result.output.replace("\\", "/").startswith(expected_output)


def test__cli__command_dialect():
    """Check the script raises the right exception on an unknown dialect."""
    # The dialect is unknown should be a non-zero exit code
    invoke_assert_code(
        ret_code=66,
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


def test__cli__command_dialect_legacy():
    """Check the script raises the right exception on a legacy dialect."""
    result = invoke_assert_code(
        ret_code=66,
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
    """Check the script raises the right exception on a non-existant extra config path."""
    result = invoke_assert_code(
        ret_code=66,
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
        "Extra config 'test/fixtures/cli/extra_configs/.sqlfluffsdfdfdfsfd' does not exist."
        in result.stdout
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
    invoke_assert_code(args=[lint, command], cli_input=sql)


@pytest.mark.parametrize(
    "command",
    [
        # Test basic linting
        (lint, ["-n", "test/fixtures/cli/passing_b.sql", "--exclude-rules", "L051"]),
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
        # Test basic linting with specific logger
        (
            lint,
            [
                "-n",
                "test/fixtures/cli/passing_b.sql",
                "-vvv",
                "--logger",
                "parser",
                "--exclude-rules",
                "L051",
            ],
        ),
        # Check basic parsing
        (parse, ["-n", "test/fixtures/cli/passing_b.sql", "--exclude-rules", "L051"]),
        # Test basic parsing with very high verbosity
        (
            parse,
            [
                "-n",
                "test/fixtures/cli/passing_b.sql",
                "-vvvvvvvvvvv",
                "--exclude-rules",
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
        (lint, ["-n", "--rules", "L001", "test/fixtures/linter/operator_errors.sql"]),
        # Check linting works in specifying multiple rules
        (
            lint,
            ["-n", "--rules", "L001,L002", "test/fixtures/linter/operator_errors.sql"],
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
    ],
)
def test__cli__command_lint_parse(command):
    """Check basic commands on a more complicated script."""
    invoke_assert_code(args=command)


@pytest.mark.parametrize(
    "command, ret_code",
    [
        # Check the script doesn't raise an unexpected exception with badly formed files.
        (
            (
                fix,
                ["--rules", "L001", "test/fixtures/cli/fail_many.sql", "-vvvvvvv"],
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
    ],
)
def test__cli__command_lint_parse_with_retcode(command, ret_code):
    """Check commands expecting a non-zero ret code."""
    invoke_assert_code(ret_code=ret_code, args=command)


def test__cli__command_lint_warning_explicit_file_ignored():
    """Check ignoring file works when passed explicitly and ignore file is in the same directory."""
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
    assert result.exit_code == 65
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
            "test/fixtures/cli/ignore_local_config/ignore_local_config_test.sql",
        ],
    )
    assert result.exit_code == 65
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
    # Check that we first detect the issue
    invoke_assert_code(ret_code=65, args=[lint, ["--rules", rulestring, filepath]])
    # Fix the file (in force mode)
    if force:
        fix_args = ["--rules", rulestring, "-f", filepath]
    else:
        fix_args = ["--rules", rulestring, filepath]
    invoke_assert_code(
        ret_code=fix_exit_code, args=[fix, fix_args], cli_input=fix_input
    )
    # Now lint the file and check for exceptions
    invoke_assert_code(
        ret_code=final_exit_code, args=[lint, ["--rules", rulestring, filepath]]
    )
    # Check the output file has the correct encoding after fix
    if output_file_encoding:
        with open(filepath, mode="rb") as f:
            data = f.read()
        assert chardet.detect(data)["encoding"] == output_file_encoding
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
        (" select * from t", "L003", "select * from t"),  # fix preceding whitespace
        # L031 fix aliases in joins
        (
            "SELECT u.id, c.first_name, c.last_name, COUNT(o.user_id) "
            "FROM users as u JOIN customers as c on u.id = c.user_id JOIN orders as o on u.id = o.user_id;",
            "L031",
            "SELECT users.id, customers.first_name, customers.last_name, COUNT(orders.user_id) "
            "FROM users JOIN customers on users.id = customers.user_id JOIN orders on users.id = orders.user_id;",
        ),
    ],
)
def test__cli__command_fix_stdin(stdin, rules, stdout):
    """Check stdin input for fix works."""
    result = invoke_assert_code(
        args=[fix, ("-", "--rules", rules, "--disable_progress_bar")], cli_input=stdin
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
        args=[fix, ("-", "--rules=L003")], cli_input=perfect_sql, mix_stderr=False
    )

    assert result.stdout == perfect_sql
    assert "<FAKE CODE>" in result.stderr


def test__cli__command_fix_stdin_safety():
    """Check edge cases regarding safety when fixing stdin."""
    perfect_sql = "select col from table"

    # just prints the very same thing
    result = invoke_assert_code(
        args=[fix, ("-", "--disable_progress_bar")], cli_input=perfect_sql
    )
    assert result.output.strip() == perfect_sql


@pytest.mark.parametrize(
    "sql,exit_code,params,output_contains",
    [
        (
            "create TABLE {{ params.dsfsdfds }}.t (a int)",
            1,
            "-v",
            "Fix aborted due to unparseable template variables.",
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
            args=[fix, ("-")],
            cli_input=sql,
        )
    else:
        with pytest.raises(SystemExit) as exc_info:
            invoke_assert_code(
                args=[fix, (params, "-")],
                cli_input=sql,
                output_contains=output_contains,
            )
        assert exc_info.value.args[0] == exit_code


@pytest.mark.parametrize(
    "rule,fname,prompt,exit_code,fix_exit_code",
    [
        ("L001", "test/fixtures/linter/indentation_errors.sql", "y", 0, 0),
        ("L001", "test/fixtures/linter/indentation_errors.sql", "n", 65, 1),
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
def test__cli__command_parse_serialize_from_stdin(serialize):
    """Check that the parser serialized output option is working.

    Not going to test for the content of the output as that is subject to change.
    """
    result = invoke_assert_code(
        args=[parse, ("-", "--format", serialize)],
        cli_input="select * from tbl",
    )
    if serialize == "json":
        result = json.loads(result.output)
    elif serialize == "yaml":
        result = yaml.safe_load(result.output)
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
            65,
        ),
    ],
)
def test__cli__command_lint_serialize_from_stdin(serialize, sql, expected, exit_code):
    """Check an explicit serialized return value for a single error."""
    result = invoke_assert_code(
        args=[
            lint,
            ("-", "--rules", "L010", "--format", serialize, "--disable_progress_bar"),
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
    result = invoke_assert_code(args=command, ret_code=1)
    assert "could not be accessed" in result.output


@pytest.mark.parametrize("serialize", ["yaml", "json", "github-annotation"])
def test__cli__command_lint_serialize_multiple_files(serialize):
    """Check the general format of JSON output for multiple files."""
    fpath = "test/fixtures/linter/indentation_errors.sql"

    # note the file is in here twice. two files = two payloads.
    result = invoke_assert_code(
        args=[lint, (fpath, fpath, "--format", serialize, "--disable_progress_bar")],
        ret_code=65,
    )

    if serialize == "json":
        result = json.loads(result.output)
        assert len(result) == 2
    elif serialize == "yaml":
        result = yaml.safe_load(result.output)
        assert len(result) == 2
    elif serialize == "github-annotation":
        result = json.loads(result.output)
        filepaths = {r["file"] for r in result}
        assert len(filepaths) == 1
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
                "--disable_progress_bar",
            ),
        ],
        ret_code=65,
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
            "message": "L027: Unqualified reference 'foo' found in select with more than "
            "one referenced table/view.",
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


def test_cli_pass_on_correct_encoding_argument():
    """Try loading a utf-8-SIG encoded file using the correct encoding via the cli."""
    result = invoke_assert_code(
        ret_code=65,
        args=[
            lint,
            ["test/fixtures/cli/encoding_test.sql", "--encoding", "utf-8-SIG"],
        ],
    )
    raw_output = repr(result.output)

    # Incorrect encoding raises paring and lexer errors.
    assert r"L:   1 | P:   1 |  LXR |" not in raw_output
    assert r"L:   1 | P:   1 |  PRS |" not in raw_output


def test_cli_fail_on_wrong_encoding_argument():
    """Try loading a utf-8-SIG encoded file using the wrong encoding via the cli."""
    result = invoke_assert_code(
        ret_code=65,
        args=[
            lint,
            ["test/fixtures/cli/encoding_test.sql", "--encoding", "utf-8"],
        ],
    )
    raw_output = repr(result.output)

    # Incorrect encoding raises paring and lexer errors.
    assert r"L:   1 | P:   1 |  LXR |" in raw_output
    assert r"L:   1 | P:   1 |  PRS |" in raw_output


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
        ret_code=65,
        args=[
            lint,
            ["test/fixtures/cli/disable_noqa_test.sql", "--disable-noqa"],
        ],
    )
    raw_output = repr(result.output)

    # Linting error is raised even though it is inline ignored.
    assert r"L:   5 | P:  11 | L010 |" in raw_output


@patch(
    "sqlfluff.core.linter.linter.progress_bar_configuration", disable_progress_bar=False
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
            ret_code=65,
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

    def test_cli_lint_enabled_progress_bar(
        self, mock_disable_progress_bar: MagicMock
    ) -> None:
        """When progress bar is enabled, there should be some tracks in output."""
        result = invoke_assert_code(
            ret_code=65,
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
            ret_code=65,
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

    def test_cli_lint_disabled_progress_bar_when_verbose_mode(
        self, mock_disable_progress_bar: MagicMock
    ) -> None:
        """Progressbar is disabled when verbose mode is set."""
        result = invoke_assert_code(
            ret_code=2,
            args=[
                lint,
                [
                    "-v" "test/fixtures/linter/passing.sql",
                ],
            ],
        )
        raw_output = repr(result.output)

        assert r"\rparsing: 0it" not in raw_output
        assert r"\rlint by rules:" not in raw_output
        assert r"\rrule L001:" not in raw_output
