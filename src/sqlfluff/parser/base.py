""" Base Objects for the Parser """


import re
import six


class Chunk(object):
    """
    A chunk of text, with a line number and position
    It can be split and eventually turned into a token.
    A chunk should have a reference to the chunk before
    and after it to maintain the sense of a chunk in it's
    order within a file.

    A chunk can optionally have corrections applied to it.
    """
    pass


class TokenChunk(object):
    """
    A chunk of text, with a line number and position
    It can be split and eventually turned into a token.
    A chunk should have a reference to the chunk before
    and after it to maintain the sense of a chunk in it's
    order within a file.

    A chunk can optionally have corrections applied to it.
    """
    def __init__(self, s, col_no, line_no, stack):
        self.s = s
        self.col_no = col_no
        self.line_no = line_no
        self.stack = stack

    def __eq__(self, other):
        return (self.s == other.s
                and self.col_no == other.col_no
                and self.line_no == other.line_no
                and self.stack == other.stack)

    def __repr__(self):
        return "<TokenChunk {s!r} col:{col_no} line:{line_no} stack:{stack!r}>".format(
            **self.__dict__
        )


class Token(Chunk):
    """
    A piece of text of fixed length, with a particular
    meaning. It will also have a normalised form for
    comparison purposes.

    A token is linked to a single SyntaxTerminal.

    In the case that multiple tokens match a chunk, then
    it it possible for multiple to initially bind ("match")
    but at parse time (when building the AST) if that
    ambiguity still exists then it should raise an exception.

    ALL tokens are based on regexes (for simplicity)
    """
    def __init__(self, pattern, name=None, case_sensitive=False, syntax=True):  # maybe implement priority if we need to?
        self._pattern = pattern
        # If no name specified, just assume it's the same as the pattern
        self.name = name or pattern
        # Should the regex match be case sensitive? (default to no)
        self.case_sensitive = case_sensitive
        # The syntax flag is about whether it is only relevant at a particular place
        self.syntax = syntax
        # Precompile the pattern
        if case_sensitive:
            self.pattern = re.compile(pattern)
        else:
            self.pattern = re.compile(pattern, re.IGNORECASE)

    def match(self, s):
        """ match a given string against this rule, returning the matched part of the string """
        m = self.pattern.match(s)
        if m:
            last_pos = m.end()
            return s[:last_pos]
        return None


class SyntaxRule(object):
    """
    which represents a unique dialect of sql. This is a collection of `tokens`
    and `syntax elements`. These are defined so that inheritance can be used to define
    related syntaxes.
    """
    def __init__(self, name, sequence):
        self.name = name
        self.validate_sequence(sequence)
        self.sequence = sequence

    @staticmethod
    def validate_sequence(seq):
        """
        Validate that the given sequence is valid according to current
        rules and assumptions.
        """
        try:
            assert isinstance(seq, list)
        except AssertionError:
            raise AssertionError("SyntaxRule sequences must be lists!")
        try:
            for elem in seq:
                assert isinstance(elem, (six.string_types, list, set, tuple))
        except AssertionError:
            raise AssertionError("SyntaxRule sequences must contain only lists, sets or tuples!")
        try:
            for elem in seq:
                if isinstance(elem, (list, tuple)):
                    assert len(elem) == 1
                    assert isinstance(elem[0], six.string_types)
        except AssertionError:
            raise AssertionError("SyntaxRule optional items (lists and tuples), must contain only "
                                 "one element, and this must be a rule reference not another construction! "
                                 "Write a seperate rule for more complex constructions!")

    def __len__(self):
        return len(self.sequence)

    def __getitem__(self, idx):
        return self.sequence[idx]

    def __repr__(self):
        return "<SyntaxRule {name!r} {sequence!r}>".format(**self.__dict__)


