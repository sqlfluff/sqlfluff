"""Implementation of Rule L006."""


from typing import List

from sqlfluff.core.rules import (
    BaseRule,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.reflow import ReflowSequence


@document_groups
@document_fix_compatible
class Rule_L006(BaseRule):
    """Operators should be surrounded by a single whitespace.

    **Anti-pattern**

    In this example, there is a space missing between the operator and ``b``.

    .. code-block:: sql

        SELECT
            a +b
        FROM foo


    **Best practice**

    Keep a single space.

    .. code-block:: sql

        SELECT
            a + b
        FROM foo
    """

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler(
        {"binary_operator", "comparison_operator", "assignment_operator"}
    )

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Operators should be surrounded by a single whitespace.

        Rewritten to assess direct children of a segment to make
        whitespace insertion more sensible.

        We only need to handle *missing* whitespace because excess
        whitespace is handled by L039.

        NOTE: We also allow bracket characters either side.
        """
        # Iterate through children of this segment looking for any of the
        # target types. We also check for whether any of the children start
        # or end with the targets.

        # We ignore any targets which start or finish this segment. They'll
        # be dealt with by the parent segment. That also means that we need
        # to have at least three children.

        # Operators can be either a single raw segment or multiple, and
        # a significant number of them are multiple (thanks TSQL). While
        # we could provide an alternative route for single raws, this is
        # implemented to separately look before, and after. In the single
        # raw case - they'll be targeting the same segment, and potentially
        # waste some processing overhead, but this makes the code simpler.

        # If this is an operator within an operator, we'll double count
        # so abort.
        if context.parent_stack and context.parent_stack[-1].is_type(
            "assignment_operator"
        ):
            return []

        violations = []

        anchors = (
            # First look for issues before.
            ("before", context.segment.raw_segments[0]),
            # Then look for issues after.
            ("after", context.segment.raw_segments[-1]),
        )

        for side, anchor in anchors:
            fixes = (
                ReflowSequence.from_around_target(
                    anchor, context.parent_stack[0], config=context.config, sides=side
                )
                .respace()
                .get_fixes()
            )
            # Filter for only creations, because edits are handled as excess
            # whitespace in a different rule.
            fixes = [
                fix
                for fix in fixes
                if fix.edit_type in ("create_before", "create_after")
            ]

            if fixes:
                violations.append(
                    LintResult(
                        context.segment,
                        fixes=fixes,
                        description=f"Missing whitespace {side} {anchor.raw}",
                    )
                )

        return violations
