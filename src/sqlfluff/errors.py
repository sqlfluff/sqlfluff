""" Errors - these are closely linked to what used to be called violations """


class SQLBaseError(ValueError):
    def __init__(self, *args, **kwargs):
        # Something about position, message and fix?
        super(SQLBaseError, self).__init__(*args, **kwargs)

    # We shoud be able to extract the info to format the exception in some consistent
    # way here.

    def rule_code(self):
        if hasattr(self, 'rule'):
            return self.rule.code
        else:
            return '????'

    def desc(self):
        if hasattr(self, 'rule'):
            return self.rule.description
        else:
            # Return the first element - probably a string message
            if len(self.args) > 1:
                return self.args
            elif len(self.args) == 1:
                return self.args[0]
            else:
                return self.__class__.__name__

    def line_no(self):
        pm = self.pos_marker()
        if pm:
            return pm.line_no
        else:
            return 0

    def line_pos(self):
        pm = self.pos_marker()
        if pm:
            return pm.line_pos
        else:
            return 0

    def char_pos(self):
        pm = self.pos_marker()
        if pm:
            return pm.char_pos
        else:
            return 0

    def pos_marker(self):
        if hasattr(self, 'segment'):
            # Linting and Parsing Errors
            return self.segment.pos_marker
        elif hasattr(self, 'pos'):
            # Lexing errors
            return self.pos
        else:
            return None

    def get_info_tuple(self):
        return self.rule_code(), self.line_no(), self.line_pos(), self.desc()


class SQLLexError(SQLBaseError):
    # Lexing errors just have position
    def __init__(self, *args, **kwargs):
        # Store the segment on creation - we might need it later
        self.pos = kwargs.pop('pos', None)
        super(SQLLexError, self).__init__(*args, **kwargs)


class SQLParseError(SQLBaseError):
    # Lex Errors are linked to unparsable segment
    def __init__(self, *args, **kwargs):
        # Store the segment on creation - we might need it later
        self.segment = kwargs.pop('segment', None)
        super(SQLParseError, self).__init__(*args, **kwargs)


class SQLLintError(SQLBaseError):
    # Linting errors are triggered by RULES. So we should reference the rule.
    def __init__(self, *args, **kwargs):
        # Something about position, message and fix?
        self.segment = kwargs.pop('segment', None)
        self.rule = kwargs.pop('rule', None)
        self.fixes = kwargs.pop('fixes', [])
        super(SQLLintError, self).__init__(*args, **kwargs)

    def check_tuple(self):
        """ This is used mostly in testing to easily example a linting result """
        return (self.rule.code, self.segment.pos_marker.line_no, self.segment.pos_marker.line_pos)

    def __repr__(self):
        return "<SQLLintError: rule {0} pos:{1!r}, #fixes: {2}>".format(
            self.rule_code(), self.pos_marker(), len(self.fixes))
