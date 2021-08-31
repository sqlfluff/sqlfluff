"""Implementation of Rule L039."""

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L039(BaseRule):
    """Unnecessary whitespace found.

    | **Anti-pattern**

    .. code-block:: sql

        SELECT
            a,        b
        FROM foo

    | **Best practice**
    | Unless an indent or preceeding a comment, whitespace should
    | be a single space.

    .. code-block:: sql

        SELECT
            a, b
        FROM foo
    """

    def _eval(self, segment, parent_stack, **kwargs):
        """Unnecessary whitespace."""
        # For the given segment, lint whitespace directly within it.
        prev_newline = True
        prev_whitespace = None
        violations = []
        for seg in segment.segments:
            if seg.is_type("newline"):
                prev_newline = True
                prev_whitespace = None
            elif seg.is_type("whitespace"):
                # This is to avoid indents
                if not prev_newline:
                    prev_whitespace = seg
                prev_newline = False
            elif seg.is_type("comment"):
                prev_newline = False
                prev_whitespace = None
            else:
                if prev_whitespace:
                    if prev_whitespace.raw != " ":
                        violations.append(
                            LintResult(
                                anchor=prev_whitespace,
                                fixes=[
                                    LintFix(
                                        "edit",
                                        prev_whitespace,
                                        WhitespaceSegment(),
                                    )
                                ],
                            )
                        )
                prev_newline = False
                prev_whitespace = None
        if violations:
            return violations
