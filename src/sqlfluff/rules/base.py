""" Defines the rule engine class """


class RuleViolation(object):
    """ The result of applying a rule to a piece of content and finding a violation """
    def __init__(self, chunk, rule):
        self.chunk = chunk
        self.rule = rule

    def __repr__(self):
        return "<Rule Violation: {rule!r} : {chunk!r}>".format(rule=self.rule, chunk=self.chunk)

    def check_tuple(self):
        return (self.rule.code, self.chunk.line_no, self.chunk.start_pos)


class BaseRule(object):
    """ A single linting rule to apply """
    def __init__(self, code, description, func):
        self.code = code
        self.description = description
        self.func = func

    def __repr__(self):
        return "<Rule {code}: {description}>".format(code=self.code, description=self.description)

    def evaluate(self, chunk):
        """ If the function evaluates then we've found a violation """
        if self.func(chunk):
            return RuleViolation(chunk, self)
        else:
            return None


class BaseRuleSet(object):
    """ A group of rules which can be applied in the same context """
    def __init__(self, *rules):
        self._rules = rules

    def evaluate(self, chunk):
        buffer = []
        for rule in self._rules:
            violation = rule.evaluate(chunk)
            if violation:
                buffer.append(violation)
        return buffer

    def evaluate_chunkstring(self, chunkstring):
        buffer = []
        for chunk in chunkstring:
            buffer = buffer + self.evaluate(chunk)
        return buffer


class BaseRuleEngine(object):
    """ The class which enables the application of of rules to a context """
    pass
