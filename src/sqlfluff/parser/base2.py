""" This is a rewrite of the parser from the ground up """

import re
import six


class sqlfluffParseError(Exception):
    def __init__(self, rule, expected, found):
        self.rule = rule
        self.expected = expected
        self.found = found[:16]
        if len(found[16:]) > 0:
            self.found += '...'

        message = "Rule {0} expected to find {1} and actually found {2}".format(
            self.rule.name,
            self.expected,
            self.found)
        # Call the base class constructor with the parameters it needs
        super(sqlfluffParseError, self).__init__(message)


class Node(object):
    def __init__(self, nodes, rule_stack, complete=False):
        self.nodes = nodes
        self.rule_stack = rule_stack
        # This will get set to true when it's fully parsed
        self.complete = complete


class Terminal(object):
    """ Like a node, but has no children """
    def __init__(self, s, token, rule_stack):
        self.s = s
        self.token = token
        self.rule_stack = rule_stack


class Dialect(object):
    """ A dialect is a collection of rules """
    def __init__(self, name, root_rule, rules):
        self.name = name
        self.root_rule = root_rule
        # Populate the rule set
        self.rules = {}
        for rule in rules:
            if rule.name in self.rules:
                raise ValueError("Rule with name {0!r} already exists in dialect {1}!".format(rule.name, self.name))
            else:
                self.rules[rule.name] = rule
        # Check that the root rule is accessible (raise expection if not)
        self.get_rule(self.root_rule)

    def get_rule(self, name):
        if name not in self.rules:
            raise ValueError("Rule {0!r} not found in set of rules provided for dialect {1}".format(name, self.name))
        else:
            return self.rules[name]

    def parse(self, s):
        rule = self.get_rule(self.root_rule)
        # Parse and make a tree recursively, passing self as the dialect
        tree, remainder = rule.parse(s, dialect=self)
        return tree, remainder


class Rule(object):
    """ The base class for patterns """
    def __init__(self, name, sequence):
        self.name = name
        # sequence can be any iterable (but the types of the elements are important)
        self.sequence = sequence

    def parse(self, s, dialect):
        # Run through the elements of the sequence in order
        for elem in self.sequence:
            # Could create subrules here?

            # Is it a compulsary rule reference?
            if isinstance(elem, six.string_types):
                rule = dialect.get_rule(elem)
                raise RuntimeError(rule)


class TerminalRule(Rule):
    """ TerminalRules are just special cases of Rules """
    def __init__(self, name, pattern, case_sensitive=False):
        self.name = name
        # Precompile the pattern
        if case_sensitive:
            self.pattern = re.compile(pattern)
        else:
            self.pattern = re.compile(pattern, re.IGNORECASE)

    def parse(self, s, rule_stack, dialect):
        """ NB: Same interface as for rules """
        m = self.pattern.match(s)
        if m:
            last_pos = m.end()
            return Terminal(s[:last_pos], self.name, rule_stack), s[last_pos:]
        return None, s
