"""Implementation of Rule L039."""
from typing import List, Optional

from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.core.parser.segments.base import IdentitySet
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

    needs_raw_stack = True

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Unnecessary whitespace."""
        # For the given segment, lint whitespace directly within it.
        prev_newline = True
        prev_whitespace = None
        violations = []
        memory = context.memory
        if not memory:
            # Use memory to avoid returning multiple fixes with the same anchor.
            # (This is illegal.)
            memory = dict(fix_anchors=IdentitySet())
        for seg in context.segment.segments:
            if seg.is_meta:
                continue
            elif seg.is_type("newline"):
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
                for child_seg in seg.get_raw_segments():
                    if child_seg.is_whitespace:
                        violations.append(
                            LintResult(
                                anchor=child_seg,
                                fixes=[LintFix.delete(child_seg)],
                            )
                        )

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

        final_violations = []
        # Here, handle a special case where this rule works in two steps to
        # remove unnecessary white space. Example query:
        #
        #     select
        #         '1'    ::   INT as id1,
        #         '2'::int as id2
        #     from table_a
        #
        # There are two fixes for line 2:
        # - Replace long runs of whitespace with a single whitespace
        # - Delete single whitespace if needed (e.g. adjacent to "::")
        #
        # As currently designed, L039 would try and "replace" and "delete" the
        # same whitespace segment, causing the linter to complain about
        # conflicting fixes to the same segment. As a simple workaround, L039
        # remembers previously returned fixes and avoids returning a second
        # fix with the same anchor. The other fix (if needed) will be applied
        # on the next linter pass.
        if violations:
            # If a violation contains fixes using the same anchor as an earlier
            # fix, skip this violation. If it's still an issue, it will again be
            # detected (and fixed) during the next linter pass.
            for violation in violations:
                # Do any of these fixes use the same anchor as a previously
                # returned fix?
                if not any(
                    [
                        fix
                        for fix in violation.fixes
                        if fix.anchor in memory["fix_anchors"]
                    ]
                ):
                    # No, thus we can safely return this fix.
                    final_violations.append(violation)
                    # Update our memory of previously used anchors.
                    for fix in violation.fixes:
                        memory["fix_anchors"].add(fix.anchor)
        if not final_violations:
            final_violations.append(LintResult())
        final_violations[-1].memory = memory
        return final_violations
