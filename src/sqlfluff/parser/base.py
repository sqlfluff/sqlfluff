""" This is a rewrite of the parser from the ground up """

import re
import six
import logging
import itertools


# ###############
# ## EXCEPTIONS
# ###############
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


# ###############
# ## SEQUENCES
# ###############
class BaseSequence(object):
    def __init__(self, *seq, nsj=True):
        self.seq = seq
        self.allow_nsj = nsj

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
        # When considering NSJ, they can only come BETWEEN elements. Not at the start or end.
        # Limiting it to not the start is done by only allowing the path if there's already something
        # in the node_buff. Limiting at the end is done by not allowing a route out except via
        # the node match path.
        for elem in self.seq:
            # We'll call recursively to match each element of the list.
            # We look for NSJ first (if we've already matched something),
            # so that any optional elements work as expected.
            # Failing to match will raise an exception which we'll raise
            # and pass upward. BEFORE we do that however, we need to
            # provide an option to match an NSJ instead.
            while True:
                # We loop so that we get multiple attempts
                logging.debug(
                    ("->" * len(pass_stack)) + " "
                    + "{cls}._m_f_s - loop: {ndl!r}".format(
                        cls=self.__class__.__name__, ndl=node_buff))

                # Be greedy and first check for NSJs (if we're already in the sequence and it's allowed)
                if dialect.join_rule and len(node_buff) > 0 and self.allow_nsj:
                    nsj_rule = dialect.get_rule(dialect.join_rule)
                    try:
                        nd, s_buff = nsj_rule.parse(s_buff, pass_stack, dialect=dialect)
                        node_buff += [nd]
                        # we carry on from here, back into the loop for another crack at the main element or another NSJ.
                    except sqlfluffParseError:
                        # We didn't match an NSJ, carry on, no biggie
                        pass

                try:
                    ndl, s_buff = rule._match_sequence(s_buff, elem, pass_stack, dialect=dialect)
                    node_buff += ndl
                    # Break so that we move on an try the next element
                    break
                except sqlfluffParseError as err:
                    # We've failed to match the primary target at this point. Raise the error.
                    # NSJs have already been tested.
                    raise err
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

    def _match(self, s, rule, pass_stack, dialect):
        return self._match_full_sequence(s, rule, pass_stack, dialect=dialect)

    def match(self, s, rule, pass_stack, dialect):
        """ A wrapper around _match, to assist with logging """
        logging.debug(
            ("->" * len(pass_stack)) + " "
            + "{cls}.match(seq={seq!r}, s={s!r}) - begin...".format(
                cls=self.__class__.__name__, seq=self.seq, s=s))
        try:
            ndl, r = self._match(s, rule, pass_stack, dialect=dialect)
        except sqlfluffParseError as err:
            logging.debug(
                ("->" * len(pass_stack)) + " "
                + "{cls}.match(seq={seq!r}, s={s!r}) - fail".format(
                    cls=self.__class__.__name__, seq=self.seq, s=s))
            raise err
        logging.debug(
            ("->" * len(pass_stack)) + " "
            + "{cls}.match(seq={seq!r}, s={s!r}) - success: {ndl!r}".format(
                cls=self.__class__.__name__, seq=self.seq, s=s, ndl=ndl))
        return ndl, r


class Seq(BaseSequence):
    """ Basically an alias for BaseSequence """
    pass


class ZeroOrMore(BaseSequence):
    def _match(self, s, rule, pass_stack, dialect):
        return self._match_sequence_multiple(s, rule, pass_stack, dialect=dialect, min_times=0, max_times=-1)


class OneOrMore(BaseSequence):
    def _match(self, s, rule, pass_stack, dialect):
        return self._match_sequence_multiple(s, rule, pass_stack, dialect=dialect, min_times=1, max_times=-1)


class ZeroOrOne(BaseSequence):
    def _match(self, s, rule, pass_stack, dialect):
        return self._match_sequence_multiple(s, rule, pass_stack, dialect=dialect, min_times=0, max_times=1)


class OneOf(BaseSequence):
    def _match(self, s, rule, pass_stack, dialect):
        """ OneOf Matching is a little different """
        # With a OneOf, we iterate across the items, looking for the first match. If
        # there are no matching options, then raise a parsing error.
        for elem in self.seq:
            try:
                # Copy each time just in case the match fails
                temp_s = s.copy()
                # If we manage to match without throwing an error, then we can just return
                # straight away. If the match fails, then we'll catch the exception and try
                # the next one.
                return rule._match_sequence(temp_s, elem, pass_stack, dialect=dialect)
            except sqlfluffParseError:
                # Any errors, we can ignore for now. We'll raise our own exception
                # if we don't find any matches
                pass
        else:
            # We've iterated through all the options, and not found a match
            # so we should raise an exception.
            raise sqlfluffParseError(rule, self.seq, s)


