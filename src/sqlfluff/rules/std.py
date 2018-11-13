""" Standard set SQL linting of rules """

from .base import BaseRule, BaseRuleSet

# We Could define like this:
# L001 = BaseRule.rule(
#     'L001', "Unnecessary trailing whitespace",
#     lambda c, m: c.context == 'whitespace' and c.chunk[-1] == '\n' and len(c) > 1)


class L004(BaseRule):
    """A file cannot mix tab and space indentation"""

    @staticmethod
    def whitespace_chars(s):
        """ Produce a set of the different whitespace chars in a string """
        chars = [' ', '\t']
        buff = set()
        for c in s:
            if c in chars:
                buff.add(c)
        return buff

    @staticmethod
    def eval_func(c, m):
        if c.context == 'whitespace' and c.start_pos == 0:
            previous_ws_chars = m.get('seen_chars', set())
            ws_chars = L004.whitespace_chars(c.chunk)
            # Check to see if we have seen other characters before
            # which we aren't seeing now, but that we are seeing some now
            # (NB: Don't just cound the number we've seen before)
            # i.e. Seeing whitespace chars AND Other characters seen before
            return len(ws_chars) > 0 and len(previous_ws_chars - ws_chars) > 0
        return False

    @staticmethod
    def memory_func(c, m):
        if c.context == 'whitespace' and c.start_pos == 0:
            previous_ws_chars = m.get('seen_chars', set())
            ws_chars = L004.whitespace_chars(c.chunk)
            return dict(seen_chars=ws_chars | previous_ws_chars)
        else:
            return m


class L005(BaseRule):
    """Commas should not have whitespace directly before them"""

    @staticmethod
    def eval_func(c, m):
        if c.context == 'comma':
            previous_whitespace = m.get('previous_whitespace', False)
            return previous_whitespace

    @staticmethod
    def memory_func(c, m):
        return dict(previous_whitespace=(c.context == 'whitespace'))


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
            lambda c, m: c.context == 'whitespace' and c.start_pos == 0 and c.chunk.count(' ') % 4 != 0),
        # Defined a seperate rules
        L004, L005
    ]
