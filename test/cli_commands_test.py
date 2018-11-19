""" The Test file for CLI (General) """

import configparser
import tempfile
import os
import shutil

from click.testing import CliRunner

import sqlfluff
from sqlfluff.cli.commands import lint, version, rules, fix


def test__cli__command_directed():
    """ Basic checking of lint functionality """
    runner = CliRunner()
    result = runner.invoke(lint, ['-n', 'test/fixtures/linter/indentation_error_simple.sql'])
    assert result.exit_code == 65
    # We should get a readout of what the error was
    check_a = "L:   2 | P:   1 | L003"
    check_b = "Single indentation uses a number of spaces not a multiple of 4"
    assert check_a in result.output
    assert check_b in result.output


def test__cli__command_dialect():
    """ Check the script raises the right exception on an unknown dialect """
    runner = CliRunner()
    result = runner.invoke(lint, ['-n', '--dialect', 'faslkjh', 'test/fixtures/linter/indentation_error_simple.sql'])
    # The dialect is unknown should be a non-zero exit code
    assert result.exit_code == 66


def test__cli__command_lint_a():
    """
    Check basic commands on a simple script.
    The subprocess command should exit without erros, as
    no issues should be found.
    """
    runner = CliRunner()
    # Not verbose
    result = runner.invoke(lint, ['-n', 'test/fixtures/cli/passing_a.sql'])
    assert result.exit_code == 0
    # Verbose
    result = runner.invoke(lint, ['-n', '-v', 'test/fixtures/cli/passing_a.sql'])
    assert result.exit_code == 0
    # Very Verbose
    result = runner.invoke(lint, ['-n', '-vv', 'test/fixtures/cli/passing_a.sql'])
    assert result.exit_code == 0
    # Very Verbose (Colored)
    result = runner.invoke(lint, ['-vv', 'test/fixtures/cli/passing_a.sql'])
    assert result.exit_code == 0


def test__cli__command_lint_b():
    """
    Check basic commands on a more complicated script.
    The subprocess command should exit without errors, as
    no issues should be found.
    """
    runner = CliRunner()
    result = runner.invoke(lint, ['-n', 'test/fixtures/cli/passing_b.sql'])
    assert result.exit_code == 0


def test__cli__command_lint_c_rules_single():
    """
    Check that only checking for a single specific rule using the cli works.
    The subprocess command should exit without erros, as
    no issues should be found.
    """
    runner = CliRunner()
    result = runner.invoke(lint, ['-n', '--rules', 'L001', 'test/fixtures/linter/operator_errors.sql'])
    assert result.exit_code == 0


def test__cli__command_lint_c_rules_multi():
    """
    Check that only checking for multiple specific rules using the cli works.
    The subprocess command should exit without erros, as
    no issues should be found.
    """
    runner = CliRunner()
    result = runner.invoke(lint, ['-n', '--rules', 'L001,L002', 'test/fixtures/linter/operator_errors.sql'])
    assert result.exit_code == 0


def test__cli__command_versioning():
    # Get the package version info
    pkg_version = sqlfluff.__version__
    # Get the version info from the config file
    config = configparser.ConfigParser()
    config.read_file(open('src/sqlfluff/config.ini'))
    config_version = config['sqlfluff']['version']
    assert pkg_version == config_version
    # Get the version from the cli
    runner = CliRunner()
    result = runner.invoke(version)
    assert result.exit_code == 0
    # We need to strip to remove the newline characters
    assert result.output.strip() == pkg_version


def test__cli__command_version():
    """ Just check version command for exceptions """
    # Get the package version info
    pkg_version = sqlfluff.__version__
    runner = CliRunner()
    result = runner.invoke(version)
    assert result.exit_code == 0
    assert pkg_version in result.output
    # Check a verbose version
    result = runner.invoke(version, ['-v'])
    assert result.exit_code == 0
    assert pkg_version in result.output


def test__cli__command_rules():
    """ Just check rules command for exceptions """
    runner = CliRunner()
    result = runner.invoke(rules)
    assert result.exit_code == 0


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
