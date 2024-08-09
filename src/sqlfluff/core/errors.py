"""Errors - these are closely linked to what used to be called violations.

NOTE: The BaseException class, which ValueError inherits from, defines
a custom __reduce__() method for picking and unpickling exceptions.
For the SQLBaseError, and it's dependent classes, we define properties
of these exceptions which don't work well with that method, which is
why we redefine __reduce__() on each of these classes. Given the
circumstances in which they are called, they don't show up on coverage
tracking.

https://stackoverflow.com/questions/49715881/how-to-pickle-inherited-exceptions
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union, cast

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser import BaseSegment, PositionMarker
    from sqlfluff.core.rules import BaseRule, LintFix

CheckTuple = Tuple[str, int, int]
SerializedObject = Dict[str, Union[str, int, bool, List["SerializedObject"]]]


def _extract_position(segment: Optional["BaseSegment"]) -> Dict[str, int]:
    """If a segment is present and is a literal, return it's source length."""
    if segment:
        position = segment.pos_marker
        assert position
        if position.is_literal():
            return position.to_source_dict()
    # An empty location is an indicator of not being able to accurately
    # represent the location.
    return {}  # pragma: no cover


class SQLBaseError(ValueError):
    """Base Error Class for all violations."""

    _code: Optional[str] = None
    _identifier = "base"
    _warning = False  # The default value for `warning`

    def __init__(
        self,
        description: Optional[str] = None,
        pos: Optional["PositionMarker"] = None,
        line_no: int = 0,
        line_pos: int = 0,
        ignore: bool = False,
        fatal: bool = False,
        warning: Optional[bool] = None,
    ) -> None:
        self.fatal = fatal
        self.ignore = ignore
        self.warning: bool = warning if warning is not None else self._warning
        self.description = description
        if pos:
            self.line_no, self.line_pos = pos.source_position()
        else:
            self.line_no = line_no
            self.line_pos = line_pos
        super().__init__(self.desc())

    def __eq__(self, other) -> bool:
        """Errors compare equal if they are the same type and same content."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __reduce__(
        self,
    ) -> Tuple[Type["SQLBaseError"], Tuple[Any, ...]]:
        """Prepare the SQLBaseError for pickling."""
        return type(self), (
            self.description,
            None,
            self.line_no,
            self.line_pos,
            self.ignore,
            self.fatal,
            self.warning,
        )

    @property
    def fixable(self) -> bool:
        """Should this error be considered fixable?"""
        return False

    def rule_code(self) -> str:
        """Fetch the code of the rule which cause this error."""
        return self._code or "????"

    def desc(self) -> str:
        """Fetch a description of this violation."""
        if self.description:
            return self.description

        return self.__class__.__name__  # pragma: no cover

    def to_dict(self) -> SerializedObject:
        """Return a dict of properties.

        This is useful in the API for outputting violations.
        """
        return {
            "start_line_no": self.line_no,
            "start_line_pos": self.line_pos,
            "code": self.rule_code(),
            "description": self.desc(),
            "name": getattr(self, "rule").name if hasattr(self, "rule") else "",
            "warning": self.warning,
        }

    def check_tuple(self) -> CheckTuple:
        """Get a tuple representing this error. Mostly for testing."""
        return (
            self.rule_code(),
            self.line_no,
            self.line_pos,
        )

    def source_signature(self) -> Tuple[Any, ...]:
        """Return hashable source signature for deduplication."""
        return (self.check_tuple(), self.desc())

    def ignore_if_in(self, ignore_iterable: List[str]) -> None:
        """Ignore this violation if it matches the iterable."""
        if self._identifier in ignore_iterable:
            self.ignore = True

    def warning_if_in(self, warning_iterable: List[str]) -> None:
        """Warning only for this violation if it matches the iterable.

        Designed for rule codes so works with L001, LL0X but also TMP or PRS
        for templating and parsing errors.

        Args:
            warning_iterable (List[str]): A list of strings representing the warning
                codes to check.

        Returns:
            None
        """
        if self.rule_code() in warning_iterable:
            self.warning = True


class SQLTemplaterError(SQLBaseError):
    """An error which occurred during templating.

    Args:
        pos (:obj:`PosMarker`, optional): The position which the error
            occurred at.

    """

    _code = "TMP"
    _identifier = "templating"


class SQLFluffSkipFile(RuntimeError):
    """An error returned from a templater to skip a file."""

    pass


class SQLLexError(SQLBaseError):
    """An error which occurred during lexing.

    Args:
        pos (:obj:`PosMarker`, optional): The position which the error
            occurred at.

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

    def __init__(
        self,
        description: Optional[str] = None,
        segment: Optional["BaseSegment"] = None,
        line_no: int = 0,
        line_pos: int = 0,
        ignore: bool = False,
        fatal: bool = False,
        warning: Optional[bool] = None,
    ) -> None:
        # Store the segment on creation - we might need it later
        self.segment = segment
        super().__init__(
            description=description,
            pos=segment.pos_marker if segment else None,
            line_no=line_no,
            line_pos=line_pos,
            ignore=ignore,
            fatal=fatal,
            warning=warning,
        )

    def __reduce__(
        self,
    ) -> Tuple[Type["SQLParseError"], Tuple[Any, ...]]:
        """Prepare the SQLParseError for pickling."""
        return type(self), (
            self.description,
            self.segment,
            self.line_no,
            self.line_pos,
            self.ignore,
            self.fatal,
            self.warning,
        )

    def to_dict(self) -> SerializedObject:
        """Return a dict of properties.

        This is useful in the API for outputting violations.

        For parsing errors we additionally add the length of the unparsable segment.
        """
        _base_dict = super().to_dict()
        _base_dict.update(
            **_extract_position(self.segment),
        )
        return _base_dict


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
        self,
        description: str,
        segment: "BaseSegment",
        rule: "BaseRule",
        fixes: Optional[List["LintFix"]] = None,
        ignore: bool = False,
        fatal: bool = False,
        warning: Optional[bool] = None,
    ) -> None:
        self.segment = segment
        self.rule = rule
        self.fixes = fixes or []
        super().__init__(
            description=description,
            pos=segment.pos_marker if segment else None,
            ignore=ignore,
            fatal=fatal,
            warning=warning,
        )

    def __reduce__(
        self,
    ) -> Tuple[Type["SQLLintError"], Tuple[Any, ...]]:
        """Prepare the SQLLintError for pickling."""
        return type(self), (
            self.description,
            self.segment,
            self.rule,
            self.fixes,
            self.ignore,
            self.fatal,
            self.warning,
        )

    def to_dict(self) -> SerializedObject:
        """Return a dict of properties.

        This is useful in the API for outputting violations.

        For linting errors we additionally add details of any fixes.
        """
        _base_dict = super().to_dict()
        _base_dict.update(
            fixes=[fix.to_dict() for fix in self.fixes],
            **_extract_position(self.segment),
        )
        # Edge case: If the base error doesn't have an end position
        # but we only have one fix and it _does_. Then use use that in the
        # overall fix.
        _fixes = cast(List[SerializedObject], _base_dict.get("fixes", []))
        if "end_line_pos" not in _base_dict and len(_fixes) == 1:
            _fix = _fixes[0]
            # If the mandatory keys match...
            if (
                _fix["start_line_no"] == _base_dict["start_line_no"]
                and _fix["start_line_pos"] == _base_dict["start_line_pos"]
            ):
                # ...then hoist all the optional ones from the fix.
                for key in [
                    "start_file_pos",
                    "end_line_no",
                    "end_line_pos",
                    "end_file_pos",
                ]:
                    _base_dict[key] = _fix[key]

        return _base_dict

    @property
    def fixable(self) -> bool:
        """Should this error be considered fixable?"""
        if self.fixes:
            return True
        return False

    def rule_code(self) -> str:
        """Fetch the code of the rule which cause this error."""
        return self.rule.code

    def source_signature(self) -> Tuple[Any, ...]:
        """Return hashable source signature for deduplication.

        For linting errors we need to dedupe on more than just location and
        description, we also need to check the edits potentially made, both
        in the templated file but also in the source.
        """
        fix_raws = tuple(
            tuple(e.raw for e in f.edit) if f.edit else None for f in self.fixes
        )
        _source_fixes: List[Tuple[str, int, int]] = []
        for fix in self.fixes:
            if not fix.edit:
                continue
            for edit in fix.edit:
                for source_edit in edit.source_fixes:
                    # NOTE: It's important that we don't dedupe on the
                    # templated slice for the source fix, because that will
                    # be different for different locations in any loop.
                    _source_fixes.append(
                        (
                            source_edit.edit,
                            source_edit.source_slice.start,
                            source_edit.source_slice.stop,
                        )
                    )
        return (self.check_tuple(), self.description, fix_raws, tuple(_source_fixes))

    def __repr__(self) -> str:
        return "<SQLLintError: rule {} pos:{!r}, #fixes: {}, description: {}>".format(
            self.rule_code(),
            (self.line_no, self.line_pos),
            len(self.fixes),
            self.description,
        )


class SQLUnusedNoQaWarning(SQLBaseError):
    """A warning about an unused noqa directive."""

    _code = "NOQA"
    _identifier = "noqa"
    _warning = True


class SQLFluffUserError(ValueError):
    """An error which should be fed back to the user."""