class ZeroOrOneOf(BaseSequence):
    def _match(self, s, rule, pass_stack, dialect):
        """ OneOf Matching is a little different """
        # With a OneOf, we iterate across the items, looking for the first match. If
        # there are no matching options, then raise a parsing error.
        for elem in self.seq:
            try:
                # Copy each time just in case the match fails
                temp_s = s.copy()
                # If we manage to match without throwing an error, then we can just return
                # straight away. If the match fails, then we'll catch the exception and try
                # the next one.
                return rule._match_sequence(temp_s, elem, pass_stack, dialect=dialect)
            except sqlfluffParseError:
                # Any errors, we can ignore for now. We'll raise our own exception
                # if we don't find any matches
                pass
        else:
            # We've iterated through all the options, and not found a match
            # but in this case we can just return having returned nothing
            return [], s


class AnyOf(BaseSequence):
    # This could be overwritten if we wanted an option to allow zero matches
    min_matches = 1

    def _match(self, s, rule, pass_stack, dialect):
        """ AnyOf Matching is a little different """
        # With a AnyOf, we continue to try and match any of the rules in the sequence
        # until we cannot match any more. Matching ZERO is not an acceptable outcome,
        # at least one element must be matched.
        s_buff = s
        node_buff = []
        while True:
            for elem in self.seq:
                try:
                    ndl, s_buff = rule._match_sequence(s_buff, elem, pass_stack, dialect=dialect)
                    node_buff += ndl
                    # We break out of the for loop here to let the while clause come back around.
                    break
                except sqlfluffParseError:
                    pass
            else:
                # We've iterated through all the loops, break to assess success:
                break
        # Check whether we've had enough matches to declare victory
        if len(node_buff) >= self.min_matches:
            return node_buff, s_buff
        else:
            # raise an exception for not matching anything
            raise sqlfluffParseError(rule, self.seq, s)


# ###############
# ## POSITIONED STRING
# ###############
class PositionedString(object):
    """ A String, but with a starting line and col """
    def __init__(self, s, col_no=1, line_no=1):
        self.s = s
        self.col_no = col_no
        self.line_no = line_no

    def __getitem__(self, item):
        return self.s[item]

    def __eq__(self, other):
        if isinstance(other, PositionedString):
            return self.s == other.s
        else:
            return self.s == other

    def __repr__(self):
        return "<{s!r} @{col},{line}>".format(
            s=self.s, col=self.col_no, line=self.line_no)

    def __str__(self):
        """ return the containing string """
        return self.s

    def copy(self):
        return PositionedString(s=self.s, col_no=self.col_no, line_no=self.line_no)

    def popleft(self, chars):
        """ chars is the number of characters to pop off the left """
        # the current object then moves it's index along
        left_string = self.s[:chars]
        newlines = left_string.count('\n')
        newcol = len(left_string.split('\n')[-1])
        result = PositionedString(s=self.s[:chars], col_no=self.col_no, line_no=self.line_no)
        self.s = self.s[chars:]
        self.line_no += newlines
        if newlines > 0:
            self.col_no = newcol + 1
        else:
            self.col_no += newcol
        return result


# ###############
# ## PARSER
# ###############
class NodeTerminalBase(object):
    """ The base class which contains the interfaces common
    to nodes and terminals """
    def __init__(self, name='-', rule_stack=None):
        self.name = name
        if rule_stack is None:
            self.rule_stack = tuple()
        else:
            self.rule_stack = rule_stack

    def __str__(self):
        return self.asstring()

    def _content(self, string=False):
        raise NotImplementedError("Method not defined for base class!")

    def node_tuple_set(self):
        """ Produce a set of tuples, but not just the terminals, all the tuples """
        raise NotImplementedError("Method not defined for base class!")

    def node_tuple(self):
        """ Produce a tuple for this node """
        return (self.name, self.asstring())

    def token_tuples(self):
        raise NotImplementedError("Method not defined for base class!")

    def tokens(self):
        raise NotImplementedError("Method not defined for base class!")

    def asstring(self):
        raise NotImplementedError("Method not defined for base class!")

    def astuple(self, string=False):
        """ string implies that we return a string rather
        than the PositionedString class """
        return (self.name, self._content(string=string))


class Node(NodeTerminalBase):
    def __init__(self, nodes, **kwargs):
        self.nodes = nodes
        super(Node, self).__init__(**kwargs)

    def __repr__(self):
        return "<Node {name!r} tkns:{tkns!r}>".format(
            name=self.name, tkns=self.tokens())

    def _content(self, string=False):
        """ The second part of the tuple function """
        return tuple([node.astuple(string=string) for node in self.nodes])

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

    def node_tuple_set(self):
        """ Produce a set of tuples, but not just the terminals, all the tuples """
        # We take the tuple for THIS node AND all the children
        return set([self.node_tuple()]) | set().union(*[nd.node_tuple_set() for nd in self.nodes])

    def token_tuples(self):
        """ Flatten the tree and return a list of token tuples """
        return list(itertools.chain(*[node.token_tuples() for node in self.nodes]))

    def tokens(self):
        """ Flatten the tree and return a list of token names """
        return list(itertools.chain(*[node.tokens() for node in self.nodes]))

    def asstring(self):
        """ reconstruct the string from the tree """
        return "".join([node.asstring() for node in self.nodes])


