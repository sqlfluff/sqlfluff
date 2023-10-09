"""Round trip tests for rules with a fix method."""

import os
import re
import shutil
import tempfile
from io import StringIO

import pytest
from click.testing import CliRunner

from sqlfluff.cli.commands import fix, lint


def generic_roundtrip_test(source_file, rulestring):
    """Run a roundtrip test given a sql file and a rule.

    We take a file buffer, lint, fix and lint, finally checking that
    the file fails initially but not after fixing.
    """
    if isinstance(source_file, str):
        # If it's a string, treat it as a path so lets load it.
        with open(source_file) as f:
            source_file = StringIO(f.read())

    filename = "testing.sql"
    # Lets get the path of a file to use
    tempdir_path = tempfile.mkdtemp()
    filepath = os.path.join(tempdir_path, filename)
    # Open the example file and write the content to it
    with open(filepath, mode="w") as dest_file:
        for line in source_file:
            dest_file.write(line)
    runner = CliRunner()
    # Check that we first detect the issue
    result = runner.invoke(lint, ["--rules", rulestring, "--dialect=ansi", filepath])
    assert result.exit_code == 1
    # Fix the file (in force mode)
    result = runner.invoke(
        fix, ["--rules", rulestring, "--dialect=ansi", "-f", filepath]
    )
    assert result.exit_code == 0
    # Now lint the file and check for exceptions
    result = runner.invoke(lint, ["--rules", rulestring, "--dialect=ansi", filepath])
    assert result.exit_code == 0
    shutil.rmtree(tempdir_path)


def jinja_roundtrip_test(
    source_path, rulestring, sqlfile="test.sql", cfgfile=".sqlfluff"
):
    """Run a roundtrip test path and rule.

    We take a file buffer, lint, fix and lint, finally checking that
    the file fails initially but not after fixing. Additionally
    we also check that we haven't messed up the templating tags
    in the process.
    """
    tempdir_path = tempfile.mkdtemp()
    sql_filepath = os.path.join(tempdir_path, sqlfile)
    cfg_filepath = os.path.join(tempdir_path, cfgfile)

    # Copy the SQL file
    with open(sql_filepath, mode="w") as dest_file:
        with open(os.path.join(source_path, sqlfile)) as source_file:
            for line in source_file:
                dest_file.write(line)
    # Copy the Config file
    with open(cfg_filepath, mode="w") as dest_file:
        with open(os.path.join(source_path, cfgfile)) as source_file:
            for line in source_file:
                dest_file.write(line)

    with open(sql_filepath) as f:
        # Get a record of the pre-existing jinja tags
        tags = re.findall(r"{{[^}]*}}|{%[^}%]*%}", f.read(), flags=0)

    runner = CliRunner()
    # Check that we first detect the issue
    result = runner.invoke(
        lint, ["--rules", rulestring, "--dialect=ansi", sql_filepath]
    )
    assert result.exit_code == 1
    # Fix the file (in force mode)
    result = runner.invoke(
        fix, ["--rules", rulestring, "-f", "--dialect=ansi", sql_filepath]
    )
    assert result.exit_code == 0
    # Now lint the file and check for exceptions
    result = runner.invoke(
        lint, ["--rules", rulestring, "--dialect=ansi", sql_filepath]
    )
    if result.exit_code != 0:
        # Output the file content for debugging
        print("File content:")
        with open(sql_filepath) as f:
            print(repr(f.read()))
        print("Command output:")
        print(result.output)
    assert result.exit_code == 0

    with open(sql_filepath) as f:
        # Check that the tags are all still there!
        new_tags = re.findall(r"{{[^}]*}}|{%[^}%]*%}", f.read(), flags=0)

    # Clear up the temp dir
    shutil.rmtree(tempdir_path)

    # Assert that the tags are the same
    assert tags == new_tags


@pytest.mark.parametrize(
    "rule,path",
    [
        ("LT01", "test/fixtures/linter/indentation_errors.sql"),
        ("LT01", "test/fixtures/linter/whitespace_errors.sql"),
        ("LT01", "test/fixtures/linter/indentation_errors.sql"),
        ("CP01", "test/fixtures/linter/whitespace_errors.sql"),
        ("AL01", "test/fixtures/dialects/ansi/select_simple_i.sql"),
        ("AL02", "test/fixtures/dialects/ansi/select_simple_i.sql"),
    ],
)
def test__cli__command__fix(rule, path):
    """Test the round trip of detecting, fixing and then not detecting given rule."""
    generic_roundtrip_test(path, rule)


@pytest.mark.parametrize("rule", ["CP01", "LT01"])
def test__cli__command__fix_templated(rule):
    """Roundtrip test, making sure that we don't drop tags while templating."""
    jinja_roundtrip_test("test/fixtures/templater/jinja_d_roundtrip", rule)
