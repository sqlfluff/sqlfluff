""" The Test file for Chunks """

import subprocess
import configparser

import sqlfluff
from sqlfluff.chunks import PositionedChunk
from sqlfluff.rules.base import RuleViolation, BaseRule
from sqlfluff.cli import format_filename, format_violation, format_violations


def test__cli__filename():
    res = format_filename('blah')
    assert res == "### [blah]: Violations:"


def test__cli__violation():
    """ NB Position is 1 + start_pos """
    c = PositionedChunk('foobarbar', 10, 20, 'context')
    r = BaseRule('A', 'DESC', lambda x: True)
    v = RuleViolation(c, r)
    f = format_violation(v)
    assert f == "L:20|P:11|A| DESC"


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
        'foo': ["L:21|P:3|B| DESC", "L:25|P:2|A| DESC"],
        'bar': ["L:2|P:11|C| DESC"]
    }
    chk2 = []
    for elem in k:
        chk2 = chk2 + [format_filename(elem)] + chk[elem]
    assert f == chk2


def test__cli__shell_directed():
    """ Check the script actually in the shell """
    res = subprocess.check_output(
        ['sqlfluff', 'lint', 'test/fixtures/linter/indentation_error_simple.sql'])
    # Removing \r is important for windows
    check = "L:2|P:1|L003| Single indentation uses a number of spaces not a multiple of 4"
    lines = res.decode().replace("\r", "").split("\n")
    assert check in lines


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
