""" The Test file for Chunks """

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
