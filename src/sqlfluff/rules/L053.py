"""Implementation of Rule L053."""
from typing import Optional

from sqlfluff.core.parser.segments.base import IdentitySet
from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.functional import Segments, sp
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L053(BaseRule):
    """Top-level statements should not be wrapped in brackets.

    **Anti-pattern**

    A top-level statement is wrapped in brackets.

    .. code-block:: sql
       :force:

        (SELECT
            foo
        FROM bar)

        -- This also applies to statements containing a sub-query.

        (SELECT
            foo
        FROM (SELECT * FROM bar))

    **Best practice**

    Don't wrap top-level statements in brackets.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar

        -- Likewise for statements containing a sub-query.

        SELECT
            foo
        FROM (SELECT * FROM bar)
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Top-level statements should not be wrapped in brackets."""
        # We only care about bracketed segments that are direct
        # descendants of a top-level statement segment.
        filtered_parent_stack = [
            segment for segment in context.parent_stack if segment.type != "batch"
        ]
        if not (
            context.segment.is_type("bracketed")
            and [segment.type for segment in filtered_parent_stack]
            == ["file", "statement"]
        ):
            return None

        # Replace the bracketed segment with it's
        # children, excluding the bracket symbols.
        bracket_set = {"start_bracket", "end_bracket"}

        filtered_children = Segments(
            *[
                segment
                for segment in context.segment.segments
                if segment.name not in bracket_set and not segment.is_meta
            ]
        )

        # Lift leading/trailing whitespace and inline comments to the
        # segment above. This avoids introducing a parse error (ANSI and other
        # dialects generally don't allow this at lower levels of the parse
        # tree).
        to_lift_predicate = sp.or_(sp.is_whitespace(), sp.is_name("inline_comment"))
        leading = filtered_children.select(loop_while=to_lift_predicate)
        trailing = (
            filtered_children.reversed().select(loop_while=to_lift_predicate).reversed()
        )
        lift_nodes = IdentitySet(leading + trailing)
        fixes = []
        if lift_nodes:
            parent = filtered_parent_stack[-1]
            fixes.append(LintFix.create_before(parent, list(leading)))
            fixes.append(LintFix.create_after(parent, list(trailing)))
            fixes.extend([LintFix.delete(segment) for segment in lift_nodes])
            filtered_children = filtered_children[len(leading) : -len(trailing)]

        fixes.append(
            LintFix.replace(
                context.segment,
                filtered_children,
            )
        )

        return LintResult(anchor=context.segment, fixes=fixes)
