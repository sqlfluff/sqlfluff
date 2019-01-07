""" The Test file for CLI Formatters """

import re

from sqlfluff.chunks import PositionedChunk
from sqlfluff.rules.base import RuleViolation, RuleGhost
from sqlfluff.cli.formatters import format_filename, format_violation, format_violations


def escape_ansi(line):
    """ A helper function to remove ANSI color codes """
    ansi_escape = re.compile(u'\u001b\\[[0-9]+(;[0-9]+)?m')
    return ansi_escape.sub('', line)


def test__cli__formatters__filename_nocol():
    res = format_filename('blahblah', success=True, verbose=0)
    assert escape_ansi(res) == "== [blahblah] PASS"


def test__cli__formatters__filename_col():
    """ Explicity test color codes """
    res = format_filename('blah', success=False, verbose=0)
    assert res == u"== [\u001b[30;1mblah\u001b[0m] \u001b[31mFAIL\u001b[0m"


def test__cli__formatters__violation():
    """ NB Position is 1 + start_pos """
    c = PositionedChunk('foobarbar', 10, 20, 'context')
    r = RuleGhost('A', 'DESC')
    v = RuleViolation(c, r, [])
    f = format_violation(v)
    assert escape_ansi(f) == "L:  20 | P:  11 | A | DESC"


def test__cli__formatters__violations():
    # check not just the formatting, but the ordering
    v = {
        'foo': [
            RuleViolation(
                PositionedChunk('blah', 1, 25, 'context'),
                RuleGhost('A', 'DESC'), []),
            RuleViolation(
                PositionedChunk('blah', 2, 21, 'context'),
                RuleGhost('B', 'DESC'), [])],
        'bar': [
            RuleViolation(
                PositionedChunk('blah', 10, 2, 'context'),
                RuleGhost('C', 'DESC'), [])]
    }
    f = format_violations(v)
    k = sorted(['foo', 'bar'])
    chk = {
        'foo': ["L:  21 | P:   3 | B | DESC", "L:  25 | P:   2 | A | DESC"],
        'bar': ["L:   2 | P:  11 | C | DESC"]
    }
    chk2 = []
    for elem in k:
        chk2 = chk2 + [format_filename(elem)] + chk[elem]
    chk2 = '\n'.join(chk2) + '\n'
    assert escape_ansi(f) == escape_ansi(chk2)
