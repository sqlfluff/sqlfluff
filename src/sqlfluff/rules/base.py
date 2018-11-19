""" Defines the rule engine class """

from collections import namedtuple

from ..chunks import PositionedCorrection

# The ghost of a rule
RuleGhost = namedtuple('RuleGhost', ['code', 'description'])


# Subclass property to create a ClassProperty
#   This enables the definition mechanism for rules
# https://stackoverflow.com/questions/128573/using-property-on-classmethods
class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class RuleViolation(namedtuple('ProtoViolation', ['chunk', 'rule', 'corrections'])):
    """ The result of applying a rule to a piece of content and finding a violation """
    __slots__ = ()

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

    # We provide a configurable init value for m
    init_m = {}

    # The Eval Func (does the rule pass or not?)
    # The function will be passed the chunk and the memory (which is a dict)
    # It should return True or False, True indicates a violation
    @staticmethod
    def eval_func(c, m):
        return False

    # The Memory Func (how should we update the memory on the basis of this chunk)
    # The function will be passed the chunk and the current memory (which is probably a dict)
    # It should return the new state of the memory (as a dict)
    # NB: The default here means that if no memory required, it can be skipped
    @staticmethod
    def memory_func(c, m):
        return m

    # The default correction func, returns a blank list.
    # If there were corrections, it will return a list of corrected chunks
    @staticmethod
    def correction_func(c, m):
        return []

    def __init__(self):
        # Just initialise the memory when instantiated
        self.memory = self.init_m

    @ClassProperty
    @classmethod
    def code(cls):
        # We use the class name for the code of the exception
        # Subclasses should subclass like: class L001(BaseRule): etc...
        # The actual class name will probably be sqlfluff.rules.base.BaseRule
        # we just want the last portion of that
        return cls.__name__.split('.')[-1]

    @ClassProperty
    @classmethod
    def description(cls):
        # We use the docstring for the description
        # Subclasses should subclass like:
        # class L001(BaseRule):
        #     """ <description> """
        return cls.__doc__

    @classmethod
    def rule(cls, code, description, eval_func, memory_func=None, correction_func=None):
        """
        Syntactic sugar to create subclassed rules with less typing.

        L999 = BaseRule.rule('L999', 'foo', func)

        ... is equivalent to ...

        class L999(BaseRule):
            '''foo'''
            @staticmethod
            def eval_func(c, m):
                return func(c, m)
        """
        return type(
            code, (cls,),
            dict(
                eval_func=staticmethod(eval_func),
                # If one has been provided use it, but otherwise use the default
                memory_func=staticmethod(memory_func or cls.memory_func),
                correction_func=staticmethod(correction_func or cls.correction_func),
                __doc__=description
            )
        )

    def __repr__(self):
        return "<Rule {code}: {description}>".format(code=self.code, description=self.description)

    def ghost(self):
        """ Return a Ghost of this rule """
        return RuleGhost(self.code, self.description)

    def evaluate(self, chunk):
        """ If the function evaluates then we've found a violation """
        # Firstly evaluate whether this chunk is a violation based on the previous memory
        resp = self.eval_func(chunk, self.memory)
        # If the result is boolean, assume it's about this chunk, otherwise optionally
        # accept a specific chunk back which is being flagged (as defined by having a chunk attribute)
        if hasattr(resp, 'chunk'):
            # it looks like a chunk
            return_chunk = resp
            is_violation = True
        else:
            return_chunk = chunk
            if resp:
                is_violation = True
            else:
                is_violation = False
        # Evaluate any corrections (before updating the memory, because we need to to be the same)
        if is_violation:
            corrections = self.correction_func(chunk, self.memory)
            if isinstance(corrections, PositionedCorrection):
                corrections = [corrections]
        else:
            corrections = []
        # Make sure all the corrections are actaually corrections
        if any([not isinstance(c, PositionedCorrection) for c in corrections]):
            raise TypeError(
                "A rule has returned something other than a correction chunk! [Rule: {0}]".format(
                    self.code))

        # Secondly update the memory based on this chunk and the existing memory
        self.memory = self.memory_func(chunk, self.memory)
        # Then return a violation if one is found
        if is_violation:
            # Return a ghost of this rule
            return RuleViolation(return_chunk, self.ghost(), corrections)
        else:
            return None


class BaseRuleSet(object):
    """ A group of rules which can be applied in the same context """
    # This is a base class which should be subclassed to provide a group of rules
    rules = []

    def __init__(self):
        # Instantiate all of our rules afresh
        self._rule_instances = [rule() for rule in self.rules]

    def evaluate(self, chunk, rule_whitelist=None):
        buffer = []
        for rule in self._rule_instances:
            if rule_whitelist is None or rule.code in rule_whitelist:
                violation = rule.evaluate(chunk)
                if violation:
                    buffer.append(violation)
        return buffer

    def evaluate_chunkstring(self, chunkstring, rule_whitelist=None):
        buffer = []
        for chunk in chunkstring:
            buffer = buffer + self.evaluate(chunk, rule_whitelist=rule_whitelist)
        return buffer

    @classmethod
    def code_lookup(cls, code):
        for rule in cls.rules:
            if rule.__name__ == code:
                return rule
        else:
            return None

    @classmethod
    def rule_tuples(cls):
        """ Return rule tuples, can be called from instance or class """
        rule_dict = {rule.code: rule.description for rule in cls.rules}
        rule_tuples = [(code, rule_dict[code]) for code in sorted(rule_dict.keys())]
        return rule_tuples
