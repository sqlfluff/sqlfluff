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
            previous_chunk = m.get('previous_chunk', None)
            if previous_chunk:
                if previous_chunk.context == 'whitespace':
                    if '\n' in previous_chunk.chunk:
                        return c
                    else:
                        return previous_chunk
        return False

    @staticmethod
    def memory_func(c, m):
        return dict(
            previous_chunk=c)


class L006(BaseRule):
    """Operators should be surrounded by a single space unless at the start/end of a line"""

    # Initialise the memory with a dict
    init_m = dict(cm3=None, cm2=None, cm1=None)

    @staticmethod
    def eval_func(c, m):
        cm1 = m['cm1']
        if cm1:
            context_m1 = cm1.context
            if context_m1 == 'operator':
                # The last chunk was an operator
                # This is where the operator should kick in

                # First check preceeding whitespace
                cm2 = m['cm2']
                if cm2:
                    if cm2.context == 'whitespace':
                        # it is whitespace (good)
                        # check length and indentation (more than 1 allowed if it's an indent)
                        if len(cm2.chunk) != 1 and cm2.start_pos != 0:
                            # Preceeding whitespace is wrong length
                            return cm1
                    else:
                        # Check for the allowed exception of a star in brackets
                        if cm1.chunk == '*' and cm2.chunk == '(' and c.chunk == ')':
                            return False
                        # Preceeding content is not whitespace
                        return cm1

                # Second check following whitespace
                if c.context == 'whitespace':
                    # it is whitespace (good)
                    # check length
                    if len(c.chunk) != 1:
                        # Following whitespace is wrong length
                        return cm1
                else:
                    # Following content is not whitespace
                    return cm1
        return False

    @staticmethod
    def memory_func(c, m):
        # Here we want to keep a buffer of the previous 3 chunks.
        # Entering this function, we want to first rotate the old ones
        # and then add the new ones
        return dict(
            cm3=m.get('cm2', None),
            cm2=m.get('cm1', None),
            cm1=c)


class L007(L006):
    """Operators should be at the start of lines rather than the end"""

    # This class is very similar to L006, but only check if an operator is followed by a newline
    @staticmethod
    def eval_func(c, m):
        cm1 = m['cm1']
        if cm1:
            context_m1 = cm1.context
            if context_m1 == 'operator':
                # The last chunk was an operator
                # This is where the operator should kick in

                # Second check following whitespace
                if '\n' in c.chunk:
                    # Following whitespace contains a newline
                    return cm1
        return False


class L008(BaseRule):
    """Commas should be followed by a single whitespace, unless followed by a comment"""

    @staticmethod
    def eval_func(c, m):
        cm1 = m.get('cm1', None)
        cm2 = m.get('cm2', None)
        if cm1 and cm2:
            if cm2.context == 'comma':
                if cm1.context != 'whitespace':
                    return cm1
                # Look for single whitespace, but allow this if it's followed by a comment
                elif cm1.chunk not in ['\n', ' '] and c.context != 'comment':
                    return cm1
        return False

    @staticmethod
    def correction_func(c, m):
        cm1 = m.get('cm1', None)
        if cm1.context != 'whitespace':
            # Just add some whitespace
            return cm1.correct(' ' + cm1.chunk)
        else:
            # It is whitespace, just the wrong amount
            if '\n' in cm1.chunk:
                return cm1.correct('\n')
            else:
                return cm1.correct(' ')

    @staticmethod
    def memory_func(c, m):
        # Store the last three chunks
        return dict(
            cm2=m.get('cm1', None),
            cm1=c)


class StandardRuleSet(BaseRuleSet):
    """ A standard set of SQL rules """
    rules = [
        BaseRule.rule(
            'L001', "Unnecessary trailing whitespace",
            lambda c, m: c.context == 'whitespace' and c.chunk[-1] == '\n' and len(c) > 1,
            # Correction Func, just trim the whitespace
            correction_func=(lambda c, m: c.correct('\n'))),
        BaseRule.rule(
            'L002', "Single indentation uses mixture of tabs and spaces",
            lambda c, m: c.context == 'whitespace' and c.start_pos == 0 and ' ' in c.chunk and '\t' in c.chunk),
        BaseRule.rule(
            'L003', "Single indentation uses a number of spaces not a multiple of 4",
            lambda c, m: c.context == 'whitespace' and c.start_pos == 0 and c.chunk.count(' ') % 4 != 0),
        # Defined a seperate rules
        L004, L005, L006, L007, L008
    ]
