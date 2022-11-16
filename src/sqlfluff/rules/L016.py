"""Implementation of Rule L016."""

from collections import defaultdict
from typing import List

from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.core.rules.base import BaseRule
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)

from sqlfluff.utils.reflow.sequence import ReflowSequence


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L016(BaseRule):
    """Line is too long."""

    groups = ("all", "core")
    crawl_behaviour = RootOnlyCrawler()
    _adjust_anchors = True
    _check_docstring = False

    config_keywords = [
        "ignore_comment_lines",
        "ignore_comment_clauses",
    ]

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Line is too long."""
        # Reflow and generate fixes.
        fixes = (
            ReflowSequence.from_root(context.segment, context.config)
            .reindent()
            .get_fixes()
        )

        # Group together for each line
        lines = defaultdict(list)
        for fix in fixes:
            lines[fix.anchor.pos_marker.working_line_no].append(fix)

        # Construct results.
        results = []
        for line_no in lines.keys():
            line_fixes = lines[line_no]
            # Filter out the long line fixes.
            long_line_fixes = [
                fix
                for fix in line_fixes
                if fix.description.startswith("Line is too long")
            ]
            # If we don't get any long line fixes. Ignore the all of them.
            if not long_line_fixes:
                continue
            # If we do, return all of them, because they should *all* shorten
            # the line.
            # TODO: We should probably anchor the fix on the start of the line
            # and not on the anchor of the first fix.
            result_anchor = long_line_fixes[0].anchor
            results.append(
                LintResult(
                    anchor=result_anchor,
                    fixes=line_fixes,
                    description=long_line_fixes[0].description,
                )
            )

        return results
