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

        message = "Rule {0} expected to find {1} and actually found {2!r}".format(
            self.rule.name,
            self.expected,
            self.found)
        # Call the base class constructor with the parameters it needs
        super(sqlfluffParseError, self).__init__(message)


class BaseSequence(object):
    def __init__(self, *seq):
        self.seq = seq

    def __iter__(self):
        return iter(self.seq)

    def __repr__(self):
        return "<{classname}: {content}>".format(
            classname=self.__class__.__name__,
            content=", ".join(["{0!r}".format(elem) for elem in self]))

    def _match_full_sequence(self, s, rule, pass_stack, dialect):
        # We'll attempt to match each element in order.
        s_buff = s
        node_buff = []
        for elem in self.seq:
            # We'll call recursively to match each element of the list:
            ndl, s_buff = rule._match_sequence(s_buff, elem, pass_stack, dialect=dialect)
            node_buff += ndl
        else:
            # If we manage to successfully loop through the whole pattern
            # without error, then we return the buffers and carry on
            return node_buff, s_buff

    def _match_sequence_multiple(self, s, rule, pass_stack, dialect, min_times=1, max_times=1):
        matches = 0
        s_buff = s
        node_buff = []
        last_err = RuntimeError("This shouldn't happen!")
        while True:
            # Check whether we have enough matches (or if there isn't a limit)
            if (matches >= max_times and max_times != -1):
                break
            try:
                ndl, s_buff = self._match_full_sequence(s_buff, rule, pass_stack, dialect=dialect)
                node_buff += ndl
                matches += 1
            except sqlfluffParseError as err:
                # Store the error in case we want to come back to it
                last_err = err
                break
        if matches >= min_times:
            return node_buff, s_buff
        else:
            # We've broken and don't have the right number of matches...
            raise last_err

    def match(self, s, rule, pass_stack, dialect):
        return self._match_full_sequence(s, rule, pass_stack, dialect=dialect)


class Seq(BaseSequence):
    """ Basically an alias """
    pass


class ZeroOrMore(BaseSequence):
    def match(self, s, rule, pass_stack, dialect):
        return self._match_sequence_multiple(s, rule, pass_stack, dialect=dialect, min_times=0, max_times=-1)


class OneOrMore(BaseSequence):
    def match(self, s, rule, pass_stack, dialect):
        return self._match_sequence_multiple(s, rule, pass_stack, dialect=dialect, min_times=1, max_times=-1)


class ZeroOrOne(BaseSequence):
    def match(self, s, rule, pass_stack, dialect):
        return self._match_sequence_multiple(s, rule, pass_stack, dialect=dialect, min_times=0, max_times=1)


class OneOf(BaseSequence):
    def match(self, s, rule, pass_stack, dialect):
        """ OneOf MAtching is a little different """
        # With a OneOf, we iterate across the items, looking for the first match. If
        # there are no matching options, then raise a parsing error.
        for elem in self.seq:
            try:
                # If we manage to match without throwing an error, then we can just return
                # straight away. If the match fails, then we'll catch the exception and try
                # the next one.
                return rule._match_sequence(s, elem, pass_stack, dialect=dialect)
            except sqlfluffParseError:
                # Any errors, we can ignore for now. We'll raise our own exception
                # if we don't find any matches
                pass
        else:
            # We've iterated through all the options, and not found a match
            # so we should raise an exception.
            raise sqlfluffParseError(rule, self.seq, s)


class Node(object):
    def __init__(self, nodes, rule_stack, name='-'):
        self.nodes = nodes
        self.rule_stack = rule_stack
        self.name = name

    def astuple(self):
        return (self.name, tuple([node.astuple() for node in self.nodes]))

    def fmt(self, indent=0, deep_indent=50):
        line_buff = []
        line_buff.append(('  ' * indent) + self.name + ':')
        for nd in self.nodes:
            line_buff += nd.fmt(indent=indent + 1, deep_indent=deep_indent)
        return line_buff

    def prnt(self, deep_indent=50):
        """ Use for printing the structure of the tree """
        # e.g. print(dialect.prnt())
        return '\n'.join(self.fmt(deep_indent=deep_indent))

    def tokens(self):
        """ Flatten the tree and return a list of token tuples """
        token_buffer = []
        for node in self.nodes:
            token_buffer += node.tokens()
        return token_buffer


class Terminal(object):
    """ Like a node, but has no children """
    def __init__(self, s, token, rule_stack):
        self.s = s
        self.token = token
        self.rule_stack = rule_stack

    def fmt(self, indent=0, deep_indent=50):
        line_buff = []
        line_buff.append(
            ('  ' * indent) + self.token + ':'
            + (' ' * (deep_indent - ((indent * 2) + len(self.token) + 1)))
            + repr(self.s))
        return line_buff

    def astuple(self):
        return (self.token, self.s)

    def tokens(self):
        """ Designed to fit with Node.tokens() """
        return [self.astuple()]


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

    def __repr__(self):
        return "<Dialect: {name}>".format(
            name=self.name)

    def get_rule(self, name):
        if name not in self.rules:
            raise ValueError("Rule {0!r} not found in set of rules provided for dialect {1}".format(name, self.name))
        else:
            return self.rules[name]

    def parse(self, s, rule_stack=None):
        rule = self.get_rule(self.root_rule)
        # Parse and make a tree recursively, passing self as the dialect
        # We should assume there's no existing rule stack, so pass an empty one in
        tree, remainder = rule.parse(s, rule_stack=rule_stack or tuple(), dialect=self)
        return tree, remainder


class Rule(object):
    """ The base class for patterns """
    def __init__(self, name, sequence):
        self.name = name
        # sequence can be any iterable (but the types of the elements are important)
        self.sequence = sequence

    def __repr__(self):
        return "<{classname}: {name!r}>".format(
            classname=self.__class__.__name__,
            name=self.name)

    def _match_sequence(self, s, seq, pass_stack, dialect):
        """ This is an internal method, designed to do the heavy
        lifting of matching sequences. It's also called recursively for
        nested rules. """
        # First we work out what we've been presented with
        # Is it a string? i.e. a reference to a rule?
        if isinstance(seq, six.string_types):
            rule = dialect.get_rule(seq)
            # Assume for now, that it's a compulsory element. If it doesn't
            # match then we'll throw a parse error, which will get caught.
            # So for now. ASSUME that this is successful.
            nd, r = rule.parse(s, pass_stack, dialect=dialect)
            # make the node into a list before returning
            return [nd], r
        # Is it any kind of sequence class?
        elif isinstance(seq, BaseSequence):
            return seq.match(s, rule=self, pass_stack=pass_stack, dialect=dialect)
        else:
            raise RuntimeError("Unknown type found in the sequence {0} {1!r}".format(type(seq), seq))

    def parse(self, s, rule_stack, dialect):
        # Update the pass-through stack
        pass_stack = rule_stack + (self.name,)
        # Create a local variable to keep track of the remaining string
        s_buff = s
        # Create a local buffer for notes
        node_buff = []
        # Find matches (any missing matches will raise an exception)
        node_buff, s_buff = self._match_sequence(s, seq=self.sequence,
                                                 pass_stack=pass_stack, dialect=dialect)
        # Assuming we get this far, spit back out a node
        return Node(node_buff, rule_stack, name=self.name), s_buff


class TerminalRule(Rule):
    """ TerminalRules are just special cases of Rules """
    def __init__(self, pattern, name=None, case_sensitive=False):
        self.name = name or pattern
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
        else:
            # We don't have a match, raise an exception which can be optionally
            # caught further up stream.
            raise sqlfluffParseError(self, self.name, s)