class Dialect(object):
    """
    which represents a unique dialect of sql. This is a collection of `tokens`
    and `syntax elements`. These are defined so that inheritance can be used to define
    related syntaxes.
    """
    def __init__(self, name, description, tokens, syntax_rules, root_element):
        self.name = name
        self.description = description
        # Check that the names of tokens are unique
        token_names = [token.name for token in tokens]
        if len(token_names) != len(set(token_names)):
            raise ValueError("Token list contains a duplicate name!")
        self._tokens = {token.name: token for token in tokens}
        # Check names of rules are unique
        rule_names = [rule.name for rule in syntax_rules]
        if len(rule_names) != len(set(rule_names)):
            raise ValueError("Syntax rule list contains a duplicate name!")
        self._rules = {rule.name: rule for rule in syntax_rules}
        # Check no intersection between rules and tokens
        if len(set(self._rules.keys()) & set(self._tokens.keys())) > 0:
            raise ValueError("Some syntax rules share names with tokens!")
        # Check we actually have the root node
        if root_element not in self._rules:
            raise ValueError("Root element {0!r} not in the given list of rules.".format(root_element))
        self.root_element = root_element
        # Detect the non-syntax tokens
        self.non_syntax_tokens = [token for token in self._tokens if not self._tokens[token].syntax]

    def _match_token(self, s, token):
        """
        match the given string against the given token name.
        return a string or None
        """
        if token not in self._tokens:
            raise ValueError("Unexpected token: {0!r}".format(token))
        return self._tokens[token].match(s)

    def _match_tokens(self, s, tokens):
        """
        match the given string against a list of given tokens.
        return a dict of token: match
        """
        matches = {}
        for token in tokens:
            m = self._match_token(s, token)
            if m:
                matches[token] = m
        return matches

    def _match_all_tokens(self, s):
        """
        match the given string against all tokens.
        return a dict of token: match
        """
        return self._match_tokens(s, self._tokens.keys())

    def match_non_syntax(self, s):
        # We should also match for non-syntax tokens at this point
        matches = {}
        non_syntax_matches = self._match_tokens(s, self.non_syntax_tokens)
        if non_syntax_matches:
            matches.update({((key, False),): non_syntax_matches[key] for key in non_syntax_matches})
        return matches

    def _is_fully_matched(self, rule, stack_pos=None):
        """ Another recursive function to asertain whether we're fully matched """
        if stack_pos:
            if stack_pos[0][0] != rule:
                return 'Unmatched'
                # raise ValueError("Stack position doesn't match current rule! {0!r} rule:{1}".format(
                #    stack_pos, rule))
            else:
                # A boolean would imply a terminal (syntax or otherwise)
                if isinstance(stack_pos[0][1], bool):
                    # Being here means we're checking whether a terminal rule has been matched.
                    # Any match at all is by definition, full
                    return 'FullyMatched'
                # If it's not a boolean, then we're dealing with an integer.
                # We also need to actually fetch the rule to find out.
                else:
                    # Get the rule
                    r = self._rules[rule]
                    pos = stack_pos[0][1]
                    remaining_stack = stack_pos[1:]
                    last_rule_exp = r[pos]
                    # Is it just a rule that we matched last time?
                    if isinstance(last_rule_exp, six.string_types):
                        m = self._is_fully_matched(last_rule_exp, remaining_stack)
                    # Is it an optional rule that we matched?
                    elif isinstance(last_rule_exp, list):
                        m = self._is_fully_matched(last_rule_exp[0], remaining_stack)
                    else:
                        raise NotImplementedError("fsaljkshealfsiuhsaef")
                    if m == 'FullyMatched':
                        # Are we already at the end of the rule?
                        if pos + 1 == len(r):
                            return 'FullyMatched'
                        # Is the next element a defined rule, or set of rules?
                        elif isinstance(r[pos + 1], (six.string_types, set)):
                            return 'Unmatched'
                        # Is the next element an optional element
                        else:
                            raise NotImplementedError("Unable to handle this situation (_is_fully_matched)")
                    elif m == 'Unmatched':
                        return 'Unmatched'
                    # else m == 'PotentiallyMatched'
                    raise RuntimeError("{0!r} {1!r} {2!r} {3!r}".format(r, pos, remaining_stack, m))
                    #  First check whether we matched the last element of the rule
        else:
            return 'Unmatched'

    def _match_rule(self, s, rule, index=0, stack_pos=None):
        """
        match a given string against a rule, and a given position within that rule.
        This is recursive, it returns a dict of ((rule, idx), ..., (token)): match
        """
        # Fetch the rule, if it's not a rule, match as a token
        if rule not in self._rules:
            if index > 0:
                raise ValueError("Attempting to access token at index > 0! ({0!r}, {1})".format(rule, index))
            matches = {}
            # This should be the only entry point to match tokens
            syntax_match = self._match_token(s, token=rule)
            if syntax_match:
                matches.update({((rule, True),): syntax_match})
            return matches
        else:
            # Get the rule
            r = self._rules[rule]
            # Are we looking beyond the end of the rule?
            # If so, just return an empty dict
            if index >= len(r):
                return {}
            # What is at this index of the rule
            elem = r[index]
            matches = {}
            # Is it a string?
            if isinstance(elem, six.string_types):
                # If it's a string, we should just straight recurse
                matches.update(self._match_rule(s, rule=elem))
            # Is it a list or tuple?
            elif isinstance(elem, (list, tuple)):
                # A list or tuple implies an optional element, so we should check this
                # one, but also whatever comes next

                # Briefly check the length of the list, make sure it's 1
                if len(elem) != 1:
                    raise ValueError("Found an optional element of length != 1! {0!r} (in rule {1})".format(elem, rule))
                m = self._match_rule(s, rule=elem[0])
                if m:
                    matches.update(m)
                else:
                    # No match from this element, try the next (this isn't a submatch, se we return directly)
                    return self._match_rule(s, rule=rule, index=index + 1)
            # Is it a set?
            elif isinstance(elem, set):
                # Try each of the elements in the set for matches
                m = {}
                for rl in elem:
                    m.update(self._match_rule(s, rl))

            if matches:
                # if we've got a match, make sure we return the full path
                return {((rule, index), ) + k: matches[k] for k in matches}
            else:
                return {}

    def match_root_element(self, s, stack_pos=None):
        matches = {}
        matches.update(self._match_rule(s, self.root_element, stack_pos=stack_pos))
        matches.update(self.match_non_syntax(s))
        return matches

    def pop_token(self, s, col_no, line_no, stack_pos=None):
        """ pop a list of potential tokens off the string """
        matches = self.match_root_element(s, stack_pos=stack_pos)
        tokens = []
        for stack in matches:
            remaining_string = s[len(matches[stack]):]
            tokens.append((TokenChunk(matches[stack], col_no, line_no, stack), remaining_string))
        return tokens

    # def parse_stream(self, stream):
    #    rule_stack = []
    #    current_element = self.root_element
    #    rule_index = 0
    #    # enumerate through line by line
    #    for line_no, line in enumerate(stream, start=1):
    #        # match
    #        pass


