"""Implementation of Rule L067."""
from typing import List, Optional
import logging
from pprint import pformat

from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.core.rules.functional import sp



@document_groups
@document_fix_compatible
class Rule_L067(BaseRule):
    """Aliases not aligned within select statement.

    **Anti-pattern**

    .. code-block:: sql

        SELECT
            a AS first_column,
            b AS second_column,
            (a + b) / 2 AS third_column
        FROM foo

    **Best practice**

    Unless there are no aliases in the clause,
    all aliases should be aligned with the longest expression in select clause

    .. code-block:: sql

        SELECT
            a           AS first_column,
            b           AS second_column,
            (a + b) / 2 AS third_column
        FROM foo
    """
    groups = ("all", "core")

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """
        Loops through each select_clause_element in a select clause
          * Sets max_len to the length of the longest expression using an Alias.
        Loops through all select_clause_elements in the select clause again
          * pads each expression with (max_len - len(expression)) whitespace.

        """
        # We loop over `select_clause_element`s to find length of the longest expression
        children = context.functional.segment.children()
        select_targets = children.select(sp.is_type("select_clause_element"))
        max_len = 0
        for expression_segment in select_targets:
            expression_sub_segments = expression_segment.segments
            for expression_sub_segment in expression_sub_segments:
                if expression_sub_segment.is_type("expression") or expression_sub_segment.is_type("column_reference"):
                    max_len = max(max_len, expression_sub_segment.matched_length)
        fixes = []

        # We loop over `select_clause_element`s again to pad each expression
        for expression_segment in select_targets:
            if expression_segment.is_type("select_clause_element"):
                expression_sub_segments = expression_segment.segments
                for expression_sub_segment in expression_sub_segments:
                    if expression_sub_segment.is_type("expression") or expression_sub_segment.is_type("column_reference"):
                        padding = max_len - expression_sub_segment.matched_length + 1
                        old_white_space = expression_sub_segments[expression_sub_segments.index(expression_sub_segment) + 1]
                        new_white_space = WhitespaceSegment(raw=" " * padding)
                        if old_white_space.matched_length < new_white_space.matched_length:
                            fixes.append(
                                LintFix.replace(
                                    old_white_space, [new_white_space]
                                ),
                            )
        if fixes:
            return LintResult(anchor=fixes[0].anchor, fixes=fixes)
        return None
