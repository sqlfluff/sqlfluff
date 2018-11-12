""" The Test file for CLI Formatters """

from sqlfluff.chunks import PositionedChunk
from sqlfluff.rules.base import RuleViolation, BaseRule
from sqlfluff.cli.formatters import format_filename, format_violation, format_violations


def test__cli__formatters__filename_nocol():
    res = format_filename('blahblah', success=True, color=False, verbose=0)
    assert res == "== [blahblah] PASS"


def test__cli__formatters__filename_col():
    res = format_filename('blah', success=False, color=True, verbose=0)
    assert res == "== [\u001b[30;1mblah\u001b[0m] \u001b[31mFAIL\u001b[0m"


def test__cli__formatters__violation():
    """ NB Position is 1 + start_pos """
    c = PositionedChunk('foobarbar', 10, 20, 'context')
    r = BaseRule('A', 'DESC', lambda x: True)
    v = RuleViolation(c, r)
    f = format_violation(v, color=False)
    assert f == "L:  20 | P:  11 | A | DESC"


def test__cli__formatters__violations():
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
    f = format_violations(v, color=False)
    k = sorted(['foo', 'bar'])
    chk = {
        'foo': ["L:  21 | P:   3 | B | DESC", "L:  25 | P:   2 | A | DESC"],
        'bar': ["L:   2 | P:  11 | C | DESC"]
    }
    chk2 = []
    for elem in k:
        chk2 = chk2 + [format_filename(elem, color=False)] + chk[elem]
    assert f == chk2
