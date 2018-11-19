""" The Test file for CLI (General) """

import subprocess
import configparser

import sqlfluff


def test__cli__shell_directed():
    """ Check the script actually in the shell """
    try:
        subprocess.check_output(
            ['sqlfluff', 'lint', '-n', 'test/fixtures/linter/indentation_error_simple.sql'])
    except subprocess.CalledProcessError as err:
        # There are violations so there should be a non-zero exit code
        assert err.returncode == 65
        # We should get a readout of what the error was
        check_a = "L:   2 | P:   1 | L003"
        check_b = "Single indentation uses a number of spaces not a multiple of 4"
        assert check_a in err.output.decode()
        assert check_b in err.output.decode()


def test__cli__shell_dialect():
    """ Check the script raises the right exception on an unknown dialect """
    try:
        subprocess.check_output(
            ['sqlfluff', 'lint', '-n', '--dialect', 'faslkjh', 'test/fixtures/linter/indentation_error_simple.sql'])
    except subprocess.CalledProcessError as err:
        # The dialect is unknown should be a non-zero exit code
        assert err.returncode == 66


def test__cli__shell_lint_a():
    """
    Check basic commands on a simple script.
    The subprocess command should exit without erros, as
    no issues should be found.
    """
    # Not verbose
    subprocess.check_output(
        ['sqlfluff', 'lint', '-n', 'test/fixtures/cli/passing_a.sql'])
    # Verbose
    subprocess.check_output(
        ['sqlfluff', 'lint', '-n', '-v', 'test/fixtures/cli/passing_a.sql'])
    # Very Verbose
    subprocess.check_output(
        ['sqlfluff', 'lint', '-n', '-vv', 'test/fixtures/cli/passing_a.sql'])
    # Very Verbose (Colored)
    subprocess.check_output(
        ['sqlfluff', 'lint', '-vv', 'test/fixtures/cli/passing_a.sql'])


def test__cli__shell_lint_b():
    """
    Check basic commands on a more complicated script.
    The subprocess command should exit without erros, as
    no issues should be found.
    """
    subprocess.check_output(
        ['sqlfluff', 'lint', '-n', 'test/fixtures/cli/passing_b.sql'])


def test__cli__shell_lint_c_rules_single():
    """
    Check that only checking for a single specific rule using the cli works.
    The subprocess command should exit without erros, as
    no issues should be found.
    """
    subprocess.check_output(
        ['sqlfluff', 'lint', '-n', '--rules', 'L001', 'test/fixtures/linter/operator_errors.sql'])


def test__cli__shell_lint_c_rules_multi():
    """
    Check that only checking for multiple specific rules using the cli works.
    The subprocess command should exit without erros, as
    no issues should be found.
    """
    subprocess.check_output(
        ['sqlfluff', 'lint', '-n', '--rules', 'L001,L002', 'test/fixtures/linter/operator_errors.sql'])


def test__cli__versioning():
    # Get the package version info
    pkg_version = sqlfluff.__version__
    # Get the version info from the config file
    config = configparser.ConfigParser()
    config.read_file(open('src/sqlfluff/config.ini'))
    config_version = config['sqlfluff']['version']
    assert pkg_version == config_version
    # Get the version from the cli
    cli_version = subprocess.check_output(
        ['sqlfluff', 'version'])
    # We need to strip to remove the newline characters, decode for python27
    assert cli_version.decode().strip() == pkg_version


def test__cli__shell_version():
    """ Just check version command for exceptions """
    subprocess.check_output(
        ['sqlfluff', 'version'])
    # Check a verbose version
    subprocess.check_output(
        ['sqlfluff', 'version', '-v'])


def test__cli__shell_rules():
    """ Just check rules command for exceptions """
    subprocess.check_output(
        ['sqlfluff', 'rules'])
