"""Implementation of Rule AM09."""

from typing import Optional, Tuple

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AM09(BaseRule):
    """Use of LIMIT and OFFSET without ORDER BY may lead to non-deterministic results.

    When using ``LIMIT`` or ``OFFSET``, it's generally recommended to include
    an ``ORDER BY`` clause to ensure deterministic results.

    **Anti-pattern**

    The following query has LIMIT and OFFSET without ORDER BY, which may return
    different results in successive executions.

    .. code-block:: sql

        SELECT *
        FROM foo
        LIMIT 10 OFFSET 5;

    **Best practice**

    Include an ``ORDER BY`` clause:

    .. code-block:: sql

        SELECT *
        FROM foo
        ORDER BY id
        LIMIT 10 OFFSET 5;
    """

    name = "ambiguous.order_by_limit"
    aliases = ()
    groups: Tuple[str, ...] = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Check if LIMIT and OFFSET are used without ORDER BY."""
        segment = context.segment

        # Ensure it's a SELECT statement
        if not segment.is_type("select_statement"):
            return None

        # Detect presence of LIMIT and OFFSET
        has_limit = segment.get_child("limit_clause")
        has_offset = segment.get_child("offset_clause")
        has_order_by = segment.get_child("orderby_clause")

        # If LIMIT or OFFSET exist but ORDER BY is missing, issue a warning
        if (has_limit or has_offset) and not has_order_by:
            # Use the first relevant segment (LIMIT or OFFSET) as the anchor
            anchor_segment = has_limit or has_offset
            return LintResult(
                anchor=anchor_segment,
                description=(
                    "LIMIT and OFFSET are used without ORDER BY,"
                    " which may lead to non-deterministic results."
                ),
            )

        return None  # No issues found
