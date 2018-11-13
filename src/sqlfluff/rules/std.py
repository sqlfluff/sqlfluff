""" Standard set SQL linting of rules """

from .base import BaseRule, BaseRuleSet


class L001(BaseRule):
    """ Unnecessary trailing whitespace """
    @staticmethod
    def eval_func(c, m):
        return c.context == 'whitespace' and c.chunk[-1] == '\n' and len(c) > 1


class L002(BaseRule):
    """ Single indentation uses mixture of tabs and spaces """
    @staticmethod
    def eval_func(c, m):
        return c.context == 'whitespace' and c.start_pos == 0 and ' ' in c.chunk and '\t' in c.chunk


class L003(BaseRule):
    """ Single indentation uses a number of spaces not a multiple of 4 """
    @staticmethod
    def eval_func(c, m):
        return c.context == 'whitespace' and c.start_pos == 0 and c.chunk.count(' ') % 4 != 0


class StandardRuleSet(BaseRuleSet):
    """ A standard set of SQL rules """
    rules = [L001, L002, L003]
