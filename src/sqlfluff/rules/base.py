""" Defines the rule engine class """

from collections import namedtuple

# The ghost of a rule
RuleGhost = namedtuple('RuleGhost', ['code', 'description'])


class RuleViolation(object):
    """ The result of applying a rule to a piece of content and finding a violation """
    def __init__(self, chunk, rule):
        self.chunk = chunk
        self.rule = rule

    def __repr__(self):
        return "<Rule Violation: {rule!r} : {chunk!r}>".format(rule=self.rule, chunk=self.chunk)

    def check_tuple(self):
        return (self.rule.code, self.chunk.line_no, self.chunk.start_pos)


# We have the idea of a rule (the BaseRule or similar) - Here we SUBCLASS BaseRule
# We have the idea of a set of rules (BaseRuleSet) - Here we SUBCLASS BaseRuleSet
# We have an instance of each Rule (which initialises it's memory) - An instance of BaseRule
# We have an instance of a set of rules (which forces each contained Rule to provide an instance)

# The base rule
# Base rules evaluate each chunk in isolation
class BaseRule(object):
    """ A Base Class to dictate Rules, [overwrite this docstring with the description] """
    # These variables should be overwritten by the subclass
    # The docstring is the description
    # The Class Name is the Code

    # The Eval Func (does the rule pass or not?)
    # The function will be passed the chunk and the memory (which is a dict)
    # It should return True or False, True indicates a violation
    @staticmethod
    def eval_func(c, m):
        return False

    # The Memory Func (how should we update the memory on the basis of this chunk)
    # The function will be passed the chunk and the current memory (which is a dict)
    # It should return the new state of the memory (as a dict)
    # NB: The default here means that if no memory required, it can be skipped
    @staticmethod
    def memory_func(c, m):
        return m

    def __init__(self):
        # Just initialise the memory when instantiated
        self.memory = {}

    @property
    def code(self):
        # We use the class name for the code of the exception
        # Subclasses should subclass like: class L001(BaseRule): etc...
        # The actual class name will probably be sqlfluff.rules.base.BaseRule
        # we just want the last portion of that
        return self.__class__.__name__.split('.')[-1]

    @property
    def description(self):
        # We use the docstring for the description
        # Subclasses should subclass like:
        # class L001(BaseRule):
        #     """ <description> """
        return self.__doc__

    def __repr__(self):
        return "<Rule {code}: {description}>".format(code=self.code, description=self.description)

    def ghost(self):
        """ Return a Ghost of this rule """
        return RuleGhost(self.code, self.description)

    def evaluate(self, chunk):
        """ If the function evaluates then we've found a violation """
        # Firstly evaluate whether this chunk is a violation based on the previous memory
        is_violation = self.eval_func(chunk, self.memory)
        # Secondly update the memory based on this chunk and the existing memory
        self.memory = self.memory_func(chunk, self.memory)
        # Then return a violation if one is found
        if is_violation:
            # Return a ghost of this rule
            return RuleViolation(chunk, self.ghost())
        else:
            return None


class BaseRuleSet(object):
    """ A group of rules which can be applied in the same context """
    # This is a base class which should be subclassed to provide a group of rules
    rules = []

    def __init__(self):
        # Instantiate all of our rules afresh
        self._rule_instances = [rule() for rule in self.rules]

    def evaluate(self, chunk):
        buffer = []
        for rule in self._rule_instances:
            violation = rule.evaluate(chunk)
            if violation:
                buffer.append(violation)
        return buffer

    def evaluate_chunkstring(self, chunkstring):
        buffer = []
        for chunk in chunkstring:
            buffer = buffer + self.evaluate(chunk)
        return buffer