# a list is a set sequence of elements
# a list inside a list implies an optional element
# a tuple implies a pattern which can be repeated any number of times (zero or more)
# a set implies a potential choice of options
ansi = Dialect(
    name='ansi',
    description="Standard ANSI SQL",
    tokens=[
        Token(
            name='string_literal',
            # Either single or double quotes
            pattern=r'\'[^\']*\'|\"[^\"]*\"'),
        Token(pattern=r'select'),
        Token(pattern=r'from'),
        Token(pattern=r'group\s+by', name='groupby'),
        Token(name='statement_terminator', pattern=r';'),
        Token(name='star', pattern=r'\*'),
        Token(
            name='whitespace',
            pattern=r'\s',
            syntax=False)
    ],
    syntax_rules=[
        SyntaxRule(
            name='sql_statements',
            sequence=[('terminated_sql_statement'), 'sql_statement', ('statement_terminator')]),
        SyntaxRule(
            name='terminated_sql_statement',
            sequence=['sql_statement', 'statement_terminator']),
        SyntaxRule(
            name='sql_statement',
            # Eventually put the other kinds of statement in here
            sequence=[set(['select_statement'])]),
        SyntaxRule(
            name='select_statement',
            sequence=['select', 'column_selection', 'from',
                      'table_expression', ['where_clause'], ['group_by_clause']])
    ],
    root_element='sql_statements'
)
