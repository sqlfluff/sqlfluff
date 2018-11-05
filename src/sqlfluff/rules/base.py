""" Defines the rule engine class """


class RuleViolation(object):
    """ The result of applying a rule to a piece of content and finding a violation """
    def __init__(self, chunk, rule):
        self.chunk = chunk
        self.rule = rule


class BaseRule(object):
    """ A single linting rule to apply """
    def __init__(self, code, description, func):
        self.code = code
        self.description = description
        self.func = func

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


class BaseRuleEngine(object):
    """ The class which enables the application of of rules to a context """
    pass
