"""Round trip tests for rules with a fix method."""

import tempfile
import os
import shutil
import re
import pytest

from click.testing import CliRunner

from sqlfluff.cli.commands import lint, fix


def generic_roundtrip_test(source_file, rulestring):
    """Run a roundtrip test given a sql file and a rule.

    We take a file buffer, lint, fix and lint, finally checking that
    the file fails initially but not after fixing.
    """
    filename = 'tesing.sql'
    # Lets get the path of a file to use
    tempdir_path = tempfile.mkdtemp()
    filepath = os.path.join(tempdir_path, filename)
    # Open the example file and write the content to it
    with open(filepath, mode='w') as dest_file:
        for line in source_file:
            dest_file.write(line)
    runner = CliRunner()
    # Check that we first detect the issue
    result = runner.invoke(lint, ['--rules', rulestring, filepath])
    assert result.exit_code == 65
    # Fix the file (in force mode)
    result = runner.invoke(fix, ['--rules', rulestring, '-f', filepath])
    assert result.exit_code == 0
    # Now lint the file and check for exceptions
    result = runner.invoke(lint, ['--rules', rulestring, filepath])
    assert result.exit_code == 0
    shutil.rmtree(tempdir_path)


def jinja_roundtrip_test(source_path, rulestring, sqlfile='test.sql', cfgfile='.sqlfluff'):
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
    with open(sql_filepath, mode='w') as dest_file:
        with open(os.path.join(source_path, sqlfile), mode='r') as source_file:
            for line in source_file:
                dest_file.write(line)
    # Copy the Config file
    with open(cfg_filepath, mode='w') as dest_file:
        with open(os.path.join(source_path, cfgfile), mode='r') as source_file:
            for line in source_file:
                dest_file.write(line)

    with open(sql_filepath, mode='r') as f:
        # Get a record of the pre-existing jinja tags
        tags = re.findall(r"{{[^}]*}}|{%[^}%]*%}", f.read(), flags=0)

    runner = CliRunner()
    # Check that we first detect the issue
    result = runner.invoke(lint, ['--rules', rulestring, sql_filepath])
    assert result.exit_code == 65
    # Fix the file (in force mode)
    result = runner.invoke(fix, ['--rules', rulestring, '-f', sql_filepath])
    assert result.exit_code == 0
    # Now lint the file and check for exceptions
    result = runner.invoke(lint, ['--rules', rulestring, sql_filepath])
    assert result.exit_code == 0

    with open(sql_filepath, mode='r') as f:
        # Check that the tags are all still there!
        new_tags = re.findall(r"{{[^}]*}}|{%[^}%]*%}", f.read(), flags=0)

    # Clear up the temp dir
    shutil.rmtree(tempdir_path)

    # Assert that the tags are the same
    assert tags == new_tags


def test__cli__command__fix_L001():
    """Test the round trip of detecting, fixing and then not detecting rule L001."""
    with open('test/fixtures/linter/indentation_errors.sql', mode='r') as f:
        generic_roundtrip_test(f, 'L001')


def test__cli__command__fix_L008_a():
    """Test the round trip of detecting, fixing and then not detecting rule L008."""
    with open('test/fixtures/linter/whitespace_errors.sql', mode='r') as f:
        generic_roundtrip_test(f, 'L008')


def test__cli__command__fix_L008_b():
    """Test the round trip of detecting, fixing and then not detecting rule L008."""
    with open('test/fixtures/linter/indentation_errors.sql', mode='r') as f:
        generic_roundtrip_test(f, 'L008')


def test__cli__command__fix_L010():
    """Test the round trip of detecting, fixing and then not detecting rule L008."""
    with open('test/fixtures/linter/whitespace_errors.sql', mode='r') as f:
        generic_roundtrip_test(f, 'L010')


@pytest.mark.parametrize("rule", ["L010", "L001"])
def test__cli__command__fix_templated(rule):
    """Roundtrip test, making sure that we don't drop tags while templating."""
    jinja_roundtrip_test('test/fixtures/templater/jinja_d_roundtrip', rule)
