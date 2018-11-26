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
    pass




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
        # Should this token be counted toward syntax (or ignored like whitespace)
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
        self.sequence = sequence


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

    def _match_rule(self, s, rule, index=0):
        """
        match a given string against a rule, and a given position within that rule.
        This is recursive, it returns a dict of ((rule, idx), ..., (token)): match
        """
        # Fetch the rule, if it's not a rule, match as a token
        if rule not in self._rules:
            # This should be the only entry point to match tokens
            m = self._match_token(s, token=rule)
            if index > 0:
                raise ValueError("Attempting to access token at index > 0! ({0!r}, {1})".format(rule, index))
            if m:
                return {(rule): m}
            else:
                return {}
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
                return {(rule, index) + k: matches[k] for k in matches}
            else:
                return {}

    def parse_stream(self, stream):
        rule_stack = []
        current_element = self.root_element
        rule_index = 0
        # enumerate through line by line
        for line_no, line in enumerate(stream, start=1):
            # match
            pass


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
            # Eventually put the other kinds of statement in here
            sequence=[('terminated_sql_statement'), 'sql_statement', ('statement_terminator')]),
        SyntaxRule(
            name='terminated_sql_statement',
            # Eventually put the other kinds of statement in here
            sequence=['sql_statement', 'statement_terminator']),
        SyntaxRule(
            name='sql_statement',
            # Eventually put the other kinds of statement in here
            sequence=set(['select_statement'])),
        SyntaxRule(
            name='select_statement',
            sequence=['select', 'column_selection', 'from',
                    'table_expression', ['where_clause'], ['group_by_clause']])
    ],
    root_element='sql_statements'
)
