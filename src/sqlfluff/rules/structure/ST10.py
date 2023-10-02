"""Implementation of Rule ST10."""
from typing import List, Optional, Tuple

from sqlfluff.core.parser import (
    KeywordSegment,
    SymbolSegment,
    WhitespaceSegment,
    WordSegment,
)
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


class Rule_ST10(BaseRule):
    """Unused tables in joins should be removed.

    This rule will check if there are any tables that are joined in but not used in the select statement.
    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Implement the logic to detect unused tables in joins.

        1. Get all the tables that are joined in the query.
        2. Get all the tables that are used in the select statement.
        3. Compare the two lists and find the tables that are in the join list but not in the select list.
        4. For each unused table, create a LintResult with a fix that removes the join.
        """
        join_tables = context.segment.get_children("join_clause")
        select_tables = context.segment.get_children("select_clause")
        unused_tables = [table for table in join_tables if table not in select_tables]
        for table in unused_tables:
            return LintResult(anchor=table, fixes=[LintFix("delete", table)])
        return None
