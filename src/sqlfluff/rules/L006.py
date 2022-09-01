"""Implementation of Rule L006."""


from typing import Tuple, List

from sqlfluff.core.rules import (
    BaseRule,
    LintResult,
    RuleContext,
    EvalResultType,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.reflow.classes import ReflowSequence


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
    crawl_behaviour = SegmentSeekerCrawler({"binary_operator", "comparison_operator"})
    # L006 works on operators so requires three operators.
    # However some rules that inherit from here (e.g. L048) do not.
    # So allow this to be configurable.
    _require_three_children: bool = True

    _target_elems: List[Tuple[str, str]] = [
        ("type", "binary_operator"),
        ("type", "comparison_operator"),
    ]

    def _eval(self, context: RuleContext) -> EvalResultType:
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
        # raw case - they'll be targetting the same segment, and potentially
        # waste some processing overhead, but this makes the code simpler.

        violations = []

        anchors = (
            # First look for issues before.
            ("before", context.segment.raw_segments[0]),
            # Then look for issues after.
            ("after", context.segment.raw_segments[-1]),
        )

        for side, anchor in anchors:
            raw = context.segment.raw_segments[0]
            fixes = (
                ReflowSequence.from_around_target(
                    raw, context.parent_stack[0], sides=side
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
                        description=f"Missing whitespace {side} {raw.raw}",
                    )
                )

        return violations
