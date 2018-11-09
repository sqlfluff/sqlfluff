""" The Test file for Chunks """

import subprocess
import configparser

import sqlfluff
from sqlfluff.chunks import PositionedChunk
from sqlfluff.rules.base import RuleViolation, BaseRule
from sqlfluff.cli import format_filename, format_violation, format_violations


def test__cli__filename():
    res = format_filename('blah')
    assert res == "== [\u001b[30;1mblah\u001b[0m] \u001b[31mFAIL\u001b[0m"


def test__cli__filename_success():
    res = format_filename('blah', success=True)
    assert res == "== [\u001b[30;1mblah\u001b[0m] \u001b[32mPASS\u001b[0m"


def test__cli__violation():
    """ NB Position is 1 + start_pos """
    c = PositionedChunk('foobarbar', 10, 20, 'context')
    r = BaseRule('A', 'DESC', lambda x: True)
    v = RuleViolation(c, r)
    f = format_violation(v)
    assert f == "\u001b[36mL:  20 | P:  11 | A |\u001b[0m DESC"


def test__cli__violations():
    # check not just the formatting, but the ordering
    v = {
        'foo': [
            RuleViolation(
                PositionedChunk('blah', 1, 25, 'context'),
                BaseRule('A', 'DESC', None)),
            RuleViolation(
                PositionedChunk('blah', 2, 21, 'context'),
                BaseRule('B', 'DESC', None))],
        'bar': [
            RuleViolation(
                PositionedChunk('blah', 10, 2, 'context'),
                BaseRule('C', 'DESC', None))]
    }
    f = format_violations(v)
    k = sorted(['foo', 'bar'])
    chk = {
        'foo': ["\u001b[36mL:  21 | P:   3 | B |\u001b[0m DESC", "\u001b[36mL:  25 | P:   2 | A |\u001b[0m DESC"],
        'bar': ["\u001b[36mL:   2 | P:  11 | C |\u001b[0m DESC"]
    }
    chk2 = []
    for elem in k:
        chk2 = chk2 + [format_filename(elem)] + chk[elem]
    assert f == chk2


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