class Terminal(NodeTerminalBase):
    """ Like a node, but has no children """
    def __init__(self, content, **kwargs):
        self.content = content
        super(Terminal, self).__init__(**kwargs)

    def __repr__(self):
        return "<Terminal {token}: {s!r}>".format(
            s=self.content, token=self.name)

    def fmt(self, indent=0, deep_indent=50):
        line_buff = []
        line_buff.append(
            ('  ' * indent) + self.name + ':'
            + (' ' * (deep_indent - ((indent * 2) + len(self.name) + 1)))
            + repr(self.content))
        return line_buff

    def _content(self, string=False):
        """ The second part of the tuple function """
        return self.content.s if string else self.content

    def node_tuple_set(self):
        """ Produce a set of tuples, but not just the terminals, all the tuples """
        return set([self.node_tuple()])

    def token_tuples(self):
        """ Designed to fit with Node.token_tuples() """
        return [self.astuple()]

    def tokens(self):
        """ Designed to fit with Node.tokens() """
        return [self.name]

    def asstring(self):
        """ reconstruct the string from the tree """
        return str(self.content)


class Dialect(object):
    """ A dialect is a collection of rules """
    def __init__(self, name, root_rule, rules, join_rule=None):
        self.name = name
        self.root_rule = root_rule
        self.join_rule = join_rule
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

    def parse(self, sql, rule_stack=None):
        rule = self.get_rule(self.root_rule)
        # Check whether we're working with a positioned string or not.
        # Turn this into one if we aren't.
        if isinstance(sql, six.string_types):
            sql = PositionedString(sql)
        # Parse and make a tree recursively, passing self as the dialect
        # We should assume there's no existing rule stack, so pass an empty one in
        tree, remainder = rule.parse(sql, rule_stack=rule_stack or tuple(), dialect=self)
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

    def _match_sequence(self, sql, seq, pass_stack, dialect):
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
            nd, r = rule.parse(sql, pass_stack, dialect=dialect)
            # make the node into a list before returning
            return [nd], r
        # Is it any kind of sequence class?
        elif isinstance(seq, BaseSequence):
            ndl, r = seq.match(sql, rule=self, pass_stack=pass_stack, dialect=dialect)
            return ndl, r
        else:
            raise RuntimeError("Unknown type found in the sequence {0} {1!r}".format(type(seq), seq))

    def parse(self, sql, rule_stack, dialect):
        logging.debug(
            ("->" * len(rule_stack)) + " "
            + "Rule.parse(name={0!r}, sql={1!r}, seq={2!r}, rule_stack={3!r}) - begin ...".format(
                self.name, sql, self.sequence, rule_stack))
        # Check whether we're working with a positioned string or not.
        # Turn this into one if we aren't.
        if isinstance(sql, six.string_types):
            sql = PositionedString(sql)
        # Update the pass-through stack
        pass_stack = rule_stack + (self.name,)
        # Create a local variable to keep track of the remaining string
        s_buff = sql
        # Create a local buffer for notes
        node_buff = []
        # Find matches (any missing matches will raise an exception)
        try:
            node_buff, s_buff = self._match_sequence(sql, seq=self.sequence,
                                                     pass_stack=pass_stack, dialect=dialect)
            logging.debug(
                ("->" * len(rule_stack)) + " "
                + "Rule.parse(name={0!r}) - success".format(
                    self.name))
        except sqlfluffParseError as err:
            logging.debug(
                ("->" * len(rule_stack)) + " "
                + "Rule.parse(name={0!r}) - fail".format(
                    self.name))
            raise err
        # Assuming we get this far, spit back out a node
        return Node(node_buff, rule_stack=rule_stack, name=self.name), s_buff


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
        # Check whether we're working with a positioned string or not.
        # Turn this into one if we aren't.
        if isinstance(s, six.string_types):
            s = PositionedString(s)
        # Reformat the rule_stack if not passed (usually in testing)
        if rule_stack is None:
            rule_stack = []
        # Match it
        m = self.pattern.match(s.s)
        if m:
            last_pos = m.end()
            left_string = s.popleft(last_pos)
            terminal = Terminal(left_string, name=self.name, rule_stack=rule_stack)
            logging.debug(
                ("->" * len(rule_stack)) + " "
                + "TerminalRule.parse(name={0!r}): Match {1!r}".format(
                    self.name, terminal))
            return terminal, s
        else:
            # We don't have a match, raise an exception which can be optionally
            # caught further up stream.
            logging.debug(
                ("->" * len(rule_stack)) + " "
                + "TerminalRule.parse(name={0!r}): No Match (raise exception)".format(
                    self.name))
            raise sqlfluffParseError(self, self.name, s)
