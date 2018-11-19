""" The Test file for CLI (General) """

import tempfile
import os
import shutil

from click.testing import CliRunner

from sqlfluff.cli.commands import lint, fix


def generic_roundtrip_test(source_file, rulestring):
    """ A test for roundtrip testing, take a file buffer, lint, fix and lint """
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


def test__cli__command__fix_L001():
    """ Test the round trip of detecting, fixing and then not detecting rule L001 """
    with open('test/fixtures/linter/indentation_errors.sql', mode='r') as f:
        generic_roundtrip_test(f, 'L001')


def test__cli__command__fix_L008_a():
    """ Test the round trip of detecting, fixing and then not detecting rule L001 """
    with open('test/fixtures/linter/whitespace_errors.sql', mode='r') as f:
        generic_roundtrip_test(f, 'L008')


def test__cli__command__fix_L008_b():
    """ Test the round trip of detecting, fixing and then not detecting rule L001 """
    with open('test/fixtures/linter/indentation_errors.sql', mode='r') as f:
        generic_roundtrip_test(f, 'L008')
