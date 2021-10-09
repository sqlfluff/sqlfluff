"""Errors - these are closely linked to what used to be called violations."""
from typing import Optional, Tuple

CheckTuple = Tuple[str, int, int]


class SQLBaseError(ValueError):
    """Base Error Class for all violations."""

    _code: Optional[str] = None
    _identifier = "base"

    def __init__(
        self,
        *args,
        pos=None,
        line_no=0,
        line_pos=0,
        ignore=False,
        fatal=False,
        **kwargs
    ):
        self.fatal = fatal
        self.ignore = ignore
        if pos:
            self.line_no, self.line_pos = pos.source_position()
        else:
            self.line_no = line_no
            self.line_pos = line_pos
        super().__init__(*args, **kwargs)

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
            if len(self.args) > 1:  # pragma: no cover TODO?
                return self.args
            elif len(self.args) == 1:
                return self.args[0]
            else:  # pragma: no cover TODO?
                return self.__class__.__name__

    def get_info_dict(self):
        """Return a dict of properties.

        This is useful in the API for outputting violations.
        """
        return {
            "line_no": self.line_no,
            "line_pos": self.line_pos,
            "code": self.rule_code(),
            "description": self.desc(),
        }

    def ignore_if_in(self, ignore_iterable):
        """Ignore this violation if it matches the iterable."""
        # Type conversion
        if isinstance(ignore_iterable, str):  # pragma: no cover TODO?
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


class SQLTemplaterSkipFile(RuntimeError):
    """An error returned from a templater to skip a file."""

    pass


class SQLLexError(SQLBaseError):
    """An error which occurred during lexing.

    Args:
        pos (:obj:`PosMarker`, optional): The position which the error
            occured at.

    """

    _code = "LXR"
    _identifier = "lexing"


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

    def __init__(self, *args, segment=None, **kwargs):
        # Store the segment on creation - we might need it later
        self.segment = segment
        if self.segment:
            kwargs["pos"] = self.segment.pos_marker
        super().__init__(*args, **kwargs)


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

    def __init__(
        self, *args, segment=None, rule=None, fixes=None, description=None, **kwargs
    ):
        # Something about position, message and fix?
        self.segment = segment
        if self.segment:
            kwargs["pos"] = self.segment.pos_marker
        self.rule = rule
        self.fixes = fixes or []
        self.description = description
        super().__init__(*args, **kwargs)

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
            self.line_no,
            self.line_pos,
        )

    def __repr__(self):
        return "<SQLLintError: rule {} pos:{!r}, #fixes: {}, description: {}>".format(
            self.rule_code(),
            (self.line_no, self.line_pos),
            len(self.fixes),
            self.description,
        )


class SQLFluffUserError(ValueError):
    """An error which should be fed back to the user."""
