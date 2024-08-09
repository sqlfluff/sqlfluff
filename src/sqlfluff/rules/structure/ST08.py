"""Implementation of Rule ST08."""

from typing import Optional, Tuple

from sqlfluff.core.parser import BaseSegment, KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp
from sqlfluff.utils.reflow.sequence import ReflowSequence


class Rule_ST08(BaseRule):
    """``DISTINCT`` used with parentheses.

    **Anti-pattern**

    In this example, parentheses are not needed and confuse
    ``DISTINCT`` with a function. The parentheses can also be misleading
    about which columns are affected by the ``DISTINCT`` (all the columns!).

    .. code-block:: sql

        SELECT DISTINCT(a), b FROM foo

    **Best practice**

    Remove parentheses to be clear that the ``DISTINCT`` applies to
    both columns.

    .. code-block:: sql

        SELECT DISTINCT a, b FROM foo

    """

    name = "structure.distinct"
    aliases = ("L015",)
    groups = ("all", "structure", "core")
    crawl_behaviour = SegmentSeekerCrawler({"select_clause", "function"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Looking for DISTINCT before a bracket.

        Look for DISTINCT keyword immediately followed by open parenthesis.
        """
        seq = None
        anchor = None
        children = FunctionalContext(context).segment.children()
        if context.segment.is_type("select_clause"):
            # Look for `select_clause_modifier`
            modifier = children.select(sp.is_type("select_clause_modifier"))
            first_element = children.select(sp.is_type("select_clause_element")).first()
            expression = (
                first_element.children(sp.is_type("expression")).first()
                or first_element
            )
            bracketed = expression.children(sp.is_type("bracketed")).first()
            # is the first element only an expression with only brackets?
            if modifier and bracketed:
                # If there's nothing else in the expression, remove the brackets.
                if len(expression[0].segments) == 1:
                    anchor, seq = self._remove_unneeded_brackets(context, bracketed)
                # Otherwise, still make sure there's a space after the DISTINCT.
                else:
                    anchor = modifier[0]
                    seq = ReflowSequence.from_around_target(
                        modifier[0],
                        context.parent_stack[0],
                        config=context.config,
                        sides="after",
                    )
        elif context.segment.is_type("function"):
            # Look for a function call DISTINCT() whose parent is an expression
            # with a single child.
            anchor = context.parent_stack[-1]
            if not anchor.is_type("expression") or len(anchor.segments) != 1:
                return None
            function_name = children.select(sp.is_type("function_name")).first()
            bracketed = children.first(sp.is_type("bracketed"))
            if (
                not function_name
                or function_name[0].raw_upper != "DISTINCT"
                or not bracketed
            ):
                return None
            # Using ReflowSequence here creates an unneeded space between CONCAT
            # and "(" in the test case test_fail_distinct_concat_inside_count:
            #    SELECT COUNT(DISTINCT(CONCAT(col1, '-', col2, '-', col3)))
            #
            # seq = ReflowSequence.from_around_target(
            #     anchor,
            #     context.parent_stack[0],
            #     config=context.config,
            # ).replace(
            #     anchor,
            #     (KeywordSegment("DISTINCT"), WhitespaceSegment())
            #     + self.filter_meta(bracketed[0].segments)[1:-1],
            # )
            # Do this until we have a fix for the above.
            return LintResult(
                anchor=anchor,
                fixes=[
                    LintFix.replace(
                        anchor,
                        (KeywordSegment("DISTINCT"), WhitespaceSegment())
                        + self.filter_meta(bracketed[0].segments)[1:-1],
                    )
                ],
            )
        if seq and anchor:
            # Get modifications.
            fixes = seq.respace().get_fixes()
            if fixes:
                return LintResult(
                    anchor=anchor,
                    fixes=fixes,
                )
        return None

    def _remove_unneeded_brackets(
        self, context: RuleContext, bracketed: Segments
    ) -> Tuple[BaseSegment, ReflowSequence]:
        # Remove the brackets and strip any meta segments.
        anchor = bracketed.get()
        assert anchor
        seq = ReflowSequence.from_around_target(
            anchor,
            context.parent_stack[0],
            config=context.config,
            sides="before",
        ).replace(anchor, self.filter_meta(anchor.segments)[1:-1])
        return anchor, seq
