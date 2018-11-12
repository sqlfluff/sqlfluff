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
