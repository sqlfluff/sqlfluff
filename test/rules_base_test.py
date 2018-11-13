""" The Test file for SQLFluff """

from sqlfluff.rules.base import BaseRule, BaseRuleSet, RuleViolation
from sqlfluff.chunks import PositionedChunk, ChunkString


# Create Directly
class TRuleA(BaseRule):
    """foo"""
    @staticmethod
    def eval_func(c, m):
        return True


# Create Using the Sugar
TRuleB = BaseRule.rule('TRuleB', "NA", lambda c, m: c % 6 == 0)


class TRuleSet(BaseRuleSet):
    rules = [TRuleA, BaseRule.rule('TRuleC', "bar", lambda c, m: False)]


# ############## BASE RULES TESTS
def test__rules__base__baserule_a():
    r = TRuleA()
    assert isinstance(r.evaluate(None), RuleViolation)


def test__rules__base__baserule_b():
    r = TRuleB()
    assert r.description == 'NA'
    assert isinstance(r.evaluate(36), RuleViolation)
    assert r.evaluate(36).chunk == 36
    assert r.evaluate(36).rule == r.ghost()
    assert r.evaluate(37) is None


def test__rules__base__ruleset():
    rs = TRuleSet()
    vs = rs.evaluate(1)
    assert len(vs) == 1
    assert vs[0].rule.code == 'TRuleA'


def test__rules__base__ruleset_lookup_class():
    rl = TRuleSet.code_lookup('blah')
    assert rl is None
    rl = TRuleSet.code_lookup('TRuleA')
    assert rl == TRuleA


def test__rules__base__ruleset_lookup_inst():
    rl = TRuleSet().code_lookup('blah')
    assert rl is None
    # Even when instantiated, it should still return the class
    rl = TRuleSet().code_lookup('TRuleA')
    assert rl == TRuleA


def test__rules__base__ruleset_chunkstring():
    """ An extension of the above test, but applied to a chunkstring """
    rs = TRuleSet()
    cs = ChunkString(
        PositionedChunk('foo', 1, 20, 'a'),
        PositionedChunk('bar', 1, 21, 'b')
    )
    vs = rs.evaluate_chunkstring(cs)
    # We should get two instances of rule A
    assert len(vs) == 2
    assert vs[0].rule.code == 'TRuleA'
    assert vs[0].chunk.chunk == 'foo'
    assert vs[1].rule.code == 'TRuleA'
    assert vs[1].chunk.chunk == 'bar'


# ############ Violations test
def test__rules__base__violation_tuple():
    r = TRuleA()
    v = r.evaluate(PositionedChunk('foo', 1, 20, 'a'))
    t = v.check_tuple()
    assert t == ('TRuleA', 20, 1)
