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
            else:
                return self.args[0]

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
            return self.segment.pos_marker
        else:
            return None

    def get_info_tuple(self):
        return self.rule_code(), self.line_no(), self.line_pos(), self.desc()


class SQLLexError(SQLBaseError):
    # Not sure how we deal with lexing errors... Do they have a location?
    pass


class SQLParseError(SQLBaseError):
    # Lex Errors are linked to unparsable segment
    def __init__(self, segment=None, *args, **kwargs):
        # Store the segment on creation - we might need it later
        self.segment = segment
        super(SQLParseError, self).__init__(*args, **kwargs)


class SQLLintError(SQLBaseError):
    # Linting errors are triggered by RULES. So we should reference the rule.
    def __init__(self, segment=None, rule=None, *args, **kwargs):
        # Something about position, message and fix?
        self.segment = segment
        self.rule = rule
        super(SQLLintError, self).__init__(*args, **kwargs)
