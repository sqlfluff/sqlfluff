"""Implementation of Rule LT07."""

from typing import Optional, Set, cast

from sqlfluff.core.parser import NewlineSegment, RawSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_LT07(BaseRule):
    """``WITH`` clause closing bracket should be on a new line.

    **Anti-pattern**

    In this example, the closing bracket is on the same line as CTE.

    .. code-block:: sql
       :force:

        WITH zoo AS (
            SELECT a FROM foo)

        SELECT * FROM zoo

    **Best practice**

    Move the closing bracket on a new line.

    .. code-block:: sql

        WITH zoo AS (
            SELECT a FROM foo
        )

        SELECT * FROM zoo

    """

    name = "layout.cte_bracket"
    aliases = ("L018",)
    groups = ("all", "core", "layout")
    crawl_behaviour = SegmentSeekerCrawler(
        {"with_compound_statement"}, provide_raw_stack=True
    )
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """WITH clause closing bracket should be aligned with WITH keyword.

        Look for a with clause and evaluate the position of closing brackets.
        """
        # We only trigger on start_bracket (open parenthesis)
        assert context.segment.is_type("with_compound_statement")

        # Find the end brackets for the CTE *query* (i.e. ignore optional
        # list of CTE columns).
        cte_end_brackets: Set[RawSegment] = set()
        for cte in (
            FunctionalContext(context)
            .segment.children(sp.is_type("common_table_expression"))
            .iterate_segments()
        ):
            cte_start_bracket = (
                cte.children()
                .last(sp.is_type("bracketed"))
                .children()
                .first(sp.is_type("start_bracket"))
            )
            cte_end_bracket = (
                cte.children()
                .last(sp.is_type("bracketed"))
                .children()
                .last(sp.is_type("end_bracket"))
            )
            if cte_start_bracket and cte_end_bracket:
                self.logger.debug(
                    "Found CTE with brackets: %s & %s",
                    cte_start_bracket,
                    cte_end_bracket,
                )
                # Are they on the same line?
                # NOTE: This assertion should be fairly safe because
                # there aren't many reasons for an bracket to not yet
                # be positioned.
                assert cte_start_bracket[0].pos_marker
                assert cte_end_bracket[0].pos_marker
                if (
                    cte_start_bracket[0].pos_marker.line_no
                    == cte_end_bracket[0].pos_marker.line_no
                ):
                    # Same line
                    self.logger.debug("Skipping because on same line.")
                    continue
                # Otherwise add to the ones to check.
                cte_end_brackets.add(cast(RawSegment, cte_end_bracket[0]))

        for seg in cte_end_brackets:
            contains_non_whitespace = False
            idx = context.segment.raw_segments.index(seg)
            self.logger.debug("End bracket %s has idx %s", seg, idx)
            # Search backward through the raw segments from just before
            # the location of the bracket.
            for elem in context.segment.raw_segments[idx - 1 :: -1]:
                if elem.is_type("newline"):
                    break
                elif not elem.is_type("indent", "whitespace"):
                    self.logger.debug("Found non-whitespace: %s", elem)
                    contains_non_whitespace = True
                    break

            if contains_non_whitespace:
                # We have to move it to a newline
                return LintResult(
                    anchor=seg,
                    fixes=[
                        LintFix.create_before(
                            seg,
                            [
                                NewlineSegment(),
                            ],
                        )
                    ],
                )

        return None
