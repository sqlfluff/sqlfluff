""" Standard set SQL linting of rules """

from .base import BaseRule, BaseRuleSet


def load_standard_set():
    rs = BaseRuleSet(
        # Layout rules
        BaseRule('L001', 'Unnecessary trailing whitespace',
                 lambda c: c.context == 'whitespace' and c.chunk[-1] == '\n' and len(c) > 1),
        BaseRule('L002', 'Single indentation uses mixture of tabs and spaces',
                 lambda c: c.context == 'whitespace' and c.start_pos == 0 and ' ' in c.chunk and '\t' in c.chunk),
        BaseRule('L003', 'Single indentation uses a number of spaces not a multiple of 4',
                 lambda c: c.context == 'whitespace' and c.start_pos == 0 and c.chunk.count(' ') % 4 != 0)
    )
    return rs
