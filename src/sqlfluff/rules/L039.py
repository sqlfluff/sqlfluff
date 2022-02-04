"""Implementation of Rule L039."""
from typing import List, Optional

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import sp


@document_fix_compatible
class Rule_L039(BaseRule):
    """Unnecessary whitespace found.

    **Anti-pattern**

    .. code-block:: sql

        SELECT
            a,        b
        FROM foo

    **Best practice**

    Unless an indent or preceding a comment, whitespace should
    be a single space.

    .. code-block:: sql

        SELECT
            a, b
        FROM foo
    """

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Unnecessary whitespace."""
        # For the given segment, lint whitespace directly within it.
        prev_newline = True
        prev_whitespace = None
        violations = []
        for seg in context.segment.segments:
            if seg.is_type("newline"):
                prev_newline = True
                prev_whitespace = None
            elif seg.is_type("whitespace"):
                # This is to avoid indents
                if not prev_newline:
                    prev_whitespace = seg
                # We won't set prev_newline to False, just for whitespace
                # in case there's multiple indents, inserted by other rule
                # fixes (see #1713)
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
                                    LintFix.replace(
                                        prev_whitespace,
                                        [WhitespaceSegment()],
                                    )
                                ],
                            )
                        )
                prev_newline = False
                prev_whitespace = None

            if seg.is_type("object_reference"):
                # This variable is a workaround to avoid removing new indents added at
                # the beginning of a segment by L003. See Github issue #1304:
                # https://github.com/sqlfluff/sqlfluff/issues/1304
                # It represents the question: are we parsing through leading whitespace
                # in this loop?
                leading_whitespace = True
                for child_seg in seg.get_raw_segments():
                    if child_seg.is_whitespace:
                        if not leading_whitespace:
                            violations.append(
                                LintResult(
                                    anchor=child_seg,
                                    fixes=[LintFix.delete(child_seg)],
                                )
                            )
                    else:
                        leading_whitespace = False

            if seg.is_type("comparison_operator"):
                delete_fixes = [
                    LintFix.delete(s) for s in seg.get_raw_segments() if s.is_whitespace
                ]
                if delete_fixes:
                    violations.append(
                        LintResult(
                            anchor=delete_fixes[0].anchor,
                            fixes=delete_fixes,
                        )
                    )

        if context.segment.is_type("casting_operator"):
            leading_whitespace_segments = (
                context.functional.raw_stack.reversed().select(
                    select_if=sp.is_whitespace(),
                    loop_while=sp.or_(sp.is_whitespace(), sp.is_meta()),
                )
            )
            trailing_whitespace_segments = (
                context.functional.siblings_post.raw_segments.select(
                    select_if=sp.is_whitespace(),
                    loop_while=sp.or_(sp.is_whitespace(), sp.is_meta()),
                )
            )

            fixes: List[LintFix] = []
            fixes.extend(LintFix.delete(s) for s in leading_whitespace_segments)
            fixes.extend(LintFix.delete(s) for s in trailing_whitespace_segments)

            if fixes:
                violations.append(
                    LintResult(
                        anchor=context.segment,
                        fixes=fixes,
                    )
                )

        return violations or None
