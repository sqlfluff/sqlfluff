"""Implementation of Rule L048."""

from typing import Optional, Tuple, List

from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.reflow.classes import ReflowSequence


@document_groups
@document_fix_compatible
class Rule_L048(BaseRule):
    """Quoted literals should be surrounded by a single whitespace.

    **Anti-pattern**

    In this example, there is a space missing between the string
    ``'foo'`` and the keyword ``AS``.

    .. code-block:: sql

        SELECT
            'foo'AS bar
        FROM foo


    **Best practice**

    Keep a single space.

    .. code-block:: sql

        SELECT
            'foo' AS bar
        FROM foo
    """

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler(
        {"quoted_literal", "date_constructor_literal"}
    )

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Quoted literals should be surrounded by a single whitespace."""
        fixes = (
            ReflowSequence.from_around_target(context.segment, context.parent_stack[0])
            .respace()
            .get_fixes()
        )

        fixes = [
            fix for fix in fixes if fix.edit_type in ("create_before", "create_after")
        ]

        violations = []

        for fix in fixes:
            # Filter for only creations, because edits are handled as excess
            # whitespace in a different rule.
            if fix.edit_type not in ("create_before", "create_after"):
                continue
            # Is it a creation before
            if fix.anchor.pos_marker < context.segment.pos_marker or (
                fix.anchor == context.segment and fix.edit_type == "create_before"
            ):
                violations.append(
                    LintResult(
                        context.segment,
                        fixes=[fix],
                        description=f"Missing whitespace before {context.segment.raw}",
                    )
                )
            # Is it a creation after
            if fix.anchor.pos_marker > context.segment.pos_marker or (
                fix.anchor == context.segment and fix.edit_type == "create_after"
            ):
                violations.append(
                    LintResult(
                        context.segment,
                        fixes=[fix],
                        description=f"Missing whitespace after {context.segment.raw}",
                    )
                )

        return violations
