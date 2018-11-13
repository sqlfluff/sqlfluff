""" Standard set SQL linting of rules """

from .base import BaseRule, BaseRuleSet

# We Could define like this:
# L001 = BaseRule.rule(
#     'L001', "Unnecessary trailing whitespace",
#     lambda c, m: c.context == 'whitespace' and c.chunk[-1] == '\n' and len(c) > 1)


class StandardRuleSet(BaseRuleSet):
    """ A standard set of SQL rules """
    rules = [
        BaseRule.rule(
            'L001', "Unnecessary trailing whitespace",
            lambda c, m: c.context == 'whitespace' and c.chunk[-1] == '\n' and len(c) > 1),
        BaseRule.rule(
            'L002', "Single indentation uses mixture of tabs and spaces",
            lambda c, m: c.context == 'whitespace' and c.start_pos == 0 and ' ' in c.chunk and '\t' in c.chunk),
        BaseRule.rule(
            'L003', "Single indentation uses a number of spaces not a multiple of 4",
            lambda c, m: c.context == 'whitespace' and c.start_pos == 0 and c.chunk.count(' ') % 4 != 0)
    ]
