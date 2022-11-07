"""Implementation of Rule L048."""

from typing import List

from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.reflow import ReflowSequence


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
        pre_fixes, _, post_fixes = (
            ReflowSequence.from_around_target(
                context.segment, context.parent_stack[0], config=context.config
            )
            .respace()
            .get_partitioned_fixes(context.segment)
        )

        # Filter for only creations, because edits are handled as excess
        # whitespace in a different rule.
        pre_fixes = [
            fix
            for fix in pre_fixes
            if fix.edit_type in ("create_before", "create_after")
        ]
        post_fixes = [
            fix
            for fix in post_fixes
            if fix.edit_type in ("create_before", "create_after")
        ]

        violations = []

        # Is it a creation before
        if pre_fixes:
            violations.append(
                LintResult(
                    context.segment,
                    fixes=pre_fixes,
                    description=f"Missing whitespace before {context.segment.raw}",
                )
            )
        # Is it a creation after
        if post_fixes:
            violations.append(
                LintResult(
                    context.segment,
                    fixes=post_fixes,
                    description=f"Missing whitespace after {context.segment.raw}",
                )
            )

        return violations
