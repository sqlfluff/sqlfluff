"""Implementation of Rule L016."""

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
        self.ignore_comment_lines: bool
        # Reflow and generate fixes.
        results = (
            ReflowSequence.from_root(context.segment, context.config)
            .reindent()
            .get_results()
        )
        # Filter only to results which start with "Line is too long".
        results = [
            res for res in results if res.description.startswith("Line is too long")
        ]
        # Apply ignore comment lines.
        if self.ignore_comment_lines:
            results = [res for res in results if not res.anchor.is_type("comment")]
        return results
