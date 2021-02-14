"""Errors - these are closely linked to what used to be called violations."""
from typing import Optional, Tuple

CheckTuple = Tuple[str, int, int]


class SQLBaseError(ValueError):
    """Base Error Class for all violations."""

    _code: Optional[str] = None
    _identifier = "base"

    def __init__(self, *args, **kwargs):
        self.ignore = kwargs.pop("ignore", False)
        super(SQLBaseError, self).__init__(*args, **kwargs)

    @property
    def fixable(self):
        """Should this error be considered fixable?"""
        return False

    def rule_code(self):
        """Fetch the code of the rule which cause this error.

        NB: This only returns a real code for some subclasses of
        error, (the ones with a `rule` attribute), but otherwise
        returns a placeholder value which can be used instead.
        """
        if hasattr(self, "rule"):
            return self.rule.code
        else:
            return self._code or "????"

    def desc(self):
        """Fetch a description of this violation.

        NB: For violations which don't directly implement a rule
        this attempts to return the error message linked to whatever
        caused the violation. Optionally some errors may have their
        description set directly.
        """
        if hasattr(self, "description") and self.description:
            # This can only override if it's present AND
            # if it's non-null.
            return self.description
        elif hasattr(self, "rule"):
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
        """Return the line number of the violation."""
        pm = self.pos_marker()
        if pm:
            return pm.line_no
        else:
            return None

    def line_pos(self):
        """Return the line position of the violation."""
        pm = self.pos_marker()
        if pm:
            return pm.line_pos
        else:
            return None

    def char_pos(self):
        """Return the character position in file of the violation."""
        pm = self.pos_marker()
        if pm:
            return pm.char_pos
        else:
            return 0

    def pos_marker(self):
        """Get the position marker of the violation.

        Returns:
            The :obj:`PosMarker` of the segments if the violation has a segment,
            the :obj:`PosMarker` directly stored in a `pos` attribute or None
            if neither a present.

        """
        if hasattr(self, "segment"):
            # Linting and Parsing Errors
            return self.segment.pos_marker
        elif hasattr(self, "pos"):
            # Lexing errors
            return self.pos
        else:
            return None

    def get_info_tuple(self):
        """Get a tuple representation of this violation.

        Returns:
            A `tuple` of (code, line_no, line_pos, description)

        """
        return self.rule_code(), self.line_no(), self.line_pos(), self.desc()

    def get_info_dict(self):
        """Get a dictionary representation of this violation.

        Returns:
            A `dictionary` with keys (code, line_no, line_pos, description)

        """
        return dict(
            zip(("code", "line_no", "line_pos", "description"), self.get_info_tuple())
        )

    def ignore_if_in(self, ignore_iterable):
        """Ignore this violation if it matches the iterable."""
        # Type conversion
        if isinstance(ignore_iterable, str):
            ignore_iterable = []
        # Ignoring
        if self._identifier in ignore_iterable:
            self.ignore = True


class SQLTemplaterError(SQLBaseError):
    """An error which occurred during templating.

    Args:
        pos (:obj:`PosMarker`, optional): The position which the error
            occured at.

    """

    _code = "TMP"
    _identifier = "templating"

    def __init__(self, *args, **kwargs):
        self.pos = kwargs.pop("pos", None)
        super(SQLTemplaterError, self).__init__(*args, **kwargs)


class SQLLexError(SQLBaseError):
    """An error which occurred during lexing.

    Args:
        pos (:obj:`PosMarker`, optional): The position which the error
            occured at.

    """

    _code = "LXR"
    _identifier = "lexing"

    def __init__(self, *args, **kwargs):
        # Store the segment on creation - we might need it later
        self.pos = kwargs.pop("pos", None)
        super(SQLLexError, self).__init__(*args, **kwargs)


class SQLParseError(SQLBaseError):
    """An error which occurred during parsing.

    Args:
        segment (:obj:`BaseSegment`, optional): The segment which is relevant
            for the failure in parsing. This is likely to be a subclass of
            `BaseSegment` rather than the parent class itself. This is mostly
            used for logging and for referencing position.

    """

    _code = "PRS"
    _identifier = "parsing"

    def __init__(self, *args, **kwargs):
        # Store the segment on creation - we might need it later
        self.segment = kwargs.pop("segment", None)
        super(SQLParseError, self).__init__(*args, **kwargs)


class SQLLintError(SQLBaseError):
    """An error which occurred during linting.

    In particular we reference the rule here to do extended logging based on
    the rule in question which caused the fail.

    Args:
        segment (:obj:`BaseSegment`, optional): The segment which is relevant
            for the failure in parsing. This is likely to be a subclass of
            `BaseSegment` rather than the parent class itself. This is mostly
            used for logging and for referencing position.

    """

    _identifier = "linting"

    def __init__(self, *args, **kwargs):
        # Something about position, message and fix?
        self.segment = kwargs.pop("segment", None)
        self.rule = kwargs.pop("rule", None)
        self.fixes = kwargs.pop("fixes", [])
        self.description = kwargs.pop("description", None)
        super(SQLLintError, self).__init__(*args, **kwargs)

    @property
    def fixable(self):
        """Should this error be considered fixable?"""
        if self.fixes:
            return True
        return False

    def check_tuple(self) -> CheckTuple:
        """Get a tuple representing this error. Mostly for testing."""
        return (
            self.rule.code,
            self.segment.pos_marker.line_no,
            self.segment.pos_marker.line_pos,
        )

    def __repr__(self):
        return (
            "<SQLLintError: rule {0} pos:{1!r}, #fixes: {2}, description: {3}>".format(
                self.rule_code(), self.pos_marker(), len(self.fixes), self.description
            )
        )
